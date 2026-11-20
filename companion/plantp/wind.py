"""Wind-turbine physics for teaching (chapter 11): a synthetic aerofoil, a
blade designed for one tip-speed ratio, blade-element momentum (BEM)
theory with tip and hub losses, the control regions that turn rotor
coefficients into a power curve, turbulence smoothing and density
correction, the Jensen (Park) wake model, rainflow counting with Miner's
rule, and the first bending frequency of a tower with a top mass.

Teaching implementation: the aerofoil and blade are fictional and simple;
real design uses measured polars, validated codes and certified loads.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy.optimize import brentq

# ------------------------------------------------------------------ aerofoil
ALPHA_STALL = 12.0              # deg, end of the attached-flow region


def polar(alpha_deg):
    """Lift and drag coefficients of a fictional thick aerofoil: linear
    lift (0.11 per degree, zero lift at -2 deg) and parabolic drag while
    attached; flat-plate values after stall; smooth blend across stall."""
    a = np.asarray(alpha_deg, dtype=float)
    cl_att = 0.11 * (a + 2.0)
    cd_att = 0.005 + 0.00008 * a ** 2
    ar = np.radians(a)
    cl_fp = 2.0 * np.sin(ar) * np.cos(ar)
    cd_fp = 2.0 * np.sin(ar) ** 2 + 0.02
    w = 0.5 * (1 + np.tanh((np.abs(a) - ALPHA_STALL) / 1.5))   # 0 attached
    return (1 - w) * cl_att + w * cl_fp, (1 - w) * cd_att + w * cd_fp


# ------------------------------------------------------------------ blade
@dataclass(frozen=True)
class Blade:
    r: np.ndarray               # m, annulus centres
    dr: np.ndarray              # m, annulus widths
    chord: np.ndarray           # m
    twist: np.ndarray           # deg
    radius: float               # m, tip radius
    hub: float                  # m, hub radius
    n_blades: int = 3


def design_blade(radius: float = 75.0, hub: float = 2.5, tsr: float = 8.0,
                 alpha_design: float = 6.0, n_blades: int = 3,
                 n_elem: int = 40, max_chord: float = 4.8) -> Blade:
    """Optimum blade with wake rotation (Schmitz): inflow angle
    phi = 2/3 atan(1/lambda_r), chord 8 pi r (1 - cos phi) / (B Cl),
    twist = phi - alpha_design; chord capped at the root."""
    edges = np.linspace(hub, radius, n_elem + 1)
    r = 0.5 * (edges[1:] + edges[:-1])
    lam_r = tsr * r / radius
    phi = 2.0 / 3.0 * np.arctan(1.0 / lam_r)
    cl = float(polar(alpha_design)[0])
    chord = 8 * math.pi * r * (1 - np.cos(phi)) / (n_blades * cl)
    chord = np.minimum(chord, max_chord)
    twist = np.degrees(phi) - alpha_design
    return Blade(r, np.diff(edges), chord, twist, radius, hub, n_blades)


# ------------------------------------------------------------------ BEM
@dataclass(frozen=True)
class BemResult:
    cp: float
    ct: float
    a: np.ndarray               # axial induction per annulus
    alpha: np.ndarray           # deg, angle of attack per annulus
    dq: np.ndarray | None = None  # torque per annulus (v = rho = 1)
    dt: np.ndarray | None = None  # thrust per annulus (v = rho = 1)


def bem(blade: Blade, tsr: float, pitch_deg: float = 0.0,
        iterations: int = 100, relax: float = 0.5,
        polar_fn=None) -> BemResult:
    """Steady BEM for all annuli at once (free stream 1 m/s, density 1):
    Prandtl tip and hub losses, Buhl's high-induction correction.
    polar_fn(alpha) may replace the clean aerofoil (e.g. an eroded one)."""
    polar = polar_fn or globals()["polar"]
    r, c, b = blade.r, blade.chord, blade.n_blades
    big_r, hub = blade.radius, blade.hub
    lam_r = tsr * r / big_r
    sigma = b * c / (2 * math.pi * r)
    a = np.full_like(r, 0.3)
    ap = np.zeros_like(r)
    for _ in range(iterations):
        phi = np.arctan2(1 - a, lam_r * (1 + ap))
        sphi = np.maximum(np.abs(np.sin(phi)), 1e-6)
        alpha = np.degrees(phi) - blade.twist - pitch_deg
        cl, cd = polar(alpha)
        cn = cl * np.cos(phi) + cd * np.sin(phi)
        ctan = cl * np.sin(phi) - cd * np.cos(phi)
        f_tip = 2 / math.pi * np.arccos(np.clip(
            np.exp(-b * (big_r - r) / (2 * r * sphi)), 0, 1))
        f_hub = 2 / math.pi * np.arccos(np.clip(
            np.exp(-b * (r - hub) / (2 * hub * sphi)), 0, 1))
        f = np.maximum(f_tip * f_hub, 1e-4)
        k = sigma * cn / (4 * f * sphi ** 2)
        a_new = k / (1 + k)
        ct_loc = sigma * (1 - a) ** 2 * cn / sphi ** 2
        hi = ct_loc > 0.96 * f
        if np.any(hi):
            fh, ch = f[hi], ct_loc[hi]
            a_new[hi] = (18 * fh - 20 - 3 * np.sqrt(np.maximum(
                ch * (50 - 36 * fh) + 12 * fh * (3 * fh - 4), 0))) \
                / (36 * fh - 50)
        kp = sigma * ctan / (4 * f * sphi * np.cos(phi))
        ap_new = kp / (1 - kp)
        a = (1 - relax) * a + relax * np.clip(a_new, -0.5, 0.95)
        ap = (1 - relax) * ap + relax * np.clip(ap_new, -0.5, 1.0)
    phi = np.arctan2(1 - a, lam_r * (1 + ap))
    alpha = np.degrees(phi) - blade.twist - pitch_deg
    cl, cd = polar(alpha)
    w2 = (1 - a) ** 2 + (lam_r * (1 + ap)) ** 2
    tang = cl * np.sin(phi) - cd * np.cos(phi)
    norm = cl * np.cos(phi) + cd * np.sin(phi)
    dq = 0.5 * w2 * b * c * tang * r * blade.dr      # torque, per annulus
    dt = 0.5 * w2 * b * c * norm * blade.dr          # thrust, per annulus
    area = math.pi * big_r ** 2
    omega = tsr / big_r
    cp = float(omega * dq.sum() / (0.5 * area))
    ct = float(dt.sum() / (0.5 * area))
    return BemResult(cp, ct, a, alpha, dq, dt)


# ------------------------------------------------------------ ideal rotors
def glauert_cp_max(tsr: float, n: int = 400) -> float:
    """Highest power coefficient of an ideal rotor with wake rotation
    (Glauert): each annulus runs at the induction a in (1/4, 1/3) with
    lambda_r^2 = (1 - a)(4a - 1)^2 / (1 - 3a), a' = (1 - 3a)/(4a - 1)."""
    lam_r = np.linspace(tsr / n, tsr, n)
    a = np.empty(n)
    for k, lr in enumerate(lam_r):
        a[k] = brentq(lambda x: (1 - x) * (4 * x - 1) ** 2 / (1 - 3 * x)
                      - lr ** 2, 0.25 + 1e-12, 1 / 3 - 1e-12)
    ap = (1 - 3 * a) / (4 * a - 1)
    f = ap * (1 - a) * lam_r ** 3
    lam_r = np.concatenate(([0.0], lam_r))
    f = np.concatenate(([0.0], f))
    return float(8 / tsr ** 2 * np.trapezoid(f, lam_r))


