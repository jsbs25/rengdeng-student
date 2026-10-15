import Foundation
import WebKit
// usage: web_measure <url> <width> <height> <js-expression|@file.js> [waitSec]
let a = CommandLine.arguments
guard a.count >= 5 else { print("usage: web_measure <url> <w> <h> <expr|@file> [wait]"); exit(1) }
let url = URL(string: a[1])!
let W = Double(a[2]) ?? 1280
let H = Double(a[3]) ?? 900
var expr = a[4]
if expr.hasPrefix("@") {
    expr = (try? String(contentsOfFile: String(expr.dropFirst()), encoding: .utf8)) ?? "''"
}
let wait = a.count > 5 ? (Double(a[5]) ?? 2.5) : 2.5
let app = NSApplication.shared
app.setActivationPolicy(.prohibited)
final class D: NSObject, WKNavigationDelegate {
    let expr: String; let wait: Double
    init(_ e: String, _ w: Double) { expr = e; wait = w }
    func webView(_ wv: WKWebView, didFinish nav: WKNavigation!) {
        DispatchQueue.main.asyncAfter(deadline: .now() + wait) {
            wv.evaluateJavaScript(self.expr) { r, e in
                if let e = e { print("ERR \(e)") } else { print("OK \(String(describing: r))") }
                exit(0)
            }
        }
    }
}
let cfg = WKWebViewConfiguration()
let wv = WKWebView(frame: NSRect(x: 0, y: 0, width: W, height: H), configuration: cfg)
let d = D(expr, wait); wv.navigationDelegate = d
wv.load(URLRequest(url: url))
app.run()
