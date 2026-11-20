"""Chapter 16, section C - exceedance values for one, ten and twenty
years, the P90 against the number of years, skewed distributions, the
confidence of a P90, and why a forecast score is not a yield
uncertainty.

Run from the project root:   python -m companion.ch16.examples_c
Writes companion/ch16/expected/c_*.txt and diagrams/data/ch16-*.csv.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch15 import forecast as fc
from companion.ch16 import sources as src
from companion.ch16.common import csv, emit
from plantp import yieldmodel as ym, yieldrisk as yr


def sig_net(years: int) -> float:
    s = src.sigmas()
    return yr.n_year(s["lt"], s["iav"], years) * s["ratio"]


def table() -> None:
    p50 = src.base()["net"]
    lines = [f"exceedance values of the net energy at the POC (P50 {p50:.2f} GWh,",
             "  normal), for the first year, a 10-year and a 20-year mean:",
             "  P-value   z       1 year     10 years   20 years"]
    for p in (0.50, 0.75, 0.90, 0.95, 0.99):
        z = yr.z_exceed(p)
        vals = [p50 - z * sig_net(n) for n in (1, 10, 20)]
        lines.append(f"  P{int(round(100 * p)):<3d}     {z:5.3f}   " +
                     "   ".join(f"{v:7.2f}" for v in vals))
    lines.append("  sigma GWh          " + "   ".join(f"{sig_net(n):7.2f}" for n in (1, 10, 20)))
    lines += ["  the P90 of a 10-year mean is higher than the one-year P90:",
              "  good and bad years average out; the long-term part does not"]
    emit("c_table", lines)
    rows = []
    for e in np.linspace(240, 340, 101):
        rows.append((f"{e:.0f}", f"{100 * (1 - _cdf(e, p50, sig_net(1))):.2f}",
                     f"{100 * (1 - _cdf(e, p50, sig_net(10))):.2f}"))
    csv("ch16-exceed.csv", "e,y1,y10", rows)
    pdf = [(f"{e:.1f}", f"{_pdf(e, p50, sig_net(1)):.5f}") for e in np.linspace(230, 360, 131)]
    csv("ch16-pdf.csv", "e,f", pdf)


def _cdf(x, m, s):
    return 0.5 * (1 + math.erf((x - m) / (s * math.sqrt(2))))


def _pdf(x, m, s):
    return math.exp(-0.5 * ((x - m) / s) ** 2) / (s * math.sqrt(2 * math.pi))


def horizon() -> None:
    p50 = src.base()["net"]
    s = src.sigmas()
    lines = ["P90 of the mean of n future years (net at the POC):",
             "  years   sigma GWh   P90 GWh"]
    rows = []
    for n in (1, 2, 3, 5, 10, 15, 20, 25):
        sg = sig_net(n)
        rows.append((n, f"{p50 - 1.2816 * sg:.2f}"))
        lines.append(f"  {n:5d}    {sg:7.2f}    {p50 - 1.2816 * sg:7.2f}")
    lt = s["lt"] * s["ratio"]
    lines += [f"  limit for many years: the long-term part alone, sigma {lt:.2f},"
              f" P90 {p50 - 1.2816 * lt:.2f} GWh",
              "  more years help less and less: the long-term uncertainty is",
              "  shared by every year and does not average out"]
    emit("c_horizon", lines)
    csv("ch16-horizon.csv", "n,p90", rows)


def skew() -> None:
    lines = ["normal against lognormal for the same median and relative spread:",
             "  spread   P90 normal   P90 lognormal   mean of lognormal / median"]
    for u in (0.05, 0.10, 0.20):
        n90 = yr.p_value(100.0, u)
        l90 = yr.p_value_lognormal(100.0, u)
        s = math.log(1 + u)
        lines.append(f"  {100 * u:4.0f} %      {n90:6.2f}        {l90:6.2f}           {math.exp(0.5 * s * s):.4f}")
    lines += ["  at the 5 % spread of this plant the shape hardly matters; a",
              "  one-sided loss (outages, curtailment) or a wide spread makes",
              "  mean, median and P50 differ: the statement says which it is"]
    emit("c_skew", lines)


def confidence() -> None:
    """The P90 depends on the sigma, which is itself estimated: the
    long-term part from about 20 years and teaching component values."""
    p50 = src.base()["net"]
    sg = sig_net(1)
    rng = np.random.default_rng(165)
    # chi-square spread of a standard deviation estimated from 20 years
    k = 19
    f = np.sqrt(rng.chisquare(k, 200_000) / k)
    p90 = p50 - 1.2816 * sg * f
    lines = ["confidence of the P90 when the sigma is estimated (one year):",
             f"  P90 with the stated sigma {sg:.2f} GWh: {p50 - 1.2816 * sg:.2f} GWh",
             "  if the sigma came from 20 values, the P90 itself spans",
             f"    {np.quantile(p90, 0.05):.2f} to {np.quantile(p90, 0.95):.2f} GWh (90 % of cases)",
             "  the P90 is an estimate with its own uncertainty; a statement",
             "  gives it to the nearest GWh and names how the sigma was found"]
    emit("c_confidence", lines)


def forecast_vs_yield() -> None:
    w_, pv, *_ = fc.truth()
    h = w_ + pv
    f = sum(fc.nwp(24))
    test = np.arange(8760) >= fc.TEST0
    rmse = ym.scores(f, h, test)["rmse"]
    s = src.sigmas()
    sg = sig_net(1)
    lines = ["a forecast score is not a yield uncertainty:",
             f"  day-ahead hourly RMSE {rmse:.2f} MW = {100 * rmse / h.mean():.0f} % of the mean power",
             f"  sum of the hourly errors over the test months {(f - h)[test].sum() / 1e3:+.2f} GWh"
             f" (bias)",
             f"  one-year yield sigma {sg:.2f} GWh = {100 * sg / src.base()['net']:.1f} % of the year",
             "  the forecast error is about tomorrow's hours and averages out;",
             "  the yield uncertainty is about the long-term mean and does not;",
             "  neither number can be turned into the other"]
    emit("c_forecast", lines)


if __name__ == "__main__":
    table()
    horizon()
    skew()
    confidence()
    forecast_vs_yield()
