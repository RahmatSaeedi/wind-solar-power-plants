"""Chapter 11 - small worked calculations, one line each (E01 ...), used by
the text and the self-checks.

Run from the project root:   python -m companion.ch11.worked
Writes companion/ch11/expected/worked.txt.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch11 import rotor
from companion.ch11.common import emit
from plantp import datapack, physics, stats, wind as w

OUT: list[str] = []
A = rotor.AREA


def e(eid: str, text: str, more: str = "") -> None:
    OUT.append(f"{eid}: {text}")
    if more:
        OUT.append(f"     {more}")


def lines() -> None:
    p0 = 0.5 * 1.225 * A * 1000 / 1e6
    p1 = 0.5 * 1.056 * A * 1000 / 1e6
    e("E01", f"1/2 rho A v^3 at 10 m/s: {p0:.2f} MW (1.225), {p1:.2f} MW (1.056);"
             f" {5e6 / A:.0f} W/m2")
    om = rotor.turbine().omega_max
    e("E02", f"11.5 rpm = {om:.3f} rad/s; tip speed {om * 75:.1f} m/s; TSR at"
             f" 10 m/s {om * 75 / 10:.2f}")
    e("E03", f"Betz a = 1/3: Cp {16 / 27:.4f}, Ct {8 / 9:.3f}; rotor 2V/3, far"
             " wake V/3")
    t_id = 8 / 9 * 0.5 * 1.225 * A * 100 / 1e3
    e("E04", f"ideal thrust at 10 m/s (Ct 8/9): {t_id:.0f} kN; BEM 923 kN")
    re = om * 52.5 * 3.5 / 1.5e-5
    e("E05", f"Reynolds number at 0.7 R: 63 m/s x 3.5 m / 1.5e-5 = {re:.1e}")
    cp = w.bem(rotor.blade(), rotor.tsr_opt()).cp
    k = 0.5 * 1.225 * A * 75 ** 3 * cp / rotor.tsr_opt() ** 3
    e("E06", f"torque law k = {k / 1e3:,.0f} kN m s2; at 0.907 rad/s: "
             f"{k * 0.907 ** 2 / 1e6:.3f} MN m")
    q = 5e6 / 0.94 / om
    e("E07", f"rated torque 5 MW / 0.94 / {om:.3f} = {q / 1e6:.2f} MN m; ratio"
             f" 1155 / 11.5 = {1155 / 11.5:.1f}")
    e("   ", f"high-speed shaft torque {q / (1155 / 11.5) / 1e3:.0f} kN m")
    e("E08", f"yaw error 10 deg: cos^2 loss {100 * (1 - math.cos(math.radians(10)) ** 2):.1f}"
             f" %, cos^3 loss {100 * (1 - math.cos(math.radians(10)) ** 3):.1f} %")
    p_std = float(physics.standard_pressure(1200.0))
    rho_std = float(physics.air_density(p_std, 15 - 0.0065 * 1200))
    e("E09", f"standard atmosphere at 1200 m: {p_std:.0f} hPa, "
             f"{15 - 0.0065 * 1200:.1f} C -> {rho_std:.3f} kg/m3")
    e("E10", f"equivalent speed 8 x (1.056/1.225)^(1/3) = "
             f"{8 * (1.056 / 1.225) ** (1 / 3):.3f} m/s")
    e("E11", "rotor energy at 11.5 rpm 23.2 MJ; 90 deg at 8 deg/s: 11.2 s")
    e("E12", f"10 rpm: 1P {10 / 60:.3f} Hz, 3P {0.5:.3f} Hz; tower 0.215 Hz")
    n = 20 * 8760 * 60 * 9 * 0.85
    e("E13", f"edgewise cycles in 20 yr at 9 rpm, 85 % running: {n:.1e}")
    e("E14", f"Miner, m = 10: half the reference range does 1/{2 ** 10} of"
             " the damage")
    h = datapack.load_hourly()
    v = h["ws_100m_ms"].to_numpy(float)
    kk, cc = stats.weibull_fit_mle(v)
    e("E15", f"Weibull k {kk:.2f}, c {cc:.2f}: mean c Gamma(1 + 1/k) = "
             f"{cc * math.gamma(1 + 1 / kk):.2f} m/s (data {v.mean():.2f})")
    e("E16", f"hours below cut-in {int((v < 3).sum())} "
             f"({100 * (v < 3).mean():.1f} %), above 25 m/s {int((v > 25).sum())}")
    for x, lab in ((4 * 150, "4D"), (8 * 150, "8D")):
        d = w.jensen_deficit(0.852, x, 150.0)
        e("E17" if lab == "4D" else "   ", f"Jensen, Ct 0.852, {lab}: deficit "
              f"{d:.3f}; power x (1 - d)^3 = {(1 - d) ** 3:.3f}")
    e("E18", f"capacity factor 188.16 GWh / (60 MW x 8760 h) = "
             f"{188.16 / (60 * 8.76):.3f}")
    e("E19", f"lightning 2 x 9 pi 0.175^2 = {2 * 9 * math.pi * 0.175 ** 2:.2f}"
             " flashes a year;", "ice throw 1.5 x (150 + 100) = 375 m")
    e("E20", f"BPFO = 12/2 x 19.25 x (1 - 0.2) = {6 * 19.25 * 0.8:.1f} Hz")
    e("E21", f"blade from hub 2.5 m to tip 75 m: {75 - 2.5:.1f} m long")
    e("E22", f"centrifugal 22 t x {om:.3f}^2 x 22 m = "
             f"{22e3 * om ** 2 * 22 / 1e3:.0f} kN;",
      f"gravity 22 t x 9.81 x 22 m = {22e3 * 9.81 * 22 / 1e6:.2f} MN m")
    e("E23", f"tower base moment 923 kN x 100 m = {923 * 100 / 1e3:.1f} MN m")
    p_aero = 5e6 / 0.94
    q_gb = 0.025 * p_aero                         # A-225 gearbox loss share
    flow = q_gb / (870 * 1900 * 15) * 6e4
    e("E24", f"losses at rated {p_aero / 1e3:,.0f} - 5,000 = {(p_aero - 5e6) / 1e3:.0f}"
             f" kW; gearbox 2.5 % = {q_gb / 1e3:.0f} kW",
      f"oil flow for 15 K rise: {q_gb / 1e3:.0f} kW / (870 x 1900 x 15) = "
      f"{flow:.0f} L/min")


if __name__ == "__main__":
    lines()
    emit("worked", OUT)
