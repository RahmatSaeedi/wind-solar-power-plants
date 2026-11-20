"""Chapter 12, section C - data treatment: flags on a faulty one-minute
day, finding a clock error, filling gaps, a drifting sensor, comparing the
ground year with a provider series, long-term correction, interannual
variability and the uncertainty budget (P50, P90).

Run from the project root:   python -m companion.ch12.examples_c
Writes companion/ch12/expected/c_*.txt and diagrams/data/ch12-*.csv.
Data pack 1.1.0 (S0); synthetic sources A-240 .. A-242; budget A-245.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch12 import sources
from companion.ch12.common import csv, emit
from plantp import irradiance as ir

MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def day_flags(x, cz, g0):
    """GHI-only flags of one-minute data: missing, physically impossible,
    extremely rare, negative at night."""
    lim = ir.qc_limits(cz, g0)
    miss = np.isnan(x)
    v = np.nan_to_num(x)
    phys = ~miss & ((v > lim["ghi_phys"]) | (v < -4))
    rare = ~miss & ~phys & (v > lim["ghi_rare"])
    night = ~miss & (cz <= 0) & (v < -2)
    return miss, phys, rare, night


def flags_day() -> None:
    d = sources.faulty_clear_day()
    x, cz = d["measured"], d["cz"]
    g0 = float(ir.g0n(d["doy"]))
    miss, phys, rare, night = day_flags(x, cz, g0)
    # the lag is estimated from values cleaned WITHOUT the sun geometry:
    # flags that use the sun's position are themselves shifted by the error
    spike = np.nan_to_num(x) > 1.2 * d["clear_sky"].max()
    robust = np.where(np.isnan(x) | spike, 0.0, np.clip(np.nan_to_num(x), 0, None))
    lag = ir.best_lag(robust, d["clear_sky"], 120)
    raw_lag = ir.best_lag(np.nan_to_num(x), d["clear_sky"], 120)
    adopted = 60 * round(lag / 60)            # a whole-hour configuration error
    fixed = np.roll(x, -adopted)
    m2, p2, r2, n2 = day_flags(fixed, cz, g0)
    t = np.arange(1440)
    rows = [(f"{k / 60:.3f}", f"{d['clear_sky'][k]:.1f}",
             "nan" if np.isnan(x[k]) else f"{min(x[k], 1200):.1f}") for k in t[::5]]
    csv("ch12-faultday.csv", "h,clear,meas", rows)
    lines = ["one clear day of one-minute GHI with five faults (A-242):",
             f"  as logged: missing {miss.sum()} min, physically impossible"
             f" {phys.sum()}, extremely rare {rare.sum()},",
             f"    negative at night {night.sum()} min (thermal offset)",
             f"  shift against the clear-sky curve, spikes and gaps removed:"
             f" {lag} min late",
             f"    (raw values: {raw_lag} min); the sunrise shadow skews it, and",
             f"    the logger set-up shows UTC+05 for +04: shift {adopted} min",
             f"  after the shift: impossible {p2.sum()}, extremely rare"
             f" {r2.sum()}; the 'impossible' values",
             "    were sun after sunset, a symptom of the clock, not the sky",
             "  left: the two spikes (extremely rare), the night offset, a dip",
             "  in the first 45 min after sunrise on a clear day (a nearby",
             "  object shades the sensor) and a 3 % step after noon (dust on",
             "  the dome, section E)"]
    emit("c_flags", lines)


def time_shift() -> None:
    p = sources.pack()
    cs = ir.clear_sky_haurwitz(p["cz"])
    late = np.roll(p["ghi"], 1)                       # logger one hour late
    lines = ["finding a clock error in hourly data (pack year):",
             f"  pack GHI against clear sky: best lag {ir.best_lag(p['ghi'], cs, 3)} h",
             f"  the same data stored one hour late: best lag"
             f" {ir.best_lag(late, cs, 3)} h",
             "  morning/afternoon symmetry around solar noon shows the same",
             "  thing on clear days; a UTC/local mix-up gives exactly 4 h here"]
    am = (p["hour"] >= 6) & (p["hour"] < 12)
    pm = (p["hour"] >= 12) & (p["hour"] < 18)
    lines.append(f"  share of GHI before noon: pack {p['ghi'][am].sum() / (p['ghi'][am].sum() + p['ghi'][pm].sum()):.3f},"
                 f" late copy {late[am].sum() / (late[am].sum() + late[pm].sum()):.3f}")
    emit("c_timeshift", lines)


def gaps() -> None:
    p = sources.pack()
    kt = ir.clearness_index(p["ghi"], p["cz"], p["g0n"])
    rng = np.random.default_rng(31)
    test = kt.copy()
    up = np.flatnonzero(~np.isnan(kt))
    holes = rng.choice(up[5:-5], 300, replace=False)
    for k in holes:
        test[k:k + 2] = np.nan                        # 300 gaps of two hours
    filled = ir.fill_short_gaps(test, 3)
    sel = np.isnan(test) & ~np.isnan(kt) & ~np.isnan(filled)
    err = (filled[sel] - kt[sel]) * p["g0n"][sel] * p["cz"][sel]
    lines = ["filling two-hour gaps by interpolating the clearness index:",
             f"  {sel.sum()} daylight hours removed and filled",
             f"  bias {err.mean():+.1f} W/m2, RMSE {np.sqrt(np.mean(err ** 2)):.1f} W/m2",
             f"  energy of the filled hours: true {np.sum(kt[sel] * p['g0n'][sel] * p['cz'][sel]) / 1e3:.1f},"
             f" filled {np.sum(filled[sel] * p['g0n'][sel] * p['cz'][sel]) / 1e3:.1f} kWh/m2",
             "  interpolating GHI itself would ignore the sun's path; the",
             "  clearness index carries the weather, the geometry is known",
             "  gaps longer than a few hours are filled from a second source",
             "  (provider series), and every filled value keeps its flag"]
    emit("c_gaps", lines)


def drift() -> None:
    """A station pyranometer that loses 0.06 % a week from a calibration
    drift (A-245), checked weekly against the provider series."""
    p = sources.pack()
    pr = sources.provider()["ghi"]
    week = np.arange(8760) // 168
    drifting = p["ghi"] * (1 - 0.0006 * week)
    r0 = ir.ratio_by_block(p["ghi"], pr, 168)
    r1 = ir.ratio_by_block(drifting, pr, 168)
    csv("ch12-drift.csv", "week,ok,drift", [(k + 1, f"{a:.4f}", f"{b:.4f}")
                                            for k, (a, b) in enumerate(zip(r0, r1))])
    wk = np.arange(len(r0))
    slope_ok = np.polyfit(wk, r0, 1)[0]
    slope_dr = np.polyfit(wk, r1, 1)[0]
    resid = r0 - np.polyval(np.polyfit(wk, r0, 1), wk)
    se = resid.std(ddof=2) / math.sqrt(np.sum((wk - wk.mean()) ** 2))
    lines = ["weekly ratio station / provider (52 weeks):",
             f"  sound sensor: mean {r0.mean():.3f}, sd {r0.std(ddof=1):.3f},"
             f" trend {100 * slope_ok * 52:+.1f} % a year",
             f"  drifting sensor: trend {100 * slope_dr * 52:+.1f} % a year",
             f"  standard error of a one-year trend: {100 * se * 52:.1f} % a year;"
             " the drift",
             f"    is {abs(slope_dr) / se:.1f} standard errors, the sound"
             f" sensor's {abs(slope_ok) / se:.1f}",
             f"  year's GHI with the drift: {drifting.sum() / 1e3:,.0f} kWh/m2"
             f" ({100 * (drifting.sum() / p['ghi'].sum() - 1):+.1f} %)",
             "  a weekly ratio scatters by several per cent (weather, provider",
             "  error); a trend over months stands out, a single week does not",
             "  a second station sensor or a recalibration settles the case"]
    emit("c_drift", lines)


def compare() -> None:
    p = sources.pack()
    pr = sources.provider()
    up = p["cz"] > 0.087
    rows, lines = [], ["provider series against the ground year (A-240):",
                       "  month  ground kWh/m2  provider  bias %"]
    for m in range(12):
        sel = p["month"] == m
        g, q = p["ghi"][sel].sum() / 1e3, pr["ghi"][sel].sum() / 1e3
        rows.append((m + 1, f"{g:.1f}", f"{q:.1f}"))
        lines.append(f"  {MONTHS[m]}     {g:7.1f}      {q:7.1f}   {100 * (q / g - 1):+5.1f}")
    mean_g = p["ghi"][up].mean()
    lines += [f"  year: ground {p['ghi'].sum() / 1e3:,.1f}, provider"
              f" {pr['ghi'].sum() / 1e3:,.1f} kWh/m2"
              f" ({100 * (pr['ghi'].sum() / p['ghi'].sum() - 1):+.1f} %)",
              f"  hourly GHI: MBE {ir.mbe(pr['ghi'][up], p['ghi'][up]):+.1f} W/m2"
              f" ({100 * ir.mbe(pr['ghi'][up], p['ghi'][up]) / mean_g:+.1f} %),"
              f" RMSE {ir.rmse(pr['ghi'][up], p['ghi'][up]):.0f} W/m2"
              f" ({100 * ir.rmse(pr['ghi'][up], p['ghi'][up]) / mean_g:.0f} %)",
              f"  hourly DNI: MBE {ir.mbe(pr['dni'][up], p['dni'][up]):+.1f} W/m2,"
              f" RMSE {ir.rmse(pr['dni'][up], p['dni'][up]):.0f} W/m2",
              f"  distribution distance (quantiles) GHI"
              f" {ir.distribution_distance(pr['ghi'][up], p['ghi'][up]):.1f} W/m2",
              f"  mean daylight GHI {mean_g:.0f} W/m2: the annual sums agree"
              " within a per cent,",
              "  single hours scatter by about 8 % RMS and DNI much more:",
              "  what matters depends on the use (energy, clipping, tracking)"]
    emit("c_compare", lines)
    csv("ch12-monthly.csv", "month,ground,provider", rows)
    rng = np.random.default_rng(9)
    pick = rng.choice(np.flatnonzero(up), 1200, replace=False)
    csv("ch12-scatter.csv", "ground,provider",
        [(f"{p['ghi'][k]:.0f}", f"{pr['ghi'][k]:.0f}") for k in pick])


def long_term() -> None:
    p = sources.pack()
    lt = sources.long_term()
    site = p["ghi"].sum() / 1e3
    conc = lt["annual"][-1]
    lt_mean = lt["annual"].mean()
    corrected = ir.long_term_ratio([site], [conc], [lt_mean])
    lines = ["long-term correction of the one-year ground record:",
             f"  ground 2023 {site:,.1f} kWh/m2; provider 2023 {conc:,.1f}",
             f"  provider 20-year mean {lt_mean:,.1f} kWh/m2",
             f"  ratio {lt_mean / conc:.4f}: long-term site estimate"
             f" {corrected:,.1f} kWh/m2 ({100 * (corrected / site - 1):+.1f} %)",
             "  the ground year was sunnier than usual; using it as it is",
             "  would overstate every later year's energy by about that much",
             "  the method assumes the provider's error is the same in every",
             "  year (no trend, no change of satellite or algorithm)"]
    # monthly regression variant
    pr_month = lt["monthly"][-1]
    g_month = np.array([p["ghi"][p["month"] == m].sum() / 1e3 for m in range(12)])
    slope, icept = np.polyfit(pr_month, g_month, 1)
    lt_month = lt["monthly"].mean(axis=0)
    reg = float(np.sum(slope * lt_month + icept))
    lines.append(f"  monthly regression variant: {reg:,.1f} kWh/m2"
                 f" (slope {slope:.3f}, intercept {icept:+.1f})")
    emit("c_longterm", lines)


def uncertainty() -> None:
    """Uncertainty budget of the long-term annual GHI (A-245, teaching
    standard uncertainties, one sigma)."""
    lt = sources.long_term()
    p50 = ir.long_term_ratio([sources.pack()["ghi"].sum() / 1e3],
                             [lt["annual"][-1]], [lt["annual"].mean()])
    iav = float(np.std(lt["annual"], ddof=1) / np.mean(lt["annual"]))
    parts = {"station sensor (class, calibration)": 0.020,
             "sensor soiling and maintenance": 0.010,
             "long-term correction (provider stability)": 0.015,
             "long-term mean of 20 years": iav / math.sqrt(20)}
    u = ir.combine_uncertainty(*parts.values())
    lines = ["uncertainty of the long-term annual GHI (A-245, one sigma):"]
    for k, v in parts.items():
        lines.append(f"  {k:44s} {100 * v:4.1f} %")
    lines += [f"  combined (root sum of squares)               {100 * u:4.1f} %",
              f"  P50 {p50:,.0f} kWh/m2; P90 long-term"
              f" {ir.p_value(p50, u):,.0f}",
              f"  any single year adds the year-to-year spread {100 * iav:.1f} %:",
              f"    P90 one-year {ir.p_value(p50, ir.combine_uncertainty(u, iav)):,.0f}"
              f" kWh/m2 (combined {100 * ir.combine_uncertainty(u, iav):.1f} %)",
              "  the plane-of-array, PV-model and loss uncertainties of chapters",
              "  15 and 16 add to these before an energy P90 is quoted"]
    emit("c_uncertainty", lines)


if __name__ == "__main__":
    flags_day()
    time_shift()
    gaps()
    drift()
    compare()
    long_term()
    uncertainty()
