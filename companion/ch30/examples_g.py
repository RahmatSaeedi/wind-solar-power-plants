"""Chapter 30, lesson G: materials and connection details - the steel's
toughness at the site's lowest temperature, a fillet weld sized by its
throat, the anchor-bolt cage that ties the tower to the concrete, the
grout under the tower flange, and the reinforcement of the foundation
slab.

Run from the project root:   python -m companion.ch30.examples_g
Writes companion/ch30/expected/g_*.txt. Teaching values (A-362).
"""
from __future__ import annotations

import math

from companion.ch30 import sources as src
from companion.ch30.common import emit
from plantp import datapack
from plantp import materials as mt
from plantp import structures as st


def _preload_needed() -> float:
    m_ext = src.LOADS["extreme (parked, 50-yr gust)"]["m_mnm"] * 1e6
    v = (src.TOP_T + src.TOWER_T) * 9.81 * 1e3
    worst = 4 * m_ext / (160 * 4.3) - v / 160
    return round(1.2 * worst / 50e3) * 50e3


PRELOAD = _preload_needed()


def toughness() -> None:
    t_min = float(datapack.load_hourly()["t_air_c"].to_numpy().min())
    rows = [("S355 with toughness tested at +20 C", 20), ("tested at 0 C", 0),
            ("tested at -20 C", -20), ("tested at -40 C", -40)]
    lines = ["steel toughness against the coldest steel temperature (teaching rule:",
             "  test temperature at or below the lowest service temperature, and",
             "  10 K lower for thick welded plates)",
             f"  lowest air temperature of the data-pack year: {t_min:.1f} C",
             f"  design value with the margin: {t_min - 10:.0f} C"]
    for name, t in rows:
        ok = t <= t_min - 10
        lines.append(f"  {name:38s} {'ok' if ok else 'not enough'}")
    lines += ["  a desert site still freezes: the tower plates are ordered",
              "  with toughness proven at -20 C; the grade, the test and",
              "  the plate thickness are on the mill certificate the",
              "  traveler checks at plate receipt (lab E)"]
    emit("g_toughness", lines)


def fillet() -> None:
    force = 300e3                                               # N on a door-frame weld (teaching)
    allow = 200e6                                               # teaching allowable shear
    lines = ["a fillet weld sized by its throat (teaching strength, no code factor)",
             f"  force {force / 1e3:.0f} kN along a weld; allowable shear ~ {allow / 1e6:.0f} MPa",
             "  leg mm   throat mm   length mm needed"]
    for leg in (6, 8, 10):
        a = 0.707 * leg / 1000
        length = force / (allow * a) * 1000
        check = mt.fillet_weld_stress(force, leg / 1000, length / 1000) / 1e6
        lines.append(f"  {leg:6d}   {1000 * a:9.1f}   {length:16.0f}   (stress check {check:.0f} MPa)")
    lines += ["  the throat, not the leg, carries the load: a bigger leg",
              "  shortens the weld but adds heat and distortion - the",
              "  welding engineer balances the two in the WPS"]
    emit("g_fillet", lines)


def anchors() -> None:
    m_ext = src.LOADS["extreme (parked, 50-yr gust)"]["m_mnm"] * 1e6
    v = (src.TOP_T + src.TOWER_T) * 9.81 * 1e3
    n, d_pitch = 2 * 80, 4.3
    worst = 4 * m_ext / (n * d_pitch) - v / n
    lines = ["anchor-bolt cage under the tower (160 bolts on a 4.3 m circle; teaching)",
             f"  extreme moment {m_ext / 1e6:.0f} MN m, weight {v / 1e6:.2f} MN",
             f"  pull on the worst bolt (4 M / n D - V / n): {worst / 1e3:,.0f} kN",
             "  preload kN   joint closed in the extreme?"]
    for preload in (600e3, 1000e3, PRELOAD):
        lines.append(f"  {preload / 1e3:10,.0f}   {'yes' if worst < preload else 'NO - it opens'}"
                     f" (margin {preload / worst:.2f})")
    lines += [f"  the cage needs about {PRELOAD / 1e3:,.0f} kN a bolt (margin 1.2): bigger bolts",
              "  or more of them; pretensioned anchors keep the concrete",
              "  under the flange in compression and the bolts' fatigue",
              "  range small - re-tensioning after the first months is in",
              "  the O&M plan"]
    emit("g_anchors", lines)


def grout() -> None:
    n, preload = 160, PRELOAD
    m_ext = src.LOADS["extreme (parked, 50-yr gust)"]["m_mnm"] * 1e6
    d_out, d_in = 4.6, 4.0
    area = math.pi / 4 * (d_out ** 2 - d_in ** 2)
    w_ring = math.pi / 32 * (d_out ** 4 - d_in ** 4) / d_out
    v = (src.TOP_T + src.TOWER_T) * 9.81 * 1e3
    sig = (n * preload + v) / area / 1e6 + m_ext / w_ring / 1e6
    lines = ["grout under the tower flange (ring 4.0-4.6 m, teaching)",
             f"  from preload and weight: {(n * preload + v) / area / 1e6:.1f} MPa;"
             f" plus extreme bending: {m_ext / w_ring / 1e6:.1f} MPa",
             f"  peak compression {sig:.1f} MPa against a high-strength grout",
             f"  (teaching 90 MPa class): use {sig / 90:.2f} - a wider flange ring or a",
             "  stronger grout follows from the higher preload",
             "  the grout is the highest-stressed material in the whole",
             "  foundation: its strength is tested (cubes), its curing",
             "  is controlled, and the bolts are tensioned only after it",
             "  has reached strength - a hold point (ch 29, n_itp)"]
    emit("g_grout", lines)


def slab() -> None:
    m_per_m = 2.4e6                                             # N m per m width (teaching)
    d_eff = 1.6
    fyd = 500e6 / 1.15
    a_s = st.rebar_area(m_per_m, d_eff, fyd)
    bar = math.pi * 0.032 ** 2 / 4
    lines = ["bottom reinforcement of the foundation slab under the pedestal",
             f"  moment {m_per_m / 1e6:.1f} MN m per metre, effective depth {d_eff} m (teaching)",
             f"  steel {a_s * 1e6:,.0f} mm2 per metre = {a_s / bar:.1f} bars of 32 mm"
             f" (every {1000 / (a_s / bar):.0f} mm)",
             f"  bottom mesh both ways under the 24 m base: about"
             f" {a_s * math.pi * 12 ** 2 * 2 * 7850 / 1000:.0f} t of steel",
             "  the bending design is the simple part; anchorage of the",
             "  bars, crack width under fatigue, shear and punching round",
             "  the pedestal are checked by the structural engineer -",
             "  the bending schedule is the factory's order (lesson H)"]
    emit("g_slab", lines)


if __name__ == "__main__":
    toughness()
    fillet()
    anchors()
    grout()
    slab()
