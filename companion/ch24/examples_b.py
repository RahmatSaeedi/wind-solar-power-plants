"""Chapter 24, sections B and C - the cable as a product and in the
field (layers, bending radius, pulling tension around bends, sidewall
pressure, drum lengths) and switchgear duties (rated values against the
fault levels of chapter 23, peak current, short-time withstand, the
force between busbars in a fault).

Run from the project root:   python -m companion.ch24.examples_b
Writes companion/ch24/expected/b_*.txt and c_*.txt. Teaching values
A-321 to A-325; pulling and bending limits come from the cable maker.
"""
from __future__ import annotations

import math

from companion.ch24 import sources as src
from companion.ch24.common import emit
from plantp import cables as cb

LAYERS = [  # 33 kV 3-core Al XLPE, one core then the whole (teaching, mm)
    ("conductor (compacted Al strands)", 0, 23.8),
    ("conductor screen (semiconducting)", 0.8, 0),
    ("insulation (XLPE)", 8.0, 0),
    ("insulation screen (semiconducting)", 0.8, 0),
    ("metallic screen (Cu wires and tape)", 0.6, 0),
]


def layers() -> None:
    d = 23.8
    lines = ["one core of a 33 kV 400 mm2 Al XLPE cable, layer by layer:",
             "  layer                                 thickness  diameter mm"]
    lines.append(f"  {LAYERS[0][0]:38s} {'-':>9s}  {d:10.1f}")
    for name, t, _ in LAYERS[1:]:
        d += 2 * t
        lines.append(f"  {name:38s} {t:9.1f}  {d:10.1f}")
    core = d
    overall = 2.155 * core + 2 * 2.5 + 2 * 3.0      # three cores, bedding, sheath
    lines += [f"  three cores laid up, bedding and PE sheath: about {overall:.0f} mm",
              f"  insulation stress at the conductor screen: 33/sqrt3 kV over"
              f" {LAYERS[2][1]:.0f} mm",
              f"    mean field {33 / math.sqrt(3) / LAYERS[2][1]:.1f} kV/mm - the screens"
              " keep it radial",
              "  each layer has a process and a test in the factory (ch 41):",
              "  extrusion of the three inner layers in one pass, then",
              "  checks of thickness, eccentricity and partial discharge"]
    emit("b_layers", lines)
    return overall


def pulling(overall_mm: float = 87.0) -> None:
    w = 9.8 * 7.5                                     # N/m, about 7.5 kg/m
    mu = 0.35                                         # friction in a duct
    # route: 200 m straight, 90-degree bend (r 1.5 m), 150 m, 45-degree bend
    t = mu * w * 200
    rows = [("200 m straight", t)]
    t = t * math.exp(mu * math.pi / 2)
    rows.append(("90 degree bend", t))
    t += mu * w * 150
    rows.append(("150 m straight", t))
    t = t * math.exp(mu * math.pi / 4)
    rows.append(("45 degree bend", t))
    side = t / 1.5                                    # N/m on the bend
    lines = ["pulling a 33 kV cable into a duct (teaching numbers):",
             f"  weight {w:.0f} N/m, friction {mu}; bend radius 1.5 m",
             "  after              tension kN"]
    lines += [f"  {n:18s} {v / 1e3:9.1f}" for n, v in rows]
    lim = 30 * 400 * 3 / 1e3                          # 30 N/mm2 on Al conductors
    r_min = 15 * overall_mm / 1e3
    lines += [f"  limit on the conductors (30 N/mm2 x 3 x 400 mm2): {lim:.0f} kN",
              f"  sidewall pressure on the last bend: {side / 1e3:.1f} kN/m",
              f"  least bending radius (15 x {overall_mm:.0f} mm): {r_min:.1f} m",
              ("    - the route's 1.5 m bends are too tight" if r_min > 1.5
               else "    - the route's 1.5 m bends are wide enough"),
              "  the bends multiply the tension (capstan: T e^(mu theta)):",
              "  pull from the end nearer the bends; the maker's limits and",
              "  the pulling record (tension logged) close the step"]
    emit("b_pulling", lines)


def drums() -> None:
    lines = ["drum lengths and the joints they force (route 4.4 km a string):"]
    for drum in (0.5, 0.75, 1.1, 1.5):
        joints = 4 * max(0, math.ceil(1.1 / drum) - 1)
        lines.append(f"  drum {drum * 1000:5.0f} m: {joints:2d} joints a string")
    lines += ["  a drum of one section's length removes the joints between",
              "  turbines; the drum's size is then limited by transport",
              "  (weight, width, road) - a logistics trade-off (ch 46)"]
    emit("b_drums", lines)


def gear() -> None:
    duty = {"33 kV": (12.5, 14.0), "132 kV": (5.2, 15.0), "0.4 kV": (7.9, 4.0)}
    lines = ["switchgear duties against the teaching ratings (ch 23 faults):",
             "  gear     Ik kA  X/R   ip kA   rated ip  Ik for 1 s vs Ik 3 s rating"]
    for k, (ik, xr) in duty.items():
        r = src.SWITCHGEAR[k]
        ip = cb.peak_ka(ik, xr)
        ok = cb.short_time_ok(ik, 1.0, r["ik_ka"], r["tk_s"])
        lines.append(f"  {k:7s}  {ik:5.1f}  {xr:4.0f}  {ip:6.1f}  {r['ip_ka']:8.0f}"
                     f"   {'ok' if ok else 'no'}")
    lines += ["  peak current: ip = kappa sqrt2 Ik, kappa from X/R (about 1.8",
              "  for X/R 14): the making and the busbar forces follow ip;",
              "  the ratings come from the makers' type tests, which the",
              "  site cannot repeat (section C)"]
    emit("c_gear", lines)


def busbar_force() -> None:
    ip = src.SWITCHGEAR["33 kV"]["ip_ka"] * 1e3       # rated peak withstand
    lines = ["force between 33 kV busbars in a fault (two parallel bars):",
             "  F/L = 2e-7 ip^2 / a (N/m), ip the gear's rated peak (63 kA)"]
    for a in (0.15, 0.25, 0.35):
        f = 2e-7 * ip ** 2 / a
        lines.append(f"  spacing {a:.2f} m: {f / 1e3:5.1f} kN/m;"
                     f" on a 1 m span {f / 1e3:.1f} kN")
    lines += [f"  ip = {ip / 1e3:.1f} kA; the supports and bars are sized for it",
              "  by the maker and proved by the short-time and peak tests",
              "  of the type test - a site test cannot show it"]
    emit("c_force", lines)


if __name__ == "__main__":
    d = layers()
    pulling(d)
    drums()
    gear()
    busbar_force()
