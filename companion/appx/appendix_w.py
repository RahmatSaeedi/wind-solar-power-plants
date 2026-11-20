"""Appendix W - the verified official-source bibliography, built from the
book's own records: the standards register (191 rows, edition and date
verified) and the three country dossiers (each fact with its source,
label and date; access date of the research).

Run from the project root:   python -m companion.appx.appendix_w
Writes companion/appx/expected/appw_*.txt.
"""
from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

from companion.appx.common import emit

ROOT = Path(__file__).resolve().parents[2]
REGISTER = ROOT / "glossary" / "standards-register.csv"
BODIES = ["IEC", "ISO", "IEEE", "UL", "NFPA", "IPC", "CENELEC", "UN"]


def rows() -> list[dict]:
    with open(REGISTER, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def natural(r: dict) -> list:
    """IEC 60076-2 before IEC 60076-10: numbers compared as numbers."""
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", r["designation"])]


def open_item(r: dict) -> bool:
    text = " ".join(r[k] for k in ("edition", "adoption_or_legal_status", "note")).lower()
    return "confirm" in text


def body_of(r: dict) -> str:
    b = r["issuing_body"]
    for k in BODIES:
        if b.startswith(k) or b.startswith("ISO/IEC") and k == "ISO":
            return k
    return "other"


def summary() -> dict:
    rs = rows()
    by = Counter(body_of(r) for r in rs)
    dates = sorted(r["date_verified"] for r in rs if r["date_verified"])
    n_open = sum(open_item(r) for r in rs)
    lines = [f"standards register: {len(rs)} rows; verified between {dates[0]} and {dates[-1]}",
             "  by issuing body: " + ", ".join(f"{k} {v}" for k, v in by.most_common()),
             f"  rows marked 'confirm' (edition, status or a reported revision): {n_open}",
             "  each row: designation, edition with amendments, official catalogue page,",
             "  date verified; '*' marks a row with an item to confirm"]
    emit("appw_summary", lines)
    return dict(n=len(rs), by=dict(by), open=n_open)


def standards() -> None:
    rs = rows()
    groups = defaultdict(list)
    for r in rs:
        groups[body_of(r)].append(r)
    lines = []
    for body in BODIES + ["other"]:
        if not groups.get(body):
            continue
        lines.append(f"== {body} ({len(groups[body])})")
        for r in sorted(groups[body], key=natural):
            mark = "*" if open_item(r) else " "
            lines.append(f"{mark}{r['id']}  {r['designation']}, {r['edition']}"
                         f"  [{r['date_verified']}]")
            lines.append(f"    {r['title']}")
            lines.append(f"    {r['official_source']}")
    emit("appw_standards", lines, hyphens=False)


def countries() -> dict:
    from companion.ch55 import sources as ir
    from companion.ch56 import sources as af
    from companion.ch57 import sources as tj
    out = {}
    lines = []
    for mod in (ir, af, tj):
        by_src = defaultdict(list)
        for f in mod.FACTS:
            by_src[f["source"]].append(f)
        st = Counter(f["status"] for f in mod.FACTS)
        sec = sum(1 for f in mod.FACTS if f["secondary"])
        lines.append(f"== {mod.COUNTRY}: {len(mod.FACTS)} statements from {len(by_src)} sources,"
                     f" accessed {mod.ACCESSED.isoformat()}")
        lines.append("   " + ", ".join(f"{k} {v}" for k, v in st.most_common())
                     + f"; secondary source only: {sec}")
        for src, fs in sorted(by_src.items(), key=lambda kv: (-len(kv[1]), kv[0])):
            ids = ", ".join(f["id"] for f in fs)
            labels = "/".join(sorted({f["status"] for f in fs}))
            dated = sorted({f["doc_date"].isoformat() for f in fs if f["doc_date"]})
            when = dated[-1] if dated else "undated"
            name = src if src.strip() not in ("-", "not found", "") else "(no source found)"
            lines.append(f"  {name}")
            lines.append(f"      {ids} | {labels} | latest text {when}")
        out[mod.COUNTRY] = dict(facts=len(mod.FACTS), sources=len(by_src), status=dict(st))
    emit("appw_countries", lines)
    return out


def main() -> None:
    summary()
    standards()
    countries()


if __name__ == "__main__":
    main()
