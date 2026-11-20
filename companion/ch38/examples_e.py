"""Chapter 38, lesson E (project controls and technical governance): earned
value of the engineering deliverables, technical queries by age, the cost
and schedule of a change, the decision log, and the chance that an
independent check finds a design error.

Run from the project root:   python -m companion.ch38.examples_e
Writes companion/ch38/expected/e_*.txt and diagrams/data/ch38-*.csv.
Synthetic registers (A-417, A-420, A-422).
"""
from __future__ import annotations

import numpy as np

from companion.ch38 import sources as src
from companion.ch38.common import csv, emit
from plantp import docctl as dc


def earned() -> None:
    docs = src.DOCS
    week = src.STATUS_DATE_WEEK
    bac = sum(d["hours"] for d in docs)
    pv = sum(d["hours"] for d in docs if d["planned_week"] <= week)
    ev = sum(d["hours"] * src.CREDIT[d["status"]] for d in docs)
    ac = sum(d["spent"] for d in docs)
    e = dc.earned_value(pv, ev, ac, bac)
    lines = [f"earned value of the engineering at week {week} (hours, synthetic)",
             f"  budget at completion {bac:,.0f} h; planned value {pv:,.0f} h",
             f"  earned value {ev:,.0f} h (credit by status: IFR 30 %, IFA 60 %,"
             " IFC 90 %)",
             f"  actual hours {ac:,.0f} h",
             f"  SPI {e['spi']:.2f}, CPI {e['cpi']:.2f}; estimate at completion"
             f" {e['eac']:,.0f} h",
             "  the design is behind its plan and costs more than planned",
             "  for what it has earned; credit only by status keeps the",
             "  progress honest - a drawing 'nearly finished' earns",
             "  nothing more until it is issued"]
    emit("e_ev", lines)
    rows = []
    for w in range(0, 61, 4):
        rows.append((w, sum(d["hours"] for d in docs if d["planned_week"] <= w)))
    csv("ch38-scurve.csv", "w,pv", rows)


def tq_ageing() -> None:
    b = dc.ageing(src.TQS)
    lines = [f"{len(src.TQS)} technical queries open at the status date, by days open",
             "  days       count"]
    for k, v in b.items():
        lines.append(f"  {k:9s} {v:6d}")
    over = sum(1 for d in src.TQS if d > 14)
    lines += [f"  older than the 14-day reply time: {over}; mean {np.mean(src.TQS):.1f} days",
              "  a query that waits holds a drawing that waits for it;",
              "  the log names who must answer, and the old ones go to",
              "  the weekly interface meeting by name"]
    emit("e_tq", lines)


def change_cost() -> None:
    hit = dc.impacted(src.DEPENDS, "unit transformer rating")
    hours = sum(src.REWORK_H[h] for h in hit)
    rate = 95.0                                          # u per engineering hour
    price_step = 10 * 4.0                                # 10 PV units x 4 k u (teaching)
    days = 10
    lines = ["impact of change C-017 (teaching rates)",
             f"  engineering rework {hours} h x {rate:.0f} u = {hours * rate / 1000:.1f} k u",
             f"  transformer price step, 10 PV units x 4 k u = {price_step:.0f} k u",
             f"  schedule: {days} working days on the transformer order, off the",
             "    critical path if placed before week 44",
             f"  decision: approved - {hours * rate / 1000 + price_step:.0f} k u against a 1 %"
             " shortfall",
             "    in reactive capability at full power (ch 25)",
             "  the change log records the reason, the cost, the schedule",
             "  effect and who approved it - the decision log links to it"]
    emit("e_change", lines)


def check_sampling() -> None:
    n, k = 200, 6                                        # drawings, errors in them
    lines = [f"independent check of a sample of {n} drawings holding {k} errors",
             "  drawings checked   chance to find at least one   expected found"]
    rows = []
    for s in (10, 20, 40, 80, 200):
        p = dc.detect_chance(n, k, s)
        rows.append((s, round(p, 4)))
        lines.append(f"  {s:16d}   {p * 100:28.0f} %   {k * s / n:14.1f}")
    csv("ch38-checks.csv", "s,p", rows)
    lines += ["  a sample finds out whether errors are there, not all of",
              "  them; drawings whose error is costly (protection, lifting,",
              "  foundations) are checked one by one, the rest sampled,",
              "  and a sample with errors widens to the whole set"]
    emit("e_checks", lines)


def decision_log() -> None:
    rows = [("D-022", "architecture A1", "ch 18", "PLP-ELE-REP-0005"),
            ("D-029", "transformers, bid B", "ch 25", "PLP-ELE-REP-0008"),
            ("D-030", "protection basis", "ch 26", "PLP-ELE-CAL-0011"),
            ("C-017", "unit transformer 5.6 MVA", "this chapter", "change request")]
    lines = ["the decision log: each decision with its source and record",
             "  id      decision                    from           record"]
    for a, b, c, d in rows:
        lines.append(f"  {a:7s} {b:26s}  {c:13s}  {d}")
    lines += ["  a later reader can follow any number in a drawing back to",
              "  the decision that set it and the evidence behind it"]
    emit("e_decisions", lines)


if __name__ == "__main__":
    earned()
    tq_ageing()
    change_cost()
    check_sampling()
    decision_log()
