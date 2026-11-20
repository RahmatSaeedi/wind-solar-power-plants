"""Calculations of the resource tool: pure functions, moved here unchanged
from step 3 (companion/ch05/step3_model.py); a regression test checks that
both give identical numbers.

Teaching models (chapter 5): horizontal irradiance on the array, the NOCT
cell temperature, a lumped "other losses" factor k_other (A-097); the wind
power curve at the site air density by the equivalent-speed method (D-008).
"""
from __future__ import annotations

import numpy as np

R_DRY_AIR = 287.05               # J/(kg K)
RHO_REF = 1.225                  # kg/m3, air density of the power curve


# [start: pv]
def cell_temperature(ghi_wm2, t_air_c, noct_c=45.0):
    """NOCT model: T_cell = T_air + (NOCT - 20) / 800 * G   (degC)."""
    return np.asarray(t_air_c) + (noct_c - 20.0) / 800.0 * np.asarray(ghi_wm2)


def pv_ac_mw(ghi_wm2, t_air_c, dc_mwp=60.0, ac_mw=50.0, noct_c=45.0,
             gamma_per_k=-0.0035, k_other=0.90, eta_inverter=0.98):
    """AC power of the PV plant (MW), limited by the inverter rating."""
    g = np.asarray(ghi_wm2, dtype=float)
    if (g < 0).any():
        raise ValueError("irradiance cannot be negative")
    t_cell = cell_temperature(g, t_air_c, noct_c)
    temp_factor = 1 + gamma_per_k * (t_cell - 25.0)
    p_dc = dc_mwp * g / 1000.0 * temp_factor * k_other
    return np.minimum(p_dc * eta_inverter, ac_mw)
# [end: pv]


# [start: wind]
def air_density(p_hpa, t_air_c):
    """Ideal gas: rho = p / (R T), dry air (kg/m3)."""
    t_k = np.asarray(t_air_c) + 273.15
    return np.asarray(p_hpa) * 100.0 / (R_DRY_AIR * t_k)


def wind_farm_mw(ws_ms, rho, curve_ms, curve_kw, turbines=12, loss=0.12):
    """Farm power (MW) from the power curve at the equivalent speed
    v_eq = v (rho / 1.225)^(1/3); one lumped loss fraction."""
    v = np.asarray(ws_ms, dtype=float)
    if (v < 0).any():
        raise ValueError("wind speed cannot be negative")
    v_eq = v * (np.asarray(rho) / RHO_REF) ** (1.0 / 3.0)
    return np.interp(v_eq, curve_ms, curve_kw) * turbines / 1000.0 * (1 - loss)
# [end: wind]


# [start: export]
def export_mw(pv_mw, wind_mw, limit_mw=100.0):
    """(export, curtailed) at the point of connection, both in MW."""
    gen = np.asarray(pv_mw) + np.asarray(wind_mw)
    exp = np.minimum(gen, limit_mw)
    return exp, gen - exp


def energy_mwh(power_mw, dt_h=1.0):
    return float(np.sum(power_mw) * dt_h)
# [end: export]
