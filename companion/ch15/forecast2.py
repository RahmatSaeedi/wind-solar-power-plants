"""Chapter 15, sections E2 and G2 - deeper forecasting: a synthetic
ensemble and its calibration (spread-skill, rank histogram, a fitted
spread inflation), blending persistence and the weather-driven forecast
by lead time, a fairly tested learned correction (modest gains), the
operational data trap (outage hours in the training data), and an
intraday update of the day-ahead schedule.

Run from the project root:   python -m companion.ch15.forecast2
Writes companion/ch15/expected/e2_*.txt, g2_*.txt and diagrams/data/ch15-*.csv.
Synthetic archive A-267; prices A-268; ensemble and outage rules A-270.
"""
from __future__ import annotations

import numpy as np

from companion.ch13 import sources as s13
from companion.ch15 import forecast as fc, lab_g, sources as src
from companion.ch15.common import csv, emit
from plantp import yieldmodel as ym

M = 20                                     # ensemble members


def ensemble(lead: int = 24, seed: int = 180):
    """Members share 70 % of the error variance of the deterministic
    forecast and draw 30 % on their own; the ensemble is therefore
    under-dispersive (A-270)."""
    w_, pv, clear, v, _ = fc.truth()
    rng = np.random.default_rng(seed)
    season = 1 + 0.45 * np.cos(2 * np.pi * (np.arange(8760) / 24 - 15) / 365)
    sd = (0.7 + 0.03 * lead) * season
    common = s13.ar1(8760, 6.0, rng)
    mem = []
    k = np.where(clear > 0.5, pv / np.maximum(clear, 1e-6), 0.0)
    ck = s13.ar1(8760, 4.0, rng)
    for _ in range(M):
        own = s13.ar1(8760, 6.0, rng)
        e = sd * (np.sqrt(0.7) * common + np.sqrt(0.3) * own) + 0.3 * sd * rng.standard_normal()
        wf = fc.farm_curve(np.clip(v + e, 0, None))
        ek = (0.08 + 0.003 * lead) * (np.sqrt(0.7) * ck + np.sqrt(0.3) * s13.ar1(8760, 4.0, rng))
        pf = clear * np.clip(k + ek, 0, 1.05)
        mem.append(wf + pf)
    return np.array(mem), w_ + pv


def rank_hist(mem, obs, mask):
    ranks = (mem[:, mask] < obs[mask][None, :]).sum(axis=0)
    return np.bincount(ranks, minlength=M + 1) / mask.sum()


def calibration() -> None:
    mem, obs = ensemble()
    test = np.arange(8760) >= fc.TEST0
    train = ~test
    mean = mem.mean(axis=0)
    spread = mem.std(axis=0)
    # inflate the spread about the mean to match the training error
    ratio = np.sqrt(np.mean((obs[train] - mean[train]) ** 2) / np.mean(spread[train] ** 2))
    cal = mean[None, :] + ratio * (mem - mean[None, :])
    h0, h1 = rank_hist(mem, obs, test), rank_hist(cal, obs, test)
    lines = ["a 20-member ensemble of the day-ahead hybrid forecast (A-270):",
             f"  test months: RMSE of the ensemble mean {ym.scores(mean, obs, test)['rmse']:.2f} MW;"
             f" mean spread {spread[test].mean():.2f} MW",
             f"  spread inflation fitted on the training months: x {ratio:.2f}",
             "  rank of the observation among the members (21 ranks, flat = 4.8 %):",
             f"    raw ensemble:        lowest {100 * h0[0]:4.1f} %, highest {100 * h0[-1]:4.1f} %,"
             f" middle {100 * h0[10]:4.1f} %",
             f"    inflated ensemble:   lowest {100 * h1[0]:4.1f} %, highest {100 * h1[-1]:4.1f} %,"
             f" middle {100 * h1[10]:4.1f} %"]
    bins = np.quantile(spread[test], [0, 0.25, 0.5, 0.75, 1.0])
    lines.append("  spread-skill (test): spread quartile   mean spread   RMSE of mean")
    for a, b in zip(bins[:-1], bins[1:]):
        m = test & (spread >= a) & (spread <= b)
        lines.append(f"                        {a:5.1f}-{b:5.1f}         {spread[m].mean():6.2f}"
                     f"      {ym.scores(mean, obs, m)['rmse']:6.2f}")
    lines += ["  a U-shaped rank histogram means the truth falls outside the",
              "  ensemble too often: the members agree more than they should;",
              "  inflating the spread on past data flattens it; more spread does",
              "  go with larger errors, so the spread carries information"]
    # CRPS: ensemble form E|X - y| - 0.5 E|X - X'|; a point forecast gives the MAE
    def crps(m_, mask):
        x = m_[:, mask]
        y = obs[mask]
        t1 = np.abs(x - y[None, :]).mean(axis=0)
        t2 = np.abs(x[:, None, :] - x[None, :, :]).mean(axis=(0, 1))
        return float((t1 - 0.5 * t2).mean())
    lines += [f"  CRPS on the test months: raw {crps(mem, test):.2f} MW, inflated"
              f" {crps(cal, test):.2f} MW;",
              f"    ensemble mean as a point forecast (MAE) {np.abs(mean - obs)[test].mean():.2f} MW"]
    emit("e2_ensemble", lines)
    csv("ch15-rankhist.csv", "rank,raw,inflated",
        [(k, f"{100 * a:.2f}", f"{100 * b:.2f}") for k, (a, b) in enumerate(zip(h0, h1))])


