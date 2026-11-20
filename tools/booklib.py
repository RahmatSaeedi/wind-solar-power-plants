"""Shared helpers for the book's own checkers (check_coverage.py, lint_chapter.py)."""
from __future__ import annotations

import glob
import os
import re

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LABEL_RE = re.compile(r"\{#((?:sec|fig|tbl|eq|exm|exr|thm|def|lst)-[A-Za-z0-9_-]+)")
FENCE_RE = re.compile(r"^\s*(```+|~~~+)")


def load_outline() -> dict:
    with open(os.path.join(ROOT, "outline", "chapters.yml"), encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def chapters(outline: dict | None = None) -> list[dict]:
    outline = outline or load_outline()
    return [c for part in outline["parts"] for c in part["chapters"]]


def chapter_files(ch: dict) -> list[str]:
    """The chapter's main .qmd followed by its included section files."""
    n = int(ch["n"])
    main = os.path.join(ROOT, "chapters", f"{n:02d}-{ch['slug']}.qmd")
    parts = sorted(glob.glob(os.path.join(ROOT, "chapters", f"{n:02d}", "_*.qmd")))
    return [main] + parts


def appendix_files(outline: dict | None = None) -> list[str]:
    outline = outline or load_outline()
    return [os.path.join(ROOT, "appendices", f"{a['id']}-{a['slug']}.qmd")
            for a in outline.get("appendices") or []]


def all_source_files(outline: dict | None = None) -> list[str]:
    outline = outline or load_outline()
    files = [os.path.join(ROOT, "index.qmd")]
    for ch in chapters(outline):
        files += chapter_files(ch)
    files += appendix_files(outline)
    return [f for f in files if os.path.exists(f)]


def read(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def prose_lines(text: str):
    """Yield (line_number, line) for lines outside fenced code blocks and HTML comments."""
    in_fence, fence, in_comment = False, "", False
    for number, line in enumerate(text.splitlines(), 1):
        m = FENCE_RE.match(line)
        if m and not in_comment:
            mark = m.group(1)[0] * 3
            if not in_fence:
                in_fence, fence = True, mark
            elif mark == fence:
                in_fence = False
            continue
        if in_fence:
            continue
        if in_comment:
            if "-->" in line:
                in_comment = False
            continue
        if "<!--" in line and "-->" not in line:
            in_comment = True
            continue
        yield number, line


def labels_in(path: str) -> list[tuple[str, int]]:
    """Every {#sec-..}/{#fig-..}/... label defined in a file, with its line number.

    A figure is included twice (an .svg branch for html/epub and a .pdf branch
    for the PDF) with the same label, so a fig- label repeated inside ONE file
    counts once; the same label in two files is still a duplicate.
    """
    out, seen_fig = [], set()
    for number, line in prose_lines(read(path)):
        for label in LABEL_RE.findall(line):
            if label.startswith("fig-"):
                if label in seen_fig:
                    continue
                seen_fig.add(label)
            out.append((label, number))
    return out


def inline_math_spans(line: str) -> list[tuple[int, int]]:
    """(start, end) of every inline $...$ on a line, found left to right.

    Skips escaped dollars and display-math delimiters; an unmatched opening
    dollar is ignored.
    """
    spans, i, n = [], 0, len(line)
    while i < n:
        if line[i] == "$" and (i == 0 or line[i - 1] != "\\") and not line.startswith("$$", i):
            j = i + 1
            while j < n:
                if line[j] == "$" and line[j - 1] != "\\":
                    break
                j += 1
            if j >= n:
                break
            spans.append((i, j + 1))
            i = j + 1
        else:
            i += 1
    return spans


def rel(path: str) -> str:
    return os.path.relpath(path, ROOT).replace("\\", "/")
