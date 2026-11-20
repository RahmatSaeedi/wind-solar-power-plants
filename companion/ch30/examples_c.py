"""Chapter 30, lesson C: PV structures and their materials - post loads
from wind uplift, pile embedment by skin friction and the pull-out test
programme that proves it, lateral capacity of a short post in sand, zinc
life in the site's soils, the purlin chosen by strength and deflection,
and a slip-resistant bolted joint.

Run from the project root:   python -m companion.ch30.examples_c
Writes companion/ch30/expected/c_*.txt. Teaching values (A-360, A-362).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch30 import sources as src
from companion.ch30.common import emit
from plantp import civil as cv
from plantp import structures as st

PERIM = 0.55            # m, C-section post 150 x 65 mm, wetted perimeter
EDGE = 1.5              # edge posts carry 1.5 x the average (teaching)


def post_loads() -> dict:
    p = src.PV_TABLE
    area = p["rows"] * p["module_l"] * p["modules_per_row"] * p["module_w"]
    q = st.dynamic_pressure(src.SITE["gust50_10m"] * (2.0 / 10) ** 0.11, src.SITE["rho"])
    normal = q * 1.2 * area / 1e3                         # kN, normal to the plane
    tilt = math.radians(p["tilt_deg"])
    dead = p["rows"] * p["modules_per_row"] * p["module_kn"] + p["steel_kn"]
    n = p["frames"] * p["posts_per_frame"]
    up = (normal * math.cos(tilt) - dead) / n * EDGE
    side = normal * math.sin(tilt) / n * EDGE
    return dict(up=up, side=side, n=n)


def embedment() -> None:
    ld = post_loads()
    lines = ["post loads (edge post, teaching) and embedment by skin friction",
             f"  uplift {ld['up']:.1f} kN, horizontal {ld['side']:.1f} kN per edge post"
             f" ({ld['n']} posts a table)",
             "  soil (ch 29)                  skin kPa   embedment for FS 2 m"]
    for name, f in (("dense sand and gravel", 25.0), ("silty sand, loose (top)", 12.0),
                    ("silty sand with gypsum", 10.0)):
        length = 2 * ld["up"] / (PERIM * f)
        lines.append(f"  {name:28s} {f:9.0f}   {length:20.2f}")
    lines += ["  the loose top layer more than doubles the embedment; skin",
              "  friction is the least certain number in the table, so it",
              "  is measured, not assumed: pull-out tests on site (below)"]
    emit("c_embedment", lines)


def pullout() -> None:
    ld = post_loads()
    need = 2 * ld["up"]
    rng = np.random.default_rng(300)
    zones = {"PV north (BH-09)": 26 + 5 * rng.standard_normal(10),
             "PV south (BH-10)": 19 + 6 * rng.standard_normal(10)}
    lines = [f"pull-out tests on posts driven 1.6 m (required 2 x design = {need:.1f} kN)",
             "  zone                 mean kN   s     5 % fractile   below required"]
    for name, x in zones.items():
        fr = cv.characteristic(x)
        lines.append(f"  {name:20s} {x.mean():7.1f}  {x.std(ddof=1):4.1f}   {fr:12.1f}"
                     f"   {int((x < need).sum()):3d} of 10")
    lines += ["  in pull-out north passes at 1.6 m; south, on looser silty",
              "  sand, does not: deeper posts there (or a test at 2.2 m) - the",
              "  embedment is set zone by zone from the test results,",
              "  and the test procedure and load are in the specification"]
    emit("c_pullout", lines)


def lateral() -> None:
    ld = post_loads()
    lines = ["lateral capacity of a short post in sand (Broms, free head)",
             "  d 0.15 m, load 1.2 m above ground, gamma 18 kN/m3",
             "  embedment m   phi 30 (Kp 3.0)   phi 34 (Kp 3.5)   load x 2"]
    for length in (1.2, 1.6, 2.0):
        h30 = st.broms_lateral_sand(0.15, length, 18.0, 3.0, 1.2)
        h34 = st.broms_lateral_sand(0.15, length, 18.0, 3.5, 1.2)
        lines.append(f"  {length:11.1f}   {h30:15.1f}   {h34:15.1f}   {2 * ld['side']:8.1f}")
    lines += ["  capacity grows with the cube of embedment; at 1.6 m the",
              "  post fails sideways long before it pulls out - in dense",
              "  sand the side load, not the uplift, sets the depth (about",
              "  2 m): the test programme pairs pull-out with lateral tests"]
    emit("c_lateral", lines)


def zinc() -> None:
    lines = ["galvanized posts in the site's soils (zinc 85 um; teaching rates)",
             "  soil                          um/yr   zinc life yr   30-yr plant?"]
    for name, rate in (("dense sand, dry (most)", 1.0), ("silty sand, moist", 3.0),
                       ("gypsum, saline (BH-07 area)", 8.0)):
        life = st.zinc_life(85.0, rate)
        lines.append(f"  {name:29s} {rate:5.1f}   {life:12.0f}   {'yes' if life >= 30 else 'NO'}")
    lines += ["  where the soil is aggressive the zinc is gone in about",
              "  ten years: a thicker coating, a sacrificial steel",
              "  allowance or a concrete footing there - the corrosivity",
              "  tests of ch 29 (missing in most boreholes) decide where"]
    emit("c_zinc", lines)


def purlin() -> None:
    p = src.PV_TABLE
    q = st.dynamic_pressure(src.SITE["gust50_10m"] * (2.0 / 10) ** 0.11, src.SITE["rho"])
    span = p["modules_per_row"] * p["module_w"] / (p["frames"] - 1)
    width = p["rows"] * p["module_l"] / 4                       # four purlins a table
    w = q * 1.2 * width                                         # N/m
    m = w * span ** 2 / 8
    sections = [("C100x50x2.0", 9.0, 45.0), ("C120x50x2.5", 14.0, 84.0),
                ("C150x50x2.5", 19.0, 142.0), ("C200x60x2.5", 32.0, 320.0)]
    lines = [f"purlin over {span:.2f} m between frames, {w:.0f} N/m (teaching sections)",
             f"  moment {m / 1e3:.2f} kN m; strength limit fy/1.1; deflection limit L/200",
             "  section        W cm3   I cm4   stress MPa   deflection mm   result"]
    for name, wz, iz in sections:
        sig = m / (wz * 1e-6) / 1e6
        dfl = 5 * w * span ** 4 / (384 * src.STEEL["e"] * iz * 1e-8) * 1000
        ok = sig <= 355 / 1.1 and dfl <= span * 1000 / 200
        lines.append(f"  {name:13s}  {wz:5.1f}  {iz:6.0f}   {sig:10.0f}   {dfl:13.1f}   {'ok' if ok else '-'}")
    lines += ["  the 120 section is strong enough but bends too much; the",
              "  stiffness limit, not the strength, picks the 200 section -",
              "  deflection matters because a bending rail stresses the",
              "  glass and the clamps (the module maker's mounting rules)"]
    emit("c_purlin", lines)


def bolts() -> None:
    shear = 40.0                                                # kN on a frame splice
    preload, mu = 80.0, 0.3                                     # kN, teaching
    lines = ["a frame splice that must not slip (teaching preload and friction)",
             f"  shear {shear:.0f} kN; preload {preload:.0f} kN a bolt; friction {mu} per surface"]
    for n, surf in ((2, 1), (2, 2), (4, 1)):
        cap = st.bolt_slip(n, mu, preload, surf)
        lines.append(f"  {n} bolts, {surf} surface(s): {cap:5.0f} kN  {'ok' if cap >= shear else 'slips'}")
    lines += ["  a slip-resistant joint relies on the preload: the bolts",
              "  are tightened by a controlled method and the faying",
              "  surfaces are prepared as specified - paint or galvanizing",
              "  there lowers the friction the calculation assumed"]
    emit("c_bolts", lines)


if __name__ == "__main__":
    embedment()
    pullout()
    lateral()
    zinc()
    purlin()
    bolts()
