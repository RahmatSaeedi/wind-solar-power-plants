"""Chapter 37, lab G (forecast and service analytics): held-out forecasts
scored by horizon against persistence, the trap of scoring on training
data, bias drift after a change in the plant, coverage of an interval
forecast, and a synthetic service-response trace scored against a
supplied acceptance specification.

Run from the project root:   python -m companion.ch37.lab_g
Writes companion/ch37/expected/g_*.txt and diagrams/data/ch37-*.csv.
Synthetic forecasts and trace (A-414, A-415); the specification is a
placeholder for the grid operator's own (U-118).
"""
from __future__ import annotations

import numpy as np

from companion.ch37 import sources as src
from companion.ch37.common import csv, emit
from plantp import performance as pf
from plantp import yieldmodel as ym

HORIZONS = (1, 6, 24, 48)
SIGMA = {1: 9.5, 6: 13.0, 24: 17.0, 48: 20.0}           # MW, synthetic error size


def forecasts(seed: int = 376):
    """Synthetic forecasts of the plant's MV output at each horizon: the
    truth plus an autocorrelated error whose size grows with the horizon."""
    y = src.operating_year()
    obs = y["pv_act"] + y["w_act"]
    rng = np.random.default_rng(seed)
    out = {}
    for h in HORIZONS:
        e = np.convolve(rng.normal(0, SIGMA[h], 8760 + 5), np.ones(6) / np.sqrt(6), "valid")
        out[h] = np.clip(obs + e[:8760], 0, 110)
    return obs, out


def by_horizon() -> None:
    obs, fc = forecasts()
    test = np.arange(8760) >= 8760 // 2                  # second half held out
    lines = ["plant output forecasts scored on the held-out half year (MW)",
             "  horizon h   bias    MAE    RMSE   persistence RMSE   skill"]
    rows = []
    for h in HORIZONS:
        s = ym.scores(fc[h], obs, test)
        p = ym.scores(ym.persistence(obs, h), obs, test)
        sk = ym.skill(s["rmse"], p["rmse"])
        rows.append((h, round(s["rmse"], 2), round(p["rmse"], 2)))
        lines.append(f"  {h:9d}   {s['bias']:5.2f}  {s['mae']:5.2f}  {s['rmse']:6.2f}"
                     f"   {p['rmse']:16.2f}   {sk:5.2f}")
    csv("ch37-horizons.csv", "h,rmse,pers", rows)
    sk = {h: ym.skill(ym.scores(fc[h], obs, test)["rmse"],
                      ym.scores(ym.persistence(obs, h), obs, test)["rmse"]) for h in HORIZONS}
    lines += [f"  at one hour persistence is hard to beat (skill {sk[1]:+.2f}); from six",
              f"  hours the forecast wins clearly ({sk[6]:+.2f}). At 24 h persistence",
              "  repeats yesterday's sun - a strong reference for PV - so the",
              "  skill dips; the score is read by horizon and by use: a",
              "  day-ahead bid needs the 24 h line, a ramp warning the 1 h",
              "  one (ch 15 built these scores; here they run on operation)"]
    emit("g_horizons", lines)


def training_trap() -> None:
    obs, fc = forecasts()
    f = fc[24]
    week = np.arange(8760) // 168
    train = week % 2 == 0                                 # even weeks fit, odd weeks test
    hod = np.arange(8760) % 24
    month = src.operating_year()["month"]
    corr = np.zeros((12, 24))
    for m in range(12):
        for hh in range(24):
            sel = train & (month == m) & (hod == hh)
            corr[m, hh] = np.mean(obs[sel] - f[sel])
    f2 = f + corr[month, hod]
    rows = [("uncorrected", ym.scores(f, obs, train)["rmse"], ym.scores(f, obs, ~train)["rmse"]),
            ("corrected (288 numbers)", ym.scores(f2, obs, train)["rmse"],
             ym.scores(f2, obs, ~train)["rmse"])]
    lines = ["a 24 h forecast 'corrected' by 288 fitted numbers (month x hour);",
             "  fitted on the even weeks, tested on the odd weeks (RMSE, MW)",
             "  forecast                   fitted weeks   held-out weeks"]
    for name, a, b in rows:
        lines.append(f"  {name:25s} {a:13.2f}   {b:14.2f}")
    lines += ["  on the weeks it was fitted to, the correction removes",
              "  error; on weeks it has not seen it adds some back - it",
              "  learned the noise of its own weeks. Scores are only ever",
              "  taken on held-out data"]
    emit("g_trap", lines)


