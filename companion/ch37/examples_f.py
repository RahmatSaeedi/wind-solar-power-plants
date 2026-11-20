"""Chapter 37, lesson F (reliability-data practice): the equipment
hierarchy and failure codes, exposure and the interval of a failure rate,
censored items, a Weibull fit, reliability growth of a young fleet,
comparability of two plants, and feedback to commissioning, warranty and
maintenance.

Run from the project root:   python -m companion.ch37.examples_f
Writes companion/ch37/expected/f_*.txt and diagrams/data/ch37-*.csv.
Synthetic failure data (A-413); factory data used as inputs only.
"""
from __future__ import annotations

import numpy as np

from companion.ch37.common import csv, emit
from plantp import performance as pf

SYSTEMS = [  # turbine system, failures in a fleet-year, mean downtime h (synthetic)
    ("converter", 9, 14), ("pitch system", 11, 8), ("generator", 2, 60),
    ("gearbox", 1, 240), ("yaw system", 4, 12), ("control and comms", 14, 4),
    ("hydraulics", 5, 10)]


def hierarchy() -> None:
    total_f = sum(f for _, f, _ in SYSTEMS)
    total_d = sum(f * d for _, f, d in SYSTEMS)
    lines = ["failures of 12 turbines in a year by system (synthetic, coded)",
             "  system              failures   share    downtime h   share"]
    rows = []
    for s, f, d in sorted(SYSTEMS, key=lambda r: -r[1] * r[2]):
        rows.append((s, f, f * d))
        lines.append(f"  {s:19s} {f:8d}   {f / total_f * 100:4.0f} %   {f * d:10,d}"
                     f"   {f * d / total_d * 100:4.0f} %")
    csv("ch37-systems.csv", "i,f,d", [(i, f, d) for i, (_, f, d) in enumerate(rows)])
    lines += ["  the many small faults (control, pitch) are not where the",
              "  downtime is: one gearbox costs more hours than all the",
              "  control faults together. Coding every failure to the",
              "  same hierarchy (plant, turbine, system, component) is",
              "  what makes this sort possible"]
    emit("f_hierarchy", lines)


def exposure() -> None:
    rows = [("model A, 8 converters", 6, 8 * 8760 * 0.92),
            ("model B, 4 converters", 1, 4 * 8760 * 0.60)]
    lines = ["converter failure rate per operating hour, with a 90 % interval",
             "  fleet                    failures   operating h   rate /1e5 h   interval"]
    for name, f, h in rows:
        lo, hi = pf.rate_interval(f, h, 0.9)
        lines.append(f"  {name:24s} {f:8d}   {h:11,.0f}   {f / h * 1e5:11.2f}"
                     f"   {lo * 1e5:.2f}-{hi * 1e5:.2f}")
    cal_a, cal_b = 6 / (8 * 8760), 1 / (4 * 8760)
    op_a, op_b = 6 / rows[0][2], 1 / rows[1][2]
    lines += [f"  per calendar hour model B looks {cal_a / cal_b:.1f} times better; per",
              f"  operating hour (B ran 60 % of the time) only {op_a / op_b:.1f} times,",
              "  and with one failure its interval is so wide that it",
              "  overlaps A's almost entirely - the two models cannot be",
              "  told apart. A rate is reported with its exposure and its",
              "  interval, never alone"]
    emit("f_exposure", lines)


def censored() -> None:
    failed = [3_200.0, 7_900.0, 12_400.0, 15_100.0]
    running = [17_520.0] * 8                        # two years, still running
    naive = np.mean(failed)
    mle = pf.mtbf_censored(failed, running)
    lines = ["12 inverter fans: 4 failed, 8 still running after 2 years",
             f"  mean of the failed ones only: {naive:,.0f} h",
             f"  all exposure over failures (censored estimate): {mle:,.0f} h",
             "  averaging only the failed items ignores every hour the",
             f"  survivors ran and makes the fan look {mle / naive:.1f} times worse",
             "  than it is; still-running items are 'censored' and count",
             "  as exposure without a failure"]
    emit("f_censored", lines)


