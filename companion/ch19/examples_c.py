"""Chapter 19, section C - manufacturing, quality, safety and life:
cell grading against the weakest cell of a series string, acceptance
sampling of incoming cells, why lot-segregated assembly matters, the
cell-to-container interface tree and a hypothetical self-discharging
cell traced from receiving inspection to containment (the chapter's
second worked example), the teaching propagation chain, and the end of
life in tonnes.

Run from the project root:   python -m companion.ch19.examples_c
Writes companion/ch19/expected/c_*.txt and diagrams/data/ch19-*.csv.
Teaching values A-290 and A-294. No cell-making recipes: process steps
appear only with their purpose and their checks.
"""
from __future__ import annotations

from math import comb

import numpy as np

from companion.ch19 import sources as src
from companion.ch19.common import csv, emit
from plantp import storage as st

C, B = src.LFP, src.BUILD
N_RACK = B["s_module"] * B["m_rack"]


def grading() -> None:
    """A series string is limited by its weakest cell (no balancing of
    capacity); grading narrows the spread."""
    rng = np.random.default_rng(190)
    lines = ["rack capacity limited by its weakest of 416 cells (A-294):",
             "  cells          spread (sd)  mean of the weakest  loss"]
    for name, sd in (("ungraded", 2.0), ("graded", 0.6)):
        weakest = rng.normal(C.q_ah, sd, size=(2000, N_RACK)).min(axis=1)
        lines.append(f"  {name:13s}  {sd:6.1f} Ah     {weakest.mean():9.1f} Ah"
                     f"        {100 * (1 - weakest.mean() / C.q_ah):4.1f} %")
    lines += ["  grading (sorting cells into narrow capacity and resistance",
              "  bins before assembly) gives back most of the loss; balancing",
              "  equalises charge, not capacity"]
    emit("c_grading", lines)


def oc(n: int, c: int, p: float) -> float:
    return float(sum(comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(c + 1)))


def sampling() -> None:
    lines = ["incoming inspection of a lot of 2,000 cells by attributes:",
             "  share defective   accept, n 50 c 0   n 125 c 1   n 200 c 2"]
    for p in (0.0005, 0.002, 0.005, 0.01, 0.02):
        lines.append(f"  {100 * p:12.2f} %   {oc(50, 0, p):14.3f}   {oc(125, 1, p):9.3f}"
                     f"   {oc(200, 2, p):9.3f}")
    lines += ["  one bad cell in 2,000 (0.05 %) passes almost every plan:",
              "  sampling finds bad lots, not single bad cells; single cells",
              "  are caught by the maker's tests and by the BMS"]
    emit("c_sampling", lines)


