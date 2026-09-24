#!/usr/bin/env python3
"""Build the study guides and mock exams. The sources are LaTeX; this script prepares what LaTeX can't do alone.

Usage:  python3 units/ecology/study-guides/build.py 1A 1B 1A-exam 1B-exam

  <T>-guide.tex         study guide  -> output/private/<T>-study-guide.pdf
  exams/<T>-exam.tex    mock exam    -> output/private/<T>-mock-exam.pdf

Before compiling, the script
  - crops every \\bookcrop{id}{book}{page}{x0 y0 x1 y1}… figure from the book PDFs into build/figs/<id>.png, and
  - for each \\begin{tbpage}{page}… in a guide, copies that textbook page into build/pages/ and finds each
    \\tbnote's find/to phrase in the scan's OCR text layer (pdftotext -bbox-layout). The highlight boxes
    go to build/anchors/<T>.tex, which the guide loads.
The PDFs contain copied textbook pages, so output/private/ and build/ are git-ignored.
"""
import html
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BUILD = HERE / "build"
OUT = ROOT / "output" / "private"
BOOKS = {
    "ML": dict(pdf=ROOT / "books" / "Biology (Miller, Kenneth R. (Kenneth Raymond) etc.) (z-library.sk, 1lib.sk, z-lib.sk).pdf",
               offset=34),  # PDF page = printed page + 34
    "C": dict(pdf=ROOT / "books" / "Campbell Biology (Lisa Urry, Kerry Hull, Peter Minorsky etc.) (z-library.sk, 1lib.sk, z-lib.sk).pdf",
              offset=35),
}


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


# ---------------------------------------------------------------- reading macro calls in the .tex

def strip_comments(tex):
    return re.sub(r"(?<!\\)%.*", "", tex)


def read_args(tex, pos, n, optional=False):
    """Read an optional [..] and n {..} arguments starting at pos. Returns (opt, [args], end)."""
    def skip(p):
        while p < len(tex) and tex[p] in " \t\n":
            p += 1
        return p
    opt = None
    pos = skip(pos)
    if optional and pos < len(tex) and tex[pos] == "[":
        end = tex.index("]", pos)
        opt, pos = tex[pos + 1:end], end + 1
    args = []
    for _ in range(n):
        pos = skip(pos)
        if tex[pos] != "{":
            raise ValueError(f"expected {{ at: {tex[pos:pos + 60]!r}")
        depth, start = 0, pos
        while True:
            c = tex[pos]
            if c == "\\":
                pos += 2
                continue
            depth += c == "{"
            depth -= c == "}"
            pos += 1
            if depth == 0:
                break
        args.append(tex[start + 1:pos - 1])
    return opt, args, pos


def calls(tex, name, n, optional=False):
    for m in re.finditer(r"\\" + name + r"(?![A-Za-z])", tex):
        yield read_args(tex, m.end(), n, optional)


# ---------------------------------------------------------------- book figures

def crop_figures(tex):
    """Crop every \\bookcrop[width]{id}{book}{page}{x0 y0 x1 y1}{label}{caption} into build/figs/<id>.png."""
    for _, (fid, book, page, crop, _label, _cap), _ in calls(tex, "bookcrop", 6, optional=True):
        b = BOOKS[book]
        x0, y0, x1, y1 = (float(v) for v in crop.split())
        png = BUILD / "figs" / f"{fid}.png"
        stamp, key = png.with_suffix(".key"), f"{book} {page} {crop}"
        if png.exists() and stamp.exists() and stamp.read_text() == key:
            continue
        png.parent.mkdir(parents=True, exist_ok=True)
        dpi = 200
        k = dpi / 72
        subprocess.run(["pdftoppm", "-f", str(int(page) + b["offset"]), "-l", str(int(page) + b["offset"]), "-r", str(dpi),
                        "-x", str(round(x0 * k)), "-y", str(round(y0 * k)),
                        "-W", str(round((x1 - x0) * k)), "-H", str(round((y1 - y0) * k)),
                        "-png", "-singlefile", str(b["pdf"]), str(png.with_suffix(""))], check=True)
        stamp.write_text(key)


# ---------------------------------------------------------------- annotated textbook pages

