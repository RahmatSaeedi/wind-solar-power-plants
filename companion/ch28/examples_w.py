"""Chapter 28 - expansion round 12: the grid strength a unit sees at its
own terminals (weaker than the POC), and the S1 night case with the
battery charging from the grid.

Run from the project root:   python -m companion.ch28.examples_w
Writes companion/ch28/expected/w_*.txt. Teaching values.
"""
from __future__ import annotations

import numpy as np

from companion.ch28 import sources as src
from companion.ch28.common import emit
from plantp import gridstudy as gs


def terminal_strength() -> None:
    lines = ["short-circuit level seen from each place, per MW of the units behind it",
             "  place                       grid    S_sc MVA   MW behind   ratio"]
    for grid in ("max", "min"):
        br = src.branches(grid)
        zbus = np.linalg.inv(gs.ybus(src.N, br)[1:, 1:])
        for name, k, mw in (("POC", 1, 100.0), ("MV-A", 3, 65.0), ("WS1 units (aggregated)", 13, 20.0),
                            ("PVF3 units (aggregated)", 15, 15.0)):
            s = 100.0 / abs(zbus[k - 1, k - 1])
            lines.append(f"  {name:26s}  {grid:4s}   {s:8.0f}   {mw:9.0f}   {s / mw:5.1f}")
    lines += ["  per MW of the units behind it, the 33 kV bus half is the",
              "  weakest place (5.6, and 4.8 on the weak grid) and the",
              "  units' terminals see 8-10 against 15 at the POC - the",
              "  transformers sit in between; a converter's control is",
              "  tuned for the strength at its terminals, which the plant's",
              "  study gives the maker (ch 27 weak grid, lesson E)"]
    emit("w_terminal", lines)


def s1_night() -> None:
    lines = ["S1 at night: the battery charges from the grid (grid max, 1.00)",
             "  battery MW   P at POC MW   Q at POC Mvar   V MV-B   losses MW"]
    for p_b in (0.0, -10.0, -20.0):
        r = src.solve({"wind": 0.0, "pv": 0.0, "bess": p_b / 20.0}, 0.0)
        lines.append(f"  {p_b:10.0f}   {round(r['s_poc'].real, 1) + 0.0:11.1f}   {r['s_poc'].imag:13.1f}"
                     f"   {r['v'][4]:6.3f}   {r['loss_mw']:9.2f}")
    lines += ["  charging turns the plant into a load at the POC: the",
              "  operator's study of the plant then includes an import",
              "  case (voltage, losses, any import limit or tariff), and",
              "  the meters record both directions (ch 34, 37)"]
    emit("w_s1night", lines)


if __name__ == "__main__":
    terminal_strength()
    s1_night()
