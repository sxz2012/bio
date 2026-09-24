# Learning-target study guides and mock exams

One study guide and one AP-style mock exam per learning target in the teacher's unit guide. Everything is written in LaTeX. Each guide can be read without the textbook: it copies in the relevant *Miller & Levine Biology* pages, highlights the key sentences, and puts a numbered note beside each highlight. Then come other sources (mainly *Campbell Biology*), a summary, the vocabulary in detail with diagrams, and full answers to the teacher's study questions.

| Target | Study guide | Mock exam | PDFs (local only) |
|---|---|---|---|
| 1A Academic and personal skills | [1A/guide.tex](1A/guide.tex) | [1A/exam.tex](1A/exam.tex) | `output/private/1A-study-guide.pdf`, `1A-mock-exam.pdf` |
| 1B What is life? Metabolism, homeostasis, feedback | [1B/guide.tex](1B/guide.tex) | [1B/exam.tex](1B/exam.tex) | `output/private/1B-study-guide.pdf`, `1B-mock-exam.pdf` |

## Folder layout

```
study-guides/
  README.md
  build.py          prepares book crops and highlight positions, then runs LaTeX
  latex/            shared design: preamble.tex, guide.sty, exam.sty, blank-grid.tex
  1A/
    guide.tex       study guide
    exam.tex        mock exam
    figures/        TikZ/pgfplots diagrams used by this target (exam-*.tex are the exam's)
  1B/               same as 1A
  build/            git-ignored: cropped figures, copied textbook pages, highlight positions, LaTeX logs
```

To add a target (say 1C), create `1C/guide.tex`, `1C/exam.tex`, and `1C/figures/`, copying the top lines of 1B's files.

## Build

```sh
python3 units/ecology/study-guides/build.py            # every target's guide and exam
python3 units/ecology/study-guides/build.py 1B         # one target
python3 units/ecology/study-guides/build.py 1B/exam    # one document
```

Needs `tectonic` and poppler (`pdfseparate`, `pdftotext`, `pdftoppm`). The book PDFs must be in `books/`. Before compiling, `build.py` crops the book figures and locates each textbook note's highlight on the scan; LaTeX does the rest.

## Writing a study guide (`<T>/guide.tex`)

Macros are in `latex/guide.sty` and `latex/preamble.tex`.

| Macro | Use |
|---|---|
| `\guidetitle{1A}{Title}{learning target statement}` | title block |
| `\notelegend` | the color key for the notes |
| `\begin{tbpage}{12}{Lesson 1.1 What Is Science?}{intro}` … `\end{tbpage}` | one annotated textbook page (printed page number), shown as a landscape page: the scan on the left, notes on the right |
| `\tbnote{kind}{label}{find}{to}{text}` | a note on that page. `kind`: `key`, `vocab`, `tip`, `watch`, `link` (sets the color); `label`: heading, empty = the kind's default; `find`/`to`: the words to highlight, exactly as printed (`to` may be empty; `find` empty = a note with no highlight) |
| `\drawfig{name}` | a TikZ/pgfplots figure from the target's `figures/name.tex` |
| `\bookcrop[width]{id}{book}{page}{x0 y0 x1 y1}{Figure 1.23}{caption}` | a figure cropped from a book: `book` is `C` (Campbell, preferred: much sharper) or `ML`; crop box in points from the page's top-left |

`build.py` matches each `find` phrase against the scan's OCR text. If a phrase isn't found, the build stops and names it. OCR sometimes splits a heading from its text or misreads a character (for example "contro! group"), so pick a nearby phrase that the OCR read cleanly. Book page = PDF page − 34 (Miller & Levine), − 35 (Campbell).

## Writing a mock exam (`<T>/exam.tex`)

Each exam has 16 data-based multiple-choice questions, four free-response questions (one long, three short), and an answer key on a new page. Macros are in `latex/exam.sty`.

| Macro | Use |
|---|---|
| `\examtitle{1A}{Title}` | title block |
| `\examsection{…}`, `\questiongroup{…}`, `\frq{…}` | section, "Questions 4–7 refer to …", free-response heading |
| `\begin{mcq}{5} stem \begin{choices}\item …\end{choices}\end{mcq}` | multiple-choice question; choices are lettered (A)–(D) automatically |
| `\begin{parts}\item …\end{parts}` | free-response parts (a), (b), … |
| `\drawfig{name}` (or `\examfig`), `\graphgrid`, `\bookcrop{…}` | figures, a blank graphing grid |
| `\answerkey`, `\answer{5}{B}{short}`, `\skill{…}`, `\begin{whynot}\wrong{(A)}{reason}\end{whynot}`, `\modelanswer` | answer key |

`latex/preamble.tex` holds the shared page design, colors, figure macros, and the annotated-page layout (each note sits level with its highlight where possible).

## Copyright

The PDFs contain pages and figures copied from the textbooks for Shawn's personal study. `output/private/` and `build/` are git-ignored so they are never pushed to GitHub. Keep it that way.
