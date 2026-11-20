"""Chapter 15, sections B2, C2 and D2 - model choices and their size: PV
transposition, temperature and incidence-angle models; the turbulence of
the power curve, the wake decay constant and high-wind and icing stops;
hourly electrical losses against a factor and the cost of reactive power;
a grid operator's spring curtailment; and twenty years of wind, PV and
hybrid energy (inter-annual variability and the hedge of a hybrid).

Run from the project root:   python -m companion.ch15.examples_h
Writes companion/ch15/expected/h_*.txt and diagrams/data/ch15-*.csv.
Model 15.1; teaching values A-269.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

from companion.ch10 import pvyear10
from companion.ch11 import lab_d as l11
from companion.ch12 import sources as s12
from companion.ch13 import sources as s13
from companion.ch14 import examples_b as eb, lab_d as l14
from companion.ch15 import sources as src
from companion.ch15.common import csv, emit
from plantp import datapack, irradiance as ir, pvcell as pc, wind as w

GAMMA = -0.0035                       # PVM-550 power temperature coefficient, 1/K (teaching)


def pvwatts(g_eff, t_cell):
    """Simple DC model for comparing model choices (relative use only)."""
    return 60.06 * np.asarray(g_eff) / 1000 * (1 + GAMMA * (np.asarray(t_cell) - 25))


def pv_models() -> None:
    h = datapack.load_hourly()
    ghi, dni, dhi = (h[k].to_numpy(float) for k in ("ghi_wm2", "dni_wm2", "dhi_wm2"))
    ci, cz, n = pvyear10.geometry()
    g0n = 1361.0 * (1 + 0.033 * np.cos(2 * np.pi * n / 365))
    b, sky, gr = pc.poa_hay_davies(ghi, dni, dhi, ci, cz, g0n, 25.0, 0.2)
    hd = b + sky + gr
    iso = np.asarray(ir.poa_isotropic(ghi, dni, dhi, ci, 25.0, 0.2))
    eff = b * pc.iam_ashrae(ci) + (sky + gr) * 0.95
    t_air = h["t_air_c"].to_numpy(float)
    wind2 = pc.wind_at_height(h["ws_100m_ms"].to_numpy(float), 100, 2)
    tc_f = pc.faiman(t_air, hd, wind2)
    tc_n = t_air + hd * (45 - 20) / 800                      # NOCT 45 C, teaching
    base = pvwatts(eff, tc_f).sum()
    lines = ["PV model choices, one change at a time (relative to the model's",
             "  Hay-Davies + IAM + Faiman chain; simple DC model):",
             f"  plane irradiation: Hay-Davies {hd.sum() / 1e3:,.0f}, isotropic {iso.sum() / 1e3:,.0f}"
             f" kWh/m2 ({100 * (iso.sum() / hd.sum() - 1):+.1f} %)",
             f"  DC energy with isotropic sky        {100 * (pvwatts(iso * eff / np.maximum(hd, 1e-9), tc_f).sum() / base - 1):+5.1f} %",
             f"  DC energy without IAM                {100 * (pvwatts(hd, tc_f).sum() / base - 1):+5.1f} %",
             f"  DC energy, NOCT temperature model    {100 * (pvwatts(eff, tc_n).sum() / base - 1):+5.1f} %",
             "  each choice moves the energy by a few per cent: the model",
             "  report names every one, and the reviewer checks them against",
             "  measured data of similar plants (chapter 16)"]
    emit("h_pvmodels", lines)


def wind_models() -> None:
    v, wd, rho = l11.hourly()
    veq = w.density_equivalent_speed(v, s13.hub_density(*[datapack.load_hourly()[k].to_numpy(float)
                                                          for k in ("p_hpa", "t_air_c")]))
    pc_ = datapack.load_power_curve()
    cv, cp = pc_.wind_speed_ms.to_numpy(float), pc_.power_kw.to_numpy(float)
    base = np.interp(veq, cv, cp).sum()
    lines = ["wind model choices (one turbine, hub density, data year):",
             "  power curve smoothed for turbulence:"]
    for ti in (0.08, 0.12, 0.16):
        sm = w.smooth_power_curve(cv, cp, ti)
        lines.append(f"    TI {ti:.2f}: {100 * (np.interp(veq, cv, sm).sum() / base - 1):+5.2f} %")
    hi = veq > 25.0
    restart = np.zeros(8760, bool)
    stopped = False
    for k in range(8760):
        if veq[k] > 25.0:
            stopped = True
        elif veq[k] < 22.0:
            stopped = False
        restart[k] = stopped
    lost_h = float(np.interp(veq[restart & ~hi], cv, cp).sum())
    t = s13.mast_year()
    iced_h = t["iced"].reshape(-1, 6).any(axis=1)
    lost_ice = float(np.interp(veq[iced_h], cv, cp).sum())
    lines += [(f"  hours above cut-out {int(hi.sum())}; hysteresis (restart below 22 m/s)"
               f" loses {lost_h / 1e3:.1f} MWh") if hi.any() else
              "  no hour above the 25 m/s cut-out in this year: stop and restart",
              "    logic (hysteresis) matters in stormier years and sites",
              f"  six icing events stop the turbine {int(iced_h.sum())} h: {lost_ice / 1e3:.1f} MWh"
              f" ({100 * lost_ice / base:.2f} %)",
              "  the measured power curve already holds the site's turbulence;",
              "  a curve for different turbulence changes the energy by about",
              "  a per cent; icing stops are small here but",
              "  belong in the loss register with their own evidence"]
    emit("h_windmodels", lines)


def wake_k() -> None:
    xy = l14.layouts()["W2b plain, adjusted"]
    lines = ["the wake decay constant of the Jensen model (W2b, flat ground):",
             "  k        wake loss"]
    keep = w.farm_speeds.__defaults__
    for k in (0.04, 0.05, 0.075):
        w.farm_speeds.__defaults__ = (k,)
        f, e = eb.farm_energy(xy)
        lines.append(f"  {k:.3f}    {100 * (1 - e / f):5.2f} %")
    w.farm_speeds.__defaults__ = keep
    lines += ["  a lower k (stable, low-turbulence nights) deepens the wakes; the",
              "  value comes from validation against operating farms of similar",
              "  climate; the model states it with its uncertainty (chapter 16)"]
    emit("h_wakek", lines)


def electrical() -> None:
    r = src.plant_year()
    mv = r["mv"]
    lines = ["electrical losses, the model's P^2 form against a constant factor:"]
    loss_model = r["el_loss"].sum()
    factor = loss_model / mv.sum()
    lines += [f"  model (no-load + load ~ P^2): {loss_model:,.0f} MWh ({100 * factor:.2f} % of MV energy)",
              "  load loss as a share of the output: 1.50 % at full output,",
              f"    {1.5 / 3:.2f} % at a third of it ({1.5 / 9:.2f} % of 100 MW); the no-load",
              "    0.10 MW weighs most in quiet hours; a constant factor gets",
              "    both shapes wrong hour by hour"]
    for pf in (1.00, 0.95, 0.90):
        ll = r["el_loss"] - 0.10
        extra = (ll / pf ** 2).sum() + 0.10 * 8760 - loss_model
        lines.append(f"  power factor {pf:.2f} at the POC: load losses x 1/pf^2: {extra:+6,.0f} MWh")
    lines += ["  reactive power asked by the grid (chapter 28) raises currents and",
              "  losses: the requirement enters the model as an operating mode"]
    emit("h_electrical", lines)


def grid_curtailment() -> None:
    """Teaching rule (A-269): on 20 % of the days from March to May the
    grid limits the plant to 70 MW from 10:00 to 15:00."""
    r = src.plant_year()
    rng = np.random.default_rng(170)
    month = r["month"]
    hour = np.arange(8760) % 24
    day = np.arange(8760) // 24
    days = np.unique(day[(month >= 2) & (month <= 4)])
    chosen = set(rng.choice(days, int(0.2 * len(days)), replace=False))
    m = np.array([d in chosen for d in day]) & (hour >= 10) & (hour < 15)
    lost = np.clip(r["delivered"][m] - 70.0, 0, None).sum()
    lines = ["a grid operator's spring limit (teaching rule, A-269):",
             f"  {len(chosen)} days x 5 midday hours at 70 MW: {lost:,.0f} MWh lost"
             f" ({100 * lost / r['net'].sum():.2f} % of the year)",
             "  ordered curtailment is not a plant loss but a grid one: it is",
             "  recorded separately (it may be compensated, chapter 28), it",
             "  falls on the sunniest hours, and a battery can take part of it"]
    emit("h_gridcurt", lines)


@lru_cache(maxsize=1)
def iav_years():
    """Twenty years: wind from the chapter 13 reference series through the
    MCP line and the farm curve of the model; PV scaled month by month by
    the chapter 12 provider's 20-year GHI against the station year.
    Returns (years, wind GWh, PV GWh), both at MV after availability."""
    ref = s13.reference()
    r = src.plant_year()
    from companion.ch15 import forecast as fc
    a, b = 0.012, 1.0862                                 # D-017 variance-ratio line
    wind_y = []
    for y in range(len(ref["years"])):
        vy = a + b * ref["long"][y]
        wind_y.append(float(fc.farm_curve(np.clip(vy, 0, None)).sum()) / 1e3)
    wind_y = np.array(wind_y)
    wind_y *= r["w_av"].sum() / 1e3 / wind_y.mean()      # scale to the model's long term
    sums = np.asarray(s12.long_term()["monthly"])
    pv_m = np.array([r["pv_av"][r["month"] == k].sum() for k in range(12)]) / 1e3
    ratio = sums / sums.mean(axis=0)[None, :]
    pv_y = (ratio * pv_m[None, :]).sum(axis=1)
    return np.asarray(ref["years"]), wind_y, pv_y


def iav() -> None:
    ref = {"years": iav_years()[0]}
    _, wind_y, pv_y = iav_years()
    hyb = wind_y + pv_y
    corr = float(np.corrcoef(wind_y, pv_y)[0, 1])
    cv = lambda x: 100 * x.std(ddof=1) / x.mean()
    lines = ["twenty years of energy at MV (wind 2004-2023 reference, PV 20-year GHI):",
             f"  wind  mean {wind_y.mean():6.1f} GWh, year-to-year sd {cv(wind_y):4.1f} %",
             f"  PV    mean {pv_y.mean():6.1f} GWh, year-to-year sd {cv(pv_y):4.1f} %",
             f"  hybrid mean {hyb.mean():6.1f} GWh, year-to-year sd {cv(hyb):4.1f} %",
             f"  correlation of annual wind and PV {corr:+.2f}",
             f"  worst year: wind {wind_y.min():.1f}, PV {pv_y.min():.1f}, hybrid {hyb.min():.1f} GWh",
             "  the hybrid's variation is less than the wind's: two resources",
             "  that do not vary together hedge each other year by year, which",
             "  lowers the one-year P90 (chapter 16) and the debt risk"]
    emit("h_iav", lines)
    csv("ch15-iavrel.csv", "year,wind,pv,hybrid",
        [(int(yy), f"{100 * a_ / wind_y.mean():.1f}", f"{100 * b_ / pv_y.mean():.1f}",
          f"{100 * c_ / hyb.mean():.1f}") for yy, a_, b_, c_ in zip(ref["years"], wind_y, pv_y, hyb)])
    csv("ch15-iav.csv", "year,wind,pv,hybrid",
        [(int(yy), f"{a_:.1f}", f"{b_:.1f}", f"{c_:.1f}") for yy, a_, b_, c_ in
         zip(ref["years"], wind_y, pv_y, hyb)])


if __name__ == "__main__":
    pv_models()
    wind_models()
    wake_k()
    electrical()
    grid_curtailment()
    iav()
