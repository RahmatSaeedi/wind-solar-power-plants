"""Chapter 13, sections B3 and C2 - running the campaign and deeper analysis:
a logger clock offset found against the lidar, a stuck vane, a vane
mounted off north, energy from the time series against three Weibull
fits, representative turbulence against a design curve, how the
long-term estimate depends on the length of the concurrent period, P90
over one to twenty years, and a step change hidden in the reference.

Run from the project root:   python -m companion.ch13.examples_g
Writes companion/ch13/expected/g_*.txt and diagrams/data/ch13-*.csv.
Teaching values A-257 (faults), A-258 (manufacturer's design curve).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch13 import integrated, lab_d, sources
from companion.ch13.common import csv, emit
from plantp import irradiance as ir, stats, windres as wr


def corr_by_lag(a, b, max_lag: int):
    """Correlation of a shifted against b for lags -max_lag .. max_lag
    (positive lag: a is late)."""
    out = []
    for lag in range(-max_lag, max_lag + 1):
        x = a[max(lag, 0):len(a) + min(lag, 0)]
        y = b[max(-lag, 0):len(b) + min(-lag, 0)]
        ok = ~np.isnan(x) & ~np.isnan(y)
        out.append((lag, stats.pearson(x[ok], y[ok])))
    return out


def clock() -> None:
    """The logger clock is 30 minutes late from day 200 (A-257)."""
    m = sources.mast_year()
    li = sources.lidar()
    v = m["true"]["v100"].copy()
    d0 = 200 * 144
    v[d0 + 3:] = v[d0:-3]                     # records stamped 30 min late
    sl = slice(d0 + 1440, d0 + 1440 + 4032)   # four weeks after the fault
    lags = corr_by_lag(v[sl], li[100][sl], 6)
    best = max(lags, key=lambda t: t[1])
    before = corr_by_lag(v[:d0], li[100][:d0], 6)
    b0 = max(before, key=lambda t: t[1])
    lines = ["logger clock check against the lidar (ten-minute records):",
             "  lag (records)  " + "   ".join(f"{k:+d}" for k, _ in lags[5:12]),
             "  r after fault  " + " ".join(f"{r:.3f}"[1:] for _, r in lags[5:12]),
             f"  best lag before day 200: {b0[0]:+d}; after: {best[0]:+d} records"
             f" ({10 * best[0]:+d} min)",
             "  the correlation peaks where the clocks agree: the mast is",
             "  30 minutes late from the fault on; the logbook shows a",
             "  battery change that reset the clock (action: resync, shift",
             "  the records, note it in the metadata)"]
    emit("g_clock", lines)


def stuck_vane() -> None:
    m = sources.mast_year()["true"]
    wd = m["wd100"].copy()
    s0 = 40 * 144
    wd[s0:s0 + 3 * 144] = 287.0               # vane frozen for three days
    flags = wr.stuck_runs(np.round(wd, 1), 6)
    d = wr.angle_diff(wd, m["wd60"])
    win = slice(s0, s0 + 3 * 144)
    lines = ["a stuck vane (100 m, three days in February, A-257):",
             f"  records flagged as stuck: {int(flags.sum())}"
             f" (432 planted)",
             f"  100 m minus 60 m direction: normal sd"
             f" {np.std(d[:s0]):.1f} deg, while stuck {np.std(d[win]):.1f} deg",
             "  a constant direction while the 60 m vane and the speeds move",
             "  is a stuck vane, not a steady wind; the same test on the",
             "  cups finds a stuck anemometer (cold, bearing, cable)"]
    emit("g_stuckvane", lines)


def vane_offset() -> None:
    m = sources.mast_year()["true"]
    hour = m["hour"]
    d_ok = wr.angle_diff(m["wd100"], m["wd60"])
    d_bad = wr.angle_diff((m["wd100"] + 20) % 360, m["wd60"])
    day = (hour >= 10) & (hour < 16)
    night = (hour >= 22) | (hour < 4)
    rows = []
    for h in range(24):
        sel = hour == h
        rows.append((h, f"{d_ok[sel].mean():.2f}", f"{d_bad[sel].mean():.2f}"))
    csv("ch13-veer.csv", "hour,ok,offset", rows)
    lines = ["veer by hour as a check of the vanes (100 m minus 60 m):",
             "                    midday   night",
             f"  vanes as mounted   {d_ok[day].mean():+5.1f}    {d_ok[night].mean():+5.1f} deg",
             f"  100 m vane +20     {d_bad[day].mean():+5.1f}    {d_bad[night].mean():+5.1f} deg",
             "  physics: the unstable midday layer mixes and turns the wind",
             "  little; a large 'veer' at midday is a mounting offset; the",
             "  mounting photos, a compass check or the lidar's direction",
             "  fix it, with the correction recorded"]
    emit("g_vaneoffset", lines)


def weibull_energy() -> None:
    v = sources.mast_year()["true"]["v100"]
    cv, cp = lab_d.curve()
    e_ts = np.interp(v, cv, cp).sum() / 6 / 1e3      # MWh a year
    grid = np.linspace(0, 35, 3501)
    lines = ["energy of one turbine (pack curve, 1.225 kg/m3) from the",
             "  ten-minute series against Weibull fits of it:",
             "  method                k      c m/s   MWh      difference"]
    lines.append(f"  time series                          {e_ts:7,.0f}")
    for name, fit in (("moments", stats.weibull_fit_moments),
                      ("maximum likelihood", stats.weibull_fit_mle),
                      ("least squares (CDF)", stats.weibull_fit_lsq)):
        k, c = fit(v)
        pdf = np.asarray(stats.weibull_pdf(grid, k, c))
        e = np.trapezoid(pdf * np.interp(grid, cv, cp), grid) * 8760 / 1e3
        lines.append(f"  {name:20s} {k:5.2f}  {c:6.2f}  {e:7,.0f}   "
                     f"{100 * (e / e_ts - 1):+6.2f} %")
    lines += ["  here all three fits come within 0.4 % of the series: the",
              "  Weibull is a good summary of this site; with calm spells or",
              "  two wind regimes it is not, so the time series (with its",
              "  direction and hour) stays the basis and the fit a check"]
    emit("g_weibull", lines)


def design_curve(v):
    """Synthetic design turbulence curve from the manufacturer (A-258)."""
    return 0.09 + 1.5 / (np.asarray(v, float) + 1.0)


def rep_ti() -> None:
    t = sources.mast_year()["true"]
    ti = t["sd100"] / t["v100"]
    lines = ["representative turbulence (mean + 1.28 sd in each bin) against",
             "  the manufacturer's design curve (synthetic, A-258):",
             "  bin m/s   n      mean    sd     represent.  design   margin"]
    rows = []
    for b in range(5, 20, 2):
        sel = (t["v100"] >= b - 0.5) & (t["v100"] < b + 0.5)
        mu, sd = ti[sel].mean(), ti[sel].std()
        rep = mu + 1.28 * sd
        dc = float(design_curve(b))
        rows.append((b, f"{rep:.4f}", f"{dc:.4f}"))
        lines.append(f"  {b:5d}   {int(sel.sum()):5d}   {mu:.3f}  {sd:.3f}   {rep:.3f}"
                     f"       {dc:.3f}    {100 * (dc / rep - 1):+5.1f} %")
    csv("ch13-repti.csv", "v,rep,design", rows)
    lines += ["  the site sits under the curve in every bin: ambient turbulence",
              "  is compatible; wakes of neighbours add to it (effective",
              "  turbulence, chapter 14), and the manufacturer confirms with",
              "  its own load calculation (chapter 16)"]
    emit("g_repti", lines)


def mcp_length() -> None:
    m = sources.mast_year()
    ref = sources.reference()
    y_all = m["true"]["v100"].reshape(-1, 6).mean(axis=1)
    x_all = ref["hourly_2023"]
    month = (np.arange(8760) // 24) * 12 // 365
    truth = wr.mcp_variance_ratio(x_all, y_all, ref["long"].ravel())[0].mean()
    lines = ["long-term mean (variance ratio) from a shorter concurrent period:",
             "  months used          start Jan   start Jul",
             ]
    for n in (3, 6, 9, 12):
        res = []
        for start in (0, 6):
            sel = ((month - start) % 12) < n
            lt = wr.mcp_variance_ratio(x_all[sel], y_all[sel], ref["long"].ravel())[0]
            res.append(lt.mean())
        lines.append(f"  {n:2d}                   {res[0]:6.3f}      {res[1]:6.3f}"
                     f"   ({100 * (res[0] / truth - 1):+.1f} / {100 * (res[1] / truth - 1):+.1f} %)")
    lines += [f"  twelve months: {truth:.3f} m/s",
              "  a few months correlate well but carry their season's",
              "  relation: the result depends on which months; twelve",
              "  months (or several whole years) remove the seasonal bias"]
    emit("g_mcplength", lines)


def multi_year() -> None:
    p50, ue, iav = integrated.farm_long_term()["farm"], 0.041, 0.056
    lines = [f"P90 of the farm over different periods (P50 {p50:.2f} GWh):",
             "  years   u(E) total   P90 GWh/yr"]
    for n in (1, 5, 10, 20):
        u = math.sqrt(ue ** 2 + iav ** 2 / n)
        lines.append(f"  {n:4d}     {100 * u:5.1f} %       {ir.p_value(p50, u):6.1f}")
    lines += ["  year-to-year variation averages out over many years; the",
              "  uncertainty of the long-term estimate does not: lenders use",
              "  the one-year P90 for the debt service of each year and the",
              "  ten-year value for the loan as a whole (chapter 21)"]
    emit("g_multiyear", lines)


def ref_step() -> None:
    """A reanalysis whose last ten years read 3 % high after a change in
    the assimilated observations (A-257); a neighbour series without it."""
    ref = sources.reference()
    rng = np.random.default_rng(146)
    ann = ref["long"].mean(axis=1)
    stepped = ann * np.where(ref["years"] >= 2014, 1.03, 1.0)
    neighbour = ann * (1 + 0.01 * rng.standard_normal(len(ann)))
    ratio = stepped / neighbour
    a, b = ratio[ref["years"] < 2014], ratio[ref["years"] >= 2014]
    t = (b.mean() - a.mean()) / math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    f_ok = ann.mean() / ann[-1]
    f_bad = stepped.mean() / stepped[-1]
    lines = ["a step hidden in the long-term reference (A-257):",
             f"  ratio to a neighbour series: 2004-2013 {a.mean():.3f},"
             f" 2014-2023 {b.mean():.3f} (t = {t:.1f})",
             f"  long-term factor for 2023: clean {f_ok:.4f}, with the step"
             f" {f_bad:.4f} ({100 * (f_bad / f_ok - 1):+.1f} %)",
             "  a step in the reference moves the whole long-term estimate;",
             "  ratios to independent neighbours show it; use the consistent",
             "  period or a corrected series, and say so in the report"]
    emit("g_refstep", lines)


if __name__ == "__main__":
    clock()
    stuck_vane()
    vane_offset()
    weibull_energy()
    rep_ti()
    mcp_length()
    multi_year()
    ref_step()