def thrust_coefficient(a, f: float = 1.0):
    """Annulus thrust coefficient: momentum theory 4aF(1 - a) up to a = 0.4,
    Buhl's empirical parabola above it (it reaches 2 at a = 1)."""
    a = np.asarray(a, float)
    mom = 4 * a * f * (1 - a)
    buhl = 8 / 9 + (4 * f - 40 / 9) * a + (50 / 9 - 4 * f) * a ** 2
    return np.where(a <= 0.4, mom, buhl)


def rotor_equivalent_speed(v_hub: float, hub: float, radius: float,
                           shear: float, n: int = 400) -> float:
    """Rotor-equivalent wind speed: the uniform speed with the same kinetic
    power through the disc as the power-law profile v_hub (z/hub)^shear."""
    t = np.linspace(-math.pi / 2, math.pi / 2, n + 1)    # y = R sin t
    v = v_hub * ((hub + radius * np.sin(t)) / hub) ** shear
    flux = np.trapezoid(2 * radius ** 2 * np.cos(t) ** 2 * v ** 3, t)
    return float((flux / (math.pi * radius ** 2)) ** (1 / 3))


def flap_moments(r: np.ndarray, force: np.ndarray) -> np.ndarray:
    """Bending moment at each station r_j from the loads outboard of it:
    M(r_j) = sum over r_i > r_j of force_i (r_i - r_j)."""
    r, force = np.asarray(r, float), np.asarray(force, float)
    arm = r[None, :] - r[:, None]
    return (np.where(arm > 0, arm, 0.0) * force[None, :]).sum(axis=1)


