"""Chapter 24 - cables in the sun: the heat a PV string cable or an MV
cable on an outdoor tray takes from sunlight against the heat of its own
current; plus the heating curves of the emergency overload of lesson A
(figure data).

Run from the project root:   python -m companion.ch24.examples_z
Writes companion/ch24/expected/z_sun.txt and diagrams/data/ch24-overload.csv.
Teaching values (A-321..A-325 extended).
"""
from __future__ import annotations

import math

from companion.ch24.common import csv, emit


def sun() -> None:
    g = 1000.0
    rows = [("PV string 6 mm2, 13 A", 0.0065, 0.7, 13.0, 0.0222 / 6 * 1.25),
            ("LV 4 x 95 mm2 on a tray, 200 A", 0.040, 0.6, 200.0, 0.0222 / 95 * 1.25 * 3 / 1),
            ("33 kV 240 mm2 riser, 276 A", 0.065, 0.6, 276.0, 3 * 0.16e-3)]
    lines = ["sunlight against current on cables outdoors (1,000 W/m2, teaching):",
             "  cable                              sun W/m   own loss W/m   sun share"]
    for name, d, alpha, i, r in rows:
        q_sun = alpha * d * g
        q_i = i ** 2 * r
        lines.append(f"  {name:34s} {q_sun:7.1f}   {q_i:12.1f}   {q_sun / (q_sun + q_i):9.0%}")
    lines += ["  a thin PV cable is heated far more by the sun than by its",
              "  current: its insulation is rated for high temperature and",
              "  its rating assumes the sun; a riser or tray in the sun loses",
              "  part of its rating too - shade, a cover with air gap, or a",
              "  lighter colour, and the rating method's solar term"]
    emit("z_sun", lines)


def overload_data() -> None:
    tau, i0 = 1.5, 0.85
    th0 = 20 + 70 * i0 ** 2
    rows = []
    for k10 in range(0, 31):
        t = k10 / 10
        vals = [20 + 70 * k ** 2 + (th0 - 20 - 70 * k ** 2) * math.exp(-t / tau) for k in (1.1, 1.2, 1.3, 1.5)]
        rows.append((f"{t:.1f}", *(f"{v:.1f}" for v in vals)))
    csv("ch24-overload.csv", "t,k11,k12,k13,k15", rows)


if __name__ == "__main__":
    sun()
    overload_data()
