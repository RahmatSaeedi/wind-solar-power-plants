"""Chapter 29 - small worked examples (E-lines) and the numerical answers
of the exercises (P-lines), each computed here.

Run from the project root:   python -m companion.ch29.worked
Writes companion/ch29/expected/worked.txt and solutions.txt.
"""
from __future__ import annotations

import math

from companion.ch29.common import emit
from plantp import civil as cv


def worked() -> None:
    nc, nq, ng = cv.bearing_factors(30)
    lines = [f"E01 refraction depth, crossover 30 m, 500/2000 m/s: {cv.refraction_depth(30, 500, 2000):.2f} m",
             f"E02 bearing factors at 30 deg: Nc {nc:.2f}, Nq {nq:.2f}, Ngamma {ng:.2f}",
             f"E03 rational method, C 0.5, 50 mm/h, 1 km2: {cv.rational_peak(0.5, 50, 1.0):.2f} m3/s",
             f"E04 Manning, 1 m wide 0.5 m deep, n 0.015, 1 %: {cv.manning_q(0.015, 0.5, 2.0, 0.01):.3f} m3/s",
             f"E05 USLE, R 100, K 0.3, LS 1, C 0.1: {cv.usle(100, 0.3, 1.0, 0.1, 1.0):.1f} t/ha/yr",
             f"E06 Gumbel 100-year level, mu 10, beta 2: {cv.gumbel_return(10, 2, 100):.2f}",
             f"E07 2:1 spread, 1,000 kN on 1 x 1 m at 1 m depth: {cv.spread_pressure(1000, 1, 1, 1):.0f} kPa",
             f"E08 settlement, 200 kPa, B 2 m, E 20 MPa, I 1: {1000 * cv.elastic_settlement(200, 2, 20000, 0.3, 1):.1f} mm"]
    emit("worked", lines)


def solutions() -> None:
    out = [f"P01 refraction depth, crossover 40 m, 400/1800 m/s: {cv.refraction_depth(40, 400, 1800):.1f} m",
           f"P02 Nq at 34 deg: {cv.bearing_factors(34)[1]:.1f}",
           f"P03 square 2 m footing, sand phi 30, gamma 18, depth 1 m: {cv.bearing_square(0, 30, 18, 2, 1):.0f} kPa",
           f"P04 allowable with FS 3: {cv.bearing_square(0, 30, 18, 2, 1) / 3:.0f} kPa",
           f"P05 settlement, 150 kPa, B 20 m, E 40 MPa: {1000 * cv.elastic_settlement(150, 20, 40000):.0f} mm",
           f"P06 rational, C 0.35, 30 mm/h, 3.2 km2: {cv.rational_peak(0.35, 30, 3.2):.1f} m3/s",
           f"P07 Kirpich, 1.5 km at 2 %: {cv.kirpich_tc(1500, 0.02):.0f} min",
           f"P08 1.2 m pipe full at 1 %, n 0.024: {cv.pipe_full_q(0.024, 1.2, 0.01):.2f} m3/s",
           f"P09 USLE, R 300, K 0.3, LS 2.07, C 0.5: {cv.usle(300, 0.3, 2.07, 0.5, 1):.0f} t/ha/yr",
           f"P10 widening, R 80 m, L 30 m: {80 - math.sqrt(80 ** 2 - 30 ** 2):.1f} m",
           f"P11 crane mat 2,000 kN on 2 x 5 m at 1 m: {cv.spread_pressure(2000, 2, 5, 1):.0f} kPa",
           f"P12 lot 95, 96, 97 with k 0.5: mean - 0.5 s = {cv.lot_accept([95, 96, 97], 95, 0.5)[1]:.2f}",
           f"P13 characteristic of 40, 42, 44, 46 MPa: {cv.characteristic([40, 42, 44, 46]):.1f} MPa",
           f"P14 Cooper-Jacob, 0.4 L/s, T 1.5e-4, S 2e-4, r 0.3 m, 30 d: "
           f"{cv.cooper_jacob(4e-4, 1.5e-4, 2e-4, 0.3, 30 * 86400):.1f} m",
           f"P15 trench inflow k 1e-4, h 5 to 4.7 m, R 30 m, 2 sides, 100 m: "
           f"{2 * cv.trench_inflow(1e-4, 5, 4.7, 30) * 100 * 1000:.2f} L/s",
           f"P16 50-year level, mu 16, beta 6: {cv.gumbel_return(16, 6, 50):.1f} mm",
           f"P17 raw water for 1,529 m3 treated at 60 % recovery: {1529 / 0.6:.0f} m3",
           f"P18 firewater 3,000 L/min for 60 min: {3000 * 60 / 1000:.0f} m3",
           f"P19 washes of 109.2 m3 each in 1,529 m3: {1529 / 109.2:.0f}",
           f"P20 towers on 7.06 km at 300 m spans: {math.ceil(7060 / 300) + 1}"]
    emit("solutions", out)


if __name__ == "__main__":
    worked()
    solutions()
