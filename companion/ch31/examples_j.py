"""Chapter 31, lesson J: storage and timing - the ground under a blade
cradle, holding stored blades down in a storm, the chance a late
delivery leaves the crane idle, the strip needed to assemble the main
crane's boom, and the hours of preservation work while parts wait.

Run from the project root:   python -m companion.ch31.examples_j
Writes companion/ch31/expected/j_*.txt and diagrams/data/ch31-slip.csv.
Teaching values (A-365, A-366); the makers' storage instructions and
the crane supplier's assembly plan govern.
"""
from __future__ import annotations

import numpy as np

from companion.ch31 import sources as src  # noqa: F401  (puts plantp on the path)
from companion.ch31.common import csv, emit

G = 9.81


def cradles() -> None:
    blade_t = 22.0
    lines = ["the ground under a blade's storage cradles (teaching)",
             f"  blade {blade_t:.0f} t + cradles 3 t on two cradles; root cradle carries 65 %",
             "  cradle feet   foot area m2   pressure kPa   gravel pad needed?"]
    root_kn = (blade_t + 3.0) * G * 0.65
    for feet, area in [(2, 0.25), (4, 0.25), (4, 1.0)]:
        p = root_kn / (feet * area)
        lines.append(f"  {feet:11d}   {area:12.2f}   {p:12.0f}   {'yes' if p > 150 else 'no'}")
    lines += ["  small feet on the loose top layer (ch 29) sink unevenly",
              "  and twist the blade - the maker's cradle positions and a",
              "  compacted, level laydown pad keep the shell in shape"]
    emit("j_cradles", lines)


def tie_down() -> None:
    area = 74.0 * 3.0 * 0.5                         # blade plan area (m2), shape factor
    lines = ["holding a stored blade down in a storm (teaching lift coefficient 1.0)",
             f"  plan area {area:.0f} m2; blade and cradles 25 t",
             "  gust m/s   lift kN   weight kN   net uplift kN"]
    for v in (20, 30, 41):
        lift = 0.5 * 1.09 * v * v * 1.0 * area / 1000
        w = 25.0 * G
        lines.append(f"  {v:8d}   {lift:7.0f}   {w:9.0f}   {max(0.0, lift - w):13.0f}")
    lines += ["  even the 41 m/s gust lifts less than the weight here - but",
              "  the light tip end carries little of that weight, gusts",
              "  push the blade sideways and turn it on its cradles: the",
              "  maker's storage instruction asks for straps to ground",
              "  anchors and a set direction to the prevailing wind"]
    emit("j_tiedown", lines)


def delivery_slip(n: int = 20_000, seed: int = 31) -> None:
    rng = np.random.default_rng(seed)
    ship = rng.normal(0, 4, n)                       # days early/late at the port
    permit = rng.exponential(1.5, n)                 # days lost to permits and escorts
    road = rng.choice([0, 0, 0, 0, 1, 2], n)          # nights lost to weather or traffic
    buffer = 7.0
    late = ship + permit + road
    idle = np.maximum(0.0, late - buffer)
    hist, edges = np.histogram(late, bins=30, range=(-10, 20))
    csv("ch31-slip.csv", "day,count", [(round(e, 1), int(h)) for e, h in zip(edges[:-1], hist)])
    lines = ["will the nacelle be at the pad when the crane is? (Monte Carlo)",
             "  ship +/- 4 days, permit delay mean 1.5 days, road 0-2 nights",
             f"  planned buffer between delivery and lift: {buffer:.0f} days",
             f"  share of nacelles later than the buffer: {np.mean(late > buffer) * 100:.1f} %",
             f"  expected crane idle days per nacelle: {idle.mean():.2f}"
             f" (at 29 k u a day: {idle.mean() * 29:.1f} k u)",
             "  with a 3-day buffer instead:"
             f" {np.mean(late > 3) * 100:.0f} % late, {np.maximum(0, late - 3).mean() * 29:.1f} k u",
             "  a week of buffer costs laydown space and preservation; a",
             "  short buffer costs crane days - the plan sets it from",
             "  these two costs, and the buffer is the cheaper one here"]
    emit("j_slip", lines)


def boom_strip() -> None:
    boom = 140.0
    lines = ["assembling the main crane's boom (teaching configuration)",
             f"  main boom and luffing jib laid out: about {boom:.0f} m long",
             "  assembly strip needed: boom length + 20 m, 12 m wide",
             f"  area {(boom + 20) * 12:,.0f} m2, flat within 1 %, cleared of obstacles",
             "  assist crane for the boom sections: 100 t class",
             "  days to assemble 4, to dismantle 3 (included in the moves)",
             "  the strip is part of the first pad's layout and the last",
             "  pad's too: where the land, the slope or a cable route does",
             "  not allow it, the crane cannot be built there"]
    emit("j_boom", lines)


def preservation() -> None:
    tasks = [("rotate drivetrain (maker's interval 4 weeks)", 2.0, 4),
             ("check desiccant and humidity cards", 0.5, 2),
             ("check heaters and power", 0.5, 1),
             ("inspect covers and seals after wind", 1.0, 2),
             ("log and photograph", 0.5, 4)]
    lines = ["preservation work while 4 nacelles wait 8 weeks (teaching)",
             "  task                                          h each   every weeks"]
    total = 0.0
    for name, h, every in tasks:
        n = 8 // every
        total += 4 * n * h
        lines.append(f"  {name:46s} {h:5.1f}   {every:5d}")
    lines += [f"  total about {total:.0f} person-hours for the waiting period",
              "  a missed rotation can mark the bearings (false brinelling)",
              "  and void the warranty: the preservation log is evidence,",
              "  kept with the custody record (lesson C)"]
    emit("j_preserve", lines)


if __name__ == "__main__":
    cradles()
    tie_down()
    delivery_slip()
    boom_strip()
    preservation()
