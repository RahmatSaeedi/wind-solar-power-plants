"""Chapter 9 - further lessons: harmonic emission carried to the 33 kV
collector, filter resonance against grid strength, UPS losses, the DC
voltage the machine-side converter needs at overspeed, film-capacitor life,
and the uncertainty of an inverter efficiency measurement.

Run from the project root:   python -m companion.ch09.examples_more2
Writes companion/ch09/expected/y_*.txt and diagrams/data/ch09-*.csv.
Teaching values A-173 .. A-177 (fictional); grid data A-100.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch09.common import csv, emit
from plantp import pe

S2, S3 = math.sqrt(2), math.sqrt(3)
L1, L2, C = 55.7e-6, 50.9e-6, 608e-6          # LCL of one stack (b_filter)


def harmonics_poc() -> None:
    f1, f_sw, m, v_dc = 50.0, 3000.0, 0.9, 1000.0
    n = 60000
    _, sa = pe.spwm_leg(m, f1, f_sw, n, levels=3)
    _, sb = pe.spwm_leg(m, f1, f_sw, n, levels=3, phase_deg=-120)
    h, a = pe.spectrum((sa - sb) * v_dc / 2, f1)                 # V peak, LL
    i_r = 1.375e6 / (S3 * 600)
    v_ph = a / S2 / S3                                           # RMS phase
    g = np.zeros(len(h))
    g[1:] = pe.lcl_gain(h[1:] * f1, L1, L2, C, 0.070)
    i_stack = v_ph * g                                           # A RMS
    ratio = 0.6 / 33.0
    n_stacks = 40
    i_lin = i_stack * n_stacks * ratio                           # aligned
    i_sqrt = i_stack * math.sqrt(n_stacks) * ratio               # random
    x_grid = 33e3 ** 2 / 500e6                                   # A-100
    i_33 = 50e6 / (S3 * 33e3)
    sel = (h > 1) & (h <= 200)
    top = h[sel][np.argsort(-i_stack[sel])][:3]
    v_h = i_sqrt * h * x_grid * S3 / 33e3                        # per unit
    lines = ["harmonic currents of one NPC stack after its LCL (A-173):",
             f"  rated stack current {i_r:,.0f} A; largest lines at h " +
             ", ".join(f"{k}" for k in sorted(top)),
             f"    h {int(top[0])}: {i_stack[int(top[0])]:.1f} A "
             f"({100 * i_stack[int(top[0])] / i_r:.2f} % of rated)",
             f"  total distortion of the stack current to h 200: "
             f"{100 * math.sqrt(np.sum(i_stack[sel] ** 2)) / i_r:.2f} %",
             "  40 stacks seen at 33 kV (current x 0.6/33):",
             f"    phases aligned (worst case)   "
             f"{100 * math.sqrt(np.sum(i_lin[sel] ** 2)) / i_33:.2f} % of 50 MW current",
             f"    random phases (sqrt N law)    "
             f"{100 * math.sqrt(np.sum(i_sqrt[sel] ** 2)) / i_33:.2f} %",
             f"  voltage distortion at 33 kV with 500 MVA short-circuit power:"
             f" {100 * math.sqrt(np.sum(v_h[sel] ** 2)):.3f} %",
             "  carrier harmonics are small after the filter and partly cancel;",
             "  the study of chapter 27 adds background distortion, cable",
             "  capacitance and resonance of the whole collector"]
    emit("y_harmonics", lines)
    csv("ch09-poc.csv", "h,pct", [(int(k), f"{100 * i_stack[k] / i_r:.4f}")
                                  for k in range(2, 161)])


def impedance() -> None:
    l_tx = 0.06 * (600 ** 2 / 1.375e6) / (2 * math.pi * 50)      # stack share
    lines = ["LCL resonance of one stack with the grid behind it (A-174):",
             "  SCR   grid L at 600 V side   resonance Hz"]
    for scr in (100, 10, 5, 3, 2):
        z = (600 ** 2) / (scr * 1.375e6)
        l_g = z / (2 * math.pi * 50) + l_tx
        f = pe.lcl_resonance(L1, L2 + l_g, C)
        lines.append(f"  {scr:4d}   {l_g * 1e6:12.1f} uH       {f:9.0f}")
    lines += ["  a weaker grid adds inductance in series with L2 and pulls the",
              "  resonance down towards the bandwidth of the current loop: the",
              "  converter that was stable on a strong grid may oscillate on a",
              "  weak one; damping and the maker's impedance model check it"]
    emit("y_impedance", lines)


def ups() -> None:
    p, eta, h = 12e3, 0.94, 8760.0                               # A-175
    loss = p * (1 / eta - 1)
    emit("y_ups", [
        f"double-conversion UPS for 12 kW of essential loads (A-175):",
        f"  efficiency {eta}: losses {loss / 1e3:.2f} kW, "
        f"{loss * h / 1e6:.1f} MWh/yr",
        "  rectifier + battery + inverter: the load sees clean voltage even",
        "  through a dip, at the price of two conversions all the time",
        "  the input filter of the rectifier is the capacitive load that",
        "  can under-excite the backup generator (chapter 8)"])


def machine_side() -> None:
    e_rated, n_rated = 690.0, 1155.0                             # A-111
    lines = ["machine-side converter: generator EMF against the DC link"
             " (A-111):",
             "  speed   EMF (line)   DC needed (SVPWM)"]
    for k in (0.5, 1.0, 1.15):
        e = e_rated * k
        lines.append(f"  {k * n_rated:5.0f} rpm  {e:8.0f} V  {pe.vdc_min(e):12.0f} V")
    lines += ["  at 15 % overspeed the EMF needs about 1122 V: almost all of a",
              "  1150 V link; above it the converter must weaken the field",
              "  (chapter 8) or the generator drives current into the link",
              "  through the diodes, uncontrolled"]
    emit("y_machineside", lines)


def cap_life() -> None:
    l0, t0 = 100e3, 70.0                                         # A-176
    lines = ["film capacitor life (teaching law, A-176):",
             "  L = L0 x 2^((T0 - T)/10) x (V0/V)^7",
             "  L0 100,000 h at 70 C hot spot and rated voltage"]
    for t, v in ((60, 1.0), (70, 1.0), (80, 1.0), (85, 1.0), (70, 1.1)):
        life = l0 * 2 ** ((t0 - t) / 10) * (1 / v) ** 7
        lines.append(f"  hot spot {t} C, voltage x {v:.1f}: {life:9,.0f} h "
                     f"({life / 8760:5.1f} years at full stress)")
    lines += ["  ten kelvin halve the life and ten per cent overvoltage halves",
              "  it again: the ripple current (heat) and the DC voltage window",
              "  of section B set the capacitor's life"]
    emit("y_caplife", lines)


def eff_uncertainty() -> None:
    p_in, eta = 5.08e6, 0.984                                    # A-177
    p_out = p_in * eta
    for u_rel in (0.001, 0.0005):
        u_eta = eta * math.sqrt(2) * u_rel
        loss = p_in - p_out
        u_loss = math.sqrt((p_in * u_rel) ** 2 + (p_out * u_rel) ** 2)
        if u_rel == 0.001:
            lines = ["efficiency from input and output power (A-177):",
                     f"  P_in {p_in / 1e6:.2f} MW, efficiency {eta}: loss "
                     f"{loss / 1e3:.1f} kW"]
        lines.append(f"  meters +-{100 * u_rel:.2f} % each: efficiency "
                     f"+-{100 * u_eta:.3f} %, loss +-{u_loss / 1e3:.1f} kW "
                     f"({100 * u_loss / loss:.0f} % of the loss)")
    lines += ["  the loss is the small difference of two large numbers: its",
              "  relative uncertainty is large; summing measured component",
              "  losses or a calorimetric method measures it directly"]
    emit("y_effunc", lines)


if __name__ == "__main__":
    harmonics_poc()
    impedance()
    ups()
    machine_side()
    cap_life()
    eff_uncertainty()