def blending() -> None:
    w_, pv, clear, _, _ = fc.truth()
    h = w_ + pv
    train = np.arange(8760) < fc.TEST0
    test = ~train
    lines = ["blending persistence and the weather-driven forecast by lead:",
             "  lead h   weight on NWP   RMSE blend   RMSE NWP   RMSE smart pers."]
    rows = []
    for L in (1, 2, 3, 6, 12):
        sp = ym.persistence(w_, L) + ym.smart_persistence(pv, clear, L)
        nw = sum(fc.nwp(L))
        best, wb = None, 0.0
        for wgt in np.linspace(0, 1, 21):
            f = wgt * nw + (1 - wgt) * sp
            e = ym.scores(f, h, train)["rmse"]
            if best is None or e < best:
                best, wb = e, wgt
        bl = wb * nw + (1 - wb) * sp
        rows.append((L, f"{wb:.2f}"))
        lines.append(f"  {L:4d}       {wb:5.2f}          {ym.scores(bl, h, test)['rmse']:6.2f}"
                     f"     {ym.scores(nw, h, test)['rmse']:6.2f}     {ym.scores(sp, h, test)['rmse']:6.2f}")
    csv("ch15-blend.csv", "lead,w", rows)
    lines += ["  for the next hour the blend leans on the observation; by a few",
              "  hours ahead it leans on the weather forecast: each source wins",
              "  where it knows most; the weights are fitted on past months only"]
    emit("e2_blend", lines)


def learned() -> None:
    """Linear corrections with features known at the issue time: the
    forecast, the hour of day and the season (sine and cosine)."""
    w_, pv, *_ = fc.truth()
    h = w_ + pv
    wf, pf = fc.nwp(24)
    f = wf + pf
    hour = np.arange(8760) % 24
    doy = np.arange(8760) / 24
    train = np.arange(8760) < fc.TEST0
    test = ~train
    feats = {
        "forecast only": [f],
        "+ hour of day": [f, np.sin(2 * np.pi * hour / 24), np.cos(2 * np.pi * hour / 24)],
        "+ hour and season": [f, np.sin(2 * np.pi * hour / 24), np.cos(2 * np.pi * hour / 24),
                              np.sin(2 * np.pi * doy / 365), np.cos(2 * np.pi * doy / 365)],
        "+ wind and PV parts apart": [wf, pf, np.sin(2 * np.pi * hour / 24),
                                      np.cos(2 * np.pi * hour / 24)]}
    lines = ["learned corrections of the day-ahead forecast, features known at",
             "  the issue time only, trained Jan-Aug, tested Sep-Dec:",
             f"  raw forecast                       RMSE {ym.scores(f, h, test)['rmse']:6.2f} MW"]
    for name, X in feats.items():
        A = np.c_[np.ones(8760), np.array(X).T]
        coef, *_ = np.linalg.lstsq(A[train], h[train], rcond=None)
        pred = np.clip(A @ coef, 0, 110)
        lines.append(f"  {name:32s}   RMSE {ym.scores(pred, h, test)['rmse']:6.2f} MW")
    lines += ["  each honest feature buys a few tenths of a megawatt; a season",
              "  feature can even hurt when the test months fall outside the",
              "  training seasons; the big errors are the weather forecast's own,",
              "  which no correction of the plant model removes"]
    emit("e2_learned", lines)


