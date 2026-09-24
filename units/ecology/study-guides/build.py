#!/usr/bin/env python3
"""Build a learning-target study guide PDF: annotated textbook pages plus the Markdown guide.

Usage:  python3 units/ecology/study-guides/build.py 1A [1B ...]

Inputs (per target, in this folder):
  <T>.md              the study guide text (summary, vocabulary, answers)
  pages/<T>.yaml      which textbook pages to copy in, what to highlight, and the notes
Output:
  output/private/<T>-study-guide.pdf   (git-ignored: it contains copied textbook pages)

Highlights are placed with the scan's OCR text layer (pdftotext -bbox-layout), so a note's
`find` / `to` phrases must match the words printed on that page.
"""
import html
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BUILD = HERE / "build"
OUT = ROOT / "output" / "private"
BOOKS = {
    "ML": dict(
        pdf=ROOT / "books" / "Biology (Miller, Kenneth R. (Kenneth Raymond) etc.) (z-library.sk, 1lib.sk, z-lib.sk).pdf",
        offset=34,  # PDF page = book page + 34
        name="Miller \\& Levine Biology",
    ),
    "C": dict(
        pdf=ROOT / "books" / "Campbell Biology (Lisa Urry, Kerry Hull, Peter Minorsky etc.) (z-library.sk, 1lib.sk, z-lib.sk).pdf",
        offset=35,
        name="Campbell Biology",
    ),
}
KINDS = {  # note kind -> (color name, label)
    "key": ("keyc", "Key idea"),
    "vocab": ("vocabc", "Vocabulary"),
    "tip": ("tipc", "Make it make sense"),
    "watch": ("watchc", "Watch out"),
    "link": ("linkc", "Connection"),
}


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def tex_escape(s):
    """Escape plain note text for LaTeX; **bold** and *italic* are supported."""
    s = s.replace("\\", r"\textbackslash{}")
    for a, b in [("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"), ("_", r"\_"), ("{", r"\{"), ("}", r"\}"),
                 ("~", r"\textasciitilde{}"), ("^", r"\textasciicircum{}")]:
        s = s.replace(a, b)
    s = s.replace(r"\textbackslash\{\}", r"\textbackslash{}")
    s = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", s)
    s = re.sub(r"\*(.+?)\*", r"\\emph{\1}", s)
    s = s.replace("→", r"$\rightarrow$").replace("≈", r"$\approx$")
    s = re.sub(r"([A-Za-z)])₂", r"\1\\textsubscript{2}", s)
    return s


# ---------------------------------------------------------------- textbook pages

def page_words(pdf, pdf_page):
    """Words on one page in reading order, with their line and block boxes (PDF points, y down)."""
    xml = subprocess.run(["pdftotext", "-f", str(pdf_page), "-l", str(pdf_page), "-bbox-layout", str(pdf), "-"],
                         capture_output=True, text=True, check=True).stdout
    xml = re.sub(r"<!DOCTYPE[^>]*>", "", xml).replace(' xmlns="http://www.w3.org/1999/xhtml"', "")
    xml = re.sub(r"<head>.*?</head>", "", xml, flags=re.S)
    root = ET.fromstring(xml)
    page = root.find(".//page")
    w, h = float(page.get("width")), float(page.get("height"))
    words = []
    for bi, block in enumerate(page.iter("block")):
        bbox = tuple(float(block.get(k)) for k in ("xMin", "yMin", "xMax", "yMax"))
        for li, line in enumerate(block.iter("line")):
            for word in line.iter("word"):
                t = norm(html.unescape(word.text or ""))
                if t:
                    words.append(dict(t=t, line=(bi, li), block=bbox,
                                      box=tuple(float(word.get(k)) for k in ("xMin", "yMin", "xMax", "yMax"))))
    return w, h, words


def same_column(a, b):
    """True if two blocks overlap horizontally by at least half of the narrower one."""
    overlap = min(a[2], b[2]) - max(a[0], b[0])
    return overlap >= 0.5 * min(a[2] - a[0], b[2] - b[0])


