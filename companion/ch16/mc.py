"""Chapter 16 - Monte Carlo of the Plant P net energy: every budget part
is a multiplicative factor on its technology (or on the net for the
plant parts), the year-to-year terms are a correlated pair averaged over
n years, and each draw runs the plant end of model 15.1 (losses, own
use, export limit, outages), so non-linear effects stay in.

Used by lab_d and lab_e; seeds fixed.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch16 import sources as src
from companion.ch15 import sources as s15
from plantp import yieldmodel as ym, yieldrisk as yr


# [start: mc]
def draw_factors(parts, n: int, rng) -> np.ndarray:
    """Product of the parts' factors, one value per draw."""
    f = np.ones(n)
    for p in parts:
        f *= yr.sample(p.kind, p.u, n, rng)
    return f


def iav_pair(n: int, years: int, rng):
    """Mean of `years` correlated wind/PV year factors, per draw."""
    b = src.base()
    r = b["r_iav"]
    z1 = rng.standard_normal((n, years))
    z2 = r * z1 + math.sqrt(1 - r * r) * rng.standard_normal((n, years))
    fw = 1 + b["iav_w"] * z1.mean(axis=1)
    fp = 1 + b["iav_p"] * z2.mean(axis=1)
    return fw, fp


def net_draws(n: int, years: int = 1, seed: int = 160, pv_scale=1.0,
              parts=None):
    """Net energy at the POC (GWh) for n draws."""
    rng = np.random.default_rng(seed)
    wind, pv, plant = parts or (src.WIND, src.PV, src.PLANT)
    fw = draw_factors(wind, n, rng)
    fp = draw_factors(pv, n, rng)
    fpl = draw_factors(plant, n, rng)
    iw, ip = iav_pair(n, years, rng)
    r = src.base()["r"]
    cfg = s15.ModelConfig()
    out = np.empty(n)
    for k in range(n):
        _, net = ym.plant_end(r["w_av"] * fw[k] * iw[k],
                              r["pv_av"] * pv_scale * fp[k] * ip[k],
                              cfg, r["outage"])
        out[k] = net.sum() / 1e3 * fpl[k]
    return out
# [end: mc]
