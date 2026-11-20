"""Chapter 53, lesson A: lifecycle performance - PV degradation from the
yearly PR with its interval, the wind availability trend and its break,
lost energy by cause in year 18, benchmarking against peers, and a
screen of improvement opportunities.

Run from the project root:   python -m companion.ch53.examples_a
Writes companion/ch53/expected/a_*.txt and diagrams/data/ch53-trends.csv.
Teaching values (A-538).
"""
from __future__ import annotations

import numpy as np

from companion.ch53 import sources as src
from companion.ch53.common import csv, emit
from plantp import lifecycle as lc


# ------------------------------------------------ 1. PV degradation
def degradation() -> dict:
    yrs = np.arange(1, len(src.PV_PR) + 1)
    b, h = lc.trend(yrs, src.PV_PR)
    rate = -b / src.PV_PR[0] * 100
    b5, h5 = lc.trend(yrs[:5], src.PV_PR[:5])
    csv("ch53-trends.csv", "year,pr,avail",
        [(int(y), p, a) for y, p, a in zip(yrs, src.PV_PR, src.WIND_AVAIL)])
    lines = ["PV performance ratio by year (temperature-corrected, %), years 1-18",
             "  " + " ".join(f"{x:.1f}" for x in src.PV_PR[:9]),
             "  " + " ".join(f"{x:.1f}" for x in src.PV_PR[9:]),
             f"  slope {b:+.3f} points a year +/- {h:.3f} (95 %) = {rate:.2f} % a year relative",
             f"  slower than the 0.5 %/yr of the finance model (ch 21): the interval",
             f"  (+/- {h / src.PV_PR[0] * 100:.2f} %/yr) excludes it - the modules age better than",
             "  planned, a finding for the energy model; the first five years",
             f"  alone gave {-b5 / src.PV_PR[0] * 100:.2f} +/- {h5 / src.PV_PR[0] * 100:.2f} %/yr - "
             "enough to correct the",
             "  model in year 6, had anyone looked (ch 37)"]
    emit("a_degr", lines)
    return dict(b=b, h=h, rate=rate)


# ------------------------------------------------ 2. wind availability trend and break
def wind_trend() -> dict:
    yrs = np.arange(1, len(src.WIND_AVAIL) + 1)
    early = lc.trend(yrs[3:9], src.WIND_AVAIL[3:9])
    late = lc.trend(yrs[9:], src.WIND_AVAIL[9:])
    lines = ["wind energy availability by year (%)",
             "  " + " ".join(f"{x:.1f}" for x in src.WIND_AVAIL[:9]),
             "  " + " ".join(f"{x:.1f}" for x in src.WIND_AVAIL[9:]),
             f"  years 4-9: {early[0]:+.2f} points a year; years 10-18: {late[0]:+.2f} +/- "
             f"{late[1]:.2f}",
             "  the fall steepens after year 9: the major components enter",
             "  wear-out (ch 52 Weibull) - one straight line through all",
             "  18 years would hide the break and the cause"]
    emit("a_wind", lines)
    return dict(early=early[0], late=late[0], late_h=late[1])


# ------------------------------------------------ 3. lost energy by cause, year 18
def lost() -> dict:
    tot = sum(src.LOST_BY_CAUSE.values())
    rows = sorted(src.LOST_BY_CAUSE.items(), key=lambda kv: -kv[1])
    csv("ch53-lost.csv", "k,mwh", [(i + 1, round(v)) for i, (_, v) in enumerate(rows)])
    lines = [f"energy lost in year 18 by cause ({tot:,.0f} MWh)"]
    for k, v in sorted(src.LOST_BY_CAUSE.items(), key=lambda kv: -kv[1]):
        lines.append(f"  {k:28s} {v:7,.0f}  {v / tot:4.0%}  {v * src.PRICE / 1000:6.0f} k u")
    big = max(src.LOST_BY_CAUSE, key=src.LOST_BY_CAUSE.get)
    lines += [f"  the largest: {big} - the one cause an intervention",
              "  can remove; curtailment is the grid's (ch 51) and soiling",
              "  the cleaning plan's (ch 52) - each goes to its owner"]
    emit("a_lost", lines)
    return dict(tot=tot, big=big)


# ------------------------------------------------ 4. benchmarking
def benchmark() -> dict:
    p = src.BENCH["Plant P"]
    peers = {k: v for k, v in src.BENCH.items() if k != "Plant P"}
    mw = np.median([v[0] for v in peers.values()])
    mp = np.median([v[1] for v in peers.values()])
    lines = ["year 18 against three peers of similar age (teaching data)",
             "  plant     wind availability %   PV PR %"]
    lines += [f"  {k:8s} {a:12.1f} {r:16.1f}" for k, (a, r) in src.BENCH.items()]
    lines += [f"  Plant P is {mw - p[0]:.1f} points below the peers' median in wind",
              f"  availability and {mp - p[1]:.1f} in PR: the gap is larger in wind -",
              "  peers differ in climate and contract, so a benchmark asks",
              "  the question; the plant's own records answer it"]
    emit("a_bench", lines)
    return dict(gap_w=float(mw - p[0]), gap_p=float(mp - p[1]))


# ------------------------------------------------ 5. screen of improvement opportunities
OPPS = [   # opportunity, cost k u, MWh a year gained, years it lasts
    ("gearbox replacement programme", 7_440.0, 2_400.0, 7),
    ("inverter replacement (10 units)", 4_200.0, 1_350.0, 7),
    ("cleaning trigger by soiling station", 60.0, 520.0, 7),
    ("yaw recalibration fleet-wide", 45.0, 600.0, 7),
    ("PV module repowering (bifacial)", 21_000.0, 9_500.0, 7),
    ("blade leading-edge repair", 110.0, 480.0, 5)]


def screen(rate: float = src.RATE) -> dict:
    rows = []
    for k, cost, mwh, yrs in OPPS:
        price = src.PRICE
        af = (1 - (1 + rate) ** -yrs) / rate
        npv = mwh * price / 1000 * af - cost
        rows.append((k, cost, mwh, npv, cost / (mwh * price / 1000)))
    rows.sort(key=lambda r: -r[3])
    lines = [f"improvement opportunities at {src.PRICE:.0f} u/MWh over the years left (teaching)",
             "  opportunity                          cost k u   MWh/yr   NPV k u  payback yr"]
    lines += [f"  {k:36s} {c:8,.0f} {m:8,.0f} {n:9,.0f} {pb:9.1f}" for k, c, m, n, pb in rows]
    lines += ["  the cheap operating fixes pay at once; the replacement",
              "  programmes do not pay on energy alone - their case rests on",
              "  avoided repairs and downtime and on the years after the PPA,",
              "  which lesson B and the decision lab weigh"]
    emit("a_screen", lines)
    return {k: n for k, c, m, n, pb in rows}


if __name__ == "__main__":
    degradation()
    wind_trend()
    lost()
    benchmark()
    screen()
