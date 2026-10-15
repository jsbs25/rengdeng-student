import Foundation
import AppKit
import WebKit

let args = CommandLine.arguments
guard args.count == 6 else { print("usage: test <url> <width> <height> <script> <output-dir>"); exit(1) }
let url = URL(string: args[1])!
let width = Double(args[2])!, height = Double(args[3])!
let script = try String(contentsOfFile: args[4], encoding: .utf8)
let output = URL(fileURLWithPath: args[5], isDirectory: true)
try FileManager.default.createDirectory(at: output, withIntermediateDirectories: true)
let app = NSApplication.shared
app.setActivationPolicy(.prohibited)

final class Driver: NSObject, WKNavigationDelegate {
    var started = false
    func webView(_ view: WKWebView, didFinish navigation: WKNavigation!) {
        if started { return }; started = true
        DispatchQueue.main.asyncAfter(deadline: .now() + 3) {
            view.callAsyncJavaScript(script, arguments: [:], in: nil, in: .page) { result in
                switch result {
                case .success(let value):
                    let text = value as? String ?? String(describing: value)
                    try? text.write(to: output.appendingPathComponent("results.json"), atomically: true, encoding: .utf8)
                    if let data = text.data(using: .utf8), let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any] {
                        print("TESTS \(obj["passed"] ?? "?")/\(obj["total"] ?? "?") viewport=\(width)x\(height)")
                        if let rows = obj["results"] as? [[String: Any]] { for row in rows where row["ok"] as? Bool == false { print("FAIL \(row)") } }
                        if let reply = obj["realReply"] as? String { print("AI: \(reply.prefix(300))") }
                    }
                    self.snapshot(view, index: 0)
                case .failure(let error):
                    print("TEST_ERROR \(error)"); exit(2)
                }
            }
        }
    }
    func snapshot(_ view: WKWebView, index: Int) {
        let tabs = ["home", "learn", "listen", "me", "ai"]
        if index >= tabs.count { print("SCREENSHOTS_OK \(output.path)"); exit(0) }
        let tab = tabs[index]
        view.evaluateJavaScript("nav('\(tab)')") { _, error in
            if let error = error { print("NAV_ERROR \(error)"); exit(3) }
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.8) {
                let cfg = WKSnapshotConfiguration()
                cfg.rect = CGRect(x: 0, y: 0, width: width, height: height)
                view.takeSnapshot(with: cfg) { image, error in
                    if let image = image, let tiff = image.tiffRepresentation,
                       let rep = NSBitmapImageRep(data: tiff), let png = rep.representation(using: .png, properties: [:]) {
                        try? png.write(to: output.appendingPathComponent(tab + ".png"))
                    } else { print("SNAPSHOT_ERROR \(String(describing: error))") }
                    self.snapshot(view, index: index + 1)
                }
            }
        }
    }
    func webView(_ view: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) { print("LOAD_ERROR \(error)"); exit(4) }
}
let config = WKWebViewConfiguration()
config.websiteDataStore = .nonPersistent()
let view = WKWebView(frame: NSRect(x: 0, y: 0, width: width, height: height), configuration: config)
let driver = Driver()
view.navigationDelegate = driver
view.load(URLRequest(url: url))
DispatchQueue.main.asyncAfter(deadline: .now() + 140) { print("TEST_TIMEOUT"); exit(5) }
app.run()
