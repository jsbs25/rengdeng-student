import Foundation
import WebKit

let a = CommandLine.arguments
guard a.count >= 2 else { print("usage: errcheck2 <url>"); exit(1) }
let url = URL(string: a[1])!

let app = NSApplication.shared
app.setActivationPolicy(.prohibited)

let inject = """
window.__errs=[];
window.addEventListener('error',function(e){try{window.__errs.push('ERR: '+e.message+' @'+(e.filename||'')+':'+e.lineno)}catch(_){}});
window.addEventListener('unhandledrejection',function(e){try{window.__errs.push('REJ: '+((e.reason&&(e.reason.stack||e.reason.message))||e.reason))}catch(_){}});
(function(){var ce=console.error;console.error=function(){try{window.__errs.push('CONSOLE: '+Array.prototype.slice.call(arguments).join(' '))}catch(_){};ce.apply(console,arguments)}})();
"""

let steps = [
 "nav('home')","nav('learn')","nav('listen')","nav('ai')","nav('me')",
 "showAllSentences()","showVocab()","showLibrary()","showBooks()","showQuran()",
 "showFlashcard()","showWordBook()","showAlphabet()","showListen()","showQuiz()",
 "showDialog()","showHistory()","showHadith()","showPrayer()","showMusic()",
 "openImageModal()","checkServer()","updateStats()","showDueBar()","renderFavState()",
 "nextQuote()","cycleGoal()","checkIn()","exportData()"
]

final class D: NSObject, WKNavigationDelegate {
    func webView(_ wv: WKWebView, didFinish nav: WKNavigation!) {
        var i = 0
        var log: [String] = []
        func runNext() {
            if i >= steps.count {
                wv.evaluateJavaScript("JSON.stringify((window.__errs||[]).slice(0,40))") { r, _ in
                    print("STEPS_DONE \(steps.count)")
                    print("ERRORS: \(r ?? "nil")")
                    exit(0)
                }
                return
            }
            let js = steps[i]
            let name = js
            i += 1
            // Async page entry functions return Promise objects, which WKWebView
            // cannot bridge as a result. Ignore the return value and only capture
            // thrown errors / window.__errs so the smoke test does not false-fail.
            let wrapped = "(function(){\(js); return true;})()"
            wv.evaluateJavaScript(wrapped) { _, e in
                if let err = e { print("CALLFAIL \(name): \(err)") }
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.35) { runNext() }
            }
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.5) { runNext() }
    }
    func webView(_ wv: WKWebView, didFail nav: WKNavigation!, withError e: Error) { print("NAVFAIL \(e)"); exit(2) }
}

let cfg = WKWebViewConfiguration()
let ucc = WKUserContentController()
ucc.addUserScript(WKUserScript(source: inject, injectionTime: .atDocumentStart, forMainFrameOnly: true))
cfg.userContentController = ucc
let wv = WKWebView(frame: NSRect(x: 0, y: 0, width: 390, height: 844), configuration: cfg)
let d = D()
wv.navigationDelegate = d
wv.load(URLRequest(url: url))
app.run()
