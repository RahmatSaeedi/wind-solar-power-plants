"""Chapter 27 - expansion round 10: how a voltage dip changes as it
passes the plant's transformers (YNd11 main, Dyn unit), how the plant's
reactive current lifts the voltage during a dip, and how many dips a
year the network around the POC produces (area of vulnerability).

Run from the project root:   python -m companion.ch27.examples_y
Writes companion/ch27/expected/y_*.txt and diagrams/data/ch27-vulnerability.csv.
Teaching values (A-337, A-338).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch27.common import csv, emit

A = complex(-0.5, math.sqrt(3) / 2)          # 120-degree operator


# [start: dip]
def through_delta(v: np.ndarray) -> np.ndarray:
    """Phase voltages (pu) on the far side of a delta-star or star-delta
    transformer: line-to-line voltages of the near side / sqrt3 (the
    30-degree shift does not change magnitudes; zero sequence is lost)."""
    return np.array([v[0] - v[1], v[1] - v[2], v[2] - v[0]]) / math.sqrt(3)


def positive_seq(v: np.ndarray) -> float:
    return abs((v[0] + A * v[1] + A * A * v[2]) / 3)
# [end: dip]


def dip_path() -> None:
    cases = {
        "single-phase fault (0.3 pu)": np.array([0.3, A * A, A]),
        "phase-to-phase fault": np.array([1.0, -0.5 + 0j, -0.5 + 0j]),
    }
    lines = ["a dip at the POC as seen further into the plant (magnitudes, pu)",
             "  case / place                    phase a   phase b   phase c   pos. seq"]
    for name, v in cases.items():
        lines.append(f"  {name}")
        for place, vv in (("POC 132 kV (phase-earth)", v),
                          ("33 kV bus (after YNd11)", through_delta(v)),
                          ("unit 600 V (after Dyn)", through_delta(through_delta(v)))):
            m = np.abs(vv)
            lines.append(f"    {place:28s}   {m[0]:7.2f}   {m[1]:7.2f}   {m[2]:7.2f}"
                         f"   {positive_seq(vv):8.2f}")
    lines += ["  one deep phase at the POC becomes two moderate ones at",
              "  33 kV and one deeper one again at 600 V; a phase-to-phase",
              "  fault looks deeper at 33 kV (one phase at zero) than at",
              "  the POC; the positive sequence (what most converters",
              "  control) is the same at every level - a ride-through",
              "  check states which voltage it uses (lowest phase, line-",
              "  to-line or positive sequence) and where"]
    emit("y_path", lines)


def reactive_boost() -> None:
    k, s_rated = 2.0, 121.0
    lines = ["voltage during a dip with the plant's reactive current (k = 2,",
             "  current limited to 1.0 pu of 121 MVA; teaching quasi-steady model)",
             "  SCR   x pu    U without pu   U with pu   reactive current pu"]
    for scr in (15, 5, 3):
        x = s_rated / (scr * 100.0)
        for u0 in (0.5, 0.8):
            u = (u0 + x * k) / (1 + x * k)
            iq = k * (1 - u)
            if iq > 1.0:
                iq, u = 1.0, u0 + x
            lines.append(f"  {scr:3d}   {x:5.3f}   {u0:12.2f}   {u:9.2f}   {iq:19.2f}")
    lines += ["  on a strong grid the plant's reactive current lifts the",
              "  voltage a little; on a weak grid much more - which also",
              "  means the plant must stop injecting quickly when the fault",
              "  clears, or the voltage overshoots (lesson E, recovery)"]
    emit("y_boost", lines)


def vulnerability() -> None:
    z_s = 132.0 ** 2 / 1500.0                # ohm, source behind the grid substation
    z_line = 0.4                             # ohm per km
    rate, n_lines = 2.0, 4                   # faults per 100 km a year, lines radiating
    d = np.linspace(0, 200, 81)
    u = z_line * d / (z_s + z_line * d)
    csv("ch27-vulnerability.csv", "d,u", [(f"{a:.1f}", f"{b:.3f}") for a, b in zip(d, u)])
    lines = ["area of vulnerability: residual voltage at the POC for a three-phase",
             f"  fault d km out on a 132 kV line (source {z_s:.1f} ohm, line 0.4 ohm/km;",
             f"  {n_lines} lines radiating, {rate:.0f} faults per 100 km a year; teaching)",
             "  residual below   fault within km   dips a year (upper bound)"]
    for target in (0.5, 0.7, 0.85):
        dd = target / (1 - target) * z_s / z_line
        lines.append(f"  {target:15.2f}   {dd:15.0f}   {rate * n_lines * dd / 100:25.1f}")
    lines += ["  every fault is treated as three-phase here, so the counts",
              "  are an upper bound; single-phase faults (most of them)",
              "  give shallower dips at the plant after the transformers;",
              "  the ride-through requirement is not a rare event - a",
              "  plant connected to this network rides several dips a",
              "  year"]
    emit("y_vulnerability", lines)


if __name__ == "__main__":
    dip_path()
    reactive_boost()
    vulnerability()
