"""Appendix X - answers of the Part IX diagnostic mastery test (chapters
51-53): operating the plant on its records, maintaining it with a RAM case
inside a stated boundary, and taking its lifecycle decisions with their
assumptions - with the numbers computed from the chapters' companion code.

Run from the project root:   python -m companion.appx.mastery_part9
Writes companion/appx/expected/mastery_part9.txt.
Data pack 1.1.0 (synthetic), decisions D-055 to D-057.
Values marked (test) are used only here.
"""
from __future__ import annotations

import math

import numpy as np

from companion.appx.common import emit
from plantp import lifecycle, operations, ram

OUT: list[str] = []


def p(pid: str, text: str) -> None:
    OUT.append(f"{pid}: {text}")


def operation() -> None:
    h = operations.autonomy_h(44.0, 4.6, 0.2)
    p("M125", f"station battery 44 kWh, load 4.6 kW, 20 % kept: {h:.1f} h on battery;"
              " the diesel start is the hidden failure behind it")
    window = np.ones(120, bool)
    held = window.copy()
    held[:7] = False
    a = operations.service_availability(held, window)
    p("M126", f"reserve held in 113 of 120 window hours: {a:.1%} against 95 % -"
              " short, and each lost hour declared at once, never left to look held")
    need = 4 * 8760 / 1804
    p("M127", f"four posts around the clock, 1,804 h a person a year: {need:.1f} people,"
              " not 16 - leave and training are counted before the roster")
    n, k, z = 24, 17, 1.96
    ph = k / n
    c = (ph + z * z / (2 * n)) / (1 + z * z / n)
    hw = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    p("M128", f"17 of 24 tasks done with the current procedure: {ph:.0%}, 95 % interval"
              f" {c - hw:.0%} to {c + hw:.0%} (Wilson) - a small sample says 'not always'")


def maintenance() -> None:
    ai = ram.a_inherent(17_520.0, 24.0)
    p("M129", f"MTBF 17,520 h, MTTR 24 h: inherent availability {ai:.5f}; operational"
              " availability adds the waits for parts and people")
    v = ram.k_of_n(2, 3, 0.95)
    p("M130", f"two of three units needed, each 0.95: {v:.5f} (independent units)")
    q = ram.pair_with_ccf(0.005, 0.10)
    p("M131", f"redundant pair, each 0.5 % unavailable, 10 % common cause: {q:.6f},"
              f" {q / 0.005 ** 2:.0f} times the independent 0.000025")
    t_wk = 2 * 0.01 / 0.5 * 52
    p("M132", f"hidden diesel start failure, 0.5 a year, target 1 %: test every"
              f" {t_wk:.1f} weeks (T = 2U/lambda); a monthly test gives about 2 %")


def lifecycle_decisions() -> None:
    med = lifecycle.median_remaining(146_642.0, 2.5, 150_000.0)
    p("M133", f"gearbox run 146,642 h, Weibull k 2.5, c 150,000 h: median remaining"
              f" life {med:,.0f} h - less than a new unit's mean suggests")
    fund = lifecycle.sinking_fund(4_635.0, 7, 0.04)
    p("M134", f"decommissioning fund of 4,635 k u in 7 years at 4 %: {fund:,.0f} k u a"
              " year - about five times a fund started in year 1")
    e = lifecycle.eac(1_000.0, 10, 0.075)
    p("M135", f"1,000 k u over 10 years at 7.5 %: equivalent annual cost {e:,.1f} k u -"
              " for options of different lives, valid only if the life is used")
    g = 1_000.0 * 1e6 / (2_000_000.0 * 1e3)
    p("M136", f"1,000 t CO2e over 2,000,000 MWh: {g:.2f} g CO2e/kWh on one boundary;"
              " avoided emissions are reported apart and never added")


if __name__ == "__main__":
    operation()
    maintenance()
    lifecycle_decisions()
    emit("mastery_part9", OUT)
