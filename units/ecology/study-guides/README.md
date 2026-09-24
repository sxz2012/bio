# Learning-target study guides

One study guide per learning target in the teacher's unit guide. Each guide can be read without the textbook. The PDF copies in the relevant *Miller & Levine Biology* pages, highlights the key sentences, and puts a numbered note beside each highlight. Then come the other sources (mainly *Campbell Biology*), a summary, the vocabulary in detail, and full answers to the teacher's study questions.

| Target | Guide text | Annotated pages | PDF (local only) |
|---|---|---|---|
| 1A Academic and personal skills | [1A.md](1A.md) | [pages/1A.yaml](pages/1A.yaml): textbook pp. 8–18 | `output/private/1A-study-guide.pdf` |
| 1B What is life? Metabolism, homeostasis, feedback | [1B.md](1B.md) | [pages/1B.yaml](pages/1B.yaml): textbook pp. 12, 21–25, 29, 907–908, 932 | `output/private/1B-study-guide.pdf` |

## Mock exams

AP-style practice exams, one per target: `exams/<target>-exam.md` (plus `exams/<target>-exam.yaml` for any book figures). Each has 16 data-based multiple-choice questions, four free-response questions (one long, three short), and an answer key after a page break: an answer table, an explanation of every choice, and a point-by-point scoring guide with model answers. Build with `build.py 1A-exam 1B-exam`; the PDFs go to `output/private/<target>-mock-exam.pdf`. `<!-- pagebreak -->` starts a new page.

## Files

- `<target>.md`: the guide text. Part 1 quotes the textbooks. In the PDF, the Miller & Levine quotes are replaced by the page images, and the other excerpts (Campbell) are kept.
- `pages/<target>.yaml`: which textbook pages to copy in, and each note: `find` (and optional `to`) is the sentence to highlight, `kind` sets the color (`key`, `vocab`, `tip`, `watch`, `link`), `label` overrides the heading, `text` is the note. A note without `find` is a page-level note.
- `figures/`: new TikZ diagrams, placed in the Markdown with `<!-- figure: name -->`.
- Book figures: `<!-- bookfig: id -->` (or `<!-- bookfig: id1 id2 -->` for side by side) crops a figure from a book page. Each id is defined under `figures:` in `pages/<target>.yaml` with `book` (`C` = Campbell, `ML` = Miller & Levine), `page` (book page), `crop` (`[x0, y0, x1, y1]` in points from the page's top-left), `width` or `height`, `label` (the figure number), and `caption`. **Choose Campbell figures first**, because its images are much sharper than the Miller & Levine scan. Crops go to the git-ignored `build/figs/`.
- `latex/preamble.tex`, `latex/template.tex`: page design. Each textbook page is a landscape page: the scan on the left and the notes on the right, each note level with its highlight where possible.
- `build.py`: the build.

## Build

```sh
python3 units/ecology/study-guides/build.py 1A 1B
```

Needs `tectonic`, `pandoc`, poppler (`pdfseparate`, `pdftotext`), and Python with PyYAML. The textbook PDF must be in `books/`.

The build finds each `find` phrase in the scan's OCR text layer. If a phrase isn't found, the build stops and names it. OCR sometimes splits a heading from its text or misreads a character (for example "contro! group"), so pick a nearby phrase that the OCR read cleanly. Book page = PDF page − 34.

## Copyright

The PDFs contain pages copied from the class textbook for Shawn's personal study. `output/private/` and `build/` are git-ignored so the PDFs are never pushed to GitHub. Keep it that way. The Markdown guides quote short passages with page citations.
