"""Chapter 30, lesson P: more on foundations and materials - soil stiffness
falls with strain, sliding of the gravity base, yield strength falls
with plate thickness, reading a pile load test, and the efficiency of a
pile group.

Run from the project root:   python -m companion.ch30.examples_p
Writes companion/ch30/expected/p_*.txt and diagrams/data/ch30-gdeg.csv,
ch30-pile.csv. Teaching values (A-357, A-358); the geotechnical engineer
and the product standards set the real ones.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch30 import sources as src
from companion.ch30.common import csv, emit
from plantp import structures as st

G0_T07 = 75e6          # small-strain shear modulus at T07 (teaching, A-358)
GAMMA_REF = 1e-4       # reference strain of the hyperbolic curve


def g_ratio(gamma: float) -> float:
    return 1 / (1 + gamma / GAMMA_REF)


def degradation() -> None:
    rows = [(f"{g:.1e}", round(g_ratio(g), 4)) for g in np.logspace(-6, -2, 41)]
    csv("ch30-gdeg.csv", "strain,ratio", rows)
    m_eff = (src.TOP_T + 0.24 * src.TOWER_T) * 1e3
    lines = ["soil stiffness falls with strain (hyperbolic model, T07, teaching)",
             f"  G0 = {G0_T07 / 1e6:.0f} MPa at very small strain; reference strain {GAMMA_REF:.0e}",
             "  state                   strain    G/G0   G MPa   K GN m/rad   f1 Hz"]
    for name, g in [("vibration, small", 1e-5), ("operation, typical", 2e-4),
                    ("extreme storm", 1e-3)]:
        gg = G0_T07 * g_ratio(g)
        k = st.rotational_stiffness(gg, src.FOUNDATION["r"], 0.35)
        f = st.frequency_with_foundation(src.F1_FIXED, k, m_eff, src.HUB)
        lines.append(f"  {name:22s} {g:7.0e}   {g_ratio(g):4.2f}   {gg / 1e6:5.0f}"
                     f"   {k / 1e9:10.0f}   {f:5.3f}")
    lines += ["  the operating strain gives lesson B's 25 MPa; a storm",
              "  softens the ground further and lowers f1 for a while -",
              "  the frequency check uses the operating strain, the",
              "  rotation check the extreme one, and the geotechnical",
              "  report states both, from tests, not from this curve"]
    emit("p_gdeg", lines)


def sliding() -> None:
    f = src.FOUNDATION
    v = (f["concrete_m3"] * f["gamma_c"] + f["backfill_m3"] * f["gamma_b"]
         + (src.TOP_T + src.TOWER_T) * 9.81)
    h = src.LOADS["extreme (parked, 50-yr gust)"]["h_mn"] * 1000
    lines = ["sliding of the gravity base under the extreme load (teaching)"]
    for name, phi in [("dense sand, phi 36", 36.0), ("T07 medium sand, phi 30", 30.0)]:
        mu = math.tan(math.radians(2 / 3 * phi))
        lines.append(f"  {name:25s} base friction {mu:.2f}: resistance {mu * v / 1000:5.1f} MN,"
                     f" FS {mu * v / h:4.1f}")
    lines += [f"  vertical load {v / 1000:.1f} MN, horizontal {h / 1000:.2f} MN",
              "  a wind turbine base does not slide: the horizontal force",
              "  is small beside its weight; the moment governs (lift-off,",
              "  bearing, rotation) - the check is done and recorded, but",
              "  it is not where the design is decided"]
    emit("p_sliding", lines)


def thickness() -> None:
    steps = [(16, 355), (40, 345), (63, 335), (80, 325)]       # typical S355 steps
    lines = ["yield strength falls with plate thickness (typical S355 steps)",
             "  thickness mm   fy MPa   section-1 can (50 mm): fy used"]
    for t_max, fy in steps:
        lines.append(f"  up to {t_max:5d}    {fy:6d}")
    d, t = 4.50, 0.050
    w = src.tube_w(d, t)
    m = src.LOADS["extreme (parked, 50-yr gust)"]["m_mnm"] * 1e6 * 1.35 * 0.85
    s = m / w / 1e6
    lines += [f"  stress at the top of section 1 (factored, teaching): {s:.0f} MPa",
              f"  use with 355: {s / 355:.2f}; with the 50 mm value 335: {s / 335:.2f}",
              "  thickening a can for fatigue moves it into a lower yield",
              "  class: every check of the thick sections uses the yield",
              "  for its own thickness, from the mill certificate's product",
              "  standard (lesson C), never the grade's headline number"]
    emit("p_thickness", lines)


def pile_test() -> None:
    d, l_m, e = 0.6, 14.0, 30e9
    area = math.pi * d * d / 4
    loads = np.arange(0, 3601, 300.0)                         # kN
    rng = np.random.default_rng(30)
    q_ult = 3000.0
    elastic = loads * 1e3 * l_m / (area * e) * 1e3              # mm
    settle = (elastic * 1.3 + 25 * (loads / q_ult) ** 4
              + rng.normal(0, 0.2, loads.size).clip(-0.3, 0.3))
    settle[0] = 0.0
    settle = np.maximum.accumulate(np.maximum(settle, 0))
    csv("ch30-pile.csv", "load,settle", [(int(p), round(s, 2)) for p, s in zip(loads, settle)])
    offset = 4 + d * 1000 / 120
    line = elastic + offset
    k = int(np.argmax(settle >= line))
    p0, p1 = loads[k - 1], loads[k]
    s0, s1 = settle[k - 1] - line[k - 1], settle[k] - line[k]
    cap = p0 + (p1 - p0) * (-s0) / (s1 - s0)
    lines = ["reading a static load test on a 0.6 m pile, 14 m long (synthetic)",
             "  load kN   settlement mm   offset line mm"]
    for p, s, ln in zip(loads, settle, line):
        lines.append(f"  {p:7.0f}   {s:13.1f}   {ln:14.1f}")
    lines += [f"  elastic line PL/AE plus 4 mm + D/120 = {offset:.1f} mm (Davisson)",
              f"  the curve crosses it at about {cap:,.0f} kN: the pile's capacity",
              "  the method gives one defined number from a curve that",
              "  bends gradually; the test pile, its loading steps and the",
              "  method are named in the test specification before the test"]
    emit("p_piletest", lines)


def group() -> None:
    lines = ["efficiency of a pile group (Converse-Labarre, teaching)",
             "  group    d m   spacing m   theta deg   efficiency"]
    for m, n, d, s in [(3, 3, 0.6, 1.8), (5, 5, 0.6, 1.8), (5, 5, 0.6, 2.4)]:
        th = math.degrees(math.atan(d / s))
        eff = 1 - th * ((n - 1) * m + (m - 1) * n) / (90 * m * n)
        lines.append(f"  {m} x {n}  {d:5.1f}   {s:9.1f}   {th:9.1f}   {eff:10.2f}")
    lines += ["  a crowded group carries less than the sum of its piles in",
              "  clay; driven piles in sand can carry more, because driving",
              "  densifies the sand between them - the formula is a",
              "  reminder that a group is not a sum, and the engineer uses",
              "  the method that fits the soil and the installation"]
    emit("p_group", lines)


if __name__ == "__main__":
    degradation()
    sliding()
    thickness()
    pile_test()
    group()