# ------------------------------------------------------------ gears, bearings
def planetary_ratio(z_sun: int, z_ring: int) -> float:
    """Speed ratio of a planetary stage: ring fixed, carrier in, sun out."""
    return 1 + z_ring / z_sun


def bearing_life_mrev(c_n: float, p_n: float,
                      exponent: float = 10 / 3) -> float:
    """Basic rating life L10 in millions of revolutions (10/3 for rollers,
    3 for balls): the life that 90 % of a large group of bearings reach."""
    return (c_n / p_n) ** exponent


# ------------------------------------------------------------ measurement
def bin_power_curve(v, p, width: float = 0.5, v_max: float = 25.0,
                    min_count: int = 10):
    """Method of bins: mean wind speed, mean power, standard deviation and
    count of the records in each speed bin; sparse bins are dropped."""
    v, p = np.asarray(v, float), np.asarray(p, float)
    edges = np.arange(0.0, v_max + width, width)
    idx = np.digitize(v, edges) - 1
    out = []
    for k in range(len(edges) - 1):
        sel = idx == k
        cnt = int(sel.sum())
        if cnt >= min_count:
            out.append((float(v[sel].mean()), float(p[sel].mean()),
                        float(p[sel].std(ddof=1)), cnt))
    return out


# ------------------------------------------------------------------ sound
def sound_pressure_level(lw_db: float, r_m, alpha_db_per_m: float = 0.005):
    """Sound pressure level at slant distance r from a point source of
    sound power level lw_db over hard flat ground (hemispherical spreading)
    with a single air-absorption coefficient; no ground or barrier terms."""
    r = np.asarray(r_m, float)
    return lw_db - 10 * np.log10(2 * math.pi * r ** 2) - alpha_db_per_m * r


def sum_levels(levels) -> float:
    """Energetic sum of sound levels in dB."""
    return float(10 * np.log10(np.sum(10 ** (np.asarray(levels) / 10))))


# ------------------------------------------------------------------ control
@dataclass(frozen=True)
class Turbine:
    blade: Blade
    rated_w: float = 5.0e6
    eta: float = 0.94           # drivetrain + generator + converter
    omega_min: float = 5.0 * math.pi / 30          # rad/s (5 rpm)
    omega_max: float = 11.5 * math.pi / 30         # rad/s (11.5 rpm)
    tsr_opt: float = 8.0
    v_in: float = 3.0
    v_out: float = 25.0


@dataclass(frozen=True)
class OperatingPoint:
    v: float
    power_w: float
    omega: float
    tsr: float
    pitch: float
    cp: float
    ct: float
    thrust_n: float
    torque_nm: float


def operate(t: Turbine, v: float, rho: float = 1.225) -> OperatingPoint:
    """Steady operating point: optimum tip-speed ratio within the rotor
    speed limits, then pitch to hold rated power above rated wind."""
    big_r = t.blade.radius
    area = math.pi * big_r ** 2
    if v < t.v_in or v > t.v_out:
        return OperatingPoint(v, 0.0, 0.0, 0.0, 90.0, 0.0, 0.0, 0.0, 0.0)
    omega = min(max(t.tsr_opt * v / big_r, t.omega_min), t.omega_max)
    tsr = omega * big_r / v
    res = bem(t.blade, tsr, 0.0)
    p_avail = 0.5 * rho * area * v ** 3
    pitch = 0.0
    target = t.rated_w / (p_avail * t.eta)
    if omega >= t.omega_max - 1e-9 and res.cp < target:
        # above rated the rotor may be stalled at zero pitch: find the
        # pitch of maximum Cp first and solve on the feathering side
        grid = np.arange(0.0, 36.0, 5.0)
        cps = [bem(t.blade, tsr, g).cp for g in grid]
        k = int(np.argmax(cps))
        if cps[k] > target:
            pitch = brentq(lambda b: bem(t.blade, tsr, b).cp - target,
                           float(grid[k]), 35.0, xtol=1e-4)
            res = bem(t.blade, tsr, pitch)
    elif res.cp > target:
        pitch = brentq(lambda b: bem(t.blade, tsr, b).cp - target, 0.0, 35.0,
                       xtol=1e-4)
        res = bem(t.blade, tsr, pitch)
    p_w = max(res.cp, 0.0) * p_avail * t.eta
    thrust = res.ct * p_avail / v                  # Ct x rho A v^2 / 2
    return OperatingPoint(v, p_w, omega, tsr, pitch, res.cp, res.ct, thrust,
                          p_w / t.eta / omega)


