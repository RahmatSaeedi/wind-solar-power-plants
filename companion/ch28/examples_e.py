"""Chapter 28, lesson E (conditional): grid strength with the plant's
neighbours, grid-forming against grid-following behaviour after a phase
jump, protection when only converters feed a fault, and
resynchronisation and black start limits.

Plant P is grid-following and offers neither grid forming nor black
start (D-024); these studies apply only where a requirement or a
contract asks for them.

Run from the project root:   python -m companion.ch28.examples_e
Writes companion/ch28/expected/e_*.txt. Teaching values (A-341, A-345).
"""
from __future__ import annotations

import math

from companion.ch28 import sources as src
from companion.ch28.common import emit
from plantp import gridstudy as gs

NEIGHBOURS = [("Plant P", 100.0, 1.00), ("plant Q, PV at the same substation", 80.0, 1.00),
              ("plant R, wind 20 km away", 60.0, 0.73)]   # MW, share of POC strength


def strength() -> None:
    q_shunt = 5.0 + 1.77 + 0.35          # filter (if fitted), cables, line (ch 27, B)
    lines = ["grid strength seen by Plant P alone and with its neighbours (teaching)",
             "  case   SCR    ESCR (with 7.1 Mvar shunt)   WSCR (P, Q, R)   dU per 10 Mvar %"]
    for case in ("max", "min"):
        s = src.GRID[case]["s_sc"]
        scr = s / 100
        e = gs.escr(s, q_shunt, 100)
        w = gs.wscr([s * k for _, _, k in NEIGHBOURS], [p for _, p, _ in NEIGHBOURS])
        lines.append(f"  {case:4s}   {scr:4.1f}   {e:26.1f}   {w:14.1f}   {100 * 10 / s:16.2f}")
    lines += [f"  neighbour: {n}, {p:.0f} MW" for n, p, _ in NEIGHBOURS[1:]]
    lines += [
              "  alone the plant sees a strong grid (SCR 9-15); with the two",
              "  converter plants beside it the grid behaves as if it were",
              "  much weaker (WSCR 3.5-5.8) - converter interactions are",
              "  studied with all of them in an EMT model, not one at a time"]
    emit("e_strength", lines)


def phase_jump() -> None:
    lines = ["extra current after a grid phase jump (pu of rating, teaching)",
             "  jump deg   grid-forming x 0.15   x 0.30   grid-following (PLL)"]
    for d in (10, 20, 40):
        lines.append(f"  {d:8d}   {gs.phase_jump_current(d, 0.15):19.2f}   "
                     f"{gs.phase_jump_current(d, 0.30):6.2f}   {'~0 (tracks)':>20s}")
    lines += ["  a grid-forming source answers a jump at once, like a",
              "  machine: with x 0.15 a 10 degree jump alone nearly fills a",
              "  1.2 pu current limit; a grid-following one tracks the angle",
              "  and helps only through its controls - which behaviour the",
              "  operator wants, and the current headroom for it, is a",
              "  requirement and a study, never a default (D-024)"]
    emit("e_gfm", lines)


def low_fault() -> None:
    i_grid = 250e3 / 0.04 / (math.sqrt(3) * 400) / 1e3       # kA via the 250 kVA SST
    i_isl = 1.2 * 250e3 / (math.sqrt(3) * 400) / 1e3           # kA from a 250 kVA source
    lines = ["fault current at the 400 V auxiliary board: grid-fed or islanded",
             f"  grid-fed through the 250 kVA station transformer (uk 4 %): {i_grid:5.2f} kA",
             f"  islanded from a 250 kVA grid-forming source at 1.2 pu:      {i_isl:5.2f} kA",
             "  type C breaker   instantaneous trip at 10 x In   grid-fed   islanded"]
    for i_n in (16, 32, 63, 100, 160):
        need = 10 * i_n / 1e3
        lines.append(f"  {i_n:13d} A   {need:26.2f} kA   {'trips' if i_grid >= need else 'slow':>8s}"
                     f"   {'trips' if i_isl >= need else 'slow':>8s}")
    lines += ["  in an island fed only by converters every breaker above",
              "  about 40 A clears a fault on its slow thermal curve, if at",
              "  all: the protection of an islanded supply is designed for",
              "  it (undervoltage, differential, a source that can give",
              "  more current) - it is not the grid-connected design"]
    emit("e_lowfault", lines)


def resync() -> None:
    lines = ["joining an island back to the grid (synchronising check, teaching)",
             "  slip Hz   angle deg/s   +/-10 deg window s   80 ms breaker travel deg"]
    for df in (0.05, 0.10, 0.20):
        rate = 360 * df
        lines.append(f"  {df:7.2f}   {rate:11.0f}   {20 / rate:18.2f}   {0.08 * rate:24.1f}")
    lines += ["  power surge on closing through x = 0.2 pu (island rating 20 MVA)",
              "  angle deg   surge pu   surge MW"]
    for d in (5, 10, 20):
        p = gs.sync_power(1.0, 1.0, 0.2, d)
        lines.append(f"  {d:9d}   {p:8.2f}   {20 * p:8.1f}")
    inrush = 5 * 63.0
    lines += [f"  black start: a 63 MVA main transformer draws ~{inrush:.0f} MVA of inrush",
              "  (5 x rated, teaching) against 24 MVA a 20 MVA battery can give;",
              "  it needs soft energisation (voltage raised from zero) designed",
              "  into both - Plant P offers neither black start nor islanded",
              "  export (D-024); a study and tests would come first"]
    emit("e_resync", lines)


if __name__ == "__main__":
    strength()
    phase_jump()
    low_fault()
    resync()
