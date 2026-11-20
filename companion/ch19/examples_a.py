"""Chapter 19, section A - electrochemical and system fundamentals: the
cell's energy and OCV curves (LFP against NMC), discharge at four
C-rates, round-trip efficiency from the cell to the AC side, SOC
estimation by coulomb counting and an OCV reset, and calendar and cycle
fade.

Run from the project root:   python -m companion.ch19.examples_a
Writes companion/ch19/expected/a_*.txt and diagrams/data/ch19-*.csv.
Teaching values A-290 to A-292.
"""
from __future__ import annotations

import numpy as np

from companion.ch19 import sources as src
from companion.ch19.common import csv, emit
from plantp import storage as st

C = src.LFP


def cell() -> None:
    e_lfp = C.q_ah * src.V_NOM["LFP"] / 1000
    e_nmc = src.NMC.q_ah * src.V_NOM["NMC"] / 1000
    lines = ["the two teaching cells (A-290):",
             f"  LFP prismatic {C.q_ah:.0f} Ah x {src.V_NOM['LFP']} V = {e_lfp:.3f} kWh;"
             f" window {C.v_min}-{C.v_max} V",
             f"  NMC prismatic {src.NMC.q_ah:.0f} Ah x {src.V_NOM['NMC']} V = {e_nmc:.3f} kWh;"
             f" window {src.NMC.v_min}-{src.NMC.v_max} V",
             "  OCV against SOC (V) and its slope (mV per % SOC):",
             "  SOC %    LFP     NMC    LFP slope  NMC slope"]
    rows = []
    for s in (0.05, 0.1, 0.2, 0.5, 0.8, 0.9, 0.95):
        lines.append(f"  {100 * s:5.0f}  {float(st.ocv(s)):6.3f}  {float(st.ocv(s, 'NMC')):6.3f}"
                     f"     {10 * float(st.ocv_slope(s)):6.2f}     {10 * float(st.ocv_slope(s, 'NMC')):6.2f}")
    for s in np.linspace(0, 1, 101):
        rows.append((f"{100 * s:.0f}", f"{float(st.ocv(s)):.4f}", f"{float(st.ocv(s, 'NMC')):.4f}"))
    lines += ["  LFP is flat between about 20 and 80 %: about 1 mV per %;",
              "  its voltage says little about its SOC there (section A3)"]
    emit("a_cell", lines)
    csv("ch19-ocv.csv", "soc,lfp,nmc", rows)


def rates() -> None:
    lines = ["LFP cell discharged from full at four C-rates (A-290):",
             "  C-rate  current A  Ah out  Wh out  mean V  Wh vs 0.25 C"]
    grid = np.linspace(0, 314, 158)
    cols, base = [], None
    for cr in (0.25, 0.5, 1.0, 2.0):
        d = st.discharge(C, cr)
        base = base or d["wh"]
        lines.append(f"  {cr:6.2f}  {cr * C.q_ah:9.0f}  {d['ah']:6.1f}  {d['wh']:6.0f}"
                     f"  {d['v_mean']:6.3f}  {100 * d['wh'] / base:6.1f} %")
        ah = np.arange(1, len(d["v"]) + 1) * cr * C.q_ah * 10 / 3600
        cols.append(np.interp(grid, ah, d["v"], right=np.nan))
    rows = [(f"{g:.1f}",) + tuple("nan" if np.isnan(c[k]) else f"{c[k]:.4f}" for c in cols)
            for k, g in enumerate(grid)]
    lines += ["  the cell gives its full charge at every rate here, but at a",
              "  lower voltage: energy, not charge, falls with power"]
    emit("a_rates", lines)
    csv("ch19-discharge.csv", "ah,c025,c05,c1,c2", rows)


def efficiency() -> None:
    lines = ["round trip from the cell to the AC side (10-90 % SOC):",
             "  C-rate  cell DC   with PCS 0.98 twice  with MV and aux"]
    for cr in (0.25, 0.5, 1.0):
        dc = st.round_trip(C, cr)
        ac = dc * src.PCS_ETA ** 2
        full = ac * src.MV_ETA ** 2 * (1 - src.AUX_SHARE)
        lines.append(f"  {cr:6.2f}  {100 * dc:6.2f} %     {100 * ac:6.2f} %"
                     f"          {100 * full:6.2f} %")
    lines += [f"  data pack S1: {100 * src.S1['rt_ac']:.0f} % AC to AC, below the model's 0.5 C",
              "  figure: it also covers HVAC in hot hours, standby and no-load",
              "  losses (a conservative teaching value); the I^2R loss grows",
              "  with current, so a slower battery is a more efficient one"]
    emit("a_efficiency", lines)


