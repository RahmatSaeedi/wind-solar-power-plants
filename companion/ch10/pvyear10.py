"""The PV array of Plant P through the data-pack year with the models of
chapter 10: plane-of-array irradiance (Hay-Davies, sun averaged over each
hour as in the data pack), incidence-angle losses, Faiman module
temperature with wind at module height, and the fitted single-diode model
for each string.

Geometry and losses are teaching assumptions (A-183): fixed tables facing
south, tilt 25 deg, two modules high in portrait, ground coverage ratio
0.40, albedo 0.2; 2 % DC wiring and 1 % mismatch losses; soiling handled in
section D.
"""
from __future__ import annotations

import math
from functools import lru_cache

import numpy as np

from companion.ch10 import common  # noqa: F401  (puts plantp on the path)
from plantp import datapack, pvcell as pc, solar

LAT = 34.0
N_MOD = 26
N_STRINGS = 4200                   # 10 inverters x 420 strings (D-013)
TILT, AZ = 25.0, 180.0
DC_LOSS = 0.02 + 0.01              # wiring + mismatch (A-183)


@lru_cache(maxsize=1)
def ref_sdm() -> pc.SDM:
    return pc.fit(pc.PVM_550_DS)


@lru_cache(maxsize=8)
def geometry(tilt: float = TILT, az: float = AZ):
    """Hourly mean cos(incidence) and cos(zenith) over six sub-steps."""
    idx = np.arange(8760)
    n = idx // 24 + 1
    hour = idx % 24
    cz_sum = np.zeros(8760)
    ci_sum = np.zeros(8760)
    for s in (np.arange(6) + 0.5) / 6:
        st = solar.solar_time(hour + s, n)
        el, azs = solar.sun_position(LAT, n, st)
        up = el > 0
        cz = np.where(up, np.sin(np.radians(el)), 0.0)
        ci = np.where(up, np.clip(solar.incidence_cos(el, azs, tilt, az), 0, None), 0.0)
        cz_sum += cz
        ci_sum += ci
    return ci_sum / 6, cz_sum / 6, n


@lru_cache(maxsize=8)
def poa(tilt: float = TILT, az: float = AZ, albedo: float = 0.2):
    """Hourly POA components and the effective irradiance after IAM."""
    h = datapack.load_hourly()
    ghi = h["ghi_wm2"].to_numpy(dtype=float)
    dni = h["dni_wm2"].to_numpy(dtype=float)
    dhi = h["dhi_wm2"].to_numpy(dtype=float)
    ci, cz, n = geometry(tilt, az)
    g0n = 1361.0 * (1 + 0.033 * np.cos(2 * np.pi * n / 365))
    beam, sky, ground = pc.poa_hay_davies(ghi, dni, dhi, ci, cz, g0n, tilt,
                                          albedo)
    eff = beam * pc.iam_ashrae(ci) + (sky + ground) * 0.95     # diffuse IAM
    return {"ghi": ghi, "beam": beam, "sky": sky, "ground": ground,
            "poa": beam + sky + ground, "eff": eff}


@lru_cache(maxsize=8)
def strings(tilt: float = TILT, n_mod: int = N_MOD):
    """Hourly string MPP voltage and power, cell temperature."""
    h = datapack.load_hourly()
    p = poa(tilt)
    wind2 = pc.wind_at_height(h["ws_100m_ms"].to_numpy(dtype=float), 100, 2)
    tc = pc.faiman(h["t_air_c"].to_numpy(dtype=float), p["poa"], wind2)
    ref = ref_sdm()
    v = np.zeros(8760)
    pw = np.zeros(8760)
    for k in np.flatnonzero(p["eff"] >= 10):
        m = pc.at_conditions(ref, p["eff"][k], tc[k], pc.PVM_550_DS.alpha_isc)
        vm, _, pm = m.mpp()
        v[k], pw[k] = n_mod * vm, n_mod * pm
    return {"v_mp": v, "p_string": pw, "t_cell": tc, "poa": p["poa"],
            "eff": p["eff"]}


def dc_power(tilt: float = TILT, n_strings: int = N_STRINGS):
    """Array DC power at the inverters (W)."""
    return strings(tilt)["p_string"] * n_strings * (1 - DC_LOSS)
