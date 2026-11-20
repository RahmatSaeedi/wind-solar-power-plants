"""Chapter 30, lesson W: two summaries - the load path from rotor to soil
with the governing check at each link, and how the base radius that
the frequency rule needs at T07 moves with the soil stiffness, the
margin and the top mass.

Run from the project root:   python -m companion.ch30.examples_w
Writes companion/ch30/expected/w_*.txt and diagrams/data/ch30-radius.csv.
Teaching values (A-356 to A-359); the numbers come from lessons A-D.
"""
from __future__ import annotations

import math

from companion.ch30 import sources as src
from companion.ch30.common import csv, emit


def chain() -> None:
    links = [("tower wall, section 1", "fatigue of the welds", "B: walls 50/45/36 mm"),
             ("tower wall, section 1", "shell buckling", "B: use 1.02-1.06"),
             ("base flange bolts", "slip and separation", "Q: method sets min"),
             ("anchor cage", "joint stays closed", "G: 1,250 kN preload"),
             ("grout under the flange", "bearing stress", "G: 96 MPa class"),
             ("pedestal and slab", "reinforcement", "H: 64 kg/m3"),
             ("base on the ground", "lift-off and bearing", "D: 24 m at T07"),
             ("ground stiffness", "1P frequency margin", "B, D: governs T07")]
    lines = ["the load path from rotor to soil and what governs each link",
             "  link                       governing check          lesson: result"]
    for a, b, c in links:
        lines.append(f"  {a:26s} {b:24s} {c}")
    lines += ["  no single check sizes the turbine's structure: fatigue sets",
              "  the walls, preload the joints, stiffness the base - and",
              "  each link is only as good as the evidence for it"]
    emit("w_chain", lines)


def radius_needed(g_pa: float, margin: float, top_t: float, nu: float = 0.35) -> float:
    m_eff = (top_t + 0.24 * src.TOWER_T) * 1e3
    f_need = src.ONE_P_MAX * (1 + margin)
    if f_need >= src.F1_FIXED:
        return math.inf                     # even a rigid base cannot reach it
    f_rot = 1 / math.sqrt(1 / f_need ** 2 - 1 / src.F1_FIXED ** 2)
    k = (2 * math.pi * f_rot) ** 2 * m_eff * src.HUB ** 2
    return (3 * (1 - nu) * k / (8 * g_pa)) ** (1 / 3)


def radius() -> None:
    base = radius_needed(25e6, src.MARGIN_1P, src.TOP_T)
    cases = [("soil G -30 % / +30 %", radius_needed(17.5e6, 0.10, src.TOP_T),
              radius_needed(32.5e6, 0.10, src.TOP_T)),
             ("margin 8 % / 11 %", radius_needed(25e6, 0.08, src.TOP_T),
              radius_needed(25e6, 0.11, src.TOP_T)),
             ("top mass -5 % / +5 %", radius_needed(25e6, 0.10, src.TOP_T * 0.95),
              radius_needed(25e6, 0.10, src.TOP_T * 1.05))]
    rows = [(k, n, round(lo, 2), round(hi, 2)) for k, (n, lo, hi) in enumerate(cases, 1)]
    csv("ch30-radius.csv", "k,name,low,high", [(k, n.split()[0], lo, hi) for k, n, lo, hi in rows])
    lines = ["base radius the 1P margin needs at T07 (G 25 MPa, 10 %, 271 t)",
             f"  base case: r = {base:.2f} m (diameter {2 * base:.1f} m)",
             "  input changed            r low m   r high m"]
    for name, lo, hi in cases:
        lines.append(f"  {name:24s} {lo:8.2f}   {hi:8.2f}")
    lines += ["  the margin rule moves the radius most - 11 % instead of",
              "  10 % needs a far larger base, and at 12 % even a rigid base",
              f"  fails (0.192 x 1.12 = {0.192 * 1.12:.5f} Hz, above the fixed 0.215):",
              "  then only a stiffer tower helps. Soil stiffness comes",
              "  next; the top mass barely matters - the maker's margin",
              "  and the measured stiffness are the numbers worth paying for"]
    emit("w_radius", lines)


if __name__ == "__main__":
    chain()
    radius()
