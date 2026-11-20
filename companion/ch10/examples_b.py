"""Chapter 10, section B - cell-to-module product: one cell shaded in a
substring (hot spot) with and without its bypass diode, a cracked cell and
the module curve, and degradation against the warranty.

Run from the project root:   python -m companion.ch10.examples_b
Writes companion/ch10/expected/b_*.txt and diagrams/data/ch10-*.csv.
Teaching values A-188, A-189 (fictional).
"""
from __future__ import annotations

import warnings

import numpy as np
from scipy.optimize import brentq

from companion.ch10 import pvyear10
from companion.ch10.common import csv, emit
from plantp import pvcell as pc

warnings.simplefilter("ignore", RuntimeWarning)
N_CELL, N_SUB, V_BYP = 72, 3, 0.6          # cells, bypass substrings, diode drop


# [start: cell]
def cell_sdm(frac_light: float = 1.0, r_sh: float = 10.0) -> pc.SDM:
    """One cell of the PVM-550 (module parameters / 72; shunt 10 ohm per
    cell, A-188), photocurrent scaled by the share of light it receives."""
    m = pvyear10.ref_sdm()
    return pc.SDM(m.i_l * frac_light, m.i_0, m.a / N_CELL,
                  m.r_s / N_CELL, r_sh)


def cell_voltage(c: pc.SDM, i: float, v_br: float = -15.0) -> float:
    """Voltage of a cell at current i: forward from the model, reverse
    (i above the photocurrent) from the breakdown model, clamped at
    the breakdown voltage."""
    if i <= c.i_l:
        return float(c.v(i))
    f = lambda v: float(pc.cell_reverse_current(v, c.i_l, c.r_sh, v_br)) - i
    lo = v_br * 0.99999
    return v_br if f(lo) < 0 else brentq(f, lo, 0.0)


def substring_voltage(cells: list, i: float, bypass: bool = True) -> float:
    """Sum of the cell voltages, clamped by the bypass diode at -V_BYP."""
    v = sum(cell_voltage(c, i) for c in cells)
    return max(v, -V_BYP) if bypass else v
# [end: cell]


def hot_spot() -> None:
    i_string = 12.5
    lines = ["one cell at 20 % light in a 24-cell substring, string current"
             f" {i_string} A (A-188):",
             "  cell (shunt, breakdown)  cell V needed  substring V  bypass"
             "     heat"]
    for r_sh, v_br in ((10.0, -15.0), (100.0, -15.0), (300.0, -25.0)):
        full, shaded = cell_sdm(1.0, r_sh), cell_sdm(0.2, r_sh)
        v_sh = cell_voltage(shaded, i_string, v_br)
        v_sub = 23 * cell_voltage(full, i_string) + v_sh
        if v_sub > -V_BYP:
            heat, state = -v_sh * i_string, "off"
        else:
            f = lambda i: (23 * cell_voltage(full, i)
                           + cell_voltage(shaded, i, v_br) + V_BYP)
            i_sub = brentq(f, shaded.i_l * 1.0001, i_string)
            heat = -cell_voltage(shaded, i_sub, v_br) * i_sub
            state = f"on ({i_sub:.1f} A)"
        lines.append(f"  {r_sh:4.0f} ohm, {v_br:4.0f} V  {v_sh:12.2f} V  "
                     f"{v_sub:9.2f} V  {state:12s} {heat:4.0f} W")
        no_diode = -v_sh * i_string
    lines += ["  a leaky cell carries the string current at a modest reverse",
              "  voltage, the diode never turns on and the cell takes over",
              "  130 W; a hard cell would need more than the other 23 cells",
              "  give, so the diode conducts and limits the cell to about the",
              "  substring voltage at a smaller current: tens of watts on",
              "  0.0179 m2, still a hot spot that thermal imaging finds;",
              f"  without the diode that cell would take {no_diode:.0f} W"]
    emit("b_hotspot", lines)


def cracked() -> None:
    full = cell_sdm(1.0)
    lines = ["module power with one cell losing active area (crack, A-188):",
             "  inactive %   module P_mp W   loss %   cracked cell at MPP"]
    rows, p0 = [], None
    for frac in (0.0, 0.05, 0.10, 0.20, 0.30, 0.50):
        weak = cell_sdm(1 - frac)
        subs = [[weak] + [full] * 23, [full] * 24, [full] * 24]
        cur = np.linspace(0.2, full.i_l * 0.998, 300)
        pw = [sum(substring_voltage(sb, i) for sb in subs) * i for i in cur]
        k = int(np.argmax(pw))
        p0 = pw[k] if p0 is None else p0
        v_w = cell_voltage(weak, cur[k])
        state = (f"{v_w:+.2f} V, heat {-v_w * cur[k]:.0f} W" if v_w < 0
                 else f"{v_w:+.2f} V, producing")
        rows.append((int(100 * frac), f"{pw[k]:.1f}"))
        lines.append(f"  {100 * frac:9.0f}   {pw[k]:13.1f}   "
                     f"{100 * (1 - pw[k] / p0):6.1f}   {state}")
    lines += ["  a small crack costs its share of current in the whole series",
              "  substring; a larger one drives the cracked cell into reverse:",
              "  the module keeps most of its power but that one cell becomes",
              "  a hot spot (with a soft cell the bypass diode stays off)"]
    emit("b_cracked", lines)
    csv("ch10-crack.csv", "frac,p", rows)


def degradation() -> None:
    years = np.arange(1, 26)
    warranty = np.where(years == 1, 0.98, 0.98 - 0.0055 * (years - 1))   # A-189
    typical = (1 - 0.01) * (1 - 0.004) ** (years - 1)
    lines = ["degradation against a linear power warranty (A-189):",
             f"  warranty: 98 % after year 1, -0.55 %/yr -> {warranty[-1]:.3f} "
             "in year 25",
             f"  module degrading 1 % then 0.4 %/yr -> {typical[-1]:.3f} in "
             "year 25",
             f"  25-year mean output: warranty floor {warranty.mean():.3f}, "
             f"typical {typical.mean():.3f}",
             "  the warranty is a floor that triggers a claim, not a forecast;",
             "  a claim needs measured power with known uncertainty"]
    emit("b_degradation", lines)
    csv("ch10-degr.csv", "y,w,t", [(int(y), f"{a:.4f}", f"{b:.4f}")
                                   for y, a, b in zip(years, warranty, typical)])


if __name__ == "__main__":
    hot_spot()
    cracked()
    degradation()
