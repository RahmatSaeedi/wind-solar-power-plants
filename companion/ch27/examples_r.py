"""Chapter 27 - expansion round 4: where the plant's 5th-harmonic current
goes (grid, cables, filter), flicker of the turbines by the flicker
coefficient, long-term flicker from short-term values, voltage THD from
several harmonics, active-power recovery after a grid fault, and a
root-cause table for an investigation.

Run from the project root:   python -m companion.ch27.examples_r
Writes companion/ch27/expected/r_*.txt and diagrams/data/ch27-recovery.csv.
Teaching values A-336 to A-339.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch27 import sources as src
from companion.ch27.common import csv, emit
from plantp import pq


def current_split() -> None:
    n, f = src.NET, src.FILTER
    h = 5.0
    z_base = n["kv_33"] ** 2 / n["s_sc_33"]
    x1 = z_base / math.sqrt(1 + 1 / n["xr_33"] ** 2)
    zg = complex(x1 / n["xr_33"], x1 * h)
    zc = 1 / (1j * h * n["q_cables"] / n["kv_33"] ** 2)
    xc1 = n["kv_33"] ** 2 / f["q_mvar"] * (f["h_tune"] ** 2 - 1) / f["h_tune"] ** 2
    xl1 = xc1 / f["h_tune"] ** 2
    zf = complex(xl1 * f["h_tune"] / f["quality"], xl1 * h - xc1 / h)
    lines = ["where the plant's 5th-harmonic current goes at the 33 kV bus (teaching;",
             "  magnitudes as % of the injected current - branches out of",
             "  phase with each other can each exceed 100 %)",
             "  case             to the grid   to the cables   to the filter"]
    for name, branches in (("no filter", (zg, zc)), ("with filter", (zg, zc, zf))):
        y = [1 / z for z in branches]
        tot = sum(y)
        shares = [abs(v / tot) for v in y] + ([0.0] if len(y) == 2 else [])
        lines.append(f"  {name:15s} {shares[0]:12.0%}   {shares[1]:13.0%}   {shares[2]:13.0%}")
    lines += ["  without the filter all of it (and a little more, the cables",
              "  pushing against it) flows into the grid and makes a voltage",
              "  there; with it, most stays in the",
              "  plant - the filter must be rated for the plant's own 5th",
              "  AND the network's (lesson B, amplification), or it",
              "  overloads"]
    emit("r_split", lines)


def flicker_coeff() -> None:
    c, s_n = 5.0, 5.5
    lines = ["flicker of the 12 turbines by the flicker coefficient (teaching c = 5)",
             "  Pst of one turbine = c S_n / S_k; of N equal turbines x sqrt(N)",
             "  network S_k MVA   one turbine   twelve turbines"]
    for s_k in (1500.0, 600.0, 300.0):
        one = c * s_n / s_k
        lines.append(f"  {s_k:16.0f}   {one:11.3f}   {one * math.sqrt(12):15.3f}")
    lines += ["  the coefficient comes from the turbine's type test (the",
              "  measurement standard STD-053 defines it for grid angles and",
              "  wind speeds); summed over the farm it stays far below the",
              "  operator's planning level even on a weak network - wind",
              "  farms with modern converters rarely set flicker limits"]
    emit("r_flicker", lines)


def plt_from_pst() -> None:
    pst = [0.25, 0.30, 0.28, 0.35, 0.90, 0.32, 0.27, 0.26, 0.31, 0.29, 0.30, 0.28]
    plt = (sum(p ** 3 for p in pst) / 12) ** (1 / 3)
    lines = ["long-term flicker Plt from twelve 10-minute Pst values (2 hours)",
             "  Pst: " + " ".join(f"{p:.2f}" for p in pst),
             f"  Plt = (sum Pst^3 / 12)^(1/3) = {plt:.3f};  mean Pst = {np.mean(pst):.3f}",
             "  the cube weights the one high value (0.90, a switching",
             "  event) strongly: Plt sits above the plain mean - a rule",
             "  chosen so that short severe flicker is not averaged away"]
    emit("r_plt", lines)


def thd_v() -> None:
    v = {5: 1.83, 7: 0.90, 11: 0.50, 13: 0.40}
    thd = math.sqrt(sum(x * x for x in v.values()))
    lines = ["voltage THD at the POC from the measured harmonics (teaching, % of U1)",
             "  " + ", ".join(f"h{h}: {x:.2f}" for h, x in v.items()),
             f"  THD_U = sqrt(sum U_h^2) = {thd:.2f} %",
             "  a total can hide which order is the problem: the 5th holds",
             f"  {v[5] ** 2 / thd ** 2:.0%} of the sum of squares here; limits and planning levels",
             "  are given per order as well as in total"]
    emit("r_thdv", lines)


def recovery() -> None:
    t = np.arange(-0.2, 2.0, 0.01)
    p = np.where(t < 0, 80.0, np.where(t < 0.15, 5.0, 5.0 + 75.0 * (1 - np.exp(-(t - 0.15) / 0.25))))
    t90 = float(t[np.argmax((t > 0.15) & (p >= 0.9 * 80))])
    csv("ch27-recovery.csv", "t,p", [(f"{a:.2f}", f"{b:.2f}") for a, b in zip(t, p)])
    lines = ["active-power recovery after a 150 ms grid fault (synthetic, A-339)",
             "  80 MW before; 5 MW during the fault; recovery after clearing",
             f"  time from clearing to 90 % of the pre-fault power: {t90 - 0.15:.2f} s",
             f"  teaching requirement 1.0 s: {'met' if t90 - 0.15 <= 1.0 else 'not met'}",
             "  recovery too slow loses energy the grid counts on; too fast",
             "  can shake a weak grid - the operator sets a window, and",
             "  the model used in the grid study (ch 28) must reproduce",
             "  the measured curve (model validation)"]
    emit("r_recovery", lines)


def root_causes() -> None:
    rows = [("network", "capacitor switching, resonance, other emitters", "switching log, scan"),
            ("plant", "converter emission, filter detuned, settings", "currents, unit bins"),
            ("measurement", "CVT error, clock offset, wrong window", "transducer data"),
            ("load", "neighbour's capacitors, drives", "their records"),
            ("operation", "new firmware, changed set-point", "configuration log")]
    lines = ["root-cause families for a power-quality complaint (teaching)"]
    for a, b, c in rows:
        lines += [f"  {a}: {b}", f"      evidence: {c}"]
    lines += ["  every family stays open until its evidence closes it - the",
              "  investigation report lists all five, not only the one",
              "  that was suspected first"]
    emit("r_causes", lines)


if __name__ == "__main__":
    current_split()
    flicker_coeff()
    plt_from_pst()
    thd_v()
    recovery()
    root_causes()
