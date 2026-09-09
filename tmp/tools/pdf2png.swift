import Foundation
import Quartz
import AppKit
let args = CommandLine.arguments
let url = URL(fileURLWithPath: args[1]); let outdir = args[2]; let scale = CGFloat(Double(args[3]) ?? 1.5)
let pages = args.count > 4 ? args[4].split(separator: ",").map{Int($0)!} : []
guard let doc = PDFDocument(url: url) else { print("no doc"); exit(1) }
let idx = pages.isEmpty ? Array(1...doc.pageCount) : pages
for p in idx {
  guard let page = doc.page(at: p-1) else { continue }
  let b = page.bounds(for: .mediaBox)
  let w = Int(b.width*scale), h = Int(b.height*scale)
  let img = NSImage(size: NSSize(width: w, height: h))
  img.lockFocus()
  NSColor.white.setFill(); NSRect(x:0,y:0,width:w,height:h).fill()
  let ctx = NSGraphicsContext.current!.cgContext
  ctx.scaleBy(x: scale, y: scale)
  page.draw(with: .mediaBox, to: ctx)
  img.unlockFocus()
  let rep = NSBitmapImageRep(data: img.tiffRepresentation!)!
  let png = rep.representation(using: .png, properties: [:])!
  try! png.write(to: URL(fileURLWithPath: String(format: "%@/page-%02d.png", outdir, p)))
}
print("pages:", doc.pageCount)
