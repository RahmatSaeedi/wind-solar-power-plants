"""Chapter 31, lesson G: the road in more detail - the sweep of a blade tip
in a bend, the pull needed on a grade, a blade in a crosswind on its
trailer, lashing the nacelle, and how many convoys a night window lets
through in a week.

Run from the project root:   python -m companion.ch31.examples_g
Writes companion/ch31/expected/g_*.txt and diagrams/data/ch31-sweep.csv.
Teaching values (A-363, A-364); the transport contractor's swept-path
study, the trailer maker's data and the road authority govern.
"""
from __future__ import annotations

import math

from companion.ch31 import sources as src  # noqa: F401  (puts plantp on the path)
from companion.ch31.common import csv, emit

G = 9.81


def sweep() -> None:
    overhang = 22.0                                   # blade beyond the rear bogie (m)
    rows = []
    lines = ["sweep of the blade tip outside the rear bogie's path in a bend",
             f"  rear overhang {overhang:.0f} m (74 m blade on an extendable trailer)",
             "  bend radius m   tip radius m   extra sweep m"]
    for r in (25, 40, 60, 90, 150):
        tip = math.hypot(r, overhang)
        rows.append((r, round(tip - r, 2)))
        lines.append(f"  {r:13d}   {tip:12.1f}   {tip - r:13.1f}")
    csv("ch31-sweep.csv", "r,extra", rows)
    lines += ["  in a tight bend the tip swings several metres outside the",
              "  road: signs, poles, walls and trees in that zone are",
              "  removed or the blade is lifted on a tilting adaptor - the",
              "  swept-path study of each bend comes before the permit"]
    emit("g_sweep", lines)


def grade() -> None:
    gross_t = 160 + 42 + 30                           # nacelle + trailer + tractor
    rolling = 0.02
    lines = ["pull needed to climb with the nacelle (gross 232 t, teaching)",
             "  grade %   pull kN   tractors at 300 kN (incl. a pusher)"]
    for g_pct in (0, 4, 8, 12):
        theta = math.atan(g_pct / 100)
        pull = gross_t * 1000 * G * (math.sin(theta) + rolling * math.cos(theta)) / 1000
        lines.append(f"  {g_pct:7d}   {pull:7.0f}   {math.ceil(pull / 300):9d}")
    lines += ["  each 4 % of grade adds about 90 kN - a third of a tractor;",
              "  at 12 % a pusher unit is needed: the steep stretches of",
              "  ch 29's roads get a pusher, gravel for grip, or a",
              "  gentler alignment - and wet",
              "  gravel halves the grip a driven axle can use"]
    emit("g_grade", lines)


def crosswind() -> None:
    area = 74.0 * 3.0 * 0.6                           # blade side area (m2), shape factor
    h_cg = 4.0
    track = 3.0
    mass = 22e3 + 30e3
    lines = ["a blade on its trailer in a crosswind (teaching)",
             f"  side area {area:.0f} m2 at {h_cg:.0f} m; blade + trailer {mass / 1e3:.0f} t; track"
             f" {track:.0f} m",
             "  gust m/s   wind force kN   tipping moment / restoring"]
    for v in (15, 20, 25, 30):
        f = 0.5 * 1.2 * v * v * 1.2 * area / 1000
        ratio = f * h_cg / (mass * G / 1000 * track / 2)
        lines.append(f"  {v:8d}   {f:13.1f}   {ratio:26.2f}")
    lines += ["  even a 30 m/s gust gives under half the restoring moment:",
              "  the load does not tip, but it sways and steers badly long",
              "  before - the convoy's wind limit is set for control, and",
              "  the plan names a place to park and wait"]
    emit("g_crosswind", lines)


def lashing() -> None:
    mass = 160e3
    lines = ["lashing the nacelle on its trailer (teaching accelerations)",
             "  design accelerations: 0.8 g forward, 0.5 g sideways, 0.5 g back",
             "  direction   force kN   friction 0.3 kN   lashings to hold (100 kN each)"]
    for name, a in [("forward", 0.8), ("sideways", 0.5), ("backward", 0.5)]:
        f = mass * G * a / 1000
        fr = 0.3 * mass * G / 1000
        need = max(0.0, f - fr)
        lines.append(f"  {name:10s}  {f:8.0f}   {fr:15.0f}   {math.ceil(need / 100 * 1.2):16d}")
    lines += ["  braking hard loads the lashings most: friction alone holds",
              "  less than half - the maker's lashing points, chain or",
              "  bolted fixtures and a check after the first kilometres",
              "  belong to the transport plan, with the accelerations of",
              "  the applicable load-securing rules"]
    emit("g_lashing", lines)


def night_capacity() -> None:
    window = 7.0                                       # h, 22:00-05:00 (teaching permit)
    trip = 9.6
    lines = ["convoys a week through a night-only permit (teaching)",
             f"  window {window:.0f} h a night; trip {trip} h -> nights per convoy:"
             f" {math.ceil(trip / window)}",
             "  parking places   convoys moving at once   convoys a week"]
    for spaces in (1, 2, 3):
        per_week = 7 * spaces / math.ceil(trip / window)
        lines.append(f"  {spaces:14d}   {spaces:22d}   {per_week:14.1f}")
    lines += ["  108 loads at 3.5 a week take about 31 weeks; three",
              "  parking places bring it near 10 a week - but only if the",
              "  escort, the road authority and the crane keep pace:",
              "  the route's capacity, not the ship, sets the campaign"]
    emit("g_capacity", lines)


if __name__ == "__main__":
    sweep()
    grade()
    crosswind()
    lashing()
    night_capacity()
