"""Chapter 32, lesson R: numbers behind safety decisions - what an audit
sample says about all permits, which contractor's rate stands out
(a funnel plot), where near misses concentrate (Pareto), whether people
leave the control building before the smoke reaches them (ASET and
RSET), and whether a security measure pays for itself.

Run from the project root:   python -m companion.ch32.examples_r
Writes companion/ch32/expected/r_*.txt and diagrams/data/ch32-funnel.csv,
ch32-pareto.csv, ch32-egress.csv.
Teaching values (A-368, A-375).
"""
from __future__ import annotations

import math

import numpy as np
from scipy import stats

from companion.ch32 import sources as src  # noqa: F401  (puts plantp on the path)
from companion.ch32.common import csv, emit
from plantp import safety as sf


def permit_sample() -> None:
    lines = ["what an audit sample says about all permits (exact binomial, 90 %)",
             "  sample   found correct   share   interval"]
    for n, k in [(20, 18), (20, 20), (60, 54)]:
        lo = stats.beta.ppf(0.05, k, n - k + 1) if k > 0 else 0.0
        hi = stats.beta.ppf(0.95, k + 1, n - k) if k < n else 1.0
        lines.append(f"  {n:6d}   {k:13d}   {k / n * 100:4.0f} %   {lo * 100:3.0f}-{hi * 100:3.0f} %")
    lines += ["  20 of 20 correct still leaves room for one permit in ten",
              "  to be wrong: a clean sample is reassuring, not proof - a",
              "  larger sample, or auditing the riskiest permits first,",
              "  narrows what the audit can say"]
    emit("r_permits", lines)


def funnel() -> None:
    contractors = [("civil works", 380_000, 6), ("electrical", 210_000, 3),
                   ("turbine erection", 160_000, 9), ("PV mechanical", 240_000, 2),
                   ("logistics", 60_000, 1)]
    total_h = sum(h for _, h, _ in contractors)
    total_n = sum(n for _, _, n in contractors)
    mean = total_n / total_h * 200_000
    rows = []
    lines = ["recordable rates by contractor against the site mean (funnel check)",
             f"  site mean {mean:.2f} per 200,000 h",
             "  contractor          hours     n   rate   95 % band for its hours   flag"]
    for name, h, n in contractors:
        exp = mean * h / 200_000
        lo = stats.poisson.ppf(0.025, exp)
        hi = stats.poisson.ppf(0.975, exp)
        flag = "above" if n > hi else ("below" if n < lo else "")
        rows.append((h, round(n / h * 200_000, 2)))
        lines.append(f"  {name:17s} {h:7,d}  {n:4d}   {n / h * 2e5:4.1f}"
                     f"   {lo / h * 2e5:4.1f}-{hi / h * 2e5:4.1f}{'':17s}{flag}")
    csv("ch32-funnel.csv", "hours,rate", rows)
    fh = np.linspace(40_000, 420_000, 40)
    csv("ch32-funnelband.csv", "hours,lo,hi",
        [(int(h), round(stats.poisson.ppf(0.025, mean * h / 2e5) / h * 2e5, 3),
          round(stats.poisson.ppf(0.975, mean * h / 2e5) / h * 2e5, 3)) for h in fh])
    lines += ["  turbine erection sits above its band: a cause worth",
              "  finding (crews, lifts, supervision), not a league table -",
              "  small contractors' rates swing widely by chance, so the",
              "  band, not the ranking, decides who is looked at"]
    emit("r_funnel", lines)


def pareto() -> None:
    causes = [("load or tool not secured", 41), ("vehicle reversing", 33),
              ("isolation step skipped", 9), ("access route blocked", 22),
              ("heat, fatigue", 21), ("housekeeping", 18), ("other", 20)]
    causes.sort(key=lambda c: -c[1])
    total = sum(n for _, n in causes)
    cum, rows = 0, []
    lines = ["near-miss causes ranked (164 in the construction year, synthetic)",
             "  cause                         count   cumulative"]
    for name, n in causes:
        cum += n
        rows.append((name.split()[0], n, round(cum / total * 100, 1)))
        lines.append(f"  {name:29s} {n:5d}   {cum / total * 100:9.0f} %")
    csv("ch32-pareto.csv", "cause,count,cum", [(k + 1, r[1], r[2]) for k, r in enumerate(rows)])
    lines += ["  three causes give about 60 % of the near misses and are",
              "  where most effort goes - but the nine skipped isolation",
              "  steps rank low by count and highest by what they could",
              "  have done (lesson A): count and severity are read together"]
    emit("r_pareto", lines)


def aset_rset() -> None:
    rset_parts = [("detection (aspirating)", 30), ("alarm and recognition", 30),
                  ("pre-movement (stop, collect)", 60), ("walk 25 m at 1.2 m/s", 21),
                  ("queue at one door (30 people)", 23)]
    rset = sum(t for _, t in rset_parts)
    aset = 2.3 * 60                                 # lesson P, 300 kW fire, layer at 2 m
    rows = [(k + 1, t) for k, (_, t) in enumerate(rset_parts)]
    csv("ch32-egress.csv", "step,t", rows)
    lines = ["can people leave before the smoke? ASET vs RSET (control building)",
             "  required safe egress time (RSET), seconds"]
    for name, t in rset_parts:
        lines.append(f"    {name:34s} {t:4d}")
    better = rset - 30 - 11                         # drilled pre-movement 30 s, second exit
    lines += [f"  RSET {rset} s; ASET (smoke at 2 m, 300 kW fire, lesson P) {aset:.0f} s",
              f"  as drawn the smoke wins by {rset - aset:.0f} s",
              f"  second exit and drilled 'leave now': RSET {better} s, margin {aset - better:.0f} s",
              f"  the same with a heat detector (detection 120 s): margin {aset - better - 90:.0f} s",
              "  pre-movement - people finishing a task - is the largest",
              "  part: drills and a second exit turn the result round;",
              "  slow detection undoes it - the three work together"]
    emit("r_egress", lines)


def security_value() -> None:
    lines = ["does a security measure pay for itself? (teaching, k u a year)",
             "  measure                      cost/yr   events/yr   loss/event   saved/yr"]
    for name, cost, f0, f1, loss in [("marked aluminium earth cable", 6, 1.5, 0.4, 40),
                                     ("alarm at stores", 12, 2.0, 0.8, 15),
                                     ("guard at every gate, 24 h", 180, 2.0, 0.6, 15)]:
        saved = (f0 - f1) * loss
        lines.append(f"  {name:28s} {cost:7d}   {f0:3.1f} -> {f1:3.1f}   {loss:10d}   {saved:8.0f}")
    lines += ["  design and records (cheap, permanent) pay back many times;",
              "  manpower is costly for the loss it prevents - and the",
              "  community relations of lesson G reduce the events",
              "  themselves; measures stay proportionate and lawful"]
    emit("r_security", lines)


if __name__ == "__main__":
    permit_sample()
    funnel()
    pareto()
    aset_rset()
    security_value()
