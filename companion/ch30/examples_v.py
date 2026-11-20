"""Chapter 30, lesson V: five checks from the site - measuring bolt preload
by ultrasonic elongation, temperature and anchor preload, choosing a PV
post foundation, a concrete-cover survey, and a tower section lifted
horizontally.

Run from the project root:   python -m companion.ch30.examples_v
Writes companion/ch30/expected/v_*.txt.
Teaching values (A-360, A-362).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch30 import sources as src
from companion.ch30.common import emit


def ultrasonic() -> None:
    e, a_s, grip = src.STEEL["e"], 1473e-6, 0.40           # M48, 400 mm effective length
    lines = ["bolt preload from ultrasonic elongation (M48, teaching)",
             "  dL = F L / (E As); instrument resolution 0.01 mm",
             "  preload kN   elongation mm"]
    for f in (500, 773, 928, 1031):
        lines.append(f"  {f:10d}   {f * 1e3 * grip / (e * a_s) * 1000:13.3f}")
    res = 0.01e-3 * e * a_s / grip / 1e3
    lines += [f"  0.01 mm of elongation is about {res:.0f} kN of preload: the",
              "  instrument reads the bolt's own stretch, not the friction",
              "  of the nut, so a sample measured this way checks the",
              "  torque method's scatter (lesson Q) on the real flange"]
    emit("v_ultrasonic", lines)


def anchor_temperature() -> None:
    d_alpha = 12e-6 - 10e-6
    lines = ["does temperature change the anchor preload? (steel in concrete)",
             "  temperature change K   stress change MPa   on a 1,250 kN M64 (As 2,676 mm2)"]
    for dt in (10, 20, 40):
        s = src.STEEL["e"] * d_alpha * dt / 1e6
        lines.append(f"  {dt:20d}   {s:17.1f}   {s * 2676 / 1000:10.0f} kN")
    lines += ["  a few per cent of the preload: the steel and the concrete",
              "  expand almost alike, so the season barely matters - the",
              "  losses that matter are grout creep and settling in the",
              "  first months, which the re-tensioning removes (lesson C)"]
    emit("v_anchortemp", lines)


def post_options() -> None:
    rows = [("driven C-post", 1.0, "dense sand, no rock", "pull-out, lateral"),
            ("ground screw", 1.4, "loose top layer, gravel", "torque record, test"),
            ("pre-drilled + grout", 2.2, "rock or cobbles", "grout cubes, test"),
            ("concrete footing", 3.0, "gypsum, saline zone", "concrete records")]
    lines = ["foundation options for PV posts (relative cost per post, teaching)",
             "  option                 cost   where it suits             evidence"]
    for name, c, where, ev in rows:
        lines.append(f"  {name:21s}  {c:4.1f}   {where:25s}  {ev}")
    lines += ["  the cheapest option is not cheap where it fails a test:",
              "  a site with three ground zones (ch 29) may use three",
              "  options, chosen block by block from the test programme -",
              "  and the posts' refusal depths are recorded as built"]
    emit("v_posts", lines)


def cover(seed: int = 30) -> None:
    rng = np.random.default_rng(seed)
    nominal, minimum = 75.0, 65.0
    readings = rng.normal(71.0, 5.5, 60)
    below = int((readings < minimum).sum())
    p5 = readings.mean() - 1.645 * readings.std(ddof=1)
    lines = ["cover-meter survey of one foundation (60 readings, synthetic)",
             f"  nominal cover {nominal:.0f} mm, minimum {minimum:.0f} mm (teaching)",
             f"  mean {readings.mean():.1f} mm, standard deviation {readings.std(ddof=1):.1f} mm",
             f"  readings below the minimum: {below} of 60; 5 % fractile {p5:.1f} mm",
             "  the mean looks fine; the fractile and the low readings",
             "  do not - where they cluster (one face, one pour) decides",
             "  between a local repair (coating, added cover) and an",
             "  assessment of durability (lesson B)"]
    emit("v_cover", lines)


def lifted_section() -> None:
    d, t, length, mass = 4.12, 0.040, 25.0, 96e3             # section 2 (ch 31)
    w = mass * 9.81 / length
    i = math.pi / 64 * (d ** 4 - (d - 2 * t) ** 4)
    z = i / (d / 2)
    lines = ["a tower section lifted horizontally at its two ends (section 2)",
             f"  {mass / 1e3:.0f} t over {length:.0f} m; tube {d} m x {t * 1000:.0f} mm"]
    for name, span, factor in [("lugs at the ends", length, 1 / 8),
                               ("lugs at quarter points", length / 2, 1 / 8)]:
        m = w * span ** 2 * factor * (1.0 if span == length else 1.0)
        lines.append(f"  {name:24s} moment {m / 1e3:6.0f} kN m, stress {m / z / 1e6:5.1f} MPa")
    lines += ["  bending is trivial for a 4 m tube; what the lift does",
              "  threaten is the shape - the thin end ovalises under its",
              "  own weight at the lugs, which is why the sections travel",
              "  and lift with their flanges braced (lesson C, ch 31)"]
    emit("v_lift", lines)


if __name__ == "__main__":
    ultrasonic()
    anchor_temperature()
    post_options()
    cover()
    lifted_section()
