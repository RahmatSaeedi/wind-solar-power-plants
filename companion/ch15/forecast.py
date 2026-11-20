"""Chapter 15, section E - short-term forecasts of the Plant P hybrid output
and their validation: a synthetic weather-driven forecast archive (wind
speed and clear-sky index errors that grow with the lead time, timing
errors on wind ramps), persistence baselines, error by horizon and skill,
quantile intervals from the training months with their coverage on the
held-out months, two kinds of data leakage, ramps and drift.

Run from the project root:   python -m companion.ch15.forecast
Writes companion/ch15/expected/e_*.txt and diagrams/data/ch15-*.csv.
Train January-August, test September-December; A-267 (forecast errors).
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

from companion.ch13 import sources as s13
from companion.ch15 import sources as src
from companion.ch15.common import csv, emit
from plantp import yieldmodel as ym

TEST0 = 243 * 24                      # 1 September, first test hour
LEADS = (1, 3, 6, 12, 24, 36)
CAP = 110.0                           # MW installed (60 wind + 50 PV AC)


@lru_cache(maxsize=1)
def truth():
    r = src.plant_year()
    _, v, *_ = src.hourly_inputs()
    w_, pv = r["w_av"], r["pv_av"]
    # PV clear-sky envelope: the highest output at the same hour within +/- 7 days
    pv2 = pv.reshape(365, 24)
    clear = np.zeros_like(pv2)
    for d in range(365):
        lo, hi = max(0, d - 7), min(365, d + 8)
        clear[d] = pv2[lo:hi].max(axis=0)
    clear = clear.ravel()
    # farm curve: median wind output in 0.5 m/s bins of the hub speed
    bins = np.round(v / 0.5).astype(int)
    curve = np.array([np.median(w_[bins == b]) if (bins == b).any() else np.nan
                      for b in range(0, 70)])
    curve = np.maximum.accumulate(np.nan_to_num(curve, nan=0.0))
    return w_, pv, clear, v, curve


def farm_curve(v):
    *_, curve = truth()
    return np.interp(v, 0.5 * np.arange(len(curve)), curve)


@lru_cache(maxsize=None)
def nwp(lead: int, seed: int = 160):
    """Weather-driven forecast for a fixed lead (hours): wind speed error
    with sd 0.7 + 0.03 lead m/s (45 % larger in midwinter, smaller in
    midsummer) and a six-hour memory, plus a +/- 1 h
    timing error on half the days; clear-sky-index error with sd 0.08 +
    0.003 lead (A-267, teaching)."""
    w_, pv, clear, v, _ = truth()
    rng = np.random.default_rng(seed + lead)
    season = 1 + 0.45 * np.cos(2 * np.pi * (np.arange(8760) / 24 - 15) / 365)
    e_v = (0.7 + 0.03 * lead) * season * s13.ar1(8760, 6.0, rng)
    shift = rng.choice([-1, 0, 0, 1], 365)
    idx = np.clip(np.arange(8760) + np.repeat(shift, 24), 0, 8759)
    w_f = farm_curve(np.clip(v[idx] + e_v, 0, None))
    k = np.where(clear > 0.5, pv / np.maximum(clear, 1e-6), 0.0)
    e_k = (0.08 + 0.003 * lead) * s13.ar1(8760, 4.0, rng)
    pv_f = clear * np.clip(k + e_k, 0.0, 1.05)
    return w_f, pv_f


def score_table() -> None:
    w_, pv, clear, _, _ = truth()
    h = w_ + pv
    test = np.arange(8760) >= TEST0
    lines = ["forecast error of the hybrid output on the test months (Sep-Dec),",
             "  RMSE in % of the 110 MW installed:",
             "  lead h   persistence   smart pers.   weather-driven   skill"]
    rows = []
    for L in LEADS:
        per = ym.persistence(h, L)
        sp = ym.persistence(w_, L) + ym.smart_persistence(pv, clear, L)
        wf, pf = nwp(L)
        s_p = ym.scores(per, h, test)["rmse"]
        s_s = ym.scores(sp, h, test)["rmse"]
        s_n = ym.scores(wf + pf, h, test)["rmse"]
        sk = ym.skill(s_n, min(s_p, s_s))
        lines.append(f"  {L:4d}      {100 * s_p / CAP:6.1f}        {100 * s_s / CAP:6.1f}"
                     f"         {100 * s_n / CAP:6.1f}       {sk:+.2f}")
        rows.append((L, f"{100 * s_p / CAP:.2f}", f"{100 * s_s / CAP:.2f}", f"{100 * s_n / CAP:.2f}"))
    csv("ch15-horizon.csv", "lead,pers,smart,nwp", rows)
    lines += ["  persistence is hard to beat for the next hour or two; the",
              "  weather-driven forecast wins from a few hours on, because it",
              "  knows the weather to come; smart persistence (the clear-sky",
              "  index for PV) beats plain persistence once the sun moves;",
              "  skill is against the better baseline at each lead"]
    emit("e_horizon", lines)


def by_technology() -> None:
    w_, pv, clear, _, _ = truth()
    test = np.arange(8760) >= TEST0
    day = clear > 1.0
    lines = ["day-ahead (lead 24 h) error by technology on the test months:",
             "  output        bias MW   MAE MW   RMSE MW   RMSE % of rating"]
    wf, pf = nwp(24)
    for name, f, o, cap, m in (("wind", wf, w_, 60.0, test), ("PV, daylight", pf, pv, 50.0, test & day),
                               ("hybrid", wf + pf, w_ + pv, CAP, test)):
        s = ym.scores(f, o, m)
        lines.append(f"  {name:12s}  {s['bias']:+6.2f}   {s['mae']:6.2f}   {s['rmse']:6.2f}"
                     f"     {100 * s['rmse'] / cap:5.1f}")
    lines += ["  PV errors are scored on daylight hours only (night zeros make",
              "  any forecast look good); the hybrid error is less than the sum",
              "  of its parts because their errors are not fully correlated"]
    emit("e_technology", lines)


def quantiles() -> None:
    w_, pv, *_ = truth()
    h = w_ + pv
    wf, pf = nwp(24)
    f = wf + pf
    train = np.arange(8760) < TEST0
    test = ~train
    err = h - f
    edges = [0, 20, 50, 80, 200]
    lines = ["day-ahead P10-P90 interval of the hybrid output (lead 24 h), test",
             "  months Sep-Dec:",
             "  quantiles learned from          coverage    pinball P10 / P90   mean width"]

    def evaluate(lo, hi):
        cov = ym.coverage(lo[test], hi[test], h[test])
        pb = (ym.pinball(lo[test], h[test], 0.10), ym.pinball(hi[test], h[test], 0.90))
        return cov, pb, float(np.mean(hi[test] - lo[test]))

    cases = {}
    q10, q90 = np.quantile(err[train], [0.10, 0.90])
    cases["train months (fair)"] = (np.clip(f + q10, 0, CAP), np.clip(f + q90, 0, CAP))
    t10, t90 = np.quantile(err[test], [0.10, 0.90])
    cases["the test months (leak)"] = (np.clip(f + t10, 0, CAP), np.clip(f + t90, 0, CAP))
    lo, hi = np.zeros(8760), np.zeros(8760)
    for a, b in zip(edges[:-1], edges[1:]):
        m = (f >= a) & (f < b)
        c10, c90 = np.quantile(err[train & m], [0.10, 0.90])
        lo[m], hi[m] = np.clip(f[m] + c10, 0, CAP), np.clip(f[m] + c90, 0, CAP)
    cases["train, by forecast level"] = (lo, hi)
    for name, (lo_, hi_) in cases.items():
        cov, pb, wid = evaluate(lo_, hi_)
        lines.append(f"  {name:30s}  {100 * cov:5.1f} %     {pb[0]:.2f} / {pb[1]:.2f}       {wid:5.1f} MW")
    lines += ["  the target coverage is 80 %; quantiles fitted on the test",
              "  months hit it by construction: perfect-looking and meaningless",
              "  (leakage); the fair interval from the past covers a little",
              "  less; letting the width depend on the forecast level (narrow",
              "  in calm hours, wide near mid-power) lowers the pinball loss"]
    emit("e_quantiles", lines)
    rows = [(k - TEST0, f"{h[k]:.1f}", f"{f[k]:.1f}", f"{lo[k]:.1f}", f"{hi[k]:.1f}")
            for k in range(TEST0 + 24 * 30, TEST0 + 24 * 37)]
    csv("ch15-fcweek.csv", "h,obs,p50,p10,p90", rows)


def leakage() -> None:
    """A linear correction y = a + b f + c x fitted two ways; x is the
    observation of the previous hour, which a day-ahead forecast cannot
    know at issue time."""
    w_, pv, *_ = truth()
    h = w_ + pv
    wf, pf = nwp(24)
    f = wf + pf
    prev = np.r_[h[0], h[:-1]]
    rng = np.random.default_rng(161)
    test = np.arange(8760) >= TEST0
    lines = ["data leakage in a learned correction of the day-ahead forecast:",
             "  model                                         RMSE test MW"]

    def fit_eval(X, train_mask, eval_mask):
        A = np.c_[np.ones(train_mask.sum()), X[train_mask]]
        coef, *_ = np.linalg.lstsq(A, h[train_mask], rcond=None)
        pred = np.c_[np.ones(eval_mask.sum()), X[eval_mask]] @ coef
        return float(np.sqrt(np.mean((pred - h[eval_mask]) ** 2)))

    X1 = f[:, None]
    X2 = np.c_[f, prev]
    rand_test = rng.random(8760) < 0.33
    lines.append(f"  raw day-ahead forecast                          {ym.scores(f, h, test)['rmse']:6.2f}")
    lines.append(f"  corrected, trained Jan-Aug, tested Sep-Dec      {fit_eval(X1, ~test, test):6.2f}")
    lines.append(f"  + last hour's observation, random split          {fit_eval(X2, ~rand_test, rand_test):6.2f}")
    lines.append(f"  + last hour's observation, time split            {fit_eval(X2, ~test, test):6.2f}")
    lines += ["  the last hour's observation is not known a day ahead: any",
              "  model that uses it scores well in a test and cannot run in",
              "  operation; a random split also lets neighbouring hours leak",
              "  into the test; features must exist at the issue time"]
    emit("e_leakage", lines)


def ramps() -> None:
    w_, pv, clear, _, _ = truth()
    h = w_ + pv
    test = np.arange(8760) >= TEST0
    obs = ym.ramps(h, 15.0)[test]
    lines = ["hybrid ramps above 15 MW in one hour on the test months:",
             f"  observed ramps: {int((obs != 0).sum())}",
             "  forecast             hits  misses  false   POD    FAR"]
    for name, f in (("persistence, 1 h", ym.persistence(h, 1)),
                    ("weather-driven, 1 h", sum(nwp(1))),
                    ("weather-driven, 24 h", sum(nwp(24)))):
        fe = ym.ramps(np.nan_to_num(f), 15.0)[test]
        t = ym.ramp_table(obs, fe)
        lines.append(f"  {name:20s} {t['hits']:4d}   {t['misses']:5d}  {t['false']:5d}   {t['pod']:.2f}"
                     f"   {t['far']:.2f}")
    lines += ["  persistence only repeats a ramp one hour late, so it catches",
              "  few; the weather-driven forecasts see many more, but often an",
              "  hour early or late (timing errors) and with false alarms;",
              "  ramp skill is scored separately from RMSE"]
    emit("e_ramps", lines)


def drift() -> None:
    w_, pv, *_ = truth()
    h = w_ + pv
    wf, pf = nwp(24)
    f = wf + pf
    month = src.plant_year()["month"]
    train = np.arange(8760) < TEST0
    A = np.c_[np.ones(train.sum()), f[train]]
    coef, *_ = np.linalg.lstsq(A, h[train], rcond=None)
    corr = coef[0] + coef[1] * f
    names = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
    lines = ["bias of the corrected day-ahead forecast by month (fit Jan-Aug):",
             "  month   bias MW"]
    for k in range(8, 12):
        m = month == k
        lines.append(f"  {names[k]}     {np.mean(corr[m] - h[m]):+6.2f}")
    lines += ["  the bias of a correction learned in one season changes from",
              "  month to month in the next (here by about a megawatt, with",
              "  changing sign): the validation reports the error by month and",
              "  the model is retrained on a rolling window"]
    emit("e_drift", lines)


if __name__ == "__main__":
    score_table()
    by_technology()
    quantiles()
    leakage()
    ramps()
    drift()
