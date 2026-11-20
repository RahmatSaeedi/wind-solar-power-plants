"""Chapter 13, section A - wind climate and measurement physics with the
synthetic Plant P mast year: day and night profiles, shear and roughness
fits, veer, turbulence intensity by speed bin, air density, and simple
instrument errors (cup overspeeding, tilt).

Run from the project root:   python -m companion.ch13.examples_a
Writes companion/ch13/expected/a_*.txt and diagrams/data/ch13-*.csv.
Synthetic mast year A-250 (true values); instrument values A-255.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch13 import sources
from companion.ch13.common import csv, emit
from plantp import windres as wr


def profiles() -> None:
    t = sources.mast_year()["true"]
    z = [60.0, 80.0, 100.0]
    rows, lines = [], ["mean profile by time of day (true values, A-250):",
                       "  hours        v60    v80    v100   shear   z0 m"]
    groups = {"night 20-06": (t["hour"] >= 20) | (t["hour"] < 6),
              "morning 06-09": (t["hour"] >= 6) & (t["hour"] < 9),
              "day 09-17": (t["hour"] >= 9) & (t["hour"] < 17),
              "evening 17-20": (t["hour"] >= 17) & (t["hour"] < 20)}
    for name, sel in groups.items():
        means = [t["v60"][sel].mean(), t["v80"][sel].mean(), t["v100"][sel].mean()]
        a = wr.fit_shear(z, means)
        z0, _ = wr.fit_roughness(z, means)
        lines.append(f"  {name:13s} {means[0]:5.2f}  {means[1]:5.2f}  {means[2]:5.2f}"
                     f"   {a:.3f}  {z0:7.3f}")
    allm = [t["v60"].mean(), t["v80"].mean(), t["v100"].mean()]
    lines += [f"  all hours     {allm[0]:5.2f}  {allm[1]:5.2f}  {allm[2]:5.2f}"
              f"   {wr.fit_shear(z, allm):.3f}",
              "  a stable night lets the upper wind slide over the lower: the",
              "  'roughness' fitted at night is not the ground's roughness but",
              "  the stability; one shear exponent for all hours hides that"]
    emit("a_profiles", lines)
    for hr in range(24):
        sel = t["hour"] == hr
        rows.append((hr, f"{t['v60'][sel].mean():.3f}", f"{t['v100'][sel].mean():.3f}",
                     f"{wr.fit_shear(z, [t['v60'][sel].mean(), t['v80'][sel].mean(), t['v100'][sel].mean()]):.4f}"))
    csv("ch13-diurnal.csv", "hour,v60,v100,alpha", rows)


def veer() -> None:
    t = sources.mast_year()["true"]
    d = wr.angle_diff(t["wd100"], t["wd60"])
    night = (t["hour"] >= 20) | (t["hour"] < 6)
    day = (t["hour"] >= 9) & (t["hour"] < 17)
    lines = ["direction change between 60 and 100 m (veer):",
             f"  night mean {d[night].mean():+.1f} deg, day {d[day].mean():+.1f} deg",
             f"  across a 150 m rotor (25 to 175 m) at night about"
             f" {d[night].mean() * 150 / 40:+.0f} deg,",
             "    if it grows linearly with height",
             "  veer twists the inflow across the rotor: the blade sees a",
             "  changing angle of attack (loads) and the turbine yaws to the",
             "  hub direction only (energy); the measurement shows if it matters"]
    emit("a_veer", lines)


def turbulence() -> None:
    t = sources.mast_year()["true"]
    edges = np.arange(3.0, 21.0, 1.0)
    rows = wr.ti_by_bin(t["v100"], t["sd100"], edges)
    lines = ["turbulence intensity at 100 m by speed bin (true values):",
             "  bin m/s  mean TI   90 % quantile   records"]
    for c, mean, q, n in rows:
        if c in (4.5, 6.5, 8.5, 10.5, 12.5, 14.5, 16.5):
            lines.append(f"  {c:5.1f}    {mean:.3f}     {q:.3f}          {n:6d}")
    q15 = [q for c, _, q, _ in rows if c == 15.5]
    lines += [f"  90 % quantile at 15 m/s: {q15[0]:.3f}" if q15 else "",
              "  the turbine's class sets a reference turbulence; the site check",
              "  compares a high quantile per bin with the class curve (the",
              "  design standard defines which quantile): U-039 needs these",
              "  ten-minute standard deviations, which hourly data cannot give"]
    emit("a_turbulence", lines)
    csv("ch13-ti.csv", "v,mean,q90", [(f"{c:.1f}", f"{m:.4f}", f"{q:.4f}")
                                      for c, m, q, _ in rows])


def density() -> None:
    t = sources.mast_year()["true"]
    rho = t["rho"]
    month = t["day"] * 12 // 365
    lines = ["air density at the mast (from pressure and temperature):",
             f"  mean {rho.mean():.3f} kg/m3; January {rho[month == 0].mean():.3f},"
             f" July {rho[month == 6].mean():.3f}",
             f"  range of ten-minute values {rho.min():.3f} .. {rho.max():.3f}",
             "  a pressure sensor near hub height (or a correction for its",
             "  height) and an air temperature sensor are part of the mast;",
             "  density enters the power curve (chapter 11, D-008)"]
    emit("a_density", lines)


def instruments() -> None:
    """Cup anemometer errors (A-255, teaching values): overspeeding in
    turbulence and cosine response to an inclined flow."""
    t = sources.mast_year()["true"]
    ti = wr.turbulence_intensity(t["v100"], t["sd100"])
    over = 1 + 0.5 * np.nan_to_num(ti) ** 2 * 0.3       # teaching overspeeding
    tilt = math.cos(math.radians(5))
    lines = ["two errors of a cup anemometer (A-255, teaching):",
             f"  overspeeding in turbulent wind: mean +{100 * (np.mean(over) - 1):.2f} %"
             f" (largest at low speed, high TI)",
             f"  flow inclined 5 deg on a slope, ideal cosine response:"
             f" {100 * (tilt - 1):+.2f} %",
             "    (real cups differ from the cosine: the class tests show how)",
             "  the cup's class (a set of tests in turbulent and inclined flow)",
             "  tells how much of this to expect; a sonic anemometer measures",
             "  the three components and has no rotating parts to wear"]
    emit("a_instruments", lines)


if __name__ == "__main__":
    profiles()
    veer()
    turbulence()
    density()
    instruments()
