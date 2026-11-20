"""Chapter 20, section E - forecasting, scheduling and dispatch as three
functions on three horizons: forecast errors of the POC export by lead,
imbalance penalties of a schedule from each horizon, a bid that knows
the penalties are unequal (newsvendor), upward reserve and SOC needed to
cover forecast shortfall, and a year of battery plans made from the
day-ahead forecast, from an intraday update and from perfect foresight.

Run from the project root:   python -m companion.ch20.examples_e
Writes companion/ch20/expected/e_*.txt and diagrams/data/ch20-*.csv.
Teaching values A-299 to A-302; forecasts from chapter 15 (A-267).
"""
from __future__ import annotations

import numpy as np

from companion.ch20 import examples_b as eb, sources as src
from companion.ch20.common import csv, emit
from plantp import control as ct

L = src.LIMITS
P = src.IMBALANCE
TEST = slice(243 * 24, 8760)          # September-December (as chapter 15)
TRAIN = slice(0, 243 * 24)


def export(x):
    return np.clip(x, 0, L["export_mw"])


def horizons() -> None:
    act = export(src.poc_actual())
    lines = ["forecast error of the POC export by horizon (test months):",
             "  horizon              lead h   MAE MW   RMSE MW   P5 err   P95 err"]
    rows = []
    pers = np.roll(act, 1)
    cases = [("day-ahead", 24, export(src.poc_forecast(24))),
             ("intraday", 4, export(src.poc_forecast(4))),
             ("persistence (1 h)", 1, pers)]
    for name, lead, f in cases:
        e = (f - act)[TEST]
        lines.append(f"  {name:20s} {lead:6d}   {np.abs(e).mean():6.1f}   {np.sqrt((e ** 2).mean()):7.1f}"
                     f"   {np.percentile(e, 5):6.1f}   {np.percentile(e, 95):7.1f}")
        rows.append((lead, f"{np.abs(e).mean():.2f}"))
    lines += ["  scheduling uses the forecast of its horizon: the day-ahead",
              "  plan is made once, the intraday plan corrects it, and",
              "  real-time dispatch uses what is measured now; each layer",
              "  keeps the decisions of the one above unless they are",
              "  infeasible (section A)"]
    emit("e_horizons", lines)


def imbalance_cost() -> None:
    act = export(src.poc_actual())
    da = export(src.poc_forecast(24))
    idf = export(src.poc_forecast(4))
    lines = ["imbalance penalty of a year by the schedule sent (A-301:",
             f"  short {P['short']:.0f} u/MWh, long {P['long']:.0f} u/MWh):",
             "  schedule                 short MWh   long MWh   penalty k u"]
    for name, sch in (("day-ahead forecast", da), ("intraday update", idf)):
        dev = act - sch
        pen = ct.imbalance(sch, act, P["short"], P["long"])
        lines.append(f"  {name:22s} {np.clip(-dev, 0, None).sum():11,.0f}"
                     f" {np.clip(dev, 0, None).sum():10,.0f} {pen / 1000:13.0f}")
    lines += ["  the intraday update cuts the penalty by about a quarter;",
              "  where the market allows changes after the day-ahead offer,",
              "  re-scheduling is the cheapest imbalance tool"]
    emit("e_imbalance", lines)


# [start: bid]
def bid_offsets(f, act, q: float, bins=np.arange(0, 110, 10)):
    """Offset to add to the forecast in each forecast bin so that the
    bid is the q-quantile of the actual export (trained on Jan-Aug)."""
    k = np.digitize(f, bins)
    off = np.zeros(len(bins) + 1)
    for b in range(len(bins) + 1):
        m = (k[TRAIN] == b)
        if m.sum() > 20:
            off[b] = np.quantile((act - f)[TRAIN][m], q)
    return off[k]
# [end: bid]


def bidding() -> None:
    act = export(src.poc_actual())
    da = export(src.poc_forecast(24))
    q_star = P["long"] / (P["short"] + P["long"])
    lines = ["day-ahead bid that knows short costs more than long:",
             f"  best quantile = long / (short + long) = {q_star:.2f}",
             "  bid                      energy bid GWh   penalty k u (Sep-Dec)"]
    for name, q in (("forecast as is", None), ("median by bin", 0.5),
                    (f"quantile {q_star:.2f} by bin", q_star)):
        bid = da if q is None else np.clip(da + bid_offsets(da, act, q), 0, 100)
        pen = ct.imbalance(bid[TEST], act[TEST], P["short"], P["long"])
        lines.append(f"  {name:24s} {bid[TEST].sum() / 1000:14.1f}   {pen / 1000:12.0f}")
    rows = []
    for q in np.arange(0.05, 0.96, 0.05):
        bid = np.clip(da + bid_offsets(da, act, q), 0, 100)
        pen = ct.imbalance(bid[TEST], act[TEST], P["short"], P["long"])
        rows.append((f"{q:.2f}", f"{pen / 1000:.1f}"))
    csv("ch20-bid.csv", "q,pen", rows)
    lines += ["  bidding low lowers the penalty although less energy is",
              "  sold ahead: the rest is sold as 'long' at a small",
              "  discount; the rule is chapter 15's newsvendor applied by",
              "  the scheduling function, and it holds only while the",
              "  penalties stay as assumed (A-301)"]
    emit("e_bidding", lines)


