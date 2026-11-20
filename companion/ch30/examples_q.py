"""Chapter 30, lesson Q: more on fabrication and erection - the scatter of
bolt preload by tightening method, when grout is strong enough to load
(maturity, from the data-pack temperatures), a control chart of weld
repairs, and tolerance stack-up at the anchor cage.

Run from the project root:   python -m companion.ch30.examples_q
Writes companion/ch30/expected/q_*.txt and diagrams/data/ch30-maturity.csv.
Teaching values (A-362); the maker's procedures and the grout supplier's
data set the real values.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch30 import sources as src  # noqa: F401  (puts plantp on the path)
from companion.ch30.common import csv, emit
from plantp import datapack


def scatter() -> None:
    a_s, fub = 1473e-6, 1000e6                        # M48 10.9 (teaching)
    nominal = 0.7 * fub * a_s / 1000                  # kN
    lines = ["preload of a flange bolt by tightening method (M48 10.9, teaching)",
             f"  nominal preload 0.7 fub As = {nominal:,.0f} kN",
             "  method                        scatter   lowest kN   bolts for same min"]
    base = None
    for name, sc in [("torque (lubricated, k known)", 0.25), ("torque + angle", 0.15),
                     ("hydraulic tensioning", 0.10)]:
        low = nominal * (1 - sc)
        base = base or low
        lines.append(f"  {name:29s} {sc * 100:5.0f} %   {low:9,.0f}   {base / low * 100:13.0f} %")
    lines += ["  the design must assume the lowest preload the method can",
              "  give: with torque alone the flange needs about a fifth",
              "  more bolt force than with tensioning - or fewer bolts",
              "  slip; the maker's procedure names the method, the tool",
              "  calibration and the lubricant, and checks a sample"]
    emit("q_scatter", lines)


def maturity() -> None:
    d = datapack.load_hourly()
    t_air = d["t_air_c"].to_numpy()
    t0, target = -10.0, 1800.0                        # datum C, maturity C-h for 70 %
    rows, lines = [], ["when the grout may be loaded: maturity (Nurse-Saul, teaching)",
                       f"  M = sum (T - ({t0:.0f})) dt; 70 % strength at {target:,.0f} C-h"
                       " (supplier's curve)",
                       "  pour on the 1st at 08:00   grout = air + 5 K   hours to 70 %"]
    for month in (1, 4, 7, 10):
        start = int(np.argmax((d.index.month == month) & (d.index.day == 1) & (d.index.hour == 8)))
        temp = t_air[start:start + 24 * 14] + 5.0
        m = np.cumsum(np.maximum(temp - t0, 0.0))
        hours = int(np.argmax(m >= target)) + 1
        rows.append((month, hours))
        lines.append(f"  month {month:2d}                  mean {temp[:hours].mean():5.1f} C"
                     f"         {hours:5d}")
    csv("ch30-maturity.csv", "month,hours", rows)
    lines += ["  a January pour waits about twice as long as a July one",
              "  before the anchors may be tensioned; the hold point is",
              "  the measured strength of cubes cured beside the grout",
              "  (or a maturity logger), never the calendar"]
    emit("q_maturity", lines)


def pchart(seed: int = 30) -> None:
    rng = np.random.default_rng(seed)
    n = 120
    p_true = np.full(16, 0.03)
    p_true[11:14] = 0.09                               # a new welder, weeks 12-14
    repairs = rng.binomial(n, p_true)
    p_bar = repairs[:10].sum() / (10 * n)
    ucl = p_bar + 3 * math.sqrt(p_bar * (1 - p_bar) / n)
    lines = ["weld repairs per week (120 welds tested by UT, synthetic)",
             f"  centre line from weeks 1-10: {p_bar * 100:.1f} %; upper limit {ucl * 100:.1f} %",
             "  week   repairs   rate %   signal"]
    for w, r in enumerate(repairs, 1):
        rate = r / n
        lines.append(f"  {w:4d}   {r:7d}   {rate * 100:6.1f}   {'ABOVE' if rate > ucl else ''}")
    lines += ["  the chart separates the normal scatter of a stable process",
              "  from a cause worth finding: weeks above the limit start a",
              "  search (here a new welder), not a blame - and the repairs",
              "  themselves are re-tested like any weld"]
    emit("q_pchart", lines)


def stackup() -> None:
    parts = [("anchor cage template, hole position", 2.0),
             ("cage set-out on site (survey)", 1.5),
             ("cage movement in a controlled pour", 1.0),
             ("bottom flange hole position (factory)", 1.0)]
    worst = sum(v for _, v in parts)
    rss = math.sqrt(sum(v * v for _, v in parts))
    clearance = 3.0
    lines = ["tolerance stack-up: will the tower flange drop over the anchors?",
             "  contribution                              +/- mm"]
    for name, v in parts:
        lines.append(f"  {name:40s} {v:5.1f}")
    lines += [f"  worst case {worst:.1f} mm; root-sum-square {rss:.1f} mm;"
              f" hole clearance {clearance:.1f} mm",
              "  worst case does not fit, the statistical sum does - but",
              "  only if the parts are independent and the pour is",
              "  controlled; a top template held in place during the pour",
              "  and a survey before the grout make the RSS honest"]
    emit("q_stackup", lines)


if __name__ == "__main__":
    scatter()
    maturity()
    pchart()
    stackup()
