"""Chapter 19, more of section C: setting the limit of a seven-day
voltage-drop screen from the statistics of a lot (false rejects against
misses), the pulse resistance of a cell at three pulse lengths and two
temperatures, a capacity test against the warranty curve with the test
uncertainty, and the structure of the runoff volume.

Run from the project root:   python -m companion.ch19.examples_g
Writes companion/ch19/expected/g_*.txt and diagrams/data/ch19-*.csv.
Teaching values A-294 and A-295.
"""
from __future__ import annotations

import math

import numpy as np
from scipy.stats import norm

from companion.ch19 import examples_f as ef, sources as src
from companion.ch19.common import csv, emit
from plantp import storage as st

C = src.LFP


def screen() -> None:
    """Seven-day drop at 30 % SOC: good cells N(0.62, 0.12) mV with
    measurement noise; leaky cells N(3.45, 0.5) mV (A-294)."""
    good, bad = (0.62, 0.12), (3.45, 0.50)
    lot, share = 2000, 0.0005
    lines = ["setting the limit of the seven-day drop screen (lot of 2,000):",
             "  limit mV   good cells rejected   chance a leaky cell passes"]
    rows = []
    for lim in (0.9, 1.0, 1.2, 1.5, 2.0, 2.5):
        fr = lot * (1 - share) * (1 - norm.cdf(lim, *good))
        miss = norm.cdf(lim, *bad)
        lines.append(f"  {lim:7.1f}   {fr:19.2f}   {miss:24.2e}")
    for lim in np.linspace(0.5, 4.0, 71):
        rows.append((f"{lim:.2f}", f"{norm.pdf(lim, *good):.4f}", f"{norm.pdf(lim, *bad):.4f}"))
    lines += ["  a low limit rejects good cells, a high one passes leaky",
              "  ones; with these spreads 1.5 mV rejects almost none and",
              "  misses almost none: the screen works only if it is applied",
              "  to every cell (the maker's ageing step), not to a sample"]
    emit("g_screen", lines)
    csv("ch19-kvalue.csv", "mv,good,bad", rows)


# [start: pulse]
def pulse_resistance(t_pulse: float, temp_c: float,
                     c_rate: float = 1.0) -> float:
    """Apparent resistance dV/dI (mohm) of a discharge pulse from rest at
    50 % SOC after t_pulse seconds."""
    cell = st.Cell(q_ah=C.q_ah, r0=ef.r_at(temp_c, C.r0),
                   r1=ef.r_at(temp_c, C.r1), c1=C.c1, chem=C.chem)
    i = c_rate * cell.q_ah
    dt = 0.1
    n = max(int(t_pulse / dt), 1)
    v, s = st.simulate(cell, np.full(n, i), dt, 0.5)
    v_rest = float(st.ocv(0.5))
    return 1000 * (v_rest - v[-1]) / i
# [end: pulse]


def dcir() -> None:
    lines = ["pulse resistance of the cell at 1 C from rest, 50 % SOC:",
             "  pulse s    25 C mohm   10 C mohm"]
    rows = []
    for t in (0.1, 1.0, 10.0, 30.0, 60.0):
        r25, r10 = pulse_resistance(t, 25.0), pulse_resistance(t, 10.0)
        lines.append(f"  {t:7.1f}    {r25:9.3f}   {r10:9.3f}")
    for t in np.linspace(0.1, 120, 60):
        rows.append((f"{t:.1f}", f"{pulse_resistance(t, 25.0):.4f}"))
    lines += ["  the 'resistance' of a cell depends on how long the pulse",
              "  lasts and on temperature; a test report states both, and a",
              "  trend is valid only between tests made the same way"]
    emit("g_dcir", lines)
    csv("ch19-dcir.csv", "t,r", rows)


def capacity_test() -> None:
    """Year-5 test against a warranty curve of 2.5 %/yr (teaching)."""
    nominal, warranty = 40.13, 1 - 0.025 * 5
    floor = nominal * warranty
    u = 0.01                                         # test uncertainty, 1 sd share
    lines = ["capacity test in year 5 against a teaching warranty curve",
             f"  (-2.5 %/yr: floor {100 * warranty:.1f} % = {floor:.2f} MWh; test sd 1 %):",
             "  measured MWh   below the floor by   chance truly below   claim?"]
    for m in (36.2, 35.3, 34.9, 34.3):
        z = (floor - m) / (u * m)
        p = norm.cdf(z)
        claim = "yes" if p > 0.95 else ("discuss" if p > 0.5 else "no")
        lines.append(f"  {m:12.1f}   {floor - m:+17.2f}   {p:18.2f}   {claim:>7s}")
    lines += ["  a claim needs the test method agreed in the contract (rate,",
              "  temperature, window, rest) and its uncertainty; a result",
              "  within the uncertainty of the floor is a discussion, not a",
              "  claim (chapter 16 on uncertainty, chapter 51 on operation)"]
    emit("g_capacity", lines)


def runoff() -> None:
    area, rain = 400.0, 0.050                       # m2 around 2 containers, m
    lines = ["runoff containment around a pair of containers (structure only):",
             f"  rain on the bunded area: {area:.0f} m2 x {1000 * rain:.0f} mm design rain"
             f" = {area * rain:.0f} m3",
             "  plus the water the fire plan may use: V_fire (from the fire",
             "    authority and the hazard mitigation analysis; not given here)",
             "  plus freeboard; then a valve, a sampling point and a disposal",
             "    route agreed with the environmental authority",
             "  the book gives the structure, not the volume"]
    emit("g_runoff", lines)


if __name__ == "__main__":
    screen()
    dcir()
    capacity_test()
    runoff()
