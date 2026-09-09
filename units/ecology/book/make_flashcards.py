#!/usr/bin/env python3
"""Generate flashcards from the vocabulary pages of ecology-1A-2C.tex.

Outputs (paths relative to the project root):
  units/ecology/book/ecology-flashcards.tex   printable fold-over cards (build with Tectonic or XeLaTeX)
  output/flashcards/ecology-1A-2C-flashcards.tsv   tab-separated import file for Anki (tab separator) or Quizlet

Run from the project root:  python3 units/ecology/book/make_flashcards.py
"""
import re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[3]
SRC = ROOT / "units/ecology/book/ecology-1A-2C.tex"
OUT_TEX = ROOT / "units/ecology/book/ecology-flashcards.tex"
OUT_TSV = ROOT / "output/flashcards/ecology-1A-2C-flashcards.tsv"

src = SRC.read_text()

# ---- 1. biology vocabulary rows from the six per-target pages ----
cards = []  # dicts: target, icon, color, term, meaning_tex, example_tex
chapter_re = re.compile(r"\\pagechapter\{(\w+)\\quad Vocabulary\}\{(\w+)\}")
row_re = re.compile(r"\\vt\[([^\]]+)\]\{(.+?)\}\{(.+?)\} & (.+?) & (.+?)\\\\$")
target = None
for line in src.splitlines():
    m = chapter_re.match(line)
    if m:
        target = m.group(1); continue
    if line.startswith(r"\pagechapter{"):
        target = None; continue
    m = row_re.match(line)
    if m and target:
        color, icon, term, meaning, example = m.groups()
        cards.append(dict(target=target, icon=icon, color=color, term=term, meaning=meaning, example=example, kind="biology"))

# ---- 2. academic words from the two academic-vocabulary pages ----
acad_re = re.compile(r"^([A-Z][^&\\]+?) & (.+?)\\\\(?:\\bottomrule)?$")
in_acad = False
for line in src.splitlines():
    if line.startswith(r"\pagechapter{Vocabulary for"):
        in_acad = True; continue
    if line.startswith(r"\pagechapter{"):
        in_acad = False
    if in_acad:
        m = acad_re.match(line)
        if m and not line.startswith("Words &"):
            cards.append(dict(target="Academic", icon=r"\faBook", color="black!60", term=m.group(1).strip(), meaning=m.group(2).strip(), example="", kind="academic"))

assert len(cards) > 60, len(cards)

# ---- plain-text conversion for the import file ----
def plain(t):
    t = re.sub(r"\s*\((?:page|p\.\\,)\s*\\pageref\{\w+\}\)", "", t)
    t = re.sub(r"\s*on page \\pageref\{\w+\}", "", t)
    t = re.sub(r"\s*\\pageref\{\w+\}", "", t)
    t = t.replace(r"\newline", " ")
    subs = [
        (r"$6\mathrm{CO_2}+6\mathrm{H_2O}+\text{light}$", "6CO₂ + 6H₂O + light"),
        (r"$\to\mathrm{C_6H_{12}O_6}+6\mathrm{O_2}$", "→ C₆H₁₂O₆ + 6O₂"),
        (r"$\Delta N=(B+I)-(D+E)$", "ΔN = (B + I) − (D + E)"),
        (r"$^\circ$", "°"), (r"($K$)", "(K)"), (r"$K$", "K"), (r"$\to$", "→"),
        ("``", "“"), ("''", "”"), ("---", "—"), ("--", "–"), (r"\,", " "), (r"\ ", " "),
        (r"\%", "%"), (r"\&", "&"),
    ]
    for a, b in subs:
        t = t.replace(a, b)
    t = re.sub(r"\\textit\{([^}]*)\}", r"\1", t)
    t = re.sub(r"\\textbf\{([^}]*)\}", r"\1", t)
    t = re.sub(r"\{\\small (.*?)\}", r"\1", t)
    t = re.sub(r"\s+", " ", t).strip()
    assert "\\" not in t, t
    return t

OUT_TSV.parent.mkdir(parents=True, exist_ok=True)
with OUT_TSV.open("w") as f:
    f.write("#separator:tab\n#html:false\n#columns:Front\tBack\tTags\n")
    for c in cards:
        back = plain(c["meaning"])
        if c["example"]:
            back += " — Example: " + plain(c["example"])
        f.write("%s\t%s\tecology %s\n" % (plain(c["term"]), back, c["target"].lower()))