def reserve_from_forecast() -> None:
    act = export(src.poc_actual())
    idf = export(src.poc_forecast(4))
    short = (idf - act)                                    # + = plant short
    bins = [(0, 20), (20, 40), (40, 60), (60, 80), (80, 101)]
    lines = ["upward reserve to cover the intraday forecast's shortfall:",
             "  forecast MW   hours   P90 short MW   P95 short MW   P99 short MW"]
    rows = []
    for lo, hi in bins:
        m = (idf >= lo) & (idf < hi)
        s = short[m]
        p90, p95, p99 = np.percentile(s, [90, 95, 99])
        lines.append(f"  {lo:3d}-{hi - 1:<3d}      {m.sum():5d}   {p90:12.1f}   {p95:12.1f}"
                     f"   {p99:12.1f}")
        rows.append(((lo + hi) / 2, f"{p90:.2f}", f"{p95:.2f}", f"{p99:.2f}"))
    e4 = np.array([short[k:k + 4].clip(0).sum() for k in range(18, 8760, 24)])
    cover = (e4 <= 32.0 * L["eta"]).mean() * 100
    lines += ["  the reserve that covers 95 % of hours grows with the forecast",
              "  level and passes the battery converter (20 MW) above 60 MW;",
              f"  evening shortfall 18-22 h: P50 {np.median(e4):.0f}, "
              f"P95 {np.percentile(e4, 95):.0f} MWh;",
              f"  the 32 MWh window covers {cover:.0f} % of evenings; the rest is an",
              "  imbalance cost or a lower schedule"]
    emit("e_reserve", lines)
    csv("ch20-reserve.csv", "f,p90,p95,p99", rows)


# [start: rolling]
def year_of_plans(fc: np.ndarray, wear: float = 10.0):
    """Plan each day from the forecast fc (charge only from the plant,
    discharge within the export room), execute with the controller on
    the actual output, and return energy, revenue and alarms."""
    act = np.clip(src.poc_actual(), 0, None)
    cap = eb.caps()
    price = src.prices()
    c = ct.Controller(e=L["e_min"])
    rev = curt = 0.0
    for d in range(365):
        h = slice(d * 24, d * 24 + 24)
        f = np.clip(fc[h], 0, None)
        _, _, plan = ct.dp_schedule(price[h], np.minimum(f, L["bess_mw"]),
                                    np.clip(cap[h] - f, 0, None),
                                    L["bess_mw"], L["e_min"], L["e_max"],
                                    round(c.e), L["eta"], wear=wear,
                                    e_end=L["e_min"])
        for k in range(24):
            t = d * 24 + k
            r = c.step(t, act[t], plan[k], cap[t], True)
            rev += r["export"] * price[t]
            curt += r["curtailed"]
    return rev, curt, len(c.alarms)
# [end: rolling]


def plans() -> None:
    act = np.clip(src.poc_actual(), 0, None)
    cap = eb.caps()
    no_bess = float((np.minimum(act, cap) * src.prices()).sum())
    cases = [("perfect foresight", act), ("day-ahead forecast", src.poc_forecast(24)),
             ("intraday forecast", src.poc_forecast(4))]
    best = None
    lines = ["a year of battery plans executed by the controller (S1):",
             f"  export revenue without the battery {no_bess / 1000:,.0f} k u",
             "  plan made from          battery adds k u   share %   curtailed   alarms"]
    for name, fc in cases:
        rev, curt, n = year_of_plans(fc)
        gain = rev - no_bess
        best = gain if best is None else best
        lines.append(f"  {name:22s} {gain / 1000:16.0f}   {gain / best * 100:7.1f}"
                     f"   {curt:9,.0f}   {n:6d}")
    lines += ["  plans from the forecasts keep almost all of the value:",
              "  shifting is decided by prices known a day ahead, and the",
              "  controller fills the battery from curtailment whatever the",
              "  plan says; the mismatches show as alarms (charge or",
              "  discharge limited) that the operator must read"]
    emit("e_plans", lines)


if __name__ == "__main__":
    horizons()
    imbalance_cost()
    bidding()
    reserve_from_forecast()
    plans()
