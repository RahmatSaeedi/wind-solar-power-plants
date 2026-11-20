"""Chapter 13, sections A2-A3 - deeper atmosphere and instruments:
stability from two temperatures (bulk Richardson number), the rotor-
equivalent wind speed of day, night, veer and low-level-jet profiles,
gust factors of synthetic one-second records, averaging directions,
a generic against an individual cup calibration, air density at hub
height from a ground pressure sensor, and the effect of a vane offset on
the wake estimate of chapter 11's layout.

Run from the project root:   python -m companion.ch13.examples_e
Writes companion/ch13/expected/e_*.txt and diagrams/data/ch13-*.csv.
Teaching values A-257 (temperatures, calibrations, gust records).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch11 import lab_d as l11
from companion.ch13 import lab_d, sources
from companion.ch13.common import csv, emit
from plantp import physics, wind as w, windres as wr

HUB, RADIUS = 100.0, 75.0


def stability() -> None:
    """Bulk Richardson number from 10 m and 92 m temperatures (A-257) and
    the mean 60/100 m speeds of each period (a_profiles)."""
    cases = [("night 22-04", 6.0, 7.6, 6.42, 7.57),
             ("morning 07", 9.0, 8.3, 6.37, 7.13),
             ("midday 13", 18.0, 16.6, 6.21, 6.61),
             ("evening 18", 14.0, 13.3, 6.07, 6.80)]
    lines = ["stability from two temperatures (10 and 92 m, A-257) and the",
             "  shear of the 60 and 100 m means:",
             "  period         T10   T92   dtheta/dz K/m   Ri bulk   class"]
    for name, t1, t2, v1, v2 in cases:
        dth = (t2 - t1) / 82 + wr.GAMMA_DRY
        # speed gradient from 60-100 m stands for the layer (bulk estimate)
        dudz = (v2 - v1) / 40
        ri = wr.G / (273.15 + 0.5 * (t1 + t2)) * dth / dudz ** 2
        cls = ("unstable" if ri < -0.05 else "near neutral" if ri < 0.05
               else "stable" if ri < 0.25 else "very stable")
        lines.append(f"  {name:13s} {t1:5.1f} {t2:5.1f}   {dth:+.4f}       "
                     f"{ri:+7.2f}   {cls}")
    lines += ["  potential temperature adds 0.0098 K/m to the measured",
              "  gradient: air that cools more slowly than that with height",
              "  is stable; well above Ri 0.25 the night layer barely mixes",
              "  (the steep night shear and low turbulence of section A)"]
    emit("e_stability", lines)


def rews() -> None:
    v0 = 8.0
    pl = (lambda a: (lambda z: v0 * (z / HUB) ** a))

    def jet(z):
        z = np.asarray(z, float)
        base = v0 * (z / HUB) ** 0.32
        nose = v0 * (130 / HUB) ** 0.32
        return np.where(z <= 130, base, nose - 0.03 * (z - 130))

    cases = [("uniform", lambda z: np.full_like(np.asarray(z, float), v0), 0.0),
             ("day, shear 0.12", pl(0.12), 0.0),
             ("year mean, shear 0.233", pl(0.233), 0.0),
             ("night, shear 0.32", pl(0.32), 0.0),
             ("night, shear 0.32 + veer 0.25 deg/m", pl(0.32), 0.25),
             ("jet: nose at 130 m, falling above", jet, 0.0)]
    lines = [f"rotor-equivalent wind speed, hub {HUB:.0f} m, rotor"
             f" {2 * RADIUS:.0f} m, hub speed {v0:.1f} m/s:",
             "  profile                               REWS m/s   (REWS/hub)^3"]
    rows = []
    for name, f, veer in cases:
        r = wr.rotor_equivalent(f, HUB, RADIUS, veer)
        lines.append(f"  {name:36s}  {r:7.3f}     {(r / v0) ** 3:7.3f}")
    for z in range(25, 180, 5):
        rows.append((z, f"{float(pl(0.12)(z)):.3f}", f"{float(pl(0.32)(z)):.3f}",
                     f"{float(jet(z)):.3f}"))
    csv("ch13-profiles.csv", "z,day,night,jet", rows)
    lines += ["  the hub speed alone misses what the upper and lower blade",
              "  see: with a power law the disc carries a little less power",
              "  than the hub speed says (most for a gentle shear), veer takes",
              "  about 4 % and a jet nose below the top about 10 %; below",
              "  rated the power follows the cube of the ratio"]
    emit("e_rews", lines)


def gust() -> None:
    """One-second records: mean 10 m/s, turbulence intensity 0.08 .. 0.20,
    first-order autoregressive with a 15 s time scale (A-257)."""
    rng = np.random.default_rng(144)
    lines = ["gust factor of ten-minute records (3 s gust / 10 min mean):",
             "  TI     mean G   95 % of G   peak factor (G-1)/TI"]
    for ti in (0.08, 0.13, 0.20):
        gs = []
        for _ in range(300):
            x = 10.0 * (1 + ti * sources.ar1(600, 15.0, rng))
            gs.append(wr.gust_factor(x, 3)[0])
        g = np.array(gs)
        lines.append(f"  {ti:.2f}    {g.mean():.3f}     {np.quantile(g, 0.95):.3f}"
                     f"        {(g.mean() - 1) / ti:.2f}")
    lines += ["  the gust grows with turbulence: G is about 1 + g x TI with a",
              "  peak factor g near 2.5 for these records (real spectra, longer",
              "  records and shorter gust windows give larger g); the mast",
              "  logs the ten-minute maximum of the one-second samples"]
    emit("e_gust", lines)


def dirmean() -> None:
    sample = [350.0, 355.0, 2.0, 8.0, 12.0, 358.0]
    scalar = float(np.mean(sample))
    vec = wr.vector_mean_direction(sample)
    m = sources.mast_year()["true"]
    wd = m["wd100"].reshape(-1, 6)
    v = m["v100"].reshape(-1, 6)
    sc = wd.mean(axis=1)
    vm = np.array([wr.vector_mean_direction(a, b) for a, b in zip(wd, v)])
    bad = np.abs(wr.angle_diff(sc, vm)) > 10
    lines = ["averaging directions:",
             f"  six ten-minute directions {', '.join(f'{a:.0f}' for a in sample)}",
             f"  arithmetic mean {scalar:.1f} deg (wrong); vector mean {vec:.1f}"
             " deg",
             "  mast year, hourly means of six records:",
             f"    arithmetic mean off by more than 10 deg in"
             f" {int(bad.sum())} of {len(bad)} hours ({100 * bad.mean():.1f} %)",
             "  every hour that straddles north is wrong by about 180 deg;",
             "  loggers and scripts average the sine and cosine (vector"
             " mean),",
             "  often weighted by speed"]
    emit("e_dirmean", lines)


def transfer() -> None:
    """Individual calibration v = 0.04897 f + 0.207 against a generic
    v = 0.0495 f + 0.200 typed into the logger (A-255, teaching)."""
    t = sources.mast_year()["true"]
    v = t["v100"]
    f = (v - 0.207) / 0.04897
    vg = wr.cup_speed(f, 0.0495, 0.200)
    cv, cp = lab_d.curve()
    sens_e = np.interp(vg, cv, cp).sum() / np.interp(v, cv, cp).sum() - 1
    lines = ["a generic transfer function in place of the cup's certificate:",
             "  certificate  v = 0.04897 f + 0.207;  logger  v = 0.0495 f + 0.200",
             f"  at 4 m/s: {float(wr.cup_speed((4 - 0.207) / 0.04897, 0.0495, 0.2)):.3f};"
             f" at 8 m/s: {float(wr.cup_speed((8 - 0.207) / 0.04897, 0.0495, 0.2)):.3f};"
             f" at 14 m/s:"
             f" {float(wr.cup_speed((14 - 0.207) / 0.04897, 0.0495, 0.2)):.3f}",
             f"  mean speed of the year {100 * (vg.mean() / v.mean() - 1):+.2f} %;"
             f" energy {100 * sens_e:+.2f} %",
             "  fix: back-calculate the frequency with the logger's factors",
             "  and apply the certificate's (records kept in the metadata);",
             "  never apply a correction twice"]
    emit("e_transfer", lines)


def hub_density() -> None:
    t = sources.mast_year()["true"]
    p2, t2 = t["p"], t["t"]
    dz = 98.0
    t_hub = t2 - 0.0065 * dz                    # standard lapse, teaching
    p_hub = p2 * np.exp(-wr.G * dz / (287.05 * (273.15 + 0.5 * (t2 + t_hub))))
    rho2 = np.asarray(physics.air_density(p2, t2))
    rhoh = np.asarray(physics.air_density(p_hub, t_hub))
    v = t["v100"]
    cv, cp = lab_d.curve()
    e2 = np.interp(w.density_equivalent_speed(v, rho2), cv, cp).sum()
    eh = np.interp(w.density_equivalent_speed(v, rhoh), cv, cp).sum()
    lines = ["air density at hub height from a pressure sensor at 2 m:",
             f"  pressure 98 m higher: x {float(np.mean(p_hub / p2)):.4f};"
             f" temperature -{0.0065 * dz:.2f} K (standard lapse)",
             f"  mean density at 2 m {rho2.mean():.4f}, at the hub"
             f" {rhoh.mean():.4f} kg/m3 ({100 * (rhoh.mean() / rho2.mean() - 1):+.2f} %)",
             f"  energy with the hub density: {100 * (eh / e2 - 1):+.2f} %"
             " (density-equivalent speed)",
             "  the data pack gives station pressure and 2 m temperature:",
             "  chapter 11 used them as they are (D-008); D-017 reduces the",
             "  pressure to the hub; a stable night (warmer air aloft) lowers",
             "  the hub density a little more than the standard lapse says"]
    emit("e_hubdensity", lines)


def farm_energy_wd(xy, wd_model):
    """Chapter 11's farm loop with a given direction series (MWh)."""
    v, _, rho = l11.hourly()
    v_eq = w.density_equivalent_speed(v, rho)
    vg, _, _, ctg = l11.rotor.curve_arrays()
    e_free = e_wake = 0.0
    for k in np.flatnonzero(v_eq > 2.5):
        ct = float(np.interp(v_eq[k], vg, ctg))
        vs = w.farm_speeds(xy, float(v_eq[k]), float(wd_model[k]), ct, l11.D)
        e_free += l11.N_T * float(l11.pack_power(v_eq[k]))
        e_wake += float(l11.pack_power(vs).sum())
    return e_free / 1e3, e_wake / 1e3


