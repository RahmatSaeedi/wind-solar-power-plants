"""Chapter 29, lesson E: climate evidence and design values - return
levels of heat, rain and gusts from a 30-year record (synthetic), the
trend the record hides if it is fitted as if the climate stood still,
and what each extreme does to the plant's design.

Run from the project root:   python -m companion.ch29.examples_e
Writes companion/ch29/expected/e_*.txt and diagrams/data/ch29-gumbel.csv.
Synthetic record and teaching scenario (A-350); not a hazard study.
"""
from __future__ import annotations

import numpy as np

from companion.ch29 import sources as src
from companion.ch29.common import csv, emit
from plantp import civil as cv
from plantp import stats as sx


def return_levels() -> None:
    e = src.extremes()
    lines = ["return levels from 30 annual maxima (Gumbel by moments; synthetic)",
             "  quantity                    10 yr    50 yr    100 yr   largest seen"]
    names = {"t_max": "daily max temperature C", "rain_1h": "1-hour rain mm",
             "rain_24h": "24-hour rain mm", "gust": "3-s gust m/s at 10 m"}
    for k, label in names.items():
        mu, beta = sx.gumbel_fit_moments(e[k])
        lines.append(f"  {label:26s} {cv.gumbel_return(mu, beta, 10):7.1f}  {cv.gumbel_return(mu, beta, 50):7.1f}"
                     f"  {cv.gumbel_return(mu, beta, 100):8.1f}   {e[k].max():12.1f}")
    x, yr = sx.gumbel_plot_positions(e["rain_1h"])        # sorted maxima, reduced variate
    mu, beta = sx.gumbel_fit_moments(e["rain_1h"])
    csv("ch29-gumbel.csv", "y,x,fit", [(f"{a:.3f}", f"{b:.2f}", f"{mu + beta * a:.2f}") for a, b in zip(yr, x)])
    csv("ch29-gumbel-fit.csv", "y,fit", [(f"{a:.1f}", f"{mu + beta * a:.2f}") for a in (-2.0, 5.0)])
    lines += ["  thirty years give a 50- or 100-year value only by",
              "  extrapolation: the fitted line carries the uncertainty of",
              "  thirty points - a real study uses longer or regional",
              "  records and states the confidence band"]
    emit("e_returns", lines)


def trend() -> None:
    e = src.extremes()
    t = e["t_max"]
    years = np.arange(30)
    slope, intercept = np.polyfit(years, t, 1)
    mu, beta = sx.gumbel_fit_moments(t)
    resid = t - (intercept + slope * years)
    mu_r, beta_r = sx.gumbel_fit_moments(resid)
    stationary = cv.gumbel_return(mu, beta, 50)
    now = intercept + slope * 29 + cv.gumbel_return(mu_r, beta_r, 50)
    in_25 = intercept + slope * (29 + 25) + cv.gumbel_return(mu_r, beta_r, 50)
    lines = ["the 50-year daily maximum temperature with and without the record's trend",
             f"  trend in the record: {10 * slope:+.2f} C per decade",
             f"  fitted as if stationary:            {stationary:5.1f} C",
             f"  with the trend, today:              {now:5.1f} C",
             f"  with the trend, 25 years on (end of life): {in_25:5.1f} C",
             "  a design value taken from the whole record as if the",
             "  climate stood still is low for the plant's later years;",
             "  the design basis states the scenario it assumes (teaching",
             "  here; climate projections are a specialist input)"]
    emit("e_trend", lines)


def links() -> None:
    rows = [("heat (47-48 C)", "derating of inverters, transformers; HVAC", "ch 9, 19, 25"),
            ("rain (1 h, 50 yr)", "culverts, ditches, ponds, pad levels", "B, C"),
            ("gusts (50 yr)", "PV structures, cranes' wind limits", "ch 30, 31"),
            ("dust and sand", "soiling, filters, cleaning water", "ch 10, H"),
            ("flood at the wadi", "substation level, crossings, access", "I"),
            ("drought", "well yield, water balance", "G")]
    lines = ["what each extreme does to the design (and where it is handled)",
             "  hazard               design consequence                         where"]
    for h, c, w in rows:
        lines.append(f"  {h:20s} {c:42s} {w}")
    lines += ["  every hazard in the design basis names its source, its",
              "  return period and the parts it governs; adaptation over",
              "  the life (more cooling, higher pads) is planned, not",
              "  improvised"]
    emit("e_links", lines)


def screen() -> None:
    from plantp import datapack
    d = datapack.load_hourly()
    t = d["t_air_c"].to_numpy()
    lines = ["screening the hazards the handoff lists, from the data-pack year",
             f"  air temperature: lowest {t.min():.1f} C, hours below 0 C: {int((t < 0).sum())},"
             f" below -5 C: {int((t < -5).sum())}",
             "  hazard     relevant here?  basis and where it is handled",
             "  heat       yes             47-48 C extremes (e_returns, ch 9, 19, 25)",
             "  wind       yes             50-year gust 41 m/s (ch 11, 30, 31)",
             "  dust       yes             soiling, filters (ch 10, lesson H)",
             "  flood      yes             wadi beside the substation (lesson I, P)",
             "  drought    yes             wells, tank (lessons G, H)",
             "  erosion    yes             bare ground in construction (lesson B, C)",
             "  cold       yes (winter)    frost nights: cold-weather concreting,",
             "                             battery heating (ch 19), frost on pads",
             "  icing      unlikely        dry cold air; confirm with the turbine maker",
             "  snow       rare            no record here; loads by the code (ch 30)",
             "  wildfire   low             sparse rangeland - grass after wet years:",
             "                             firebreaks at the fence (lesson F)",
             "  a hazard is screened out with a reason and a source, not",
             "  left off the list; the screen is redone when the record",
             "  or the climate scenario changes"]
    emit("e_screen", lines)


if __name__ == "__main__":
    return_levels()
    trend()
    links()
    screen()
