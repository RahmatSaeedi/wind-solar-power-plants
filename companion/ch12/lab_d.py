"""Chapter 12, section D - resource-to-design lab: two irradiance sources
into a preliminary PV energy estimate (the chapter's worked example), and
cleaning a station year with five injected faults, fault by fault.

Run from the project root:   python -m companion.ch12.lab_d
Writes companion/ch12/expected/d_*.txt and diagrams/data/ch12-*.csv.
Data pack 1.1.0 (S0); synthetic provider A-240; injected faults A-246.
"""
from __future__ import annotations

import numpy as np

from companion.ch10 import pvyear10
from companion.ch10.integrated import EFF_POINTS
from companion.ch12 import sources
from companion.ch12.common import emit
from plantp import datapack, irradiance as ir, pe, pvcell as pc

P_STC = 60.06e6
GAMMA = -0.0035


# [start: pvquick]
def pv_energy_mwh(ghi, dni, dhi) -> float:
    """Preliminary AC energy of the Plant P array (MWh): Hay-Davies plane of
    array, IAM, Faiman cell temperature, linear power rule, 3 % DC losses,
    the chapter 10 inverter curve and clipping, soiling 1.43 %."""
    ci, cz, n = pvyear10.geometry(25.0, 180.0)
    g0 = ir.g0n(n)
    beam, sky, ground = pc.poa_hay_davies(ghi, dni, dhi, ci, cz, g0, 25.0)
    poa = beam + sky + ground
    eff = beam * pc.iam_ashrae(ci) + (sky + ground) * 0.95
    h = datapack.load_hourly()
    wind2 = pc.wind_at_height(h["ws_100m_ms"].to_numpy(float), 100, 2)
    tc = pc.faiman(h["t_air_c"].to_numpy(float), poa, wind2)
    p_dc = P_STC * eff / 1000 * (1 + GAMMA * (tc - 25)) * (1 - 0.03)
    c0, c1, c2 = pe.fit_loss_coeffs(EFF_POINTS)
    x = p_dc / 50e6                   # inverter input in per unit; invert
    root = np.sqrt((1 + c1) ** 2 - 4 * c2 * (c0 - x))   # the loss model
    y = np.where(x > c0, (-(1 + c1) + root) / (2 * c2), 0.0)
    ac = np.minimum(y * 50e6, 50e6 * 0.98)
    return float(ac.sum() / 1e6 * (1 - 0.0143) * (1 - 0.0007))
# [end: pvquick]


def two_sources() -> None:
    p = sources.pack()
    pr = sources.provider()
    lt = sources.long_term()
    e_g = pv_energy_mwh(p["ghi"], p["dni"], p["dhi"])
    e_p = pv_energy_mwh(pr["ghi"], pr["dni"], pr["dhi"])
    dni_g, dhi_g = ir.decompose(p["ghi"], p["cz"], p["g0n"], model="orgill")
    e_go = pv_energy_mwh(p["ghi"], dni_g, dhi_g)
    lt_fac = lt["annual"].mean() / lt["annual"][-1]
    e_lt = pv_energy_mwh(p["ghi"] * lt_fac, p["dni"] * lt_fac, p["dhi"] * lt_fac)
    e_99 = pv_energy_mwh(p["ghi"] * 0.99, p["dni"] * 0.99, p["dhi"] * 0.99)
    lines = ["worked example: two irradiance sources, one preliminary PV estimate",
             "  source                              GHI kWh/m2   AC energy MWh",
             f"  A ground station 2023                  {p['ghi'].sum() / 1e3:7.1f}"
             f"      {e_g:9,.0f}",
             f"  B provider 2023 (its own split)        {pr['ghi'].sum() / 1e3:7.1f}"
             f"      {e_p:9,.0f}   ({100 * (e_p / e_g - 1):+.1f} %)",
             f"  A with Orgill-Hollands split           {p['ghi'].sum() / 1e3:7.1f}"
             f"      {e_go:9,.0f}   ({100 * (e_go / e_g - 1):+.1f} %)",
             f"  A scaled to the long term (x {lt_fac:.4f})"
             f"   {p['ghi'].sum() / 1e3 * lt_fac:7.1f}"
             f"      {e_lt:9,.0f}   ({100 * (e_lt / e_g - 1):+.1f} %)",
             f"  sensitivity: 1 % less irradiance -> {100 * (1 - e_99 / e_g):.2f} %"
             " less energy",
             "    (clipping and cell temperature absorb part of it)",
             "  the chapter 10 chain (single-diode model) gave 111,339 MWh for A",
             "  the year matters more than the source here: the 2023 ground",
             "  year is a sunny year, so the long-term step moves the answer",
             "  more than the choice between two good sources"]
    emit("d_compare", lines)


