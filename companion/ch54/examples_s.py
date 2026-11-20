"""Chapter 54, round s: one idea written three ways (power factor, tan phi,
Q/Pmax), requirements needed by each project gate, how often the rules
change (a regulatory watch), and the register by discipline.

Run from the project root:   python -m companion.ch54.examples_s
Writes companion/ch54/expected/s_*.txt and diagrams/data/ch54-forms.csv.
Fictional teaching data (A-546 to A-548).
"""
from __future__ import annotations

import math
from datetime import date

from companion.ch54 import sources as src
from companion.ch54.common import csv, emit
from plantp import compliance as cp

P_RATED = 100.0

GATES = ("financial close", "notice to proceed", "first energisation",
         "commercial operation")
NEEDED = {   # requirement -> gate by which its source must be verified
    "Z-013": "financial close", "Z-014": "financial close",
    "Z-006": "notice to proceed", "Z-001": "notice to proceed",
    "Z-002": "notice to proceed", "Z-009": "notice to proceed",
    "Z-010": "notice to proceed", "Z-004": "first energisation",
    "Z-005": "first energisation", "Z-012": "notice to proceed",
    "Z-011": "first energisation", "Z-003": "notice to proceed",
    "Z-007": "notice to proceed", "Z-008": "financial close",
}
CHANGES = [date(2022, 4, 1), date(2024, 7, 1), date(2025, 7, 1), date(2026, 9, 1)]
SINCE = date(2019, 3, 1)       # GCZ 2019 edition: start of the record
COD = date(2028, 9, 1)

DISCIPLINE = {   # requirement -> discipline
    "Z-001": "grid", "Z-002": "grid", "Z-003": "grid", "Z-004": "controls",
    "Z-005": "controls", "Z-006": "environment", "Z-007": "environment",
    "Z-008": "environment", "Z-009": "grid", "Z-010": "protection",
    "Z-011": "power quality", "Z-012": "electrical", "Z-013": "permits",
    "Z-014": "permits",
}


# ------------------------------------------------ s1. one idea, three forms
def forms() -> dict:
    t = math.tan(math.acos(0.95))
    rows = []
    for p in (10, 20, 50, 80, 100):
        rows.append((p, p * t, 0.33 * P_RATED))
    csv("ch54-forms.csv", "p,pf,qpmax", [(p, round(a, 2), round(b, 2))
                                         for p, a, b in
                                         [(x, x * t, 0.33 * P_RATED)
                                          for x in range(10, 101, 5)]])
    lines = ["the same 'reactive requirement' written three ways",
             f"  pf 0.95 at the POC        -> Q = P x {t:.3f} (follows P)",
             f"  tan phi 0.33              -> Q = P x 0.33 (the same, rounded)",
             f"  Q/Pmax 0.33               -> Q = {0.33 * P_RATED:.0f} Mvar at every P",
             "  P (MW)   pf 0.95   Q/Pmax 0.33"]
    lines += [f"  {p:6.0f}  {a:8.1f}  {b:10.1f}" for p, a, b in rows]
    lines += [f"  at 20 MW the two readings differ {rows[1][2] / rows[1][1]:.1f} times:"
              " the form",
              "  of the requirement, not its headline number, sets the",
              "  design case (ch 28 used the Q/Pmax form as a placeholder)"]
    emit("s_forms", lines)
    return dict(t=t, ratio=rows[1][2] / rows[1][1])


# ------------------------------------------------ s2. what each gate needs
def gates() -> dict:
    status = {r["id"]: r["status"] for r in src.REQS
              if cp.applies(r, src.PROJECT)}
    out = {}
    lines = ["applicable requirements whose source must be verified by each gate"]
    for i, g in enumerate(GATES):
        due = [r for r, gg in NEEDED.items() if GATES.index(gg) <= i and r in status]
        block = sorted(r for r in due if status[r] != "verified")
        out[g] = block
        lines.append(f"  {g:22s} due {len(due):2d}, not verified {len(block)}:"
                     f" {', '.join(block) or '-'}")
    lines += ["  financial close already waits on Z-014 (licence threshold,",
              "  answered by CQ-02 but not yet re-filed as verified); notice",
              "  to proceed waits on the contract draft and the ride-through",
              "  conflict - gates tie the register to the schedule"]
    emit("s_gates", lines)
    return out


# ------------------------------------------------ s3. how often the rules change
def watch() -> dict:
    years = (src.TODAY - SINCE).days / 365.25
    rate = len(CHANGES) / years
    to_conn = (src.CONNECT - src.TODAY).days / 365.25
    to_cod = (COD - src.TODAY).days / 365.25
    p_conn = 1 - math.exp(-rate * to_conn)
    p_cod = 1 - math.exp(-rate * to_cod)
    life = rate * 25
    lines = [f"grid documents changed {len(CHANGES)} times in {years:.1f} years: "
             f"{rate:.2f} a year",
             f"  chance of at least one change before first energisation"
             f" ({to_conn:.1f} yr): {p_conn:.0%}",
             f"  before commercial operation ({to_cod:.1f} yr): {p_cod:.0%}",
             f"  expected changes over a 25-year life: {life:.0f}",
             "  a Poisson rate from four events is rough; the point stands:",
             "  someone checks the official sources on a fixed day each",
             "  month and records 'no change' too"]
    emit("s_watch", lines)
    return dict(rate=rate, p_conn=p_conn, p_cod=p_cod, life=life)


# ------------------------------------------------ s4. register by discipline
def matrix() -> dict:
    status = {r["id"]: r["status"] for r in src.REQS
              if cp.applies(r, src.PROJECT)}
    tab = {}
    for rid, d in DISCIPLINE.items():
        if rid not in status:
            continue
        tab.setdefault(d, {s: 0 for s in ("verified", "project-dependent",
                                          "to-confirm")})
        tab[d][status[rid]] += 1
    lines = ["the register by discipline (verified / project-dependent / to-confirm)"]
    for d, row in sorted(tab.items()):
        lines.append(f"  {d:14s} {row['verified']:3d} {row['project-dependent']:3d}"
                     f" {row['to-confirm']:3d}")
    open_ = [d for d, row in tab.items() if row["to-confirm"]]
    lines += [f"  disciplines with a to-confirm item: {', '.join(sorted(open_))}",
              "  (Z-011 left out: not applicable at 132 kV, reason recorded)",
              "  each discipline lead owns its rows; the compliance manager",
              "  owns the register, not the answers"]
    emit("s_matrix", lines)
    return tab


if __name__ == "__main__":
    forms()
    gates()
    watch()
    matrix()
