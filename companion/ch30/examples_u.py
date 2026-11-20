"""Chapter 30, lesson U: six smaller structural checks - the force in a PV
rail that cannot expand, buoyancy on T07's base under high water, twist
of a PV table on uneven posts, aeolian vibration of the conductors,
swing of a suspension insulator in wind, and the wall of a transformer
bund.

Run from the project root:   python -m companion.ch30.examples_u
Writes companion/ch30/expected/u_*.txt and diagrams/data/ch30-swing.csv.
Teaching values (A-357, A-360, A-361); the designers' calculations and
the codes govern.
"""
from __future__ import annotations

import math

from companion.ch30 import sources as src
from companion.ch30.common import csv, emit
from plantp import structures as st


def rail_force() -> None:
    a_rail = 600e-6                                  # m2, C-rail (teaching)
    dt = 65.7 - (-8.6)                               # lesson A's steel range
    f_full = src.STEEL["e"] * a_rail * src.STEEL["alpha"] * dt / 1e3
    lines = ["force in a 29.5 m PV rail if it cannot expand (teaching)",
             f"  rail area {a_rail * 1e6:.0f} mm2; steel range {dt:.1f} K",
             f"  fully restrained: E A alpha dT = {f_full:,.0f} kN",
             "  restraint left   force kN   against a post's side load 5.5 kN"]
    for r in (1.0, 0.25, 0.05):
        lines.append(f"  {r * 100:13.0f} %   {f_full * r:8.0f}   {f_full * r / 5.5:5.0f} x")
    lines += ["  even 5 % of the restraint loads the end posts as much as",
              "  the storm does: slotted holes or a joint every table",
              "  let the rail move - the 26 mm of lesson A must be free"]
    emit("u_rail", lines)


def buoyancy() -> None:
    f = src.FOUNDATION
    area = math.pi * f["r"] ** 2
    v_dry = (f["concrete_m3"] * f["gamma_c"] + f["backfill_m3"] * f["gamma_b"]
             + (src.TOP_T + src.TOWER_T) * 9.81) / 1000
    m = src.LOADS["extreme (parked, 50-yr gust)"]["m_mnm"]
    lines = ["buoyancy on the 20 m base when the water rises (T07, teaching)",
             f"  base area {area:.0f} m2, founded at {f['depth']:.1f} m; dry weight {v_dry:.1f} MN",
             "  water below ground m   uplift MN   weight MN   e = M/V m   e / R"]
    for w in (3.5, 2.0, 0.5):
        h = max(0.0, f["depth"] - w)
        up = area * h * 9.81 / 1000
        v = v_dry - up
        e = m / v
        lines.append(f"  {w:20.1f}   {up:9.1f}   {v:9.1f}   {e:9.2f}   {e / f['r']:5.2f}")
    lines += ["  water at 0.5 m lifts about a quarter of the weight: the",
              "  eccentricity of the extreme load grows by a third and the",
              "  base lifts further off its edge - the 'ok except wet' of",
              "  lesson D's scheme S2 comes from exactly this number"]
    emit("u_buoyancy", lines)


def pv_twist() -> None:
    span, width = 29.5, 4.6                          # table length and depth (m)
    lines = ["twist of a PV table when one post settles (teaching)",
             "  post settles mm   twist mrad   module corner out of plane mm"]
    for s in (5, 10, 20, 40):
        twist = s / 1000 / (span / 5)                  # over one bay of 5.9 m
        corner = twist * 2.278 * 1000
        lines.append(f"  {s:15d}   {twist * 1000:10.2f}   {corner:30.1f}")
    lines += ["  a module tolerates only a few millimetres of twist before",
              "  the glass and frame are stressed; posts in the loose top",
              "  layer (ch 29) that settle or heave 20 mm warp the table -",
              "  driving to the tested depth and a survey of post heads",
              "  after a wet season catch it"]
    emit("u_twist", lines)


def aeolian() -> None:
    d = 0.024
    lines = ["aeolian vibration of a 24 mm conductor (Strouhal 0.2)",
             "  wind m/s   shedding frequency Hz"]
    for v in (1, 3, 5, 7):
        lines.append(f"  {v:8d}   {0.2 * v / d:20.0f}")
    lines += ["  steady light winds across a flat desert drive the wire at",
              "  tens of hertz for millions of cycles a year; the strands",
              "  fatigue at the clamps. Dampers near each clamp, tension",
              "  limits for the everyday case and the line designer's",
              "  span-by-span check are the remedy (ch 24)"]
    emit("u_aeolian", lines)


def swing() -> None:
    wind_kn = 7.7                                     # lesson F, one phase, 300 m wind span
    ins_kn = 0.6
    rows = []
    lines = ["swing of a suspension insulator in the design wind (teaching)",
             "  weight span m   vertical kN   swing angle deg"]
    for ws in (300, 200, 100, 50):
        v = ws * 11.8 / 1000 + ins_kn / 2
        ang = math.degrees(math.atan(wind_kn / v))
        rows.append((ws, round(ang, 1)))
        lines.append(f"  {ws:13d}   {v:11.2f}   {ang:15.0f}")
    csv("ch30-swing.csv", "ws,angle", rows)
    lines += ["  the wires blow out far in a storm, and further where the",
              "  weight span is short (a tower in a hollow): the air gap to",
              "  the tower body is checked at the swing angle of each",
              "  tower, which is why the hollow tower of the weight-span",
              "  lesson is a double problem"]
    emit("u_swing", lines)


def bund_wall() -> None:
    lines = ["the wall of a transformer bund full of oil and water (teaching)",
             "  height m   base moment kN m per m   wall t mm (rebar check)"]
    for h in (0.6, 1.0, 1.5):
        p_base = 10.0 * h                                # kPa, water density for safety
        m = 10.0 * h ** 3 / 6
        as_req = st.rebar_area(m * 1e3 * 1.5, 0.15, 435e6) * 1e6
        lines.append(f"  {h:8.1f}   {m:22.2f}   {200:10d} (As {as_req:4.0f} mm2/m)")
    lines += ["  the hydrostatic load is small; the wall is sized by",
              "  crack control and watertightness, not strength - a bund",
              "  that leaks fails its only job (ch 29 sets its volume)"]
    emit("u_bund", lines)


if __name__ == "__main__":
    rail_force()
    buoyancy()
    pv_twist()
    aeolian()
    swing()
    bund_wall()
