import AppKit
import Foundation

let W: CGFloat = 1600, H: CGFloat = 1000
let img = NSImage(size: NSSize(width: W, height: H))
img.lockFocus()
let ctx = NSGraphicsContext.current!.cgContext
let cs = CGColorSpaceCreateDeviceRGB()

// 背景
let bg = CGGradient(colorsSpace: cs, colors: [
    NSColor(calibratedRed: 0.09, green: 0.09, blue: 0.10, alpha: 1).cgColor,
    NSColor(calibratedRed: 0.02, green: 0.02, blue: 0.03, alpha: 1).cgColor
] as CFArray, locations: [0, 1])!
ctx.drawLinearGradient(bg, start: CGPoint(x: 0, y: H), end: CGPoint(x: W, y: 0), options: [])

// 中央光晕
let glow = CGGradient(colorsSpace: cs, colors: [
    NSColor(calibratedRed: 0.95, green: 0.72, blue: 0.30, alpha: 0.20).cgColor,
    NSColor(calibratedRed: 0.95, green: 0.72, blue: 0.30, alpha: 0.0).cgColor
] as CFArray, locations: [0, 1])!
ctx.drawRadialGradient(glow, startCenter: CGPoint(x: W * 0.5, y: H * 0.62), startRadius: 0,
                       endCenter: CGPoint(x: W * 0.5, y: H * 0.62), endRadius: W * 0.46, options: [])

// 贴入图标
if let icon = NSImage(contentsOfFile: "/tmp/appicon.png") {
    let s: CGFloat = 260
    icon.draw(in: NSRect(x: W / 2 - s / 2, y: H * 0.52, width: s, height: s))
}

func draw(_ text: String, size: CGFloat, color: NSColor, y: CGFloat, font: NSFont? = nil, kern: CGFloat = 0) {
    let f = font ?? NSFont(name: "Geeza Pro", size: size) ?? NSFont.systemFont(ofSize: size)
    let attrs: [NSAttributedString.Key: Any] = [.font: f, .foregroundColor: color, .kern: kern]
    let ns = text as NSString
    let sz = ns.size(withAttributes: attrs)
    ns.draw(at: NSPoint(x: (W - sz.width) / 2, y: y), withAttributes: attrs)
}

let gold = NSColor(calibratedRed: 0.93, green: 0.76, blue: 0.40, alpha: 1)
let grey = NSColor(calibratedRed: 0.72, green: 0.72, blue: 0.74, alpha: 1)
let dim = NSColor(calibratedRed: 0.55, green: 0.55, blue: 0.58, alpha: 1)

draw("حامل المصباح", size: 132, color: gold, y: H * 0.335)
draw("燃灯者 · 无声却引人归途", size: 44, color: grey, y: H * 0.255,
     font: NSFont(name: "PingFang SC", size: 44) ?? NSFont.systemFont(ofSize: 44), kern: 4)
draw("23,835 部伊斯兰典籍 · 13,185 部全文可读 · 六大部圣训 34,153 段", size: 26, color: dim, y: H * 0.165,
     font: NSFont(name: "PingFang SC", size: 26) ?? NSFont.systemFont(ofSize: 26), kern: 1)
draw("صامتٌ لكنّه يهدي إلى الطريق", size: 30, color: dim, y: H * 0.085)

img.unlockFocus()
let rep = NSBitmapImageRep(data: img.tiffRepresentation!)!
try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: "/tmp/appcover.png"))
print("COVER_OK")
