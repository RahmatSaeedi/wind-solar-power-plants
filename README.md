# نیروگاه‌های هیبریدیِ بادی–خورشیدی

**Hybrid Wind–Solar Power Plants: from fundamentals to design, manufacturing, commissioning and
operation** — a technical book in Persian by **Rahmat Saeedi** (رحمت سعیدی).

The book takes a reader with a high-school background to working mastery of commercial hybrid
wind–solar plants with battery storage. One fictional teaching plant, **Plant P**, runs through
every chapter: its resource data, energy model, electrical and civil design, grid studies,
manufacturing and factory acceptance, construction, commissioning, operation, maintenance and end
of life, and finally a regulatory dossier for three countries (Iran, Afghanistan, Tajikistan).
Every number printed in the book comes from, or is checked by, the companion Python code in this
repository.

- **Read online (HTML):** <https://rahmatsaeedi.github.io/wind-solar-power-plants/>
- **Author:** [LinkedIn](https://ca.linkedin.com/in/rahmatsaeedi)

## Download

| Edition | File | Notes |
|---|---|---|
| PDF, whole book | [`_book/…خورشیدی.pdf`](_book/%D9%86%DB%8C%D8%B1%D9%88%DA%AF%D8%A7%D9%87%E2%80%8C%D9%87%D8%A7%DB%8C-%D9%87%DB%8C%D8%A8%D8%B1%DB%8C%D8%AF%DB%8C%D9%90-%D8%A8%D8%A7%D8%AF%DB%8C%E2%80%93%D8%AE%D9%88%D8%B1%D8%B4%DB%8C%D8%AF%DB%8C.pdf) | 5,614 pages, 56 MB; Persian text copies and searches correctly |
| EPUB 3 | [`_book/…خورشیدی.epub`](_book/%D9%86%DB%8C%D8%B1%D9%88%DA%AF%D8%A7%D9%87%E2%80%8C%D9%87%D8%A7%DB%8C-%D9%87%DB%8C%D8%A8%D8%B1%DB%8C%D8%AF%DB%8C%D9%90-%D8%A8%D8%A7%D8%AF%DB%8C%E2%80%93%D8%AE%D9%88%D8%B1%D8%B4%DB%8C%D8%AF%DB%8C.epub) | Apple Books, Google Play Books, Kobo; passes epubcheck |
| Kindle EPUB | [`_book/book-kindle.epub`](_book/book-kindle.epub) | for Kindle / KDP; Kindle Previewer: converts, Enhanced Typesetting supported |
| PDF, nine volumes | [`_volumes/`](_volumes/) | `hybrid-plant-book-vol1.pdf` … `vol9.pdf` (440–994 pages each) |

The same files are on the website too, e.g.
<https://rahmatsaeedi.github.io/wind-solar-power-plants/book-kindle.epub>.

| Volume | Chapters | Parts | Pages |
|---|---|---|---|
| 1 | 1–5 | I | 513 |
| 2 | 6–11 | II | 660 |
| 3 | 12–16 | III | 440 |
| 4 | 17–22 | IV | 553 |
| 5 | 23–28 | V | 612 |
| 6 | 29–37 | VI, VII | 812 |
| 7 | 38–43 | VIII | 516 |
| 8 | 44–50 | VIII | 558 |
| 9 | 51–59, appendices A–X | IX, X | 994 |

## Contents

59 chapters in ten parts, plus appendices A–X (glossary and notation, templates and forms, the
data pack, bibliography, and a mastery test for each part):

1. بخشِ یکم — اندیشیدن و محاسبه مانندِ مهندس (thinking and computing like an engineer)
2. بخشِ دوم — برق و تجهیزاتِ تبدیلِ انرژی (electricity and energy-conversion equipment)
3. بخشِ سوم — ارزیابیِ منابع و برآوردِ تولیدِ انرژی (resource assessment and energy yield)
4. بخشِ چهارم — معماریِ نیروگاه، ذخیره‌سازی و اقتصاد (plant architecture, storage and economics)
5. بخشِ پنجم — مهندسیِ تفصیلی و اتصال به شبکه (detailed engineering and grid connection)
6. بخشِ ششم — عمران، مکانیک، ایمنی، حریق و محیطِ‌زیست (civil, mechanical, safety, fire and environment)
7. بخشِ هفتم — کنترل، ارتباطات و امنیتِ سایبری (control, communications and cybersecurity)
8. بخشِ هشتم — تدارکات، تولیدِ صنعتی، اجرا و راه‌اندازی (procurement, manufacturing, construction and commissioning)
9. بخشِ نهم — بهره‌برداری، نگهداری و پایانِ عمر (operation, maintenance and end of life)
10. بخشِ دهم — انطباق با مقرراتِ کشورها و پروژهٔ پایانی (country regulations and the capstone project)

## What is in this repository

| Path | What it holds |
|---|---|
| `index.qmd`, `chapters/`, `appendices/` | the book's source (Quarto Markdown, Persian, right to left) |
| `companion/` | the companion code: the `plantp` Python package, one folder of scripts per chapter, the data pack, tests; `expected/*.txt` are the outputs quoted in the book |
| `diagrams/` | figure sources (TikZ / pgfplots) and their data; built to PDF and SVG by `tools/build_diagrams.py` |
| `glossary/` | Persian–English terms, notation, the standards register (191 standards with the date each was checked) |
| `outline/` | chapter outline and status, the plans of each chapter, the source research of chapters 55–57 |
| `theme/`, `fonts/`, `cover/` | page design, Lua filters, Vazirmatn fonts, cover |
| `tools/` | build, check and lint scripts |
| `docs/` | build guide (`BUILD.md`, `BUILD.fa.md`), the accuracy review of November 2026 (`review-2026-11/`), the original template guide (`template-README.md`) |
| `_book/` | the built editions and website (committed: see below) |
| `_volumes/` | the nine volume PDFs |

## Companion code

```bash
pip install -r requirements.txt
python -m pytest companion                  # tests of the companion code and data pack
python -m companion.ch10.examples_a         # run one chapter script from the project root
```

Scripts are run as modules from the project root. Their outputs go to
`companion/chNN/expected/` and are quoted in the book unchanged.

## Building the book

The toolchain is Quarto + LuaLaTeX (TinyTeX) + Python; [`docs/BUILD.md`](docs/BUILD.md) gives the
full setup (Persian: [`docs/BUILD.fa.md`](docs/BUILD.fa.md)).

```bash
python tools/draft.py 10 --to pdf           # one chapter -> _draft/
python tools/build_all.py                   # whole book: HTML, PDF, EPUB, Kindle, checks
python tools/build_volume.py 3 --to pdf     # one volume -> _volumes/ (after build_all, never at the same time)
```

A full build takes about seven hours, which is longer than a GitHub Actions job may run. So the
built editions in `_book/` are committed, and the workflow in `.github/workflows/build.yml` only
publishes that folder to GitHub Pages. After a rebuild, commit `_book/` (and `_volumes/`) again.

## Accuracy and the use of AI

AI was used in gathering the information for this book. To the best knowledge of the author and
reviewer, the contents are accurate. A whole-book adversarial review in November 2026 checked
formulas, physics, arithmetic, standards editions and the country statements; its method and
findings are in [`docs/review-2026-11/`](docs/review-2026-11/README.md).

Plant P is a teaching example: its values are assumptions for learning, not a recommended
design. Standards are cited by verified title and edition, and the country chapters label every
statement as verified, project-dependent or to be confirmed. Check any number or requirement
against the original source, and have licensed engineers, the authorities and the grid operator
decide, before using it on a real project.
