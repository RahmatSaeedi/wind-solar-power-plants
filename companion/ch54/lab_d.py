"""Chapter 54, lab D (worked example): trace one fictional grid-connection
requirement - power factor 0.95 at the POC (Z-001, GCZ 6.2 with A1) -
from the official source through interpretation, design, procurement,
settings, test, approval and retained evidence; dispose of the test
deviation (DEV-11, chapter 50) with numbers; and show a trace that cannot
pass its interpretation stage (Z-009, ride-through, CQ-01 open).

Run from the project root:   python -m companion.ch54.lab_d
Writes companion/ch54/expected/d_*.txt and diagrams/data/ch54-export.csv.
Fictional requirement texts; Plant P teaching values (A-549).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch15 import sources as s15
from companion.ch54 import sources as src
from companion.ch54.common import csv, emit
from plantp import compliance as cp
from plantp import finance as fn

PF = 0.95
P_RATED = 100.0          # MW, export limit at the POC
Q_TEST = 30.6            # Mvar at 100 MW, ch 50 test (DEV-11)
PRICE = 70.0             # u/MWh, PPA (ch 21), kept flat here (teaching)
YEARS = 20               # PPA years
RATE = 0.075             # WACC (ch 21)
COMP_COST = 360.0        # k u: 5 Mvar switched capacitor bay at 33 kV (A-549)
COMP_MVAR = 5.0

TRACE_Z001 = {
    "source": "GCZ 2024 cl 6.2 + A1 (consolidated on the filing date)",
    "design": "ch 28 PLP-ELE-CAL-0014: +46 Mvar at 25 C, +29 at 45 C",
    "procurement": "ch 44 PLP-ELE-SPC-0011: unit P-Q curve, clause 4.3",
    "construction": "ch 48/50 as-left PPC settings, Q mode and limits",
    "test": "ch 50 Q test: 30.6 Mvar at 100 MW against 32.9 (DEV-11)",
    "approval": None,
    "retained": None,
}
TRACE_Z009 = {
    "source": "GCZ 2024 cl 8.4 (150 ms) - and TCR 2022 sec 5 (trip at 100 ms)",
    "design": None,
    "procurement": "ch 44 converter type test covers 150 ms",
    "construction": None,
    "test": None,
    "approval": None,
    "retained": None,
}


def q_needed(p_mw: float, pf: float = PF) -> float:
    return p_mw * math.tan(math.acos(pf))


# ------------------------------------------------ 1. source and reading
def source() -> dict:
    text = cp.consolidated(src.GCZ_CLAUSES, src.FILED)["6.2"]
    rows = [(p, q_needed(p)) for p in (10, 20, 40, 60, 80, 100)]
    lines = [f"Z-001 source: GCZ clause 6.2 as amended ({text[0]}):",
             f"  {text[1]}",
             "reading INT-01 (written, TSOZ): Q = P tan(acos 0.95), both signs",
             "  P (MW)   Q needed (Mvar)"]
    lines += [f"  {p:6.0f}   {q:8.2f}" for p, q in rows]
    lines += ["  the amendment A1 extends the band down to 10 % of rated P:",
              "  a design checked only from 20 % (the 2024 base) misses it;",
              "  and ch 28's placeholder of +/-33 Mvar at every P is not",
              f"  this text: at 50 MW Z-001 asks {q_needed(50):.1f} Mvar"]
    emit("d_source", lines)
    return dict(q100=q_needed(P_RATED))


# ------------------------------------------------ 2. the trace
def trace() -> dict:
    gaps1 = cp.trace_gaps(TRACE_Z001)
    gaps2 = cp.trace_gaps(TRACE_Z009)
    lines = ["trace of Z-001, stage by stage"]
    for st in cp.STAGES:
        lines.append(f"  {st:12s} {TRACE_Z001[st] or 'OPEN'}")
    lines += [f"  open stages: {', '.join(gaps1)} - the test failed, so no",
              "  approval and nothing to retain as closure yet; the design",
              "  record had already shown the hot-day shortfall (29 Mvar)",
              "  and left it as 'an operator decision' nobody took",
              "",
              "trace of Z-009 (ride-through)"]
    for st in cp.STAGES:
        lines.append(f"  {st:12s} {TRACE_Z009[st] or 'OPEN'}")
    lines += [f"  open stages: {len(gaps2)} of {len(cp.STAGES)} - two sources disagree",
              "  (CQ-01), so design cannot start where the conflict bites:",
              "  the protection settings wait; the converter's 150 ms type",
              "  test is evidence for one reading only"]
    emit("d_trace", lines)
    return dict(gaps1=gaps1, gaps2=gaps2)


# ------------------------------------------------ 3. disposition of DEV-11
def disposition() -> dict:
    q100 = q_needed(P_RATED)
    p_ok = Q_TEST / math.tan(math.acos(PF))
    deliv = np.minimum(s15.plant_year()["delivered"], P_RATED)
    above = np.clip(deliv - p_ok, 0.0, None)
    hours = int((deliv > p_ok).sum())
    mwh = float(above.sum())
    lost_k = mwh * PRICE / 1000
    pv_lost = fn.pv(np.full(YEARS, lost_k), RATE)
    order = np.sort(deliv)[::-1]
    step = 20
    csv("ch54-export.csv", "h,mw", [(i, round(float(order[i]), 2))
                                    for i in range(0, 1201, step)])
    lines = [f"DEV-11: Q at 100 MW {Q_TEST} Mvar against {q100:.1f} needed"
             f" (short {q100 - Q_TEST:.1f} Mvar)",
             f"  (a) cap export at {p_ok:.1f} MW, where {Q_TEST} Mvar meets pf 0.95:",
             f"      model 15.1 year: {hours} hours above, {mwh:,.0f} MWh lost,",
             f"      {lost_k:.0f} k u a year, {pv_lost:,.0f} k u over {YEARS} years at"
             f" {RATE:.1%}",
             f"  (b) add a {COMP_MVAR:.0f} Mvar switched capacitor bay: {COMP_COST:.0f} k u"
             " (teaching),",
             f"      margin {COMP_MVAR - (q100 - Q_TEST):.1f} Mvar for a hot day",
             "  (c) ask TSOZ for a derogation: no cost if granted, but the",
             "      register shows 'to-confirm' until it is written",
             f"  cheapest certain option: {'(b)' if COMP_COST < pv_lost else '(a)'};"
             " the cap stays the",
             "  fallback while (b) is bought - and the decision is TSOZ's"]
    emit("d_dispose", lines)
    return dict(p_ok=p_ok, hours=hours, mwh=mwh, lost_k=lost_k, pv_lost=pv_lost,
                q100=q100)


# ------------------------------------------------ 4. evidence that closes it
def evidence() -> list:
    items = [("source", "consolidated GCZ text with A1, gazette reference, date read",
              True),
             ("reading", "INT-01 letter from TSOZ", True),
             ("design", "capability calculation incl. hot day and 10 % band", True),
             ("procurement", "unit P-Q curve in the converter order", True),
             ("settings", "as-left PPC file with checksum", True),
             ("disposition", "DEV-11 decision by TSOZ (derogation or remedy)", False),
             ("retest", "Q test at 100 MW after the remedy, witnessed", False),
             ("approval", "TSOZ acceptance of REQ-G01 / Z-001", False),
             ("register", "R4 of the register with Z-001 closed", False)]
    done = sum(ok for *_, ok in items)
    lines = ["evidence file that closes Z-001"]
    lines += [f"  [{'x' if ok else ' '}] {k:12s} {t}" for k, t, ok in items]
    lines += [f"  {done} of {len(items)} in hand: everything before the test is",
              "  done; closure waits on the network operator's decision"]
    emit("d_evidence", lines)
    return items


if __name__ == "__main__":
    source()
    trace()
    disposition()
    evidence()
