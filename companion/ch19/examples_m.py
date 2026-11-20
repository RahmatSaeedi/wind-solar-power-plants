"""Chapter 19, closing lessons: constant-current constant-voltage
charging and why the window stops short of full, the container when one
of two HVAC units fails, how long passive balancing takes, spare modules
by Poisson demand, the uncertainty of health after ten years (Monte
Carlo on the fade laws), the bases of 'a cycle', which fade dominates
for a duty, the energy given up to SOC uncertainty, and the cost of
holding a reserve for the critical-load island.

Run from the project root:   python -m companion.ch19.examples_m
Writes companion/ch19/expected/m_*.txt and diagrams/data/ch19-*.csv.
Teaching values A-290 to A-296.
"""
from __future__ import annotations

import math

import numpy as np
from scipy.stats import poisson

from companion.ch19 import lab_d, sources as src
from companion.ch19.common import csv, emit
from plantp import storage as st
from plantp.wind import rainflow

C, F = src.LFP, src.FADE


# [start: cccv]
def cccv(cell: st.Cell, c_rate: float, soc0: float = 0.1,
         i_end: float = 0.05, dt: float = 10.0):
    """Charge at constant current until v_max, then hold v_max while the
    current tapers to i_end (C-rate). Returns minutes in each phase and
    the SOC reached."""
    soc, v1, t_cc, t_cv = soc0, 0.0, 0.0, 0.0
    a = math.exp(-dt / (cell.r1 * cell.c1))
    i = -c_rate * cell.q_ah
    while soc < 0.999:
        v = float(st.ocv(soc, cell.chem)) - cell.r0 * i - v1
        if v >= cell.v_max:
            # constant voltage: current that holds the terminal at v_max
            i = -max((cell.v_max - float(st.ocv(soc, cell.chem)) + v1)
                     / cell.r0, 0.0)
            if -i < i_end * cell.q_ah:
                break
            t_cv += dt
        else:
            t_cc += dt
        soc -= i * dt / 3600.0 / cell.q_ah
        v1 = a * v1 + (1.0 - a) * cell.r1 * i
    return t_cc / 60, t_cv / 60, soc
# [end: cccv]


def charging() -> None:
    lines = ["constant-current constant-voltage charge from 10 % (stop at",
             "  0.05 C; LFP to 3.6 V, NMC to 4.2 V):",
             "  cell  C-rate   CC minutes   CV minutes   SOC when CV starts/ends"]
    for cell in (C, src.NMC):
        for cr in (0.25, 0.5, 1.0):
            cc, cv, s_end = cccv(cell, cr)
            s_cv = 0.1 + cr * cc / 60
            lines.append(f"  {cell.chem:4s}  {cr:6.2f}   {cc:10.0f}   {cv:10.0f}"
                         f"   {100 * min(s_cv, s_end):5.1f} / {100 * s_end:5.1f} %")
    lines += ["  the flat LFP curve with a low resistance reaches full charge",
              "  almost entirely at constant current; NMC reaches its voltage",
              "  limit early at higher rates and spends a long slow tail at",
              "  constant voltage; stopping at 90 % skips the tail and keeps",
              "  the cells off the high-voltage end where they age faster"]
    emit("m_cccv", lines)


def cccv_trace() -> None:
    """Plot data: NMC cell charged at 1 C from 10 %, voltage and current
    (C-rate) every minute."""
    cell = src.NMC
    dt = 10.0
    soc, v1, t = 0.1, 0.0, 0.0
    a = math.exp(-dt / (cell.r1 * cell.c1))
    i = -1.0 * cell.q_ah
    rows = []
    while soc < 0.999:
        v = float(st.ocv(soc, cell.chem)) - cell.r0 * i - v1
        if v >= cell.v_max:
            i = -max((cell.v_max - float(st.ocv(soc, cell.chem)) + v1)
                     / cell.r0, 0.0)
            v = cell.v_max
            if -i < 0.05 * cell.q_ah:
                break
        if int(t) % 60 == 0:
            rows.append((f"{t / 60:.1f}", f"{v:.4f}", f"{-i / cell.q_ah:.3f}",
                         f"{100 * soc:.2f}"))
        soc -= i * dt / 3600.0 / cell.q_ah
        v1 = a * v1 + (1.0 - a) * cell.r1 * i
        t += dt
    csv("ch19-cccv.csv", "t,v,c,soc", rows)


