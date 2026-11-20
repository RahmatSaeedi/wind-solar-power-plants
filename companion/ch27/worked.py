"""Chapter 27 - small worked examples (E-lines) and the numerical answers
of the exercises (P-lines), each computed here.

Run from the project root:   python -m companion.ch27.worked
Writes companion/ch27/expected/worked.txt and solutions.txt.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch27.common import emit
from plantp import ac
from plantp import pq


def worked() -> None:
    lines = [f"E01 THD of 3 A and 4 A over 50 A: {pq.thd({5: 3, 7: 4}, 50):.1%}",
             f"E02 TDD of the same over 100 A demand: {pq.tdd({5: 3, 7: 4}, 100):.1%}",
             f"E03 resonance of 365 MVA with 1.77 Mvar: h = {ac.resonance_order(365, 1.77):.1f}",
             f"E04 current at 100 MW, 132 kV, pf 0.9: {ac.line_current_a(100e6, 132e3, 0.9):.0f} A",
             f"E05 dU for -30 MW at 500 MVA, X/R 5: {100 * pq.voltage_change(-30, 0, 500, 5):.2f} %"]
    emit("worked", lines)


def solutions() -> None:
    c3, l3, xc3, xl3 = pq.tuned_filter(3.0, 4.7, 33.0)
    i08 = ac.line_current_a(100e6, 132e3, 0.8)
    va, vb, vc = 1.0, 0.95 * complex(math.cos(math.radians(-120)), math.sin(math.radians(-120))), \
        complex(math.cos(math.radians(120)), math.sin(math.radians(120)))
    t = np.linspace(0, 5, 5001)
    m = pq.step_metrics(t, 1 - np.exp(-t / 0.4), 0.0, 1.0)
    out = [f"P01 THD at 20 % output when TDD is 1.6 %: {1.6 / 0.2:.1f} %",
           f"P02 TDD of 3 A and 4 A over a 100 A demand: {pq.tdd({5: 3, 7: 4}, 100):.1%}",
           f"P03 resonance, 365 MVA with 3 Mvar: h = {ac.resonance_order(365, 3):.1f}",
           f"P04 filter 3 Mvar at 33 kV tuned 4.7: X_C {xc3:.0f} ohm, X_L {xl3:.1f} ohm, C {c3:.2f} uF",
           f"P05 current at 100 MW, 132 kV, pf 0.8: {i08:.0f} A",
           f"P06 line loss at that current (0.847 ohm): {3 * i08 ** 2 * 0.847 / 1e3:.0f} kW",
           f"P07 dU for -20 MW at 500 MVA, X/R 5: {100 * pq.voltage_change(-20, 0, 500, 5):.2f} %",
           f"P08 Q to cancel it: {20 / 5:.1f} Mvar",
           f"P09 SCR of 800 MVA for a 100 MW plant: {800 / 100:.0f}",
           f"P10 ten sources of 2 A, alpha 1.4: {pq.summation([2.0] * 10, 1.4):.1f} A",
           f"P11 unbalance with phase b at 0.95 pu: {100 * ac.unbalance_factor(va, vb, vc):.2f} %",
           f"P12 first order tau 0.4 s: rise {m['rise']:.2f} s, settle (5 %) {m['settle']:.2f} s",
           f"P13 droop 5 % on 100 MW, 0.4 Hz with 0.2 Hz deadband: {100 * 0.2 / (50 * 0.05):.0f} MW",
           f"P14 one-minute steps 0, 6, 3, 12, 13 MW over 5 MW/min: "
           f"{pq.ramp_exceedance(np.array([0, 6, 3, 12, 13]), 5.0):.0%}",
           f"P15 samples lost at 99.5 % completeness, 4 s for a week: {151200 * 0.005:.0f}",
           f"P16 two of ten capacitor units failed: tuned to {4.7 / math.sqrt(0.8):.2f}",
           f"P17 4 % and 3 % combined: {math.hypot(4, 3):.1f} %",
           f"P18 sign of P5 at 85 +/- 10 deg: {'inconclusive' if math.cos(math.radians(95)) < 0 else 'positive'}",
           f"P19 the top 5 % of 1,008 values: {0.05 * 1008:.0f} values = {0.05 * 1008 / 6:.1f} h",
           f"P20 Q at 90 MW from 121 MVA of units: {ac.q_capability(121, 90):.1f} Mvar",
           f"P21 capacitor voltage in a filter tuned 4.7: {1 + 1 / (4.7 ** 2 - 1):.3f} pu",
           f"P22 PF true with displacement 0.98 and THD_I 10 %: {ac.power_factor_true(0.98, 0.10):.3f}"]
    emit("solutions", out)


def solutions2() -> None:
    """Numerical answers of the exercises added with the later lessons."""
    a = complex(-0.5, math.sqrt(3) / 2)
    f_r = 50 * math.sqrt(365 / 1.77)
    x5 = 121 / 500
    choke = {5: 0.35, 7: 0.20, 11: 0.08, 13: 0.06}
    thd_aux = math.sqrt(sum((0.4 * c * h * 0.04) ** 2 for h, c in choke.items()))
    d = math.log(2.0 / 1.6)
    out = [f"P23 flicker, 6 turbines c 8, 5.5 MVA on 600 MVA: "
           f"{8 * 5.5 / 600 * math.sqrt(6):.3f}",
           f"P24 Plt of twelve Pst of 0.4: {(12 * 0.4 ** 3 / 12) ** (1 / 3):.2f}",
           f"P25 voltage THD of 2.0 % and 1.5 %: {math.hypot(2.0, 1.5):.1f} %",
           f"P26 time to 90 % recovery, tau 0.5 s: {0.5 * math.log(75 / 8):.2f} s",
           f"P27 measured: own 1.2 %, background 0.5 % over 0.40 pu: "
           f"{math.hypot(1.2, 0.5 / 0.40):.2f} %",
           f"P28 Q at 0.95 pu voltage and 80 MW: "
           f"{math.sqrt((121 * 0.95) ** 2 - 80 ** 2):.1f} Mvar",
           f"P29 unbalance margin, 1.2 % against 1.4 %: {1 - 1.2 / 1.4:.0%}",
           f"P30 damping from peaks 2.0 and 1.6: "
           f"{d / math.sqrt(4 * math.pi ** 2 + d * d):.3f}",
           f"P31 3p frequency at 10 rpm: {3 * 10 / 60:.1f} Hz",
           f"P32 spread factor with k 6.6 at SCR 5: {1 / (1 + 6.6 / 5):.2f}",
           f"P33 CVT gain at the 9th, resonance near the 10th: "
           f"{1 / abs(1 - 0.81):.2f}",
           f"P34 bus above POC at 50 MW, 0 Mvar: "
           f"{100 * 0.5 * 0.12 * 7.06 / 174.24:.2f} %",
           f"P35 Q at pf 0.95 and 100 MW: "
           f"{100 * math.tan(math.acos(0.95)):.1f} Mvar",
           f"P36 share reaching the grid at 5 kHz: "
           f"{1 / abs(1 - (5000 / f_r) ** 2):.3f}",
           f"P37 DC 0.5 % against magnetising peak (0.5 %): "
           f"{0.5 / (math.sqrt(2) * 0.5):.2f}",
           f"P38 series resonance from 132 kV with X_T 3.0 ohm: "
           f"{math.sqrt(228.1 / (10.33 + 3.0)):.2f}",
           f"P39 unbalance, 30 km line at half current: "
           f"{100 * 0.03 * 30 * 218.5 / (132e3 / math.sqrt(3)):.2f} %",
           f"P40 33 kV phases for a zero-volt fault at the POC: "
           f"{abs(0 - a * a) / math.sqrt(3):.3f} (two), "
           f"{abs(a * a - a) / math.sqrt(3):.3f} (one)",
           f"P41 dip 0.80 at SCR 5 with k 2: "
           f"{(0.8 + 2 * x5) / (1 + 2 * x5):.3f} pu",
           f"P42 fault distance for 0.9 pu residual: "
           f"{0.9 / 0.1 * 132 ** 2 / 1500 / 0.4:.0f} km",
           f"P43 resonance with 12 units online: "
           f"{math.sqrt(365 / (1.77 + 12 * 0.15)):.1f}",
           f"P44 aux board THD, 100 kW of drives with chokes: "
           f"{100 * thd_aux:.1f} %"]
    emit("solutions2", out)


if __name__ == "__main__":
    worked()
    solutions()
    solutions2()
