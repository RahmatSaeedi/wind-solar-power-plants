"""Physics for plant engineering, chapter 4 (used again in chapters 6-13, 24-30).

    air_density            ideal gas, dry air or with humidity (virtual temperature)
    standard_pressure      ISA-style barometric pressure at an elevation
    rotor_thrust           F = 1/2 rho A v^2 C_T
    betz_cp, betz_ct       actuator-disc power and thrust coefficients for induction a
    shear_exponent         power-law exponent from two heights
    log_law_speed          neutral logarithmic profile with roughness length z0
    pv_cell_temp_noct      NOCT-style module temperature
    expansion              L alpha dT
    conductor_temperature  steady temperature with R(T) = R20 (1 + alpha (T - 20))
    coax_field             electric field in a coaxial (cable) insulation
    parallel_force_per_m   force between two long parallel conductors
    core_flux_density      transformer EMF equation solved for B
    photon_energy_ev       E = h c / lambda
    planck_fraction_above  share of blackbody power at photon energies above a band gap
    fresnel_reflectance    unpolarised reflectance at a smooth interface
    cantilever_f1          first natural frequency of a uniform cantilever
    spl_at_distance        sound pressure level from sound power, spherical spreading

SI units unless a name says otherwise. Teaching models: each states its assumptions.
"""
from __future__ import annotations

import math

import numpy as np
from scipy import integrate

R_DRY = 287.05          # J/(kg K), specific gas constant of dry air
G0 = 9.80665            # m/s2
MU0 = 4e-7 * math.pi    # H/m (to the precision used in this book)
H_PLANCK = 6.62607015e-34
C_LIGHT = 299_792_458.0
K_BOLTZ = 1.380649e-23
Q_E = 1.602176634e-19
SIGMA_SB = 5.670374419e-8


def saturation_vapour_pressure_hpa(t_c):
    """Magnus-type approximation (Tetens), hPa, for -40..50 C."""
    t_c = np.asarray(t_c, dtype=float)
    return 6.1078 * np.exp(17.27 * t_c / (t_c + 237.3))


def air_density(p_hpa, t_c, rh: float | None = None):
    """Density in kg/m3 from pressure (hPa) and temperature (C); rh in 0..1 optional."""
    t_k = np.asarray(t_c, dtype=float) + 273.15
    p = np.asarray(p_hpa, dtype=float) * 100.0
    if rh is None:
        return p / (R_DRY * t_k)
    e = rh * saturation_vapour_pressure_hpa(t_c) * 100.0
    t_v = t_k / (1.0 - 0.378 * e / p)                 # virtual temperature
    return p / (R_DRY * t_v)


def standard_pressure(z_m, p0_hpa: float = 1013.25, t0_k: float = 288.15,
                      lapse: float = 0.0065):
    """Troposphere with a constant lapse rate: p = p0 (1 - L z / T0)^(g / (R L))."""
    z = np.asarray(z_m, dtype=float)
    return p0_hpa * (1.0 - lapse * z / t0_k) ** (G0 / (R_DRY * lapse))


def rotor_thrust(rho, area_m2, v, ct):
    return 0.5 * rho * area_m2 * np.asarray(v, dtype=float) ** 2 * ct


def betz_cp(a):
    a = np.asarray(a, dtype=float)
    return 4.0 * a * (1.0 - a) ** 2


def betz_ct(a):
    a = np.asarray(a, dtype=float)
    return 4.0 * a * (1.0 - a)


def shear_exponent(v1, z1: float, v2, z2: float):
    return np.log(np.asarray(v2, dtype=float) / np.asarray(v1, dtype=float)) / math.log(z2 / z1)


def log_law_speed(v_ref, z_ref: float, z, z0: float):
    return np.asarray(v_ref, dtype=float) * np.log(np.asarray(z, dtype=float) / z0) / math.log(z_ref / z0)


def pv_cell_temp_noct(t_amb_c, g_wm2, noct_c: float = 45.0):
    """T_cell = T_amb + (NOCT - 20) G / 800 (NOCT conditions: 800 W/m2, 20 C, 1 m/s)."""
    return np.asarray(t_amb_c, dtype=float) + (noct_c - 20.0) * np.asarray(g_wm2, dtype=float) / 800.0


