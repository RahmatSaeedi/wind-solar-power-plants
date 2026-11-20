#!/usr/bin/env python3
"""Print a figure's text line by line in right-to-left reading order.

    python tools/fig_words.py ch01-book-map [more names...]  > out.txt

In an RTL line the first logical word must have the LARGEST x. This lists each
line's words from the largest x to the smallest, so the printed line should
read as the sentence was written (docs/BUILD.md, "do not trust your eyes").
Output is UTF-8; the Windows console cannot show Persian, so redirect to a file.
"""
import os
import sys

import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    for name in sys.argv[1:]:
        page = pymupdf.open(os.path.join(ROOT, "diagrams", name + ".pdf"))[0]
        lines: dict[int, list] = {}
        for x0, y0, x1, y1, word, *_ in page.get_text("words"):
            lines.setdefault(round((y0 + y1) / 2 / 5), []).append((x0, word))
        print(f"== {name}")
        for key in sorted(lines):
            print("   " + "  ".join(w for _, w in sorted(lines[key], reverse=True)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