def hvac_n1() -> None:
    """Two 60 kW units; one fails at the worst hour at end of life."""
    t = src.THERMAL
    q_in = 118.0                                     # kW, b_heat worst hour
    left = 60.0
    rise = (q_in - left) / t["c_kwh_k"]              # K per hour
    to_35 = (35.0 - t["setpoint"]) / rise * 60
    lines = ["one of two 60 kW HVAC units fails at the worst hour (A-291):",
             f"  heat in {q_in:.0f} kW, removed {left:.0f} kW: inside rises {rise:.1f} K an hour",
             f"  from {t['setpoint']:.0f} C to 35 C in about {to_35:.0f} minutes",
             "  the BMS then limits power (state 'limited', fig. states),",
             "  which also cuts the heat; N+1 units (three of 60 kW) keep",
             "  full power through one failure; the choice is a price for",
             "  availability on the hottest days"]
    emit("m_hvac", lines)


def balancing() -> None:
    gap = 0.02 * C.q_ah                              # 2 % of capacity, Ah
    lines = ["passive balancing of a 2 % charge gap (A-294):",
             "  bleed mA   hours of bleeding   days at 2 h a day"]
    for ma in (50, 100, 200):
        h = gap / (ma / 1000)
        lines.append(f"  {ma:8d}   {h:17.0f}   {h / 2:18.0f}")
    lines += ["  balancing only near the top of charge is slow; a cell that",
              "  leaks more than the bleed can return drifts away anyway",
              "  (@exm-ch19-defect); active balancing moves charge instead",
              "  of burning it, at more cost and complexity"]
    lines = [ln.replace("(@exm-ch19-defect)", "(the defect example)") for ln in lines]
    emit("m_balancing", lines)


def module_spares() -> None:
    n_mod = src.BUILD["containers"] * src.BUILD["r_container"] * src.BUILD["m_rack"]
    lines = [f"spare modules ({n_mod} installed; lead time 16 weeks, A-294):",
             "  failures per module-year   mean in lead time   stock for 95 %"]
    for lam in (0.001, 0.002, 0.005):
        m = n_mod * lam * 16 / 52
        lines.append(f"  {lam:24.3f}   {m:17.2f}   {int(poisson.ppf(0.95, m)):14d}")
    lines += ["  a few modules on site turn a weeks-long wait into hours",
              "  and keep a rack out of service only for the swap"]
    emit("m_spares", lines)


def mc_health() -> None:
    """Fade laws with uncertain constants: k25, n100, k each +-30 %
    (lognormal, 1 sd), the lab D duty (A-292)."""
    y = lab_d.year()
    soc = y["soc"] / 40.0
    cyc = rainflow(lab_d.turning(soc))
    rng = np.random.default_rng(1919)
    n = 4000
    k25 = F["k25"] * rng.lognormal(0, 0.3, n)
    n100 = F["n100"] * rng.lognormal(0, 0.3, n)
    kk = F["k"] * rng.lognormal(0, 0.1, n)
    h10 = np.empty(n)
    for i in range(n):
        cal = float(st.calendar_fade(10, 25.0, soc.mean(), k25[i], F["ea_ev"]))
        h10[i] = 1 - cal - 10 * st.cycle_fade(cyc, n100[i], kk[i], F["loss_at_life"])
    p10, p50, p90 = np.percentile(h10, [10, 50, 90])
    lines = ["health after ten years with uncertain fade laws (Monte Carlo, n 4,000):",
             f"  P90 (health exceeded by 90 % of draws) {100 * p10:.1f} %",
             f"  P50 {100 * p50:.1f} %;  P10 {100 * p90:.1f} %",
             f"  chance of falling below 80 %: {100 * (h10 < 0.80).mean():.0f} %",
             "  a sizing on the median leaves about half the cases short;",
             "  augmentation keeps the choice open until measured health",
             "  shows which case the battery is in (chapter 16 for P-values)"]
    emit("m_mc", lines)
    hist, edges = np.histogram(100 * h10, bins=np.arange(60, 96, 1.0))
    csv("ch19-mc.csv", "h,n", [(f"{edges[k] + 0.5:.1f}", int(v)) for k, v in enumerate(hist)])


