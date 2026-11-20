"""Chapter 12, further lessons - the uncertainty of one reading against an
annual sum, spatial variability across the array (how many sensors), dust
and aerosol (beam against diffuse), one-minute ramps, solar-wind
complementarity at Plant P, and the side-by-side check that commissions a
station.

Run from the project root:   python -m companion.ch12.examples_g
Writes companion/ch12/expected/g_*.txt and diagrams/data/ch12-*.csv.
Data pack 1.1.0 (S0); teaching values A-249 (see the text).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch10 import pvyear10
from companion.ch12 import sources
from companion.ch12.common import csv, emit
from plantp import datapack, irradiance as ir, pvcell as pc


def reading_uncertainty() -> None:
    """One hourly value against the annual sum: random parts average out,
    systematic parts do not (teaching standard uncertainties)."""
    systematic = {"calibration factor": 0.012, "directional response": 0.005,
                  "levelling": 0.003}
    random_h = {"thermal offset and noise": 0.010, "temperature dependence": 0.004,
                "non-linearity": 0.003, "soiling between cleanings": 0.004}
    u_sys = ir.combine_uncertainty(*systematic.values())
    u_rnd = ir.combine_uncertainty(*random_h.values())
    n_eff = 4380 / 24                                     # days as independent
    lines = ["uncertainty of one hourly GHI value and of the annual sum (teaching):",
             "  systematic parts (same sign every hour):"]
    for k, v in systematic.items():
        lines.append(f"    {k:28s} {100 * v:.1f} %")
    lines.append("  random parts (change from hour to hour, correlated within a day):")
    for k, v in random_h.items():
        lines.append(f"    {k:28s} {100 * v:.1f} %")
    lines += [f"  one hourly value: {100 * ir.combine_uncertainty(u_sys, u_rnd):.1f} %",
              f"  annual sum: random part / sqrt({n_eff:.0f} days) ->"
              f" {100 * u_rnd / math.sqrt(n_eff):.2f} %; total"
              f" {100 * ir.combine_uncertainty(u_sys, u_rnd / math.sqrt(n_eff)):.1f} %",
              "  the calibration factor dominates the year; the random parts",
              "  dominate a single hour (performance tests over short periods)"]
    emit("g_reading", lines)


def spatial() -> None:
    """Two POA sensors at distance d see the same broken-cloud field with a
    delay d / u_cloud (frozen clouds moving at 10 m/s, teaching)."""
    x = sources.minute_days()["broken"]["true"]
    day = x > 20
    rows, lines = [], ["two sensors under moving clouds (broken day, frozen-cloud model):",
                       "  distance m  delay min  r one-minute  r ten-minute  daily diff"]
    for d in (0, 100, 300, 600, 1200, 2400):
        lag = int(round(d / 10 / 60))
        y = np.roll(x, lag)
        r1 = float(np.corrcoef(x[day], y[day])[0, 1])
        x10, y10 = x.reshape(-1, 10).mean(axis=1), y.reshape(-1, 10).mean(axis=1)
        d10 = x10 > 20
        r10 = float(np.corrcoef(x10[d10], y10[d10])[0, 1])
        rows.append((d, f"{r1:.4f}", f"{r10:.4f}"))
        lines.append(f"  {d:8d}    {lag:4d}       {r1:.3f}         {r10:.3f}"
                     f"        {100 * (y.sum() / x.sum() - 1):+.2f} %")
    lines += ["  this synthetic day's clouds last tens of minutes, so minute values",
              "  stay alike over a few hundred metres and part over kilometres;",
              "  real cloud edges are smaller and part sooner. Daily sums agree:",
              "  one sensor per block suffices for daily PR; minute studies",
              "  (ramps, clipping) need sensors next to the blocks studied"]
    emit("g_spatial", lines)
    csv("ch12-spatial.csv", "d,r1,r10", rows)


def aerosol() -> None:
    """A dusty clear day (A-249): aerosol removes 30 % of the beam and turns
    a third of it into diffuse light; GHI changes much less."""
    p = sources.pack()
    k = slice(173 * 24, 174 * 24)
    ghi, dni, dhi, cz = p["ghi"][k], p["dni"][k], p["dhi"][k], p["cz"][k]
    dni2 = 0.70 * dni
    dhi2 = dhi + 0.10 * dni * cz
    ghi2 = dni2 * cz + dhi2
    ci_f, cz_f, n = pvyear10.geometry(25.0, 180.0)
    g0 = ir.g0n(n[k])
    b1, s1, r1 = pc.poa_hay_davies(ghi, dni, dhi, ci_f[k], cz_f[k], g0, 25.0)
    b2, s2, r2 = pc.poa_hay_davies(ghi2, dni2, dhi2, ci_f[k], cz_f[k], g0, 25.0)
    lines = ["a dusty clear day, 23 June (A-249: beam -30 %, a third of the lost",
             "beam reappears as diffuse):",
             f"  GHI {ghi.sum() / 1e3:.2f} -> {ghi2.sum() / 1e3:.2f} kWh/m2"
             f" ({100 * (ghi2.sum() / ghi.sum() - 1):+.1f} %)",
             f"  DNI {dni.sum() / 1e3:.2f} -> {dni2.sum() / 1e3:.2f} kWh/m2 (-30 %)",
             f"  POA 25 deg {(b1 + s1 + r1).sum() / 1e3:.2f} ->"
             f" {(b2 + s2 + r2).sum() / 1e3:.2f} kWh/m2"
             f" ({100 * ((b2 + s2 + r2).sum() / (b1 + s1 + r1).sum() - 1):+.1f} %)",
             "  GHI falls about half as much as DNI: dust shows most clearly in",
             "  DNI and in the diffuse fraction; trackers (beam) lose more than",
             "  fixed fronts, and the modules get dirty too"]
    emit("g_aerosol", lines)


def ramps() -> None:
    x = sources.minute_days()["broken"]["true"]
    r1 = np.diff(x)
    x10 = x.reshape(-1, 10).mean(axis=1)
    r10 = np.diff(x10)
    p_plant = 50.0 / 1000                                 # MW per W/m2 (rough)
    lines = ["ramps of GHI on the broken-cloud day:",
             f"  one-minute steps: largest {np.abs(r1).max():.0f} W/m2, 99th"
             f" percentile {np.quantile(np.abs(r1), 0.99):.0f} W/m2",
             f"  ten-minute steps: largest {np.abs(r10).max():.0f} W/m2",
             f"  one sensor's largest minute step times the plant: about"
             f" {np.abs(r1).max() * p_plant:.0f} MW in a minute",
             "  the plant's 28 ha smooth this (clouds cover blocks one after",
             "  another): the plant ramp is smaller than one sensor's; grid",
             "  ramp limits and storage sizing need the plant's ramps (ch 19, 27)"]
    emit("g_ramps", lines)
    edges = np.arange(0, 700, 25)
    h1, _ = np.histogram(np.abs(r1), edges)
    csv("ch12-ramps.csv", "step,count", [(f"{a + 12.5:.0f}", int(c))
                                         for a, c in zip(edges[:-1], h1)])


def complementarity() -> None:
    p = sources.pack()
    pv_ac = pvyear10.dc_power() * 0.98 / 1e6
    h = datapack.load_hourly()
    from companion.ch11 import lab_d as w11
    v, _, rho = w11.hourly()
    from plantp import wind as w
    wind_mw = 12 * w11.pack_power(w.density_equivalent_speed(v, rho)) / 1e3
    hours = p["hour"]
    rows = []
    for hh in range(24):
        sel = hours == hh
        rows.append((hh, f"{pv_ac[sel].mean():.3f}", f"{wind_mw[sel].mean():.3f}"))
    r_h = float(np.corrcoef(pv_ac, wind_mw)[0, 1])
    mon = p["month"]
    pv_m = np.array([pv_ac[mon == m].sum() for m in range(12)])
    wd_m = np.array([wind_mw[mon == m].sum() for m in range(12)])
    r_m = float(np.corrcoef(pv_m, wd_m)[0, 1])
    both = pv_ac + wind_mw
    lines = ["solar and wind at Plant P (data-pack year, before losses):",
             f"  hourly correlation r = {r_h:+.3f}; monthly r = {r_m:+.3f}",
             f"  hours with combined output above 100 MW: {(both > 100).sum()}",
             f"  standard deviation of hourly output: solar {pv_ac.std():.1f}, wind"
             f" {wind_mw.std():.1f}, together {both.std():.1f} MW",
             "  wind is stronger at night and in winter, solar by day and in",
             "  summer: the two fill each other's gaps, which is the reason for",
             "  a hybrid plant behind one connection (chapters 17 and 18)"]
    emit("g_complement", lines)
    csv("ch12-diurnal.csv", "hour,pv,wind", rows)
    del h


def side_by_side() -> None:
    """Commissioning: four pyranometers side by side for 14 days; one was
    set up with the sensitivity of another serial (+3.6 % reading)."""
    p = sources.pack()
    k = slice(100 * 24, 114 * 24)
    rng = np.random.default_rng(151)
    ref = p["ghi"][k]
    factors = [1.000, 1.004, 1.036, 0.997]
    lines = ["side-by-side check of four pyranometers, 14 days (A-249):",
             "  sensor  ratio to the median   verdict"]
    reads = [ref * f * (1 + 0.004 * rng.standard_normal(len(ref))) for f in factors]
    med = np.median(np.array(reads), axis=0)
    ok = ref > 200
    for i, x in enumerate(reads):
        r = x[ok].sum() / med[ok].sum()
        verdict = "accept" if abs(r - 1) < 0.015 else "check certificate"
        lines.append(f"  S{i + 1}      {r:.4f}                {verdict}")
    lines += ["  sensor S3 reads about 3.3 % above the median (3.6 % was put in):",
              "  its logger used the sensitivity",
              "  of another serial; found before the campaign started, not a",
              "  year later in the energy report"]
    emit("g_sidebyside", lines)


if __name__ == "__main__":
    reading_uncertainty()
    spatial()
    aerosol()
    ramps()
    complementarity()
    side_by_side()
