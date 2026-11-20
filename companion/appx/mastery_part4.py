"""Appendix X - answers of the Part IV diagnostic mastery test (chapters
17-22): turn requirements into an architecture, size and run storage
with evidence, show whether the plant is economic and financeable, and
choose between options with traceable evidence.

Run from the project root:   python -m companion.appx.mastery_part4
Writes companion/appx/expected/mastery_part4.txt.
Data pack 1.1.0 (synthetic), S1; decisions D-021 to D-026. Test values
marked (test) are used only here.
"""
from __future__ import annotations

import math

import numpy as np

from companion.appx.common import emit
from companion.ch18 import sources as s18
from companion.ch21 import model
from companion.ch22.examples_h import rollback
from plantp import appraisal as ap
from plantp import finance as fn

OUT: list[str] = []


def p(pid: str, text: str) -> None:
    OUT.append(f"{pid}: {text}")


def architecture() -> None:
    p("M46", "installed AC 60 + 50 = 110 MW against a 100 MW export limit:"
             " curtailed 0.23 GWh a year; a 90 MW limit would curtail 1.76 GWh")
    e = s18.EFF
    p("M47", "AC-coupled PV -> battery -> grid 85.0 %, DC-coupled 86.7 %"
             f" (one-way set of {len(e)} efficiencies, A-286)")
    p("M48", "requirement REQ-007-like test (test): 'export <= 100 MW at the"
             " POC meter, 1-min mean' is measurable; 'export limited' is not")
    p("M49", f"water: 2,500 m3 tank with a held reserve; demand above a"
             f" 40 m3/day well for 30 days (test): {30 * 120 - 30 * 40:,} m3 from the tank"
             " at 120 m3/day")


def storage() -> None:
    cells = 52 * 8 * 12 * 8
    mwh = cells * 314 * 3.2 / 1e6
    p("M50", f"build-up 52 x 8 x 12 x 8 = {cells:,} cells x 314 Ah x 3.2 V ="
             f" {mwh:.2f} MWh; window 10-90 % usable {0.8 * mwh:.1f} MWh")
    eta = math.sqrt(0.86)
    p("M51", f"service floor: 4 MWh + 5 MW x 1 h / {eta:.3f} ="
             f" {4 + 5 / eta:.2f} MWh held from 18 to 22 h")
    p("M52", "priority order safety > operator > service > schedule > recapture:"
             " an operator cap and a service call -> obey the cap, keep the"
             " service within it, log the conflict (D-024)")
    p("M53", "battery at teaching prices repays about 40 % of its capital"
             " (D-025): technically defined (D-023), financially conditional")


def economics() -> None:
    crf = 0.05 / (1 - 1.05 ** -25)
    p("M54", f"envelope LCOE: (156,450 x CRF {crf:.4f} + 4,270) / 288,854 MWh ="
             f" {(156450 * crf + 4270) / 288.854:.1f} u/MWh")
    cf = np.full(15, 13_000.0)                     # (test) flat P90 CFADS
    d, *_ = fn.sculpted_debt(cf, 1.20, 0.06)
    p("M55", f"sculpted debt on a flat 13,000 a year, DSCR 1.20, 6 %, 15 years:"
             f" {d:,.0f} k u")
    base = model.run()
    p("M56", f"model base: debt {base['debt']:,.0f} ({base['gearing'] * 100:.0f} %),"
             f" equity IRR {base['equity_irr'] * 100:.2f} %, min DSCR"
             f" {base['min_dscr']:.2f}, min LLCR {base['min_llcr']:.2f}")
    p("M57", "break-even energy 85.9 % of P50 (DSCR 1.00, debt fixed) against"
             " the one-year P99 of 88.1 %: lenders are paid in a P99 year")


def feasibility() -> None:
    s = np.array([[1.0, 0.0, 0.0], [0.49, 0.71, 1.0], [0.0, 1.0, 0.55]])
    w = [0.5, 0.3, 0.2]                            # (test)
    t = ap.weighted(s, w)
    p("M58", "scores (energy, cost, time) with weights 0.5/0.3/0.2 (test):"
             f" {', '.join(f'{x:.2f}' for x in t)}; dominated:"
             f" {ap.dominated(s) or 'none'}")
    v = rollback([(2_200, 0.75), (2_500, 0.80)], 7_740)
    v2 = rollback([(2_200, 0.75), (2_500, 0.80)], 5_000)
    p("M59", f"development tree: value 7,740 -> EV {v:,.0f}; value 5,000 ->"
             f" EV {v2:,.0f} (stop)")
    p("M60", "D-026: P-Central (295 GWh) over P-North (330 GWh): equity IRR"
             " 10.21 vs 9.85 %, NPV today 4,740 vs 4,646 k u, two flags,"
             " 22 months later close")


if __name__ == "__main__":
    architecture()
    storage()
    economics()
    feasibility()
    emit("mastery_part4", OUT)
