"""Chapter 13, section C3 - more long-term practice: extremes from storm
peaks over a threshold against annual maxima (with bootstrap intervals)
and the 50-year gust, the matrix MCP method, when the wind produces
(night, season) at three hub heights and what that means next to the PV
and the 100 MW export limit, and filling the 80 m gaps by substitution.

Run from the project root:   python -m companion.ch13.examples_h
Writes companion/ch13/expected/h_*.txt and diagrams/data/ch13-*.csv.
Synthetic storms A-257; mast year A-250; D-017.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch13 import lab_d, sources
from companion.ch13.common import csv, emit
from plantp import datapack, screening, stats, windres as wr


def storms(seed: int = 147, years: int = 20):
    """Independent storm peaks (ten-minute, 100 m): Poisson with 4 storms
    a year, peaks above 25.3 m/s exceed it by an exponential amount with
    mean 1.0 m/s (A-257): annual maxima follow a Gumbel law with location
    25.3 + ln 4 and scale 1.0, near the chapter's site fit."""
    rng = np.random.default_rng(seed)
    peaks, ann = [], []
    for _ in range(years):
        n = rng.poisson(4.0)
        p = 25.3 + rng.exponential(1.0, n)
        peaks.append(p)
        ann.append(p.max() if n else 25.3 - rng.exponential(0.5))
    return peaks, np.array(ann)


def pot_level(peaks, years: float, u: float, period: float) -> float:
    ex = np.concatenate(peaks) - u
    ex = ex[ex > 0]
    lam = len(ex) / years
    return u + ex.mean() * math.log(lam * period)


def extremes_pot() -> None:
    peaks, ann = storms()
    mu, beta = stats.gumbel_fit_moments(ann)
    g50 = stats.return_level(mu, beta, 50)
    p50 = pot_level(peaks, 20, 25.3, 50)
    true50 = 25.3 + math.log(4) + 1.0 * -math.log(-math.log(1 - 1 / 50))
    rng = np.random.default_rng(148)
    bg, bp = [], []
    for _ in range(1000):
        k = rng.integers(0, 20, 20)
        a = ann[k]
        m, b = stats.gumbel_fit_moments(a)
        bg.append(stats.return_level(m, b, 50))
        bp.append(pot_level([peaks[i] for i in k], 20, 25.3, 50))
    qg, qp = np.quantile(bg, [0.05, 0.95]), np.quantile(bp, [0.05, 0.95])
    n_peaks = sum(len(p) for p in peaks)
    gust = p50 * (1 + 2.5 * 0.10)
    lines = ["50-year ten-minute wind from 20 years of synthetic storms (A-257):",
             f"  storms above 25.3 m/s: {n_peaks} in 20 years; annual maxima: 20",
             "  method              50-year m/s   90 % interval (bootstrap)",
             f"  annual maxima        {g50:6.1f}       {qg[0]:.1f} .. {qg[1]:.1f}",
             f"  peaks over threshold {p50:6.1f}       {qp[0]:.1f} .. {qp[1]:.1f}",
             f"  true value of this synthetic climate: {true50:.1f} m/s",
             f"  50-year gust, x (1 + 2.5 x 0.10) at storm turbulence: {gust:.1f} m/s",
             "  the storm method uses every storm, not one per year: its",
             "  interval is narrower; both need independent storms and a",
             "  threshold chosen with care; the design value and its gust",
             "  relation follow the design standard's method (chapter 11)"]
    emit("h_pot", lines)


def matrix_mcp() -> None:
    m = sources.mast_year()
    lg = m["logged"]
    ok10 = ~np.isnan(lg["v100"]) & ~m["iced"]
    site = np.where(ok10, lg["v100"], np.nan).reshape(-1, 6)
    good = np.sum(~np.isnan(site), axis=1) == 6
    y = np.mean(site[good], axis=1)
    ref = sources.reference()
    x = ref["hourly_2023"][good]
    wd = ref["wd_2023"][good]
    xl = ref["long"].ravel()
    wdl = np.tile(ref["wd_2023"], len(ref["years"]))
    vr = wr.mcp_variance_ratio(x, y, xl)[0]
    sec = wr.mcp_sector_ratio(x, y, wd, xl, wdl)
    mat = wr.mcp_matrix(x, y, wd, xl, wdl)
    cv, cp = lab_d.curve()
    e = {k: np.interp(np.clip(v, 0, None), cv, cp).sum() / len(ref["years"]) / 1e3
         for k, v in (("vr", vr), ("sec", sec), ("mat", mat))}
    lines = ["the matrix method against the others (long term, 100 m):",
             "  method                       mean m/s   MWh a year per turbine",
             f"  variance ratio               {vr.mean():7.3f}    {e['vr']:8,.0f}",
             f"  sector ratio                 {sec.mean():7.3f}    {e['sec']:8,.0f}",
             f"  matrix (sector x speed bin)  {mat.mean():7.3f}    {e['mat']:8,.0f}",
             "  the matrix lets the ratio change with speed and keeps more of",
             "  the strong winds: +0.1 % of mean speed but +1.6 % of energy;",
             "  thin cells (under 30 hours) fall back to the sector ratio; the",
             "  spread between methods is part of the MCP uncertainty"]
    emit("h_matrix", lines)


