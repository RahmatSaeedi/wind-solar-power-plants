"""Chapter 37, deeper lessons on metrics, diagnosis and analytics: the
uncertainty of PR, production-based availability of the wind farm from the
event log, EWMA against CUSUM, many tags tested every day, soiling read
from a cleaning step, how many years a degradation rate needs, and the
chance that an unchanged fleet misses an availability guarantee.

Run from the project root:   python -m companion.ch37.examples_k
Writes companion/ch37/expected/k_*.txt and diagrams/data/ch37-*.csv.
Synthetic data and teaching values (A-409 to A-413).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch37 import lab_e, sources as src
from companion.ch37.common import csv, emit
from companion.ch37.examples_b import daily_residual


def pr_uncertainty() -> None:
    parts = [("plane-of-array irradiation (sensor class)", 1.5),
             ("energy meter at MV", 0.2),
             ("DC rating (flash-test tolerance)", 1.0)]
    u = math.sqrt(sum(p ** 2 for _, p in parts))
    pr = 0.832
    lines = ["standard uncertainty of the annual PR (teaching values, %)",
             "  source                                     u %"]
    for name, p in parts:
        lines.append(f"  {name:42s} {p:4.1f}")
    lines += [f"  combined (root sum of squares)             {u:4.1f}",
              f"  PR {pr:.3f} +/- {pr * u / 100:.3f} (k = 1), +/- {2 * pr * u / 100:.3f} (k = 2)",
              "  the sensor dominates. A PR of 0.83 cannot be told from",
              "  0.85 by this sensor alone; month-to-month changes on the",
              "  same sensor are far better known, because its bias is",
              "  the same in both months and cancels - trends are",
              "  sharper than absolute values (ch 2, uncertainty)"]
    emit("k_pruncert", lines)


def wind_energy_availability() -> None:
    y = src.operating_year()
    w1 = y["w_exp"] / 12                                 # one turbine, MW
    truth, _ = lab_e.event_log()
    hours = np.arange(8760)
    lost, possible, down_h = 0.0, 12 * w1.sum(), 0.0
    for t, s, _, e in truth:
        frac = np.clip(np.minimum(hours + 1, e) - np.maximum(hours, s), 0, 1)
        lost += np.sum(frac * w1)
        down_h += e - s
    a_t = 1 - down_h / (12 * 8760)
    a_e = 1 - lost / possible
    lines = ["the wind farm's outages of lab E against the hourly wind of the year",
             f"  downtime {down_h:,.0f} turbine-hours; energy lost {lost:,.0f} MWh"
             f" of {possible:,.0f}",
             f"  time-based availability       {a_t * 100:6.2f} %",
             f"  production-based availability {a_e * 100:6.2f} %",
             f"  mean output of a turbine in its down hours {lost / down_h:.2f} MW,"
             f" against {w1.mean():.2f} MW",
             "    over the year",
             "  the down hours were about as windy as the year, so the two",
             f"  agree within {abs(a_e - a_t) * 100:.2f} points; lesson A's March stop shows",
             "  how far they part when an outage meets a windy spell. A",
             "  team that plans its work in calm spells raises the",
             "  production-based figure and leaves the time-based one",
             "  unchanged"]
    emit("k_windenergy", lines)


def ewma_vs_cusum(lam: float = 0.2, width: float = 3.0) -> None:
    r = daily_residual()
    sigma = np.std(r[:90], ddof=1)
    s_e = sigma * math.sqrt(lam / (2 - lam))
    z = 0.0
    alarm_e = None
    rows = []
    for d in range(90, 130):
        z = lam * r[d] + (1 - lam) * z
        rows.append((d - 89, round(r[d], 4), round(z, 4)))
        if alarm_e is None and z < -width * s_e:
            alarm_e = d
    csv("ch37-ewma.csv", "d,r,z", rows)
    lines = ["April: an EWMA chart beside the CUSUM of lesson B",
             f"  noise of the daily residual {sigma:.4f}; EWMA weight {lam},"
             f" limit {width:.0f} x {s_e:.4f}",
             f"  EWMA alarm on day {alarm_e} (April {alarm_e - 89});"
             " CUSUM alarmed on day 99",
             "  both charts smooth the noise and remember the past; the",
             "  EWMA forgets old days at a fixed rate, the CUSUM adds",
             "  shortfalls above an allowance. For a slow drift they",
             "  find it within days of each other; the CUSUM is simpler",
             "  to explain in a report, the EWMA's line is easier to",
             "  plot beside the residual"]
    emit("k_ewma", lines)


def many_tags(seed: int = 387) -> None:
    rng = np.random.default_rng(seed)
    n, days, p = 210, 365, 0.01                          # 10 blocks x 21 combiners
    z_lim = 2.326                                        # one-sided 1 %
    x = rng.normal(0, 1, (days, n))
    x[200:, 57] -= 1.6                                   # one combiner 4 % low from day 200
    flag1 = x < -z_lim
    run3 = flag1[2:] & flag1[1:-1] & flag1[:-2]
    false1 = int(flag1[:, np.arange(n) != 57].sum())
    false3 = int(run3[:, np.arange(n) != 57].sum())
    first1 = 200 + int(np.argmax(flag1[200:, 57]))
    hit3 = np.where(run3[198:, 57])[0]
    first3 = 200 + int(hit3[0]) if hit3.size else None
    # a CUSUM on each box (allowance 0.5, threshold 8, in units of z)
    s = np.zeros(n)
    cus_false, cus_first = 0, None
    for d in range(days):
        s = np.maximum(0.0, s - x[d] - 0.5)
        hit = s > 8.0
        cus_false += int(hit[np.arange(n) != 57].sum())
        if hit[57] and cus_first is None and d >= 200:
            cus_first = d
        s[hit] = 0.0                                     # reset after a flag
    lines = ["210 combiner boxes, each tested every day at a 1 % false-alarm rate",
             f"  expected false flags a day: {n * p:.1f}; in the year: {false1}",
             f"  flag only after 3 days in a row: {false3} false flags in the year",
             "  the faulty box (from day 200, z about -1.6 a day):",
             f"    single-day rule first flags it on day {first1}",
             f"    three-in-a-row rule first flags it on day {first3}",
             f"    CUSUM on each box (allowance 0.5, threshold 8): day {cus_first},",
             f"    with {cus_false} false flags in the year",
             "  one test is quiet; 210 tests a day are not - two false",
             "  flags every day add up to a queue nobody reads. Plain",
             f"  persistence removes them but waits {first3 - 200} days for this",
             "  fault; a CUSUM per box keeps the false flags rare and",
             f"  finds it in {cus_first - 200} days, because it adds up a small",
             "  shortfall instead of waiting for three large ones"]
    emit("k_manytags", lines)


def soiling_from_cleaning() -> None:
    y = src.operating_year()
    r = daily_residual()
    before = np.mean(r[116:119])                         # last three April days
    after = np.mean(r[121:124])                          # first days of May
    slope = np.polyfit(np.arange(90, 120), r[90:120], 1)[0]
    lines = ["April's soiling read from the data alone",
             f"  residual, last three days before cleaning {before * 100:+.2f} %",
             f"  residual, three days after                {after * 100:+.2f} %",
             f"  step at cleaning {(after - before) * 100:.2f} %; slope through April"
             f" {slope * 100:.3f} %/day",
             f"  planted: 6 % at the end of the month, {6 / 29:.3f} %/day",
             "  the step at a cleaning measures the soiling directly, the",
             "  slope says how fast it builds; with both, the cleaning",
             "  interval of chapter 10 is re-checked against the site's",
             "  real soiling rate, not the design value"]
    emit("k_soilstep", lines)


def trend_years(seed: int = 388) -> None:
    rng = np.random.default_rng(seed)
    lines = ["width of the 90 % interval of the degradation rate (synthetic,",
             "  median over 100 plants with a true rate of -0.50 %/yr)",
             "  years of monthly PR   median %/yr   90 % interval width"]
    rows = []
    for years in (2, 3, 4, 5, 6):
        m = 12 * years
        months = np.arange(m)
        meds, widths = [], []
        for _ in range(100):                             # 100 synthetic plants
            pr = (0.85 * (1 - 0.005 * months / 12)
                  + 0.02 * np.cos(2 * np.pi * (months - 6) / 12)
                  + rng.normal(0, 0.006, m))
            yoy = pr[12:] / pr[:-12] - 1
            boot = np.median(rng.choice(yoy, (300, yoy.size)), axis=1)
            lo, hi = np.percentile(boot, [5, 95])
            meds.append(np.median(yoy))
            widths.append(hi - lo)
        w = float(np.median(widths))
        rows.append((years, round(w * 100, 3)))
        lines.append(f"  {years:18d}   {np.median(meds) * 100:11.2f}   {w * 100:19.2f}")
    csv("ch37-trendyears.csv", "y,w", rows)
    lines += ["  the interval narrows with every year of data; a claim",
              "  that the rate exceeds a warranty limit of 0.7 %/yr is",
              "  only possible once the interval is narrower than the",
              "  gap between the measured rate and the limit"]
    emit("k_trendyears", lines)


def guarantee_risk(n_years: int = 400) -> None:
    vals = []
    for seed in range(1000, 1000 + n_years):
        truth, _ = lab_e.event_log(seed=seed)
        a, _, _ = lab_e.metrics(truth, 3)
        vals.append(a)
    vals = np.array(vals)
    hist, edges = np.histogram(vals * 100, bins=np.arange(97.0, 99.6, 0.1))
    csv("ch37-guarantee.csv", "a,n", [(round(e + 0.05, 2), int(h)) for e, h in zip(edges, hist)])
    lines = [f"the same fleet and the same failure process, {n_years} simulated years",
             f"  fleet availability: mean {vals.mean() * 100:.2f} %,"
             f" 5th percentile {np.percentile(vals, 5) * 100:.2f} %",
             f"  years below a 98.5 % guarantee: {np.mean(vals < 0.985) * 100:.1f} %",
             f"  years below a 98.3 % guarantee: {np.mean(vals < 0.983) * 100:.1f} %",
             f"  years below a 98.0 % guarantee: {np.mean(vals < 0.98) * 100:.1f} %",
             "  nothing changed from year to year except chance: a",
             "  guarantee set near the mean is missed in many years by a",
             "  fleet doing nothing wrong. The guarantee level, its",
             "  measurement period and any averaging over years are a",
             "  commercial choice made with this spread in view"]
    emit("k_guarantee", lines)


if __name__ == "__main__":
    pr_uncertainty()
    wind_energy_availability()
    ewma_vs_cusum()
    many_tags()
    soiling_from_cleaning()
    trend_years()
    guarantee_risk()
