"""Chapter 15, sections B3, C3 and D3 - wind energy from a distribution
against the time series, the PV performance ratio by month, night-time
import, the size of the PV block against the export limit (overbuild),
the loss of the average year against the average loss, and a first
operating year checked against the model (faults found by comparison).

Run from the project root:   python -m companion.ch15.examples_k
Writes companion/ch15/expected/k_*.txt and diagrams/data/ch15-*.csv.
Model 15.1; teaching values A-271.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch10 import pvyear10
from companion.ch11 import lab_d as l11
from companion.ch13 import sources as s13
from companion.ch15 import examples_h as eh, sources as src
from companion.ch15.common import csv, emit
from plantp import datapack, wind as w, yieldmodel as ym

GAMMA = -0.0035                       # power temperature coefficient, 1/K (teaching)
P_STC = 60.06                         # MWp DC


# [start: weibull]
def weibull_pdf(v, k, c):
    return (k / c) * (v / c) ** (k - 1) * np.exp(-(v / c) ** k)


def weibull_energy(k, c, v_max=30.0, n=3001):
    """One turbine, MWh a year, pack curve and a Weibull distribution."""
    v = np.linspace(0, v_max, n)
    f = weibull_pdf(np.maximum(v, 1e-9), k, c)
    return float(np.trapezoid(l11.pack_power(v) * f, v) * 8760 / 1e3)


def moments_fit(v):
    """Weibull k and c from the mean and standard deviation (Justus)."""
    m, s = float(np.mean(v)), float(np.std(v))
    k = (s / m) ** -1.086
    return k, m / math.gamma(1 + 1 / k)


def energy_fit(v):
    """Weibull k and c keeping the mean and the mean cube (energy)."""
    m, m3 = float(np.mean(v)), float(np.mean(v ** 3))
    lo, hi = 1.0, 4.0
    for _ in range(60):
        k = 0.5 * (lo + hi)
        c = m / math.gamma(1 + 1 / k)
        if c ** 3 * math.gamma(1 + 3 / k) > m3:
            lo = k
        else:
            hi = k
    return k, c
# [end: weibull]


def distribution() -> None:
    h = datapack.load_hourly()
    v = h["ws_100m_ms"].to_numpy(float)
    rho = s13.hub_density(h["p_hpa"].to_numpy(float), h["t_air_c"].to_numpy(float))
    veq = w.density_equivalent_speed(v, rho)
    e_ts = float(l11.pack_power(veq).sum()) / 1e3
    km, cm = moments_fit(veq)
    ke, ce = energy_fit(veq)
    lines = ["one turbine, hub density, data year: energy from the hourly series",
             "  against a fitted Weibull distribution",
             f"  hourly series                     {e_ts:7,.0f} MWh",
             f"  Weibull by moments   k {km:.2f} c {cm:.2f} {weibull_energy(km, cm):7,.0f} MWh"
             f" ({100 * (weibull_energy(km, cm) / e_ts - 1):+.1f} %)",
             f"  Weibull, mean cube   k {ke:.2f} c {ce:.2f} {weibull_energy(ke, ce):7,.0f} MWh"
             f" ({100 * (weibull_energy(ke, ce) / e_ts - 1):+.1f} %)"]
    # by 30-degree sector
    wd = h["wd_100m_deg"].to_numpy(float)
    sec = (np.floor(((wd + 15) % 360) / 30)).astype(int)
    e_sec = 0.0
    for s_ in range(12):
        m = sec == s_
        if m.sum() > 30:
            k_, c_ = moments_fit(veq[m])
            e_sec += weibull_energy(k_, c_) * m.mean()
    lines.append(f"  12 sector Weibulls by moments      {e_sec:7,.0f} MWh"
                 f" ({100 * (e_sec / e_ts - 1):+.1f} %)")
    lines.append("  the same mean speed with another shape factor (energy against k 2.0):")
    for m in (float(np.mean(veq)), 5.5):
        ref_e = weibull_energy(2.0, m / math.gamma(1.5))
        row = []
        for k_ in (1.6, 2.0, 2.4):
            c_ = m / math.gamma(1 + 1 / k_)
            row.append(f"k {k_:.1f} {100 * (weibull_energy(k_, c_) / ref_e - 1):+5.1f} %")
        lines.append(f"    mean {m:4.2f} m/s: " + ", ".join(row))
    lines += ["  a distribution keeps the speeds but loses time: it cannot give",
              "  clipping, export limits, storage or the hour-by-hour match with",
              "  PV; it is a check on the time series and a quick screening tool;",
              "  near this site's mean the shape hardly matters above k 2, but at",
              "  a low mean a wide distribution (low k) puts more hours on the",
              "  steep part of the curve: +5 % at k 1.6, -6 % at k 2.4"]
    emit("k_weibull", lines)


def performance_ratio() -> None:
    r = src.plant_year()
    poa = np.asarray(pvyear10.poa()["poa"])
    tc = np.asarray(pvyear10.strings()["t_cell"])
    month = r["month"]
    lines = ["PV performance ratio at MV (after availability), model 15.1:",
             "  month  H_poa kWh/m2  yield kWh/kWp   PR    T_cell,w   PR at 25 C"]
    rows = []
    for k in range(12):
        m = month == k
        hp = poa[m].sum() / 1e3
        yf = r["pv_av"][m].sum() / P_STC                    # MWh/MWp = kWh/kWp
        pr = yf / hp
        tw = float((tc[m] * poa[m]).sum() / poa[m].sum())
        prc = pr / (1 + GAMMA * (tw - 25))
        rows.append((k + 1, f"{pr:.3f}", f"{prc:.3f}"))
        lines.append(f"  {k + 1:5d}   {hp:9.1f}      {yf:9.1f}      {pr:.3f}  {tw:6.1f}"
                     f"      {prc:.3f}")
    hp = poa.sum() / 1e3
    yf = r["pv_av"].sum() / P_STC
    tw = float((tc * poa).sum() / poa.sum())
    lines += [f"  year    {hp:9.1f}      {yf:9.1f}      {yf / hp:.3f}  {tw:6.1f}"
              f"      {yf / hp / (1 + GAMMA * (tw - 25)):.3f}",
              "  PR is lowest in the hot months; corrected to 25 C it is nearly",
              "  flat: a falling corrected PR is a fault or soiling, a falling",
              "  raw PR in July may only be the heat (chapters 50 and 52)"]
    emit("k_pr", lines)
    csv("ch15-pr.csv", "month,pr,pr25", rows)


def inverter() -> None:
    from companion.ch10.integrated import EFF_POINTS
    from plantp import pe
    c = pe.fit_loss_coeffs(EFF_POINTS)
    lines = ["inverter loss model fitted to five efficiency points (ch 10):",
             f"  c0 {c[0]:.5f}, c1 {c[1]:.5f}, c2 {c[2]:.5f} (per unit of rated AC)",
             "  DC in (pu)   AC out (pu)   efficiency"]
    for x in (0.004, 0.02, 0.10, 0.25, 0.50, 0.75, 1.00):
        y = float(ym.ac_from_dc([x], c)[0])
        lines.append(f"  {x:9.3f}    {y:9.4f}      {100 * y / x:6.2f} %")
    r = src.plant_year()
    lines += [f"  year: DC {r['pv_dc'].sum() / 1e3:.2f} GWh, AC {r['pv_inv'].sum() / 1e3:.2f} GWh,"
              f" loss {100 * (1 - r['pv_inv'].sum() / r['pv_dc'].sum()):.2f} %",
              "  efficiency falls at low load where the no-load loss dominates;",
              "  the yearly loss is weighted by the hours the inverter spends at",
              "  each load, which is why it is not the peak efficiency"]
    emit("k_inverter", lines)


def one_hour() -> None:
    """Every step of both chains for one hour each, to check by hand."""
    r = src.plant_year()
    h, v, wd, pa, ta, _ = src.hourly_inputs()
    k = 173 * 24 + 12                                      # 23 June, 12:00
    poa = pvyear10.poa()
    st = pvyear10.strings()
    w2 = float(np.asarray(pvyear10.pc.wind_at_height(v[k], 100, 2)))
    lines = ["one hour by hand, PV (23 June 12:00, model 15.1):",
             f"  POA {poa['poa'][k]:.0f} W/m2, after IAM {poa['eff'][k]:.0f} W/m2,"
             f" air {ta[k]:.1f} C, wind at 2 m {w2:.2f} m/s",
             f"  cell temperature (Faiman 25 + 6.84 v) {st['t_cell'][k]:.1f} C",
             f"  STC {r['pv_stc'][k]:.2f} | DC gross {r['pv_dc_gross'][k]:.2f} | DC"
             f" {r['pv_dc'][k]:.2f} | inverter {r['pv_inv'][k]:.2f} MW",
             f"  clipped {r['pv_clip'][k]:.2f} | soiling+shading {r['pv_soil'][k]:.2f} |"
             f" long-term {r['pv_lt'][k]:.2f} MW",
             f"  degradation {r['pv_deg'][k]:.2f} | availability {r['pv_av'][k]:.2f} MW"]
    cand = np.flatnonzero((v > 8.9) & (v < 9.1) & (wd > 255) & (wd < 285))
    j = int(cand[0])
    rho = float(s13.hub_density(pa[j], ta[j]))
    veq = float(w.density_equivalent_speed(v[j], rho))
    lines += [f"one hour by hand, wind (hour {j}, day {j // 24 + 1}, {j % 24:02d}:00):",
              f"  hub speed {v[j]:.2f} m/s from {wd[j]:.0f} deg; ground {pa[j]:.1f} hPa,"
              f" {ta[j]:.1f} C",
              f"  hub density {rho:.4f} kg/m3; density-equivalent speed {veq:.2f} m/s",
              f"  pack curve: {float(l11.pack_power(v[j])):.0f} kW at {v[j]:.2f},"
              f" {float(l11.pack_power(veq)):.0f} kW at {veq:.2f},"
              f" {float(l11.pack_power(0.5 * round(veq / 0.5))):.0f} kW at the"
              f" {0.5 * round(veq / 0.5):.1f} m/s bin",
              f"  gross (1.225) {r['w_gross'][j]:.2f} | density {r['w_dens'][j]:.2f} | terrain"
              f" {r['w_terr'][j]:.2f} MW",
              f"  wakes {r['w_wake'][j]:.2f} | long-term {r['w_lt'][j]:.2f} | availability"
              f" {r['w_av'][j]:.2f} MW"]
    emit("k_onehour", lines)


def lifetime() -> None:
    """Twenty-five years: PV degradation 0.5 % a year (A-275), none for
    the wind (A-274, teaching); plant end as in the model."""
    from companion.ch15 import examples_m as em
    r = src.plant_year()
    cfg = src.ModelConfig()
    out = r["outage"]
    lines = ["net energy at the POC over the life (S0, model 15.1):",
             "  year   PV at MV GWh   net GWh"]
    nets = []
    for y in range(1, 26):
        f = (1 - 0.005 * y) / (1 - 0.005)
        pv = r["pv_av"] * f
        net = em.tail(r["w_av"], pv, cfg, out)[1].sum() / 1e3
        nets.append(net)
        if y in (1, 5, 10, 15, 20, 25):
            lines.append(f"  {y:4d}     {pv.sum() / 1e3:8.2f}     {net:8.2f}")
    m = float(np.mean(nets))
    lines += [f"  mean of 25 years {m:.2f} GWh; year 1 is {100 * (nets[0] / m - 1):+.1f} % above it",
              "  a statement names its year; the finance model takes the series"]
    emit("k_lifetime", lines)


def night_import() -> None:
    r = src.plant_year()
    net = r["net"]
    imp = np.clip(-net, 0, None)
    lines = ["energy taken from the grid when the plant's own use and no-load",
             "  losses exceed its output (model 15.1, at the POC):",
             f"  hours with import          {int((net < 0).sum()):5d}",
             f"  energy imported            {imp.sum():7,.0f} MWh",
             f"  energy exported            {np.clip(net, 0, None).sum() / 1e3:7.2f} GWh",
             f"  net (export - import)      {net.sum() / 1e3:7.2f} GWh",
             "  import and export are metered apart and may be priced apart:",
             "  the yield statement shows both, not only the net (chapter 26)"]
    emit("k_import", lines)


def overbuild() -> None:
    """Scale the PV block (same hourly shape) at the 100 MW limit."""
    r = src.plant_year()
    base_pv = r["pv_av"]
    wind_ = r["w_av"]
    cfg = src.ModelConfig()
    lines = ["PV block size at the 100 MW export limit (same hourly shape,",
             "  before grid outages):",
             "  PV MW AC   delivered GWh   curtailed GWh   curtailed %   marginal"]
    rows = []
    prev = None
    for f in (1.0, 1.2, 1.4, 1.6, 1.8, 2.0):
        poc, _ = ym.plant_end(wind_, f * base_pv, cfg, np.zeros(8760, bool))
        dl = np.minimum(poc, 100.0).sum() / 1e3
        cu = np.clip(poc - 100.0, 0, None).sum() / 1e3
        marg = "" if prev is None else f"{100 * (dl - prev) / (0.2 * base_pv.sum() / 1e3):5.0f} %"
        prev = dl
        rows.append((int(round(50 * f)), f"{100 * cu / (dl + cu):.2f}"))
        lines.append(f"  {50 * f:6.0f}     {dl:10.2f}      {cu:10.2f}      {100 * cu / (dl + cu):6.2f}"
                     f"      {marg}")
    lines += ["  marginal: share of each added block's energy that reaches the",
              "  grid; the shared connection is the hybrid's saving, and its",
              "  curtailment is the price; a battery, a contract for curtailed",
              "  energy or a larger limit changes the balance (chapters 17-19)"]
    emit("k_overbuild", lines)
    csv("ch15-overbuild.csv", "pv,curt", rows)


def average_year() -> None:
    """Hourly series scaled to each of the 20 years (wind and PV apart)."""
    r = src.plant_year()
    years, wy, py = eh.iav_years()
    cfg = src.ModelConfig()
    w0, p0 = r["w_av"], r["pv_av"]
    curt = []
    for a, b in zip(wy / wy.mean(), py / py.mean()):
        poc, _ = ym.plant_end(a * w0, b * p0, cfg, np.zeros(8760, bool))
        curt.append(float(np.clip(poc - 100.0, 0, None).sum()))
    curt = np.array(curt)
    lines = ["curtailment of the average year against the average curtailment",
             "  (hourly shape of the data year, scaled to each of 20 years):",
             f"  average year (scale 1, 1)          {r['curtailed'].sum():6,.0f} MWh",
             f"  mean over the 20 years             {curt.mean():6,.0f} MWh",
             f"  range                              {curt.min():6,.0f} to {curt.max():,.0f} MWh",
             f"  windiest year {int(years[np.argmax(wy)])}: {curt[np.argmax(wy)]:,.0f} MWh",
             "  a loss that grows faster than the resource (a limit, clipping)",
             "  is larger on average than in the average year: run the model",
             "  on many years or correct the loss, do not scale one number"]
    emit("k_avgyear", lines)


def first_year() -> None:
    """A synthetic first operating year (A-271): the model's delivered
    energy with SCADA noise, one turbine 4 % below its power curve all
    year, one PV block (a tenth) out for 20 days from 3 March, and a
    soiling rate 1.5 times the model's from June."""
    r = src.plant_year()
    rng = np.random.default_rng(190)
    month = r["month"]
    day = np.arange(8760) // 24
    t_share = np.full(12, 1 / 12)
    turb = np.outer(r["w_av"], t_share)                     # MW per turbine
    turb[:, 6] *= 0.96                                      # T07
    pv = r["pv_av"].copy()
    pv[(day >= 61) & (day < 81)] *= 0.9                     # one block of ten out
    soil_extra = np.where(day >= 151, 0.5 * src.ModelConfig().soiling, 0.0)
    pv *= 1 - soil_extra
    noise = 1 + 0.02 * rng.standard_normal(8760)
    w_act, p_act = turb.sum(axis=1) * noise, pv * noise
    lines = ["first operating year against the model (A-271), at MV:",
             "  month   wind act/model   PV act/model   plant act/model"]
    for k in range(12):
        m = month == k
        lines.append(f"  {k + 1:5d}       {w_act[m].sum() / r['w_av'][m].sum():6.3f}"
                     f"          {p_act[m].sum() / r['pv_av'][m].sum():6.3f}"
                     f"          {(w_act[m] + p_act[m]).sum() / (r['w_av'][m] + r['pv_av'][m]).sum():6.3f}")
    tot = (w_act.sum() + p_act.sum()) / (r["w_av"].sum() + r["pv_av"].sum())
    t_noise = turb * (1 + 0.02 * rng.standard_normal((8760, 12)))
    ratio = t_noise.sum(axis=0) / np.median(t_noise.sum(axis=0))
    worst = int(np.argmin(ratio))
    lines += [f"  year: plant {tot:.4f} ({100 * (tot - 1):+.2f} %)",
              f"  turbine energy against the fleet median: lowest T{worst + 1:02d} at {ratio[worst]:.3f},",
              f"    others {np.sort(ratio)[1]:.3f} to {ratio.max():.3f}",
              "  the plant total hides three faults in a half per cent shortfall;",
              "  split by technology, month and unit, each one shows: the March",
              "  dip (PV block), the drift from June (soiling), one turbine low"]
    emit("k_firstyear", lines)


if __name__ == "__main__":
    distribution()
    one_hour()
    lifetime()
    inverter()
    performance_ratio()
    night_import()
    overbuild()
    average_year()
    first_year()
