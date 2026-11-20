"""Chapter 33 - small worked examples (E-lines) and the numerical answers
of the exercises (P-lines), each computed here.

Run from the project root:   python -m companion.ch33.worked
Writes companion/ch33/expected/worked.txt and solutions.txt.
"""
from __future__ import annotations

import math

from companion.ch33.common import emit
from plantp import civil as cv
from plantp import envsocial as es


def worked() -> None:
    lines = [f"E01 two equal sources of 40 dB(A): {es.db_sum([40, 40]):.1f} dB(A)",
             f"E02 one turbine (106) at 1,000 m: {es.noise_at(106, 1000):.1f} dB(A)",
             f"E03 collisions, 500 passages, p 0.08, avoidance 0.98: "
             f"{es.collision_estimate(500, 0.08, 0.98):.2f} a year",
             f"E04 livelihood, 100 ha x 0.8 animals/ha x 0.12 k u: "
             f"{es.livelihood_income(100, 0.8, 0.12):.1f} k u a year",
             f"E05 footprint, 1,000 t over 100 GWh: {es.per_kwh(1e6, 1e8):.1f} g/kWh",
             f"E06 indicator 88 % vs target 90 %, tolerance 5: {es.kpi_rag(88, 90, 5)}",
             f"E07 probability of 1 % rain event in 25 yr: {(1 - 0.99 ** 25) * 100:.0f} %"]
    emit("worked", lines)


def solutions() -> None:
    out = [f"P01 sum of 38.5 and 28 dB(A): {es.db_sum([38.5, 28]):.1f}",
           f"P02 sum of 28, 33 and 38.5 dB(A): {es.db_sum([28, 33, 38.5]):.1f}",
           f"P03 one turbine at 806 m: {es.noise_at(106, 806):.1f} dB(A)",
           f"P04 one turbine at 2,854 m: {es.noise_at(106, 2854):.1f} dB(A)",
           f"P05 collisions, 739 passages: {es.collision_estimate(739, 0.08, 0.98):.2f}",
           f"P06 collisions with avoidance 0.99 instead: {es.collision_estimate(739, 0.08, 0.99):.2f}",
           f"P07 grazing income, 780 ha, 600 animals, 0.12 k u: "
           f"{es.livelihood_income(780, 600 / 780, 0.12):.0f} k u",
           f"P08 extra walking, detour 3.5 vs 1.2 km, there and back: {(3.5 - 1.2) * 2:.1f} km a day",
           f"P09 PV modules, 60,000 kWp x 450 kg: {60_000 * 450 / 1000:,.0f} t",
           f"P10 towers, 4,464 t x 2,000 kg/t: {4464 * 2.0:,.0f} t",
           f"P11 S0 g/kWh, 90,252 t over 7,378 GWh: {es.per_kwh(90_252e3, 7_377.5e6):.1f}",
           f"P12 avoided at 0.5 t/MWh, 295,100 MWh: {295_100 * 0.5:,.0f} t a year",
           f"P13 recharge, 20 km2, 120 mm, 3 %: {20e6 * 0.12 * 0.03:,.0f} m3",
           f"P14 drawdown 3 km after 1 yr (0.4 L/s, T 1.5e-4, S 2e-4): "
           f"{cv.cooper_jacob(4e-4, 1.5e-4, 2e-4, 3000, 365 * 86400):.2f} m",
           f"P15 sampling grid, 2,400 m2 at 100 m2: {math.ceil(2400 / 100)} samples",
           f"P16 tanker loads, 160 m3 at 20 m3: {math.ceil(160 / 20)}",
           f"P17 indicator 55 vs target 80, tolerance 10: {es.kpi_rag(55, 80, 10)}",
           f"P18 water intensity, 3,986 m3 over 295,100 MWh: {3986 / 295_100 * 1000:.1f} L/MWh",
           f"P19 budget share, 270 k u of 20,657 k u: {270 / 20_657 * 100:.1f} %",
           f"P20 offset area, 18.7 ha at 2:1: {18.7 * 2:.1f} ha"]
    emit("solutions", out)


if __name__ == "__main__":
    worked()
    solutions()
