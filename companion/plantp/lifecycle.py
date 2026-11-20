"""Lifecycle decision helpers (chapter 53).

Options compared on present value and equivalent annual cost with their
downtime, remaining life from a conditional Weibull, a degradation trend
with its interval, repowering energy, a sinking-fund provision for
decommissioning, a material and waste balance, and a footprint per kWh
with lognormal uncertainty. Teaching models on plain data, not a
financial, legal or environmental assessment.
"""
from __future__ import annotations

import math

import numpy as np


# [start: option]
def option_pv(capex: float, opex: float, lost_mwh: float, price: float,
              years: int, rate: float, salvage: float = 0.0) -> float:
    """Present cost of an option: capital now, a yearly cost and the
    energy it loses each year (valued at price), less salvage at the end."""
    af = (1 - (1 + rate) ** -years) / rate
    end = salvage / (1 + rate) ** years
    return capex + (opex + lost_mwh * price) * af - end


def eac(pv_cost: float, years: int, rate: float) -> float:
    """Equivalent annual cost of a present cost over a life."""
    return pv_cost * rate / (1 - (1 + rate) ** -years)
# [end: option]


# [start: remaining]
def conditional_reliability(t_now: float, dt, k: float, c: float):
    """P(survive dt more | survived t_now), Weibull shape k, scale c."""
    dt = np.asarray(dt, float)
    return np.exp(-(((t_now + dt) / c) ** k - (t_now / c) ** k))


def median_remaining(t_now: float, k: float, c: float) -> float:
    """Median remaining life of a unit that has survived t_now."""
    return c * ((t_now / c) ** k + math.log(2)) ** (1 / k) - t_now
# [end: remaining]


# [start: trend]
def trend(years, values, conf_z: float = 1.96) -> tuple:
    """Least-squares slope per year and its half-width (normal approx)."""
    x = np.asarray(years, float)
    y = np.asarray(values, float)
    b, a = np.polyfit(x, y, 1)
    res = y - (a + b * x)
    s = math.sqrt(float(np.sum(res ** 2)) / (x.size - 2))
    se = s / math.sqrt(float(np.sum((x - x.mean()) ** 2)))
    return float(b), float(conf_z * se)
# [end: trend]


# [start: provision]
def sinking_fund(target: float, years: int, rate: float) -> float:
    """Yearly payment that grows to target after years at rate."""
    return target * rate / ((1 + rate) ** years - 1)
# [end: provision]


# [start: waste]
def waste_balance(materials: dict) -> dict:
    """materials: name -> (tonnes, share recycled, share reused, hazardous?).
    Returns tonnes recycled, reused, landfilled and hazardous."""
    rec = sum(t * r for t, r, _, _ in materials.values())
    reu = sum(t * u for t, _, u, _ in materials.values())
    tot = sum(t for t, *_ in materials.values())
    haz = sum(t for t, _, _, h in materials.values() if h)
    return dict(total=tot, recycled=rec, reused=reu, landfill=tot - rec - reu,
                hazardous=haz)
# [end: waste]


# [start: footprint]
def footprint_mc(parts: dict, energy_mwh: float, n: int = 20_000,
                 seed: int = 53) -> np.ndarray:
    """parts: name -> (t CO2e median, coefficient of variation); lognormal
    draws summed, per kWh delivered (g CO2e/kWh)."""
    rng = np.random.default_rng(seed)
    tot = np.zeros(n)
    for med, cov in parts.values():
        sigma = math.sqrt(math.log(1 + cov ** 2))
        tot += rng.lognormal(math.log(med), sigma, n)
    return tot * 1e6 / (energy_mwh * 1e3)
# [end: footprint]
