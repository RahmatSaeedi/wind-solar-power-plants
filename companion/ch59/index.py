"""Chapter 59, the dossier index: for each of the 14 items, the chapters,
decisions, documents and open unknowns that feed it, and the checks that
every decision and every chapter belongs to some item.

Run from the project root:   python -m companion.ch59.index
"""
from __future__ import annotations

from companion.ch59 import sources as src
from companion.ch59.common import csv, emit


def index() -> dict:
    rows, all_docs, all_unk = [], set(), set()
    for n, title, chs in src.ITEMS:
        docs = sorted({d for c in chs for d in src.records(c)["docs"]})
        unk = sorted({u for c in chs for u in src.records(c)["unknowns"]})
        dec = src.decisions_of(chs)
        all_docs |= set(docs)
        all_unk |= set(unk)
        rows.append((n, title, chs, dec, docs, unk))
    lines = ["the staged dossier of Plant P: 14 items built from the chapters",
             "   #  ch  dec  docs  unk  title"]
    for n, title, chs, dec, docs, unk in rows:
        lines.append(f"  {n:2d} {len(chs):3d} {len(dec):4d} {len(docs):5d} {len(unk):4d}"
                     f"  {title[:50]}")
    covered = {c for _, _, chs in src.ITEMS for c in chs}
    missing_ch = [c for c in range(1, 59) if c not in covered]
    all_dec = {f"D-{k:03d}" for k in src.DECISION_CH}
    used_dec = {d for r in rows for d in r[3]}
    lines += [f"  distinct documents {len(all_docs)}, unknowns named {len(all_unk)},"
              f" decisions {len(used_dec)} of {len(all_dec)}",
              f"  chapters in no item: {', '.join(map(str, missing_ch)) or 'none'};"
              f" decisions in no item: {', '.join(sorted(all_dec - used_dec)) or 'none'}",
              "  an item with no document or no decision would be a gap in",
              "  the dossier; the index is rebuilt from the chapters each time"]
    emit("x_index", lines)
    csv("ch59-index.csv", "k,docs,unk,dec",
        [(n, len(docs), len(unk), len(dec)) for n, _, _, dec, docs, unk in rows])
    return dict(rows=rows, docs=len(all_docs), unk=len(all_unk), dec=len(used_dec),
                missing_ch=missing_ch, missing_dec=sorted(all_dec - used_dec))


def main() -> dict:
    return index()


if __name__ == "__main__":
    main()