def soc_estimate() -> None:
    """Thirty days of one cycle a day at 0.5 C; current sensor offset."""
    i_day = np.concatenate([np.full(80, 0.5 * C.q_ah), np.zeros(40),
                            np.full(80, -0.5 * C.q_ah), np.zeros(88)])
    cur = np.tile(i_day, 30)                         # 5-minute steps
    dt = 300.0
    true = st.coulomb_count(cur, dt, C.q_ah, 0.9)
    lines = ["SOC from coulomb counting with a current-sensor error",
             "  (one cycle a day at 0.5 C, no reset):",
             "  sensor error           after 1 day   7 days   30 days"]
    for name, bias, gain in (("offset 0.05 A", 0.05, 1.0), ("offset 0.5 A", 0.5, 1.0),
                             ("gain +0.5 %", 0.0, 1.005)):
        est = st.coulomb_count(cur, dt, C.q_ah, 0.9, bias_a=bias, gain=gain)
        e = [100 * abs(est[288 * d - 1] - true[288 * d - 1]) for d in (1, 7, 30)]
        lines.append(f"  {name:20s}  {e[0]:9.2f} %  {e[1]:6.1f} %  {e[2]:6.1f} %")
    lines += ["  an offset adds up every hour; a gain error cancels over a",
              "  cycle with equal charge and discharge, but not over a day of",
              "  charging only"]
    lines += ["  an OCV reset at rest removes the drift, if the curve is steep:",
              "  voltage error 2 mV gives an SOC error of"]
    for chem in ("LFP", "NMC"):
        e = [0.002 / float(st.ocv_slope(s, chem)) for s in (0.15, 0.5)]
        lines.append(f"    {chem}: {100 * e[0]:5.1f} % at 15 % SOC, {100 * e[1]:5.1f} % at 50 % SOC")
    lines += ["  LFP must be reset near the ends of its window (or by a full",
              "  charge), NMC anywhere: the BMS design follows the chemistry"]
    emit("a_soc", lines)


def fade() -> None:
    f = src.FADE
    lines = ["calendar fade (storage) by temperature and mean SOC (A-292):",
             "  years   15 C/50 %   25 C/50 %   35 C/50 %   25 C/90 %"]
    rows = []
    for y in (1, 5, 10, 15, 20):
        v = [float(st.calendar_fade(y, t, s, f["k25"], f["ea_ev"]))
             for t, s in ((15, 0.5), (25, 0.5), (35, 0.5), (25, 0.9))]
        lines.append(f"  {y:5d}   " + "   ".join(f"{100 * x:8.1f} %" for x in v))
    for y in np.linspace(0, 20, 41):
        v = [float(st.calendar_fade(y, t, 0.5, f["k25"], f["ea_ev"])) for t in (15, 25, 35)]
        rows.append((f"{y:.1f}",) + tuple(f"{100 * x:.2f}" for x in v))
    lines += ["cycle fade per 365 cycles a year by depth (A-292):",
              "  depth   cycles to end of life   loss per year"]
    for d in (0.2, 0.5, 0.8, 1.0):
        n_life = f["n100"] * d ** -f["k"]
        loss = st.cycle_fade([(d, 365)], f["n100"], f["k"], f["loss_at_life"])
        lines.append(f"  {100 * d:4.0f} %   {n_life:20,.0f}   {100 * loss:9.2f} %")
    lines += ["  heat roughly doubles calendar fade every 10-12 K here; deep",
              "  cycles cost more than their energy share; both shapes are",
              "  teaching laws and the warranty curve of the maker governs"]
    emit("a_fade", lines)
    csv("ch19-fade.csv", "y,t15,t25,t35", rows)


if __name__ == "__main__":
    cell()
    rates()
    efficiency()
    soc_estimate()
    fade()
