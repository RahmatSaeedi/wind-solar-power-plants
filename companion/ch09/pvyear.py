"""The PV array of Plant P through the data-pack year, hour by hour, as
chapter 9 needs it: string MPP voltage and power, array DC power, and the
inverter's response (DC window, efficiency curve, derating, clipping).

Simple model of this chapter (A-153): horizontal irradiance stands in for
the plane of array, NOCT cell temperature, 3 % DC losses before the
inverter; chapters 10 and 15 build the full yield model.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

from companion.ch09 import common  # noqa: F401  (puts plantp on the path)
from plantp import datapack, mppt as mp, pe

N_MOD = 26                     # modules per string (A-015, D-002)
N_STRINGS = 4195              # 60 MWp / (26 x 550 W)
DC_LOSS = 0.03                 # A-153
N_INV, P_INV = 10, 5.0e6       # 10 inverters of 5 MW (A-101)
ELEV_M = 1200.0                # site elevation (A-002)


@lru_cache(maxsize=1)
def hourly() -> dict:
    """Hourly arrays: g, t_air, t_cell, v_mp (string), p_dc (array, W),
    and the four-point string curves (None at night)."""
    h = datapack.load_hourly()
    g = h["ghi_wm2"].to_numpy(dtype=float)
    ta = h["t_air_c"].to_numpy(dtype=float)
    tc = mp.cell_temperature(ta, g)
    v = np.zeros(len(g))
    p = np.zeros(len(g))
    curves = [None] * len(g)
    for k in np.flatnonzero(g >= 20):
        c = mp.PVM_550.at(g[k], tc[k], N_MOD)
        v[k], p[k] = c.mpp(400)
        curves[k] = c
    return {"g": g, "t_air": ta, "t_cell": tc, "v_mp": v,
            "p_dc": p * N_STRINGS * (1 - DC_LOSS), "curves": curves}


def window_loss(v_ac: float, headroom: float = 0.1) -> tuple[int, float, float]:
    """Hours below the DC window of an inverter with AC voltage v_ac, energy
    lost by running at the window floor instead of the MPP (MWh), and the
    share of the array's DC energy."""
    d = hourly()
    v_min = pe.vdc_min(v_ac, headroom=headroom)
    hours, lost = 0, 0.0
    for k in np.flatnonzero(d["v_mp"] > 0):
        if d["v_mp"][k] < v_min:
            c = d["curves"][k]
            hours += 1
            share = 1 - float(c.p(v_min)) / (d["v_mp"][k] * float(c.i(d["v_mp"][k])))
            lost += d["p_dc"][k] * share
    return hours, lost / 1e6, lost / d["p_dc"].sum()


def inverter_year(coeffs, derate: bool = True, clip_w: float = N_INV * P_INV):
    """AC output, inverter losses, derating and clipping over the year (W
    arrays, whole plant, all inverters sharing the power equally)."""
    d = hourly()
    p_dc = d["p_dc"]
    rated = clip_w
    k_t = (pe.derating(d["t_air"], ELEV_M) if derate
           else np.ones(len(p_dc)))
    # efficiency curve is per unit of AC output; solve P_ac + loss = P_dc
    p_ac = np.zeros(len(p_dc))
    for k in np.flatnonzero(p_dc > 0):
        x = p_dc[k] / rated
        c0, c1, c2 = coeffs                        # loss = c0 + c1 y + c2 y^2
        # y + c0 + c1 y + c2 y^2 = x  ->  c2 y^2 + (1 + c1) y + c0 - x = 0
        disc = (1 + c1) ** 2 - 4 * c2 * (c0 - x)
        y = (-(1 + c1) + np.sqrt(disc)) / (2 * c2) if x > c0 else 0.0
        p_ac[k] = y * rated
    p_clip = np.minimum(p_ac, rated)                 # rating limit
    p_out = np.minimum(p_clip, rated * k_t)          # temperature derating
    return {"p_dc": p_dc, "p_ac": p_ac, "p_out": p_out,
            "loss": p_dc - p_ac, "clip": p_ac - p_clip,
            "derate": p_clip - p_out}
