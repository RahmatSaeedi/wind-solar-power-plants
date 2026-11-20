"""Chapter 14, section B3 - a small layout optimisation: the two rows of
the plain layout with the west row shifted south by 0 .. 1,500 m (stagger)
and the whole layout turned by -20 .. +20 deg, scored by long-term energy
(wakes, 2-degree bins) and by noise at the seasonal camp; the search
stops at what the constraints allow.

Run from the project root:   python -m companion.ch14.lab_h
Writes companion/ch14/expected/h_*.txt and diagrams/data/ch14-stagger.csv.
Synthetic site A-259; D-015, D-017, D-018.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch14 import examples_b as eb, examples_g as eg, sources as src
from companion.ch14.common import csv, emit

CAMP = src.DWELLINGS["herders' camp B (seasonal)"]


def plain(shift: float) -> np.ndarray:
    west = [[3600.0, 2700.0 - shift + 600.0 * k] for k in range(6)]
    east = [[4800.0, 2700.0 + 600.0 * k] for k in range(6)]
    return np.array(west + east)


def turn(xy: np.ndarray, deg: float) -> np.ndarray:
    c = xy.mean(axis=0)
    a = math.radians(deg)
    r = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
    return (xy - c) @ r.T + c


def stagger() -> None:
    lines = ["the west row shifted south (east row fixed), long-term energy",
             "  with the teaching speed-up:",
             "  shift m   farm GWh   wake loss   camp dB(A)   lowest west turbine y"]
    rows = []
    for sh in (0, 300, 600, 900, 1200, 1500):
        xy = plain(float(sh))
        f, e = eb.farm_energy(xy, eb.speedups(xy))
        lv = eg.levels_at(xy, [CAMP])[0]
        rows.append((sh, f"{eb.LT * e:.2f}", f"{lv:.1f}"))
        lines.append(f"  {sh:6d}    {eb.LT * e:7.2f}    {100 * (1 - e / f):5.2f} %     {lv:5.1f}"
                     f"        {xy[0, 1]:6.0f} m")
    csv("ch14-stagger.csv", "shift,energy,noise", rows)
    lines += ["  staggering the rows lifts the energy (the rows stop shading each",
              "  other in the prevailing wind) and moves the west row away from",
              "  the camp; at 1,500 m the southern turbine stands 75 m from the",
              "  wadi, inside its 100 m buffer: the shift stops at 1,200 m, on a",
              "  constraint, where optima usually sit"]
    emit("h_stagger", lines)


def orientation() -> None:
    base = plain(1200.0)
    lines = ["W2b turned about its centre, long-term energy:",
             "  turn deg   farm GWh   wake loss"]
    res = {}
    for deg in (-20, -10, 0, 10, 20):
        xy = turn(base, float(deg))
        f, e = eb.farm_energy(xy, eb.speedups(xy))
        res[deg] = eb.LT * e
        lines.append(f"  {deg:+5d}      {eb.LT * e:7.2f}    {100 * (1 - e / f):5.2f} %")
    lines += [f"  -20 deg costs {res[0] - res[-20]:.1f} GWh a year; +20 deg gains"
              f" {res[20] - res[0]:.1f} GWh:",
              "  the rows already stand nearly across the prevailing sector;",
              "  a small gain is not worth new land or a turbine nearer the",
              "  camp; orientation matters most where the wind rose is narrow"]
    emit("h_orientation", lines)


if __name__ == "__main__":
    stagger()
    orientation()