def cycle_bases() -> None:
    dis_ac = 10817.0
    eta = math.sqrt(0.86)
    rows = [("AC at the POC / nominal 40 MWh", dis_ac / 40.13),
            ("DC from the cells / nominal", dis_ac / eta / 40.13),
            ("DC from the cells / usable 32.1 MWh", dis_ac / eta / 32.1)]
    lines = ["one year of discharge counted as 'cycles' on three bases:",
             "  basis                                  cycles"]
    lines += [f"  {k:38s} {v:7.0f}" for k, v in rows]
    v = [f"{x:.0f}" for _, x in rows]
    lines += [f"  the same year is {v[0]}, {v[1]} or {v[2]} 'cycles': a warranty limit",
              "  in cycles means nothing until its basis is written down"]
    emit("m_bases", lines)


def dominance() -> None:
    lines = ["which fade dominates after ten years (25 C, depth 80 %):",
             "  cycles a day   calendar   cycling   larger"]
    for cpd in (0.25, 0.5, 1.0, 2.0):
        cal = float(st.calendar_fade(10, 25.0, 0.4, F["k25"], F["ea_ev"]))
        cy = st.cycle_fade([(0.8, 3650 * cpd)], F["n100"], F["k"], F["loss_at_life"])
        lines.append(f"  {cpd:11.2f}   {100 * cal:7.1f} %  {100 * cy:7.1f} %   "
                     f"{'calendar' if cal > cy else 'cycling'}")
    lines += ["  a battery used rarely ages by the calendar, a busy one by its",
              "  cycles; the duty decides which fade law matters"]
    emit("m_dominance", lines)


def soc_margin() -> None:
    lines = ["energy given up to the SOC estimate's uncertainty (window 10-90 %):",
             "  SOC error   window kept   usable MWh   lost a year at 365 cycles"]
    for err in (0.01, 0.03, 0.05):
        lo, hi = 0.10 + err, 0.90 - err
        usable = 40.13 * (hi - lo)
        lost = (40.13 * 0.8 - usable) * math.sqrt(0.86) * 365
        lines.append(f"  {100 * err:7.0f} %   {100 * lo:3.0f}-{100 * hi:3.0f} %    {usable:9.1f}"
                     f"   {lost:12,.0f} MWh")
    lines += ["  to keep the cells inside their limits the controller shrinks",
              "  the window by its own uncertainty; a better estimate is",
              "  energy sold every day"]
    emit("m_soc", lines)


def reserve_cost() -> None:
    hold = 0.2 * 10                                  # 10 h of critical load, MWh
    eta = math.sqrt(0.86)
    lost_e = hold * eta * 365
    price = 75.0 - 35.0 / 0.86
    lines = ["holding 2 MWh (10 h of the 200 kW critical load) for the island:",
             f"  usable for shifting falls by {hold:.0f} MWh: {lost_e:,.0f} MWh a year less shifted",
             f"  at a spread of 75 - 35/0.86 = {price:.1f} u/MWh: {lost_e * price / 1000:,.1f} k u a year",
             "  the reserve has a yearly price; resilience is a requirement",
             "  with a cost, and the owner chooses its size (chapter 17)"]
    emit("m_reserve", lines)


if __name__ == "__main__":
    charging()
    cccv_trace()
    hvac_n1()
    balancing()
    module_spares()
    mc_health()
    cycle_bases()
    dominance()
    soc_margin()
    reserve_cost()
