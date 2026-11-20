"""Materials, manufacturing and inspection arithmetic, chapter 4 (chapters 30, 40-48).

    tube_section          area, second moment and section modulus of a circular tube
    cantilever_tip        deflection of a cantilever with an end load
    basquin_cycles        cycles to failure on an S-N line N = N_ref (S_ref / S)^m
    miner_damage          Palmgren-Miner damage sum of a stress-range histogram
    critical_crack        crack length at which K = Y sigma sqrt(pi a) reaches K_IC
    faraday_loss_um_per_yr  metal thickness loss from a corrosion current density
    mismatch_stress       E d_alpha dT for a fully restrained bond
    dielectric_loss_w_per_m omega C V^2 tan(delta) per metre of cable (phase-to-earth V)
    weighted_scores       weighted-sum scores of a selection matrix
    cost_per_part         material + machine time + tooling / volume
    break_even_volume     volume at which two process routes cost the same
    fit_limits            minimum and maximum clearance of a hole/shaft pair
    roughness             Ra and Rq of a measured profile
    capability            Cp, Cpk and expected nonconforming parts per million
    bolt_torque           T = K F d (nut factor model)
    weld_heat_input       eta V I / v in kJ/mm
    arrhenius_factor      rate ratio exp(Ea/R (1/T1 - 1/T2))

Teaching models with their assumptions stated; real design follows the governing codes.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy.stats import norm

R_GAS = 8.314462618       # J/(mol K)
FARADAY = 96485.33212     # C/mol


@dataclass
class Section:
    area: float           # m2
    second_moment: float  # m4
    modulus: float        # m3 (elastic section modulus I / c)


def tube_section(d_outer: float, t: float) -> Section:
    d_in = d_outer - 2 * t
    if d_in <= 0:
        raise ValueError("wall too thick for the diameter")
    a = math.pi / 4 * (d_outer ** 2 - d_in ** 2)
    i = math.pi / 64 * (d_outer ** 4 - d_in ** 4)
    return Section(a, i, i / (d_outer / 2))


def cantilever_tip(force_n: float, length_m: float, e_pa: float, i_m4: float) -> float:
    return force_n * length_m ** 3 / (3 * e_pa * i_m4)


def basquin_cycles(s, s_ref: float, n_ref: float, m: float):
    return n_ref * (s_ref / np.asarray(s, dtype=float)) ** m


def miner_damage(ranges, counts, s_ref: float, n_ref: float, m: float) -> float:
    return float(np.sum(np.asarray(counts, dtype=float) / basquin_cycles(ranges, s_ref, n_ref, m)))


def critical_crack(k_ic: float, sigma: float, y: float = 1.12) -> float:
    """a_c = (K_IC / (Y sigma))^2 / pi (m); K in Pa sqrt(m), sigma in Pa."""
    return (k_ic / (y * sigma)) ** 2 / math.pi


def faraday_loss_um_per_yr(i_a_per_m2: float, molar_g: float, n_e: int,
                           density_g_cm3: float) -> float:
    """Uniform thickness loss from a corrosion current density (micrometres per year)."""
    mass_rate = i_a_per_m2 * molar_g / (n_e * FARADAY)            # g per m2 per s
    return mass_rate * 3600 * 24 * 365.25 / (density_g_cm3 * 1e6) * 1e6


def mismatch_stress(e_pa: float, d_alpha: float, d_t: float) -> float:
    return e_pa * d_alpha * d_t


def dielectric_loss_w_per_m(u0_v: float, f_hz: float, c_f_per_m: float, tan_d: float) -> float:
    return 2 * math.pi * f_hz * c_f_per_m * u0_v ** 2 * tan_d


def weighted_scores(matrix, weights) -> np.ndarray:
    w = np.asarray(weights, dtype=float)
    if not math.isclose(w.sum(), 1.0, rel_tol=1e-9):
        raise ValueError("weights must sum to 1")
    return np.asarray(matrix, dtype=float) @ w


def cost_per_part(volume, material: float, rate_per_h: float, hours: float,
                  tooling: float):
    v = np.asarray(volume, dtype=float)
    return material + rate_per_h * hours + tooling / v


def break_even_volume(route_a: tuple, route_b: tuple) -> float:
    """Each route: (material, rate_per_h, hours, tooling). Volume where costs are equal."""
    va = route_a[0] + route_a[1] * route_a[2]
    vb = route_b[0] + route_b[1] * route_b[2]
    if math.isclose(va, vb):
        raise ValueError("equal variable costs: no break-even")
    return (route_b[3] - route_a[3]) / (va - vb)


def fit_limits(hole: tuple, shaft: tuple) -> tuple[float, float, str]:
    """hole, shaft = (min, max) sizes. Returns (min clearance, max clearance, kind)."""
    c_min, c_max = hole[0] - shaft[1], hole[1] - shaft[0]
    kind = "clearance" if c_min >= 0 else ("interference" if c_max <= 0 else "transition")
    return c_min, c_max, kind


def roughness(profile) -> tuple[float, float]:
    z = np.asarray(profile, dtype=float)
    z = z - z.mean()
    return float(np.mean(np.abs(z))), float(math.sqrt(np.mean(z * z)))


def capability(data, lsl: float, usl: float) -> tuple[float, float, float]:
    x = np.asarray(data, dtype=float)
    mu, s = float(x.mean()), float(x.std(ddof=1))
    cp = (usl - lsl) / (6 * s)
    cpk = min(usl - mu, mu - lsl) / (3 * s)
    ppm = (norm.sf((usl - mu) / s) + norm.cdf((lsl - mu) / s)) * 1e6
    return cp, cpk, float(ppm)


def bolt_torque(k_nut: float, preload_n: float, d_m: float) -> float:
    return k_nut * preload_n * d_m


def weld_heat_input(volts: float, amps: float, speed_mm_s: float, eta: float = 0.8) -> float:
    return eta * volts * amps / speed_mm_s / 1000.0


def arrhenius_factor(ea_j_mol: float, t1_c: float, t2_c: float) -> float:
    """How many times faster a thermally activated process runs at t2 than at t1."""
    t1, t2 = t1_c + 273.15, t2_c + 273.15
    return math.exp(ea_j_mol / R_GAS * (1 / t1 - 1 / t2))


# ---- chapter 4, second part ----------------------------------------------------------
def von_mises(sigma: float, tau: float) -> float:
    """Equivalent stress for a normal stress with a shear stress: sqrt(s^2 + 3 t^2)."""
    return math.sqrt(sigma ** 2 + 3 * tau ** 2)


def euler_buckling(e_pa: float, i_m4: float, length_m: float, k_eff: float = 1.0) -> float:
    """Critical load pi^2 E I / (K L)^2 of an ideal elastic column."""
    return math.pi ** 2 * e_pa * i_m4 / (k_eff * length_m) ** 2


def rule_of_mixtures(e_f: float, e_m: float, v_f: float) -> tuple[float, float]:
    """Longitudinal (Voigt) and transverse (Reuss) modulus of a unidirectional composite."""
    if not 0 <= v_f <= 1:
        raise ValueError("fibre fraction must lie in [0, 1]")
    return v_f * e_f + (1 - v_f) * e_m, 1.0 / (v_f / e_f + (1 - v_f) / e_m)


def life_consumed(temps_c, hours, ref_c: float, ea_j_mol: float) -> float:
    """Hours of life at the reference temperature used up by a temperature history."""
    t = np.asarray(temps_c, dtype=float) + 273.15
    tr = ref_c + 273.15
    return float(np.sum(np.asarray(hours, dtype=float) * np.exp(ea_j_mol / R_GAS * (1 / tr - 1 / t))))


def halving_interval_k(ea_j_mol: float, t_c: float) -> float:
    """Temperature rise (K) near t_c that doubles an Arrhenius rate (halves a life)."""
    t = t_c + 273.15
    # solve exp(Ea/R (1/t - 1/(t + d))) = 2  ->  1/(t + d) = 1/t - R ln2 / Ea
    return 1.0 / (1.0 / t - R_GAS * math.log(2) / ea_j_mol) - t


def adiabatic_rise(cement_kg_m3: float, heat_kj_kg: float, rho_kg_m3: float = 2400.0,
                   c_kj_kgk: float = 1.0) -> float:
    """Temperature rise of fully insulated concrete from its heat of hydration (K)."""
    return cement_kg_m3 * heat_kj_kg / (rho_kg_m3 * c_kj_kgk)


def accept_probability(n: int, c: int, p) -> np.ndarray:
    """Operating characteristic of single sampling: P(accept) = P(defects in n <= c)."""
    from scipy.stats import binom
    return binom.cdf(c, n, np.asarray(p, dtype=float))


def stack(tolerances, method: str = "worst") -> float:
    t = np.abs(np.asarray(tolerances, dtype=float))
    if method == "worst":
        return float(t.sum())
    if method == "rss":
        return float(math.sqrt(np.sum(t ** 2)))
    raise ValueError("method is 'worst' or 'rss'")


# ---- chapter 4, fourth part ---------------------------------------------------------
def joint_load_factor(k_bolt: float, k_clamp: float) -> float:
    """Share of an external tensile load that reaches the bolt, k_b / (k_b + k_c)."""
    return k_bolt / (k_bolt + k_clamp)


def fillet_weld_stress(force_n: float, leg_m: float, length_m: float) -> float:
    """Average stress on the throat a = 0.707 s of a fillet weld."""
    return force_n / (0.7071 * leg_m * length_m)


def infusion_time(viscosity: float, porosity: float, length_m: float,
                  permeability: float, dp_pa: float) -> float:
    """Time for resin to flow a length L under a pressure difference (Darcy, 1-D):
    t = mu phi L^2 / (2 K dP)."""
    return viscosity * porosity * length_m ** 2 / (2 * permeability * dp_pa)
