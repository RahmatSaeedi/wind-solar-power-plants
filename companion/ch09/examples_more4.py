"""Chapter 9 - overmodulation, DC offset from current sensing, positive and
negative sequence currents in an unbalanced dip, and the sensitivity of the
DC-window result to the PV model assumptions.

Run from the project root:   python -m companion.ch09.examples_more4
Writes companion/ch09/expected/w_*.txt and diagrams/data/ch09-*.csv.
Teaching values A-180 .. A-182 (fictional); data pack 1.1.0 (S0).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch09.common import csv, emit
from plantp import datapack, mppt as mp, pe

S3 = math.sqrt(3)


def overmodulation() -> None:
    lines = ["two-level leg, carrier 51 x 50 Hz: line voltage against m:",
             "     m   fundamental / linear   5th+7th %   with 3rd-harmonic injection"]
    rows = []
    for m in (0.6, 0.8, 1.0, 1.1, 1.155, 1.27):
        res = []
        for third in (0.0, 1 / 6):
            _, sa = pe.spwm_leg(m, 50, 2550, 51000, third=third)
            _, sb = pe.spwm_leg(m, 50, 2550, 51000, third=third, phase_deg=-120)
            h, a = pe.spectrum(sa - sb, 50)
            lin = m * S3 / 2
            low = math.hypot(a[5], a[7]) / a[1]
            res.append((a[1] / lin, 100 * low))
        rows.append((m, f"{res[0][0]:.3f}", f"{res[0][1]:.2f}",
                     f"{res[1][0]:.3f}", f"{res[1][1]:.2f}"))
        lines.append(f"  {m:5.3f}   {res[0][0]:8.3f}   {res[0][1]:13.2f}   "
                     f"{res[1][0]:10.3f}  ({res[1][1]:.2f} %)")
    lines += ["  above m 1 plain sine-triangle PWM loses fundamental gain and",
              "  creates 5th and 7th; with third-harmonic injection the leg stays",
              "  linear up to 1.155 (the space-vector limit, section A)"]
    emit("w_overmod", lines)
    csv("ch09-overmod.csv", "m,g0,l0,g3,l3", rows)


def dc_offset() -> None:
    i_r = 5.5e6 / (S3 * 600)
    i_m = 0.01 * i_r                                             # A-180
    lines = [f"current-sensor offset and DC into the unit transformer (A-180):",
             f"  rated current {i_r:,.0f} A; magnetising current (1 %) "
             f"{i_m:.0f} A peak-ish"]
    for off in (0.001, 0.002, 0.005):
        i_dc = off * i_r * math.sqrt(2)
        lines.append(f"  offset {100 * off:.1f} % of rated peak: DC {i_dc:5.1f} A ="
                     f" {100 * i_dc / i_m:4.0f} % of the magnetising current")
    lines += ["  a DC current comparable with the magnetising current biases",
              "  the core towards saturation in one half-cycle: noise, heat and",
              "  even-order harmonics; inverters measure and cancel it, and",
              "  grid codes limit DC injection"]
    emit("w_dcoffset", lines)


def sequences() -> None:
    v_p, v_n, i_lim = 0.7, 0.3, 1.1                              # A-181
    lines = [f"unbalanced dip: V+ {v_p} pu, V- {v_n} pu, current limit "
             f"{i_lim} pu (A-181):"]
    th = np.linspace(0, 2 * np.pi, 3600, endpoint=False)
    for name, k in (("positive only", 0.0), ("ripple cancelled", v_n / v_p)):
        peak = 1.0 + k
        i_p = min(1.0, i_lim / peak)
        p_mean = 3 * v_p * i_p * (1 - k * v_n / v_p) / 3
        ripple = abs(v_n * i_p - k * i_p * v_p)
        lines.append(f"  {name:17s} I+ {i_p:.2f}, I- {k * i_p:.2f}, P "
                     f"{p_mean:.2f} pu, 100 Hz ripple {ripple:.2f} pu")
    lines += ["  cancelling the ripple protects the DC link but unbalances the",
              "  phase currents: the current limit then cuts the active power;",
              "  the grid code says which sequence currents it wants in a dip"]
    emit("w_sequences", lines)


def sensitivity() -> None:
    h = datapack.load_hourly()
    g0 = h["ghi_wm2"].to_numpy(dtype=float)
    ta = h["t_air_c"].to_numpy(dtype=float)
    v600, v630 = pe.vdc_min(600, headroom=0.1), pe.vdc_min(630, headroom=0.1)
    cases = [("base (A-153)", 1.0, 45.0, 26), ("irradiance x 1.1", 1.1, 45.0, 26),
             ("NOCT 48 C", 1.0, 48.0, 26), ("27 modules", 1.0, 45.0, 27)]
    lines = ["sensitivity of the window result to model assumptions (A-182):",
             "  case                 630 V: hours  share     600 V: hours  share"]
    for name, kg, noct, n_mod in cases:
        g = g0 * kg
        tc = mp.cell_temperature(ta, g, noct)
        res = {v600: [0, 0.0], v630: [0, 0.0]}
        tot = 0.0
        for k in np.flatnonzero(g >= 20):
            c = mp.PVM_550.at(g[k], tc[k], n_mod)
            v, p = c.mpp(400)
            tot += p
            for v_min, r in res.items():
                if v < v_min:
                    r[0] += 1
                    r[1] += p - float(c.p(v_min))
        a, b = res[v630], res[v600]
        lines.append(f"  {name:20s} {a[0]:6d}  {100 * a[1] / tot:6.3f} %"
                     f"   {b[0]:6d}  {100 * b[1] / tot:6.3f} %")
    lines += ["  hotter cells (more irradiance on the tilted plane, higher NOCT)",
              "  push more hours below the floor; one more module per string",
              "  lifts the voltage but must be checked against 1500 V in the",
              "  cold (chapter 6): D-012 at 600 V keeps its margin in all cases"]
    emit("w_sensitivity", lines)


if __name__ == "__main__":
    overmodulation()
    dc_offset()
    sequences()
    sensitivity()
