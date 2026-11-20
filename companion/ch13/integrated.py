"""Chapter 13 - three integrated Plant P examples: one mast day hour by
hour (introductory), the long-term hub-height wind and farm energy with its
uncertainty (intermediate), and the campaign acceptance report (integrated).

Run from the project root:   python -m companion.ch13.integrated
Writes companion/ch13/expected/i_*.txt.
Synthetic data A-250 .. A-256; D-015, D-017.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch13 import lab_d, sources
from companion.ch13.common import emit
from plantp import irradiance as ir, windres as wr


def one_day() -> None:
    m = sources.mast_year()
    lg = m["logged"]
    d0 = 91                                              # 2 April
    sl = slice(d0 * 144, d0 * 144 + 144)
    v100, v80, v60 = lg["v100"][sl], lg["v80"][sl], lg["v60"][sl]
    sd, wd, t = lg["sd100"][sl], lg["wd100"][sl], lg["t"][sl]
    lines = ["one mast day, 2 April 2023 (logged, hourly means of ten-minute data):",
             "  hour  v60   v80   v100  shear  TI    dir  T C"]
    for h in range(0, 24, 2):
        k = slice(h * 6, h * 6 + 6)
        a2 =math.log(v100[k].mean() / v60[k].mean()) / math.log(100 / 60)
        lines.append(f"  {h:02d}   {v60[k].mean():5.2f} {v80[k].mean():5.2f} "
                     f"{v100[k].mean():5.2f}  {a2:5.2f}  {np.mean(sd[k] / v100[k]):.3f}"
                     f"  {np.mean(wd[k]):4.0f} {np.mean(t[k]):5.1f}")
    lines += ["  shear from 60 and 100 m (the 80 m cup is in the shadow sector",
              "  for part of the day); the night profile is steeper and less",
              "  turbulent, the day profile flatter and more turbulent"]
    emit("i_day", lines)


def farm_long_term() -> dict:
    """Long-term 100 m series by variance-ratio MCP and the farm energy
    with hub-height density and the D-015 wake factor (D-017)."""
    m = sources.mast_year()
    lg = m["logged"]
    ok10 = ~np.isnan(lg["v100"]) & ~m["iced"]
    site = np.where(ok10, lg["v100"], np.nan).reshape(-1, 6)
    good = np.sum(~np.isnan(site), axis=1) == 6
    y = np.mean(site[good], axis=1)
    ref = sources.reference()
    x = ref["hourly_2023"][good]
    long_, a, b = wr.mcp_variance_ratio(x, y, ref["long"].ravel())
    rho = m["true"]["rho_hub"].reshape(-1, 6).mean(axis=1)
    rho_l = np.tile(rho, len(ref["years"]))
    v_eq = np.clip(long_, 0, None) * (rho_l / 1.225) ** (1 / 3)
    cv, cp = lab_d.curve()
    wake = 188.16 / 201.23                               # D-015, layout A
    farm = 12 * np.interp(v_eq, cv, cp).sum() / len(ref["years"]) / 1e6 * wake
    v_eq23 = sources.mast_year()["true"]["v100"].reshape(-1, 6).mean(axis=1) * \
        (rho / 1.225) ** (1 / 3)
    farm23 = 12 * np.interp(v_eq23, cv, cp).sum() / 1e6 * wake
    return {"farm": farm, "farm23": farm23, "a": a, "b": b, "long": long_,
            "y": y, "rho": rho, "wake": wake}


def long_term() -> None:
    r = farm_long_term()
    farm, farm23, a, b, long_, y = (r[k] for k in ("farm", "farm23", "a", "b",
                                                   "long", "y"))
    u_e = 0.041                                          # lab D budget, energy
    iav = 0.035 * 1.6                                    # one year, energy
    lines = ["long-term wind and farm energy (variance-ratio MCP, D-017):",
             f"  MCP line: site = {a:+.3f} + {b:.4f} x reference",
             f"  long-term 100 m mean {np.mean(long_):.3f} m/s; 2023"
             f" {np.mean(y):.3f} m/s",
             f"  farm after hub density and wakes: 2023 {farm23:.2f} GWh,",
             f"    long term {farm:.2f} GWh ({100 * (farm / farm23 - 1):+.1f} %)",
             f"  energy uncertainty from the wind {100 * u_e:.1f} %: P90 long-term"
             f" {ir.p_value(farm, u_e):.1f} GWh",
             f"  one year adds year-to-year {100 * iav:.1f} %: P90 one year"
             f" {ir.p_value(farm, math.sqrt(u_e ** 2 + iav ** 2)):.1f} GWh",
             "  2023 was a slightly calm year; the measured year alone would",
             "  understate the long-term energy (chapter 11 used it as it is)"]
    emit("i_longterm", lines)


def acceptance() -> None:
    lines = ["campaign acceptance report of the Plant P mast (PLP-GEN-REP-0005):",
             "  period: 12 months, ten-minute data, logger PLP-MET-01",
             "  recovery after QC: 100 m 98.6 %, 60 m 98.9 %, 80 m 36.9 %",
             "    (80 m: shadow sector excluded, bearing wear from July)",
             "  instruments: calibration certificates per serial; 80 m cup",
             "    replaced and recalibrated (action), boom turned out of the",
             "    prevailing sector (action)",
             "  icing: 6 events, detected at the start; heated sensors advised",
             "  lidar: verified against the 100 m cup (slope 1.005, r^2 0.997)",
             "  long term: variance-ratio MCP with a 20-year reference, r 0.95",
             "  shear: from 60 and 100 m by hour of day; veer recorded",
             "  turbulence: mean and 90 % quantile by bin for the class check",
             "  extremes: Gumbel fit of 20 annual maxima, 50-year value",
             "  accepted for: hub-height energy at 100 m; conditional for a",
             "    higher hub (lidar to hub height); not for loads at 80 m"]
    emit("i_accept", lines)


if __name__ == "__main__":
    one_day()
    long_term()
    acceptance()