def vane_wake() -> None:
    _, wd, _ = l11.hourly()
    off = (wd + 20.0) % 360
    lay = l11.layouts()["A: 2 rows of 6, 4D x 8D"]
    xy_true = l11.rotate(lay, l11.prevailing(wd))
    xy_off = l11.rotate(lay, l11.prevailing(off))
    f0, w0 = farm_energy_wd(xy_true, wd)
    f1, w1 = farm_energy_wd(xy_true, off)
    f2, w2 = farm_energy_wd(xy_off, wd)
    lines = ["a vane mounted 20 deg off, and chapter 11's wake model (layout A):",
             f"  prevailing sector: true {l11.prevailing(wd):.0f} deg,"
             f" with the offset {l11.prevailing(off):.0f} deg",
             "  case                                       wake loss   farm GWh",
             f"  true directions, layout for the true wind   {100 * (1 - w0 / f0):6.2f} %"
             f"   {w0 / 1e3:7.2f}",
             f"  estimate with the offset directions         {100 * (1 - w1 / f1):6.2f} %"
             f"   {w1 / 1e3:7.2f}",
             f"  layout turned to the offset, true wind      {100 * (1 - w2 / f2):6.2f} %"
             f"   {w2 / 1e3:7.2f}",
             "  a direction error moves energy between sectors: the wake",
             "  estimate and the layout follow the wrong rose; the vane's",
             "  north mark, photos and a second vane or the lidar find it"]
    emit("e_vanewake", lines)


if __name__ == "__main__":
    stability()
    rews()
    gust()
    dirmean()
    transfer()
    hub_density()
    vane_wake()
