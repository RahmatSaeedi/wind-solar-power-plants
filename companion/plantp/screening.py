"""Screening-level (first-pass) plant numbers, used in chapter 1.

These are deliberately crude models: one lumped loss factor per technology and
no geometry. They answer "roughly how much?" at the first decision gate and are
replaced step by step in later chapters (PV in chapters 10 and 15, wind in 11
and 15, storage in 19 and 20). Every factor below is an ASSUMPTION.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

#: assumed share of DC nameplate power that survives temperature, soiling,
#: mismatch and DC wiring at 1000 W/m2 (screening value)
PR_DC = 0.85
#: assumed inverter efficiency
ETA_INVERTER = 0.98
#: assumed lumped wind losses (wakes, availability, electrical)
WIND_LOSS = 0.12


def pv_dc_power_mw(ghi_wm2, dc_mwp: float, pr_dc: float = PR_DC):
    """DC power of the PV array from horizontal irradiance (screening model).

    P_dc = dc_mwp * (GHI / 1000 W/m2) * pr_dc
    """
    ghi = np.asarray(ghi_wm2, dtype=float)
    if (ghi < 0).any():
        raise ValueError("irradiance cannot be negative")
    return dc_mwp * ghi / 1000.0 * pr_dc


def pv_ac_power_mw(ghi_wm2, dc_mwp: float, ac_mw: float,
                   pr_dc: float = PR_DC, eta_inverter: float = ETA_INVERTER):
    """AC power of the PV plant from horizontal irradiance, limited by the inverters.

    P_ac = min(P_dc * eta_inverter, ac_mw)
    """
    p_dc = pv_dc_power_mw(ghi_wm2, dc_mwp, pr_dc)
    return np.minimum(p_dc * eta_inverter, ac_mw)


def pv_land_area_ha(dc_mwp: float, ha_per_mwp: float = 1.8) -> float:
    """Screening land take of a ground-mounted PV array.

    ha_per_mwp is a RULE OF THUMB (fixed-tilt arrays commonly need about
    1.5 to 2.5 ha per MWp, depending on latitude, row spacing and terrain).
    A layout study (chapter 14) replaces it.
    """
    if dc_mwp <= 0 or ha_per_mwp <= 0:
        raise ValueError("capacity and land ratio must be positive")
    return dc_mwp * ha_per_mwp


def wind_envelope_km2(turbines: int, rotor_diameter_m: float,
                      downwind_d: float = 7.0, crosswind_d: float = 4.0) -> float:
    """Screening area a wind farm needs when turbines sit downwind_d rotor
    diameters apart along the wind and crosswind_d across it.

    This is the envelope of the farm, not the land taken out of use: the
    permanent footprint (pads, roads, substation) is only a few percent of it.
    """
    if turbines <= 0 or rotor_diameter_m <= 0:
        raise ValueError("turbine count and rotor diameter must be positive")
    cell_m2 = (downwind_d * rotor_diameter_m) * (crosswind_d * rotor_diameter_m)
    return turbines * cell_m2 / 1e6


def wind_power_mw(wind_speed_ms, curve_speed_ms, curve_power_kw, turbines: int,
                  loss: float = WIND_LOSS):
    """Wind-farm power: power curve read by linear interpolation, times the
    number of turbines, minus one lumped loss fraction."""
    speed = np.asarray(wind_speed_ms, dtype=float)
    if (speed < 0).any():
        raise ValueError("wind speed cannot be negative")
    per_turbine_kw = np.interp(speed, curve_speed_ms, curve_power_kw)
    return per_turbine_kw * turbines / 1000.0 * (1.0 - loss)


def export_and_curtailment_mw(generation_mw, export_limit_mw: float):
    """Split generation into what the grid connection can take and what is cut off."""
    generation = np.asarray(generation_mw, dtype=float)
    export = np.minimum(generation, export_limit_mw)
    return export, generation - export


def capacity_factor(energy_mwh: float, rated_mw: float,
                    hours: float = 8760.0) -> float:
    """Energy actually produced divided by the energy at rated power all the time."""
    if rated_mw <= 0 or hours <= 0:
        raise ValueError("rated power and hours must be positive")
    return energy_mwh / (rated_mw * hours)


@dataclass
class ShiftResult:
    charged_mwh: float        # AC energy taken from the surplus
    delivered_mwh: float      # AC energy later delivered to the grid
    soc_mwh: np.ndarray       # stored energy at the end of each hour


def shift_surplus_with_battery(surplus_mw, headroom_mw, power_mw: float,
                               usable_energy_mwh: float, roundtrip_efficiency: float,
                               dt_h: float = 1.0) -> ShiftResult:
    """Greedy use of a battery for ONE role: store energy that would be curtailed
    and deliver it later, whenever the grid connection has room.

    surplus_mw   generation above the export limit in each step (would be lost)
    headroom_mw  unused export capacity in each step
    The battery never charges from the grid. Charging and discharging losses
    are equal: one-way efficiency = sqrt(round-trip efficiency).
    """
    surplus = np.asarray(surplus_mw, dtype=float)
    headroom = np.asarray(headroom_mw, dtype=float)
    if surplus.shape != headroom.shape:
        raise ValueError("surplus and headroom must have the same length")
    if not 0 < roundtrip_efficiency <= 1:
        raise ValueError("round-trip efficiency must be in (0, 1]")
    eta = math.sqrt(roundtrip_efficiency)
    soc = 0.0
    soc_trace = np.empty(len(surplus))
    charged = delivered = 0.0
    for k in range(len(surplus)):
        if surplus[k] > 0:
            p = min(surplus[k], power_mw, (usable_energy_mwh - soc) / (eta * dt_h))
            soc += p * eta * dt_h
            charged += p * dt_h
        elif headroom[k] > 0 and soc > 0:
            p = min(headroom[k], power_mw, soc * eta / dt_h)
            soc -= p / eta * dt_h
            delivered += p * dt_h
        soc = min(max(soc, 0.0), usable_energy_mwh)
        soc_trace[k] = soc
    return ShiftResult(charged, delivered, soc_trace)