def lots() -> None:
    """One suspect lot of 2,000 cells among 39,936: how many racks?"""
    n_tot, n_lot, racks = B["containers"] * B["r_container"] * N_RACK, 2000, 96
    p_none = 1.0
    for k in range(N_RACK):
        p_none *= (n_tot - n_lot - k) / (n_tot - k)
    mixed = racks * (1 - p_none)
    seg = -(-n_lot // N_RACK) + 1
    lines = ["one suspect lot of 2,000 cells: racks to inspect",
             f"  cells mixed at random in assembly: {mixed:.0f} of {racks} racks",
             f"  lots kept together (lot-segregated assembly): about {seg} racks",
             "  traceability (cell serial to module, rack and container) is",
             "  what turns a recall of the whole battery into a few racks"]
    emit("c_lots", lines)


# [start: tree]
TREE = [
    ("cell", "module", "busbar weld, voltage and temperature leads, "
     "compression frame, thermal pad"),
    ("module", "rack", "power connector, BMS daisy chain, module fuse, "
     "mounting and earthing"),
    ("rack", "container", "rack switch and fuse, DC bus, rack BMS link, "
     "airflow, gas and smoke detection"),
    ("container", "PCS and plant", "DC cables, protocol (IF-007), auxiliary "
     "power, earthing, remote isolation, fire panel"),
]
# [end: tree]


def trace_defect() -> None:
    """A cell with an internal leak of 60 mA (a normal cell 11 mA)."""
    normal, leak = 11.0, 60.0
    lines = ["cell-to-container interfaces (worked example 2, part 1):"]
    for a, b, what in TREE:
        lines.append(f"  {a} -> {b}:")
        lines.append(f"    {what}")
    lines += ["hypothetical defect: an internal leak of 60 mA (normal 11 mA)",
              "  1 receiving inspection (OCV now and after 7 days, 30 % SOC):"]
    d_n = st.ocv_drift_mv(normal, C.q_ah, 7, 0.30)
    d_d = st.ocv_drift_mv(leak, C.q_ah, 7, 0.30)
    lines += [f"    drop normal {d_n:.2f} mV, defective {d_d:.2f} mV; a limit of 1.5 mV",
              "    catches it, but only if this cell is in the sample (125 of",
              "    2,000: 6 %)"]
    extra = (leak - normal) / 1000 * 24 / C.q_ah                      # SOC a day
    bal = 0.100 * 2.0 / C.q_ah                                        # 100 mA, 2 h a day
    net = extra - bal
    days = None
    for d in range(1, 400):
        dv = 1000 * float(st.ocv(0.90) - st.ocv(0.90 - net * d))
        if dv > 30.0:
            days = d
            break
    lines += ["  2 in operation, a series string carries one current; the",
              f"    leak drains the cell {100 * extra:.2f} % SOC a day more; balancing",
              f"    (100 mA, 2 h a day) returns {100 * bal:.2f} %; net {100 * net:.2f} % a day",
              f"    its voltage at the top of charge falls 30 mV below the others",
              f"    after {days} days: the BMS deviation alarm (teaching limit)",
              "    and the balancing log (the same cell every day) both show it",
              "  3 containment: the rack controller limits current, then opens",
              "    the rack switch; 11 of 12 racks keep running; the module (the",
              "    replaceable unit) is changed under the maker's procedure; the",
              "    cell goes to failure analysis and its lot is traced (c_lots)"]
    emit("c_defect", lines)
    rows = []
    for d in range(0, 61):
        rows.append((d, f"{1000 * float(st.ocv(0.90) - st.ocv(0.90 - net * d)):.2f}"))
    csv("ch19-defect.csv", "day,dv", rows)


def chain() -> None:
    lines = ["teaching propagation chain (not a design method; A-294):",
             "  design                       p cell  p module  cells  modules"]
    for name, pc, pm in (("no barriers", 0.9, 0.6), ("cell barriers", 0.3, 0.3),
                         ("cell and module barriers", 0.3, 0.05)):
        r = st.chain_expected(B["s_module"], pc, B["m_rack"], pm)
        lines.append(f"  {name:27s} {pc:6.2f}  {pm:8.2f}  {r['cells_in_module']:5.1f}"
                     f"  {r['modules']:7.2f}")
    lines += ["  the chain shows why a barrier between cells matters more than",
              "  one between modules: a module passes the event on only if the",
              "  cells carried it to its edge; real probabilities come only",
              "  from large-scale tests of the product (UL 9540A, chapter 32)"]
    emit("c_chain", lines)


def end_of_life() -> None:
    kg_cell = 5.5                                   # teaching mass, A-294
    t_cells = B["containers"] * B["r_container"] * N_RACK * kg_cell / 1000
    lines = ["end of life of the S1 battery (teaching masses, A-294):",
             f"  cells {t_cells:,.0f} t; with modules, racks and containers about"
             f" {1.8 * t_cells:,.0f} t",
             f"  trucks of 20 t for the cells: {t_cells / 20:.0f}",
             "  routes: second use (if health and records allow), then",
             "  recycling by a licensed recycler; spent cells travel as",
             "  dangerous goods with their own test and packing rules",
             "  the end-of-life plan and its cost belong in the design basis",
             "  and the decommissioning fund (chapter 53)"]
    emit("c_eol", lines)


if __name__ == "__main__":
    grading()
    sampling()
    lots()
    trace_defect()
    chain()
    end_of_life()
