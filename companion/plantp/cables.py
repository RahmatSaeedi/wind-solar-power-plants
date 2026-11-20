"""Chapter 24 - cables, overhead lines and switchgear duties.

Resistance at temperature, current rating with installation factors,
voltage drop, losses (instant and over a year), the adiabatic
short-circuit limit, charging current, the standing voltage on a
single-point-bonded sheath, a steady-state conductor temperature from a
thermal resistance, the economic choice of a conductor section, the sag
of a span, and switchgear duties (peak current, short-time withstand).

Teaching methods: real ratings come from the cable and switchgear makers
and the applicable standards (current-rating methods, short-circuit
calculation), applied by qualified engineers.
"""
from __future__ import annotations

import math

import numpy as np

F_HZ = 50.0


# [start: rating]
def r_at(r20: float, theta: float, alpha: float = 0.00393,
         skin: float = 1.0) -> float:
    """Resistance (any unit per length) at conductor temperature theta C:
    R = R20 (1 + alpha (theta - 20)) x skin factor for AC."""
    return r20 * (1 + alpha * (theta - 20.0)) * skin


def rating(i0: float, factors: dict) -> tuple[float, float]:
    """Current rating in place: the rating in reference conditions times
    every installation factor (depth, soil, ground temperature,
    grouping); returns (rating A, product of the factors)."""
    k = float(np.prod(list(factors.values())))
    return i0 * k, k
# [end: rating]


# [start: drop]
def drop_pct(i: float, km: float, r: float, x: float, pf: float,
             kv: float) -> float:
    """Three-phase voltage drop in % of the line voltage:
    dU = sqrt3 I L (R cos phi + X sin phi)."""
    s = math.sin(math.acos(pf))
    du = math.sqrt(3) * i * km * (r * pf + x * s)
    return du / (kv * 1e3) * 100


def loss_kw(i: float, r_ohm_km: float, km: float) -> float:
    """Joule loss of a three-phase circuit, kW."""
    return 3 * i ** 2 * r_ohm_km * km / 1e3


def annual_loss_mwh(i_series, r_ohm_km: float, km: float) -> float:
    """Energy lost in a year from an hourly current series (A)."""
    i = np.asarray(i_series, float)
    return float((3 * i ** 2 * r_ohm_km * km).sum() / 1e6)
# [end: drop]


# [start: fault]
def adiabatic_mm2(ik_ka: float, t_s: float, k: float) -> float:
    """Least section that carries ik for t without exceeding the
    insulation's short-circuit temperature: S = I sqrt(t) / k."""
    return ik_ka * 1e3 * math.sqrt(t_s) / k


def withstand_ka(mm2: float, t_s: float, k: float) -> float:
    """Short-circuit current a section of mm2 carries for t seconds."""
    return k * mm2 / math.sqrt(t_s) / 1e3


def peak_ka(ik_ka: float, x_over_r: float) -> float:
    """Peak (first-loop) short-circuit current: i_p = kappa sqrt2 Ik with
    kappa = 1.02 + 0.98 exp(-3 R/X)."""
    kappa = 1.02 + 0.98 * math.exp(-3.0 / x_over_r)
    return kappa * math.sqrt(2) * ik_ka


def short_time_ok(ik_ka: float, t_s: float, rated_ka: float,
                  rated_t: float) -> bool:
    """Equal-I2t check of a short-time withstand rating."""
    return ik_ka ** 2 * t_s <= rated_ka ** 2 * rated_t
# [end: fault]


# [start: cable]
def charging_a(kv: float, c_uf_km: float, km: float) -> float:
    """Charging current of a cable: U/sqrt3 x omega C L (A)."""
    return kv * 1e3 / math.sqrt(3) * 2 * math.pi * F_HZ * c_uf_km * 1e-6 * km


def sheath_v(i: float, s_mm: float, d_mm: float, length_m: float) -> float:
    """Standing voltage at the open end of a single-point-bonded sheath
    (trefoil, mean geometry): E = omega 2e-7 ln(2s/d) I L."""
    m = 2e-7 * math.log(2 * s_mm / d_mm)          # H/m
    return 2 * math.pi * F_HZ * m * i * length_m


def conductor_temp(i: float, r_ohm_m: float, t_amb: float,
                   r_th: float) -> float:
    """Steady conductor temperature with the Joule loss of one conductor
    (W/m) through a total thermal resistance r_th (K m/W); dielectric
    loss and mutual heating are left to the full method."""
    return t_amb + i ** 2 * r_ohm_m * r_th


def economic_section(options, i_series, km: float, price: float,
                     years: int, rate: float):
    """Present value of cost + losses for each (mm2, r_ohm_km, cost_k)
    option: losses priced at `price` u/MWh for `years` at `rate`."""
    af = (1 - (1 + rate) ** -years) / rate
    out = []
    for mm2, r, cost in options:
        e = annual_loss_mwh(i_series, r, km)
        out.append((mm2, cost, e, cost + e * price / 1e3 * af))
    return out
# [end: cable]


def sag_m(w_n_m: float, span_m: float, h_n: float) -> float:
    """Sag at mid-span of a level span (parabola): w L^2 / (8 H)."""
    return w_n_m * span_m ** 2 / (8 * h_n)
