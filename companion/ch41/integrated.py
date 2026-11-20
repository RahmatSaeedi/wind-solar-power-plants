"""Chapter 41 - three integrated Plant P examples: one module from cell to
string by hand, the lot from the flash file to the plant's acceptance,
and the module manufacturing and acceptance basis D-045.

Run from the project root:   python -m companion.ch41.integrated
Writes companion/ch41/expected/int_*.txt.
"""
from __future__ import annotations

import math

from companion.ch41 import examples_c, examples_e, lab_d
from companion.ch41 import sources as src
from companion.ch41.common import emit
from companion.ch41.examples_a import CELL
from plantp import pvfab as fab


def by_hand() -> None:
    voc = fab.voc(CELL["jsc"], 9.1e-14)
    ff = fab.fill_factor(voc, CELL["rs"], CELL["jsc"])
    p_cell = voc * CELL["jsc"] * ff * CELL["area_cm2"]
    lines = ["one module from cell to string, by hand",
             f"  cell Voc = 0.02569 ln(0.0418 / 9.1e-14) = {voc:.3f} V",
             f"  cell FF (Green, Rs 0.64 ohm cm2) = {ff:.3f}",
             f"  cell power = {voc:.3f} x 0.0418 x {ff:.3f} x 330 = "
             f"{p_cell:.2f} W",
             f"  module = 72 x {p_cell:.2f} x CTM 0.992 = "
             f"{72 * p_cell * 0.992:.0f} W (label class 550)",
             f"  string Voc at -15 C = 26 x 49.90 x 1.108 = "
             f"{26 * 49.90 * 1.108:.0f} V < 1,500 V",
             "  a hand check of this chain catches a cell area in m2, a",
             "  CTM above 1 without a reason, or a string sized at 25 C"]
    emit("int_hand", lines)


def lot() -> None:
    v = lab_d.validate()
    d = lab_d.drift_quiet()
    c = lab_d.classes()
    o = lab_d.outliers()
    t = examples_c.transport()
    el = examples_e.el_sample()
    lines = ["the lot from the flash file to the plant's acceptance",
             f"  file: {v['problems']} data problems returned to the maker",
             f"  tester drift +{d['shift']:.1f} W from seq {d['first']}: "
             f"{c['moved']} labels reissued",
             f"  outliers: {o['flags']} flagged, each with a first guess at "
             "its cause",
             f"  transport: EL of a pallet a container, caught "
             f"{t['catch']:.0%} of rough ones",
             f"  site EL: {el[0.01]} modules to see a 1 % cracked share",
             "  the lot is accepted on evidence the plant checked itself,",
             "  not on the maker's 'all passed'"]
    emit("int_lot", lines)


def basis() -> None:
    lines = ["D-045 module manufacturing and acceptance basis (PVM-550)",
             "  1 purchase by BOM revision: a certificate (IEC 61215,",
             "    IEC 61730) counts only for the BOM it tested; any change",
             "    follows the retesting guideline (IEC TS 62915)",
             "  2 the maker's quality system (IEC 62941) and its control",
             "    plan seen before award; golden-module checks every 100",
             "  3 flash files parsed on receipt: data, drift, outliers;",
             "    labels reissued when a drift is found",
             "  4 EL of one pallet a container; whole container if two or",
             "    more cracked; site EL sample of 299 a block after",
             "    installation (1 % at 95 %)",
             "  5 laboratory flash 12 per 10 MWp under the contract's",
             "    decision rule (ch 10)",
             "  6 strings along one table row; returns beside outgoing",
             "    cables; clamps in the maker's zones, checked by crew",
             "  7 connectors of one maker and type; frame bonding tested",
             "    on every table",
             "  8 spares of the same class and connector; string-current",
             "    CUSUM against each string's own history",
             "  9 light-induced loss data priced in the bid evaluation;",
             "    EL before and after lamination in the maker's plan",
             " 10 power claims by relative measurement: control modules",
             "    kept in the dark, same laboratory, same reference",
             "  open: the chosen maker's qualification evidence for the",
             "    exact BOM and its PID result (U-122)"]
    emit("int_basis", lines)


if __name__ == "__main__":
    by_hand()
    lot()
    basis()
