"""Chapter 32, lesson M: more on fire, response and people - how fast a fire
grows and when it is detected, how much water a tanker shuttle brings,
false alarms against missed fires when detectors vote, construction
noise at the village, first aiders and drinking water for the
workforce, and walking distances to the muster points across the array.

Run from the project root:   python -m companion.ch32.examples_m
Writes companion/ch32/expected/m_*.txt and diagrams/data/ch32-growth.csv.
Teaching values (A-369 to A-375); the fire strategy, the fire service,
the occupational physician and local law set the real ones.
"""
from __future__ import annotations

import math

from companion.ch32 import sources as src
from companion.ch32.common import csv, emit


def growth() -> None:
    alphas = [("slow", 0.00293), ("medium", 0.01172), ("fast", 0.0469), ("ultra-fast", 0.1876)]
    rows = []
    for t in range(0, 601, 15):
        rows.append((t, *[round(a * t * t, 1) for _, a in alphas]))
    csv("ch32-growth.csv", "t,slow,medium,fast,ultra", rows)
    lines = ["fire growth Q = alpha t^2 (teaching growth classes)",
             "  class        alpha kW/s2   100 kW at   1 MW at   5 MW at"]
    for name, a in alphas:
        lines.append(f"  {name:11s}  {a:11.4f}   {math.sqrt(100 / a):7.0f} s   "
                     f"{math.sqrt(1000 / a):5.0f} s   {math.sqrt(5000 / a):5.0f} s")
    lines += ["  a fast cable or panel fire reaches 1 MW in about 2.5",
              "  minutes: detection that responds near 100 kW (under a",
              "  minute) leaves time to alarm, isolate and leave; detection",
              "  that waits for 1 MW leaves almost none - which is why the",
              "  building uses aspirating detection (lesson C)"]
    emit("m_growth", lines)


def tankers() -> None:
    cap, fill_min, unload_min = 10.0, 10.0, 8.0         # m3, minutes (placeholders)
    lines = ["water a tanker shuttle delivers (placeholders, A-370)",
             "  source distance km   round trip min   L/min per tanker   tankers for 1,500"]
    for km in (2, 10, 35):
        trip = 2 * km / 40 * 60 + fill_min + unload_min
        rate = cap * 1000 / trip
        lines.append(f"  {km:18d}   {trip:14.0f}   {rate:16.0f}   {math.ceil(1500 / rate):16d}")
    lines += ["  from the town 35 km away one tanker delivers about 80 L/min",
              "  - a shuttle needs many tankers or a nearer source: the",
              "  site tank (refilled by tankers between events) and an",
              "  agreed filling point at the wells are what make a long",
              "  exposure-cooling case possible at all"]
    emit("m_tankers", lines)


def voting() -> None:
    n, fa, lam, t = 40, 0.05, 0.02, 0.5                # detectors, false alarms/yr, failures/yr, years
    one_out = n * fa
    two_out = n * (n - 1) * fa * fa * (1 / 365 / 24) * 2      # coincident within an hour (teaching)
    pfd1 = lam * t / 2
    pfd2 = 2 * pfd1                                     # need two of two in the fire zone
    lines = ["voting: false alarms against missed fires (teaching rates)",
             f"  {n} detectors, each {fa} false alarms a year; failure rate {lam} a year",
             "  logic                  unwanted actions a year   PFD in the fire zone",
             f"  any one detector acts  {one_out:23.2f}   {pfd1:20.4f}",
             f"  two must agree         {two_out:23.5f}   {pfd2:20.4f}",
             "  voting cuts unwanted trips from about two a year to almost",
             "  none, and doubles the chance of missing a real fire - so",
             "  a single detector may raise the ALARM while the trip of a",
             "  container or a building waits for a second: the cause-",
             "  and-effect matrix states which (lesson C)"]
    emit("m_voting", lines)


def village_noise() -> None:
    sources = [("pile driver for PV posts", 115, "day"), ("concrete batching", 105, "day"),
               ("night concrete pour (pumps)", 100, "night"), ("trucks on the haul road", 95, "day")]
    lines = ["construction noise at the village 1.2 km away (point source, teaching)",
             "  Lp = Lw - 20 log10(r) - 11 (free field, no screening)",
             "  source                          Lw dB(A)   at 1.2 km   period"]
    for name, lw, period in sources:
        lp = lw - 20 * math.log10(1200) - 11
        lines.append(f"  {name:32s} {lw:8d}   {lp:9.0f}   {period}")
    lines += ["  the pile driver is heard in the village by day; a night",
              "  pour reaches about 27 dB(A), audible in a quiet desert",
              "  night - the limits come from the permit (ch 33), and",
              "  night work near the village is agreed and announced"]
    emit("m_noise", lines)


def welfare_numbers() -> None:
    w = src.WORKFORCE
    peak = w["peak"]
    lines = ["first aid and drinking water for the peak workforce (teaching ratios)",
             f"  peak workforce {peak}, two shifts, five work fronts",
             f"  first aiders at 1 per 25 on each front: {math.ceil(peak / 25)}"
             " (plus one per remote crew)",
             f"  drinking water at 5 L a person on a hot day: {peak * 5 / 1000:.2f} m3",
             f"  at 8 L for heavy work in summer: {peak * 8 / 1000:.2f} m3",
             "  shade and cool water at every front, not only at the",
             "  welfare cabins: the walk to water is a heat risk itself;",
             "  the ratios come from local law and the site's medical",
             "  provider, and a nurse on site at peak is a common choice"]
    emit("m_welfare", lines)


def muster() -> None:
    lines = ["walking to a muster point across the PV array (teaching)",
             "  block size km   muster points   farthest walk m   minutes at 4 km/h"]
    for size, points in [(1.5, 1), (1.5, 2), (1.5, 4)]:
        a = size if points == 1 else size / 2          # cell sides, km
        b = size if points < 4 else size / 2
        far = 0.5 * math.hypot(a, b) * 1000           # cell centre to corner
        lines.append(f"  {size:13.1f}   {points:13d}   {far:15.0f}   {far / 4000 * 60:17.0f}")
    lines += ["  one muster point for a 1.5 km block means a quarter-hour",
              "  walk in the heat or smoke; four points halve it to about",
              "  eight minutes, and each crew knows its own point and the",
              "  second one upwind (lesson C)"]
    emit("m_muster", lines)


if __name__ == "__main__":
    growth()
    tankers()
    voting()
    village_noise()
    welfare_numbers()
    muster()