def scada_trap() -> None:
    """The observed output used for training contains outage hours (3 % of
    hours, whole plant at a third of its output) that are not flagged
    (A-270)."""
    w_, pv, *_ = fc.truth()
    h = w_ + pv
    wf, pf = fc.nwp(24)
    f = wf + pf
    rng = np.random.default_rng(181)
    out = rng.random(8760) < 0.03
    obs = np.where(out, h / 3, h)
    train = np.arange(8760) < fc.TEST0
    test = ~train
    res = {}
    for name, mask in (("all hours, outages unflagged", train),
                       ("outage hours flagged and left out", train & ~out)):
        A = np.c_[np.ones(mask.sum()), f[mask]]
        coef, *_ = np.linalg.lstsq(A, obs[mask], rcond=None)
        pred = coef[0] + coef[1] * f
        ok = test & ~out
        res[name] = ym.scores(pred, h, ok)
    lines = ["training on operational data with unflagged outages (A-270):"]
    for name, s in res.items():
        lines.append(f"  {name:36s} bias {s['bias']:+5.2f} MW, RMSE {s['rmse']:5.2f} MW")
    lines += ["  the model learns that the plant sometimes gives a third of its",
              "  output and forecasts low in every normal hour; flag outages,",
              "  ordered curtailment and maintenance in the training data and",
              "  forecast availability separately (chapter 52)"]
    emit("e2_scada", lines)


def reliability() -> None:
    """Observed frequency below each forecast quantile (unconditional
    offsets fitted on Jan-Aug), on the training and the test months."""
    test = np.arange(8760) >= fc.TEST0
    train = ~test
    lines = ["reliability of the day-ahead quantiles (share of hours below):",
             "  level    training months   test months"]
    rows = []
    for tau in (0.1, 0.25, 0.5, 0.75, 0.9):
        q, h = lab_g.quantile_fc(tau)
        a = float(np.mean(h[train] < q[train]))
        b = float(np.mean(h[test] < q[test]))
        rows.append((tau, f"{100 * a:.1f}", f"{100 * b:.1f}"))
        lines.append(f"  {tau:5.2f}       {100 * a:6.1f} %          {100 * b:6.1f} %")
    lines += ["  on the months they were fitted on the quantiles are reliable by",
              "  construction; on the test months every level moves, the median",
              "  most (45.5 % instead of 50 %): autumn is not like the training",
              "  months; reliability is checked on held-out data, level by level"]
    emit("e2_reliability", lines)
    csv("ch15-reliability.csv", "tau,train,test", rows)


def error_map() -> None:
    """RMSE of the raw day-ahead hybrid forecast by month and hour of
    day, over the whole year (no fitting involved)."""
    w_, pv, *_ = fc.truth()
    h = w_ + pv
    f = sum(fc.nwp(24))
    e = (f - h).reshape(365, 24)
    month = src.hourly_inputs()[5].reshape(365, 24)[:, 0]
    grid = np.array([[np.sqrt(np.mean(e[month == m, hh] ** 2)) for hh in range(24)]
                     for m in range(12)])
    by_m = [np.sqrt(np.mean(e[month == m] ** 2)) for m in range(12)]
    by_h = np.sqrt(np.mean(e ** 2, axis=0))
    lines = ["RMSE of the day-ahead hybrid forecast by month and hour (MW):",
             "  by month: " + " ".join(f"{x:4.1f}" for x in by_m[:6]),
             "            " + " ".join(f"{x:4.1f}" for x in by_m[6:]),
             "  by hour:  " + " ".join(f"{x:4.1f}" for x in by_h[:12]),
             "            " + " ".join(f"{x:4.1f}" for x in by_h[12:]),
             f"  largest cell {grid.max():.1f} MW (month {np.unravel_index(grid.argmax(), grid.shape)[0] + 1},"
             f" hour {np.unravel_index(grid.argmax(), grid.shape)[1]:02d}),"
             f" smallest {grid.min():.1f} MW",
             f"  errors follow the season ({by_m[0]:.1f} MW in January, {by_m[6]:.1f} in July)",
             f"  far more than the hour of day ({by_h.min():.1f} to {by_h.max():.1f} MW): the",
             "  winter wind is strong and its forecast uncertain; reserve and",
             "  quantiles can follow the month"]
    emit("e2_errmap", lines)
    csv("ch15-errmap.csv", "x,y,c",
        [(hh, m + 1, f"{grid[m, hh]:.2f}") for m in range(12) for hh in range(24)])


