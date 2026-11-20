"""Chapter 59 sources: the 14 items of the staged dossier (handoff), the
chapters that feed each item, and a reader of every chapter's own
deliverable section (documents, decisions, unknowns) - so the dossier
index is built from the book, not typed again.
"""
from __future__ import annotations

import glob
import re
from functools import lru_cache
from pathlib import Path

from companion.ch59 import common

ROOT = common.HERE.parents[1]

# [start: items]
ITEMS = [   # (number, short title, chapters that feed it)
    (1, "data pack, requirements, assumptions, changes",
     [1, 2, 3, 4, 5, 17, 38]),
    (2, "resource-measurement and data-quality plan", [12, 13]),
    (3, "site, layout, water balance and stewardship", [14, 29]),
    (4, "yield model, losses and uncertainty", [15, 16]),
    (5, "architecture and equipment selection", [8, 9, 10, 11, 18, 19]),
    (6, "one-lines, auxiliaries, load lists, schedules",
     [6, 7, 23, 24, 25, 26, 27]),
    (7, "civil, mech., E&S, welfare, security, emergency",
     [29, 30, 31, 32, 33]),
    (8, "grid study, export, forecast/dispatch, services", [17, 20, 28]),
    (9, "procurement specifications and quality plan", list(range(39, 49))),
    (10, "construction, inspection, commissioning, handover", [49, 50]),
    (11, "operation, maintenance, spares, data governance",
     [34, 35, 36, 51, 52]),
    (12, "RAM basis, critical equipment, verification plan", [37, 52]),
    (13, "economics, finance, risk, footprint, retirement", [21, 22, 33, 53]),
    (14, "Iran, Afghanistan, Tajikistan appendices", [54, 55, 56, 57, 58]),
]
# [end: items]

# decision -> chapter where it was taken (from the chapters' deliverable sections)
DECISION_CH = {1: 1, 2: 6, 3: 6, 4: 1, 5: 2, 6: 2, 7: 3, 8: 4, 9: 5, 10: 7, 11: 8, 12: 9,
               13: 10, 14: 10, 15: 11}
DECISION_CH.update({k: k - 4 for k in range(16, 63)})


def chapter_text(n: int) -> str:
    files = sorted(glob.glob(str(ROOT / "chapters" / f"{n:02d}-*.qmd")))
    files += sorted(glob.glob(str(ROOT / "chapters" / f"{n:02d}" / "*.qmd")))
    return "\n".join(Path(f).read_text(encoding="utf-8") for f in files)


@lru_cache(maxsize=None)
def records(n: int) -> dict:
    """Documents and unknowns named in chapter n's deliverable section."""
    text = chapter_text(n)
    m = re.search(r"\{#sec-ch%02d(?:-[a-z])?-deliverable\}" % n, text)   # ch 1: -c-
    seg = ""
    if m:
        seg = text[m.end():]
        nxt = re.search(r"\n## ", seg)
        seg = seg[:nxt.start()] if nxt else seg
    docs = sorted(set(re.findall(r"PLP-[A-Z]{3}-[A-Z]{3}-\d{4}", seg)))
    unk = sorted(set(re.findall(r"U-\d{3}", seg)))
    return dict(docs=docs, unknowns=unk, found=bool(m))


def decisions_of(chapters: list[int]) -> list[str]:
    return [f"D-{k:03d}" for k, ch in sorted(DECISION_CH.items()) if ch in chapters]
