"""Chapter 15, section G - forecast-to-dispatch lab: the held-out months
(Sep-Dec) scheduled day ahead from the forecast distribution (P50, or a
lower quantile), delivered against the schedule with and without the S1
battery absorbing the deviations, imbalance energy and its teaching cost,
and the reserve the uncertainty interval asks for.

Run from the project root:   python -m companion.ch15.lab_g
Writes companion/ch15/expected/g_*.txt and diagrams/data/ch15-*.csv.
Teaching prices A-268: day-ahead 50 u/MWh, shortfall 100 u/MWh, surplus
sold at 25 u/MWh; S1 battery 20 MW, 32 MWh usable, 86 % round trip.
"""
from __future__ import annotations

import numpy as np

from companion.ch15 import forecast as fc
from companion.ch15.common import csv, emit

PRICE, SHORT, SURPLUS = 50.0, 100.0, 25.0


def quantile_fc(tau: float):
    w_, pv, *_ = fc.truth()
    h = w_ + pv
    wf, pf = fc.nwp(24)
    f = wf + pf
    train = np.arange(8760) < fc.TEST0
    q = np.quantile((h - f)[train], tau)
    return np.clip(f + q, 0, 100.0), h


# [start: settle]
def settle(schedule, actual, battery: bool):
    """Deliver against the schedule hour by hour; the battery (if any)
    fills shortfalls and stores surpluses within its power and energy."""
    soc, eta = 16.0, 0.86 ** 0.5
    short = surplus = 0.0
    sold = 0.0
    for s, a in zip(schedule, actual):
        d = min(a, 100.0) - s
        if battery:
            if d < 0:
                dis = min(-d, 20.0, soc * eta)
                soc -= dis / eta
                d += dis
            elif d > 0:
                ch = min(d, 20.0, (32.0 - soc) / eta)
                soc += ch * eta
                d -= ch
        if d < 0:
            short -= d
        else:
            surplus += d
        sold += s
    revenue = sold * PRICE - short * SHORT + surplus * SURPLUS
    return short, surplus, sold, revenue
# [end: settle]


def policies() -> None:
    test = np.arange(8760) >= fc.TEST0
    lines = ["day-ahead schedules on the test months (Sep-Dec), teaching prices:",
             "  schedule        battery   scheduled GWh  short MWh  surplus MWh  revenue k u"]
    rows = []
    for name, tau in (("P50", 0.50), ("P40", 0.40), ("P30", 0.30)):
        sch, h = quantile_fc(tau)
        for bat in (False, True):
            sh, su, so, rev = settle(sch[test], h[test], bat)
            lines.append(f"  {name:14s}  {'yes' if bat else 'no ':3s}       {so / 1e3:8.2f}     {sh:8,.0f}"
                         f"    {su:8,.0f}     {rev / 1e3:8,.0f}")
            rows.append((f"{name}{'+B' if bat else ''}", f"{sh:.0f}", f"{su:.0f}", f"{rev / 1e3:.0f}"))
    csv("ch15-dispatch.csv", "case,short,surplus,revenue", rows)
    lines += ["  a lower quantile sells less day ahead but is short less often;",
              "  with a shortfall price twice the day-ahead price the best",
              "  quantile is near P33 (a third of the hours may fall short);",
              "  the battery absorbs part of the deviation either way, but a",
              "  32 MWh battery cannot carry a day of forecast error"]
    emit("g_policies", lines)


def reserve() -> None:
    w_, pv, *_ = fc.truth()
    h = w_ + pv
    wf, pf = fc.nwp(24)
    f = wf + pf
    train = np.arange(8760) < fc.TEST0
    test = ~train
    q10, q50 = np.quantile((h - f)[train], [0.10, 0.50])
    down = (f + q50) - np.clip(f + q10, 0, None)
    lines = ["downward reserve from the forecast interval (P50 - P10), test months:",
             f"  mean {down[test].mean():.1f} MW; 95 % of hours below {np.quantile(down[test], 0.95):.1f} MW",
             f"  the S1 battery's 20 MW covers it in {100 * np.mean(down[test] <= 20):.0f} % of the hours",
             "  the forecast's uncertainty becomes a capacity to hold back: a",
             "  battery, a margin on the schedule, or bought reserve (chapters",
             "  17-19 and 34); a sharper forecast is cheaper reserve"]
    emit("g_reserve", lines)


if __name__ == "__main__":
    policies()
    reserve()
