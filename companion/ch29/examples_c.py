"""Chapter 29, lesson C: construction quality and environment - field
compaction lots, concrete strength results of the foundation pours, a
sediment pond for the graded PV block, and the non-conformance log.

Run from the project root:   python -m companion.ch29.examples_c
Writes companion/ch29/expected/c_*.txt and diagrams/data/ch29-*.csv.
Synthetic results; acceptance rules are teaching (the project's
specification states its own).
"""
from __future__ import annotations

import numpy as np

from companion.ch29.common import csv, emit
from plantp import civil as cv


def compaction() -> None:
    lots = {"road km 0-1": np.array([96.9, 95.5, 96.5, 98.1, 97.4, 97.6]),
            "road km 1-2": np.array([99.0, 94.0, 97.5, 92.5, 98.5, 96.0]),
            "crane pad T07": np.array([94.2, 95.3, 94.0, 94.4, 93.8, 93.2])}
    lines = ["field compaction: relative compaction % of the laboratory maximum",
             "  (teaching rule: lot mean - 0.5 s >= 95 % and no test below 92 %)",
             "  lot             tests                                   mean-0.5s   result"]
    for name, v in lots.items():
        ok, m = cv.lot_accept(v, 95.0, k=0.5)
        ok = ok and v.min() >= 92.0
        vals = " ".join(f"{x:4.1f}" for x in v)
        lines.append(f"  {name:14s}  {vals}   {m:9.2f}   {'accept' if ok else 'REJECT'}")
    lines += ["  the second lot's mean (96.3) is above 95, but its spread",
              "  pulls mean - 0.5 s below: it fails on its uniformity;",
              "  the T07 pad fails - rework (moisture, more passes) and",
              "  retest before the crane stands on it; the rule is fixed",
              "  in the specification before the first test, not tuned"]
    emit("c_compaction", lines)


def concrete() -> None:
    rng = np.random.default_rng(293)
    pours = {f"F{k:02d}": rng.normal(43.0, 3.0, 3) for k in range(1, 13)}
    pours["F07"] = np.array([33.5, 35.0, 31.8])          # a weak pour
    allv = np.concatenate(list(pours.values()))
    fck = cv.characteristic(allv)
    csv("ch29-concrete.csv", "k,mean,lo,hi",
        [(k, f"{v.mean():.1f}", f"{v.min():.1f}", f"{v.max():.1f}") for k, v in enumerate(pours.values(), 1)])
    lines = ["28-day strength of the foundation pours (3 specimens each, MPa, synthetic)",
             f"  all 36 results: mean {allv.mean():.1f}, s {allv.std(ddof=1):.1f},"
             f" characteristic (mean - 1.645 s) {fck:.1f}",
             "  specified class (teaching): 35 MPa characteristic",
             "  pour   mean    lowest   flag"]
    for k, v in pours.items():
        flag = "NCR: below 35 MPa" if v.mean() < 35.0 else ""
        lines.append(f"  {k}    {v.mean():5.1f}   {v.min():6.1f}   {flag}")
    lines += ["  the set as a whole looks acceptable, but pour F07 is weak",
              "  on its own: a non-conformance report, cores from the",
              "  structure, and the structural engineer's assessment",
              "  before the tower goes on (ch 30) - a good average never",
              "  excuses one weak foundation"]
    emit("c_concrete", lines)


def sediment() -> None:
    area_ha, months = 30.0, 3
    loss_t = 16.6 * area_ha * months / 12              # bare graded PV ground (lesson B)
    vol_sed = loss_t / 1.5                             # m3 at 1.5 t/m3
    runoff = 0.5 * 25.0 / 1000 * area_ha * 1e4         # 25 mm storm, C 0.5
    lines = ["a sediment pond for the PV block while it is graded and bare",
             f"  soil loss over {months} bare months on {area_ha:.0f} ha: {loss_t:.0f} t ="
             f" {vol_sed:.0f} m3 of sediment",
             f"  runoff of a 25 mm storm (C 0.5) to hold for settling: {runoff:.0f} m3",
             f"  pond: about {vol_sed + runoff:,.0f} m3 (storage + settling), emptied",
             "  after storms and removed when the cover is back; its outlet",
             "  goes to the wadi only through a stable, rock-lined spillway"]
    emit("c_sediment", lines)


def ncr_log() -> None:
    rng = np.random.default_rng(294)
    cats = ["compaction", "concrete", "setting out", "drainage", "documentation"]
    n = 40
    cat = rng.choice(cats, n, p=[0.25, 0.15, 0.15, 0.15, 0.30])
    days_open = rng.exponential(14, n).round()
    closed = rng.random(n) < 0.8
    lines = ["non-conformance log of the civil works (synthetic, 40 reports)",
             "  category        reports   open   median days to close"]
    for c in cats:
        m = cat == c
        cl = days_open[m & closed]
        lines.append(f"  {c:14s}  {int(m.sum()):7d}   {int((m & ~closed).sum()):4d}"
                     f"   {np.median(cl) if len(cl) else float('nan'):20.0f}")
    lines += [f"  {int((~closed).sum())} open at handover would block it: each NCR closes with",
              "  the evidence (retest, core, engineer's acceptance), not",
              "  with a signature; documentation is the largest category -",
              "  records are part of the work, not paperwork after it"]
    emit("c_ncr", lines)


if __name__ == "__main__":
    compaction()
    concrete()
    sediment()
    ncr_log()