def page_words(pdf, pdf_page):
    """Words on one page in reading order, with their line and block boxes (PDF points, y down)."""
    xml = subprocess.run(["pdftotext", "-f", str(pdf_page), "-l", str(pdf_page), "-bbox-layout", str(pdf), "-"],
                         capture_output=True, text=True, check=True).stdout
    xml = re.sub(r"<!DOCTYPE[^>]*>", "", xml).replace(' xmlns="http://www.w3.org/1999/xhtml"', "")
    xml = re.sub(r"<head>.*?</head>", "", xml, flags=re.S)
    page = ET.fromstring(xml).find(".//page")
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


def unescape(s):
    return re.sub(r"\\([&%$#_{}])", r"\1", s)


def write_anchors(target, tex):
    """Copy each tbpage's textbook page and locate its notes; write build/anchors/<T>.tex."""
    out, problems, notes = [], [], 0
    for m in re.finditer(r"\\begin\{tbpage\}", tex):
        _, (page, _lesson, _intro), pos = read_args(tex, m.end(), 3)
        body = tex[pos:tex.index(r"\end{tbpage}", pos)]
        book = BOOKS["ML"]
        pdf_page = int(page) + book["offset"]
        img = BUILD / "pages" / f"ML-{page}.pdf"
        if not img.exists():
            img.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(["pdfseparate", "-f", str(pdf_page), "-l", str(pdf_page), str(book["pdf"]), str(img)], check=True)
        w, h, words = page_words(book["pdf"], pdf_page)
        out.append(f"\\tbpageinfo{{{page}}}{{{img.relative_to(HERE).as_posix()}}}{{{w}}}{{{h}}}")
        for k, (_, (_kind, _label, find, to, _text), _) in enumerate(calls(body, "tbnote", 5), start=1):
            notes += 1
            find, to = unescape(find.strip()), unescape(to.strip())
            if not find:
                out.append(f"\\tbanchor{{{page}}}{{{k}}}{{-1}}{{0}}{{}}")
                continue
            m1 = find_phrase(words, find)
            if not m1:
                problems.append(f"p.{page} note {k}: cannot find {find!r}")
                continue
            i, j = m1
            if to:
                m2 = find_phrase(words, to, start=i, column=words[i]["block"])
                if not m2:
                    problems.append(f"p.{page} note {k}: cannot find end {to!r}")
                    continue
                j = m2[1]
            rects = highlight_lines(words, i, j)
            _, y0, _, y1 = rects[0]
            gutter = words[i]["block"][0]  # badge sits just left of the text column
            boxes = "".join(f"\\tbrect{{{a:.1f}}}{{{b:.1f}}}{{{c:.1f}}}{{{d:.1f}}}" for a, b, c, d in rects)
            out.append(f"\\tbanchor{{{page}}}{{{k}}}{{{(y0 + y1) / 2:.1f}}}{{{gutter:.1f}}}{{{boxes}}}")
    if problems:
        print("Annotation anchors not found (pick a phrase the OCR read cleanly):\n  " + "\n  ".join(problems), file=sys.stderr)
        sys.exit(1)
    path = BUILD / "anchors" / f"{target}.tex"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("% Generated by build.py from the tbpage/tbnote calls in the guide. Do not edit.\n" + "\n".join(out) + "\n")
    return notes


# ---------------------------------------------------------------- compile

def compile_tex(src, pdf_name):
    BUILD.mkdir(exist_ok=True)
    r = subprocess.run(["tectonic", "--keep-logs", "--outdir", str(BUILD), src.name], cwd=src.parent, capture_output=True, text=True)
    if r.returncode:
        print(r.stdout[-4000:], r.stderr[-4000:], file=sys.stderr)
        sys.exit(r.returncode)
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copy(BUILD / src.with_suffix(".pdf").name, OUT / pdf_name)
    log = (BUILD / src.with_suffix(".log").name).read_text(errors="replace").splitlines()
    return [l for l in log if "Missing character" in l or "Overfull" in l or "WARNING" in l]


def build(target):
    if target.endswith("-exam"):
        target = target.removesuffix("-exam")
        src, pdf, what = HERE / "exams" / f"{target}-exam.tex", f"{target}-mock-exam.pdf", "exam"
    else:
        src, pdf, what = HERE / f"{target}-guide.tex", f"{target}-study-guide.pdf", "study guide"
    tex = strip_comments(src.read_text())
    crop_figures(tex)
    extra = ""
    if what == "study guide":
        extra = f", {write_anchors(target, tex)} notes"
    warnings = compile_tex(src, pdf)
    print(f"{target} {what}{extra} -> {OUT / pdf}")
    for l in warnings[:20]:
        print("  warning:", l)


if __name__ == "__main__":
    for t in sys.argv[1:] or ["1A"]:
        build(t)
