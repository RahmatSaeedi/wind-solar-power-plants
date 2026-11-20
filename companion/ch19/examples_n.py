"""Chapter 19, last lessons: reversible (entropic) heat beside Joule
heat, a frequency-response duty and the SOC headroom it needs, the
PCS efficiency at part load and its effect on the round trip, the
thermal path from cell to cold plate, ageing in a warehouse before
commissioning, a first look at the battery's economics, detector
availability with proof tests, the time budget from detection to rack
isolation, and second-life screening.

Run from the project root:   python -m companion.ch19.examples_n
Writes companion/ch19/expected/n_*.txt and diagrams/data/ch19-*.csv.
Teaching values A-290 to A-297.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch10.integrated import EFF_POINTS
from companion.ch19 import sources as src
from companion.ch19.common import csv, emit
from plantp import pe, storage as st
from plantp.yieldrisk import annuity

C, F = src.LFP, src.FADE


def entropic() -> None:
    """q_rev = I T dU/dT with a teaching dU/dT (A-297)."""
    i, t = 157.0, 298.15                               # 0.5 C, 25 C
    joule = i ** 2 * (C.r0 + C.r1)
    lines = ["reversible against Joule heat of one cell at 0.5 C, 25 C (A-297):",
             "  SOC %   dU/dT mV/K   reversible W   Joule W   share"]
    for soc, dudt in ((0.1, -0.15), (0.5, 0.05), (0.9, -0.05)):
        q = i * t * dudt / 1000
        lines.append(f"  {100 * soc:5.0f}   {dudt:10.2f}   {q:+12.2f}   {joule:7.2f}"
                     f"   {100 * abs(q) / joule:4.0f} %")
    lines += ["  reversible heat changes sign with the direction of current",
              "  and with SOC; over a full cycle it nearly cancels, while",
              "  Joule heat always adds; a thermal model of an hour at the",
              "  ends of the window should carry both"]
    emit("n_entropic", lines)


# [start: freq]
def freq_response(p_max: float = 10.0, hours: int = 24, seed: int = 197):
    """A zero-mean frequency-response signal (minute steps, slowly
    varying) on the battery: energy throughput and SOC wander."""
    rng = np.random.default_rng(seed)
    n = hours * 60
    x = np.zeros(n)
    for k in range(1, n):                       # first-order random signal
        x[k] = 0.9 * x[k - 1] + 0.2 * rng.normal()
    p = np.clip(x, -1, 1) * p_max               # MW, + discharge
    eta = math.sqrt(0.86)
    e = np.cumsum(np.where(p > 0, -p / eta, -p * eta)) / 60.0   # MWh
    return p, e
# [end: freq]


def frequency() -> None:
    p, e = freq_response()
    eta = math.sqrt(0.86)
    dis = np.clip(p, 0, None).sum() / 60
    chg = np.clip(-p, 0, None).sum() / 60
    loss = dis * (1 / eta - 1) + chg * (1 - eta)
    lines = ["a day of frequency response at up to +-10 MW (teaching, A-297):",
             f"  energy through the battery {dis + chg:,.0f} MWh"
             f" ({(dis + chg) / 2 / 32.1:.2f} full cycles of the usable window)",
             f"  stored energy wanders from {e.min():+.1f} to {e.max():+.1f} MWh",
             f"  end of day {e[-1]:+.1f} MWh = signal's net charge {chg - dis:+.1f}"
             f" less losses {loss:.1f} MWh",
             "  the signal is zero on average only over long times; in a day",
             "  its imbalance and the losses move the SOC, so the service",
             "  needs headroom both ways and a slow correction that the",
             "  rules of the service must allow (chapter 20)"]
    emit("n_freq", lines)
    csv("ch19-freq.csv", "h,e", [(f"{k / 60:.2f}", f"{e[k]:.3f}") for k in range(0, len(e), 10)])


def pcs_partload() -> None:
    c = pe.fit_loss_coeffs(EFF_POINTS)
    lines = ["round trip at part load: cells at their rate, PCS on its curve",
             "  (the chapter 9-10 inverter curve, used here for the PCS):",
             "  power MW   PCS one way   cells DC   AC round trip"]
    rows = []
    for mw in (2.0, 5.0, 10.0, 20.0):
        eta_pcs = float(pe.efficiency_from_coeffs(mw / 20.0, c))
        cr = mw / 40.0
        rt_cell = st.round_trip(C, cr)
        rt = rt_cell * eta_pcs ** 2
        lines.append(f"  {mw:8.0f}   {eta_pcs:11.4f}   {rt_cell:8.4f}   {100 * rt:10.2f} %")
        rows.append((mw, f"{100 * rt:.2f}"))
    lines += ["  at low power the PCS's fixed losses dominate and the round",
              "  trip falls although the cells are more efficient; a",
              "  battery that idles at small power loses on both counts"]
    emit("n_partload", lines)
    csv("ch19-partload.csv", "mw,rt", rows)


def thermal_path() -> None:
    q = 157.0 ** 2 * (C.r0 + C.r1)
    lines = ["cell temperature above the cold plate at 0.5 C (teaching):",
             "  path resistance K/W   rise K"]
    for r_th in (0.3, 0.6, 1.2):
        lines.append(f"  {r_th:19.1f}   {q * r_th:6.1f}")
    lines += [f"  (heat {q:.1f} W a cell)",
              "  a poor thermal pad or a gap doubles the rise; the spread",
              "  between cells (section B) comes from these paths"]
    emit("n_path", lines)


def warehouse() -> None:
    lines = ["calendar fade while waiting for commissioning (A-292):",
             "  months   at 15 C, 30 %   at 25 C, 50 %   at 35 C, 50 %"]
    for m in (3, 6, 12):
        y = m / 12
        v = [float(st.calendar_fade(y, t, s, F["k25"], F["ea_ev"]))
             for t, s in ((15, 0.3), (25, 0.5), (35, 0.5))]
        lines.append(f"  {m:6d}   " + "   ".join(f"{100 * x:12.2f} %" for x in v))
    lines += ["  a year in a hot yard costs about as much health as a year",
              "  of work; delivery, storage SOC and shade are contract terms"]
    emit("n_warehouse", lines)


def economics() -> None:
    capex = 40.13 * 250.0 + 20.0 * 150.0                 # k u (A-293)
    yearly = capex / annuity(0.06, 15) + 0.02 * capex
    lines = ["a first look at the battery's money (teaching, A-293; chapter 21):",
             f"  capex {capex:,.0f} k u; yearly at 6 %, 15 years, plus 2 % opex: {yearly:,.0f} k u",
             "  shifting value of a year: 371 k u (fixed prices) to 455 k u",
             "    (daily prices, optimum)",
             f"  shifting pays {100 * 455 / yearly:.0f} % of the yearly cost at best",
             "  shifting alone does not pay for this battery at these prices;",
             "  capacity payments, services or a larger spread must; chapter 21",
             "  prices them and the owner decides whether S1 is built"]
    emit("n_money", lines)


# [start: detector]
def unavailability(lam_per_yr: float, test_months: float, n: int = 1) -> float:
    """Mean unavailability of n redundant detectors (any one suffices)
    with failures found only at the proof test: (lam T)^n / (n + 1)."""
    lt = lam_per_yr * test_months / 12.0
    return lt ** n / (n + 1)
# [end: detector]


def detectors() -> None:
    lines = ["a gas detector that fails silently, found at the proof test",
             "  (failure rate 0.05 a year, teaching A-297):",
             "  test interval   one detector   two detectors (1 of 2)"]
    for mths in (3, 6, 12):
        lines.append(f"  {mths:8d} months   {100 * unavailability(0.05, mths):11.2f} %"
                     f"   {100 * unavailability(0.05, mths, 2):20.4f} %")
    lines += ["  testing more often and adding a second detector both cut the",
              "  time the protection is silently missing; the test interval",
              "  is a maintenance requirement with an owner (chapter 52)"]
    emit("n_detector", lines)


def isolation_budget() -> None:
    steps = [("BMS sees the cell outside its limit (scan)", 1.0),
             ("rack controller decides (logic, filter)", 0.5),
             ("rack switch opens", 0.05),
             ("message reaches the plant controller", 1.0),
             ("plant controller stops the PCS and HVAC as designed", 2.0)]
    lines = ["time budget from detection to isolation (teaching, A-297):",
             "  step                                                seconds"]
    t = 0.0
    for name, s in steps:
        t += s
        lines.append(f"  {name:51s} {s:6.2f}")
    lines += [f"  total {t:.2f} s; the rack opens locally in about 1.6 s without",
              "  waiting for the network; actions that need the network come",
              "  later and must not be needed for the first protection"]
    emit("n_isolation", lines)


def second_life() -> None:
    rng = np.random.default_rng(1990)
    h15 = rng.normal(0.727, 0.035, 768)             # module health at year 15
    ok = (h15 >= 0.70).mean()
    lines = ["second-life screening of the 768 modules at year 15 (teaching):",
             f"  mean health {100 * h15.mean():.1f} %, spread {100 * h15.std():.1f} points",
             f"  modules at or above 70 %: {100 * ok:.0f} %",
             "  each needs its records (history, events), a capacity and",
             "  resistance test and a buyer who accepts them: traceability",
             "  from the factory pays again at the end"]
    emit("n_second", lines)


if __name__ == "__main__":
    entropic()
    frequency()
    pcs_partload()
    thermal_path()
    warehouse()
    economics()
    detectors()
    isolation_budget()
    second_life()
