"""Chapter 37 - small worked examples (E-lines) and the numerical answers
of the exercises (P-lines), each computed here.

Run from the project root:   python -m companion.ch37.worked
Writes companion/ch37/expected/worked.txt and solutions.txt.
"""
from __future__ import annotations

import math

from companion.ch37.common import emit
from plantp import performance as pf


def worked() -> None:
    lines = [f"E01 PR, 9,000 MWh, 60 MWp, 180 kWh/m2: {pf.performance_ratio(9e6, 60_000, 180):.3f}",
             f"E02 PR 0.80 at 45 C cell, -0.35 %/K, to 25 C: {pf.pr_temperature(0.80, 45):.3f}",
             f"E03 time availability, 700 up of 720, 10 excluded: "
             f"{pf.time_availability(700, 720, 10) * 100:.2f} %",
             f"E04 production availability, 950 MWh made, 50 lost: "
             f"{pf.energy_availability(950, 50) * 100:.1f} %",
             f"E05 MTBF, 3 failures in 30,000 h of exposure: {30_000 / 3:,.0f} h",
             f"E06 events (0,4),(2,6),(10,12) merged: {pf.event_hours([(0, 4), (2, 6), (10, 12)], 0, 24):.0f} h"]
    emit("worked", lines)


def solutions() -> None:
    lo, hi = pf.rate_interval(3, 50_000, 0.9)
    out = [f"P01 PR, 10,500 MWh, 60.06 MWp, 210 kWh/m2: "
           f"{pf.performance_ratio(10.5e6, 60_060, 210):.3f}",
           f"P02 specific yield of 107,426 MWh on 60.06 MWp: {107_426_000 / 60_060:,.0f} kWh/kWp",
           f"P03 capacity factor, 192,786 MWh on 60 MW: {192_786 / (60 * 8760) * 100:.1f} %",
           f"P04 PR 0.785 at 54 C, to 25 C: {pf.pr_temperature(0.785, 54.1):.3f}",
           f"P05 time availability 8,500 of 8,760 h, 60 h excluded: "
           f"{pf.time_availability(8500, 8760, 60) * 100:.2f} %",
           f"P06 production availability 4,800 MWh, 120 lost, 40 excluded: "
           f"{pf.energy_availability(4800, 120, 40) * 100:.2f} %",
           f"P07 50 h outage in a 744 h month: {(1 - 50 / 744) * 100:.2f} %",
           f"P08 same over a year: {(1 - 50 / 8760) * 100:.2f} %",
           f"P09 downtime 08:00 trip to 15:30 restart: {15.5 - 8:.1f} h",
           f"P10 MTBF censored, failed 2,000 and 6,000 h, 6 running at 10,000 h: "
           f"{pf.mtbf_censored([2000, 6000], [10000] * 6):,.0f} h",
           f"P11 naive mean of the failed ones: {(2000 + 6000) / 2:,.0f} h",
           f"P12 90 % interval, 3 failures in 50,000 h: "
           f"{lo * 1e5:.2f}-{hi * 1e5:.2f} per 1e5 h",
           f"P13 Weibull share failed at t = scale with k = 2.5: {(1 - math.exp(-1)) * 100:.1f} %",
           f"P14 Crow-AMSAA, failures at 100, 400, 900 h, end 1,000: "
           f"{pf.crow_amsaa_beta([100, 400, 900], 1000):.2f}",
           f"P15 skill, RMSE 14.4 against persistence 24.8: {1 - 14.4 / 24.8:.2f}",
           f"P16 skill, RMSE 8.8 against 8.8: {1 - 8.8 / 8.8:.2f}",
           f"P17 coverage, 830 of 900 hours inside: {830 / 900 * 100:.1f} %",
           f"P18 service availability, 500 called, 10 excluded, 6 failed: "
           f"{(500 - 10 - 6) / (500 - 10) * 100:.2f} %",
           f"P19 first-order response, tau 3 s, delay 1 s: 90 % at {1 + 3 * math.log(10):.1f} s",
           f"P20 CUSUM steps of 0.75 to pass h = 2: {math.floor(2 / 0.75) + 1} days",
           f"P21 loss share, 314 + 339 + 163 MWh of 301,494: "
           f"{(314 + 339 + 163) / 301_494 * 100:.2f} %",
           f"P22 fault 10 h with 3 h external inside, 744 h month: "
           f"{(1 - 7 / 741) * 100:.3f} %",
           f"P23 planned 24 h, took 30 h: forced {30 - 24} h",
           f"P24 two turbines added to 12: bias about -{2 / 12 * 22.0:.1f} MW at 22 MW"
           " mean wind",
           f"P25 alarms acted on, 410 of 3,420: {410 / 3420 * 100:.0f} %"]
    emit("solutions", out)


