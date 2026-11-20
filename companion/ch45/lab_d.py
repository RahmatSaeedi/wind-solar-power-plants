"""Chapter 45, lab D: the evidence chain - an educational SOC simulator
run through a day with its invariants checked, what a receiving sample can
and cannot find in a lot, how a shortened rest test lets leakers through,
how a leaker shows in the BMS's balancing, and the trail of one fictional
defect from receiving to the records.

Run from the project root:   python -m companion.ch45.lab_d
Writes companion/ch45/expected/d_*.txt and diagrams/data/ch45-*.csv.
Educational simulations; nothing here is a BMS (A-478, A-481).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch45 import sources as src
from companion.ch45.common import csv, emit
from plantp import cellmfg as cf
from plantp import storage as st

C, B, D = src.CELL, src.BUILD, src.DEFECT


# ------------------------------------------------ 1. SOC simulator and invariants
# [start: day]
def day_profile(rack_kw: float = 20000.0 / 96) -> list[float]:
    """Rack current (A) for 24 hours in 15-minute steps: charge at midday,
    discharge in the evening, a long charge that runs into the window."""
    v = B["s_module"] * B["m_rack"] * C["v_nom"]
    i = []
    for k in range(96):
        h = k / 4
        if 10 <= h < 13:
            i.append(+rack_kw * 1000 / v)            # charge
        elif 18 <= h < 20:
            i.append(-rack_kw * 1000 / v)            # discharge
        else:
            i.append(0.0)
    return i
# [end: day]


def soc_day(soc0: float = 0.30) -> dict:
    sim = cf.SocSim(q_ah=C["q_ah"], soc=soc0)
    prof = day_profile()
    socs, taken = [], []
    for i in prof:
        taken.append(sim.step(i, 900.0))
        socs.append(sim.soc)
    csv("ch45-soc.csv", "h,soc,req,got",
        [(k / 4, round(s, 4), round(r, 1), round(t, 1))
         for k, (s, r, t) in enumerate(zip(socs, prof, taken))])
    err = sim.balance_error(soc0)
    cut_c = sum(1 for r, t in zip(prof, taken) if r > 0 and t < r - 1e-9)
    cut_d = sum(1 for r, t in zip(prof, taken) if r < 0 and t > r + 1e-9)
    lines = [f"one rack through a day, 15-minute steps, start at {soc0:.0%} SOC",
             "  (educational simulator): 3 h of charge asked at midday, 2 h of",
             "  discharge in the evening",
             f"  rack current while charging/discharging: {max(prof):.0f} A "
             f"({max(prof) / C['q_ah']:.2f} C)",
             f"  SOC: lowest {min(socs):.3f}, highest {max(socs):.3f}, end "
             f"{socs[-1]:.3f} (window {sim.lo}-{sim.hi})",
             f"  charge in {sim.ah_in:.1f} Ah, out {sim.ah_out:.1f} Ah, refused "
             f"{sim.refused_ah:.1f} Ah",
             f"  steps cut: {cut_c} while charging, {cut_d} while discharging",
             f"  invariant, charge balance error: {err:.2e} Ah",
             "  the simulator never leaves the window: the end of the charge",
             "  and of the discharge are cut, and each cut is logged - the",
             "  tests check the invariant and the edges on every version"]
    emit("d_soc", lines)
    return dict(lo=min(socs), hi=max(socs), err=err, refused=sim.refused_ah,
                cut_c=cut_c, cut_d=cut_d)


# ------------------------------------------------ 2. a receiving sample
def receiving(n_lot: int = 2000, bad: int = 5, target: float = 0.90) -> dict:
    def p_find(n: int) -> float:
        return 1 - math.comb(n_lot - bad, n) / math.comb(n_lot, n)
    need = next(n for n in range(1, n_lot) if p_find(n) >= target)
    lines = [f"lot of {n_lot} cells with {bad} slow leakers; the integrator rests",
             "  a sample and measures K",
             "  sample   chance to find at least one leaker"]
    out = {}
    for n in (20, 50, 200, 500):
        out[n] = p_find(n)
        lines.append(f"  {n:6d}   {p_find(n):10.1%}")
    lines += [f"  {need} cells for {target:.0%}: a receiving sample cannot screen "
              "a lot",
              "  for rare defects - the cell maker's rest test of every cell",
              "  is the screen, and its data file comes with the lot; the",
              "  sample checks the file, not the cells"]
    emit("d_receiving", lines)
    return dict(p50=out[50], need=need)


# ------------------------------------------------ 3. a shortened rest test
def rest_test(limit: float = 0.06, res_mv: float = 0.05) -> dict:
    lot = src.lot()
    leaks = [float(lot["k"][i]) for i in lot["leak"]]
    n = len(lot["k"])
    lines = [f"rest test: K = OCV drop / days; each reading sd {res_mv} mV, "
             f"limit {limit} mV/day",
             "  rest days   K noise sd   leakers caught   good cells flagged",
             "                mV/day       (of 5)"]
    out = {}
    for days in (14, 7, 3):
        sd = math.sqrt(2) * res_mv / days
        caught = sum(0.5 * math.erfc((limit - k) / (sd * math.sqrt(2)))
                     for k in leaks)
        good_sd = math.sqrt(0.006 ** 2 + sd ** 2)
        false = 0.5 * math.erfc((limit - 0.030) / (good_sd * math.sqrt(2)))
        out[days] = (sd, caught, false * n)
        lines.append(f"  {days:9d}   {sd:10.4f}   {caught:14.1f}   "
                     f"{false * n:18.1f}")
    lines += ["  halving the rest halves the time a leaker has to show and",
              "  doubles the noise of the reading: leakers slip through and",
              "  good cells are flagged - the rest time is a process",
              "  parameter with its own record, not a scheduling convenience"]
    emit("d_rest", lines)
    return out


# ------------------------------------------------ 4. a leaker in the BMS
def leak_current(k_mv_day: float, soc: float = 0.5) -> float:
    """Self-discharge current (mA) that gives an OCV drop of k a day."""
    slope = float(st.ocv_slope(soc))                       # V per unit SOC
    d_soc_day = k_mv_day / 1000 / slope
    return d_soc_day * C["q_ah"] / 24 * 1000


def balancing(k_normal: float = 0.030, k_leak: float = 0.064,
              i_bal_ma: float = 100.0) -> dict:
    """A leaker as weak as the lowest of lot L4506 - the kind most likely
    to pass a shortened rest test (cell L4507-0412 of the trail)."""
    i_n, i_l = leak_current(k_normal), leak_current(k_leak)
    extra = i_l - i_n
    duty = extra / i_bal_ma
    days_30 = 30.0 / (k_leak - k_normal)
    lines = [f"a leaking cell in a module (K {k_leak} against {k_normal} mV/day, "
             "LFP at 50 % SOC)",
             f"  self-discharge: normal {i_n:.1f} mA, leaker {i_l:.1f} mA, extra "
             f"{extra:.1f} mA",
             f"  passive balancing ({i_bal_ma:.0f} mA bleed on the other cells) "
             f"must run {duty:.0%} of the time",
             f"  without balancing the leaker falls 30 mV behind in "
             f"{days_30:.0f} days of rest",
             "  the BMS keeps the string even and so hides the leaker; what",
             "  shows it is the balancing duty of one module against its",
             "  peers - a signal the monitoring must export (ch 37)"]
    emit("d_balance", lines)
    return dict(extra=extra, duty=duty, days=days_30)


# ------------------------------------------------ 5. the trail of one defect
TRAIL = [   # step, should record, did record, verdict
    ("cell maker: rest test", "14-day K of every cell", "7-day K for L4507",
     "deviation"),
    ("cell maker: lot release", "K file with the lot", "file sent", "ok"),
    ("integrator: receiving", "sample checks the file",
     "rest time not read; 50 cells, no find", "blind"),
    ("integrator: module build", "cell IDs per module", "recorded", "ok"),
    ("integrator: BMS config", "limits = cell data", "t_charge_max 58 C",
     "deviation"),
    ("site acceptance", "OCV spread after rest", "not in the test plan", "gap"),
    ("operation, month 3", "balancing duty by module", "duty of 1 module high",
     "signal"),
    ("incident learning", "trace to lot and cells", "L4507-0412 in C5-R03-M2",
     "ok"),
    ("lifecycle record", "replacements, cause, lot", "updated", "ok"),
]


def trail() -> dict:
    counts = {}
    lines = [f"fictional defect: lot {D['lot']}, {D['cause']};",
             "  followed through the records",
             "  step                       should record",
             "    recorded -> verdict"]
    for step, should, did, verdict in TRAIL:
        counts[verdict] = counts.get(verdict, 0) + 1
        lines.append(f"  {step:26s} {should}")
        lines.append(f"    {did} -> {verdict}")
    lines += ["  " + ", ".join(f"{k} {v}" for k, v in counts.items()),
              "  two deviations (rest time, a BMS limit), a blind sample and",
              "  one gap (no OCV check at acceptance) let the defect reach the",
              "  site; the records let it be traced in hours once it showed"]
    emit("d_trail", lines)
    return counts


if __name__ == "__main__":
    soc_day()
    receiving()
    rest_test()
    balancing()
    trail()
