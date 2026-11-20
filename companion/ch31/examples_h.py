"""Chapter 31, lesson H: lifting in more detail - sling angles, single-
blade lifts against the rotor-star lift in the data-pack year, the time
to bolt a tower flange against the vortex risk, cable pulling with the
capstan equation, the bend radius a drum must keep, and skidding the
transformer onto its plinth.

Run from the project root:   python -m companion.ch31.examples_h
Writes companion/ch31/expected/h_*.txt and diagrams/data/ch31-slings.csv.
Teaching values (A-365 to A-367); lift plans, the cable maker's limits
and the heavy-haul contractor's method govern.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch31 import sources as src  # noqa: F401  (puts plantp on the path)
from companion.ch31.common import csv, emit
from plantp import datapack

G = 9.81


def slings() -> None:
    w = 168.0 * G                                     # nacelle + rigging, kN
    rows = []
    lines = ["tension in each leg of a two-leg sling (168 t, teaching)",
             "  angle between legs deg   tension per leg kN   factor"]
    for ang in (0, 30, 60, 90, 120):
        t = w / (2 * math.cos(math.radians(ang / 2)))
        rows.append((ang, round(t, 0)))
        lines.append(f"  {ang:22d}   {t:18,.0f}   {t / (w / 2):6.2f}")
    csv("ch31-slings.csv", "angle,tension", rows)
    lines += ["  at 120 degrees each leg carries the whole load: wide",
              "  angles also squeeze the load - which is why nacelles lift",
              "  on a spreader beam or the maker's lifting yoke, never on",
              "  slings chosen on site"]
    emit("h_slings", lines)


def blade_windows() -> None:
    d = datapack.load_hourly()
    v = d["ws_100m_ms"].to_numpy()

    def windows(limit, hours):
        ok = v < limit
        n, run = 0, 0
        for x in ok:
            run = run + 1 if x else 0
            if run == hours:
                n += 1
                run = 0
        return n

    star = windows(8.0, 8)
    single = windows(10.0, 4)
    lines = ["rotor-star lift or three single-blade lifts? (data-pack year)",
             "  method              window needed           windows a year   lifts each",
             f"  rotor star          8 h below 8 m/s         {star:14d}   1",
             f"  single blade        4 h below 10 m/s        {single:14d}   3",
             "  single-blade lifts need shorter, windier windows, and so",
             "  find many more of them; they avoid the ground assembly of",
             "  the rotor but need the maker's blade yoke and three",
             "  lifts - which one the maker's method allows comes first"]
    emit("h_blades", lines)


def bolting_time() -> None:
    bolts = 120
    lines = ["time to tension a tower flange (teaching rates)",
             "  tools   min a bolt (2 passes)   hours a flange"]
    for tools in (1, 2, 4):
        t = bolts * 2 * 3.0 / tools / 60
        lines.append(f"  {tools:5d}   {6.0:20.0f}   {t:14.1f}")
    lines += ["  with one tool a flange takes about 12 hours: the top",
              "  section, its bolting and the nacelle in one day need",
              "  four tools and a crew for each - or the bare tower stands",
              "  overnight in the vortex wind (ch 30), within the maker's",
              "  procedure and its wind limit"]
    emit("h_bolting", lines)


def pulling() -> None:
    t_max = 40.0 * 400                                # N: 40 N/mm2 on a 400 mm2 Al conductor... x3 cores
    t_max *= 3
    lines = ["pulling a 33 kV cable through a duct run (capstan equation)",
             "  T_out = T_in exp(mu theta) at each bend; friction mu 0.35 (teaching)",
             f"  allowed pull on the conductors: {t_max / 1e3:.0f} kN (40 N/mm2 x 3 x 400 mm2)",
             "  route                                    pull at the end kN"]
    w = 10.0 * G * 0.35                                # N/m: 10 kg/m cable, friction on straights
    for name, straight, bends in [("300 m straight", 300, 0), ("300 m, two 90 deg bends", 300, 2),
                                  ("300 m, four 90 deg bends", 300, 4), ("500 m, four bends", 500, 4)]:
        t = 0.0
        seg = straight / (bends + 1)
        for _ in range(bends):
            t = (t + w * seg) * math.exp(0.35 * math.pi / 2)
        t += w * seg
        flag = "" if t <= t_max else "  OVER"
        lines.append(f"  {name:40s} {t / 1e3:18.1f}{flag}")
    lines += ["  each 90 degree bend multiplies the pull by 1.7, so bends",
              "  and length together end a pull - the duct route is drawn with",
              "  few bends, and joint bays placed where the pull would",
              "  exceed the cable maker's limit"]
    emit("h_pulling", lines)


def drum_radius() -> None:
    d_cable = 0.075
    lines = ["the bend radius a 33 kV cable must keep (teaching 15 x D)",
             f"  cable {d_cable * 1000:.0f} mm -> minimum bend radius {15 * d_cable:.2f} m"
             " (12 x D once laid)",
             "  drum barrel m   radius m   ok?"]
    for barrel in (1.6, 2.0, 2.4):
        r = barrel / 2 + d_cable / 2
        lines.append(f"  {barrel:13.1f}   {r:8.2f}   {'yes' if r >= 15 * d_cable else 'NO'}")
    lines += ["  a drum too small for the cable damages the insulation",
              "  before it leaves the yard; the cable maker states the",
              "  drum, the pulling limits and the bend radius - receiving",
              "  inspection checks the drum against that sheet (lesson C)"]
    emit("h_drum", lines)


def skid() -> None:
    mass = 72.0
    lines = ["skidding the main transformer onto its plinth (72 t, oil out)",
             "  skid surface             friction   pull kN"]
    for name, mu in [("greased steel on steel", 0.10), ("PTFE pads", 0.05),
                     ("dry steel on steel", 0.25)]:
        lines.append(f"  {name:24s} {mu:8.2f}   {mu * mass * G:7.0f}")
    lines += ["  jacks lift it on its jacking points, skid beams carry it",
              "  over, and a pull of a few tens of kN moves it - slowly,",
              "  with a restraint on the other side; the maker's",
              "  drawings fix the jacking and lashing points and the",
              "  impact recorder is read before and after (lesson C)"]
    emit("h_skid", lines)


if __name__ == "__main__":
    slings()
    blade_windows()
    bolting_time()
    pulling()
    drum_radius()
    skid()