def expansion(length_m, alpha_per_k, d_t):
    return length_m * alpha_per_k * d_t


def conductor_temperature(current_a, r20_ohm, alpha_r, h_w_m2k, area_m2, t_amb_c):
    """Steady temperature of a conductor cooled by h A (convection + linearised radiation).

    Energy balance: I^2 R20 (1 + alpha (T - 20)) = h A (T - T_amb). Linear in T:
    T - T_amb = k (1 + alpha (T_amb - 20)) / (1 - k alpha), k = I^2 R20 / (h A).
    Returns (T, k alpha); k alpha >= 1 means no steady state (thermal runaway)."""
    k = current_a ** 2 * r20_ohm / (h_w_m2k * area_m2)
    ka = k * alpha_r
    if ka >= 1.0:
        return math.inf, ka
    return t_amb_c + k * (1.0 + alpha_r * (t_amb_c - 20.0)) / (1.0 - ka), ka


def coax_field(v, r, r_in: float, r_out: float):
    """E(r) = V / (r ln(r_out / r_in)) for r_in <= r <= r_out (V/m)."""
    return v / (np.asarray(r, dtype=float) * math.log(r_out / r_in))


def parallel_force_per_m(i1, i2, d_m):
    """F/L = mu0 i1 i2 / (2 pi d): attractive for currents in the same direction (N/m)."""
    return MU0 * np.asarray(i1, dtype=float) * np.asarray(i2, dtype=float) / (2 * math.pi * d_m)


def core_flux_density(v_rms, f_hz, turns, core_area_m2):
    """Peak flux density from V = 4.44 f N A B (sinusoidal flux)."""
    return v_rms / (4.44 * f_hz * turns * core_area_m2)


def photon_energy_ev(wavelength_nm):
    return H_PLANCK * C_LIGHT / (np.asarray(wavelength_nm, dtype=float) * 1e-9) / Q_E


def planck_spectral(wavelength_m, t_k):
    """Blackbody spectral radiance shape (W per m2 per m per sr)."""
    lam = np.asarray(wavelength_m, dtype=float)
    return 2 * H_PLANCK * C_LIGHT ** 2 / lam ** 5 / np.expm1(H_PLANCK * C_LIGHT / (lam * K_BOLTZ * t_k))


def planck_fraction_above(e_gap_ev: float, t_k: float = 5778.0) -> float:
    """Share of blackbody power carried by photons with energy above e_gap (numerical)."""
    # in x = h nu / (k T) the blackbody power density is x^3 / (e^x - 1), total pi^4 / 15
    x_g = e_gap_ev * Q_E / (K_BOLTZ * t_k)

    def f(x):
        return x ** 3 / math.expm1(x) if x > 0 else 0.0
    part, _ = integrate.quad(f, x_g, 50.0, limit=200)
    return part * 15.0 / math.pi ** 4


def ultimate_efficiency(e_gap_ev: float, t_k: float = 5778.0) -> float:
    """Each photon above the gap delivers exactly E_gap; others deliver nothing.

    u = x_g * (photons above x_g) / (total power), with the photon density x^2/(e^x - 1)."""
    x_g = e_gap_ev * Q_E / (K_BOLTZ * t_k)

    def n(x):
        return x ** 2 / math.expm1(x) if x > 0 else 0.0
    photons, _ = integrate.quad(n, x_g, 50.0, limit=200)
    return x_g * photons * 15.0 / math.pi ** 4


def fresnel_reflectance(theta_deg, n1: float = 1.0, n2: float = 1.5):
    """Unpolarised reflectance of a smooth interface for incidence angle theta (deg)."""
    th = np.radians(np.asarray(theta_deg, dtype=float))
    s = n1 / n2 * np.sin(th)
    tt = np.arcsin(np.clip(s, -1, 1))
    ci, ct = np.cos(th), np.cos(tt)
    rs = ((n1 * ci - n2 * ct) / (n1 * ci + n2 * ct)) ** 2
    rp = ((n1 * ct - n2 * ci) / (n1 * ct + n2 * ci)) ** 2
    return 0.5 * (rs + rp)


