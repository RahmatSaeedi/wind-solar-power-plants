#!/usr/bin/env python3
"""Find ink that runs past the page margins of a built PDF.

    python tools/check_overflow.py                 # the PDF in _draft/ (else _book/)
    python tools/check_overflow.py path/to/book.pdf
    python tools/check_overflow.py --tolerance 2   # points beyond the margin to allow

How: the margins are measured from the text layer (justified Persian prose
fills the block from margin to margin, so the most frequent line edges ARE
the margins). Each page is then RENDERED and every dark pixel outside the
margins is reported, with the text nearest to it. Measuring rendered ink, not
the text layer, matters: theme/pdf-copytext.lua shifts the text layer of some
lines by a few points while the glyphs on the page are correctly placed.
Light shading (code-block backgrounds) is ignored. Exit code 1 when anything
overflows. Output is UTF-8: redirect it to a file on Windows.
"""
from __future__ import annotations

import argparse
import collections
import glob
import os
import sys

import numpy as np
import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DPI = 72                     # one pixel per point
DARK = 160                   # 0..255; darker than this counts as ink


def find_pdf() -> str:
    for folder in ("_draft", "_book"):
        found = glob.glob(os.path.join(ROOT, folder, "*.pdf"))
        if found:
            return found[0]
    sys.exit("check_overflow: no PDF in _draft/ or _book/")


def margins(doc) -> tuple[float, float]:
    lefts, rights = collections.Counter(), collections.Counter()
    for page in doc:
        width = page.rect.width
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                x0, _, x1, _ = line["bbox"]
                if x1 - x0 > 0.5 * width:          # full-width prose lines only
                    lefts[round(x0)] += 1
                    rights[round(x1)] += 1
    return float(lefts.most_common(1)[0][0]), float(rights.most_common(1)[0][0])


def nearest_text(page, y: float) -> str:
    best, best_d = "", 1e9
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            y0, y1 = line["bbox"][1], line["bbox"][3]
            d = 0 if y0 <= y <= y1 else min(abs(y - y0), abs(y - y1))
            if d < best_d:
                best_d = d
                best = "".join(s["text"] for s in line["spans"]).strip()
    return best[:80]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pdf", nargs="?")
    ap.add_argument("--tolerance", type=float, default=3.0)
    ap.add_argument("--block", help="text block 'LEFT,RIGHT' in pt, for documents "
                    "with little full-width prose (e.g. a glossary of tables); "
                    "the book's block is 83,529")
    args = ap.parse_args()
    doc = pymupdf.open(args.pdf or find_pdf())
    if args.block:
        left, right = (float(x) for x in args.block.split(","))
    else:
        left, right = margins(doc)
    problems = 0
    for number, page in enumerate(doc, 1):
        if page.rect.width - (right - left) < 10:          # full-bleed page
            continue
        if not page.get_text().strip():                     # cover, blank page
            continue
        pix = page.get_pixmap(dpi=DPI, colorspace=pymupdf.csGRAY)
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
        ink = img < DARK
        lo = int(left - args.tolerance)
        hi = int(np.ceil(right + args.tolerance))
        outside = ink.copy()
        outside[:, max(lo, 0):min(hi, pix.width)] = False
        rows = np.where(outside.any(axis=1))[0]
        if rows.size == 0:
            continue
        # group consecutive rows into separate findings
        groups = np.split(rows, np.where(np.diff(rows) > 3)[0] + 1)
        for g in groups:
            cols = np.where(outside[g].any(axis=0))[0]
            side = "right" if cols.max() >= hi else "left"
            over = (cols.max() - right) if side == "right" else (left - cols.min())
            y = float(g.mean())
            print(f"page {number} (label {page.get_label() or number}), y={y:.0f}, "
                  f"{side} +{over:.0f}pt: {nearest_text(page, y)}")
            problems += 1
    print(f"\ntext block {left:.0f}-{right:.0f} pt; {problems} overflow(s) in {doc.page_count} pages")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
