#!/usr/bin/env python3
"""Read-only checks of chapter sources: labels, references, RTL/LTR markup, figures, code.

    python tools/lint_chapter.py 6        # chapter 6 (main file + chapters/06/_*.qmd)
    python tools/lint_chapter.py          # every chapter that is not a stub, + appendices

ERRORS (exit 1)
  * a label defined twice anywhere in the book
  * @sec-/@fig-/@tbl-/@eq-/@exm-/@exr- reference to a label that is not defined
  * math wrapped in an LTR span  [$x$]{.ltr}            (breaks the PDF for some expressions)
  * raw LaTeX inside an LTR span [\\omega_0]{.ltr}
  * a space just inside inline-math dollars  $ x $      (Pandoc prints it as text)
  * Arabic yeh/kaf (ي ك) instead of Persian (ی ک)
  * a figure with only one of its two includes (html/svg and pdf), or no .tex source
  * a code include whose file does not exist
  * a link to a .qmd file (breaks the EPUB)
WARNINGS
  * Latin words in Persian prose outside an LTR span / math / code
"""
from __future__ import annotations

import argparse
import os
import re
import sys

import booklib

REF_RE = re.compile(r"(?<![\w/.-])@((?:sec|fig|tbl|eq|exm|exr|thm|def|lst)-[A-Za-z0-9_-]+)")
LTR_SPAN_RE = re.compile(r"\[([^\]\[]*)\]\{\.ltr\}")
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
DISPLAY_MATH_RE = re.compile(r"\$\$.*?\$\$", re.S)
FIG_RE = re.compile(r"!\[[^\]]*\]\(\.\./diagrams/([A-Za-z0-9_.-]+)\.(svg|pdf)\)")
INCLUDE_RE = re.compile(r"include=\"([^\"]+)\"")
QMD_LINK_RE = re.compile(r"\]\([^)\s]*\.qmd[)#]")
LATIN_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9+/.-]*[A-Za-z0-9]|[A-Za-z]{2,}")
ATTR_RE = re.compile(r"\{[^{}\n]*\}")
LINK_TARGET_RE = re.compile(r"\]\([^)]*\)")
SHORTCODE_RE = re.compile(r"\{\{<.*?>\}\}")
CITE_RE = re.compile(r"\[?-?@[A-Za-z0-9_:.-]+(?:[;,]\s*-?@[A-Za-z0-9_:.-]+)*\]?")


def strip_display_math(text: str) -> str:
    return DISPLAY_MATH_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)


def lint_file(path: str, defined: set[str]) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    name = booklib.rel(path)
    with open(path, "rb") as fh:
        if fh.read(3) == b"\xef\xbb\xbf":
            # a byte-order mark hides the first line from Pandoc: an included file's
            # opening heading is then printed as plain text
            errors.append(f"{name}:1: UTF-8 byte-order mark at the start of the file")
    raw = booklib.read(path)
    text = strip_display_math(raw)
    figures: dict[str, set[str]] = {}

    in_ltr = False                    # inside a `::: {.ltr}` block (English text)
    for number, line in booklib.prose_lines(text):
        where = f"{name}:{number}"
        if line.strip().startswith("::: {.ltr}"):
            in_ltr = True
        elif in_ltr and line.strip() == ":::":
            in_ltr = False
        bare = INLINE_CODE_RE.sub("", line)
        if "ي" in bare or "ك" in bare:
            errors.append(f"{where}: Arabic yeh/kaf (ي ك); use Persian ی ک")
        if QMD_LINK_RE.search(bare):
            errors.append(f"{where}: link to a .qmd file; use @sec-... instead")
        for inner in LTR_SPAN_RE.findall(bare):
            if "$" in inner:
                errors.append(f"{where}: math inside an LTR span: [{inner}]{{.ltr}}")
            elif "\\" in inner:
                errors.append(f"{where}: raw LaTeX inside an LTR span: [{inner}]{{.ltr}}")
        math_spans = booklib.inline_math_spans(bare)
        for start, end in math_spans:
            inner = bare[start + 1:end - 1]
            if inner != inner.strip():
                errors.append(f"{where}: space just inside inline-math dollars: {bare[start:end]}")
        for label in REF_RE.findall(bare):
            if label not in defined:
                errors.append(f"{where}: reference to undefined label @{label}")
        for base, ext in FIG_RE.findall(line):
            figures.setdefault(base, set()).add(ext)
        # Latin words left in Persian prose
        probe = bare
        for start, end in reversed(math_spans):
            probe = probe[:start] + probe[end:]
        probe = LTR_SPAN_RE.sub("", probe)
        probe = SHORTCODE_RE.sub("", probe)
        probe = LINK_TARGET_RE.sub("]", probe)
        probe = ATTR_RE.sub("", probe)
        probe = CITE_RE.sub("", probe)
        if in_ltr or probe.lstrip().startswith((":::", "<", "|--", "|:-")):
            continue
        latin = [w for w in LATIN_WORD_RE.findall(probe)]
        if latin:
            warnings.append(f"{where}: Latin outside an LTR span: {' '.join(latin[:6])}")

    for number, line in enumerate(raw.splitlines(), 1):
        for target in INCLUDE_RE.findall(line):
            if line.lstrip().startswith(("```", "~~~")) and not os.path.exists(
                    os.path.join(booklib.ROOT, target)):
                errors.append(f"{name}:{number}: code include not found: {target}")

    for base, exts in figures.items():
        if exts != {"svg", "pdf"}:
            errors.append(f"{name}: figure '{base}' needs both an .svg (html) and a .pdf include")
        if not os.path.exists(os.path.join(booklib.ROOT, "diagrams", base + ".tex")):
            errors.append(f"{name}: figure '{base}' has no diagrams/{base}.tex")
    return errors, warnings


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("chapters", nargs="*", type=int)
    ap.add_argument("--all-warnings", action="store_true", help="print every warning")
    args = ap.parse_args()
    outline = booklib.load_outline()

    # labels: book-wide, because references cross chapters
    defined: dict[str, str] = {}
    errors: list[str] = []
    for path in booklib.all_source_files(outline):
        for label, number in booklib.labels_in(path):
            here = f"{booklib.rel(path)}:{number}"
            if label in defined:
                errors.append(f"{here}: label {label} is already defined at {defined[label]}")
            else:
                defined[label] = here

    targets: list[str] = []
    for ch in booklib.chapters(outline):
        if args.chapters:
            if int(ch["n"]) in args.chapters:
                targets += booklib.chapter_files(ch)
        elif ch.get("status") != "planned":
            targets += booklib.chapter_files(ch)
    if not args.chapters:
        targets += [os.path.join(booklib.ROOT, "index.qmd")] + booklib.appendix_files(outline)

    warnings: list[str] = []
    for path in targets:
        if os.path.exists(path):
            e, w = lint_file(path, set(defined))
            errors += e
            warnings += w

    for line in errors:
        print("ERROR  " + line)
    shown = warnings if args.all_warnings else warnings[:25]
    for line in shown:
        print("warn   " + line)
    if len(warnings) > len(shown):
        print(f"warn   ... and {len(warnings) - len(shown)} more (--all-warnings)")
    print(f"\n{len(targets)} file(s), {len(defined)} labels in the book: "
          f"{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
