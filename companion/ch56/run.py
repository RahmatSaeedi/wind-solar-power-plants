"""Chapter 56: run the dossier engine (chapter 55) on the Afghanistan
sources, and compare equipment options against local service constraints.

Run from the project root:   python -m companion.ch56.run
Writes companion/ch56/expected/*.txt.
"""
from __future__ import annotations

from datetime import date

from companion.ch55 import engine as en
from companion.ch55.run import status_csv as _status_csv
from companion.ch56 import sources as src
from companion.ch56.common import csv, emit
from plantp import dossier

TODAY = date(2026, 11, 17)


def compare(name: str = "d_compare") -> dict:
    r = dossier.compare(src.OPTIONS, src.CONSTRAINTS)
    lines = ["equipment options against local service constraints (teaching",
             "constraints; an unknown is never a pass)",
             f"  {'option':28s} {'ok':>3s} {'fails':>6s} {'unknown':>8s}"]
    for k, v in r.items():
        lines.append(f"  {k:28s} {v['ok']:3d} {v['fails']:6d} {v['unknown']:8d}")
        for c, x in v["verdicts"].items():
            if x != "ok":
                lines.append(f"      {x:8s} {c}")
    clean = [k for k, v in r.items() if v["fails"] == 0 and v["unknown"] == 0]
    lines += [f"  options with every constraint met and known: {', '.join(clean) or 'none'}",
              "  the string inverters pass on the evidence; the turbines cannot",
              "  be judged until service capability is evidenced"]
    emit(name, lines)
    return r


def main() -> dict:
    r = {}
    r["status"] = en.status_table(src, emit)
    r["stale"] = en.stale(src, emit, TODAY)
    r["approvals"] = en.approvals(src, emit)
    r["grid"] = en.grid_gaps(src, emit)
    r["cert"] = en.cert(src, emit)
    r["traces"] = en.traces(src, emit)
    r["services"] = en.services(src, emit)
    r["finance"] = en.finance(src, emit)
    r["issues"] = en.issues(src, emit)
    r["compare"] = compare()
    tab = dossier.status_by(src.FACTS)
    rows = []
    for k, t in enumerate(en.TOPICS, 1):
        x = tab.get(t, {"verified": 0, "project-dependent": 0, "to-confirm": 0})
        rows.append((k, x["verified"], x["project-dependent"], x["to-confirm"]))
    csv("ch56-status.csv", "k,ver,dep,tbc", rows)
    return r


if __name__ == "__main__":
    main()
