"""Chapter 55: run the dossier engine on the Iran sources.

Run from the project root:   python -m companion.ch55.run
Writes companion/ch55/expected/*.txt.
"""
from __future__ import annotations

from datetime import date

from companion.ch55 import engine as en
from companion.ch55 import sources as src
from companion.ch55.common import csv, emit

TODAY = date(2026, 11, 17)


def status_csv(src, name: str) -> None:
    """Counts by topic for the stacked-bar figure (topic index 1..6)."""
    tab = en.dossier.status_by(src.FACTS)
    rows = []
    for k, t in enumerate(en.TOPICS, 1):
        r = tab.get(t, {"verified": 0, "project-dependent": 0, "to-confirm": 0})
        rows.append((k, r["verified"], r["project-dependent"], r["to-confirm"]))
    csv(name, "k,ver,dep,tbc", rows)


def main() -> dict:
    r = {}
    r["status"] = en.status_table(src, emit)
    for t in ("A", "B", "C", "E", "F", "G"):
        r[f"facts_{t}"] = en.facts_list(src, emit, t, f"{t.lower()}_facts")
    r["stale"] = en.stale(src, emit, TODAY)
    r["approvals"] = en.approvals(src, emit)
    r["grid"] = en.grid_gaps(src, emit)
    r["cert"] = en.cert(src, emit)
    r["traces"] = en.traces(src, emit)
    r["services"] = en.services(src, emit)
    r["finance"] = en.finance(src, emit)
    r["issues"] = en.issues(src, emit)
    status_csv(src, "ch55-status.csv")
    return r


if __name__ == "__main__":
    main()
