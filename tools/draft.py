#!/usr/bin/env python3
"""Render a few chapters on their own into _draft/, leaving _book/ alone.

    python tools/draft.py 6              # chapter 6: HTML + PDF + EPUB
    python tools/draft.py 1 6 A          # chapters 1 and 6 and appendix A
    python tools/draft.py 6 --to pdf     # one format only (faster)
    python tools/draft.py 6 --no-render  # only report the page counts of the last draft

Why: `quarto render` always builds the whole book and empties _book/ first.
While a chapter is being written we want a quick PDF of that chapter alone, to
check right-to-left layout, math, tables, code and the page count against the
budget in outline/chapters.yml. This writes the scratch profile
_quarto-draft.yml (chapter list + output-dir _draft) and runs
`quarto render --profile draft`. Cross-references to chapters that are not in
the draft show as "?@sec-..." -- expected in a draft, not an error.
"""
from __future__ import annotations

import argparse
import glob
import os
import shutil
import subprocess
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import check_env  # noqa: E402
import build_all  # noqa: E402  (stale_figures)

DRAFT = os.path.join(ROOT, "_draft")
PROFILE = os.path.join(ROOT, "_quarto-draft.yml")


def outline() -> dict:
    with open(os.path.join(ROOT, "outline", "chapters.yml"), encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def resolve(keys: list[str]) -> tuple[list[dict], list[dict]]:
    out = outline()
    chapters = {str(c["n"]): c for p in out["parts"] for c in p["chapters"]}
    appendices = {str(a["id"]).upper(): a for a in out.get("appendices") or []}
    chosen_ch, chosen_ap = [], []
    for key in keys:
        if key.lstrip("0") in chapters or key in chapters:
            chosen_ch.append(chapters.get(key) or chapters[key.lstrip("0")])
        elif key.upper() in appendices:
            chosen_ap.append(appendices[key.upper()])
        else:
            sys.exit(f"draft: '{key}' is neither a chapter number nor an appendix id in the outline")
    return chosen_ch, chosen_ap


def write_profile(chapters: list[dict], appendices: list[dict]) -> None:
    lines = ["# scratch profile written by tools/draft.py -- safe to delete",
             "project:", "  output-dir: _draft", "book:", "  chapters:", "    - index.qmd"]
    lines += [f"    - chapters/{int(c['n']):02d}-{c['slug']}.qmd" for c in chapters]
    if appendices:
        lines.append("  appendices:")
        lines += [f"    - appendices/{a['id']}-{a['slug']}.qmd" for a in appendices]
    with open(PROFILE, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")


def page_report(chapters: list[dict]) -> None:
    import pymupdf
    pdfs = glob.glob(os.path.join(DRAFT, "*.pdf"))
    if not pdfs:
        print("draft: no PDF in _draft/")
        return
    doc = pymupdf.open(pdfs[0])
    # level-1 bookmarks are the chapters (parts are absent in a draft)
    marks = [(title, page) for level, title, page in doc.get_toc() if level == 1]
    print(f"\n=== pages ({os.path.basename(pdfs[0])}: {doc.page_count} in total) ===")
    budget = {c["title_fa"]: c.get("pages") for c in chapters}
    for i, (title, page) in enumerate(marks):
        end = marks[i + 1][1] if i + 1 < len(marks) else doc.page_count + 1
        want = next((b for t, b in budget.items() if t and t[:12] in title), None)
        note = f"   (budget {want})" if want else ""
        print(f"  {end - page:4d} pp  {title}{note}")


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("items", nargs="+", help="chapter numbers and/or appendix ids")
    ap.add_argument("--to", help="render one format only: pdf, html or epub")
    ap.add_argument("--no-render", action="store_true", help="only report page counts")
    args = ap.parse_args()

    chapters, appendices = resolve(args.items)
    if not args.no_render:
        env = check_env.tex_env()
        for base in build_all.stale_figures():
            code = subprocess.run([sys.executable, "tools/build_diagrams.py", base],
                                  cwd=ROOT, env=env).returncode
            if code != 0:
                sys.exit(f"draft: figure '{base}' failed to build")
        write_profile(chapters, appendices)
        quarto = shutil.which("quarto", path=env.get("PATH")) or "quarto"
        cmd = [quarto, "render", "--profile", "draft"] + (["--to", args.to] if args.to else [])
        print("$ " + " ".join(["quarto"] + cmd[1:]), flush=True)
        code = subprocess.run(cmd, cwd=ROOT, env=env).returncode
        if code != 0:
            sys.exit(f"draft: quarto render failed (exit {code})")
    page_report(chapters)
    return 0


if __name__ == "__main__":
    sys.exit(main())
