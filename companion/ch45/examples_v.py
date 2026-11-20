"""Chapter 45, round v: the cell case's leak tightness over twenty years,
grading near a bin edge with measurement uncertainty, an open sense wire
found by plausibility, how much record a battery keeps, what a rest check
at site can and cannot see, a waiting container drained by its own BMS,
the weight a module puts on its handlers, and the energy counter behind a
warranty.

Run from the project root:   python -m companion.ch45.examples_v
Writes companion/ch45/expected/v_*.txt.
Teaching values (A-474 to A-481).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch45 import lab_d
from companion.ch45 import sources as src
from companion.ch45.common import csv, emit

C, B = src.CELL, src.BUILD


# ------------------------------------------------ 1. leak tightness
def hermetic(years: float = 20.0, allow_mg: float = 50.0) -> dict:
    """Water entering a sealed cell through a leak, proportional to the
    leak rate (teaching: 1e-6 mbar l/s of helium ~ 1 mg of water a year)."""
    lines = [f"water entering one cell over {years:.0f} years by the leak rate "
             "of its case",
             "  (teaching scale: 1e-6 mbar l/s of helium ~ 1 mg of water a year;",
             f"  budget {allow_mg:.0f} mg)",
             "  helium leak rate mbar l/s   water in 20 years mg   verdict"]
    out = {}
    for rate in (1e-8, 1e-7, 1e-6, 1e-5):
        w = rate / 1e-6 * years
        out[rate] = w
        lines.append(f"  {rate:24.0e}   {w:20.1f}   "
                     f"{'within' if w <= allow_mg else 'over'}")
    lines += ["  the case must hold water out for the cell's whole life: the",
              "  leak test after sealing measures a rate, and the limit comes",
              "  from a water budget like this one - the real budget and",
              "  scale are the cell maker's"]
    emit("v_hermetic", lines)
    return out


# ------------------------------------------------ 2. grading near a bin edge
def bin_edge(edge: float = 316.0, u_sd: float = 0.3) -> dict:
    lot = src.lot()
    bad = set(lot["leak"]) | set(lot["high"]) | {lot["bad_record"]}
    caps = np.array([float(c) for i, c in enumerate(lot["cap"]) if i not in bad])
    rng = np.random.default_rng(4510)
    meas = caps + rng.normal(0.0, u_sd, len(caps))
    a_true, a_meas = caps >= edge, meas >= edge
    up = int((~a_true & a_meas).sum())
    down = int((a_true & ~a_meas).sum())
    guard = meas >= edge + 2 * u_sd
    up_g = int((~a_true & guard).sum())
    lines = [f"bin edge {edge:.0f} Ah, capacity measured with sd {u_sd} Ah "
             f"({len(caps)} cells)",
             f"  B cells graded A: {up}; A cells graded B: {down}",
             f"  with a guard band of 2 sd ({2 * u_sd:.1f} Ah): B cells graded A "
             f"{up_g},",
             f"    A cells lost to B {int((a_true & ~guard).sum())}",
             "  the cycler's accuracy decides how many cells near the edge",
             "  land in the wrong bin; a B cell in an A module limits that",
             "  module (lesson B) - the guard band moves the doubt to the",
             "  cheaper side, as for capacitors in ch 44"]
    emit("v_binedge", lines)
    return dict(up=up, down=down, up_g=up_g)


# ------------------------------------------------ 3. an open sense wire
def sense_wire(n: int = 52, v_cell: float = 3.30) -> dict:
    """With an open sense wire between cells k and k+1, a simple front end
    reads their sum split between the two channels, or one channel near
    zero and the next near double (teaching)."""
    true = [v_cell] * n
    read = list(true)
    k = 20
    read[k], read[k + 1] = 0.05, 2 * v_cell - 0.05        # one way it can read
    pack = sum(true)
    lines = [f"module of {n} cells at {v_cell} V; the sense wire between cells "
             f"{k + 1} and {k + 2} opens",
             f"  channel {k + 1} reads {read[k]:.2f} V, channel {k + 2} reads "
             f"{read[k + 1]:.2f} V",
             f"  sum of channels {sum(read):.2f} V, module voltage measured "
             f"directly {pack:.2f} V",
             "  the sum still agrees - the plausibility that finds it is a",
             "  per-cell one: no cell can read near zero or near double while",
             "  its neighbours agree; the danger is the other way the fault",
             "  can show - a channel frozen at a normal value while its cell",
             "  overcharges - which is why the BMS tests its own sense lines",
             "  and the test is part of the factory evidence"]
    emit("v_sense", lines)
    return dict(read=(read[k], read[k + 1]), sum_ok=abs(sum(read) - pack) < 1e-9)


# ------------------------------------------------ 4. how much record
def records() -> dict:
    cells = B["s_module"] * B["m_rack"] * B["r_container"] * B["containers"]
    items = [("ID, lot, bin, capacity, resistance, K, fill weights", 0.5),
             ("formation and grading curves", 60.0),
             ("module build: cells, welds, torques, insulation", 0.4),
             ("BMS history, 1-minute cell data for 20 years", 3500.0)]
    lines = [f"record of a battery of {cells:,} cells (teaching sizes, kB a cell)",
             "  record                                             GB"]
    tot = 0.0
    out = {}
    for name, kb in items:
        gb = kb * cells / 1e6
        tot += gb
        out[name] = gb
        lines.append(f"  {name:48s} {gb:9.2f}")
    lines += [f"  total {tot:,.0f} GB - small next to what it protects; the",
              "  question is not space but keeping the record readable and",
              "  linked for twenty-five years: IDs that never change, formats",
              "  that can still be opened, and an owner (ch 38)"]
    emit("v_records", lines)
    return dict(total=tot)


# ------------------------------------------------ 5. what a site rest check sees
def site_check(res_mv: float = 1.0, k_normal: float = 0.030) -> dict:
    """OCV deviation of a leaker from its module after a rest at site,
    against a reading resolution (teaching)."""
    lines = ["cell OCV against its module after a rest at site;",
             f"  reading resolution {res_mv} mV (3 x to call it)",
             "  leaker K mV/day   days to 3 mV of difference"]
    out = {}
    for k in (0.064, 0.085, 0.110, 0.300):
        d = 3 * res_mv / (k - k_normal)
        out[k] = d
        lines.append(f"  {k:15.3f}   {d:25.0f}")
    csv("ch45-site.csv", "k,days", [(round(k - k_normal, 3),
                                     round(3 * res_mv / (k - k_normal), 1))
                                    for k in [0.045 + 0.005 * j for j in range(52)]])
    lines += ["  a site check of a few weeks finds strong leakers only; the",
              "  weak one of lab D (0.064) needs about three months - the",
              "  balancing-duty signal, not the rest check, is what finds it",
              "  in service; both go into D-049, each for what it can see"]
    emit("v_sitecheck", lines)
    return out


# ------------------------------------------------ 6. a container drained by its BMS
def standby_drain(soc0: float = 0.30, soc_min: float = 0.05,
                  bms_ma=(0.0, 20.0, 50.0)) -> dict:
    q = C["q_ah"]
    self_ma = lab_d.leak_current(0.030)
    lines = [f"a container waiting at site at {soc0:.0%} SOC: cells lose their own",
             f"  self-discharge ({self_ma:.1f} mA) and feed the BMS from the "
             "battery itself",
             "  (teaching BMS currents from each string)",
             "  BMS draw mA   days to fall to 5 % SOC"]
    out = {}
    for b in bms_ma:
        days = (soc0 - soc_min) * q / ((self_ma + b) / 1000 * 24)
        out[b] = days
        lines.append(f"  {b:11.0f}   {days:22,.0f}")
    lines += ["  a battery left with its BMS powered from itself can be",
              "  emptied while it waits for commissioning; below the cell's",
              "  minimum it may be unusable - storage instructions say who",
              "  charges it, when, and from what (ch 19, ch 50)"]
    emit("v_drain", lines)
    return out


# ------------------------------------------------ 7. module weight
def handling(overhead: float = 1.18) -> dict:
    m = B["s_module"] * C["mass_kg"] * overhead
    lines = [f"one module: {B['s_module']} cells x {C['mass_kg']} kg x "
             f"{overhead} = {m:.0f} kg",
             "  far beyond what people lift: lifting points, a lifting aid",
             "  rated for the module, and a proof test of the points are",
             "  part of the design and the factory evidence; the module is",
             "  live while it hangs (lesson C), so the aid is insulated",
             "  where it touches - a design question, not a site improvisation"]
    emit("v_handling", lines)
    return dict(mass=m)


# ------------------------------------------------ 8. the warranty energy counter
def counter(err: float = 0.01, mwh_year: float = 9000.0, limit_mwh: float = 180000.0,
            years: int = 20) -> dict:
    true_total = mwh_year * years
    read_hi = true_total * (1 + err)
    year_hi = limit_mwh / (mwh_year * (1 + err))
    lines = [f"warranty limited to {limit_mwh:,.0f} MWh discharged; true throughput "
             f"{mwh_year:,.0f} MWh a year",
             f"  a counter reading {err:+.0%} high shows {read_hi:,.0f} MWh after "
             f"{years} years",
             f"  the limit is 'reached' in year {year_hi:.1f} instead of "
             f"{limit_mwh / mwh_year:.1f}",
             "  the counter that ends a warranty is a measuring instrument:",
             "  its accuracy, calibration and the meter it is checked against",
             "  are written into the contract, not discovered in a dispute"]
    emit("v_counter", lines)
    return dict(year_hi=year_hi)


if __name__ == "__main__":
    hermetic()
    bin_edge()
    sense_wire()
    records()
    site_check()
    standby_drain()
    handling()
    counter()
    _ = math
