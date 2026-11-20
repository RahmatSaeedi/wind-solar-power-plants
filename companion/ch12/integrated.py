"""Chapter 12 - three integrated Plant P examples: one station day from
raw values to a checked plane-of-array day (introductory), the long-term
annual resource with its uncertainty (intermediate), and the measurement
and data-quality plan with the cleaning-decision inputs (integrated).

Run from the project root:   python -m companion.ch12.integrated
Writes companion/ch12/expected/i_*.txt.
Data pack 1.1.0 (S0); A-240 .. A-249; D-016.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch10 import pvyear10
from companion.ch12 import sources
from companion.ch12.common import emit
from plantp import irradiance as ir, pvcell as pc


def one_day() -> None:
    p = sources.pack()
    pr = sources.provider()
    day = 173                                           # 23 June (index)
    sl = slice(day * 24, day * 24 + 24)
    ghi, dni, dhi, cz = p["ghi"][sl], p["dni"][sl], p["dhi"][sl], p["cz"][sl]
    g0 = p["g0n"][sl]
    flags = ir.qc_flags(ghi, dni, dhi, cz, g0)
    kt = ir.clearness_index(ghi, cz, g0)
    cs = ir.clear_sky_haurwitz(cz)
    ci, czt, _ = pvyear10.geometry(25.0, 180.0)
    b, s, g = pc.poa_hay_davies(ghi, dni, dhi, ci[sl], czt[sl], g0, 25.0)
    lines = ["one station day, 23 June 2023 (S0), hourly means:",
             "  hour  GHI  DNI  DHI   k_t   GHI/clear  flags  POA W/m2"]
    for h in range(5, 20):
        lines.append(f"  {h:02d}   {ghi[h]:4.0f} {dni[h]:4.0f} {dhi[h]:4.0f}"
                     f"  {kt[h] if not math.isnan(kt[h]) else 0:5.3f}"
                     f"   {ghi[h] / cs[h] if cs[h] > 20 else 0:5.3f}     {flags[h]:3d}"
                     f"   {b[h] + s[h] + g[h]:5.0f}")
    lines += [f"  day: GHI {ghi.sum() / 1e3:.2f}, POA {(b + s + g).sum() / 1e3:.2f},"
              f" provider GHI {pr['ghi'][sl].sum() / 1e3:.2f} kWh/m2",
              "  no flags; k_t near 0.75 all day and GHI/clear near 1: a clear",
              "  day, good for checking the clock and the sensor's level"]
    emit("i_day", lines)


def annual() -> None:
    p = sources.pack()
    lt = sources.long_term()
    fac = lt["annual"].mean() / lt["annual"][-1]
    poa_y = pvyear10.poa()["poa"].sum() / 1e3
    iav = float(np.std(lt["annual"], ddof=1) / np.mean(lt["annual"]))
    u_ghi = ir.combine_uncertainty(0.020, 0.010, 0.015, iav / math.sqrt(20))
    u_poa = ir.combine_uncertainty(u_ghi, 0.015, 0.010)   # transposition, split
    ghi50, poa50 = p["ghi"].sum() / 1e3 * fac, poa_y * fac
    lines = ["long-term annual resource of Plant P (D-016):",
             f"  ground 2023 GHI {p['ghi'].sum() / 1e3:,.1f}; long-term factor"
             f" {fac:.4f} (provider 20 years)",
             f"  GHI  P50 {ghi50:,.0f} kWh/m2, u {100 * u_ghi:.1f} %:"
             f" P90 {ir.p_value(ghi50, u_ghi):,.0f}",
             f"  POA  P50 {poa50:,.0f} kWh/m2 (25 deg), u {100 * u_poa:.1f} %",
             "       (adds transposition 1.5 % and the beam/diffuse split 1.0 %)",
             f"       P90 long-term {ir.p_value(poa50, u_poa):,.0f};"
             f" P90 one year {ir.p_value(poa50, ir.combine_uncertainty(u_poa, iav)):,.0f}",
             f"  year-to-year spread {100 * iav:.1f} %; the PV model and losses",
             "  (chapter 15) and their uncertainty (chapter 16) come on top",
             "  the energy of chapters 5 and 10 used the 2023 year as it is:",
             f"  {100 * (fac - 1):+.1f} % for the long term"]
    emit("i_annual", lines)


def plan() -> None:
    lines = ["measurement and data-quality plan of the Plant P station"
             " (PLP-GEN-PRO-0001):",
             "  instruments: GHI and DHI (shadow ball) thermopile pyranometers,",
             "    DNI pyrheliometer on a sun tracker, two POA reference cells",
             "    (a redundant pair), rear-side cell, soiling pair,",
             "    air temperature, humidity, pressure, rain, wind at 2 and 10 m",
             "  sampling 1 s, stored one-minute mean/min/max; clock synchronised",
             "    daily and logged; all times in local standard time +04:00",
             "  quality control: missing, limits (physically possible, extremely",
             "    rare), closure, night offset, stuck, clock (clear days), weekly",
             "    ratio to the provider series; every flag kept with the value",
             "  maintenance: dome cleaning daily in the dry season (log with",
             "    time), levelling and desiccant monthly, tracker alignment",
             "    weekly; recalibration by an accredited laboratory or by",
             "    comparison on site at the interval the plan sets",
             "  acceptance of a month: recovery after QC at least the plan's",
             "    target (teaching: 95 %), closure within 8 % on 95 % of hours,",
             "    ratio to provider stable within 2 % of its annual mean",
             "  outputs: monthly QC report, filled hourly series with flags,",
             "    soiling-loss series and rain events for the cleaning decision"]
    emit("i_plan", lines)


if __name__ == "__main__":
    one_day()
    annual()
    plan()
