"""Chapter 11 - three integrated Plant P examples: one turbine at one hour
(introductory), the wind farm's annual energy from free stream to wakes
(intermediate), and the inspection basis of a tower section (integrated).

Run from the project root:   python -m companion.ch11.integrated
Writes companion/ch11/expected/i_*.txt.
Data pack 1.1.0, S0; teaching values A-211 .. A-224; D-011, D-015.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch11 import lab_d, rotor
from companion.ch11.common import emit
from plantp import datapack, physics, wind as w


def one_hour() -> None:
    h = datapack.load_hourly()
    v = h["ws_100m_ms"].to_numpy(float)
    t = h["t_air_c"].to_numpy(float)
    k = int(np.argmin(np.abs(v - 9.5) + 100 * (t < 25)))
    rho = float(physics.air_density(float(h["p_hpa"].iloc[k]), float(t[k])))
    op = w.operate(rotor.turbine(), float(v[k]), rho)
    v_eq = float(w.density_equivalent_speed(v[k], rho))
    pack = float(lab_d.pack_power(v_eq))
    day, hour = k // 24 + 1, k % 24
    rpm = op.omega * 30 / math.pi
    emit("i_hour", [
        f"one turbine, day {day} of the data year, {hour:02d}:00 (S0):",
        f"  wind at hub {v[k]:.2f} m/s from {h['wd_100m_deg'].iloc[k]:.0f} deg; "
        f"air {t[k]:.1f} C, {h['p_hpa'].iloc[k]:.0f} hPa -> {rho:.3f} kg/m3",
        f"  rotor (BEM, steady): {rpm:.2f} rpm, TSR {op.tsr:.2f}, pitch "
        f"{op.pitch:.1f} deg, Cp {op.cp:.3f}",
        f"  power {op.power_w / 1e3:,.0f} kW; aero torque {op.torque_nm / 1e6:.2f}"
        f" MN m; thrust {op.thrust_n / 1e3:,.0f} kN",
        f"  generator {rpm * 100.4:.0f} rpm through the 1:100.4 gearbox"
        " (D-011)",
        f"  data-pack curve at the equivalent speed {v_eq:.2f} m/s: "
        f"{pack:,.0f} kW",
        "  the steady model and the measured-style curve differ by the",
        "  turbulence averaging of a real ten-minute mean"])


def farm() -> None:
    v, wd, rho = lab_d.hourly()
    gross = 12 * lab_d.pack_power(v).sum() / 1e6
    v_eq = w.density_equivalent_speed(v, rho)
    dens = 12 * lab_d.pack_power(v_eq).sum() / 1e6
    xy = lab_d.rotate(lab_d.layouts()["A: 2 rows of 6, 4D x 8D"],
                      lab_d.prevailing(wd))
    waked = lab_d.farm_energy(xy)[1] / 1e3              # layout A, GWh
    emit("i_farm", [
        "annual energy of the 12 turbines, free stream to wakes (D-015):",
        f"  gross, power curve at 1.225 kg/m3          {gross:7.2f} GWh",
        f"  site air density (equivalent speed)        {dens:7.2f} GWh "
        f"({100 * (dens / gross - 1):+.1f} %)",
        f"  wakes, layout A (2 x 6, 4D x 8D)           {waked:7.2f} GWh "
        f"({100 * (waked / dens - 1):+.1f} %)",
        f"  capacity factor {waked / (60 * 8.76):.3f}; full-load hours "
        f"{waked / 60 * 1e3:,.0f}",
        "  not yet included: availability, electrical losses, curtailment",
        "  at the export limit, icing, degradation and the uncertainty of",
        "  each step (chapters 13, 15 and 21)",
        "  chapter 5's 177.08 GWh used one lumped 12 % loss: the wake loss",
        "  alone is about half of it"])


def tower_plan() -> None:
    welds_circ, welds_long, flanges = 518.0, 100.0, 8      # c_tower, A-224
    emit("i_quality", [
        "inspection basis of one tower section family (A-224, teaching):",
        f"  per tower: {welds_circ:.0f} m circumferential and {welds_long:.0f} m"
        f" longitudinal welds, {flanges} flanges",
        "  plate: mill certificate per heat, thickness and lamination check",
        "  rolling: roundness and diameter of each can",
        "  welding: approved procedures and welders; visual 100 %;",
        "    volumetric (ultrasonic) and surface tests at the extents the",
        "    design and its standard require",
        "  flanges: flatness and inclination after welding (bolt fatigue)",
        "  coating: surface preparation, dry-film thickness, adhesion",
        "  dimensional check and records before release; transport and",
        "  site receipt inspection for damage to coating and flanges",
        f"  twelve towers: {12 * welds_circ / 1e3:.1f} km of circumferential"
        " welds in the records"])


if __name__ == "__main__":
    one_hour()
    farm()
    tower_plan()
