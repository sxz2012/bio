from pathlib import Path
import json
from urllib.parse import quote
p=Path('units/ecology/book/ecology-1A-2C.tex');s=p.read_text()
s=s.replace(r'\begin{document}',r'\pdfstringdefDisableCommands{\def\quad{ }}'+'\n'+r'\begin{document}')
s=s.replace("Use the class's exact criteria when answering its checklist questions.",r'The full class checklist is explained on page \pageref{lifecheck}.')
s=s.replace('Quiz extension: keystone species.','Keystone species.')
s=s.replace('As an extension, name its service category.','Name its service category.')
s=s.replace('Naming a category is not required.','The category is provisioning.')
p.write_text(s)
records=json.loads(Path('units/ecology/source-inventory.json').read_text())
lines=['# Ecology materials index','','The 35-page study book covers targets 1A–2C using the teacher guide, practice quiz, and newly supplied class materials. All originals remain at the project root.','','The collection contains 26 source files: 14 Word documents, eight slide decks (111 slides), and four PDFs. The two Ecology 2 framework PDFs are byte-identical. Text extraction supports indexing; it does not preserve all images or slide layout. Links and video activities mentioned inside documents are source content, not additional completed tasks.','','| Original source | Study connection | Extracted text |','| --- | --- | --- |']
for r in records:
 f=r['file'];lo=f.lower()
 if any(x in lo for x in ['class basics','deductive','geotastic','observation']): target='1A: class expectations and reasoning'
 elif any(x in lo for x in ['feedback','what is life']): target='1B: life and homeostasis'
 elif any(x in lo for x in ['energy','metabolism','trophic']): target='1C: energy, matter, and trophic roles'
 elif 'population' in lo: target='2C: population and resources'
 elif 'cer' in lo: target='2B: scientific arguments'
 elif 'biodiversity' in lo: target='2A–2B: biodiversity and threats'
 elif 'eco_2' in lo: target='2A–2C: review framework'
 else: target='1A–2C: scope and exam practice'
 lines.append(f'| [{f}](../../{quote(f)}) | {target} | [Text](source-text/{quote(Path(r["text_file"]).name)}) |')
lines += ['','## Revision notes','','- Expanded from 22 to 35 pages, adding 13 sections and 12 diagram/application questions with answers.','- New editable figures cover cells and viruses, feedback in both directions, energy and gas exchange, lab setup and data, biodiversity scales, habitat corridors, and changing carrying capacity.','- Invented numerical examples and schematic graphs are labeled; no invented measurements are attributed to Shawn.','- The class worksheet confirms all four ecosystem-service categories and corridors are part of the review material.','- The textbook edition and pages are still pending. The book has not been checked against the actual California Miller & Levine textbook.','- File hashes and extraction metadata: [source-inventory.json](source-inventory.json).']
Path('units/ecology/materials-index.md').write_text('\n'.join(lines)+'\n')
p=Path('units/ecology/book/README.md');s=p.read_text().replace('The book covers teacher learning targets','The expanded 35-page book covers teacher learning targets');s=s.replace('## Sources and limits','## September revision\n\nThe revision adds 13 sections with fuller explanations, worked examples, editable scientific diagrams, and 12 new application questions with separate answers. It incorporates the newly supplied class notes, worksheets, lab, and slide text. See the [materials index](../materials-index.md) for all 26 source files and the [extraction inventory](../source-inventory.json) for file metadata.\n\n## Sources and limits');p.write_text(s)
p=Path('README.md');s=p.read_text().replace('### Materials collected','### Materials collected\n\n- [Ecology materials index](units/ecology/materials-index.md): all 26 supplied source files, mapped to learning targets. The study book now has 35 pages with expanded explanations and diagrams.');p.write_text(s)
