"""Chapter 52, lesson E: RAM models and their assumptions - exponential
against Weibull at the same mean, what an MTBF does and does not say,
rate intervals and how many failures make a number, repairable fleets
and reliability growth, the export path as a block diagram and as a fault
tree, a common cause between redundant servers, k-out-of-n turbines, a
shared cable that breaks the independence assumption, and allocating a
plant target.

Run from the project root:   python -m companion.ch52.examples_e
Writes companion/ch52/expected/e_*.txt and diagrams/data/ch52-weibull.csv.
Teaching values (A-534).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch52.common import csv, emit
from plantp import performance as pf
from plantp import ram


# ------------------------------------------------ 1. exponential vs Weibull
def exp_vs_weibull(beta: float = 2.5, eta: float = 60_000.0) -> dict:
    mean = ram.w_mean(beta, eta)
    t = np.array([10_000, 30_000, 50_000, 80_000], float)
    rw = ram.w_reliability(t, beta, eta)
    re = np.exp(-t / mean)
    grid = np.arange(0, 120_001, 4_000)
    csv("ch52-weibull.csv", "t,weibull,exponential",
        [(int(x), round(float(ram.w_reliability(x, beta, eta)), 4), round(float(np.exp(-x / mean)), 4))
         for x in grid])
    lines = [f"main bearings: Weibull beta {beta}, eta {eta:,.0f} h (ch 37) against an",
             f"  exponential with the same mean life {mean:,.0f} h",
             "  hours     R Weibull   R exponential"]
    lines += [f"  {x:7,.0f}   {a:9.3f}   {b:13.3f}" for x, a, b in zip(t, rw, re)]
    lines += [f"  at 10,000 h the constant rate predicts {1 - re[0]:.0%} failed, the wear-out",
              f"  model {1 - rw[0]:.1%}; at 80,000 h {1 - re[3]:.0%} against {1 - rw[3]:.0%}:",
              "  the exponential buys spares too early and too few late -",
              "  same MTBF, different plant"]
    emit("e_weibull", lines)
    return dict(mean=mean, rw=rw.tolist(), re=re.tolist())


# ------------------------------------------------ 2. what an MTBF says
def mtbf_meaning(n: int = 10, lam_yr: float = 0.5) -> dict:
    mtbf = 8760 / lam_yr
    surv = math.exp(-lam_yr)
    lines = [f"PV inverters: {lam_yr} failures a unit-year -> MTBF {mtbf:,.0f} h",
             f"  this does NOT mean an inverter lasts {mtbf / 8760:.0f} years: it means",
             f"  {n} inverters give about {n * lam_yr:.0f} failures a year; one inverter",
             "  runs a whole year without one with",
             f"  probability {surv:.0%} (constant rate); the MTBF of a repairable unit",
             "  says how often, not how long - the life of a part is a",
             "  different question with a different model (Weibull)"]
    emit("e_mtbf", lines)
    return dict(mtbf=mtbf, surv=surv)


# ------------------------------------------------ 3. rate intervals and data sufficiency
def intervals(exposure_h: float = 10 * 8760.0) -> dict:
    rows = []
    for k in (0, 1, 2, 5, 10, 20):
        lo, hi = pf.rate_interval(k, exposure_h, 0.9)
        rows.append((k, lo * 8760, hi * 8760, (hi / lo) if lo > 0 else float("inf")))
    need = next(k for k in range(1, 200)
                if pf.rate_interval(k, exposure_h, 0.9)[1] / pf.rate_interval(k, exposure_h, 0.9)[0] <= 2)
    lines = ["90 % interval of a failure rate after ten unit-years, by failures seen",
             "  failures   low /yr   high /yr   high/low"]
    lines += [f"  {k:8d} {a:9.3f} {b:10.3f} {r:10.1f}" for k, a, b, r in rows]
    lines += [f"  the interval narrows to a factor 2 only after {need} failures:",
              "  a fleet of ten with two failures knows its rate within a",
              f"  factor of about {rows[2][3]:.0f} - a supplier's 'MTBF' from a few units",
              "  is a claim, not a measurement (ch 39)"]
    emit("e_interval", lines)
    return dict(rows=rows, need=need)


# ------------------------------------------------ 4. repairable fleet and growth
def growth() -> dict:
    times = np.array([150, 420, 700, 1_100, 1_900, 2_600, 3_900, 5_600, 7_900], float)
    beta = pf.crow_amsaa_beta(times, 8_760.0)
    first = int(np.sum(times < 4380))
    lines = ["PV inverter fleet: failure times in the first year (hours of operation)",
             "  " + ", ".join(f"{x:,.0f}" for x in times),
             f"  Crow-AMSAA slope {beta:.2f} (below 1: failures thinning out);",
             f"  first half-year {first}, second {times.size - first}",
             "  a repairable fleet has a failure intensity in time, not a",
             "  life: early failures (ch 40 infant mortality) dominate the",
             "  first year, so the year-one rate overstates year five"]
    emit("e_growth", lines)
    return dict(beta=beta, first=first)


# ------------------------------------------------ 5. the export path as a block diagram
def export_rbd() -> dict:
    a = {"line": 1 - 2 * 4.2 / 8760, "T1": 0.9923, "T2": 0.9923, "bus132": 0.99995,
         "PPC": 0.9995, "fallback": 0.99}
    any_export = ram.rbd(("s", ["line", "bus132", ("p", ["T1", "T2"]),
                                ("p", ["PPC", "fallback"])]), a)
    full_export = ram.rbd(("s", ["line", "bus132", "T1", "T2", ("p", ["PPC", "fallback"])]), a)
    lines = ["export path: line, 132 kV bus, two transformers, plant controller with",
             "  a fallback mode (ch 20)",
             f"  some export possible:   {any_export:.5f}  ({(1 - any_export) * 8760:.1f} h a year without)",
             f"  full export possible:   {full_export:.5f}  ({(1 - full_export) * 8760:.1f} h a year limited)",
             "  the two transformers in parallel almost remove the 'none'",
             "  case, but each still limits export when out: one diagram is",
             "  not enough - the question asked decides the diagram"]
    emit("e_rbd", lines)
    return dict(any=any_export, full=full_export)


# ------------------------------------------------ 6. fault tree of losing all export
def fault_tree() -> dict:
    tree = ("or", ["line", "bus132", ("and", ["T1", "T2"]),
                   ("and", ["PPC", "fallback"]), ("and", ["T1", "T2common"]),
                   ("and", ["T2", "T2common"])])
    q = {"line": 2 * 4.2 / 8760, "bus132": 5e-5, "T1": 0.0077, "T2": 0.0077,
         "PPC": 5e-4, "fallback": 0.01, "T2common": 0.0005}
    cuts = ram.cut_sets(tree)
    rare = ram.top_rare(cuts, q)
    exact = ram.top_exact(tree, q)
    lines = ["fault tree 'no export at all': minimal cut sets"]
    lines += [f"  {{{', '.join(sorted(c))}}}   q = {np.prod([q[e] for e in c]):.2e}" for c in cuts]
    share = {", ".join(sorted(c)): float(np.prod([q[e] for e in c])) / rare for c in cuts}
    ccf_share = share["T1, T2common"] + share["T2, T2common"]
    lines += [f"  top: rare-event sum {rare:.2e}, exact {exact:.2e}",
              f"  the line alone is {share['line']:.0%} of it; both transformers together "
              f"{share['T1, T2']:.1%},",
              f"  the bus {share['bus132']:.1%}, the common-cause pairs {ccf_share:.1%} - small here",
              "  only because the shared breaker ('T2common') was given a",
              "  small q: a tree lists the combinations a block diagram",
              "  hides, and each q is then a question for the data"]
    emit("e_tree", lines)
    return dict(cuts=len(cuts), rare=rare, exact=exact, line=share["line"])


# ------------------------------------------------ 7. common cause between redundant servers
def ccf(q: float = 0.005) -> dict:
    out = {b: ram.pair_with_ccf(q, b) for b in (0.0, 0.05, 0.10)}
    lines = [f"two SCADA servers, each unavailable {q:.1%}; share beta of that is common",
             "  (same firmware, same room cooling, same power)",
             "  beta    pair unavailable   hours a year"]
    lines += [f"  {b:4.2f}   {v:16.6f} {v * 8760:12.2f}" for b, v in out.items()]
    lines += [f"  a beta of 0.10 makes the pair {out[0.10] / out[0.0]:.0f} times worse than the",
              "  independent model: redundancy is only as good as what the",
              "  two do not share (ch 35 rings, ch 36 recovery)"]
    emit("e_ccf", lines)
    return out


# ------------------------------------------------ 8. k-out-of-n turbines
def turbines(a: float = 0.98, n: int = 12) -> dict:
    p = {k: ram.k_of_n(k, n, a) for k in (12, 11, 10)}
    lines = [f"{n} turbines, each available {a:.0%} (independent)"]
    lines += [f"  at least {k:2d} available: {v:.3f}" for k, v in p.items()]
    lines += [f"  all twelve run only {p[12]:.0%} of the time: the plant",
              "  almost never has its full wind capacity - which is why",
              "  energy availability, not 'all units up', is the measure"]
    emit("e_kofn", lines)
    return p


# ------------------------------------------------ 9. a shared cable breaks independence
def shared_cable() -> dict:
    q_block = 0.006                                     # one PV block unavailable
    q_cable = 0.01 * 4.5 * (120 + 48) / 8760            # feeder PVF2: 4.5 km cable
    indep = q_block ** 4
    shared = q_cable + indep
    lines = ["feeder PVF1 carries four PV blocks (PVF1-1..PVF1-4) on one 4.5 km cable",
             f"  'all four out' if the blocks were independent: {indep:.1e}",
             f"  with the shared cable (fail 0.01/km-yr, 168 h down): {shared:.1e}",
             f"  {shared / indep:,.0f} times more likely: the dependence, not the",
             "  blocks, sets the risk - a model that multiplies unit",
             "  availabilities misses every shared cause"]
    emit("e_shared", lines)
    return dict(indep=indep, shared=shared)


# ------------------------------------------------ 10. allocating a plant target
def allocation(target: float = 0.97) -> dict:
    share = {"wind": 0.64, "PV": 0.36, "BESS": 0.0}
    now = {"wind": 0.958, "PV": 0.978}
    budget = 1 - target
    alloc = {k: 1 - budget for k in ("wind", "PV")}
    lines = [f"plant energy-availability target {target:.0%} (teaching): the same",
             "  unavailability budget for each source, weighted by energy",
             "  source   energy share   allocated   first year"]
    for k in ("wind", "PV"):
        lines.append(f"  {k:6s} {share[k]:12.0%} {alloc[k]:11.1%} {now[k]:12.1%}")
    plant = sum(share[k] * now[k] for k in ("wind", "PV")) / (share["wind"] + share["PV"])
    lines += [f"  first-year plant (energy-weighted): {plant:.1%}; wind is short of its",
              "  share - the gap goes to the turbine service agreement and",
              "  its waiting times (lesson A), not spread over everything"]
    emit("e_alloc", lines)
    return dict(plant=plant)


if __name__ == "__main__":
    exp_vs_weibull()
    mtbf_meaning()
    intervals()
    growth()
    export_rbd()
    fault_tree()
    ccf()
    turbines()
    shared_cable()
    allocation()
