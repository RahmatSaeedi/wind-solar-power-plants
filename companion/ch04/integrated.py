"""Chapter 4 — three integrated Plant P examples.

Run from the project root:   python -m companion.ch04.integrated
  int_wind     one turbine through a year: hub density, power density, Betz, capture,
               and the rotor-equivalent wind speed under shear
  int_busbar   the 33 kV main busbar: hourly export current, four bar options, hours
               above a temperature limit (A-061)
  int_joint    a bolted joint that degrades: contact resistance, temperature and the
               thermal feedback, with a thermography alarm (A-062)
Writes companion/ch04/expected/int_*.txt and diagrams/data/ch04-joint.csv.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch04.common import csv, emit
from plantp import datapack, materials as mt, physics as ph, screening as sc

AREA = math.pi * 75.0 ** 2
MONTH_HOURS = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]) * 24


def hub_density(hourly):
    p, t = hourly["p_hpa"].to_numpy(), hourly["t_air_c"].to_numpy()
    p_hub = p * (1 - 0.0065 * 100 / (t + 273.15)) ** (ph.G0 / (ph.R_DRY * 0.0065))
    return ph.air_density(p_hub, t - 0.65)


def wind_chain() -> None:
    hourly = datapack.load_hourly()
    curve = datapack.load_power_curve()
    vs, pk = curve["wind_speed_ms"].to_numpy(), curve["power_kw"].to_numpy()
    v = hourly["ws_100m_ms"].to_numpy()
    rho = hub_density(hourly)
    pd = 0.5 * rho * v ** 3
    e_wind = float(np.sum(pd)) * AREA / 1e9                 # GWh per year through the rotor
    e_betz = e_wind * 16 / 27
    veq = v * (rho / 1.225) ** (1 / 3)
    e_turb = float(np.sum(np.interp(veq, vs, pk))) / 1e6
    alpha = 0.171
    # rotor-equivalent speed: average v^3 over the disc with v(z) = v_hub (z / 100)^alpha
    z = np.linspace(25.0, 175.0, 3001)
    chord = 2 * np.sqrt(np.maximum(75.0 ** 2 - (z - 100.0) ** 2, 0.0))
    w = chord / np.trapezoid(chord, z)
    cube = float(np.trapezoid(w * (z / 100.0) ** (3 * alpha), z))
    rews = cube ** (1 / 3)
    emit("int_wind", [
        "one WT-5.0-150 at Plant P through the data-pack year (S0, synthetic data):",
        f"  mean hub density {rho.mean():.3f} kg/m3; mean wind power density "
        f"{pd.mean():.0f} W/m2",
        f"  energy carried through the rotor area: {e_wind:.1f} GWh/yr",
        f"  Betz limit 16/27 of it: {e_betz:.1f} GWh/yr",
        f"  turbine output (density-corrected power curve, no farm losses): {e_turb:.2f} GWh/yr",
        f"  capture: {e_turb / e_wind:.1%} of the wind, {e_turb / e_betz:.1%} of the Betz limit",
        f"  capacity factor {e_turb / (5 * 8.76):.1%}",
        f"  shear alpha {alpha}: cube of the speed averaged over the disc = {cube:.4f} x hub;",
        f"    rotor-equivalent speed = {rews:.4f} x hub speed ({100 * (rews - 1):+.2f} %)",
        "  most of the wind's energy is never captured: above rated speed the turbine",
        "    sheds it on purpose, and below cut-in there is nothing to gain",
    ])


def busbar() -> None:
    hourly = datapack.load_hourly()
    curve = datapack.load_power_curve()
    vs, pk = curve["wind_speed_ms"].to_numpy(), curve["power_kw"].to_numpy()
    pv = np.asarray(sc.pv_ac_power_mw(hourly["ghi_wm2"], 60, 50))
    wind = np.asarray(sc.wind_power_mw(hourly["ws_100m_ms"].to_numpy(), vs, pk, 12))
    export = np.minimum(pv + wind, 100.0)
    i = export * 1e6 / (math.sqrt(3) * 33e3 * 0.95)
    t_room = hourly["t_air_c"].to_numpy() + 15.0         # switchgear room (A-061)
    h, limit = 10.0, 90.0                                 # W/m2K, C (A-061)
    options = [("Cu 80 x 10", 1.72e-8, 0.00393, 80e-3, 10e-3, 1),
               ("Cu 2 x (80 x 10)", 1.72e-8, 0.00393, 80e-3, 10e-3, 2),
               ("Al 100 x 10", 2.82e-8, 0.00403, 100e-3, 10e-3, 1),
               ("Al 2 x (100 x 10)", 2.82e-8, 0.00403, 100e-3, 10e-3, 2)]
    lines = [f"33 kV main busbar: export current I = P / (sqrt3 x 33 kV x 0.95); peak "
             f"{i.max():.0f} A",
             f"  room = air + 15 K, cooling h = {h} W/m2K, limit {limit:.0f} C (A-061);"
             " steady state each hour",
             "  option            R20 (micro-ohm/m)  T max (C)  hours > limit  kg/m"]
    for name, rho_e, a_r, b, t, n in options:
        r20 = rho_e / (b * t * n)
        perim = n * 2 * (b + t)
        temps = np.array([ph.conductor_temperature(ii, r20, a_r, h, perim, ta)[0]
                          for ii, ta in zip(i, t_room)])
        dens = 8960 if name.startswith("Cu") else 2700
        lines.append(f"  {name:18s} {r20 * 1e6:12.2f} {temps.max():12.1f} "
                     f"{int((temps > limit).sum()):12d} {dens * b * t * n:7.1f}")
    lines += ["  the hottest hours are windy summer middays: high current and a warm room",
              "  bar spacing, enclosure ventilation and the standard's rating method decide",
              "    the final rating (chapter 24); this is the physics underneath"]
    emit("int_busbar", lines)


def hot_joint() -> None:
    hourly = datapack.load_hourly()
    curve = datapack.load_power_curve()
    vs, pk = curve["wind_speed_ms"].to_numpy(), curve["power_kw"].to_numpy()
    pv = np.asarray(sc.pv_ac_power_mw(hourly["ghi_wm2"], 60, 50))
    wind = np.asarray(sc.wind_power_mw(hourly["ws_100m_ms"].to_numpy(), vs, pk, 12))
    i = np.minimum(pv + wind, 100.0) * 1e6 / (math.sqrt(3) * 33e3 * 0.95) / 2   # one of two
    edges = np.concatenate([[0], np.cumsum(MONTH_HOURS)])
    i2_month = np.array([np.mean(i[a:b] ** 2) for a, b in zip(edges[:-1], edges[1:])])
    i_peak = np.array([np.quantile(i[a:b], 0.99) for a, b in zip(edges[:-1], edges[1:])])
    t_room = np.array([np.mean(hourly["t_air_c"].to_numpy()[a:b]) for a, b in
                       zip(edges[:-1], edges[1:])]) + 15.0
    ha, k0, ea = 1.2, 0.08, 70e3                          # W/K, 1/yr at 40 C, J/mol (A-062)
    lines = ["bolted joint on a feeder busbar (half the plant current; A-062):",
             "  joint temperature = room + I^2 R_c / (h A), using the 99th-percentile",
             "  current of each month; R_c grows by k0 x Arrhenius(T) per year",
             f"  h A = {ha} W/K, k0 = {k0}/yr at 40 C, Ea = 70 kJ/mol (all assumed)",
             "  R_c start      rise in month 0   alarm (rise > 10 K)   T > 105 C"]
    series = {}
    for rc0 in (10e-6, 30e-6, 60e-6):
        rc, temps, alarm, fail = rc0, [], None, None
        for month in range(120):
            m = month % 12
            t_j = t_room[m] + i_peak[m] ** 2 * rc / ha
            temps.append(t_j)
            if alarm is None and t_j - t_room[m] > 10.0:
                alarm = month
            if fail is None and t_j > 105.0:
                fail = month
            if t_j > 400:                                 # far past failure: stop
                break
            rc *= math.exp(k0 * mt.arrhenius_factor(ea, 40.0, t_j) / 12)
        series[rc0] = temps
        rise0 = i_peak[0] ** 2 * rc0 / ha
        lines.append(f"  {rc0 * 1e6:5.0f} micro-ohm  {rise0:12.1f} K  "
                     f"{'month ' + str(alarm) if alarm is not None else 'never':>18s}  "
                     f"{'month ' + str(fail) if fail is not None else 'never':>12s}")
    lines += ["  a poor joint heats, oxidises and loosens faster, which heats it more:",
              "  positive feedback. Thermography finds it months before it fails, if the",
              f"  survey happens under load (a 99th-percentile month current of {i_peak.max():.0f} A)"]
    emit("int_joint", lines)
    n = max(len(v) for v in series.values())
    rows = []
    for k in range(n):
        rows.append((k, *(f"{min(series[r][k], 160):.2f}" if k < len(series[r]) else "nan"
                          for r in (10e-6, 30e-6, 60e-6))))
    csv("ch04-joint.csv", "month,r10,r30,r60", rows)
    _ = i2_month


def main() -> None:
    wind_chain()
    busbar()
    hot_joint()


if __name__ == "__main__":
    main()
