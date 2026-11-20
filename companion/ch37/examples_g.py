"""Chapter 37, lesson G (forecast monitoring): errors by technology and by
the hours scored, ramp events, a forecast feed with gaps, and why the
forecast with the lower RMSE can cost more.

Run from the project root:   python -m companion.ch37.examples_g
Writes companion/ch37/expected/g2_*.txt and diagrams/data/ch37-*.csv.
Synthetic forecasts (A-414); teaching prices (A-415).
"""
from __future__ import annotations

import numpy as np

from companion.ch37 import sources as src
from companion.ch37.common import csv, emit
from plantp import yieldmodel as ym


def tech_forecasts(seed: int = 383):
    """Day-ahead forecasts of PV and wind (MW), synthetic errors."""
    y = src.operating_year()
    rng = np.random.default_rng(seed)
    pv, w = y["pv_act"], y["w_act"]
    day = y["poa_true"] > 20
    e_pv = np.convolve(rng.normal(0, 4.0, 8760 + 3), np.ones(4) / 2, "valid")[:8760]
    e_w = np.convolve(rng.normal(0, 7.0, 8760 + 5), np.ones(6) / np.sqrt(6), "valid")[:8760]
    pv_fc = np.clip(pv + np.where(day, e_pv, 0.0), 0, 50)
    w_fc = np.clip(w + e_w, 0, 60)
    return pv, w, pv_fc, w_fc, day


def by_technology() -> None:
    pv, w, pv_fc, w_fc, day = tech_forecasts()
    s_pv_all = ym.scores(pv_fc, pv)
    s_pv_day = ym.scores(pv_fc, pv, day)
    s_w = ym.scores(w_fc, w)
    rows = [("PV, all 8,760 hours", s_pv_all, 50.0), ("PV, daylight hours only", s_pv_day, 50.0),
            ("wind, all hours", s_w, 60.0)]
    lines = ["day-ahead errors by technology (synthetic, % of capacity)",
             "  series                     hours   MAE %   RMSE %"]
    for name, s, cap in rows:
        lines.append(f"  {name:25s} {s['n']:6d}   {s['mae'] / cap * 100:5.1f}"
                     f"   {s['rmse'] / cap * 100:6.1f}")
    lines += ["  the night hours, where a PV forecast of zero is always",
              "  right, nearly halve PV's average error: a score states",
              "  which hours it covers. Wind and PV are scored apart,",
              "  each against its own capacity - a plant total hides",
              "  which forecast needs work"]
    emit("g2_tech", lines)


def ramp_events() -> None:
    pv, w, pv_fc, w_fc, _ = tech_forecasts()
    obs, fc = pv + w, pv_fc + w_fc
    th = 15.0
    o = ym.ramps(obs, th, 1)
    f = ym.ramps(fc, th, 1)
    t = ym.ramp_table(o, f)
    # a ramp forecast one hour early or late still counts as a hit if +/- 1 h
    near = 0
    idx = np.where(o != 0)[0]
    for i in idx:
        lo, hi = max(i - 1, 0), min(i + 2, 8760)
        near += int(np.any(f[lo:hi] == o[i]))
    lines = [f"ramp events of the plant output: change above {th:.0f} MW",
             "  within one hour (same hour, same sign):",
             f"    observed ramps {t['hits'] + t['misses']}, forecast hits {t['hits']},"
             f" misses {t['misses']}, false alarms {t['false']}",
             f"    probability of detection {t['pod']:.2f}, false-alarm ratio {t['far']:.2f}",
             "  the same ramps, a forecast ramp up to 1 h early or late",
             f"    allowed: caught {near} of {len(idx)} ({near / max(len(idx), 1) * 100:.0f} %)",
             "  an hourly RMSE says nothing about ramps; ramps are scored",
             "  as events, and the timing tolerance is part of the",
             "  definition - the same forecast looks poor or useful",
             "  depending on it"]
    emit("g2_ramps", lines)


def feed_gaps() -> None:
    pv, w, pv_fc, w_fc, _ = tech_forecasts()
    obs, fc = pv + w, pv_fc + w_fc
    # the feed fails in stormy hours (largest wind changes), 4 % of hours
    dw = np.abs(np.diff(w, prepend=w[0]))
    gap = np.zeros(8760, bool)
    gap[np.argsort(dw)[-int(0.04 * 8760):]] = True
    used = np.where(gap, ym.persistence(obs, 24), fc)       # fallback the desk used
    used = np.where(np.isfinite(used), used, fc)
    s_av = ym.scores(fc, obs, ~gap)
    s_op = ym.scores(used, obs)
    lines = ["a forecast feed that fails in 4 % of hours - the stormy ones",
             f"  RMSE on the hours it arrived:                   {s_av['rmse']:5.2f} MW",
             f"  RMSE of what the desk actually used (gaps filled",
             f"    with yesterday's value):                     {s_op['rmse']:5.2f} MW",
             "  the provider's score leaves out the hours it missed, and",
             "  they are the hard ones; the plant scores the chain it",
             "  operated, with the fallback, and reports the feed's",
             "  completeness beside the score"]
    emit("g2_gaps", lines)


def skill_vs_cost(seed: int = 385) -> None:
    pv, w, pv_fc, w_fc, _ = tech_forecasts()
    obs = pv + w
    rng = np.random.default_rng(seed)
    a = obs + rng.normal(0, 8.0, 8760) + 3.0          # tighter, leans high
    b = obs + rng.normal(0, 10.0, 8760) - 4.0         # wider, leans low
    short, long_ = 30.0, 10.0           # u/MWh: short (delivered < sold), long
    lines = ["two day-ahead forecasts used to sell the plant's output",
             f"  imbalance price (teaching): short {short:.0f} u/MWh, long {long_:.0f} u/MWh",
             "  forecast   RMSE MW   bias MW   imbalance cost k u/yr"]
    rows = []
    for name, f in (("A", a), ("B", b)):
        s = ym.scores(f, obs)
        d = obs - f                      # delivered minus sold
        cost = np.sum(np.where(d < 0, -d * short, d * long_)) / 1000
        rows.append((name, s["rmse"], s["bias"], cost))
        lines.append(f"  {name:9s}  {s['rmse']:7.2f}   {s['bias']:7.2f}   {cost:20,.0f}")
    tight = min(rows, key=lambda r: r[1])[0]
    better = min(rows, key=lambda r: r[3])[0]
    lines += [f"  {tight} has the lower RMSE; {better} is the cheaper one to sell with:",
              "  with short positions costing three times long ones, a",
              "  forecast that leans low sells less than the plant",
              "  delivers and pays the cheap price. Skill and money are",
              "  different measures; the plant reports both and never",
              "  calls either a guarantee of what dispatch or delivery",
              "  will be"]
    emit("g2_cost", lines)


if __name__ == "__main__":
    by_technology()
    ramp_events()
    feed_gaps()
    skill_vs_cost()