def cantilever_f1(e_pa, i_m4, mass_per_m, length_m):
    """f1 = (1.8751^2 / 2 pi) sqrt(E I / (m L^4)) for a uniform clamped-free beam (Hz)."""
    return 1.8751 ** 2 / (2 * math.pi) * math.sqrt(e_pa * i_m4 / (mass_per_m * length_m ** 4))


def spl_at_distance(lw_db, r_m):
    """Free-field spherical spreading only: Lp = Lw - 20 log10 r - 11 (no ground, air)."""
    return np.asarray(lw_db, dtype=float) - 20.0 * np.log10(np.asarray(r_m, dtype=float)) - 11.0


# ---- chapter 4, second part ----------------------------------------------------------
def magnetising_current(b_peak: float, path_iron_m: float, mu_r: float, gap_m: float,
                        turns: int) -> float:
    """Peak magnetising current of a core: N i = B (l_fe / (mu0 mu_r) + g / mu0)."""
    h_total = b_peak * (path_iron_m / (MU0 * mu_r) + gap_m / MU0)
    return h_total / turns


def air_flow_for_heat(p_w: float, d_t_k: float, rho: float = 1.1, cp: float = 1005.0) -> float:
    """Volume flow (m3/s) that carries away p_w with a temperature rise d_t_k."""
    return p_w / (rho * cp * d_t_k)


def module_temperature_balance(g_wm2: float, t_air_c: float, wind_ms: float,
                               absorptance: float = 0.9, eta_el: float = 0.20,
                               emissivity: float = 0.85, t_sky_drop_k: float = 20.0,
                               h_scale: float = 1.0) -> float:
    """Steady module temperature from an energy balance (two faces, simple correlations).

    absorbed (1 - eta) a G = h_c (T - T_air) x 2 + eps sigma (T^4 - T_sky^4) + eps sigma
    (T^4 - T_ground^4), with h_c = 5.7 + 3.8 v (a classic flat-plate correlation, W/m2K),
    sky at T_air - t_sky_drop_k and ground at T_air. h_scale multiplies h_c (calibration of
    the convection, e.g. against the data-sheet NOCT). Solved by Newton's method."""
    q_in = (absorptance - eta_el) * g_wm2
    ta = t_air_c + 273.15
    ts = ta - t_sky_drop_k
    hc = h_scale * (5.7 + 3.8 * wind_ms)
    t = ta + 20.0
    for _ in range(50):
        f = (q_in - 2 * hc * (t - ta) - emissivity * SIGMA_SB * (2 * t ** 4 - ts ** 4 - ta ** 4))
        df = -2 * hc - emissivity * SIGMA_SB * 8 * t ** 3
        step = f / df
        t -= step
        if abs(step) < 1e-9:
            break
    return t - 273.15


def intrinsic_ratio(e_gap_ev: float, t1_c: float, t2_c: float) -> float:
    """Ratio of intrinsic carrier density n_i(T2)/n_i(T1) ~ T^1.5 exp(-Eg / 2kT)."""
    k_ev = K_BOLTZ / Q_E
    t1, t2 = t1_c + 273.15, t2_c + 273.15
    return (t2 / t1) ** 1.5 * math.exp(-e_gap_ev / (2 * k_ev) * (1 / t2 - 1 / t1))


# ---- chapter 4, third part ----------------------------------------------------------
SOLAR_CONSTANT = 1361.0     # W/m2, mean total solar irradiance at 1 au


def skin_depth(resistivity: float, f_hz: float, mu_r: float = 1.0) -> float:
    """delta = sqrt(2 rho / (omega mu)) in metres."""
    return math.sqrt(2 * resistivity / (2 * math.pi * f_hz * MU0 * mu_r))


def ac_dc_ratio_round(radius_m: float, resistivity: float, f_hz: float) -> float:
    """R_ac / R_dc of an isolated round solid conductor (Kelvin-Bessel functions)."""
    from scipy import special
    x = math.sqrt(2) * radius_m / skin_depth(resistivity, f_hz)
    if x < 1e-6:
        return 1.0
    ber, bei = special.ber(x), special.bei(x)
    berp, beip = special.berp(x), special.beip(x)
    return x / 2 * (ber * beip - bei * berp) / (berp ** 2 + beip ** 2)