def drift(seed: int = 379) -> None:
    y = src.operating_year()
    obs = y["pv_act"] + y["w_act"]
    rng = np.random.default_rng(seed)
    f = np.clip(obs + rng.normal(0, 15, 8760), 0, 110)       # an unbiased forecast
    # from day 250 two more turbines run; the forecast model does not know
    obs2 = obs + np.where(np.arange(8760) >= 250 * 24, y["w_act"] * 2 / 12, 0.0)
    bias_m = [float(np.mean(f[y["month"] == m] - obs2[y["month"] == m])) for m in range(12)]
    daily = np.array([np.mean(f[d * 24:(d + 1) * 24] - obs2[d * 24:(d + 1) * 24])
                      for d in range(365)])
    m0, s0 = daily[:200].mean(), daily[:200].std(ddof=1)
    z = (daily - m0) / s0
    a = pf.cusum(z, 1.0, 5.0)
    loose = pf.cusum(z, 0.5, 5.0)
    csv("ch37-drift.csv", "m,bias", [(m + 1, round(b, 3)) for m, b in enumerate(bias_m)])
    lines = ["day-ahead forecast bias by month; two turbines added on day 250",
             "  month   bias MW"]
    for m, b in enumerate(bias_m):
        lines.append(f"  {src.MONTHS[m]:5s}   {b:7.2f}")
    lines += [f"  CUSUM on the daily bias (k 1.0, h 5): alarm on day {a},",
              f"    {a - 250} days after the change",
              f"  a looser setting (k 0.5) alarmed on day {loose}, when nothing had",
              "    changed - the setting trades early warning for false alarms",
              "  the plant now makes more than the forecast expects: the",
              "  bias turns negative from September, by about the output of",
              "  two turbines, and nearly vanishes in calm November; a",
              "  forecast is re-checked after every change to the plant"]
    emit("g_drift", lines)


def interval_coverage() -> None:
    obs, fc = forecasts()
    f = fc[24]
    test = np.arange(8760) >= 8760 // 2
    resid = (obs - f)[~test]
    lo_q, hi_q = np.quantile(resid, [0.05, 0.95])
    cov = ym.coverage(f[test] + lo_q, f[test] + hi_q, obs[test])
    lines = ["a 90 % interval around the 24 h forecast, built on the first half",
             f"  interval: forecast {lo_q:+.1f} to {hi_q:+.1f} MW",
             f"  share of held-out hours inside it: {cov * 100:.1f} %",
             "  an interval that holds about 90 % of new hours is",
             "  calibrated; one that holds 70 % promises a certainty the",
             "  forecast does not have - and a dispatch or bid built on",
             "  it carries that hidden risk"]
    emit("g_coverage", lines)


SPEC = dict(t90_max_s=10.0, band_pct=2.0, settle_max_s=30.0, rms_max_pct=1.5)


def service_trace(seed: int = 378):
    rng = np.random.default_rng(seed)
    t = np.arange(0, 60.0, 0.5)
    start, final = 60.0, 40.0                           # MW: a set point step down
    tau, delay = 3.0, 1.0
    r = np.where(t < delay, start, final + (start - final) * np.exp(-(t - delay) / tau))
    r = r + rng.normal(0, 0.15, t.size)
    return t, r, start, final


def service() -> None:
    t, r, start, final = service_trace()
    band = SPEC["band_pct"] / 100 * 100                 # % of 100 MW
    t90, ts = pf.response_times(t, r, start, final, band)
    demand = np.where(t < 0, start, final)
    rms, mx = pf.tracking_error(demand[t >= ts], r[t >= ts])
    csv("ch37-trace.csv", "t,r", [(round(a, 1), round(b, 2)) for a, b in zip(t, r)])
    ok = [("time to 90 % of the step", f"{t90:.1f} s", f"<= {SPEC['t90_max_s']:.0f} s",
           t90 <= SPEC["t90_max_s"]),
          ("settled within +/-2 MW", f"{ts:.1f} s", f"<= {SPEC['settle_max_s']:.0f} s",
           ts <= SPEC["settle_max_s"]),
          ("RMS error after settling", f"{rms:.2f} MW", f"<= {SPEC['rms_max_pct']:.1f} MW",
           rms <= SPEC["rms_max_pct"])]
    lines = ["a set-point step from 60 to 40 MW against a supplied specification",
             "  (placeholder specification U-118; synthetic trace)",
             "  measure                        result     required   pass?"]
    for a, b, c, d in ok:
        lines.append(f"  {a:30s} {b:9s}  {c:9s}  {'yes' if d else 'NO'}")
    lines += [f"  largest error after settling {mx:.2f} MW",
              "  the specification is written down before the test, with",
              "  its tolerances and the telemetry it is judged on; the",
              "  trace, the specification and the result are kept",
              "  together as settlement evidence"]
    emit("g_service", lines)


def service_month() -> None:
    hours = 744
    required = 600                                       # hours the service was called
    excluded = 12                                        # grid outage, by agreement
    failed = 9                                           # hours not delivered
    avail = (required - excluded - failed) / (required - excluded)
    lines = ["a month of service availability (synthetic, placeholder rules)",
             f"  hours in the month {hours}; hours the service was called {required}",
             f"  excluded by agreement (grid outage) {excluded}; not delivered {failed}",
             f"  service availability: {avail * 100:.2f} %",
             "  each failed hour has its evidence (telemetry, set points,",
             "  plant state) and each excluded hour its reason; the",
             "  operator settles on the same records, so they are kept",
             "  untouched (lesson B)"]
    emit("g_month", lines)


if __name__ == "__main__":
    by_horizon()
    training_trap()
    drift()
    interval_coverage()
    service()
    service_month()