def weibull(seed: int = 375) -> None:
    rng = np.random.default_rng(seed)
    life = 60_000 * rng.weibull(2.5, 40)            # main bearings, hours (synthetic)
    end = 50_000.0
    failed = life[life < end]
    cens = np.full(int(np.sum(life >= end)), end)
    k, lam = pf.weibull_mle(failed, cens)
    lines = ["Weibull fit of 40 main bearings after 50,000 h (synthetic)",
             f"  failed {len(failed)}, still running {len(cens)}",
             f"  shape k = {k:.2f}, scale = {lam:,.0f} h (true 2.5 and 60,000)",
             f"  share failed by 80,000 h on this fit: {(1 - np.exp(-(80_000 / lam) ** k)) * 100:.0f} %",
             f"  a constant rate on the same record (MTBF {pf.mtbf_censored(failed, cens):,.0f} h)"
             f" predicts {(1 - np.exp(-80_000 / pf.mtbf_censored(failed, cens))) * 100:.0f} %",
             "  a shape above 1 means wear-out: the rate rises with age,",
             "  and a constant rate reads it as chance and under-plans the",
             "  later years; spares and exchanges are planned by age, not",
             "  by an average rate (STD-166)"]
    emit("f_weibull", lines)


def growth() -> None:
    times = np.array([30, 80, 150, 260, 420, 700, 1100, 1800, 2900, 4400, 6500.0])
    beta = pf.crow_amsaa_beta(times, 8760.0)
    csv("ch37-growth.csv", "n,t", [(i + 1, t) for i, t in enumerate(times)])
    lines = ["failures of the new PV inverter fleet in its first year (synthetic)",
             f"  {len(times)} failures; Crow-AMSAA slope beta = {beta:.2f}",
             "  beta below 1: failures come further apart as the fleet",
             "  settles - early defects being removed (ch 48, 50); a",
             "  beta near 1 would mean a steady rate, above 1 wear-out.",
             "  The slope separates a young plant settling from a plant",
             "  getting worse"]
    emit("f_growth", lines)


def comparability() -> None:
    rows = [("Plant P", 97.9, "time, grid and curtailment excluded"),
            ("Plant Q", 98.8, "time, all planned work excluded too")]
    lines = ["two plants' reported availability (synthetic)",
             "  plant     reported %   definition"]
    for p, a, d in rows:
        lines.append(f"  {p:9s} {a:10.1f}   {d}")
    lines += ["  Plant Q looks better because it excludes more; on Plant",
              "  P's definition it would be about 98.1 % (its planned work",
              "  is 60 h a turbine a year): comparisons need one",
              "  definition, recomputed from the events, not two reports"]
    emit("f_compare", lines)


def feedback() -> None:
    rows = [("factory test", "burn-in failures by part", "input to spares, ch 48"),
            ("commissioning", "punch list, early trips", "input to growth, ch 50"),
            ("warranty", "claims and their root causes", "maker's fixes, ch 39"),
            ("maintenance", "failures coded to the hierarchy", "plans, ch 51")]
    lines = ["where reliability data comes from and where it goes",
             "  source           data                               feeds"]
    for a, b, c in rows:
        lines.append(f"  {a:16s} {b:34s} {c}")
    lines += ["  manufacturing is not part of this chapter; its failure",
              "  and quality data are inputs here, and each loop ends in a",
              "  change somebody owns"]
    emit("f_feedback", lines)


def lots() -> None:
    rows = [("lot L1", 200, 3), ("lot L2", 200, 11), ("lot L3", 150, 2)]
    lines = ["field failures of inverter fans by production lot, first year",
             "  (synthetic; units run 95 % of the year)",
             "  lot      units   failures   rate /1e6 h   90 % interval"]
    out = []
    for name, n, f in rows:
        h = n * 8760 * 0.95
        lo, hi = pf.rate_interval(f, h, 0.9)
        out.append((name, lo, hi))
        lines.append(f"  {name:7s} {n:6d}   {f:8d}   {f / h * 1e6:11.2f}"
                     f"   {lo * 1e6:.2f}-{hi * 1e6:.2f}")
    h_pool = (200 + 150) * 8760 * 0.95
    p_lo, p_hi = pf.rate_interval(5, h_pool, 0.9)
    sep = out[1][1] > p_hi
    verdict = "lies above" if sep else "overlaps"
    lines += [f"  L1 and L3 pooled: 5 failures, {5 / h_pool * 1e6:.2f} per 1e6 h,"
              f" {p_lo * 1e6:.2f}-{p_hi * 1e6:.2f}",
              f"  L2's interval {verdict} the pooled one: the lot, not",
              "  the site, is the first suspect - the serial numbers",
              "  tie each field failure to its lot, and the maker's",
              "  factory records for that lot (burn-in, process changes)",
              "  are asked for as inputs (ch 40-48); the cause is",
              "  settled with the maker, not guessed from the field"]
    emit("f_lots", lines)


if __name__ == "__main__":
    lots()
    hierarchy()
    exposure()
    censored()
    weibull()
    growth()
    comparability()
    feedback()
