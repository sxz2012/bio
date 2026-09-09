from pathlib import Path
import re,json
p=Path('units/ecology/book/ecology-1A-2C.tex')
s=p.read_text()
a=re.split(r'% INSERT BEFORE (\w+)\n',Path('tmp/book-additions.tex').read_text())
for i in range(1,len(a),2):
    m=re.search(r'\\pagechapter\{[^\n]+\}\{'+a[i]+r'\}',s)
    assert m,a[i]
    s=s[:m.start()]+a[i+1]+'\n'+s[m.start():]
s=s.replace(r'\begin{document}',r'''\newcommand{\classsource}[1]{{\footnotesize\textit{Class connection:} #1\par}}
\makeatletter
\renewcommand{\l@section}{\@dottedtocline{1}{0em}{0em}}
\makeatother
\begin{document}''')
s=re.sub(r'\\textbf\{Class-specific information\.\}[^\n]+',r'\\textbf{Class-specific information.} See page \\pageref{classroom} for the supplied class expectations and grading overview.',s)
s=s.replace('The practice quiz includes these commonly used categories; its notes make subtype requirements class-dependent:', 'The supplied Biodiversity Worksheet asks for all four categories, so learn each definition and be able to provide examples:')
s=re.sub(r'\\textbf\{Class-dependent topics\.\}[^\n]+',r'\\textbf{Class requirements clarified.} Although the practice key calls some topics class-dependent, the supplied Biodiversity Worksheet explicitly asks for all four ecosystem-service categories and wildlife corridors. Study both.',s)
s=s.replace('The linked class slides, videos, and worksheets have not yet been reviewed for this book. Explanations, examples, knowledge graphs, and new review questions are supplemental study material rather than teacher-issued answers.', 'This revision incorporates text from all 26 supplied source files, including eight slide decks, class worksheets, skeleton notes, CER materials, the energy-flow lab, and the Ecology 2 framework. The two copies of the Ecology 2 framework are identical. Class-connection notes identify the relevant sources throughout. Original explanations, diagrams, synthetic data, and new questions supplement the supplied materials; they are not teacher-issued answers. Linked videos and textbook pages were not supplied or reviewed.')
s=s.replace('Add class notes and teacher feedback, confirm class-specific requirements, and update practice around Shawn\'s missed questions.', 'Add textbook pages and teacher feedback, and update practice around Shawn\'s missed questions.')
p.write_text(s)
