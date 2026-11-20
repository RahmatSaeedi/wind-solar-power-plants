"""Chapter 31, lesson I: two planning tools - the operating characteristic
of a sampling plan at receiving, and how long the erection campaign
takes when it starts in different months of the data-pack year.

Run from the project root:   python -m companion.ch31.examples_i
Writes companion/ch31/expected/i_*.txt and diagrams/data/ch31-campaign.csv.
Teaching values (A-365, A-366); sampling plans come from the contract and
ISO 2859-1 (STD-076), the campaign plan from the schedule model.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch31 import sources as src  # noqa: F401  (puts plantp on the path)
from companion.ch31.common import csv, emit
from plantp import datapack


def oc_curve() -> None:
    n, c = 50, 1
    lines = ["operating characteristic of a sampling plan (n = 50, accept on <= 1)",
             "  lot defect rate %   probability the lot is accepted"]
    for p in (0.5, 1, 2, 4, 6, 10):
        q = p / 100
        pa = sum(math.comb(n, k) * q ** k * (1 - q) ** (n - k) for k in range(c + 1))
        lines.append(f"  {p:17.1f}   {pa:31.2f}")
    lines += ["  a lot with 4 % defective bolts still passes four times in",
              "  ten: sampling protects against bad lots on average, not",
              "  against every bad lot - which is why critical items",
              "  (anchor bolts, lifting gear) get certificates and 100 %",
              "  checks, and sampling is kept for the rest"]
    emit("i_oc", lines)


def campaign(seed: int = 31) -> None:
    d = datapack.load_hourly()
    v = d["ws_100m_ms"].to_numpy()
    n_hours = v.size
    tasks = [(10.0, 6, 1), (8.0, 8, 1), (12.0, 4, 4)]      # (limit, hours, count) per turbine:
    #   nacelle lift, rotor lift, tower sections; plus fixed work between them
    fixed_h = 13 * 24 - 30                    # 13 crane days a turbine less the 30 lift hours
    rows = []
    lines = ["erection campaign length by start month (one crane, data-pack wind)",
             "  start month   campaign days   weather waiting days"]
    for month in range(1, 13):
        t = int(np.argmax(d.index.month == month))
        start, wait = t, 0
        for _ in range(12):
            t += fixed_h
            for limit, hours, count in tasks:
                for _ in range(count):
                    run = 0
                    while True:
                        if v[t % n_hours] < limit:
                            run += 1
                            if run == hours:
                                break
                        else:
                            wait += 1 + run
                            run = 0
                        t += 1
                    t += 1
        days = (t - start) / 24
        rows.append((month, round(days, 1), round(wait / 24, 1)))
        lines.append(f"  {month:11d}   {days:13.0f}   {wait / 24:20.0f}")
    csv("ch31-campaign.csv", "month,days,wait", rows)
    best = min(rows, key=lambda r: r[1])
    worst = max(rows, key=lambda r: r[1])
    lines += ["  156 crane days of work (int_campaign) plus the weather waits",
              f"  best start month {best[0]} ({best[1]:.0f} days), worst {worst[0]}"
              f" ({worst[1]:.0f} days)",
              "  the same twelve turbines take two and a half weeks longer when",
              "  the lifts fall in the windy months: the start date is",
              "  a design choice of the schedule (ch 22, 49), and one",
              "  data year is a teaching sample, not a forecast"]
    emit("i_campaign", lines)


if __name__ == "__main__":
    oc_curve()
    campaign()
