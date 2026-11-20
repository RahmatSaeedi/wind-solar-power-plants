"""Chapter 33, lesson N (monitoring, more): fatalities estimated from a
carcass search, noise compliance by wind speed with the background taken
out, quarterly reporting of the indicators, the salinity of the site
well, and water reused instead of trucked or evaporated.

Run from the project root:   python -m companion.ch33.examples_n
Writes companion/ch33/expected/n_*.txt and diagrams/data/ch33-compliance.csv,
ch33-carcass.csv. Synthetic monitoring results (A-382); the limits, the
survey method and the salinity trigger are PLACEHOLDERS (U-112, U-114).
"""
from __future__ import annotations

import math

import numpy as np
from scipy import stats

from companion.ch33 import sources as src  # noqa: F401  (path set-up)
from companion.ch33.common import csv, emit
from plantp import envsocial as es


def _poisson_ci(k: int, conf: float = 0.90) -> tuple[float, float]:
    a = 1 - conf
    lo = 0.0 if k == 0 else stats.chi2.ppf(a / 2, 2 * k) / 2
    hi = stats.chi2.ppf(1 - a / 2, 2 * k + 2) / 2
    return lo, hi


def carcass() -> None:
    groups = [  # name, found, searcher efficiency, mean persistence d, interval d, area
        ("raptors", 2, 0.85, 25.0, 14.0, 0.70),
        ("bats, 14-day rounds", 9, 0.40, 4.0, 14.0, 0.70),
        ("bats, 3-day rounds", 9, 0.40, 4.0, 3.0, 0.70)]
    lines = ["fatalities estimated from the carcasses found in year 1 (synthetic)",
             "  group                found  search  persist  p find  estimate   90 % range"]
    out, res = [], []
    for k, (name, n, se, pd, iv, ar) in enumerate(groups, 1):
        ps = es.persistence_share(pd, iv)
        p = se * ps * ar
        est = es.fatality_estimate(n, se, pd, iv, ar)
        lo, hi = _poisson_ci(n)
        out.append((k, n, round(est, 1)))
        res.append((p, est, lo / p, hi / p))
        lines.append(f"  {name:20s} {n:5d}  {se:6.2f}  {ps:7.2f}  {p:6.3f}"
                     f"  {est:8.1f}  {lo / p:5.1f} -{hi / p:6.1f}")
    csv("ch33-carcass.csv", "k,found,estimate", out)
    (p_r, e_r, lo_r, hi_r), (p14, e14, _, _), (_, e3, _, _) = res
    lines += [f"  two raptors found means about {e_r:.0f} killed - close to the",
              f"  4.8 predicted (lesson A), but two carcasses cannot tell"
              f" {lo_r:.0f} from {hi_r:.0f}",
              "  a year: the range, not the point, goes in the report;",
              f"  bats vanish in days, so 14-day rounds find only {p14 * 100:.0f} % of",
              f"  them: 9 found means about {e14:.0f} killed, while 9 found in",
              f"  3-day rounds would mean {e3:.0f}. The search interval is set",
              "  from the persistence before the survey starts, and the",
              "  estimates feed the curtailment trigger"]
    emit("n_carcass", lines)


def compliance(seed: int = 333) -> None:
    rng = np.random.default_rng(seed)
    v = np.arange(4, 13)
    lw = np.minimum(106.0, 106.0 - 3.0 * (9 - v))           # teaching sound power curve
    cx, cy = src.DWELLINGS["herders' camp B (seasonal)"]
    dist = np.hypot(src.TURBINES[:, 0] - cx, src.TURBINES[:, 1] - cy)
    pred = np.array([es.db_sum([es.noise_at(L, d) for d in dist]) for L in lw])
    bg = 26.0 + 1.8 * (v - 4)                                # background rises with wind
    actual = pred + 0.8                                      # turbines a little louder than modelled
    total = np.array([es.db_sum([a, b]) for a, b in zip(actual, bg)]) + rng.normal(0, 0.3, v.size)
    alone = [es.energy_difference_db(t, b) if t - b > 3 else float("nan")
             for t, b in zip(total, bg)]
    lines = ["noise compliance at the camp by hub wind speed (synthetic survey)",
             "  v m/s  total  background  turbines  predicted  limit 40?"]
    out = []
    for i in range(v.size):
        a = alone[i]
        ok = "-" if math.isnan(a) else ("yes" if a <= 40.0 else "NO")
        txt = "  n/a  " if math.isnan(a) else f"{a:7.1f}"
        lines.append(f"  {v[i]:5d}  {total[i]:5.1f}  {bg[i]:10.1f}  {txt:>8s}  {pred[i]:9.1f}  {ok:>9s}")
        out.append((int(v[i]), round(float(total[i]), 1), round(float(bg[i]), 1),
                    round(float(pred[i]), 1)))
    csv("ch33-compliance.csv", "v,total,bg,pred", out)
    worst = max(a for a in alone if not math.isnan(a))
    na = [int(v[i]) for i in range(v.size) if math.isnan(alone[i])]
    lines += ["  the turbines alone come out of each total by subtracting",
              "  the background as energy; where the total is within 3 dB",
              f"  of the background (bins {na} m/s) the subtraction is",
              "  unreliable and the bin is reported as not determinable;",
              "  the measured turbine level runs about 0.8 dB above the",
              f"  prediction; the loudest determinable bin, {worst:.1f} dB(A), is",
              f"  {'under' if worst <= 40 else 'over'} the placeholder limit - a margin under 1 dB,",
              "  so the survey is repeated in the camp's season; the",
              "  method, bins and limit come from the permit (U-112)"]
    emit("n_compliance", lines)


