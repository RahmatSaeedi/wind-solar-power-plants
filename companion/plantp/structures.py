"""Structures, foundations and mechanical loads (chapter 30).

Textbook forms a student can check by hand: wind speed with height,
dynamic pressure, peak gusts and drag; vortex shedding; axial buckling
of a thin cylinder with a knock-down factor; a bilinear S-N curve for a
welded detail; the effective area of a circular foundation under an
eccentric load and its rotational stiffness on an elastic half-space;
the tower frequency with a flexible foundation; pile uplift and the
lateral capacity of a short pile in sand; zinc life; thermal expansion;
an equivalent seismic base shear; bolt slip resistance; and the steel
area of a reinforced section.

These are teaching forms. Real structures are designed by qualified
engineers to the codes that apply on the project, with their partial
factors and checks; nothing here is a design.
"""
from __future__ import annotations

import math

G = 9.81


# [start: wind]
def wind_profile(v_ref: float, z_ref: float, z: float,
                 alpha: float = 0.14) -> float:
    """Mean wind speed at height z by the power law (m/s)."""
    return v_ref * (z / z_ref) ** alpha


def dynamic_pressure(v: float, rho: float = 1.225) -> float:
    """q = rho v^2 / 2 (Pa)."""
    return 0.5 * rho * v * v


def peak_speed(v_mean: float, ti: float, g_peak: float = 3.5) -> float:
    """Peak gust from mean speed and turbulence intensity (m/s)."""
    return v_mean * (1 + g_peak * ti)


def drag_force(q: float, cd: float, area: float) -> float:
    """F = q Cd A (N)."""
    return q * cd * area


def vortex_speed(f_hz: float, d_m: float, strouhal: float = 0.2) -> float:
    """Wind speed at which vortex shedding locks onto frequency f (m/s)."""
    return f_hz * d_m / strouhal
# [end: wind]


# [start: buckling]
def shell_buckling(e_pa: float, t_m: float, r_m: float,
                   knockdown: float) -> float:
    """Axial buckling stress of a thin cylinder, the classical value
    0.605 E t / r times a knock-down factor for imperfections (Pa)."""
    return knockdown * 0.605 * e_pa * t_m / r_m


def rankine(fy: float, s_el: float) -> float:
    """Strength when yield and elastic buckling interact (Rankine):
    1 / s = 1 / fy + 1 / s_el."""
    return 1 / (1 / fy + 1 / s_el)
# [end: buckling]


# [start: fatigue]
def sn_life(ds: float, ds_c: float, n_c: float = 2e6, m1: float = 3.0,
            n_d: float = 5e6, m2: float = 5.0) -> float:
    """Cycles to failure at stress range ds on a bilinear S-N curve:
    slope m1 through (n_c, ds_c) down to n_d, slope m2 below (no cut-off)."""
    ds_d = ds_c * (n_c / n_d) ** (1 / m1)
    if ds >= ds_d:
        return n_c * (ds_c / ds) ** m1
    return n_d * (ds_d / ds) ** m2
# [end: fatigue]


# [start: foundation]
def effective_area_circle(r: float, e: float) -> float:
    """Effective (compressed) area of a circular base of radius r under a
    load with eccentricity e < r:
    A' = 2 [r^2 acos(e/r) - e sqrt(r^2 - e^2)]."""
    if e >= r:
        return 0.0
    return 2 * (r * r * math.acos(e / r) - e * math.sqrt(r * r - e * e))


def foundation_pressure(v_kn: float, m_knm: float,
                        r: float) -> tuple[float, float, float]:
    """(eccentricity m, effective area m2, pressure kPa) of a circular base."""
    e = m_knm / v_kn
    a = effective_area_circle(r, e)
    return e, a, (v_kn / a if a > 0 else math.inf)


def rotational_stiffness(g_pa: float, r: float, nu: float) -> float:
    """Rocking stiffness of a rigid circular base on an elastic half-space
    K = 8 G r^3 / (3 (1 - nu)) (N m/rad)."""
    return 8 * g_pa * r ** 3 / (3 * (1 - nu))


def frequency_with_foundation(f_fixed: float, k_rot: float, m_top: float,
                              h: float) -> float:
    """First tower frequency on a rotational spring (Dunkerley):
    1/f^2 = 1/f_fixed^2 + 1/f_rot^2, f_rot = sqrt(K / (m h^2)) / 2 pi."""
    f_rot = math.sqrt(k_rot / (m_top * h * h)) / (2 * math.pi)
    return 1 / math.sqrt(1 / f_fixed ** 2 + 1 / f_rot ** 2)
# [end: foundation]


# [start: piles]
def pile_uplift(perimeter_m: float, length_m: float, skin_kpa: float,
                weight_kn: float = 0.0) -> float:
    """Uplift resistance of a pile: shaft friction plus its weight (kN)."""
    return perimeter_m * length_m * skin_kpa + weight_kn


def broms_lateral_sand(d_m: float, l_m: float, gamma: float, kp: float,
                       e_m: float) -> float:
    """Lateral capacity of a short free-head pile in sand (Broms):
    H = 0.5 gamma d L^3 Kp / (e + L) (kN), load at height e."""
    return 0.5 * gamma * d_m * l_m ** 3 * kp / (e_m + l_m)
# [end: piles]


def zinc_life(thickness_um: float, rate_um_yr: float) -> float:
    """Years until a zinc coating is consumed at a uniform rate."""
    return thickness_um / rate_um_yr


def thermal_expansion(alpha: float, length_m: float, dt: float) -> float:
    """Free change of length (m)."""
    return alpha * length_m * dt


def base_shear(mass_kg: float, sa_g: float, behaviour: float = 1.0) -> float:
    """Equivalent seismic base shear V = m g Sa / q (N)."""
    return mass_kg * G * sa_g / behaviour


def bolt_slip(n_bolts: int, mu: float, preload_n: float,
              surfaces: int = 1) -> float:
    """Slip resistance of a preloaded joint: n mu Fp per surface (N)."""
    return n_bolts * surfaces * mu * preload_n


def rebar_area(m_nm: float, d_m: float, f_yd_pa: float,
               lever: float = 0.9) -> float:
    """Tension steel for moment M with a lever arm of lever x d (m2)."""
    return m_nm / (f_yd_pa * lever * d_m)
