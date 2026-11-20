"""Chapter 30, lesson M: fatigue from a load history and durability -
rainflow counting of a synthetic tower-base moment record, the damage-
equivalent load for two S-N slopes, Miner's sum on the bilinear curve
against the single-slope shortcut, carbonation of the concrete cover,
and the coating's life to first maintenance.

Run from the project root:   python -m companion.ch30.examples_m
Writes companion/ch30/expected/m_*.txt and diagrams/data/ch30-*.csv.
Teaching values (A-356, A-362).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch30 import sources as src
from companion.ch30.common import csv, emit
from plantp import structures as st
from plantp import wind as w


def record():
    rng = np.random.default_rng(3030)
    t = np.arange(0, 600, 0.5)                                  # 10 minutes at 2 Hz
    m = (60 + 8 * np.sin(2 * np.pi * 0.215 * t) + 5 * np.sin(2 * np.pi * 0.19 * t + 1.0)
         + 6 * np.cumsum(rng.standard_normal(t.size)) / np.sqrt(t.size))
    return t, m


def rainflow_del() -> None:
    t, m = record()
    cycles = w.rainflow(m)
    rng_ = np.array([r for r, c in cycles])
    cnt = np.array([c for r, c in cycles])
    n_eq = 600 * 1.0                                            # 1 Hz reference, 10 min
    lines = ["rainflow counting of a 10-minute tower-base moment record (synthetic)",
             f"  {len(cycles)} counted ranges; largest {rng_.max():.1f} MN m"]
    for m_slope in (3, 5):
        del_ = (np.sum(cnt * rng_ ** m_slope) / n_eq) ** (1 / m_slope)
        lines.append(f"  DEL at 1 Hz, slope m = {m_slope}: {del_:.2f} MN m")
    csv("ch30-record.csv", "t,m", [(f"{a:.1f}", f"{b:.2f}") for a, b in zip(t[::4], m[::4])])
    lines += ["  the same record gives a larger DEL for the steeper slope:",
              "  the big ranges weigh more - so a DEL is always quoted with",
              "  its slope and its reference cycle count, and welds (m 3)",
              "  and bolts or composites (other slopes) get their own"]
    emit("m_rainflow", lines)


def miner() -> None:
    spectrum = [(80, 2e4), (60, 2e5), (45, 1.5e6), (30, 8e6), (20, 4e7)]   # MPa, cycles/life
    det = 71.0
    d_bi = sum(n / st.sn_life(s, det) for s, n in spectrum)
    d_one = sum(n / (2e6 * (det / s) ** 3) for s, n in spectrum)
    lines = ["Miner's sum for a stress spectrum at a weld (teaching, detail 71)",
             "  range MPa   cycles in 20 yr   damage (bilinear)   damage (slope 3 only)"]
    for s, n in spectrum:
        lines.append(f"  {s:9.0f}   {n:15.1e}   {n / st.sn_life(s, det):17.3f}"
                     f"   {n / (2e6 * (det / s) ** 3):21.3f}")
    lines += [f"  total                         {d_bi:17.2f}   {d_one:21.2f}",
              "  the many small ranges below the knee hurt far less on the",
              "  shallower slope: the single-slope shortcut is safe but",
              "  pessimistic; the bilinear curve the code gives (with or",
              "  without a cut-off) is what the designer uses"]
    emit("m_miner", lines)


def carbonation() -> None:
    lines = ["carbonation of the concrete cover, x = k sqrt(t) (teaching k values)",
             "  concrete                     k mm/sqrt(yr)   years to reach 50 mm   60 mm"]
    for name, k in (("dense, low w/c (specified)", 3.0), ("average", 5.0),
                    ("poorly cured (hot weather)", 8.0)):
        lines.append(f"  {name:28s} {k:13.1f}   {(50 / k) ** 2:20.0f}   {(60 / k) ** 2:5.0f}")
    lines += ["  cover and curing, not strength alone, set the life of the",
              "  reinforcement: a hot-weather pour cured badly (ch 29) can",
              "  lose most of its protection within the plant's life;",
              "  sulphates from gypsum ground (T12) attack faster still"]
    emit("m_carbonation", lines)


def coating() -> None:
    cats = [("inland desert, dry (low)", 25), ("near a saline flat (medium)", 15),
            ("splash of irrigation or brine (high)", 8)]
    lines = ["tower coating: years to first major maintenance (teaching durability",
             "  for the 320 um system of ch 11; the coating maker states real values)"]
    for name, yrs in cats:
        lines.append(f"  {name:38s} {yrs:3d} years")
    lines += ["  the inside of the tower and the base flange, where",
              "  condensation and dust collect, often fail first; the",
              "  O&M plan inspects there before the outside (ch 52)"]
    emit("m_coating", lines)


def wall_effect() -> None:
    added_t = 32.0
    m_top = (src.TOP_T + 0.24 * (src.TOWER_T + added_t)) * 1e3
    m_old = (src.TOP_T + 0.24 * src.TOWER_T) * 1e3
    stiff = 1 + 0.08                                            # about 8 % more bending stiffness
    f_new = src.F1_FIXED * math.sqrt(stiff * m_old / m_top)
    lines = ["the thicker walls of lesson B change the tower's frequency",
             f"  +{added_t:.0f} t of steel low in the tower: stiffness up about 8 %"
             " (estimate),",
             f"  effective mass up {100 * (m_top / m_old - 1):.1f} %",
             f"  fixed-base f1: {src.F1_FIXED} -> {f_new:.3f} Hz",
             "  thicker walls low down raise the frequency a little: one",
             "  fix (fatigue) helps another check (1P margin) - but every",
             "  change to the tower goes back through the whole loop:",
             "  loads, frequency, fatigue, foundation (lesson D)"]
    emit("m_walls", lines)


if __name__ == "__main__":
    rainflow_del()
    miner()
    carbonation()
    coating()
    wall_effect()
