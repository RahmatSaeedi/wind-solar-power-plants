"""Chapter 30, lesson F: line and substation structures - wind on the
132 kV conductors and the tower, the transverse pull at the angle points
of the straightened route (ch 29), the broken-wire case, short-circuit
forces on busbars and gantries, and the main transformer on its plinth
in an earthquake.

Run from the project root:   python -m companion.ch30.examples_f
Writes companion/ch30/expected/f_*.txt. Teaching values (A-361, A-362);
the line designer and the substation designer decide.
"""
from __future__ import annotations

import math

from companion.ch24 import sources as s24
from companion.ch30 import sources as src
from companion.ch30.common import emit
from plantp import structures as st

D_COND, D_EARTH = 0.024, 0.012          # m, conductor and earth wire (teaching)
T_MAX, T_EARTH = 35.0, 15.0             # kN, maximum working tensions (teaching)
MU0_2PI = 2e-7


def tower_wind() -> None:
    v20 = src.SITE["gust50_10m"] * (20 / 10) ** 0.11
    q = st.dynamic_pressure(v20, src.SITE["rho"])
    span = s24.LINE["span_m"]
    phase = st.drag_force(q, 1.0, D_COND * span) / 1e3
    earth = st.drag_force(q, 1.0, D_EARTH * span) / 1e3
    body = 8.0
    total = 3 * phase + earth + body
    lines = ["transverse wind on a 132 kV suspension tower (50-yr gust at 20 m)",
             f"  gust {v20:.1f} m/s, pressure {q:,.0f} Pa, wind span {span:.0f} m",
             f"  each phase conductor ({1000 * D_COND:.0f} mm): {phase:.1f} kN;"
             f" earth wire {earth:.1f} kN",
             f"  tower body {body:.0f} kN (teaching)",
             f"  total transverse load {total:.1f} kN",
             "  the wires, not the lattice, catch most of the wind: wire",
             "  diameter and span set the tower's transverse case"]
    emit("f_wind", lines)


def angles() -> None:
    lines = ["transverse pull at the angle points of the straightened route (ch 29)",
             f"  per wire 2 T sin(theta/2); T {T_MAX:.0f} kN on 3 phases, {T_EARTH:.0f} kN earth wire",
             "  deviation deg   per phase kN   whole tower kN   tower type"]
    for th in (40, 44, 45, 86):
        per = 2 * T_MAX * math.sin(math.radians(th / 2))
        tot = 3 * per + 2 * T_EARTH * math.sin(math.radians(th / 2))
        kind = "terminal / dead-end" if th > 60 else "heavy angle"
        lines.append(f"  {th:13d}   {per:12.1f}   {tot:14.1f}   {kind}")
    lines += ["  at 40-45 deg the wires pull more than twice as hard as",
              "  the storm pushes a suspension tower; at 86 deg almost",
              "  five times -",
              "  that tower is nearly a dead end - which is why the line",
              "  designer may split that turn into two smaller angles"]
    emit("f_angles", lines)


def broken() -> None:
    h_arm = 24.0
    lines = ["broken-wire case on a suspension tower (teaching)",
             f"  one phase breaks: unbalanced pull {T_MAX:.0f} kN along the line at {h_arm:.0f} m",
             f"  base moment about the line's direction: {T_MAX * h_arm:.0f} kN m",
             "  (with torsion from the offset crossarm)",
             "  intact towers see no longitudinal load at all; this case",
             "  (and a cascade stopped by stronger towers every few km)",
             "  sizes the tower's longitudinal bracing and its foundations"]
    emit("f_broken", lines)


def busbar() -> None:
    cases = [("132 kV gantry, fault 7.8 kA (ch 28)", 7.79, 2.5),
             ("33 kV busbar, fault 8.5 kA (ch 28)", 8.54, 0.5),
             ("33 kV busbar at the gear's rated peak", 63.0 / (1.8 * math.sqrt(2)), 0.5)]
    lines = ["short-circuit force between parallel conductors, F' = 2e-7 ip^2 / a",
             "  (peak factor 1.8; teaching spacings)",
             "  case                                       ip kA   a m   N per m"]
    for name, i_k, a in cases:
        ip = 1.8 * math.sqrt(2) * i_k * 1e3
        f = MU0_2PI * ip ** 2 / a
        lines.append(f"  {name:40s} {ip / 1e3:7.1f}   {a:3.1f}   {f:8.0f}")
    lines += ["  the 132 kV gantry hardly notices a fault; close-spaced",
              "  33 kV bars feel a sharp blow - supports and insulators are",
              "  designed to the gear's rated peak, not today's fault",
              "  level, because the network's fault level grows (ch 28)"]
    emit("f_busbar", lines)


def transformer() -> None:
    mass, h_cg, b = 95e3, 2.5, 3.0
    v = st.base_shear(mass, 0.625)
    m_over = v * h_cg
    w = mass * 9.81
    m_res = w * b / 2
    anchor = max(m_over - m_res, 0.0) / b
    lines = ["main transformer on its plinth in the teaching earthquake (a_seismic)",
             f"  shear {v / 1e3:.0f} kN at {h_cg} m: overturning {m_over / 1e3:,.0f} kN m",
             f"  weight {w / 1e3:.0f} kN on a {b} m anchor base: resisting {m_res / 1e3:,.0f} kN m",
             f"  net uplift on one side: {anchor / 1e3:.0f} kN -> anchors in tension",
             "  without anchors a heavy, short transformer can still tip",
             "  or slide in a strong earthquake; anchors, the plinth and",
             "  the bushings' qualification (tall porcelain is fragile)",
             "  come from the local seismic code and the maker (ch 25)"]
    emit("f_transformer", lines)


if __name__ == "__main__":
    tower_wind()
    angles()
    broken()
    busbar()
    transformer()
