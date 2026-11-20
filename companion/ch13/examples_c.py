"""Chapter 13, section C - long-term characterisation: vertical
extrapolation with one or with time-varying shear, direction sectors,
distributions, measure-correlate-predict with three methods, and extreme
wind from annual maxima.

Run from the project root:   python -m companion.ch13.examples_c
Writes companion/ch13/expected/c_*.txt and diagrams/data/ch13-*.csv.
Synthetic data A-250, A-253; extremes A-256.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch13 import lab_d, sources
from companion.ch13.common import csv, emit
from plantp import stats, windres as wr


def extrapolation() -> None:
    t = sources.mast_year()["true"]
    cv, cp = lab_d.curve()
    a_all = wr.fit_shear([60, 80, 100], [t["v60"].mean(), t["v80"].mean(),
                                         t["v100"].mean()])
    a_row = wr.pair_shear(t["v60"], t["v100"], 60, 100)
    a_row = np.where(np.isnan(a_row), a_all, np.clip(a_row, -0.2, 0.7))
    lines = ["from the 100 m mast to higher hubs (true mast year):",
             "  hub m   one shear   shear row by row   difference"]
    for z in (120.0, 150.0):
        e1 = np.interp(t["v100"] * (z / 100) ** a_all, cv, cp).sum() / 6 / 1e3
        e2 = np.interp(t["v100"] * (z / 100) ** a_row, cv, cp).sum() / 6 / 1e3
        lines.append(f"  {z:5.0f}   {e1:8,.0f}    {e2:8,.0f}          "
                     f"{100 * (e2 / e1 - 1):+.2f} %")
    lines += [f"  one shear exponent {a_all:.3f} (mean profile); row by row it is",
              "  high at night and low by day; for the energy of this site the",
              "  difference is small (a few tenths of a per cent), but it is",
              "  large for the loads of each hour and for comparing a lidar's",
              "  upper heights with an extrapolated mast",
              "  (MWh per turbine a year, data-pack power curve, 1.225 kg/m3)"]
    emit("c_extrap", lines)


def sectors() -> None:
    t = sources.mast_year()["true"]
    cv, cp = lab_d.curve()
    e = np.interp(t["v100"], cv, cp)
    wd = t["wd100"] % 360
    rows, lines = [], ["wind rose at 100 m, 12 sectors (true mast year):",
                       "  sector  share of time  mean m/s  share of energy"]
    for k in range(12):
        sel = (wd >= 30 * k) & (wd < 30 * (k + 1))
        f, v, s = sel.mean(), t["v100"][sel].mean(), e[sel].sum() / e.sum()
        rows.append((30 * k + 15, f"{100 * f:.2f}", f"{v:.2f}", f"{100 * s:.2f}"))
        lines.append(f"  {30 * k:3d}-{30 * (k + 1):3d}  {100 * f:6.1f} %        {v:5.2f}"
                     f"     {100 * s:6.1f} %")
    lines += ["  energy comes from fewer directions than time does: the wake",
              "  layout of chapter 11 and the boom orientation follow it"]
    emit("c_sectors", lines)
    csv("ch13-rose.csv", "dir,time,mean,energy", rows)


def distribution() -> None:
    t = sources.mast_year()["true"]
    v10 = t["v100"]
    vh = v10.reshape(-1, 6).mean(axis=1)
    k10, c10 = stats.weibull_fit_mle(v10)
    kh, ch = stats.weibull_fit_mle(vh)
    cv, cp = lab_d.curve()
    e10 = np.interp(v10, cv, cp).sum() / 6 / 1e3
    eh = np.interp(vh, cv, cp).sum() / 1e3
    lines = ["distribution of the 100 m speed, ten-minute against hourly means:",
             f"  ten-minute: Weibull k {k10:.2f}, c {c10:.2f} m/s; energy {e10:,.0f} MWh",
             f"  hourly:     Weibull k {kh:.2f}, c {ch:.2f} m/s; energy {eh:,.0f} MWh"
             f" ({100 * (eh / e10 - 1):+.2f} %)",
             "  hourly averaging narrows this site's distribution only a little",
             "  and moves the energy by a tenth of a per cent: hourly data are",
             "  enough for energy here; ten-minute data are still needed for",
             "  turbulence, gusts and power-curve work"]
    emit("c_distribution", lines)
    edges = np.arange(0, 26, 1.0)
    hist, _ = np.histogram(v10, edges, density=True)
    vv = 0.5 * (edges[1:] + edges[:-1])
    csv("ch13-weibull.csv", "v,hist,fit",
        [(f"{a:.1f}", f"{b:.5f}", f"{float(stats.weibull_pdf(a, k10, c10)):.5f}")
         for a, b in zip(vv, hist)])


def mcp() -> None:
    m = sources.mast_year()
    lg = m["logged"]
    ok10 = ~np.isnan(lg["v100"]) & ~m["iced"]
    site = np.where(ok10, lg["v100"], np.nan).reshape(-1, 6)
    good = np.sum(~np.isnan(site), axis=1) == 6
    site_h = np.nanmean(site, axis=1)
    ref = sources.reference()
    x, y = ref["hourly_2023"][good], site_h[good]
    r = stats.pearson(x, y)
    long_ = ref["long"].ravel()
    wd_long = np.tile(ref["wd_2023"], len(ref["years"]))
    cv, cp = lab_d.curve()
    lt_true = np.nanmean(m["true"]["v100"]) / (1 + ref["anom"][-1])
    lines = ["measure-correlate-predict, hourly, 100 m (A-253):",
             f"  concurrent hours {good.sum():,}; correlation r = {r:.3f}",
             f"  site 2023 mean {y.mean():.3f} m/s; reference 2023 {x.mean():.3f},"
             f" 20 years {long_.mean():.3f}",
             "  method               long-term mean   energy MWh/turbine"]
    preds = {"linear least squares": wr.mcp_linear(x, y, long_)[0],
             "variance ratio": wr.mcp_variance_ratio(x, y, long_)[0],
             "sector ratio": wr.mcp_sector_ratio(x, y, ref["wd_2023"][good], long_,
                                                 wd_long)}
    for name, pr in preds.items():
        pr = np.clip(pr, 0, None)
        e = np.interp(pr, cv, cp).sum() / len(ref["years"]) / 1e3
        lines.append(f"  {name:20s}   {pr.mean():6.3f} m/s       {e:8,.0f}")
    e_site = np.interp(y, cv, cp).sum() / 1e3 * 8760 / good.sum()
    lines += [f"  site year as measured  {y.mean():6.3f} m/s       {e_site:8,.0f}",
              f"  'true' long-term mean of this synthetic site: {lt_true:.3f} m/s",
              "  the line of least squares shrinks the spread (r < 1) and loses",
              "  energy from the cube; variance ratio keeps it; the methods'",
              "  spread is part of the long-term uncertainty"]
    emit("c_mcp", lines)
    rng = np.random.default_rng(3)
    pick = rng.choice(len(x), 1500, replace=False)
    csv("ch13-mcp.csv", "ref,site", [(f"{x[k]:.2f}", f"{y[k]:.2f}") for k in pick])


def extremes() -> None:
    """Annual maxima of the reference hourly speed, scaled to the site by
    the ratio of the 2023 means and to a ten-minute peak by 1.08 (A-256)."""
    ref = sources.reference()
    rng = np.random.default_rng(144)
    peaks = ref["long"].max(axis=1) * (1 + 0.06 * rng.standard_normal(len(ref["years"])))
    ratio = 7.066 / 6.494                       # site / reference means, 2023
    site_peaks = peaks * ratio * 1.08           # hourly to ten-minute peaks
    mu, beta = stats.gumbel_fit_moments(site_peaks)
    v50 = stats.return_level(mu, beta, 50)
    lines = ["extreme wind at 100 m from 20 annual maxima (A-256):",
             f"  annual maxima {site_peaks.min():.1f} .. {site_peaks.max():.1f} m/s"
             f" (ten-minute, site)",
             f"  Gumbel fit: location {mu:.2f}, scale {beta:.2f} m/s",
             f"  50-year return level {v50:.1f} m/s; chance of exceeding it",
             f"    at least once in 25 years"
             f" {100 * stats.prob_exceed_in_life(50, 25):.0f} %",
             "  twenty maxima give a wide confidence interval; reanalysis",
             "  smooths peaks, so its extremes need a correction checked",
             "  against measured storms; the result is compared with the",
             "  reference extreme speed of the turbine class (chapter 11)"]
    emit("c_extremes", lines)
    xs, yv = stats.gumbel_plot_positions(site_peaks)
    csv("ch13-gumbel.csv", "y,v", [(f"{a:.4f}", f"{b:.3f}") for a, b in zip(yv, xs)])
    line = [(f"{y:.2f}", f"{mu + beta * y:.3f}") for y in np.linspace(-1.5, 4.5, 13)]
    csv("ch13-gumbelfit.csv", "y,v", line)


if __name__ == "__main__":
    extrapolation()
    sectors()
    distribution()
    mcp()
    extremes()
