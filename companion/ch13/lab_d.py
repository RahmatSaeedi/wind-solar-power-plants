"""Chapter 13, section D - analysis lab: diagnose the inconsistent 80 m
cup from the ratios to the 60 m and 100 m cups (the chapter's worked
example), its effect on shear, hub-height speed and energy, the quality
flags and recovery of the year, and the uncertainty budget.

Run from the project root:   python -m companion.ch13.lab_d
Writes companion/ch13/expected/d_*.txt and diagrams/data/ch13-*.csv.
Synthetic mast year A-250, faults A-251; budget A-254.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch13 import sources
from companion.ch13.common import csv, emit
from plantp import datapack, windres as wr

MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def curve():
    pc = datapack.load_power_curve()
    return pc.wind_speed_ms.to_numpy(float), pc.power_kw.to_numpy(float)


def diagnose() -> None:
    m = sources.mast_year()
    lg = m["logged"]
    ok = ~np.isnan(lg["v100"]) & (lg["v100"] > 4) & ~m["iced"]
    r80 = lg["v80"] / lg["v100"]
    r60 = lg["v60"] / lg["v100"]
    month = m["true"]["day"] * 12 // 365
    lines = ["the 80 m cup against its neighbours (logged year, A-251):",
             "  by month         80/100   60/100"]
    rows = []
    for k in range(12):
        sel = ok & (month == k)
        a, b = float(np.mean(r80[sel])), float(np.mean(r60[sel]))
        rows.append((k + 1, f"{a:.4f}", f"{b:.4f}"))
        lines.append(f"  {MONTHS[k]}              {a:.4f}   {b:.4f}")
    csv("ch13-ratio-month.csv", "month,r80,r60", rows)
    sec = wr.sector_ratio(lg["v80"], lg["v100"], lg["wd100"])
    sec60 = wr.sector_ratio(lg["v60"], lg["v100"], lg["wd100"])
    csv("ch13-ratio-sector.csv", "dir,r80,r60",
        [(f"{a:.0f}", f"{b:.4f}", f"{c[1]:.4f}") for (a, b, _), c in zip(sec, sec60)])
    low = ok & (lg["v100"] < 5.5) & m["wear"]
    high = ok & (lg["v100"] > 8) & m["wear"]
    lines += ["  by direction: the 80/100 ratio dips in the sectors 300-330 and",
              f"    330-360 ({sec[10][1]:.3f}, {sec[11][1]:.3f}) against"
              f" {np.nanmedian([s[1] for s in sec]):.3f} elsewhere; 60/100 is flat",
              f"  from July, low winds read lower still: 80/100 = {np.mean(r80[low]):.3f}"
              f" below 5.5 m/s, {np.mean(r80[high]):.3f} above 8 m/s",
              "  diagnosis: (1) mast shadow on the 80 m boom for winds from",
              "  300-340 deg (boom on the wrong side for the prevailing wind);",
              "  (2) bearing wear from July: a growing loss and a higher",
              "  starting threshold. The 60 m cup and the vane agree with 100 m"]
    emit("d_diagnose", lines)


def effect() -> None:
    m = sources.mast_year()
    t, lg = m["true"], m["logged"]
    ok = ~np.isnan(lg["v100"]) & ~m["iced"]
    z = [60.0, 80.0, 100.0]
    a_true = wr.fit_shear(z, [t["v60"][ok].mean(), t["v80"][ok].mean(), t["v100"][ok].mean()])
    a_bad = wr.fit_shear(z, [lg["v60"][ok].mean(), lg["v80"][ok].mean(),
                             lg["v100"][ok].mean()])
    a_two = wr.fit_shear([60.0, 100.0], [lg["v60"][ok].mean(), lg["v100"][ok].mean()])
    a_top = wr.fit_shear([80.0, 100.0], [lg["v80"][ok].mean(), lg["v100"][ok].mean()])
    a_top_t = wr.fit_shear([80.0, 100.0], [t["v80"][ok].mean(), t["v100"][ok].mean()])
    cv, cp = curve()
    v120_true = t["v100"] * (120 / 100) ** a_true
    lines = ["effect of the faulty 80 m cup on the shear and a 120 m hub:",
             "  shear exponent from                      true     logged",
             f"    three heights 60/80/100 m              {a_true:.4f}   {a_bad:.4f}",
             f"    the two upper heights 80/100 m         {a_top_t:.4f}   {a_top:.4f}",
             f"    60 and 100 m (80 m left out)           -        {a_two:.4f}"]
    e_true = np.interp(v120_true, cv, cp).sum() / 6 / 1e3
    lines.append(f"  energy at 120 m with the true shear: {e_true:,.0f} MWh per turbine")
    for name, a in (("logged, three heights", a_bad), ("logged, 80/100 m", a_top),
                    ("logged, 60/100 m", a_two)):
        v120 = t["v100"] * (120 / 100) ** a
        e = np.interp(v120, cv, cp).sum() / 6 / 1e3
        lines.append(f"    {name:22s} {e:8,.0f} MWh ({100 * (e / e_true - 1):+.2f} %)")
    sens = wr.energy_sensitivity(t["v100"], cv, cp)
    lines += [f"  sensitivity of energy to speed at this site: {sens:.2f} % per %",
              "  the low 80 m readings barely move a three-height fit, but the",
              "  common shortcut 'shear from the two top cups' raises the",
              "  exponent by two thirds and overstates a 120 m hub by about 4 %",
              "  of energy;",
              "  leaving the faulty cup out removes the bias; two heights left",
              "  make the shear less certain (section C)"]
    emit("d_effect", lines)


def flags() -> None:
    m = sources.mast_year()
    lg = m["logged"]
    miss = np.isnan(lg["v100"])
    ice = wr.icing_flags(lg["v100"], lg["sd100"], lg["t"]) & ~miss
    shadow80 = ((lg["wd100"] - 300) % 360 < 40) & ~miss
    month = m["true"]["day"] * 12 // 365
    wear80 = (month >= 6) & ~miss
    valid100 = ~miss & ~ice
    valid80 = ~miss & ~shadow80 & ~wear80
    valid60 = ~miss
    rows, lines = [], ["quality flags and data recovery of the mast year:",
                       "  month   100 m    80 m    60 m"]
    for k in range(12):
        sel = month == k
        a, b, c = (wr.recovery(v[sel]) for v in (valid100, valid80, valid60))
        rows.append((k + 1, f"{100 * a:.1f}", f"{100 * b:.1f}", f"{100 * c:.1f}"))
        lines.append(f"  {MONTHS[k]}     {100 * a:5.1f}   {100 * b:5.1f}   {100 * c:5.1f}")
    lines += [f"  year:   {100 * wr.recovery(valid100):5.1f}   {100 * wr.recovery(valid80):5.1f}"
              f"   {100 * wr.recovery(valid60):5.1f}  (%)",
              f"  flags: outage {miss.sum()} records, icing at 100 m {ice.sum()},"
              f" shadow at 80 m {shadow80.sum()}",
              f"  injected icing {m['iced'].sum()} records: found"
              f" {np.sum(ice & m['iced'])}, false alarms {np.sum(ice & ~m['iced'])}",
              "  80 m data after June are excluded for shear work: recovery",
              "  is a property of each sensor, not of the mast"]
    emit("d_flags", lines)
    csv("ch13-recovery.csv", "month,r100,r80,r60", rows)


def uncertainty() -> None:
    """Wind-speed and energy uncertainty (A-254, teaching one-sigma values)."""
    t = sources.mast_year()["true"]
    cv, cp = curve()
    sens = wr.energy_sensitivity(t["v100"], cv, cp)
    parts = {"anemometer calibration and class": 0.010,
             "mounting, flow distortion, tower shadow": 0.010,
             "long-term correction (MCP)": 0.020,
             "long-term period, 20 years at sd 3.5 %": 0.035 / math.sqrt(20),
             "vertical extrapolation (hub at 100 m: none)": 0.0}
    u_v = math.sqrt(sum(v ** 2 for v in parts.values()))
    lines = ["uncertainty of the long-term hub-height wind speed (A-254):"]
    for k, v in parts.items():
        lines.append(f"  {k:45s} {100 * v:4.1f} %")
    lines += [f"  combined wind speed                           {100 * u_v:4.1f} %",
              f"  energy: sensitivity {sens:.2f} x {100 * u_v:.1f} % ="
              f" {100 * sens * u_v:.1f} % (before power curve and losses)",
              f"  a hub at 150 m from the 100 m mast with a shear uncertainty of",
              f"    0.03 adds {100 * (1.5 ** 0.03 - 1):.1f} % of speed:"
              f" {100 * sens * (1.5 ** 0.03 - 1):.1f} % of energy",
              "  measuring at hub height (or a lidar to it) is cheaper than",
              "  the energy this uncertainty costs in financing (chapter 16)"]
    emit("d_uncertainty", lines)


if __name__ == "__main__":
    diagnose()
    effect()
    flags()
    uncertainty()
