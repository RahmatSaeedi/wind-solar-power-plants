"""Chapter 13, sections A3 and B2 - remote sensing and campaign design:
a four-beam lidar on flat ground and on a hilltop, a lidar that loses
more data at night (recovery is not representativeness), the power
budget of a solar-powered mast, the uncertainty of extrapolating to a
higher hub, and the value of measuring better (P90 and its money).

Run from the project root:   python -m companion.ch13.examples_f
Writes companion/ch13/expected/f_*.txt.
Teaching values A-257 (beam angle, loads, efficiencies, campaign options).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch13 import integrated, sources
from companion.ch13.common import emit
from plantp import datapack, irradiance as ir, windres as wr

HALF_ANGLE = 28.0                # beam angle from the vertical, teaching


def dbs() -> None:
    u = 7.5                                      # wind from the west
    z = 100.0
    lines = [f"four-beam lidar, beams {HALF_ANGLE:.0f} deg off vertical,"
             f" west wind 7.5 m/s at {z:.0f} m:",
             f"  scan circle diameter at {z:.0f} m:"
             f" {2 * z * math.tan(math.radians(HALF_ANGLE)):.0f} m",
             "  vertical wind  west beam  east beam   reconstructed   error"]
    for dw in (0.0, 0.1, 0.2, 0.3):
        wb = {"N": 0.0, "S": 0.0, "W": dw / 2, "E": -dw / 2}
        rad = wr.dbs_radials(u, 0.0, wb, HALF_ANGLE)
        ur, _, _ = wr.dbs_reconstruct(rad, HALF_ANGLE)
        lines.append(f"  difference {dw:.1f}   {wb['W']:+.2f}      {wb['E']:+.2f}"
                     f"        {ur:6.3f} m/s     {100 * (ur / u - 1):+.1f} %")
    lines += ["  on a hilltop the flow rises on the windward side and sinks on",
              "  the lee side: the beams see different vertical winds and the",
              "  homogeneous reconstruction reads the horizontal speed low;",
              "  flat sites keep the error small, complex sites need a flow",
              "  model correction or a mast (chapter 14)"]
    emit("f_dbs", lines)


def conditional() -> None:
    """Lidar loses 25 % of the night records (clean stable air) and 3 % by
    day (A-257); the 150 m speed from the true profile."""
    rng = np.random.default_rng(145)
    t = sources.mast_year()["true"]
    alpha = np.log(t["v100"] / t["v60"]) / np.log(100 / 60)
    v150 = t["v100"] * 1.5 ** alpha
    night = (t["hour"] >= 20) | (t["hour"] < 6)
    p_loss = np.where(night, 0.25, 0.03)
    kept = rng.random(len(v150)) > p_loss
    hours = np.array([np.mean(v150[kept & (t["hour"] == h)]) for h in range(24)])
    lines = ["a lidar that loses more data at night (A-257):",
             f"  recovery {100 * kept.mean():.1f} %; night"
             f" {100 * kept[night].mean():.1f} %, day {100 * kept[~night].mean():.1f} %",
             f"  true mean at 150 m             {v150.mean():.3f} m/s",
             f"  mean of the records kept       {v150[kept].mean():.3f} m/s"
             f" ({100 * (v150[kept].mean() / v150.mean() - 1):+.2f} %)",
             f"  mean of the 24 hourly means    {hours.mean():.3f} m/s"
             f" ({100 * (hours.mean() / v150.mean() - 1):+.2f} %)",
             "  the windy stable nights are lost more often: a high recovery",
             "  can still be biased; weighting by hour (or month and hour)",
             "  restores the balance, and the loss pattern is reported"]
    emit("f_conditional", lines)


def power_budget() -> None:
    """Solar-powered mast: logger 0.5 W, modem 1.5 W, sensors 0.5 W; two
    heated sensors 15 W each below 1 C; panel tilted 50 deg gains 1.6 x
    the horizontal winter irradiation; system efficiency 0.6; battery
    five days of the base load at 50 % depth, 12 V (A-257)."""
    h = datapack.load_hourly()
    jan = h.index.month == 1
    ghi_day = float(h["ghi_wm2"][jan].sum()) / 31 / 1000     # kWh/m2/day
    t = sources.mast_year()["true"]
    day = t["day"]
    jan10 = day < 31
    cold_h = float(np.sum(t["t"][jan10] < 1.0)) / 6 / 31     # hours/day
    base = (0.5 + 1.5 + 0.5) * 24                             # Wh/day
    heat = 2 * 15 * cold_h
    psh = 1.6 * ghi_day
    panel_base = base / (psh * 0.6)
    panel_all = (base + heat) / (psh * 0.6)
    batt = 5 * base / 0.5 / 12
    lines = ["power budget of a solar-powered mast in January (A-257):",
             f"  horizontal {ghi_day:.2f} kWh/m2 a day; tilted panel x 1.6"
             f" = {psh:.2f} sun-hours",
             f"  base load (logger, modem, sensors) {base:.0f} Wh a day",
             f"  heated cup and vane below 1 C: {cold_h:.1f} h a day ->"
             f" {heat:.0f} Wh a day",
             f"  panel for the base load      {panel_base:5.0f} W",
             f"  panel with heating           {panel_all:5.0f} W",
             f"  battery, 5 days of base load {batt:5.0f} Ah at 12 V",
             "  heating multiplies the winter energy several times: heated",
             "  sensors need a larger supply or grid power; the logger and",
             "  modem keep a separate protected supply so data survive"]
    emit("f_power", lines)


def extrapolation_table() -> None:
    lines = ["uncertainty of extrapolating the speed from the top cup to the hub:",
             "  u(v)/v = ln(hub / top) x u(shear); energy x 1.6",
             "  top m  hub m   u(shear) 0.03       u(shear) 0.05",
             "                 speed   energy      speed   energy"]
    for top, hub in ((100, 100), (100, 120), (100, 150), (100, 175),
                     (80, 120), (60, 150)):
        a = math.log(hub / top)
        lines.append(f"  {top:4d}  {hub:5d}   {100 * a * 0.03:4.1f} %  {160 * a * 0.03:4.1f} %"
                     f"      {100 * a * 0.05:4.1f} %  {160 * a * 0.05:4.1f} %")
    lines += ["  measuring at (or near) hub height removes the largest term a",
              "  short mast adds; a lidar to the hub replaces it by its own",
              "  smaller verified uncertainty"]
    emit("f_extrap_unc", lines)


def value() -> None:
    """Campaign options and the long-term P90 of the farm (integrated
    example 2, hub 100 m): speed terms from lab D (A-254), changes A-257."""
    p50 = integrated.farm_long_term()["farm"]
    base = {"cal": 1.0, "mount": 1.0, "mcp": 2.0, "period": 0.8, "extrap": 0.0}
    hub150 = dict(base, extrap=100 * math.log(1.5) * 0.03)
    options = [("hub 100 m, campaign as built", base),
               ("hub 150 m, mast only (extrapolated)", hub150),
               ("hub 150 m, lidar to the hub (0.8 %)", dict(hub150, extrap=0.8)),
               ("hub 100 m, second year (MCP 1.5 %)", dict(base, mcp=1.5)),
               ("hub 100 m, second year + second mast", dict(base, mcp=1.5,
                                                             mount=0.7))]
    lines = [f"what a better campaign is worth (farm P50 {p50:.2f} GWh,"
             " 50 u/MWh):",
             "  option                                  u(v)   u(E)   P90 GWh"]
    for name, d in options:
        uv = math.sqrt(sum(x ** 2 for x in d.values()))
        ue = round(1.6 * uv / 100, 3)
        p90 = f"{ir.p_value(p50, ue):6.1f}" if "100 m" in name else "   (*)"
        lines.append(f"  {name:38s} {uv:4.2f} % {100 * ue:4.1f} %   {p90}")
    p_a = ir.p_value(p50, round(1.6 * math.sqrt(1 + 1 + 4 + 0.64) / 100, 3))
    p_b = ir.p_value(p50, round(1.6 * math.sqrt(1 + 1 + 1.5 ** 2 + 0.64) / 100, 3))
    lines += ["  (*) a 150 m hub also has a larger P50 (lab E)",
              f"  a second year raises P90 by {p_b - p_a:.2f} GWh a year:"
              f" about {(p_b - p_a) * 50:,.0f} k u a year",
              "  of energy that lenders count (debt is sized on P90, chapter 21);",
              "  the extra campaign costs are compared with that, not with the",
              "  P50 (which measuring does not change)"]
    emit("f_value", lines)


if __name__ == "__main__":
    dbs()
    conditional()
    power_budget()
    extrapolation_table()
    value()