def faulty_year(seed: int = 131):
    """The pack's GHI as a station would have logged it with five faults
    (A-246): weekly-cleaned dome soiling (sawtooth to -2 %), a one-hour
    clock error from 1 March to 30 April, a ten-day gap in August, two
    stuck days in October, 20 spikes."""
    p = sources.pack()
    rng = np.random.default_rng(seed)
    g = p["ghi"].copy()
    day = np.arange(8760) // 24
    faults = np.zeros(8760, int)
    soil = 0.02 * ((day % 7) / 7)                       # cleaned every 7 days
    g *= 1 - soil
    clock = (day >= 59) & (day < 120)
    g[clock] = np.roll(p["ghi"], 1)[clock] * (1 - soil[clock])
    faults[clock] |= 1
    gap = (day >= 220) & (day < 230)
    g[gap] = np.nan
    faults[gap] |= 2
    stuck = (day >= 280) & (day < 282)
    g[stuck] = g[np.flatnonzero(stuck)[0]]
    faults[stuck] |= 4
    spikes = rng.choice(np.flatnonzero(p["cz"] > 0.3), 20, replace=False)
    g[spikes] = 1450.0
    faults[spikes] |= 8
    return g, faults, soil


def clean_year() -> None:
    p = sources.pack()
    pr = sources.provider()
    g, faults, soil = faulty_year()
    true_sum = p["ghi"].sum() / 1e3
    raw_sum = np.nansum(g) / 1e3
    steps = []
    x = g.copy()
    cs = ir.clear_sky_haurwitz(p["cz"])
    # 1 spikes: a limit that does not use the sun's position (the clock
    #   may be wrong): 1.25 x the highest clear-sky value of the year
    spike = np.nan_to_num(x) > 1.25 * cs.max()
    x[spike] = np.nan
    steps.append(("spikes (above 1.25 x clear-sky maximum)", spike.sum(),
                  np.nansum(x) / 1e3))
    # 2 stuck values: identical for 6+ daylight hours (gaps excluded)
    same = np.r_[False, np.diff(x) == 0] & (p["cz"] > 0.1)
    run = np.convolve(same.astype(int), np.ones(6, int), mode="same") >= 6
    x[run] = np.nan
    steps.append(("stuck values flagged and removed", run.sum(), np.nansum(x) / 1e3))
    # 3 clock: lag by month against clear sky; shift months found late
    shifted = 0
    for m in range(12):
        sel = np.flatnonzero(p["month"] == m)
        lag = ir.best_lag(np.nan_to_num(x[sel]), cs[sel], 2)
        if lag != 0:
            x[sel] = np.roll(x[sel], -lag)
            shifted += len(sel)
    steps.append(("months found late, shifted back", shifted, np.nansum(x) / 1e3))
    # 4 limits that use the sun's position, now that the clock is right
    lim = ir.qc_limits(p["cz"], p["g0n"])
    rare = np.nan_to_num(x) > lim["ghi_rare"]
    x[rare] = np.nan
    steps.append(("extremely rare values after the clock fix", rare.sum(),
                  np.nansum(x) / 1e3))
    # 5 gaps: short in clearness index, long from the provider (scaled)
    kt = ir.clearness_index(x, p["cz"], p["g0n"])
    kt_f = ir.fill_short_gaps(kt, 3)
    x = np.where(np.isnan(x) & ~np.isnan(kt_f), kt_f * p["g0n"] * p["cz"], x)
    ok = ~np.isnan(x) & (p["cz"] > 0.087)
    scale = np.nansum(x[ok]) / pr["ghi"][ok].sum()
    long_gap = np.isnan(x)
    x = np.where(long_gap, pr["ghi"] * scale, x)
    steps.append(("gaps filled (short: k_t; long: provider)", long_gap.sum(),
                  np.nansum(x) / 1e3))
    # 6 soiling: the weekly sawtooth, corrected from the cleaning log
    x = x / (1 - soil)
    steps.append(("dome soiling corrected from the cleaning log", 8760,
                  np.nansum(x) / 1e3))
    lines = ["cleaning a station year with five faults (A-246):",
             f"  true GHI {true_sum:,.1f} kWh/m2; as logged {raw_sum:,.1f}"
             f" ({100 * (raw_sum / true_sum - 1):+.1f} %, gaps simply skipped)",
             "  step                                          hours   GHI kWh/m2"
             "  error"]
    for name, n, s in steps:
        lines.append(f"  {name:45s} {n:5d}   {s:8.1f}  {100 * (s / true_sum - 1):+5.1f} %")
    hr = ~np.isnan(x) & (p["cz"] > 0.087)
    lines += [f"  hourly RMSE after cleaning {ir.rmse(x[hr], p['ghi'][hr]):.1f} W/m2;"
              " each step is logged with its flag",
              "  the order matters: spikes and stuck values first with tests",
              "  that ignore the sun's position (they would fool the clock",
              "  test), then the clock, then every test and fill that uses the",
              "  sun's position, the soiling last"]
    emit("d_clean", lines)


if __name__ == "__main__":
    two_sources()
    clean_year()
