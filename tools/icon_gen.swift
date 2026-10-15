import AppKit
import Foundation

let S: CGFloat = 1024
let img = NSImage(size: NSSize(width: S, height: S))
img.lockFocus()
guard let ctx = NSGraphicsContext.current?.cgContext else { print("ERR ctx"); exit(1) }

// 背景：圆角矩形 + 深色径向渐变
let rect = CGRect(x: 0, y: 0, width: S, height: S)
let rr = CGPath(roundedRect: rect, cornerWidth: 224, cornerHeight: 224, transform: nil)
ctx.saveGState()
ctx.addPath(rr)
ctx.clip()
let space = CGColorSpaceCreateDeviceRGB()
let bg = CGGradient(colorsSpace: space, colors: [
    NSColor(calibratedRed: 0.16, green: 0.16, blue: 0.17, alpha: 1).cgColor,
    NSColor(calibratedRed: 0.04, green: 0.04, blue: 0.05, alpha: 1).cgColor
] as CFArray, locations: [0, 1])!
ctx.drawRadialGradient(bg, startCenter: CGPoint(x: S * 0.5, y: S * 0.82), startRadius: 0,
                       endCenter: CGPoint(x: S * 0.5, y: S * 0.5), endRadius: S * 0.78, options: [.drawsAfterEndLocation])
ctx.restoreGState()

// 金色渐变（灯罩描边 / 火苗）
func gold(_ a: CGFloat) -> NSColor { NSColor(calibratedRed: 0.91, green: 0.72, blue: 0.33, alpha: a) }
func amber(_ a: CGFloat) -> NSColor { NSColor(calibratedRed: 1.0, green: 0.62, blue: 0.12, alpha: a) }

// 拱门（米哈拉布）
let arch = NSBezierPath()
let cx = S * 0.5, baseY = S * 0.235, topY = S * 0.735, halfW = S * 0.235
arch.move(to: NSPoint(x: cx - halfW, y: baseY))
arch.line(to: NSPoint(x: cx - halfW, y: topY - halfW * 1.15))
arch.curve(to: NSPoint(x: cx + halfW, y: topY - halfW * 1.15),
           controlPoint1: NSPoint(x: cx - halfW, y: topY + halfW * 0.30),
           controlPoint2: NSPoint(x: cx + halfW, y: topY + halfW * 0.30))
arch.line(to: NSPoint(x: cx + halfW, y: baseY))
arch.lineWidth = 26
arch.lineCapStyle = .round
gold(0.92).setStroke()
arch.stroke()

// 底部横线（灯座）
let base = NSBezierPath()
base.move(to: NSPoint(x: cx - halfW * 1.34, y: baseY))
base.line(to: NSPoint(x: cx + halfW * 1.34, y: baseY))
base.lineWidth = 26
base.lineCapStyle = .round
gold(0.92).setStroke()
base.stroke()

// 火苗 + 光晕
let cy = S * 0.49
let glow = CGGradient(colorsSpace: space, colors: [
    amber(0.55).cgColor, amber(0.0).cgColor
] as CFArray, locations: [0, 1])!
ctx.drawRadialGradient(glow, startCenter: CGPoint(x: cx, y: cy), startRadius: 0,
                       endCenter: CGPoint(x: cx, y: cy), endRadius: S * 0.30, options: [])

let flame = NSBezierPath()
flame.move(to: NSPoint(x: cx, y: cy + S * 0.175))
flame.curve(to: NSPoint(x: cx + S * 0.088, y: cy - S * 0.055),
            controlPoint1: NSPoint(x: cx + S * 0.070, y: cy + S * 0.105),
            controlPoint2: NSPoint(x: cx + S * 0.092, y: cy + S * 0.020))
flame.curve(to: NSPoint(x: cx, y: cy - S * 0.135),
            controlPoint1: NSPoint(x: cx + S * 0.084, y: cy - S * 0.098),
            controlPoint2: NSPoint(x: cx + S * 0.046, y: cy - S * 0.132))
flame.curve(to: NSPoint(x: cx - S * 0.088, y: cy - S * 0.055),
            controlPoint1: NSPoint(x: cx - S * 0.046, y: cy - S * 0.132),
            controlPoint2: NSPoint(x: cx - S * 0.084, y: cy - S * 0.098))
flame.curve(to: NSPoint(x: cx, y: cy + S * 0.175),
            controlPoint1: NSPoint(x: cx - S * 0.092, y: cy + S * 0.020),
            controlPoint2: NSPoint(x: cx - S * 0.070, y: cy + S * 0.105))
flame.close()
let fg = CGGradient(colorsSpace: space, colors: [
    NSColor(calibratedRed: 1.0, green: 0.94, blue: 0.72, alpha: 1).cgColor,
    NSColor(calibratedRed: 1.0, green: 0.68, blue: 0.20, alpha: 1).cgColor,
    NSColor(calibratedRed: 0.93, green: 0.45, blue: 0.06, alpha: 1).cgColor
] as CFArray, locations: [0, 0.55, 1])!
ctx.saveGState()
flame.addClip()
ctx.drawLinearGradient(fg, start: CGPoint(x: cx, y: cy - S * 0.14),
                       end: CGPoint(x: cx, y: cy + S * 0.18), options: [])
ctx.restoreGState()

img.unlockFocus()
guard let tiff = img.tiffRepresentation, let rep = NSBitmapImageRep(data: tiff),
      let png = rep.representation(using: .png, properties: [:]) else { print("ERR png"); exit(2) }
let out = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "/tmp/appicon.png"
try! png.write(to: URL(fileURLWithPath: out))
print("ICON_OK \(out)")
