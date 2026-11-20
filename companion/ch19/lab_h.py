"""Chapter 19, lab H - optimal price shifting with a wear cost: the S1
battery (window 4-36 MWh, 86 % round trip, 20 MW) shifted day by day by
dynamic programming (chapter 5) on teaching prices that vary from day
to day, against the fixed rule of lab D, for four wear costs per MWh
discharged.

Charging is valued at the price of the hour: the energy comes from the
plant, which would otherwise have sold it then (no grid charging; the
plant's midday output covers 20 MW on almost every day, lab B).

Run from the project root:   python -m companion.ch19.lab_h
Writes companion/ch19/expected/h_*.txt and diagrams/data/ch19-dp.csv.
Teaching prices A-273 with daily variation A-295.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch19 import sources as src
from companion.ch19.common import csv, emit
from plantp import dispatch as dp

S1 = src.S1
ETA = math.sqrt(S1["rt_ac"])
LO, HI = 4.0, 36.0


# [start: prices]
def daily_prices(seed: int = 195) -> np.ndarray:
    """365 x 24 teaching prices: the chapter 15 shape with a midday and
    an evening level that change from day to day."""
    rng = np.random.default_rng(seed)
    base = src.prices()[:24]
    out = np.tile(base, (365, 1)).astype(float)
    mid = rng.uniform(0.7, 1.1, 365)
    eve = rng.uniform(0.75, 1.35, 365)
    out[:, 10:15] *= mid[:, None]
    out[:, 18:22] *= eve[:, None]
    return out
# [end: prices]


def rule_day(price) -> tuple[float, float]:
    """Lab D rule on one day: charge 10-15 h at up to 20 MW, discharge
    18-22 h at up to 20 MW; charging valued at the hour's price."""
    e, rev, dis = LO, 0.0, 0.0
    for h in range(24):
        if 10 <= h < 15:
            c = min(20.0, (HI - e) / ETA)
            e += c * ETA
            rev -= price[h] * c
        elif 18 <= h < 22:
            d = min(20.0, (e - LO) * ETA)
            e -= d / ETA
            rev += price[h] * d
            dis += d
    return rev, dis


def compare() -> None:
    pr = daily_prices()
    lines = ["a year of price shifting, rule against optimum (A-295):",
             "  wear u/MWh   rule k u   optimum k u   discharged MWh   cycles"]
    rule_rev = sum(rule_day(pr[d])[0] for d in range(365)) / 1000
    for wear in (0.0, 10.0, 20.0, 30.0):
        rev = dis = 0.0
        for d in range(365):
            r = dp.dp_arbitrage(pr[d], 20.0, LO, HI, LO, ETA, 1.0, wear)
            rev += r.revenue
            dis += float(np.clip(r.power, 0, None).sum())
        rule_net = rule_revenue_net(pr, wear)
        lines.append(f"  {wear:9.0f}   {rule_net:8,.0f}   {rev / 1000:11,.0f}   {dis:14,.0f}"
                     f"   {dis / ETA / (HI - LO):6.0f}")
    lines += [f"  (rule before wear: {rule_rev:,.0f} k u)",
              "  with this price shape the fixed rule is already optimal while",
              "  wear is cheap; with a dearer wear the optimum skips days whose",
              "  spread does not pay the round trip and the wear, and earns",
              "  more with fewer cycles; a wear cost turns the battery's life",
              "  into a price the dispatch can see"]
    emit("h_compare", lines)
    day = int(np.argmax(pr[:, 18:22].mean(axis=1) - pr[:, 10:15].mean(axis=1)))
    r = dp.dp_arbitrage(pr[day], 20.0, LO, HI, LO, ETA, 1.0, 10.0)
    csv("ch19-dp.csv", "h,price,soc", [(h, f"{pr[day][h]:.2f}", f"{r.energy[h + 1]:.2f}")
                                         for h in range(24)])


def rule_revenue_net(pr, wear) -> float:
    tot = 0.0
    for d in range(365):
        rev, dis = rule_day(pr[d])
        tot += rev - wear * dis
    return tot / 1000


if __name__ == "__main__":
    compare()