def more_solutions() -> None:
    k, lam = 2.89, 56_180.0
    sun = "equal sun each day"
    out = [f"P26 robust z, value 1,726, median 1,788, MAD x 1.4826 = 9.1: "
           f"{(1726 - 1788) / 9.1:.1f}",
           f"P27 region-2 loss 5 % on 6,000 of 7,000 MWh made there: {0.05 * 6000:,.0f} MWh",
           f"P28 reviewer hours, 12 flags a day at 15 min: {12 * 0.25:.1f} h",
           f"P29 precision, 3 true of 12 flags: {3 / 12:.2f}",
           f"P30 PR on valid hours, 8,000 MWh, 60.06 MWp, 163 kWh/m2: "
           f"{pf.performance_ratio(8e6, 60_060, 163):.3f}",
           f"P31 completeness, 26 of 31 days: {26 / 31 * 100:.1f} %",
           f"P32 year-on-year rate, PR 0.850 then 0.846: {(0.846 / 0.850 - 1) * 100:.2f} %/yr",
           f"P33 Weibull k {k}, scale {lam:,.0f} h: share failed by 40,000 h "
           f"{(1 - math.exp(-(40_000 / lam) ** k)) * 100:.0f} %",
           f"P34 Weibull hazard ratio at 40,000 vs 20,000 h, k {k}: "
           f"{(40_000 / 20_000) ** (k - 1):.2f}",
           f"P35 substation 10 h x 12 turbines in 12 x 8,760 h: "
           f"{10 * 12 / (12 * 8760) * 100:.3f} % of turbine time",
           f"P36 waiting 1,230 h halved, 12 x 8,760 h: availability +"
           f"{615 / (12 * 8760) * 100:.2f} points",
           f"P37 PV MAE 1.5 MW over 8,760 h, 0 at night (4,504 h): daylight MAE "
           f"{1.5 * 8760 / 4256:.2f} MW",
           f"P38 POD, 640 hits, 220 misses: {640 / 860:.2f}",
           f"P39 FAR, 640 hits, 398 false: {398 / (640 + 398):.2f}",
           f"P40 imbalance, 5 MWh short at 30 and 8 MWh long at 10: {5 * 30 + 8 * 10} u",
           f"P41 delivered share, 2.401 of 2.500 MWh: {2.401 / 2.5 * 100:.2f} %",
           f"P42 recovery, 1.00 MWh at 3 MW x 0.94: {1.0 / (3 * 0.94) * 60:.0f} min",
           f"P43 service availability, 600 h, 14 excluded, 9 failed: "
           f"{(586 - 9) / 586 * 100:.2f} %",
           f"P44 penalty, 2 certain + 2 disputed hours at 500 u: "
           f"{2 * 500:,} to {4 * 500:,} u",
           f"P45 April soiling: 0 to 6 % linear, mean loss {6 / 2:.1f} %",
           f"P46 June block out: 10 % for 9 of 30 days, month loss {0.1 * 9 / 30 * 100:.1f} %",
           f"P47 sensor 8 % low on 20 of 31 days, {sun}: month PR x "
           f"{1 / (1 - 0.08 * 20 / 31):.3f}",
           f"P48 August cap 80 MW, 40 h at 84 MW mean: {40 * (84 - 80)} MWh not taken",
           f"P49 time availability of a 48 h stop in 744 h: "
           f"{(1 - 48 / 744) * 100:.2f} %",
           f"P50 production availability, 1,500 MWh month, 179 MWh lost: "
           f"{pf.energy_availability(1500 - 179, 179) * 100:.2f} %"]
    emit("solutions2", out)


if __name__ == "__main__":
    worked()
    solutions()
    more_solutions()
