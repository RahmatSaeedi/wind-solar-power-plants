"""Chapter 28 - expansion round 9: choosing the Q(U) slope against the
plant's capability and the grid strength, the equipment margin as the
grid's fault level grows over the plant's life, and the trips a year a
mis-set undervoltage relay would cause.

Run from the project root:   python -m companion.ch28.examples_t
Writes companion/ch28/expected/t_*.txt and diagrams/data/ch28-qu.csv.
Teaching values (A-348).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch28 import sources as src
from companion.ch28.common import csv, emit
from plantp import gridstudy as gs

Q_MAX = 46.0          # Mvar the plant can give at the POC (lesson B)


# [start: qu]
def qu_point(e: float, s_sc: float, slope: float) -> tuple:
    """Steady state of a Q(U) characteristic (full Q_MAX for a deviation
    of `slope` pu) on a grid source e behind s_sc MVA: (U, Q)."""
    g = Q_MAX / (slope * s_sc)              # loop gain
    u = (e + g) / (1 + g)
    q = -(u - 1.0) / slope * Q_MAX
    if abs(q) > Q_MAX:                      # at the capability limit
        q = math.copysign(Q_MAX, q)
        u = e + q / s_sc
    return u, q
# [end: qu]


def qu_slope() -> None:
    lines = ["choosing the Q(U) slope (full 46 Mvar for a deviation of 'slope')",
             "  slope %   grid    source 0.95: U POC  Q Mvar    source 1.05: U POC  Q Mvar"]
    for slope in (0.02, 0.04, 0.08):
        for grid, s_sc in (("max", 1500.0), ("min", 900.0)):
            lo = qu_point(0.95, s_sc, slope)
            hi = qu_point(1.05, s_sc, slope)
            lines.append(f"  {100 * slope:7.0f}   {grid:4s}   {lo[0]:18.3f}  {lo[1]:6.1f}"
                         f"    {hi[0]:18.3f}  {hi[1]:6.1f}")
    rows = []
    for u in np.linspace(0.90, 1.10, 41):
        rows.append((f"{u:.3f}",) + tuple(f"{max(min(-(u - 1) / s * Q_MAX, Q_MAX), -Q_MAX):.1f}"
                                          for s in (0.02, 0.04, 0.08)))
    csv("ch28-qu.csv", "u,s2,s4,s8", rows)
    lines += ["  a steep characteristic (2 %) spends nearly the whole",
              "  capability on a 5 % grid deviation; a shallow one (8 %)",
              "  uses less than half and lets the voltage wander more;",
              "  even the steepest brings 0.95 only to 0.98 on this POC",
              "  (lesson B: 0.7 % per 10 Mvar) - the slope is chosen with",
              "  the operator for the grid's needs, inside the",
              "  requirement's range (REQ-G02)"]
    emit("t_qu", lines)


def fault_growth() -> None:
    lines = ["fault level growing 2 % a year over the plant's life (teaching)",
             "  year   S_sc MVA   POC kA (c 1.1, all)   MV-A kA   ratings 31.5 / 25"]
    for year in (0, 10, 20, 25):
        s = 1500 * 1.02 ** year
        src.GRID["future"] = dict(s_sc=s, xr=8.0)
        br = src.branches("future")
        zbus = np.linalg.inv(gs.ybus(src.N, br)[1:, 1:])
        sources = [(13 + j - 1, f.units * f.unit_mva * 1.1 / src.S_BASE)
                   for j, f in enumerate(src.FEEDERS) if f.kind != "bess"]
        poc = gs.fault_current(zbus, 0, 1.1, sources)["total"] * 100 / (math.sqrt(3) * 132)
        mv = gs.fault_current(zbus, 2, 1.1, sources)["total"] * 100 / (math.sqrt(3) * 33)
        lines.append(f"  {year:4d}   {s:8.0f}   {poc:19.2f}   {mv:7.2f}")
    del src.GRID["future"]
    lines += ["  the 132 kV current grows with the grid; the 33 kV current",
              "  hardly moves - the main transformers' impedance dominates",
              "  it; both stay inside the ratings for the plant's life, and",
              "  the study asks the operator for the planned growth"]
    emit("t_growth", lines)


def trips() -> None:
    dips = {"below 0.50 pu": 2.3, "0.50-0.70 pu": 5.4 - 2.3, "0.70-0.85 pu": 13.2 - 5.4}
    p_trip_bad = {"below 0.50 pu": 0.9, "0.50-0.70 pu": 0.8, "0.70-0.85 pu": 0.5}
    lost_per_trip = 6.7 + 34 * 0.5                 # MWh: restart (lesson C) + 30 min out
    lines = ["trips a year if an undervoltage relay is set at 0.80 pu, 0.2 s (an error)",
             "  (dip counts: ch 27's upper bound, every fault three-phase)",
             "  dip depth        dips/yr (ch 27)   share that trips   trips/yr"]
    total = 0.0
    for name, n in dips.items():
        t = n * p_trip_bad[name]
        total += t
        lines.append(f"  {name:15s}  {n:15.1f}   {p_trip_bad[name]:16.1f}   {t:8.1f}")
    lines += [f"  about {total:.0f} needless trips a year, ~{total * lost_per_trip:.0f} MWh"
              f" ({total * lost_per_trip * 0.07:.0f} k u) - and each one a",
              "  ride-through breach the operator records; settings are",
              "  checked against the ride-through envelope in the study",
              "  (ch 26 setting file), not left to defaults"]
    emit("t_trips", lines)


if __name__ == "__main__":
    qu_slope()
    fault_growth()
    trips()
