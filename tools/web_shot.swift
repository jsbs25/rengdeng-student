import Foundation
import WebKit

let a = CommandLine.arguments
guard a.count >= 3 else { print("usage: htmlshot <in.html> <out.png> [w] [h] [y]"); exit(1) }
let inURL = URL(fileURLWithPath: a[1])
let outPath = a[2]
let W = a.count > 3 ? (Double(a[3]) ?? 390) : 390
let H = a.count > 4 ? (Double(a[4]) ?? 844) : 844
let Y = a.count > 5 ? (Double(a[5]) ?? 0) : 0

let app = NSApplication.shared
app.setActivationPolicy(.prohibited)

final class D: NSObject, WKNavigationDelegate {
    let outPath: String; let W: Double; let H: Double; let Y: Double
    init(outPath: String, W: Double, H: Double, Y: Double){ self.outPath=outPath; self.W=W; self.H=H; self.Y=Y }
    func webView(_ wv: WKWebView, didFinish nav: WKNavigation!) {
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
            wv.evaluateJavaScript("window.scrollTo(0, \(self.Y));") { _, _ in
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.6) {
            let cfg = WKSnapshotConfiguration()
            cfg.rect = CGRect(x: 0, y: 0, width: self.W, height: self.H)
            wv.takeSnapshot(with: cfg) { img, err in
                if let img = img,
                   let tiff = img.tiffRepresentation,
                   let rep = NSBitmapImageRep(data: tiff),
                   let png = rep.representation(using: .png, properties: [:]) {
                    try? png.write(to: URL(fileURLWithPath: self.outPath))
                    print("SHOT_OK \(self.outPath)")
                } else { print("ERR shot \(String(describing: err))") }
                exit(0)
            }
            }
            }
        }
    }
    func webView(_ wv: WKWebView, didFail nav: WKNavigation!, withError e: Error) { print("ERR nav \(e)"); exit(2) }
}

let cfg = WKWebViewConfiguration()
let wv = WKWebView(frame: NSRect(x: 0, y: 0, width: W, height: H), configuration: cfg)
let d = D(outPath: outPath, W: W, H: H, Y: Y)
wv.navigationDelegate = d
wv.loadFileURL(inURL, allowingReadAccessTo: inURL.deletingLastPathComponent())
app.run()
