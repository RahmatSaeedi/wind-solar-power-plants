"""Chapter 38 - small worked examples (E-lines) and the numerical answers
of the exercises (P-lines), each computed here.

Run from the project root:   python -m companion.ch38.worked
Writes companion/ch38/expected/worked.txt and solutions.txt.
"""
from __future__ import annotations

import math

from companion.ch38.common import emit
from plantp import docctl as dc


def worked() -> None:
    e = dc.earned_value(200, 150, 180, 1000)
    lines = [f"E01 'PLP-ELE-DWG-0005' follows the scheme: {dc.id_ok('PLP-ELE-DWG-0005')}",
             f"E02 revision 'B' with status IFC is valid: {dc.rev_ok('B', 'IFC')}",
             f"E03 IFR -> IFC allowed: {dc.transition_ok('IFR', 'IFC')}",
             f"E04 SPI and CPI with PV 200, EV 150, AC 180: {e['spi']:.2f}, {e['cpi']:.2f}",
             f"E05 EAC with BAC 1,000 h and CPI {e['cpi']:.3f}: {e['eac']:,.0f} h",
             f"E06 sample 10 of 50 with 2 errors finds one: {dc.detect_chance(50, 2, 10):.3f}"]
    emit("worked", lines)


def solutions() -> None:
    i_lv = 5.0e3 / (math.sqrt(3) * 0.6)
    out = [f"P01 SPI, EV 3,012 h, PV 4,451 h: {3012 / 4451:.2f}",
           f"P02 CPI, EV 3,012 h, AC 3,553 h: {3012 / 3553:.2f}",
           f"P03 EAC, BAC 7,342 h: {7342 / (3012 / 3553):,.0f} h",
           f"P04 earned hours of a 60 h drawing at IFA (60 %): {60 * 0.6:.0f} h",
           f"P05 detection chance, 40 of 200, 6 errors: {dc.detect_chance(200, 6, 40):.2f}",
           f"P06 detection chance, 80 of 200, 6 errors: {dc.detect_chance(200, 6, 80):.2f}",
           f"P07 expected errors found, 40 of 200 with 6: {6 * 40 / 200:.1f}",
           f"P08 LV current at 5.0 MVA, 0.6 kV: {i_lv:,.0f} A",
           f"P09 parallel cables at 620 A: {math.ceil(i_lv / 620)}",
           f"P10 heat at 98.5 %, 5.0 MVA: {5000 * 0.015:.0f} kW",
           f"P11 short-circuit at 33 kV, 500 MVA + 0.12 ohm: "
           f"{33 / (math.sqrt(3) * (33 ** 2 / 500 + 0.12)):.1f} kA",
           f"P12 rework hours of C-017: {4 + 6 + 6 + 16 + 8 + 24 + 6 + 4 + 6 + 4 + 8 + 4 + 6} h",
           f"P13 rework cost at 95 u/h: {102 * 95 / 1000:.1f} k u",
           f"P14 handover score, weights 3,3,2,3,1,2,1: "
           f"{dc.handover_score({'a': (3, .92), 'b': (3, .85), 'c': (2, .70), 'd': (3, 1.0), 'e': (1, .60), 'f': (2, .95), 'g': (1, .80)}) * 100:.1f} %",
           f"P15 metadata completeness, 9 of 120 owners missing: {(120 - 9) / 120 * 100:.1f} %",
           f"P16 RVTM design coverage, 10 of 12: {10 / 12 * 100:.0f} %",
           f"P17 TQ share older than 14 days, 18 of 42: {18 / 42 * 100:.0f} %",
           f"P18 mean approval time, 55/25/17 % at 14/28/42 d: "
           f"{(0.55 * 14 + 0.25 * 28 + 0.17 * 42) / 0.97:.0f} d",
           f"P19 pairwise interfaces among 8 subsystems: {8 * 7 // 2}",
           f"P20 hazard actions closed, 18 of 20: {18 / 20 * 100:.0f} %"]
    emit("solutions", out)


if __name__ == "__main__":
    worked()
    solutions()