def find_phrase(words, phrase, start=0, column=None):
    """(i, j): first match of `phrase` from word `start` on, skipping words in other columns.

    OCR may split or merge words, so matching works on the concatenated normalized text.
    Returns the index of the first and last matched words.
    """
    target = norm(phrase)
    for i in range(start, len(words)):
        col = column or words[i]["block"]
        if not same_column(words[i]["block"], col):
            continue
        acc, j = "", i
        for k in range(i, min(len(words), i + 400)):
            if not same_column(words[k]["block"], col):
                continue
            acc += words[k]["t"]
            j = k
            if len(acc) >= len(target) or not target.startswith(acc):
                break
        if acc.startswith(target):
            return i, j
    return None


def highlight_lines(words, i, j):
    """One rectangle per text line between words i..j, restricted to the column the phrase starts in."""
    col = words[i]["block"]
    lines = {}
    for w in words[i: j + 1]:
        if not same_column(w["block"], col):
            continue  # sidebar text that the OCR interleaved with the paragraph
        x0, y0, x1, y1 = w["box"]
        if w["line"] in lines:
            a = lines[w["line"]]
            lines[w["line"]] = (min(a[0], x0), min(a[1], y0), max(a[2], x1), max(a[3], y1))
        else:
            lines[w["line"]] = (x0, y0, x1, y1)
    return sorted(lines.values(), key=lambda r: (r[1], r[0]))


def textbook_page_tex(spec, target, counter):
    book = BOOKS[spec.get("book", "ML")]
    pdf_page = spec["page"] + book["offset"]
    img = BUILD / "pages" / f"{spec.get('book', 'ML')}-{spec['page']}.pdf"
    if not img.exists():
        img.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["pdfseparate", "-f", str(pdf_page), "-l", str(pdf_page), str(book["pdf"]), str(img)], check=True)
    w, h, words = page_words(book["pdf"], pdf_page)

    out = [f"\\textbookpage{{{img.relative_to(BUILD).as_posix()}}}{{{w}}}{{{h}}}"
           f"{{{tex_escape(spec['lesson'])}}}{{{spec['page']}}}{{{tex_escape(spec.get('intro', ''))}}}{{%"]
    notes_tex = []
    problems = []
    for note in spec.get("notes", []):
        counter[0] += 1
        n = counter[0]
        color = KINDS[note.get("kind", "key")][0]
        label = note.get("label", KINDS[note.get("kind", "key")][1])
        if "find" in note:
            m = find_phrase(words, note["find"])
            if not m:
                problems.append(f"p.{spec['page']}: cannot find {note['find']!r}")
                continue
            i, j = m
            if "to" in note:
                m2 = find_phrase(words, note["to"], start=i, column=words[i]["block"])
                if not m2:
                    problems.append(f"p.{spec['page']}: cannot find end {note['to']!r}")
                    continue
                j = m2[1]
            rects = highlight_lines(words, i, j)
            for x0, y0, x1, y1 in rects:
                out.append(f"  \\hl{{{color}}}{{{x0:.1f}}}{{{y0:.1f}}}{{{x1:.1f}}}{{{y1:.1f}}}%")
            _, y0, _, y1 = rects[0]
            gutter = words[i]["block"][0]  # badge sits just left of the text column, not on the text
            out.append(f"  \\badge{{{color}}}{{{n}}}{{{gutter:.1f}}}{{{(y0 + y1) / 2:.1f}}}%")
            anchor_y = (y0 + y1) / 2
        else:
            anchor_y = -1  # page-level note: stack under the previous one
        notes_tex.append(f"  \\addnote{{{color}}}{{{n}}}{{{tex_escape(label)}}}{{{anchor_y:.1f}}}{{{tex_escape(note['text'])}}}%")
    out.append("}{%")
    out += notes_tex
    out.append("}")
    return "\n".join(out), problems


# ---------------------------------------------------------------- Markdown body

def md_sections(md):
    """Split the guide into (intro, parts) where parts is a list of (heading, body)."""
    chunks = re.split(r"^## ", md, flags=re.M)
    intro, parts = chunks[0], []
    for c in chunks[1:]:
        head, _, body = c.partition("\n")
        parts.append((head.strip(), body))
    return intro, parts