def timing() -> None:
    """When the wind produces at three hub heights next to the PV, and the
    curtailment at the 100 MW export limit (data year, no losses)."""
    t = sources.mast_year()["true"]
    alpha = np.log(t["v100"] / t["v60"]) / math.log(100 / 60)
    cv, cp = lab_d.curve()
    h = datapack.load_hourly()
    pv = np.asarray(screening.pv_ac_power_mw(h["ghi_wm2"].to_numpy(float), 60.0, 50.0))
    hour = np.arange(8760) % 24
    night = (hour >= 20) | (hour < 6)
    lines = ["when the wind produces, by hub height (true mast year, 12 turbines,",
             "  pack curve at 1.225 kg/m3, PV from the screening model):",
             "  hub m   wind GWh   night share   in PV hours   curtailed at 100 MW"]
    rows = []
    for z in (60, 100, 150):
        v = t["v100"] * (z / 100) ** alpha
        p = 12 * np.interp(v, cv, cp).reshape(-1, 6).mean(axis=1) / 1e3      # MW
        e = p.sum() / 1e3
        cur = np.clip(p + pv - 100.0, 0, None).sum() / 1e3
        lines.append(f"  {z:4d}    {e:7.1f}      {100 * p[night].sum() / p.sum():5.1f} %"
                     f"       {100 * p[pv > 1].sum() / p.sum():5.1f} %      {cur:5.2f} GWh")
        prof = [p[hour == k].mean() for k in range(24)]
        rows.append(prof)
    csv("ch13-timing.csv", "hour,h60,h100,h150,pv",
        [(k, f"{rows[0][k]:.2f}", f"{rows[1][k]:.2f}", f"{rows[2][k]:.2f}",
          f"{pv[hour == k].mean():.2f}") for k in range(24)])
    lines += ["  a taller hub adds more of its energy at night, when the stable",
              "  shear is large and the PV is off: the hybrid's profile fills;",
              "  curtailment stays near a tenth of a per cent of the wind energy;",
              "  a reason to measure the shear by hour (chapter 17 uses it)"]
    emit("h_timing", lines)


def substitution() -> None:
    m = sources.mast_year()
    lg, t = m["logged"], m["true"]
    hour = t["hour"]
    ok = ~np.isnan(lg["v100"]) & ~m["iced"] & (lg["v60"] > 3)
    a = np.log(lg["v100"] / lg["v60"]) / math.log(100 / 60)
    a_h = np.array([np.mean(a[ok & (hour == k)]) for k in range(24)])
    rec = lg["v60"] * (100 / 60) ** a                       # record by record
    fill_rec = lg["v60"] * (80 / 60) ** a
    fill_hour = lg["v100"] * (80 / 100) ** a_h[hour]
    clean = ok & ~m["shadow"] & ~m["wear"]
    b, c = np.polyfit(lg["v100"][clean], lg["v80"][clean], 1)
    fill_lin = b * lg["v100"] + c
    test = ok & (m["shadow"] | m["wear"])                  # the records to fill
    del rec
    lines = ["filling the 80 m records the QC removed (shadow, wear) and checking",
             "  each method against the true 80 m speed (synthetic, so known):",
             "  method                               bias       rms error"]
    for name, f in (("profile of the same record (60/100)", fill_rec),
                    ("shear by hour from 100 m", fill_hour),
                    ("line fitted on clean 80/100 records", fill_lin)):
        err = f[test] - t["v80"][test]
        lines.append(f"  {name:36s} {100 * err.mean() / t['v80'][test].mean():+6.2f} %"
                     f"    {np.sqrt(np.mean(err ** 2)):.3f} m/s")
    lines += [f"  records filled: {int(test.sum()):,}",
              "  the same-record profile is exact here only because the synthetic",
              "  profile is a pure power law; on real data it is still the best",
              "  start, as it carries the hour's stability, and its error is",
              "  measured on clean records; filled values are flagged",
              "  'substituted' and never count as measured data recovery"]
    emit("h_substitution", lines)


if __name__ == "__main__":
    extremes_pot()
    matrix_mcp()
    timing()
    substitution()