def air_mass(elevation_deg):
    """Relative optical air mass 1 / sin(elevation) (plane atmosphere; above ~15 deg)."""
    return 1.0 / np.sin(np.radians(np.asarray(elevation_deg, dtype=float)))


def meinel_dni(elevation_deg):
    """Clear-sky beam irradiance 1.353 kW/m2 x 0.7^(AM^0.678), an empirical teaching fit."""
    return 1353.0 * 0.7 ** (air_mass(elevation_deg) ** 0.678)


def inflow(v_wind: float, a: float, omega: float, r: float) -> tuple[float, float]:
    """Relative speed and inflow angle (deg) at a blade section, tangential induction ignored."""
    axial = v_wind * (1 - a)
    tang = omega * r
    return math.hypot(axial, tang), math.degrees(math.atan2(axial, tang))


def kennelly_resistance(rho_soil: float, depth_m: float, diameter_m: float) -> float:
    """Thermal resistance (K m/W) between a buried cylinder and the ground surface."""
    u = 2 * depth_m / diameter_m
    return rho_soil / (2 * math.pi) * math.log(u + math.sqrt(u * u - 1))


def sum_levels_db(levels):
    """Total level of incoherent sources: 10 log10(sum 10^(L/10))."""
    return float(10 * np.log10(np.sum(10 ** (np.asarray(levels, dtype=float) / 10))))


# ---- chapter 4, fourth part ---------------------------------------------------------
def line_inductance_per_m(gmd_m: float, r_m: float) -> float:
    """Per-phase inductance of a transposed three-phase line, mu0/(2 pi) ln(GMD / r'),
    with r' = 0.7788 r for a solid round conductor."""
    return MU0 / (2 * math.pi) * math.log(gmd_m / (0.7788 * r_m))


def transmissibility(f_hz, f_n: float, zeta: float = 0.0):
    """Force transmissibility of a spring-mass-damper mount."""
    r = np.asarray(f_hz, dtype=float) / f_n
    num = 1 + (2 * zeta * r) ** 2
    den = (1 - r ** 2) ** 2 + (2 * zeta * r) ** 2
    return np.sqrt(num / den)


def adiabatic_k(c_vol: float, rho20: float, beta: float) -> float:
    """K in I^2 t = K^2 A^2 ln((T_f + beta)/(T_i + beta)) for a conductor heated with no
    cooling, from c_v dT = (I/A)^2 rho20 (T + beta)/(20 + beta) dt. Units A s^0.5 / m^2."""
    return math.sqrt(c_vol * (20 + beta) / rho20)


def adiabatic_final_temp(i_a: float, t_s: float, area_m2: float, t_i: float,
                         c_vol: float, rho20: float, beta: float) -> float:
    k = adiabatic_k(c_vol, rho20, beta)
    return (t_i + beta) * math.exp(i_a ** 2 * t_s / (k * area_m2) ** 2) - beta


# ---- chapter 4, fifth part ----------------------------------------------------------
WIEN_B = 2.897771955e-3      # m K


def wien_peak_um(t_k: float) -> float:
    """Wavelength of peak blackbody emission (micrometres)."""
    return WIEN_B / t_k * 1e6


def apparent_temperature(t_obj_c: float, eps_true: float, eps_set: float,
                         t_refl_c: float) -> float:
    """Temperature an ideal thermal camera reports for a grey surface (broadband model).

    Received W = eps sigma T_obj^4 + (1 - eps) sigma T_refl^4; the camera inverts it with its
    emissivity setting eps_set and the same reflected temperature."""
    to, tr = t_obj_c + 273.15, t_refl_c + 273.15
    w = eps_true * SIGMA_SB * to ** 4 + (1 - eps_true) * SIGMA_SB * tr ** 4
    t4 = (w - (1 - eps_set) * SIGMA_SB * tr ** 4) / (eps_set * SIGMA_SB)
    return t4 ** 0.25 - 273.15


def relative_air_density(p_hpa: float, t_c: float, p0: float = 1013.25,
                         t0_c: float = 20.0) -> float:
    """delta = (p / p0) (T0 / T): scales the breakdown strength of air gaps (first order)."""
    return (p_hpa / p0) * ((t0_c + 273.15) / (t_c + 273.15))