def newsvendor() -> None:
    """Revenue of the four months against the offered quantile, on the
    training and the test months (no battery)."""
    test = np.arange(8760) >= fc.TEST0
    train = ~test
    lines = ["revenue against the offered quantile (no battery, A-268 prices):",
             "  quantile   training k u (8 months)   test k u (4 months)"]
    rows = []
    for tau in np.arange(0.10, 0.91, 0.05):
        q, h = lab_g.quantile_fc(float(tau))
        a = lab_g.settle(q[train], h[train], False)[3] / 1e3
        b = lab_g.settle(q[test], h[test], False)[3] / 1e3
        rows.append((f"{tau:.2f}", f"{a:.0f}", f"{b:.0f}"))
        lines.append(f"  {tau:8.2f}   {a:12,.0f}              {b:10,.0f}")
    best_a = max(rows, key=lambda x: float(x[1]))[0]
    best_b = max(rows, key=lambda x: float(x[2]))[0]
    lines += [f"  best quantile: training {best_a}, test {best_b}; theory 1/3",
              "  the curve is flat near its top: a quantile a little off costs",
              "  little, a median offer costs more, a high quantile much more"]
    emit("g2_newsvendor", lines)
    csv("ch15-newsvendor.csv", "tau,train,test", rows)


def value() -> None:
    """What a better forecast is worth: errors of the day-ahead forecast
    scaled by 0.9 and 0.8 (A-270), and a perfect forecast; P33 offers,
    no battery, test months."""
    w_, pv, *_ = fc.truth()
    h = w_ + pv
    wf, pf = fc.nwp(24)
    f0 = wf + pf
    test = np.arange(8760) >= fc.TEST0
    train = ~test
    lines = ["the value of a better day-ahead forecast (test months, P33 offer,",
             "  no battery):",
             "  forecast                  RMSE MW    revenue k u"]
    base = None
    gains = []
    for name, s_ in (("as built", 1.0), ("errors x 0.9", 0.9), ("errors x 0.8", 0.8),
                     ("perfect", 0.0)):
        f = h + s_ * (f0 - h)
        q = np.quantile((h - f)[train], 1 / 3)
        sch = np.clip(f + q, 0, 100.0)
        rev = lab_g.settle(sch[test], h[test], False)[3] / 1e3
        base = rev if base is None else base
        gains.append(rev - base)
        lines.append(f"  {name:22s}   {ym.scores(f, h, test)['rmse']:7.2f}    {rev:8,.0f}"
                     f"  ({rev - base:+5,.0f})")
    lines += [f"  errors 10 % smaller are worth about {gains[1]:.0f} k u in these four",
              "  months at these prices: a ceiling for what a better forecast",
              f"  may cost; a perfect one is worth {gains[3]:.0f} k u, the whole cost of",
              "  forecast error in these months: no forecast can earn more"]
    emit("g2_value", lines)


def intraday() -> None:
    """Day-ahead P33 schedule, then re-schedule hours 6 h ahead with the
    6 h blend (weight 0.9 on the weather forecast, e2_blend) at no cost
    for the move (teaching)."""
    sch, h = lab_g.quantile_fc(1 / 3)
    w_, pv, clear, _, _ = fc.truth()
    sp = ym.persistence(w_, 6) + ym.smart_persistence(pv, clear, 6)
    nw = sum(fc.nwp(6))
    blend = np.where(np.isfinite(sp), 0.9 * nw + 0.1 * sp, nw)
    train = np.arange(8760) < fc.TEST0
    q = np.quantile((h - blend)[train], 1 / 3)
    sch2 = np.clip(blend + q, 0, 100)
    test = ~train
    lines = ["day-ahead P33 against an intraday update 6 hours ahead (test):",
             "  schedule              short MWh   surplus MWh   revenue k u"]
    for name, s in (("day-ahead only", sch), ("intraday update", sch2)):
        sh, su, so, rev = lab_g.settle(s[test], h[test], False)
        lines.append(f"  {name:20s}   {sh:9,.0f}    {su:9,.0f}    {rev / 1e3:8,.0f}")
    lines += ["  updating the schedule closer to the hour cuts both shortfall and",
              "  surplus: the market or grid rules decide whether such updates",
              "  are possible and at what cost (chapters 19 and 28)"]
    emit("g2_intraday", lines)


if __name__ == "__main__":
    calibration()
    blending()
    learned()
    scada_trap()
    reliability()
    error_map()
    newsvendor()
    value()
    intraday()
