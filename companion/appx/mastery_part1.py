"""Appendix X - answers of the Part I diagnostic mastery test (chapters 1-5).

Run from the project root:   python -m companion.appx.mastery_part1
Writes companion/appx/expected/mastery_part1.txt.
Data pack 1.1.0 (synthetic); chapter 1 and chapter 5 models; fictional money.
"""
from __future__ import annotations

import math

import numpy as np

from companion.appx.common import emit
from companion.ch05 import step3_model as m
from plantp import datapack, money, screening as sc
from plantp.units import Q

OUT: list[str] = []


def p(pid: str, text: str) -> None:
    OUT.append(f"{pid}: {text}")


def units() -> None:
    e = Q(97.3, "GWh")
    cf = (e / (Q(50, "MW") * Q(8760, "h"))).to("")
    p("M1", f"97.3 GWh / (50 MW x 8760 h) = {cf:.3f}; '97.3 GW' is a power, not an energy")
    area = math.pi * 75 ** 2
    p_wind = 0.5 * 1.056 * area * 8.0 ** 3
    p("M2", f"wind power through the rotor 1/2 rho A v^3 = 0.5 x 1.056 x {area:,.0f} x 512 = "
            f"{p_wind / 1e6:.3f} MW; in 1 h {p_wind / 1e6:.3f} MWh (kg/m3 m2 m3/s3 = W)")
    p("M3", f"289 812 000 in a column read as kWh = {289_812_000 / 1e6:.1f} GWh "
            "(plausible); read as MWh it would be 290 TWh (impossible)")


def calculations() -> None:
    h = datapack.load_hourly()
    noon = h.loc["2023-06-23 12:00"]
    p("M10", f"23 June 12:00: G {noon['ghi_wm2']} W/m2, T {noon['t_air_c']} C -> "
             f"{float(m.pv_ac_mw(noon['ghi_wm2'], noon['t_air_c'])):.3f} MW")
    cf = money.project_cash_flow(273_520, 50.0, 100e6, 2.75e6, 25, 0.005, 0.70, 0.06, 15)
    p("M11", f"DSCR year 1 = {cf['cfads'][1] / 1e6:.3f} / {cf['debt_service'][1] / 1e6:.3f} "
             f"= {cf['dscr'][1]:.2f}")
    p("M12", f"annual GHI from the data pack = {h['ghi_wm2'].sum() / 1000:.1f} kWh/m2 "
             "(expected_results.json 1947.2)")
    curve = datapack.load_power_curve()
    wind = np.asarray(sc.wind_power_mw(h["ws_100m_ms"], curve["wind_speed_ms"],
                                       curve["power_kw"], 12))
    rho = m.air_density(h["p_hpa"], h["t_air_c"])
    wind5 = np.asarray(m.wind_farm_mw(h["ws_100m_ms"], rho, curve["wind_speed_ms"],
                                      curve["power_kw"]))
    p("M4", f"wind: chapter 1 {wind.sum() / 1000:.1f} GWh (1.225 kg/m3), chapter 5 "
            f"{wind5.sum() / 1000:.2f} GWh (hourly density, mean {float(np.mean(rho)):.3f})")
    p("M13", f"same speeds, hourly vs one annual mean: "
             f"{np.interp(h['ws_100m_ms'], curve['wind_speed_ms'], curve['power_kw']).sum() * 12 / 1e6:.1f}"
             f" vs {np.interp(np.full(8760, h['ws_100m_ms'].mean()), curve['wind_speed_ms'], curve['power_kw']).sum() * 12 / 1e6:.1f} GWh gross")


if __name__ == "__main__":
    units()
    calculations()
    emit("mastery_part1", sorted(OUT, key=lambda s: int(s.split(":")[0][1:])))