def reporting() -> None:
    rows = [  # indicator, target, tolerance, higher better, four quarters
        ("grievances closed in 30 days %", 90, 5, True, (72, 81, 88, 93)),
        ("local hires % of workforce", 40, 5, True, (31, 34, 36, 41)),
        ("dust days over trigger a month", 2, 1, False, (5, 4, 3, 2)),
        ("restored area with cover % ", 80, 10, True, (0, 20, 40, 55)),
        ("village well level change m", 0.5, 0.2, False, (0.2, 0.4, 0.6, 0.5))]
    lines = ["the year's indicators by quarter (synthetic; R red, A amber, G green)",
             "  indicator                          Q1     Q2     Q3     Q4"]
    for name, t, tol, hi, q in rows:
        cells = [f"{x:4g} {es.kpi_rag(x, t, tol, hi)[0].upper()}" for x in q]
        lines.append(f"  {name:32s} " + "  ".join(f"{c:>6s}" for c in cells))
    lines += ["  a trend says more than a quarter: grievances and hires",
              "  are improving and reach green; restored cover is red all",
              "  year because vegetation needs seasons (closure waits,",
              "  lesson C); the annual report shows each line with its",
              "  trend, the corrective actions and what changed because of",
              "  them - and goes to the village in the local language"]
    emit("n_reporting", lines)


def salinity() -> None:
    ec0, growth, trigger = 1450.0, 0.03, 2000.0     # uS/cm, per year, PLACEHOLDER trigger
    years = math.log(trigger / ec0) / math.log(1 + growth)
    lines = ["salinity of the site well W-1 (teaching trend)",
             f"  electrical conductivity {ec0:.0f} uS/cm at the start, rising"
             f" {growth * 100:.0f} % a year",
             f"  trigger (PLACEHOLDER, the village's drinking limit): {trigger:.0f} uS/cm",
             f"  reached after about {years:.0f} years if nothing changes",
             "  a rising salinity says the well draws older, deeper or",
             "  saltier water - the same aquifer the village drinks; the",
             "  quarterly sample is part of the water plan, and the trend,",
             "  not one value, triggers a review: less pumping, the second",
             "  well, or water brought in - long before the trigger"]
    emit("n_salinity", lines)


def reuse() -> None:
    camp = 30.0 * 0.8 * 540            # m3 of treated camp wastewater over 18 months
    shortfall = 57_130.0               # trucked construction water (ch 29)
    reject = 1_000.0                   # RO reject a year in operation (lesson F)
    lines = ["water reused instead of trucked or evaporated (teaching)",
             "  construction: treated camp wastewater for dust,",
             f"    30 m3/d x 0.8 x 540 d = {camp:,.0f} m3",
             f"    {camp / shortfall * 100:.0f} % of the {shortfall:,.0f} m3 that would"
             " otherwise be trucked in (ch 29)",
             f"  operation: RO reject {reject:,.0f} m3 a year sprayed on the gravel"
             " roads",
             "    instead of evaporated - a smaller pond, and the salt crust",
             "    binds the dust",
             "  conditions: the discharge permit allows it, the treated",
             "  water meets the reuse quality, no spraying near the farms,",
             "  the wadi or the spring, and a record of every load - reuse",
             "  is a permitted use of a waste stream, not a way around it"]
    emit("n_reuse", lines)


if __name__ == "__main__":
    carcass()
    compliance()
    reporting()
    salinity()
    reuse()
