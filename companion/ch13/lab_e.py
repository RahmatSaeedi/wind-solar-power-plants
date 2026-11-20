"""Chapter 13, section D2 - second lab: which hub height? The long-term
100 m series (integrated example 2) carried to 120 and 150 m with the
mast's shear by hour of day, checked against the lidar, with hub density,
the farm energy, the uncertainty of each option and the P90 it gives,
and the most a taller tower may cost per metre for the P90 energy alone.

Run from the project root:   python -m companion.ch13.lab_e
Writes companion/ch13/expected/l_*.txt and diagrams/data/ch13-hubs.csv.
Synthetic data A-250 .. A-257; D-015, D-017.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch13 import integrated, lab_d, sources
from companion.ch13.common import csv, emit
from plantp import irradiance as ir

HUBS = (100, 120, 150)
U_BASE = 2.58                    # speed, per cent (lab D, A-254)
U_LIDAR = 0.8                    # lidar to the hub, verified (A-257)
PRICE = 50.0                     # u per MWh (teaching)


def shear_by_hour() -> np.ndarray:
    """Mean shear exponent of each hour from the clean 60 and 100 m cups."""
    m = sources.mast_year()
    lg = m["logged"]
    ok = ~np.isnan(lg["v100"]) & ~m["iced"] & (lg["v60"] > 3)
    a = np.log(lg["v100"] / lg["v60"]) / math.log(100 / 60)
    hour = m["true"]["hour"]
    return np.array([np.mean(a[ok & (hour == h)]) for h in range(24)])


def lidar_check(alpha_h) -> dict:
    """Extrapolated mast against the lidar (bias 1.005 removed) on the
    records both have, at 120 and 150 m."""
    m = sources.mast_year()
    li = sources.lidar()
    lg = m["logged"]
    hour = m["true"]["hour"]
    ok = ~np.isnan(lg["v100"]) & ~m["iced"] & ~li["lost"]
    out = {}
    for z in (120, 150):
        ext = lg["v100"] * (z / 100) ** alpha_h[hour]
        out[z] = float(np.mean(li[z][ok] / 1.005) / np.mean(ext[ok]))
    return out


def hubs() -> None:
    r = integrated.farm_long_term()
    alpha_h = shear_by_hour()
    check = lidar_check(alpha_h)
    hour_l = np.tile(np.arange(8760) % 24, len(sources.reference()["years"]))
    rho_l = np.tile(r["rho"], len(sources.reference()["years"]))
    cv, cp = lab_d.curve()
    n_years = len(sources.reference()["years"])
    lines = ["hub height study of the twelve turbines (long term, D-017):",
             "  shear by hour from 60/100 m: night "
             f"{alpha_h[0]:.3f}, midday {alpha_h[12]:.3f}",
             "  lidar against the extrapolated mast: 120 m"
             f" {100 * (check[120] - 1):+.2f} %, 150 m {100 * (check[150] - 1):+.2f} %",
             "    (synthetic data agree closely; a real site differs more)",
             "  hub m  mean m/s   farm GWh   u(E) mast  u(E) lidar"
             "   P90 lidar"]
    rows, res = [], {}
    for z in HUBS:
        v = np.clip(r["long"], 0, None) * (z / 100) ** alpha_h[hour_l]
        if z > 100:
            v = v * check[z]                    # lidar-verified level
        dz = z - 100
        rho = rho_l * math.exp(-9.81 * dz / (287.05 * 283.0))
        v_eq = v * (rho / 1.225) ** (1 / 3)
        farm = 12 * np.interp(v_eq, cv, cp).sum() / n_years / 1e6 * r["wake"]
        u_mast = 1.6 * math.sqrt(U_BASE ** 2 + (100 * math.log(z / 100) * 0.03) ** 2)
        u_lid = 1.6 * math.sqrt(U_BASE ** 2 + (U_LIDAR if z > 100 else 0.0) ** 2)
        p90 = ir.p_value(farm, round(u_lid / 100, 3))
        res[z] = (farm, p90)
        rows.append((z, f"{farm:.2f}", f"{p90:.2f}"))
        lines.append(f"  {z:4d}   {v.mean():6.3f}    {farm:7.2f}     {u_mast:4.1f} %"
                     f"      {u_lid:4.1f} %     {p90:6.1f}")
    csv("ch13-hubs.csv", "hub,p50,p90", rows)
    base = res[100][1]
    lines.append("  extra P90 energy against 100 m and the most a taller tower")
    lines.append("  may cost for it (20 years, 50 u/MWh, no discounting):")
    for z in (120, 150):
        d = res[z][1] - base
        per_m = d * 1e3 * PRICE * 20 / (12 * (z - 100))
        lines.append(f"    {z} m: +{d:.2f} GWh a year; up to {per_m / 1e3:,.0f} k u"
                     " per metre per turbine")
    lines += ["  a taller hub gains energy from the shear and loses a little",
              "  density; the lidar keeps its uncertainty close to a hub-height",
              "  mast; the cost side (tower, foundation, crane, loads) belongs",
              "  to chapters 11, 21, 30 and 31, and discounting lowers the limit"]
    emit("l_hubs", lines)


def sensitivity() -> None:
    """How the 150 m result moves with the shear: one exponent for all
    hours, by hour, and by hour minus or plus 0.03."""
    r = integrated.farm_long_term()
    alpha_h = shear_by_hour()
    n_years = len(sources.reference()["years"])
    hour_l = np.tile(np.arange(8760) % 24, n_years)
    rho_l = np.tile(r["rho"], n_years) * math.exp(-9.81 * 50 / (287.05 * 283.0))
    cv, cp = lab_d.curve()
    one = float(np.average(alpha_h))
    lines = ["the 150 m farm energy with different shear assumptions:"]
    base = None
    for name, a in (("by hour (basis)", alpha_h[hour_l]),
                    (f"one exponent {one:.3f}", np.full(len(hour_l), one)),
                    ("by hour - 0.03", alpha_h[hour_l] - 0.03),
                    ("by hour + 0.03", alpha_h[hour_l] + 0.03)):
        v = np.clip(r["long"], 0, None) * 1.5 ** a
        e = 12 * np.interp(v * (rho_l / 1.225) ** (1 / 3), cv, cp).sum() / n_years / 1e6
        e *= r["wake"]
        base = base or e
        lines.append(f"  {name:22s} {e:7.2f} GWh  ({100 * (e / base - 1):+.2f} %)")
    lines += ["  an error of 0.03 in the shear moves a 150 m hub by about",
              "  2 % of energy: the term a lidar to the hub removes"]
    emit("l_sensitivity", lines)


if __name__ == "__main__":
    hubs()
    sensitivity()