def book_figure(fid, fig):
    """Crop a figure from a book page (crop box in points from the page's top-left) and return LaTeX for it."""
    book = BOOKS[fig["book"]]
    png = BUILD / "figs" / f"{fid}.png"
    x0, y0, x1, y1 = fig["crop"]
    key = f"{fig['book']}-{fig['page']}-{x0}-{y0}-{x1}-{y1}"
    stamp = png.with_suffix(".key")
    if not png.exists() or not stamp.exists() or stamp.read_text() != key:
        png.parent.mkdir(parents=True, exist_ok=True)
        dpi = 200
        k = dpi / 72
        subprocess.run(["pdftoppm", "-f", str(fig["page"] + book["offset"]), "-l", str(fig["page"] + book["offset"]),
                        "-r", str(dpi), "-x", str(round(x0 * k)), "-y", str(round(y0 * k)),
                        "-W", str(round((x1 - x0) * k)), "-H", str(round((y1 - y0) * k)),
                        "-png", "-singlefile", str(book["pdf"]), str(png.with_suffix(""))], check=True)
        stamp.write_text(key)
    source = f"{book['name']}, {fig.get('label', 'figure')}, p.\\,{fig['page']}"
    return png.as_posix(), tex_escape(fig.get("caption", "")), source


def figure_tex(ids, figs):
    """One book figure, or several side by side."""
    items = [book_figure(i, figs[i]) for i in ids]
    if len(items) == 1:
        (path, cap, src), w = items[0], figs[ids[0]].get("width", 0.7)
        return f"\\bookfig{{{path}}}{{{w}}}{{{cap}}}{{{src}}}"
    cols = []
    for (path, cap, src), i in zip(items, ids):
        cols.append(f"\\bookfigcol{{{0.96 / len(items):.3f}}}{{{path}}}{{{figs[i].get('height', '5cm')}}}{{{cap}}}{{{src}}}")
    return "\\bookfigrow{" + "\\hfill".join(cols) + "}"


def pandoc(md_text, figs=None):
    md_text = md_text.replace("<!-- pagebreak -->", "\n```{=latex}\n\\clearpage\n```\n")
    md_text = re.sub(r"<!-- figure: ([\w-]+) -->", lambda m: f"\n```{{=latex}}\n\\input{{{(HERE / 'figures' / m.group(1)).as_posix()}}}\n```\n", md_text)
    md_text = re.sub(r"<!-- bookfig: ([\w\- ]+?) -->", lambda m: f"\n```{{=latex}}\n{figure_tex(m.group(1).split(), figs)}\n```\n", md_text)
    tex = subprocess.run(["pandoc", "-f", "markdown+lists_without_preceding_blankline", "-t", "latex", "--wrap=preserve", "--top-level-division=section"],
                         input=md_text, capture_output=True, text=True, check=True).stdout
    tex = re.sub(r"([A-Za-z)])₂", r"\1\\textsubscript{2}", tex)
    tex = tex.replace("₂", r"\textsubscript{2}")
    return tex