def smooth_power_curve(v, p, ti: float = 0.10):
    """Average a steady curve over Gaussian wind speeds with standard
    deviation ti * v (a ten-minute mean sees turbulence)."""
    v, p = np.asarray(v, float), np.asarray(p, float)
    out = np.zeros_like(p)
    for k, vk in enumerate(v):
        s = max(ti * vk, 1e-6)
        w = np.exp(-0.5 * ((v - vk) / s) ** 2)
        out[k] = (w * p).sum() / w.sum()
    return out


def density_equivalent_speed(v, rho: float, rho0: float = 1.225):
    """Wind speed that carries the same kinetic power at reference density."""
    return np.asarray(v, float) * (rho / rho0) ** (1 / 3)


# ------------------------------------------------------------------ wakes
def jensen_deficit(ct: float, x: float, d: float, k: float = 0.05):
    """Fractional speed deficit at distance x behind a rotor of diameter d
    (top-hat Park model, wake decay constant k)."""
    if x <= 0:
        return 0.0
    return (1 - math.sqrt(max(1 - ct, 0.0))) * (d / (d + 2 * k * x)) ** 2


def farm_speeds(xy: np.ndarray, v: float, wd_deg: float, ct: float,
                d: float, k: float = 0.05) -> np.ndarray:
    """Waked speed at each turbine for wind from wd_deg (meteorological),
    square-root-of-sum-of-squares superposition, full-wake overlap when
    the downstream rotor centre lies inside the wake cone."""
    th = math.radians(wd_deg)
    u = np.array([-math.sin(th), -math.cos(th)])      # flow direction
    n = len(xy)
    deficit2 = np.zeros(n)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            dvec = xy[j] - xy[i]
            x = float(dvec @ u)
            if x <= 0:
                continue
            y = abs(float(dvec[0] * u[1] - dvec[1] * u[0]))
            if y < d / 2 + k * x:
                deficit2[j] += jensen_deficit(ct, x, d, k) ** 2
    return v * (1 - np.sqrt(deficit2))


# ------------------------------------------------------------------ fatigue
def rainflow(series) -> list[tuple[float, float]]:
    """Rainflow counting (four-point method on turning points): returns
    (range, count) with count 1.0 for full cycles and 0.5 for residue."""
    x = np.asarray(series, float)
    tp = [x[0]]
    for k in range(1, len(x) - 1):
        if (x[k] - x[k - 1]) * (x[k + 1] - x[k]) < 0:
            tp.append(x[k])
    tp.append(x[-1])
    stack, cycles = [], []
    for p in tp:
        stack.append(p)
        while len(stack) >= 4:
            s1, s2, s3, s4 = stack[-4:]
            r_in, r_out1, r_out2 = abs(s3 - s2), abs(s2 - s1), abs(s4 - s3)
            if r_in <= r_out1 and r_in <= r_out2:
                cycles.append((r_in, 1.0))
                del stack[-3:-1]
            else:
                break
    for k in range(len(stack) - 1):
        cycles.append((abs(stack[k + 1] - stack[k]), 0.5))
    return cycles


def miner_damage(cycles, s_ref: float, n_ref: float, m: float) -> float:
    """Palmgren-Miner damage with a Basquin S-N curve N = n_ref (s_ref/S)^m."""
    return float(sum(c * (s / s_ref) ** m / n_ref for s, c in cycles if s > 0))


def damage_equivalent_load(cycles, m: float, n_eq: float) -> float:
    """Constant range that does the same damage in n_eq cycles."""
    tot = sum(c * s ** m for s, c in cycles)
    return float((tot / n_eq) ** (1 / m))


# ------------------------------------------------------------------ tower
def tower_frequency(e_pa: float, i_m4: float, mass_per_m: float,
                    length_m: float, top_mass_kg: float) -> float:
    """First bending frequency of a uniform cantilever with a top mass
    (Rayleigh: 0.24 of the tower mass acts at the top)."""
    k = 3 * e_pa * i_m4 / length_m ** 3
    m_eff = top_mass_kg + 0.2357 * mass_per_m * length_m
    return math.sqrt(k / m_eff) / (2 * math.pi)


def tube_inertia(d_out: float, t: float) -> float:
    """Second moment of area of a thin-walled circular tube."""
    d_in = d_out - 2 * t
    return math.pi / 64 * (d_out ** 4 - d_in ** 4)
