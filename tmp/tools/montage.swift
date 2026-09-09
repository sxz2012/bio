import AppKit
let a = CommandLine.arguments; let out = a[1]; let cols = Int(a[2])!; let files = Array(a[3...])
let imgs = files.compactMap { NSImage(contentsOfFile: $0) }
let w = imgs[0].size.width, h = imgs[0].size.height
let rows = (imgs.count + cols - 1)/cols
let canvas = NSImage(size: NSSize(width: w*CGFloat(cols), height: h*CGFloat(rows)))
canvas.lockFocus(); NSColor.gray.setFill(); NSRect(origin: .zero, size: canvas.size).fill()
for (i, im) in imgs.enumerated() { let r = i/cols, c = i%cols
  im.draw(in: NSRect(x: CGFloat(c)*w, y: h*CGFloat(rows-1-r), width: w-4, height: h-4)) }
canvas.unlockFocus()
let rep = NSBitmapImageRep(data: canvas.tiffRepresentation!)!
try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: out))