def build(target):
    spec = yaml.safe_load((HERE / "pages" / f"{target}.yaml").read_text())
    md = (HERE / f"{target}.md").read_text()
    intro, parts = md_sections(md)

    # Title and "where to read" come from the Markdown intro.
    title = re.search(r"^# (.+)$", intro, re.M).group(1)
    statement = re.search(r"^> \*\*Learning target [^*]+\*\* (.+)$", intro, re.M).group(1)
    intro_body = re.sub(r"^# .+$|^> \*\*Learning target.+$|^---\s*$", "", intro, flags=re.M)

    # Part 1: the Miller & Levine excerpts are replaced by the page images; other excerpts are kept.
    body_md = []
    for head, body in parts:
        if head.startswith("Part 1"):
            subs = re.split(r"^### ", body, flags=re.M)
            kept = [s for s in subs[1:] if not s.startswith("Miller & Levine")]
            if kept:
                body_md.append("## Part 1 (continued). Other sources for this target\n\n"
                               "The class textbook pages are reproduced in full in Part 1. These excerpts cover the rest: "
                               "the reference book *Campbell Biology* and anything the class textbook leaves out.\n\n"
                               + "".join("### " + s for s in kept))
        else:
            body_md.append(f"## {head}\n{body}")

    counter, pages_tex, problems = [0], [], []
    for p in spec["pages"]:
        t, probs = textbook_page_tex(p, target, counter)
        pages_tex.append(t)
        problems += probs
    if problems:
        print("Annotation anchors not found:\n  " + "\n  ".join(problems), file=sys.stderr)
        sys.exit(1)

    doc = (HERE / "latex" / "template.tex").read_text()
    fill = {
        "TARGET": target,
        "TITLE": tex_escape(title),
        "STATEMENT": tex_escape(statement),
        "INTRO": pandoc(intro_body),
        "HOWTO": pandoc(spec.get("how_to_use", "")),
        "PAGES": "\n\n".join(pages_tex),
        "BODY": pandoc("\n\n".join(body_md).replace("\n---\n", "\n"), spec.get("figures", {})),
        "PREAMBLE": (HERE / "latex" / "preamble.tex").as_posix(),
    }
    for k, v in fill.items():
        doc = doc.replace(f"<<{k}>>", v)
    BUILD.mkdir(exist_ok=True)
    tex = BUILD / f"{target}-study-guide.tex"
    tex.write_text(doc)
    r = subprocess.run(["tectonic", "--keep-logs", "--outdir", str(BUILD), str(tex)], cwd=BUILD, capture_output=True, text=True)
    if r.returncode:
        print(r.stdout[-4000:], r.stderr[-4000:], file=sys.stderr)
        sys.exit(r.returncode)
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copy(BUILD / f"{target}-study-guide.pdf", OUT / f"{target}-study-guide.pdf")
    warn = [l for l in (BUILD / f"{target}-study-guide.log").read_text(errors="replace").splitlines()
            if "Missing character" in l or "Overfull" in l]
    print(f"{target}: {counter[0]} notes on {len(spec['pages'])} textbook pages -> {OUT / f'{target}-study-guide.pdf'}")
    for l in warn[:20]:
        print("  warning:", l)


def build_exam(target):
    """Mock AP-style exam. The source is LaTeX: exams/<T>-exam.tex (macros in latex/exam.sty).

    Book figures used with \\bookfigure{id} are defined in exams/<T>-exam.yaml; this step crops them and
    writes build/figs/<id>.tex. Output: output/private/<T>-mock-exam.pdf.
    """
    ypath = HERE / "exams" / f"{target}-exam.yaml"
    figs = (yaml.safe_load(ypath.read_text()) or {}).get("figures", {}) if ypath.exists() else {}
    for fid in figs:
        path, cap, src = book_figure(fid, figs[fid])
        (BUILD / "figs" / f"{fid}.tex").write_text(
            f"\\bookfig{{{path}}}{{{figs[fid].get('width', 0.7)}}}{{{cap}}}{{{src}}}\n")
    src_tex = HERE / "exams" / f"{target}-exam.tex"
    BUILD.mkdir(exist_ok=True)
    r = subprocess.run(["tectonic", "--keep-logs", "--outdir", str(BUILD), src_tex.name],
                       cwd=src_tex.parent, capture_output=True, text=True)
    if r.returncode:
        print(r.stdout[-4000:], r.stderr[-4000:], file=sys.stderr)
        sys.exit(r.returncode)
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copy(BUILD / f"{target}-exam.pdf", OUT / f"{target}-mock-exam.pdf")
    warn = [l for l in (BUILD / f"{target}-exam.log").read_text(errors="replace").splitlines()
            if "Missing character" in l or "Overfull" in l]
    print(f"{target} exam -> {OUT / f'{target}-mock-exam.pdf'}")
    for l in warn[:20]:
        print("  warning:", l)

if __name__ == "__main__":
    for t in sys.argv[1:] or ["1A"]:
        if t.endswith("-exam"):
            build_exam(t.removesuffix("-exam"))
        else:
            build(t)
