"""Solar-resource assessment (chapter 12): extraterrestrial irradiance, air
mass, clearness index, a simple clear-sky model, decomposition of global
into beam and diffuse, isotropic transposition, quality-control tests for
irradiance data, time-shift and gap checks, sensor drift, comparison
statistics of two sources, long-term correction and P50/P90 values.

Teaching implementation: the quality-control limits follow the form of
published test families for radiation networks with teaching constants;
a real campaign uses the current documents of the network or standard it
reports against, and the methods its lenders accept.
"""
from __future__ import annotations

import math

import numpy as np

from plantp.physics import SOLAR_CONSTANT


# ------------------------------------------------------------ sun and sky
def g0n(day_of_year):
    """Extraterrestrial normal irradiance (W/m2): the solar constant
    corrected for the Earth-Sun distance (simple cosine form)."""
    n = np.asarray(day_of_year, dtype=float)
    return SOLAR_CONSTANT * (1 + 0.033 * np.cos(2 * np.pi * n / 365))


def air_mass(zenith_deg):
    """Relative optical air mass (Kasten and Young 1989); nan below the
    horizon."""
    z = np.asarray(zenith_deg, dtype=float)
    am = 1.0 / (np.cos(np.radians(z)) + 0.50572 * (96.07995 - z) ** -1.6364)
    return np.where(z < 90.0, am, np.nan)


def clearness_index(ghi, cos_zen, g0n_wm2, min_cos: float = 0.087):
    """k_t = GHI / (G0n cos z); nan when the sun is lower than about 5 deg."""
    ghi, cz = np.asarray(ghi, float), np.asarray(cos_zen, float)
    g0h = np.asarray(g0n_wm2, float) * cz
    return np.where(cz > min_cos, ghi / np.where(g0h > 0, g0h, np.nan), np.nan)


def clear_sky_haurwitz(cos_zen):
    """Clear-sky global horizontal irradiance (W/m2), Haurwitz's empirical
    form: 1098 cos z exp(-0.057 / cos z); zero below the horizon."""
    cz = np.asarray(cos_zen, dtype=float)
    out = np.zeros_like(cz)
    up = cz > 0
    out[up] = 1098.0 * cz[up] * np.exp(-0.057 / cz[up])
    return out


# [start: erbs]
def erbs_diffuse_fraction(kt):
    """Diffuse fraction k_d = DHI / GHI from the clearness index (Erbs,
    Klein and Duffie 1982): three pieces joined at k_t 0.22 and 0.80."""
    kt = np.asarray(kt, dtype=float)
    mid = (0.9511 - 0.1604 * kt + 4.388 * kt ** 2 - 16.638 * kt ** 3
           + 12.336 * kt ** 4)
    return np.where(kt <= 0.22, 1 - 0.09 * kt,
                    np.where(kt <= 0.80, mid, 0.165))
# [end: erbs]


def orgill_hollands_diffuse_fraction(kt):
    """Diffuse fraction from the clearness index (Orgill and Hollands 1977):
    1 - 0.249 k_t below 0.35, 1.557 - 1.84 k_t up to 0.75, 0.177 above."""
    kt = np.asarray(kt, dtype=float)
    return np.where(kt < 0.35, 1 - 0.249 * kt,
                    np.where(kt <= 0.75, 1.557 - 1.84 * kt, 0.177))


def decompose(ghi, cos_zen, g0n_wm2, model: str = "erbs"):
    """Beam (DNI) and diffuse (DHI) from GHI with the Erbs model or the
    Orgill-Hollands model (model='orgill')."""
    ghi, cz = np.asarray(ghi, float), np.asarray(cos_zen, float)
    kt = np.nan_to_num(clearness_index(ghi, cz, g0n_wm2), nan=0.0)
    fn = orgill_hollands_diffuse_fraction if model == "orgill" else erbs_diffuse_fraction
    dhi = np.where(cz > 0.087, ghi * np.clip(fn(kt), 0, 1), ghi)
    dni = np.where(cz > 0.087, (ghi - dhi) / np.where(cz > 0, cz, 1), 0.0)
    return np.clip(dni, 0, None), dhi


def poa_isotropic(ghi, dni, dhi, cos_inc, tilt_deg: float, albedo: float = 0.2):
    """Plane-of-array beam, sky and ground irradiance with an isotropic sky
    (Liu and Jordan)."""
    b = math.radians(tilt_deg)
    ci = np.clip(np.asarray(cos_inc, float), 0, None)
    beam = np.asarray(dni, float) * ci
    sky = np.asarray(dhi, float) * (1 + math.cos(b)) / 2
    ground = np.asarray(ghi, float) * albedo * (1 - math.cos(b)) / 2
    return beam, sky, ground


# ------------------------------------------------------------ quality control
FLAG_PHYS, FLAG_RARE, FLAG_CLOSURE, FLAG_NIGHT_NEG, FLAG_MISSING = 1, 2, 4, 8, 16


# [start: qc]
def qc_limits(cos_zen, g0n_wm2) -> dict:
    """Upper limits of the two test families (teaching constants): a value
    above 'phys' is physically impossible, above 'rare' extremely rare."""
    mu = np.clip(np.asarray(cos_zen, float), 0, None)
    s = np.asarray(g0n_wm2, float)
    m12 = mu ** 1.2
    return {"ghi_phys": 1.5 * s * m12 + 100, "ghi_rare": 1.2 * s * m12 + 50,
            "dhi_phys": 0.95 * s * m12 + 50, "dhi_rare": 0.75 * s * m12 + 30,
            "dni_phys": s, "dni_rare": 0.95 * s * mu ** 0.2 + 10}


