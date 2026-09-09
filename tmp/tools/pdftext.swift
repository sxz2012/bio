import Quartz
let doc = PDFDocument(url: URL(fileURLWithPath: CommandLine.arguments[1]))!
print(doc.string ?? "")
