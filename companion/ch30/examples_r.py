"""Chapter 30, lesson R: more on line and substation structures - weight
span and uplift of a suspension tower in a hollow, leg forces and the
uplift foundation of a lattice tower, an equipment support in an
earthquake, and wind uplift on the control building's roof.

Run from the project root:   python -m companion.ch30.examples_r
Writes companion/ch30/expected/r_*.txt and diagrams/data/ch30-weightspan.csv.
Teaching values (A-361, A-362); the line designer's and the building
engineer's calculations govern.
"""
from __future__ import annotations

import math

from companion.ch30 import sources as src
from companion.ch30.common import csv, emit
from plantp import structures as st

W_COND = 11.8          # N/m, 24 mm conductor (teaching)
T_COLD = 35.0e3        # N, tension at the coldest (lesson F's maximum working tension)


def weight_span() -> None:
    span = 300.0
    rows = []
    lines = ["weight span of a suspension tower lower than its neighbours",
             f"  spans {span:.0f} m each side, conductor {W_COND} N/m, cold tension"
             f" {T_COLD / 1e3:.0f} kN",
             "  tower below both neighbours m   weight span m   vertical load N"]
    for drop in (0, 5, 10, 15, 20, 25):
        ws = span + T_COLD / W_COND * (-drop / span - drop / span)
        rows.append((drop, round(ws, 1)))
        lines.append(f"  {drop:29d}   {ws:13.0f}   {ws * W_COND:15,.0f}")
    csv("ch30-weightspan.csv", "drop,ws", rows)
    lim = span * span * W_COND / (2 * T_COLD)
    lines += [f"  the weight span reaches zero at a drop of {lim:.1f} m; any deeper",
              "  and the wires pull the insulator UP on the coldest night -",
              "  a suspension string cannot take that; the profile",
              "  places a tension tower or heavier attachment there, and",
              "  the wadi crossing of ch 29 is checked for exactly this"]
    emit("r_weightspan", lines)


def legs() -> None:
    h_kn, height = 163.7, 24.0            # dead-end pull (lesson F) at the crossarm level
    w_kn = 180.0                           # tower, wires and hardware vertical (teaching)
    ups = {}
    lines = ["leg forces of a square lattice tower under the dead-end pull",
             f"  transverse {h_kn:.0f} kN at {height:.0f} m; vertical {w_kn:.0f} kN (teaching)",
             "  base width m   moment kN m   leg kN (diagonal)   uplift leg kN"]
    for b in (6.0, 8.0, 10.0):
        m = h_kn * height
        leg = m / (b * math.sqrt(2))
        up = leg - w_kn / 4
        ups[b] = up
        lines.append(f"  {b:12.1f}   {m:11,.0f}   {leg:17.0f}   {up:13.0f}")
    # uplift resistance of a pad: concrete + soil frustum at 30 degrees (teaching)
    b_pad, depth, g_soil, g_conc = 2.4, 3.0, 18.0, 24.0
    top = b_pad + 2 * depth * math.tan(math.radians(30))
    v_frustum = depth / 3 * (b_pad ** 2 + top ** 2 + b_pad * top)
    conc = b_pad * b_pad * 0.5 * g_conc
    soil = (v_frustum - b_pad * b_pad * 0.5) * g_soil
    lines += [f"  pad {b_pad} m square at {depth:.0f} m: concrete {conc:.0f} kN +"
              f" soil cone {soil:,.0f} kN",
              f"  resistance {conc + soil:,.0f} kN against {ups[8.0]:.0f} kN on an 8 m base"
              f" (FS {(conc + soil) / ups[8.0]:.1f})",
              "  a dead-end tower is held down by the soil above its pads;",
              "  the cone method is a teaching estimate - the line",
              "  designer uses the code's method and site test results"]
    emit("r_legs", lines)


def equipment() -> None:
    m, h = 1800.0, 3.0                     # breaker pole kg on a 3 m steel column (teaching)
    lines = ["a circuit breaker on its support in an earthquake (teaching)",
             f"  mass {m:,.0f} kg at {h:.0f} m; ground acceleration ag {src.SITE['ag']} g",
             "  support          stiffness kN/m   f Hz   spectral acc. g   base shear kN"]
    for name, k in [("stiff column", 4000.0), ("slender column", 900.0),
                    ("braced frame", 20000.0), ("rigid pedestal", 80000.0)]:
        f = math.sqrt(k * 1e3 / m) / (2 * math.pi)
        sa = src.SITE["ag"] * (2.5 if f < 10 else 2.5 - 1.5 * (f - 10) / 23 if f < 33 else 1.0)
        v = st.base_shear(m, sa) / 1e3
        lines.append(f"  {name:15s}  {k:14,.0f}   {f:4.1f}   {sa:15.2f}   {v:13.1f}")
    lines += ["  equipment between about 1 and 10 Hz sits on the plateau of",
              "  the spectrum and feels 2.5 times the ground; a stiff",
              "  support above about 33 Hz moves with the ground. The",
              "  porcelain, not the steel, is usually the weak part: the",
              "  maker's qualification and the support are checked together"]
    emit("r_equipment", lines)


def roof() -> None:
    v = src.SITE["gust50_10m"]
    q = st.dynamic_pressure(v * (6 / 10) ** 0.14, src.SITE["rho"])
    lines = ["wind uplift on the control building roof (12 x 24 m, 6 m high)",
             f"  gust at roof height {v * (6 / 10) ** 0.14:.1f} m/s -> pressure {q:,.0f} Pa",
             "  roof zone      cp,e   internal   net kPa   dead kPa   uplift kPa"]
    dead = 0.6
    for zone, cpe in [("corner", -2.0), ("edge", -1.4), ("middle", -0.7)]:
        net = q * (abs(cpe) + 0.2) / 1000
        lines.append(f"  {zone:12s} {cpe:6.1f}   {'+0.2':>8s}   {net:7.2f}   {dead:8.2f}"
                     f"   {net - dead:10.2f}")
    lines += ["  the dead load nearly balances the middle of the roof;",
              "  the corners lift twice the roof's weight - their fixings,",
              "  purlins and the holding-down of the columns are designed",
              "  for it; most roof failures in storms start at a corner"]
    emit("r_roof", lines)


if __name__ == "__main__":
    weight_span()
    legs()
    equipment()
    roof()
