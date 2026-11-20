"""Chapter 37, lesson C (analytics and limits): peer benchmarking of PV
blocks, a power-curve anomaly on one turbine, the review queue an anomaly
detector creates, data completeness and normalisation, a degradation trend
with its uncertainty, and a baseline learned on bad data.

Run from the project root:   python -m companion.ch37.examples_c
Writes companion/ch37/expected/c2_*.txt and diagrams/data/ch37-*.csv.
Synthetic data and teaching values (A-411).
"""
from __future__ import annotations

import numpy as np

from companion.ch37 import sources as src
from companion.ch37.common import csv, emit


def peers(seed: int = 380) -> None:
    rng = np.random.default_rng(seed)
    base = 1_789.0                                    # kWh/kWp, lesson A
    spread = rng.normal(0, 0.006, 10)                 # block-to-block, 0.6 %
    spread[3] = -0.035                                # block B04: 3.5 % low
    y = base * (1 + spread)
    med = np.median(y)
    mad = np.median(np.abs(y - med)) * 1.4826
    z = (y - med) / mad
    csv("ch37-peers.csv", "b,y", [(i + 1, round(v, 1)) for i, v in enumerate(y)])
    lines = ["specific yield of the ten PV blocks in a year (synthetic)",
             "  block   kWh/kWp   robust z"]
    for i, (v, zz) in enumerate(zip(y, z)):
        flag = "  <- check" if abs(zz) > 3.5 else ""
        lines.append(f"  B{i + 1:02d}     {v:7.0f}   {zz:8.1f}{flag}")
    lines += ["  blocks share the weather, so comparing them removes it:",
              "  the median and the median absolute deviation are not",
              "  pulled by the bad block itself, as a mean and a standard",
              f"  deviation would be. B04 is {(1 - y[3] / med) * 100:.1f} % below its peers"]
    emit("c2_peers", lines)


def curve(v):
    """Teaching power curve of one turbine (MW), rated 5 MW at 12 m/s."""
    v = np.asarray(v, float)
    x = np.clip((v - 3) / 9, 0.0, 1.0)
    p = np.where((v >= 3) & (v < 12), 5.0 * x ** 2.2, 0.0)
    return np.where((v >= 12) & (v < 25), 5.0, p)


def power_curve(seed: int = 381) -> None:
    rng = np.random.default_rng(seed)
    v = 8.0 * rng.weibull(2.1, 4_380)                 # half a year of hours
    healthy = curve(v) * (1 + rng.normal(0, 0.04, v.size))
    faulty = healthy.copy()
    region2 = (v >= 4) & (v < 11)
    faulty[region2] *= 0.95                           # pitch offset: 5 % in region 2
    bins = np.arange(3, 16, 1.0)
    lines = ["one turbine against its expected curve, by wind-speed bin (synthetic)",
             "  bin m/s   hours   expected MW   measured MW   ratio"]
    rows = []
    for lo in bins:
        s = (v >= lo) & (v < lo + 1)
        if s.sum() < 20:
            continue
        e, m = curve(v[s]).mean(), faulty[s].mean()
        rows.append((lo + 0.5, round(e, 3), round(m, 3)))
        lines.append(f"  {int(lo):2d}-{int(lo) + 1:<5d} {int(s.sum()):6d}   {e:11.2f}"
                     f"   {m:11.2f}   {m / e:5.3f}")
    csv("ch37-curve.csv", "v,e,m", rows)
    lost = (healthy - faulty).sum()
    lines += [f"  energy lost in half a year: {lost:,.0f} MWh of {healthy.sum():,.0f}"
              f" ({lost / healthy.sum() * 100:.1f} %)",
              "  the loss shows only below rated speed: above it the",
              "  controller pitches to 5 MW anyway. Monthly energy hides",
              "  it in the weather; the curve by bin shows it in weeks"]
    emit("c2_curve", lines)


