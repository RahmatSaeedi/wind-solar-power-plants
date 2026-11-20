"""Chapter 28 - expansion round 1: voltage stability at the POC (P-V
'nose' curves for the strong and the weak grid), the voltage sensitivity
of each bus to reactive power, and where the tap changers run out.

Run from the project root:   python -m companion.ch28.examples_h
Writes companion/ch28/expected/h_*.txt and diagrams/data/ch28-nose.csv.
Teaching values (A-341, A-342).
"""
from __future__ import annotations

import numpy as np

from companion.ch28 import sources as src
from companion.ch28.common import csv, emit


# [start: nose]
def nose(grid: str, q_pu: float = 0.0, step: float = 0.05) -> list:
    """Raise the plant's output in steps (beyond its real size, as a
    study does) until the load flow no longer solves; returns
    (MW at the POC, POC voltage) points up to the last solution."""
    pts, x = [], 0.0
    while True:
        try:
            r = src.solve({"wind": x, "pv": x}, q_pu, grid=grid)
        except RuntimeError:
            return pts
        pts.append((r["s_poc"].real, r["v"][1]))
        x += step
# [end: nose]


def nose_curves() -> None:
    lines = ["P-V curves at the POC: output raised (in study only) until no solution",
             "  grid     unit q   last solved MW   POC V there   margin over 100 MW"]
    data = {}
    for grid in ("max", "min"):
        for q in (0.0, 0.12):
            pts = nose(grid, q, step=0.1)
            p_last, v_last = pts[-1]
            lines.append(f"  {grid:6s}   {q:6.2f}   {p_last:14.0f}   {v_last:11.3f}   "
                         f"{p_last / 100:16.1f} x")
            data[(grid, q)] = pts
    rows = []
    for k in range(max(len(v) for v in data.values())):
        row = [str(k)]
        for key in (("max", 0.0), ("min", 0.0)):
            pts = data[key]
            row += [f"{pts[k][0]:.1f}", f"{pts[k][1]:.4f}"] if k < len(pts) else ["nan", "nan"]
        rows.append(tuple(row))
    csv("ch28-nose.csv", "k,pmax,vmax,pmin,vmin", rows)
    lines += ["  the plant is far from the voltage-stability limit of its",
              "  connection (about twice its size); the weak grid lowers",
              "  the limit by about an eighth and the units' reactive power",
              "  moves it out again - a study shows the margin,",
              "  it does not assume it (a weak connection or a long line",
              "  can bring the nose close to the plant's own output)"]
    emit("h_nose", lines)


def sensitivity() -> None:
    base = src.solve({"wind": 1.0, "pv": 0.84}, 0.12)
    up = src.solve({"wind": 1.0, "pv": 0.84}, 0.12 + 10.0 / 122.2)
    lines = ["voltage change at each bus for 10 Mvar more from the units (grid max)",
             "  bus        V before   V after   dV per 10 Mvar %"]
    for name, k in (("POC", 1), ("HV", 2), ("MV-A", 3), ("WS1 end", 5), ("WS1 units", 13),
                    ("PVF3 units", 15)):
        lines.append(f"  {name:10s} {base['v'][k]:8.4f}   {up['v'][k]:7.4f}   "
                     f"{100 * (up['v'][k] - base['v'][k]):16.2f}")
    lines += ["  the same 10 Mvar moves the POC by about 0.7 % and the",
              "  units' own terminals by more: the impedance between them",
              "  adds up - a unit controller that 'sees' its terminal moves",
              "  further than the POC does, which is why the plant",
              "  controller, not the units, regulates the POC voltage"]
    emit("h_sensitivity", lines)


def tap_map() -> None:
    lines = ["can the taps hold the 33 kV bus at 1.00 +/- 0.0125? (grid min)",
             "  source V   P 0 MW         P 50 MW        P 100 MW"]
    for e in (0.90, 0.95, 1.00, 1.05, 1.10):
        cells = []
        for x in (0.0, 0.45, 0.91):
            t, r = src.oltc({"wind": x, "pv": x}, 0.12 if x > 0 else 0.0, grid="min", e=e)
            ok = abs(r["v"][3] - 1.0) <= 0.0125
            cells.append(f"{100 * (t - 1):+5.1f} % {'ok' if ok else 'OUT':3s}")
        lines.append(f"  {e:8.2f}   " + "   ".join(cells))
    lines += ["  the taps hold the 33 kV bus everywhere but at the top of",
              "  the grid's band with output: at 1.10 pu they reach their",
              "  +10 % end stop and the bus rises out of band; there the",
              "  units must absorb reactive power (or the tap range is",
              "  widened) - the study names the remedy and the operator",
              "  confirms how often the grid sits at 1.10"]
    emit("h_taps", lines)


if __name__ == "__main__":
    nose_curves()
    sensitivity()
    tap_map()
