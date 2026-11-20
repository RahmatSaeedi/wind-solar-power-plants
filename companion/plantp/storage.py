"""Battery storage (chapter 19): open-circuit voltage curves of two
teaching chemistries, a Thevenin cell (R0 plus one RC branch), discharge
at a C-rate, round-trip efficiency from I^2R, the build-up from cells to
the system, coulomb counting with a sensor bias and an OCV reset,
calendar and cycle fade, a lumped container heat balance, the voltage
drift of a self-discharging cell, a teaching propagation chain, sizing
for end of life, augmentation and a warranty check.

Cell quantities in V, A, Ah, ohm; plant quantities in MW, MWh. Every
parameter is a teaching value (A-290 onwards), not a product's data.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


# ------------------------------------------------------------ OCV
# [start: ocv]
def ocv(soc, chem: str = "LFP"):
    """Open-circuit voltage (V) of a teaching cell against state of
    charge 0..1. LFP has a long flat plateau; NMC a steady slope."""
    s = np.clip(np.asarray(soc, float), 0.0, 1.0)
    if chem == "LFP":
        return (3.20 + 0.10 * s - 0.35 * np.exp(-25.0 * s)
                + 0.25 * np.exp(-25.0 * (1.0 - s)))
    if chem == "NMC":
        return 3.40 + 0.75 * s - 0.25 * np.exp(-20.0 * s) + 0.05 * s ** 8
    raise ValueError(f"unknown chemistry {chem}")
# [end: ocv]


def soc_from_ocv(v, chem: str = "LFP"):
    """Inverse of ocv() by interpolation on a fine grid."""
    grid = np.linspace(0.0, 1.0, 2001)
    return np.interp(v, ocv(grid, chem), grid)


def ocv_slope(soc, chem: str = "LFP", h: float = 1e-4):
    """dV/dSOC (V per unit SOC) of the teaching curve."""
    return (ocv(np.asarray(soc) + h, chem) - ocv(np.asarray(soc) - h, chem)) / (2 * h)


# ------------------------------------------------------------ cell model
# [start: cell]
@dataclass
class Cell:
    q_ah: float = 314.0        # capacity, Ah
    r0: float = 0.00025        # series resistance, ohm
    r1: float = 0.00015        # polarisation resistance, ohm
    c1: float = 200000.0       # polarisation capacitance, F (tau 30 s)
    chem: str = "LFP"
    v_min: float = 2.5
    v_max: float = 3.6


def simulate(cell: Cell, current, dt_s: float, soc0: float):
    """Terminal voltage and SOC for a current series in A (+ discharge,
    - charge), one value every dt_s seconds."""
    soc, v1 = soc0, 0.0
    a = math.exp(-dt_s / (cell.r1 * cell.c1))
    vs, ss = [], []
    for i in np.asarray(current, float):
        soc -= i * dt_s / 3600.0 / cell.q_ah
        v1 = a * v1 + (1.0 - a) * cell.r1 * i
        vs.append(float(ocv(soc, cell.chem)) - cell.r0 * i - v1)
        ss.append(soc)
    return np.array(vs), np.array(ss)
# [end: cell]


def discharge(cell: Cell, c_rate: float, soc0: float = 1.0, dt_s: float = 10.0):
    """Constant-current discharge until v_min or empty: Ah and Wh
    delivered and the mean voltage."""
    i = c_rate * cell.q_ah
    n = int(3600.0 / c_rate / dt_s * 1.2) + 1
    v, s = simulate(cell, np.full(n, i), dt_s, soc0)
    stop = np.argmax((v < cell.v_min) | (s <= 0.0)) or n
    ah = i * dt_s * stop / 3600.0
    wh = float(np.sum(v[:stop]) * i * dt_s / 3600.0)
    return {"ah": ah, "wh": wh, "v_mean": wh / ah if ah else 0.0,
            "v": v[:stop], "soc": s[:stop]}


def round_trip(cell: Cell, c_rate: float, lo: float = 0.1, hi: float = 0.9,
               dt_s: float = 10.0) -> float:
    """DC round-trip efficiency of the cell between two SOC limits at
    one C-rate both ways (energy out over energy in)."""
    i = c_rate * cell.q_ah
    n = int((hi - lo) * 3600.0 / c_rate / dt_s)
    v_c, _ = simulate(cell, np.full(n, -i), dt_s, lo)
    v_d, _ = simulate(cell, np.full(n, i), dt_s, hi)
    return float(v_d.sum() / v_c.sum())


# ------------------------------------------------------------ build-up
# [start: buildup]
def build_up(cell: Cell, v_nom: float, s_module: int, m_rack: int,
             r_container: int, containers: int) -> dict:
    """Voltages and energies from the cell to the system: modules of
    cells in series, racks of modules in series, containers of racks in
    parallel."""
    cells_rack = s_module * m_rack
    e_cell = cell.q_ah * v_nom / 1000.0                 # kWh
    return {"module_v": s_module * v_nom,
            "module_kwh": s_module * e_cell,
            "rack_v_nom": cells_rack * v_nom,
            "rack_v_max": cells_rack * cell.v_max,
            "rack_v_min": cells_rack * cell.v_min,
            "rack_kwh": cells_rack * e_cell,
            "container_mwh": r_container * cells_rack * e_cell / 1000.0,
            "system_mwh": containers * r_container * cells_rack
            * e_cell / 1000.0,
            "cells": containers * r_container * cells_rack}
# [end: buildup]


# ------------------------------------------------------------ SOC
# [start: soc]
def coulomb_count(current, dt_s: float, q_ah: float, soc0: float,
                  bias_a: float = 0.0, gain: float = 1.0):
    """SOC estimated by integrating a measured current that carries a
    gain error and an offset (bias)."""
    meas = gain * np.asarray(current, float) + bias_a
    return soc0 - np.cumsum(meas) * dt_s / 3600.0 / q_ah
# [end: soc]


# ------------------------------------------------------------ fade
# [start: fade]
def calendar_fade(years, temp_c: float, soc_mean: float,
                  k25: float = 0.02, ea_ev: float = 0.5):
    """Capacity lost in storage: k(T, SOC) * sqrt(t), Arrhenius in
    temperature, more at a high mean SOC (teaching)."""
    kb = 8.617e-5                                     # eV/K
    k = k25 * math.exp(ea_ev / kb * (1 / 298.15 - 1 / (temp_c + 273.15)))
    return k * (0.6 + 0.8 * soc_mean) * np.sqrt(np.asarray(years, float))


def cycle_fade(cycles, n100: float = 4000.0, k: float = 1.3,
               loss_at_life: float = 0.2) -> float:
    """Capacity lost by cycling: each (depth, count) uses count/N(depth)
    of a life, N(depth) = n100 * depth**-k; one life = loss_at_life."""
    used = sum(c / (n100 * max(d, 1e-3) ** -k) for d, c in cycles if d > 0)
    return loss_at_life * used
# [end: fade]


# ------------------------------------------------------------ thermal
def container_heat(t_amb, q_batt_kw, ua_kw_k: float, c_kwh_k: float,
                   hvac_kw: float, setpoint: float = 25.0,
                   solar_kw=0.0, aux_kw: float = 3.0, dt_h: float = 1.0):
    """Hourly heat balance of a container: battery heat, auxiliaries,
    solar gain and the envelope against an HVAC of limited capacity.
    Returns the inside temperature and the heat the HVAC removed."""
    t_amb = np.asarray(t_amb, float)
    q = np.broadcast_to(np.asarray(q_batt_kw, float), t_amb.shape)
    sol = np.broadcast_to(np.asarray(solar_kw, float), t_amb.shape)
    t, temps, rem = setpoint, [], []
    for k in range(len(t_amb)):
        gain = q[k] + aux_kw + sol[k] + ua_kw_k * (t_amb[k] - t)
        want = gain + c_kwh_k * (t - setpoint) / dt_h
        r = min(max(want, 0.0), hvac_kw)
        t += dt_h * (gain - r) / c_kwh_k
        temps.append(t)
        rem.append(r)
    return np.array(temps), np.array(rem)


# ------------------------------------------------------------ defects
# [start: drift]
def ocv_drift_mv(leak_ma: float, q_ah: float, days: float, soc0: float,
                 chem: str = "LFP") -> float:
    """Drop of open-circuit voltage (mV) of a cell resting for some days
    with a self-discharge current leak_ma."""
    d_soc = leak_ma / 1000.0 * 24.0 * days / q_ah
    return 1000.0 * float(ocv(soc0, chem) - ocv(soc0 - d_soc, chem))
# [end: drift]


# [start: chain]
def chain_expected(n_cells: int, p_cell: float, n_modules: int,
                   p_module: float) -> dict:
    """Teaching abstraction of propagation: a cell in the middle of a
    module fails; each neighbour follows with probability p_cell (one
    line of cells); a whole module passes it to the next module with
    probability p_module. Expected cells and modules involved. Not a
    design method: evidence comes from tests of the real product."""
    half = n_cells // 2
    cells = 1.0 + 2.0 * sum(p_cell ** k for k in range(1, half + 1))
    reach_end = p_cell ** half                   # propagation reaches an edge
    mods = 1.0 + 2.0 * sum((reach_end * p_module) ** k
                           for k in range(1, n_modules // 2 + 1))
    return {"cells_in_module": cells, "modules": mods}
# [end: chain]


# ------------------------------------------------------------ sizing
# [start: sizing]
def size_nominal(e_poc_mwh: float, window: float, eta_out: float,
                 aux_share: float, soh_eol: float) -> float:
    """Nominal energy at the beginning of life (MWh) so that at the end
    of life the battery still delivers e_poc_mwh at the POC in one
    discharge: e_nom = e / (window * eta_out * (1 - aux) * soh_eol)."""
    return e_poc_mwh / (window * eta_out * (1.0 - aux_share) * soh_eol)


def augmentation(e_nom: float, need_usable: float, window: float,
                 fade_per_year, years: int, step: float):
    """Years and sizes of additions that keep usable energy at or above
    need_usable when capacity fades; additions fade from new."""
    blocks = [(0, e_nom)]
    adds = []
    for y in range(years + 1):
        usable = sum(e * window * (1.0 - fade_per_year(y - y0))
                     for y0, e in blocks)
        while usable < need_usable:
            blocks.append((y, step))
            adds.append(y)
            usable += step * window
    return adds, blocks
# [end: sizing]


# [start: warranty]
def warranty_check(throughput_mwh: float, efc: float, soc_mean: float,
                   t_max: float, limits: dict) -> list:
    """Compare a year of operation with warranty limits; each item is
    (name, value, limit, ok)."""
    rows = [("throughput MWh/yr", throughput_mwh, limits["throughput"],
             throughput_mwh <= limits["throughput"]),
            ("equivalent full cycles/yr", efc, limits["efc"],
             efc <= limits["efc"]),
            ("mean SOC", soc_mean, limits["soc_mean"],
             soc_mean <= limits["soc_mean"]),
            ("cell temperature max C", t_max, limits["t_max"],
             t_max <= limits["t_max"])]
    return rows
# [end: warranty]
