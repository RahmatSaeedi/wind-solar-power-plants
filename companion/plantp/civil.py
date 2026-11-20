"""Site investigation and civil works tools (chapter 29).

Textbook forms a student can check by hand: depth to a refractor from a
seismic line, bearing capacity factors and an ultimate bearing pressure,
elastic settlement, load spreading under a pad, the rational method
and Kirpich's time of concentration, Manning's formula, the soil-loss
equation, compaction and concrete acceptance statistics, well drawdown
(Cooper-Jacob), inflow to an open trench (Dupuit) and return levels of
annual maxima (Gumbel).

These are teaching forms. Foundations, slopes, drainage and water
supply are designed by qualified engineers to the codes that apply on
the project; correlations used here are screening tools only.
"""
from __future__ import annotations

import math

import numpy as np


# [start: refraction]
def refraction_depth(x_cross: float, v1: float, v2: float) -> float:
    """Depth (m) of a flat refractor from the crossover distance x_cross
    (m) of a two-layer seismic refraction line, velocities v1 < v2."""
    if v2 <= v1:
        raise ValueError("the lower layer must be faster (v2 > v1)")
    return x_cross / 2 * math.sqrt((v2 - v1) / (v2 + v1))
# [end: refraction]


# [start: bearing]
def bearing_factors(phi_deg: float) -> tuple[float, float, float]:
    """Bearing capacity factors (Nc, Nq, Ngamma) for a friction angle
    (Nq and Nc of Prandtl-Reissner, Ngamma of Vesic)."""
    phi = math.radians(phi_deg)
    nq = (math.exp(math.pi * math.tan(phi))
          * math.tan(math.pi / 4 + phi / 2) ** 2)
    nc = (nq - 1) / math.tan(phi) if phi > 0 else 5.14
    ng = 2 * (nq + 1) * math.tan(phi)
    return nc, nq, ng


def bearing_square(c_kpa: float, phi_deg: float, gamma: float,
                   b_m: float, depth_m: float) -> float:
    """Ultimate bearing pressure (kPa) of a square footing, Terzaghi's
    shape factors: 1.3 c Nc + q Nq + 0.4 gamma B Ngamma."""
    nc, nq, ng = bearing_factors(phi_deg)
    q = gamma * depth_m
    return 1.3 * c_kpa * nc + q * nq + 0.4 * gamma * b_m * ng
# [end: bearing]


def elastic_settlement(q_kpa: float, b_m: float, e_kpa: float,
                       nu: float = 0.3, influence: float = 0.88) -> float:
    """Immediate settlement (m) of a flexible footing on an elastic soil:
    s = q B (1 - nu^2) I / E."""
    return q_kpa * b_m * (1 - nu ** 2) * influence / e_kpa


def spread_pressure(load_kn: float, b_m: float, l_m: float,
                    z_m: float) -> float:
    """Pressure (kPa) at depth z under a b x l pad by 2:1 load spreading."""
    return load_kn / ((b_m + z_m) * (l_m + z_m))


# [start: drainage]
def rational_peak(c: float, i_mm_h: float, area_km2: float) -> float:
    """Peak runoff (m3/s) by the rational method, Q = 0.278 C i A."""
    return 0.278 * c * i_mm_h * area_km2


def kirpich_tc(length_m: float, slope: float) -> float:
    """Time of concentration (min) of a small catchment (Kirpich)."""
    return 0.0195 * length_m ** 0.77 * slope ** -0.385


def manning_q(n: float, area_m2: float, perimeter_m: float,
              slope: float) -> float:
    """Flow (m3/s) in an open channel or a pipe running full (Manning)."""
    r = area_m2 / perimeter_m
    return area_m2 * r ** (2 / 3) * math.sqrt(slope) / n


def pipe_full_q(n: float, d_m: float, slope: float) -> float:
    """Full-bore capacity (m3/s) of a circular culvert or pipe."""
    return manning_q(n, math.pi * d_m ** 2 / 4, math.pi * d_m, slope)
# [end: drainage]


def usle(r: float, k: float, ls: float, c: float, p: float) -> float:
    """Average annual soil loss (t/ha/yr) by the universal soil-loss
    equation A = R K LS C P."""
    return r * k * ls * c * p


def ls_factor(length_m: float, slope_pct: float) -> float:
    """Slope length and steepness factor (Wischmeier-Smith form)."""
    theta = math.atan(slope_pct / 100)
    m = (0.5 if slope_pct >= 5 else 0.4 if slope_pct >= 3.5
         else 0.3 if slope_pct >= 1 else 0.2)
    s = math.sin(theta)
    return (length_m / 22.13) ** m * (65.41 * s * s + 4.56 * s + 0.065)


# [start: acceptance]
def lot_accept(values, limit: float, k: float = 0.0) -> tuple[bool, float]:
    """Accept a lot if mean - k s >= limit; returns (accepted, mean - k s)."""
    v = np.asarray(values, float)
    s = float(v.std(ddof=1)) if len(v) > 1 else 0.0
    m = float(v.mean()) - k * s
    return m >= limit, m


def characteristic(values, k: float = 1.645) -> float:
    """Characteristic value (5 % fractile, normal) of test results."""
    v = np.asarray(values, float)
    return float(v.mean() - k * v.std(ddof=1))
# [end: acceptance]


# [start: water]
def cooper_jacob(q_m3_s: float, t_m2_s: float, s_store: float,
                 r_m: float, t_s: float) -> float:
    """Drawdown (m) at distance r after pumping time t (Cooper-Jacob)."""
    u = 2.25 * t_m2_s * t_s / (r_m ** 2 * s_store)
    return q_m3_s / (4 * math.pi * t_m2_s) * math.log(u)


def trench_inflow(k_m_s: float, h_m: float, hw_m: float,
                  radius_m: float) -> float:
    """Inflow (m3/s per metre of trench, one side) to an open trench
    lowering water from h to hw over a radius of influence (Dupuit)."""
    return k_m_s * (h_m ** 2 - hw_m ** 2) / (2 * radius_m)
# [end: water]


# [start: gumbel]
def gumbel_return(mu: float, beta: float, years: float) -> float:
    """Return level of annual maxima for a return period in years."""
    return mu - beta * math.log(-math.log(1 - 1 / years))
# [end: gumbel]