def review_queue() -> None:
    lines = ["an anomaly detector and the people who read its output",
             "  threshold   flags a day   true faults among them   reviewer hours"]
    rows = (("loose", 40, 0.08), ("", 12, 0.25), ("", 4, 0.6), ("tight", 1, 0.9))
    for name, flags, precision in rows:
        lines.append(f"  {name:9s}   {flags:11d}   {flags * precision:22.1f}"
                     f"   {flags * 0.25:14.1f}")
    true_l = 40 * 0.08
    lines += ["  (15 minutes to review a flag; synthetic precision values)",
              f"  a loose detector buries {true_l:.1f} real faults a day under"
              f" {40 - true_l:.0f}",
              "  false ones and ten hours of reading; a tight one is",
              "  believed but misses faults that start small. Every flag",
              "  goes to a person who decides; the detector only sorts",
              "  the queue (a score is never an instruction to act)"]
    emit("c2_queue", lines)


def completeness() -> None:
    y = src.operating_year()
    day = y["day"]
    valid = np.ones(8760, bool)
    valid[(day >= 120) & (day < 125)] = False         # 5 days of logger outage in May
    may = y["month"] == 4
    e_all = y["pv_act"][may].sum()
    e_val = y["pv_act"][may & valid].sum()
    h_all = y["poa_true"][may].sum() / 1000
    h_val = y["poa_true"][may & valid].sum() / 1000
    pr_wrong = (e_val * 1000 / src.P_DC_KWP) / h_all
    pr_right = (e_val * 1000 / src.P_DC_KWP) / h_val
    pr_true = (e_all * 1000 / src.P_DC_KWP) / h_all
    lines = ["May with 5 days of energy data missing (logger outage)",
             f"  data completeness: {(may & valid).sum() / may.sum() * 100:.1f} % of hours",
             f"  PR, energy of valid hours over the whole month's sun: {pr_wrong:.3f}",
             f"  PR, both on the same valid hours:                     {pr_right:.3f}",
             f"  PR with no gap (known here only because it is synthetic): {pr_true:.3f}",
             "  an indicator divides like by like: the gap is removed",
             "  from numerator and denominator together, and the report",
             "  states the completeness beside the value. A meter gap is",
             "  not lost energy - the revenue meter still counted it"]
    emit("c2_complete", lines)


def degradation(seed: int = 382) -> None:
    rng = np.random.default_rng(seed)
    months = np.arange(60)
    true_rate = -0.005                                 # -0.5 % a year
    season = 0.02 * np.cos(2 * np.pi * (months - 6) / 12)
    pr = 0.85 * (1 + true_rate * months / 12) + season + rng.normal(0, 0.006, 60)
    # year-on-year: same month, one year apart, removes the season
    yoy = (pr[12:] / pr[:-12] - 1)
    med = float(np.median(yoy))
    boot = [np.median(rng.choice(yoy, yoy.size)) for _ in range(2000)]
    lo, hi = np.percentile(boot, [5, 95])
    slope = np.polyfit(months[:12], pr[:12], 1)[0] * 12
    lines = ["degradation of the PV from 5 years of monthly PR (synthetic)",
             f"  true rate {true_rate * 100:.2f} %/yr",
             f"  year-on-year median: {med * 100:.2f} %/yr, 90 % interval"
             f" {lo * 100:.2f} to {hi * 100:.2f}",
             f"  a straight line through the first 12 months: {slope / 0.85 * 100:+.1f} %/yr",
             "  the one-year line reads the season as a trend; pairing",
             "  each month with the same month a year later removes the",
             "  season, and the interval says how sure the rate is - a",
             "  warranty claim on degradation needs that interval"]
    emit("c2_degradation", lines)


def baseline_trap() -> None:
    y = src.operating_year()
    apr = y["month"] == 3
    ratio_true = y["pv_act"][apr].sum() / y["pv_exp"][apr].sum()
    # a baseline 'learned' on April itself absorbs the soiling
    k = ratio_true
    learned = y["pv_exp"][apr] * k
    ratio_learned = y["pv_act"][apr].sum() / learned.sum()
    lines = ["a baseline fitted on the period it should judge (April)",
             f"  actual over model 15.1: {ratio_true:.3f}",
             f"  actual over a baseline scaled to April's own data: {ratio_learned:.3f}",
             "  the learned baseline 'expects' the soiling and the loss",
             "  disappears. A baseline is fixed from a reference period",
             "  checked to be healthy, kept under version control, and",
             "  refitted only with a record of why (ch 35, ch 15 model)"]
    emit("c2_baseline", lines)


if __name__ == "__main__":
    peers()
    power_curve()
    review_queue()
    completeness()
    degradation()
    baseline_trap()
