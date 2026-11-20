"""Chapter 12, section A - solar geometry and resource terms with the
Plant P year: timestamps and sun position, extraterrestrial irradiation
and clearness index, component closure, clear sky, decomposition,
transposition models, horizon shading and the seasons.

Run from the project root:   python -m companion.ch12.examples_a
Writes companion/ch12/expected/a_*.txt and diagrams/data/ch12-*.csv.
Data pack 1.1.0 (S0); teaching values A-243, A-244.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch10 import pvyear10
from companion.ch12 import sources
from companion.ch12.common import csv, emit
from plantp import irradiance as ir, pvcell as pc, solar

TILT, AZ = 25.0, 180.0
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def instant_geometry(offset_h: float, tilt: float = TILT):
    """cos(zenith) and cos(incidence) at one instant of each hour."""
    idx = np.arange(8760)
    n, hour = idx // 24 + 1, idx % 24
    st = solar.solar_time(hour + offset_h, n)
    el, az = solar.sun_position(sources.LAT, n, st)
    up = el > 0
    cz = np.where(up, np.sin(np.radians(el)), 0.0)
    ci = np.where(up, np.clip(solar.incidence_cos(el, az, tilt, AZ), 0, None), 0.0)
    return cz, ci


def timestamps() -> None:
    p = sources.pack()
    ref = pvyear10.poa()["poa"].sum() / 1e3
    lines = ["timestamps: the pack labels each hourly mean by its START",
             "(local standard time +04:00); the sun must be taken over the hour",
             f"  POA, sun averaged over the hour (chapter 10):  {ref:7.0f} kWh/m2"]
    ref_h = pvyear10.poa()["poa"]
    sunny = ref_h > 300
    for off, name in ((0.5, "sun at the centre of the hour"),
                      (0.0, "sun at the label (start)"),
                      (1.0, "sun at the end of the hour")):
        cz, ci = instant_geometry(off)
        beam, sky, ground = pc.poa_hay_davies(p["ghi"], p["dni"], p["dhi"], ci,
                                             cz, p["g0n"], TILT)
        h = beam + sky + ground
        tot = h.sum() / 1e3
        rms = 100 * np.sqrt(np.mean(((h - ref_h)[sunny] / ref_h[sunny]) ** 2))
        lines.append(f"  {name:31s} {tot:6.0f} kWh/m2 ({100 * (tot / ref - 1):+.1f} %);"
                     f" hourly RMS {rms:.1f} %")
    noon = 12 - float(solar.equation_of_time(174)) / 60
    lines += [f"  solar noon on 23 June: {int(noon)}:{round((noon % 1) * 60):02d}"
              " local standard time (equation of time)",
              "  a half-hour error in the time convention moves the beam onto",
              "  the wrong side of noon: morning and evening hours swap"]
    emit("a_time", lines)


def extraterrestrial() -> None:
    p = sources.pack()
    phi = math.radians(sources.LAT)
    rows, lines = [], ["extraterrestrial irradiation and clearness index at 34 deg N:",
                       "  month  H0 kWh/m2/d  H kWh/m2/d  K_T"]
    for m in range(12):
        sel = p["month"] == m
        days = sel.sum() / 24
        doy = p["doy"][sel]
        d = np.radians(solar.declination(doy))
        ws = np.arccos(np.clip(-np.tan(phi) * np.tan(d), -1, 1))
        h0 = 24 / math.pi * ir.g0n(doy) * (np.cos(phi) * np.cos(d) * np.sin(ws)
                                          + ws * np.sin(phi) * np.sin(d)) / 1e3
        h0d = float(h0.mean())
        hd = p["ghi"][sel].sum() / 1e3 / days
        rows.append((MONTHS[m], f"{h0d:.2f}", f"{hd:.2f}", f"{hd / h0d:.3f}"))
        lines.append(f"  {MONTHS[m]}    {h0d:7.2f}     {hd:7.2f}    {hd / h0d:.3f}")
    total0 = sum(float(r[1]) * 0 for r in rows)
    lines += [f"  extraterrestrial normal: {float(ir.g0n(3)):.0f} W/m2 in early"
              f" January, {float(ir.g0n(185)):.0f} W/m2 in early July",
              "  K_T is the share of the top-of-atmosphere energy that reaches",
              "  the ground: a dry site has high K_T in summer"]
    del total0
    emit("a_extra", lines)
    csv("ch12-kt.csv", "month,h0,h,kt", [(k + 1, r[1], r[2], r[3])
                                          for k, r in enumerate(rows)])


def components() -> None:
    p = sources.pack()
    r = ir.closure_ratio(p["ghi"], p["dni"], p["dhi"], p["cz"])
    test = (p["cz"] > math.sin(math.radians(15))) & (p["ghi"] > 50)
    dev = np.abs(r[test] - 1)
    lines = ["component closure GHI = DNI cos z + DHI over the pack year:",
             f"  hours tested (sun above 15 deg, GHI > 50 W/m2): {test.sum():,}",
             f"  within 2 %: {100 * np.mean(dev < 0.02):.1f} %;"
             f" within 8 %: {100 * np.mean(dev < 0.08):.1f} %",
             f"  median ratio {np.median(r[test]):.4f}",
             "  the pack's DNI and DHI were computed from its GHI, so they",
             "  close by construction; three real instruments disagree, and",
             "  the closure test finds which one drifts (section C)"]
    emit("a_components", lines)


def clear_sky() -> None:
    p = sources.pack()
    cs = ir.clear_sky_haurwitz(p["cz"])
    lines = ["clear-sky index GHI / GHI_clear (Haurwitz) by month:",
             "  month  GHI kWh/m2  clear kWh/m2  index  clear-sky hours"]
    for m in range(12):
        sel = p["month"] == m
        g, c = p["ghi"][sel].sum() / 1e3, cs[sel].sum() / 1e3
        k = np.divide(p["ghi"][sel], cs[sel], out=np.zeros(sel.sum()),
                      where=cs[sel] > 50)
        lines.append(f"  {MONTHS[m]}    {g:7.1f}     {c:7.1f}     {g / c:.3f}"
                     f"   {int(np.sum(k > 0.9))}")
    lines += [f"  year: {p['ghi'].sum() / 1e3:,.0f} of {cs.sum() / 1e3:,.0f} kWh/m2"
              f" clear-sky ({p['ghi'].sum() / cs.sum():.3f})",
              "  Haurwitz uses only the sun's height; it has no aerosol or",
              "  water vapour, so it is a check, not a model of the site"]
    emit("a_clearsky", lines)


def decomposition() -> None:
    p = sources.pack()
    up = p["cz"] > 0.087
    kt = ir.clearness_index(p["ghi"], p["cz"], p["g0n"])
    dni_e, dhi_e = ir.decompose(p["ghi"], p["cz"], p["g0n"])
    kd = np.divide(p["dhi"], p["ghi"], out=np.full(8760, np.nan), where=p["ghi"] > 20)
    rng = np.random.default_rng(7)
    pick = rng.choice(np.flatnonzero(up & (p["ghi"] > 20)), 1500, replace=False)
    csv("ch12-kdkt.csv", "kt,kd", [(f"{kt[k]:.3f}", f"{kd[k]:.3f}") for k in pick])
    grid = np.linspace(0.0, 0.85, 86)
    csv("ch12-erbs.csv", "kt,kd", [(f"{x:.3f}", f"{float(ir.erbs_diffuse_fraction(x)):.4f}")
                                   for x in grid])
    csv("ch12-orgill.csv", "kt,kd",
        [(f"{x:.3f}", f"{float(ir.orgill_hollands_diffuse_fraction(x)):.4f}")
         for x in grid])
    dni_o, dhi_o = ir.decompose(p["ghi"], p["cz"], p["g0n"], model="orgill")
    ci, cz, _ = pvyear10.geometry(TILT, AZ)
    tot = {}
    for name, (dn, dh) in (("erbs", (dni_e, dhi_e)), ("orgill", (dni_o, dhi_o))):
        b, s, g = pc.poa_hay_davies(p["ghi"], dn, dh, ci, cz, p["g0n"], TILT)
        tot[name] = ((b + s + g).sum() / 1e3, dn.sum() / 1e3, dh.sum() / 1e3)
    e, o = tot["erbs"], tot["orgill"]
    lines = ["two decomposition models on the same GHI (the pack's own DNI and",
             "DHI were made with Erbs when the pack was built, A-013):",
             f"  Erbs reproduces the pack: DHI bias"
             f" {ir.mbe(dhi_e[up], p['dhi'][up]):+.1f} W/m2 (a circular test)",
             "  model          DNI kWh/m2  DHI kWh/m2  POA at 25 deg",
             f"  Erbs            {e[1]:8,.0f}    {e[2]:8,.0f}     {e[0]:8,.0f}",
             f"  Orgill-Hollands {o[1]:8,.0f}    {o[2]:8,.0f}     {o[0]:8,.0f}",
             f"  POA differs by {100 * (o[0] / e[0] - 1):+.1f} %, DNI by"
             f" {100 * (o[1] / e[1] - 1):+.1f} %",
             "  when only GHI is measured, the choice of decomposition model",
             "  is an uncertainty of the plane-of-array estimate (section C);",
             "  a synthetic dataset cannot test the model that made it"]
    emit("a_decomp", lines)


def transposition() -> None:
    p = sources.pack()
    ci, cz, _ = pvyear10.geometry(TILT, AZ)
    rows, lines = [], ["isotropic and Hay-Davies skies for the Plant P plane:",
                       "  tilt  isotropic  Hay-Davies  difference"]
    for tilt in (0, 10, 20, 25, 30, 40, 50):
        ci_t, cz_t, _ = pvyear10.geometry(float(tilt), AZ)
        b, s, g = ir.poa_isotropic(p["ghi"], p["dni"], p["dhi"], ci_t, float(tilt))
        iso = (b + s + g).sum() / 1e3
        b2, s2, g2 = pc.poa_hay_davies(p["ghi"], p["dni"], p["dhi"], ci_t, cz_t,
                                       p["g0n"], float(tilt))
        hd = (b2 + s2 + g2).sum() / 1e3
        rows.append((tilt, f"{iso:.0f}", f"{hd:.0f}"))
        lines.append(f"  {tilt:4d}  {iso:9.0f}  {hd:10.0f}  {100 * (hd / iso - 1):+6.2f} %")
    best = max(rows, key=lambda r: float(r[2]))
    lines += [f"  Hay-Davies peaks at about {best[0]} deg tilt;",
              "  Plant P uses 25 deg (row spacing, wind load, D-013)",
              "  the circumsolar part of the diffuse light follows the sun:",
              "  an isotropic sky under-rates a tilted plane at a sunny site"]
    emit("a_transposition", lines)
    csv("ch12-transposition.csv", "tilt,iso,hd", rows)


def horizon() -> None:
    """Far horizon (A-243, teaching): hills to the east-north-east rising
    to 6 deg, a ridge to the west at 3 deg; flat to the south."""
    p = sources.pack()
    az_h = np.arange(0, 361, 5)
    elev_h = np.interp(az_h, [0, 50, 75, 100, 125, 180, 235, 255, 290, 310, 360],
                       [1, 2, 6, 5, 2, 0.5, 1, 3, 3, 1.5, 1])
    csv("ch12-horizon.csv", "az,elev", [(a, f"{e:.1f}") for a, e in zip(az_h, elev_h)])
    tt = np.arange(0, 24, 1 / 6)
    paths = []
    for doy in (172, 80, 355):
        el, az = solar.sun_position(sources.LAT, doy, solar.solar_time(tt, doy))
        paths.append((el, az))
    rows = []
    for k in range(len(tt)):
        rows.append((f"{tt[k]:.3f}",) + tuple(
            f"{az[k]:.1f},{el[k]:.2f}" if el[k] > -1 else "nan,nan"
            for el, az in paths))
    csv("ch12-sunpath.csv", "t,az_jun,el_jun,az_mar,el_mar,az_dec,el_dec", rows)
    idx = np.arange(8760)
    n, hour = idx // 24 + 1, idx % 24
    blocked = np.zeros(8760)
    for s in (np.arange(6) + 0.5) / 6:
        el, az = solar.sun_position(sources.LAT, n, solar.solar_time(hour + s, n))
        blocked += ((el > 0) & (el < np.interp(az, az_h, elev_h))) / 6
    ci, cz, _ = pvyear10.geometry(TILT, AZ)
    beam, sky, ground = pc.poa_hay_davies(p["ghi"], p["dni"], p["dhi"], ci, cz,
                                         p["g0n"], TILT)
    lost = (beam * blocked).sum() / 1e3
    sky_loss = 0.5 * np.mean(np.sin(np.radians(elev_h)) ** 2)
    lines = ["far-horizon shading of the beam (A-243, teaching profile):",
             f"  highest horizon 6 deg at azimuth 75 (east-north-east)",
             f"  sun-up time behind the horizon: {blocked.sum():,.0f} h a year",
             f"  beam lost on the Plant P plane: {lost:.1f} kWh/m2 of"
             f" {(beam + sky + ground).sum() / 1e3:,.0f}"
             f" ({100 * lost / (beam + sky + ground).sum() * 1e3:.2f} %)",
             f"  sky-diffuse share hidden by the horizon (isotropic): about"
             f" {100 * sky_loss:.2f} %",
             "  low winter and summer-morning sun is what a far horizon takes;",
             "  near objects (masts, fences, the sensor's own neighbours)",
             "  matter more for the measurement than for the plant"]
    emit("a_horizon", lines)


def seasons() -> None:
    p = sources.pack()
    lt = sources.long_term()
    ann = lt["annual"]
    lines = ["seasons and years at the Plant P site:",
             "  month  GHI kWh/m2  day length h  mean T C"]
    phi = math.radians(sources.LAT)
    for m in range(12):
        sel = p["month"] == m
        doy = int(np.median(p["doy"][sel]))
        d = math.radians(float(solar.declination(doy)))
        day = 2 * math.degrees(math.acos(-math.tan(phi) * math.tan(d))) / 15
        lines.append(f"  {MONTHS[m]}    {p['ghi'][sel].sum() / 1e3:7.1f}       "
                     f"{day:5.2f}       {p['t_air'][sel].mean():5.1f}")
    sd = float(np.std(ann, ddof=1) / np.mean(ann))
    lines += [f"  20-year provider record: mean {ann.mean():,.0f} kWh/m2,"
              f" year-to-year sd {100 * sd:.1f} %",
              f"  lowest year {ann.min():,.0f}, highest {ann.max():,.0f};"
              f" 2023 {ann[-1]:,.0f} ({100 * (ann[-1] / ann.mean() - 1):+.1f} %)",
              "  one measured year is one draw from this spread (section C)"]
    emit("a_seasons", lines)
    csv("ch12-longterm.csv", "year,ghi", [(int(y), f"{a:.1f}")
                                          for y, a in zip(lt["years"], ann)])


if __name__ == "__main__":
    timestamps()
    extraterrestrial()
    components()
    clear_sky()
    decomposition()
    transposition()
    horizon()
    seasons()