# ---- printable fold-over cards ----
preamble = src[: src.index(r"\begin{document}")]
# drop document-specific header/hyperref title bits; keep fonts, colors, icons, macros
preamble = preamble.replace(r"\hypersetup{colorlinks=true,linkcolor=forest,urlcolor=blue,pdftitle={Shawn's Ecology Study Book 1A to 2C},pdfauthor={Prepared for Shawn}}",
                            r"\hypersetup{colorlinks=true,linkcolor=forest,urlcolor=blue,pdftitle={Ecology flashcards 1A to 2C},pdfauthor={Prepared for Shawn}}")
preamble = preamble.replace(r"\fancyhead[R]{\small\sffamily ECOLOGY\quad 1A--2C}", r"\fancyhead[R]{\small\sffamily ECOLOGY FLASHCARDS\quad 1A--2C}")
preamble = re.sub(r"\\usepackage\[margin=[^\]]*\]\{geometry\}", r"\\usepackage[margin=0.5in,headheight=15pt,headsep=8pt]{geometry}", preamble)

W, H = 9.5, 5.9   # card size in cm (a US-letter page holds 2 x 4 with 0.5 in margins)
COLS, ROWS = 2, 4
per_page = COLS * ROWS

def esc(t):
    t = t.replace(r"\newline", " ")
    t = re.sub(r"\s*\((?:page|p\.\\,)\s*\\pageref\{\w+\}\)", "", t)
    t = re.sub(r"\s*on page \\pageref\{\w+\}", "", t)
    t = re.sub(r"\s*\\pageref\{\w+\}", "", t)
    return t

body = []
body.append(r"""\begin{document}
\thispagestyle{fancy}
{\Large\bfseries Ecology flashcards, learning targets 1A--2C\par}
\medskip
\textbf{How to use.} Cut along the solid lines and fold each card on the dashed line so the term is on one side and the meaning on the other. Say the meaning before you flip. Sort cards into ``know it'' and ``not yet'' piles and repeat the ``not yet'' pile the next day. The same cards are available as an import file for Anki or Quizlet in \texttt{output/flashcards/}.\par
\medskip
\textbf{Sets.} """ + ", ".join("%s (%d cards)" % (t, sum(1 for c in cards if c["target"] == t)) for t in ["1A","1B","1C","2A","2B","2C","Academic"]) + r""". Colors match the book: blue for evidence and biodiversity, green for life and matter, orange for regulation and population.\par
\medskip
Definitions are the same as the vocabulary pages of the study book. Terms come from the teacher's Ecology Unit Guide.
\clearpage
""")
for i in range(0, len(cards), per_page):
    chunk = cards[i:i + per_page]
    body.append(r"\noindent\begin{tikzpicture}[x=1cm,y=1cm]")
    for j, c in enumerate(chunk):
        col, row = j % COLS, j // COLS
        x0, y0 = col * W, -row * H
        body.append(r"\draw[black!35] (%.2f,%.2f) rectangle ++(%.2f,%.2f);" % (x0, y0, W, -H))
        body.append(r"\draw[black!35,dashed] (%.2f,%.2f) -- ++(%.2f,0);" % (x0, y0 - H/2, W))
        body.append(r"\node[font=\scriptsize\sffamily,text=black!50,anchor=north east] at (%.2f,%.2f) {%s};" % (x0 + W - 0.15, y0 - 0.12, c["target"]))
        body.append(r"\node[align=center,text width=%.1fcm] at (%.2f,%.2f) {\ico[%s]{%s}{22pt}\\[3pt]{\large\bfseries %s}};" % (W - 1.2, x0 + W/2, y0 - H/4, c["color"], c["icon"], esc(c["term"])))
        back = r"{\footnotesize %s}" % esc(c["meaning"])
        if c["example"]:
            back += r"\\[3pt]{\scriptsize\itshape %s}" % esc(c["example"])
        body.append(r"\node[align=center,text width=%.1fcm] at (%.2f,%.2f) {%s};" % (W - 1.0, x0 + W/2, y0 - 3*H/4, back))
    body.append(r"\end{tikzpicture}")
    body.append(r"\clearpage")
body.append(r"\end{document}")
OUT_TEX.write_text(preamble + "\n".join(body) + "\n")
print("cards:", len(cards), "| pages of cards:", -(-len(cards) // per_page))
