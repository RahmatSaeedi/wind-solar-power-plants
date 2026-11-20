"""Chapter 9 - three integrated Plant P examples: one inverter at one hour
of the data-pack summer day (introductory), the loss and thermal budget of
a 5 MW inverter (intermediate), and the numbers behind its specification
and factory-to-site test plan (integrated).

Run from the project root:   python -m companion.ch09.integrated
Writes companion/ch09/expected/i_*.txt.
Data pack 1.1.0, S0; teaching values A-145 .. A-157, A-165; D-012.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch09 import pvyear
from companion.ch09.common import emit
from companion.ch09.examples_a import DEV_NPC, EFF_POINTS
from companion.ch09.examples_b import STACK
from plantp import datapack, mppt as mp, pe

S2, S3 = math.sqrt(2), math.sqrt(3)
STRINGS_PER_INV = pvyear.N_STRINGS / pvyear.N_INV


def one_hour() -> None:
    day = datapack.load_hourly("day_summer")
    row = day.iloc[13]
    g, ta = float(row["ghi_wm2"]), float(row["t_air_c"])
    tc = float(mp.cell_temperature(ta, g))
    c = mp.PVM_550.at(g, tc, pvyear.N_MOD)
    v, p_str = c.mpp()
    p_dc = p_str * STRINGS_PER_INV * (1 - pvyear.DC_LOSS)
    floor = pe.vdc_min(600, headroom=0.1)
    coeffs = pe.fit_loss_coeffs(EFF_POINTS)
    y = p_dc / 5e6
    for _ in range(20):                             # P_ac + loss(P_ac) = P_dc
        y = p_dc / 5e6 - (coeffs[0] + coeffs[1] * y + coeffs[2] * y * y)
    p_ac = y * 5e6
    i_ac = p_ac / (S3 * 600)
    q_av = math.sqrt(5.5e6 ** 2 - p_ac ** 2)
    emit("i_hour", [
        f"inverter 1 at 13:00 on 23 June (data pack 1.1.0, S0):",
        f"  GHI {g:.0f} W/m2, air {ta:.1f} C -> cell {tc:.1f} C (NOCT rule)",
        f"  string of 26: MPP {v:.0f} V, {p_str / 1e3:.2f} kW; "
        f"{STRINGS_PER_INV:.1f} strings, 3 % DC losses",
        f"  DC power at the inverter {p_dc / 1e6:.3f} MW at {v:.0f} V: "
        f"{p_dc / v:,.0f} A",
        f"  DC window floor for 600 V AC: {floor:.0f} V -> "
        f"{'inside' if v >= floor else 'BELOW'}, margin {v - floor:.0f} V",
        f"  efficiency at {p_dc / 5e6:.2f} pu: "
        f"{p_ac / p_dc:.4f} -> AC {p_ac / 1e6:.3f} MW, loss {(p_dc - p_ac) / 1e3:.0f} kW",
        f"  AC current at 600 V, pf 1: {i_ac:,.0f} A "
        f"({i_ac / 4:,.0f} A per stack)",
        f"  reactive power still available within 5.5 MVA: "
        f"{q_av / 1e6:.2f} Mvar",
    ])


def budget() -> None:
    s, pf = 5.5e6, 0.909                     # full S with P 5 MW
    i_rms = s / 4 / (S3 * 600)
    i_pk = i_rms * S2
    leg = pe.npc_leg_losses(i_pk, 0.95, math.degrees(math.acos(pf)),
                            STACK["v_dc"], STACK["f_sw"], DEV_NPC)
    semi = 4 * 3 * sum(leg.values())
    i_c = pe.dclink_ripple_current_rms(i_rms, 0.95, pf)
    esr = 0.1e-3                                         # A-165, whole bank
    items = [("semiconductors (4 stacks x 3 NPC legs)", semi),
             ("LCL inductors L1 and L2 (copper and core)", 0.0035 * s),
             ("filter damping resistors", 4 * 915.0),
             ("DC-link capacitors (ESR)", 4 * i_c ** 2 * esr),
             ("busbars, cables, contactors", 0.0008 * s),
             ("control, gate drives, sensors", 1.2e3),
             ("fans, pumps, cabinet cooling", 0.0010 * s)]       # A-165
    total = sum(v for _, v in items)
    lines = [f"loss and thermal budget of one 5 MW inverter at 5.5 MVA, pf "
             f"{pf} (A-165):"]
    for name, val in items:
        lines.append(f"  {name:42s} {val / 1e3:6.1f} kW "
                     f"({100 * val / total:4.1f} %)")
    lines += [f"  total {total / 1e3:.1f} kW; efficiency at 5 MW "
              f"{5e6 / (5e6 + total):.4f}"]
    worst = max(leg, key=leg.get)
    r_jc = 0.060                         # K/W per module to coolant, A-165
    t_cool = 45.0
    tj = t_cool + leg[worst] / 2 * r_jc              # two modules share it
    lines += [f"  hottest device {worst}: {leg[worst]:,.0f} W per position, "
              "two modules in parallel,",
              "    R_th junction-to-coolant 0.060 K/W each:",
              f"    mean junction {tj:.0f} C at 45 C coolant,",
              "    plus a ripple of about 10 K at 50 Hz (section A): well below",
              "    the data-sheet limit, a margin for hot days and ageing",
              f"  coolant flow for a 6 K rise: {total / (3600 * 6):.1f} kg/s;"
              " heat to air outside the skid"]
    emit("i_budget", lines)


def test_windows() -> None:
    d = pvyear.hourly()
    p = d["p_dc"] / pvyear.N_INV                      # per inverter, W
    months = np.arange(len(p)) // (24 * 365 / 12)
    lines = ["hours when one inverter could be tested near full power",
             "(DC above 4.5 MW, data-pack year 1.1.0):"]
    counts = []
    for mth in range(12):
        sel = months == mth
        counts.append(int(np.sum(p[sel] >= 4.5e6)))
    names = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
    lines.append("  " + "  ".join(f"{n} {c}" for n, c in zip(names[:6],
                                                           counts[:6])))
    lines.append("  " + "  ".join(f"{n} {c}" for n, c in zip(names[6:],
                                                           counts[6:])))
    lines += [f"  total {sum(counts)} hours a year; a site test at full power",
              "  waits for clear middays, so the factory heat run at full power",
              "  on a test bench carries the thermal proof (FAT), and the site",
              "  test (SAT) checks function, settings and integration"]
    emit("i_tests", lines)


if __name__ == "__main__":
    one_hour()
    budget()
    test_windows()