def qc_flags(ghi, dni, dhi, cos_zen, g0n_wm2, closure_tol: float = 0.08):
    """Bit flags per sample: 1 physically impossible, 2 extremely rare,
    4 components do not close (sun above 15 deg, GHI > 50 W/m2), 8 large
    negative value at night, 16 missing."""
    ghi, dni, dhi = (np.asarray(x, float) for x in (ghi, dni, dhi))
    cz = np.asarray(cos_zen, float)
    lim = qc_limits(cz, g0n_wm2)
    f = np.zeros(ghi.shape, dtype=int)
    miss = np.isnan(ghi) | np.isnan(dni) | np.isnan(dhi)
    f |= np.where(miss, FLAG_MISSING, 0)
    g, d, b = (np.nan_to_num(x) for x in (ghi, dhi, dni))
    phys = ((g > lim["ghi_phys"]) | (d > lim["dhi_phys"])
            | (b > lim["dni_phys"]) | (g < -4) | (d < -4) | (b < -4))
    rare = ((g > lim["ghi_rare"]) | (d > lim["dhi_rare"])
            | (b > lim["dni_rare"]))
    f |= np.where(phys & ~miss, FLAG_PHYS, 0)
    f |= np.where(rare & ~phys & ~miss, FLAG_RARE, 0)
    test = (cz > math.sin(math.radians(15))) & (g > 50) & ~miss
    ratio = np.divide(b * cz + d, g, out=np.ones_like(g), where=g > 0)
    f |= np.where(test & (np.abs(ratio - 1) > closure_tol), FLAG_CLOSURE, 0)
    f |= np.where((cz <= 0) & (g < -10) & ~miss, FLAG_NIGHT_NEG, 0)
    return f
# [end: qc]


def closure_ratio(ghi, dni, dhi, cos_zen):
    """(DNI cos z + DHI) / GHI: 1 for consistent components."""
    g = np.asarray(ghi, float)
    s = np.asarray(dni, float) * np.asarray(cos_zen, float) + np.asarray(dhi, float)
    return np.divide(s, g, out=np.full_like(g, np.nan), where=g > 0)


# ------------------------------------------------------------ time, gaps, drift
def best_lag(measured, reference, max_lag: int) -> int:
    """Shift (samples) that best aligns a measured series with a reference:
    largest normalised cross-product (no mean removal, so the dark night
    hours anchor the day); positive means the measurement is late."""
    m = np.nan_to_num(np.asarray(measured, float))
    r = np.nan_to_num(np.asarray(reference, float))
    best, best_c = 0, -np.inf
    for lag in range(-max_lag, max_lag + 1):
        a = m[max(lag, 0):len(m) + min(lag, 0)]
        b = r[max(-lag, 0):len(r) + min(-lag, 0)]
        c = float(np.dot(a, b) / math.sqrt(max(np.dot(a, a) * np.dot(b, b), 1e-30)))
        if c > best_c:
            best, best_c = lag, c
    return best


def fill_short_gaps(kt, max_gap: int = 3):
    """Fill gaps of at most max_gap samples by linear interpolation of the
    clearness index; longer gaps stay nan (they need another source)."""
    x = np.asarray(kt, float).copy()
    nan = np.isnan(x)
    i = 0
    while i < len(x):
        if nan[i]:
            j = i
            while j < len(x) and nan[j]:
                j += 1
            if 0 < i and j < len(x) and j - i <= max_gap:
                x[i:j] = np.interp(np.arange(i, j), [i - 1, j], [x[i - 1], x[j]])
            i = j
        else:
            i += 1
    return x


def ratio_by_block(measured, reference, block: int):
    """Ratio of sums in consecutive blocks (e.g. weeks): a drifting or
    soiled sensor shows as a falling ratio against a stable reference."""
    m = np.asarray(measured, float)
    r = np.asarray(reference, float)
    n = len(m) // block
    return np.array([np.nansum(m[k * block:(k + 1) * block])
                     / np.nansum(r[k * block:(k + 1) * block]) for k in range(n)])


# ------------------------------------------------------------ comparing sources
def mbe(estimate, reference) -> float:
    """Mean bias error (estimate minus reference)."""
    e, r = np.asarray(estimate, float), np.asarray(reference, float)
    ok = ~(np.isnan(e) | np.isnan(r))
    return float(np.mean(e[ok] - r[ok]))


def rmse(estimate, reference) -> float:
    e, r = np.asarray(estimate, float), np.asarray(reference, float)
    ok = ~(np.isnan(e) | np.isnan(r))
    return float(np.sqrt(np.mean((e[ok] - r[ok]) ** 2)))


def distribution_distance(a, b, n: int = 100) -> float:
    """Mean absolute difference between the quantiles of two samples: zero
    when the two distributions are the same, whatever the timing."""
    q = np.linspace(0.01, 0.99, n)
    return float(np.mean(np.abs(np.nanquantile(a, q) - np.nanquantile(b, q))))


# ------------------------------------------------------------ long term
# [start: longterm]
def long_term_ratio(site, ref_concurrent, ref_long) -> float:
    """Long-term mean at the site: the short site record scaled by the
    reference source's long-term to concurrent ratio (sums or means)."""
    return float(np.mean(site) * np.mean(ref_long) / np.mean(ref_concurrent))
# [end: longterm]


def combine_uncertainty(*parts) -> float:
    """Root-sum-square of independent relative uncertainties."""
    return float(math.sqrt(sum(u ** 2 for u in parts)))


def p_value(p50: float, u_rel: float, exceed: float = 0.90) -> float:
    """Value exceeded with the given probability for a normal spread with
    relative standard uncertainty u_rel (P90 = P50 (1 - 1.2816 u))."""
    from statistics import NormalDist
    z = NormalDist().inv_cdf(exceed)
    return p50 * (1 - z * u_rel)
