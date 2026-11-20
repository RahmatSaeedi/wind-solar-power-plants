"""Wind-resource assessment (chapter 13): vertical profiles and their fits,
turbulence intensity, veer, sensor checks (tower shadow between two booms,
icing, stuck values), data recovery, measure-correlate-predict (MCP) with
three methods, and the sensitivity of energy to wind speed.

Teaching implementation: the formulas are the textbook forms; a real
campaign follows the measurement standards and the methods its reviewer
accepts, with the instruments' calibration and mounting documents.
"""
from __future__ import annotations

import math

import numpy as np

KAPPA = 0.4                      # von Karman constant


# ------------------------------------------------------------ profiles
def power_law(v_ref, z_ref: float, z, alpha: float):
    """v(z) = v_ref (z / z_ref)^alpha."""
    return np.asarray(v_ref, float) * (np.asarray(z, float) / z_ref) ** alpha


def log_law(v_ref, z_ref: float, z, z0: float):
    """Neutral logarithmic profile: v(z) = v_ref ln(z/z0) / ln(z_ref/z0)."""
    return (np.asarray(v_ref, float) * np.log(np.asarray(z, float) / z0)
            / math.log(z_ref / z0))


# [start: shearfit]
def fit_shear(heights, speeds) -> float:
    """Power-law exponent by least squares on ln v against ln z (one mean
    speed per height, or many concurrent rows averaged first)."""
    z = np.log(np.asarray(heights, float))
    v = np.log(np.asarray(speeds, float))
    return float(np.polyfit(z, v, 1)[0])


def fit_roughness(heights, speeds) -> tuple[float, float]:
    """Neutral log-law fit v = (u*/kappa) ln(z / z0): returns (z0, u*)."""
    slope, icept = np.polyfit(np.log(np.asarray(heights, float)),
                              np.asarray(speeds, float), 1)
    return float(math.exp(-icept / slope)), float(slope * KAPPA)
# [end: shearfit]


def pair_shear(v_low, v_high, z_low: float, z_high: float):
    """Row-by-row shear exponent between two heights (nan where either
    speed is below 3 m/s, where the exponent means little)."""
    lo, hi = np.asarray(v_low, float), np.asarray(v_high, float)
    ok = (lo > 3) & (hi > 3)
    out = np.full(lo.shape, np.nan)
    out[ok] = np.log(hi[ok] / lo[ok]) / math.log(z_high / z_low)
    return out


# ------------------------------------------------------------ turbulence, veer
def turbulence_intensity(mean, sd):
    """TI = sigma / mean for each ten-minute record (nan below 1 m/s)."""
    m, s = np.asarray(mean, float), np.asarray(sd, float)
    return np.where(m > 1, s / np.where(m > 1, m, 1), np.nan)


def ti_by_bin(mean, sd, edges, quantile: float = 0.9):
    """Mean and a high quantile of TI in each speed bin (the design standard
    defines which quantile is 'representative'): (centre, mean, q, n)."""
    m, s = np.asarray(mean, float), np.asarray(sd, float)
    ti = turbulence_intensity(m, s)
    out = []
    for a, b in zip(edges[:-1], edges[1:]):
        sel = (m >= a) & (m < b) & ~np.isnan(ti)
        if sel.sum() >= 10:
            out.append((0.5 * (a + b), float(np.mean(ti[sel])),
                        float(np.quantile(ti[sel], quantile)), int(sel.sum())))
    return out


def angle_diff(a, b):
    """Signed difference a - b of two directions in degrees, in (-180, 180]."""
    d = (np.asarray(a, float) - np.asarray(b, float) + 180.0) % 360.0 - 180.0
    return np.where(d == -180.0, 180.0, d)


# ------------------------------------------------------------ sensor checks
def sector_ratio(v1, v2, wd, width: float = 30.0):
    """Mean ratio v1/v2 by direction sector: a dip of one boom's ratio
    in the sectors where the mast stands upwind of it is tower shadow."""
    v1, v2, wd = (np.asarray(x, float) for x in (v1, v2, wd))
    ok = (v1 > 4) & (v2 > 4)
    edges = np.arange(0.0, 360.0 + width, width)
    out = []
    for a, b in zip(edges[:-1], edges[1:]):
        sel = ok & (wd % 360 >= a) & (wd % 360 < b)
        out.append((0.5 * (a + b), float(np.mean(v1[sel] / v2[sel])) if sel.sum() > 5
                    else float("nan"), int(sel.sum())))
    return out


def icing_flags(mean, sd, t_air, sd_min: float = 0.05, t_max: float = 1.0):
    """Probable icing: almost no variability (sd below sd_min) while the
    air is near or below freezing."""
    return ((np.asarray(sd, float) < sd_min) & (np.asarray(t_air, float) < t_max)
            & (np.asarray(mean, float) >= 0))


def stuck_runs(x, n: int = 6):
    """True where a value repeats for at least n consecutive records."""
    x = np.asarray(x, float)
    same = np.r_[False, np.diff(x) == 0]
    run = np.zeros(len(x), int)
    for k in range(1, len(x)):
        run[k] = run[k - 1] + 1 if same[k] else 0
    flag = run >= n - 1
    for k in range(len(x) - 1, 0, -1):          # spread back over the run
        if flag[k] and same[k]:
            flag[k - 1] = True
    return flag


def recovery(valid) -> float:
    """Share of records that passed quality control."""
    v = np.asarray(valid, bool)
    return float(v.sum() / v.size)


# ------------------------------------------------------------ MCP
# [start: mcp]
def mcp_linear(x_conc, y_conc, x_long):
    """Least-squares line y = a + b x on the concurrent period, applied to
    the long-term reference (it shrinks the spread of y)."""
    b, a = np.polyfit(x_conc, y_conc, 1)
    return a + b * np.asarray(x_long, float), float(a), float(b)


def mcp_variance_ratio(x_conc, y_conc, x_long):
    """Variance-ratio method: keeps the mean and the spread of the site."""
    x, y = np.asarray(x_conc, float), np.asarray(y_conc, float)
    b = y.std() / x.std()
    a = y.mean() - b * x.mean()
    return a + b * np.asarray(x_long, float), float(a), float(b)


def mcp_sector_ratio(x_conc, y_conc, wd_conc, x_long, wd_long, width=30.0):
    """Ratio of means by direction sector of the reference."""
    x, y = np.asarray(x_conc, float), np.asarray(y_conc, float)
    wdc, wdl = np.asarray(wd_conc, float) % 360, np.asarray(wd_long, float) % 360
    xl = np.asarray(x_long, float)
    out = np.empty_like(xl)
    for a in np.arange(0.0, 360.0, width):
        sc = (wdc >= a) & (wdc < a + width)
        sl = (wdl >= a) & (wdl < a + width)
        r = y[sc].mean() / x[sc].mean() if sc.sum() > 10 else y.mean() / x.mean()
        out[sl] = r * xl[sl]
    return out
# [end: mcp]


def mcp_matrix(x_conc, y_conc, wd_conc, x_long, wd_long, width: float = 30.0,
               bin_ms: float = 2.0, min_n: int = 30):
    """Matrix method: mean ratio site/reference in each (direction sector,
    reference-speed bin) cell; sparse cells fall back to the sector ratio
    and then to the overall ratio."""
    x, y = np.asarray(x_conc, float), np.asarray(y_conc, float)
    wdc = np.asarray(wd_conc, float) % 360
    wdl = np.asarray(wd_long, float) % 360
    xl = np.asarray(x_long, float)
    overall = y.mean() / x.mean()
    out = np.empty_like(xl)
    for a in np.arange(0.0, 360.0, width):
        sc = (wdc >= a) & (wdc < a + width)
        sl = (wdl >= a) & (wdl < a + width)
        r_sec = y[sc].mean() / x[sc].mean() if sc.sum() >= min_n else overall
        for b in np.arange(0.0, 40.0, bin_ms):
            cc = sc & (x >= b) & (x < b + bin_ms)
            cl = sl & (xl >= b) & (xl < b + bin_ms)
            r = y[cc].mean() / x[cc].mean() if cc.sum() >= min_n else r_sec
            out[cl] = r * xl[cl]
    return out


# ------------------------------------------------------------ energy
def energy_sensitivity(speeds, curve_v, curve_p, step: float = 0.01) -> float:
    """Relative change of energy for a relative change of every speed:
    (dE/E) / (dv/v), by finite difference over the speed series."""
    v = np.asarray(speeds, float)
    e0 = np.interp(v, curve_v, curve_p).sum()
    e1 = np.interp(v * (1 + step), curve_v, curve_p).sum()
    return float((e1 / e0 - 1) / step)


# ------------------------------------------------------------ atmosphere
G = 9.81                         # gravity, m/s2
GAMMA_DRY = 0.0098               # dry-adiabatic lapse rate, K/m


def bulk_richardson(t_low_c: float, t_high_c: float, v_low: float,
                    v_high: float, z_low: float, z_high: float) -> float:
    """Bulk Richardson number between two heights: buoyancy (potential
    temperature gradient) over shear production. Positive is stable,
    negative unstable; well above about 0.25 turbulence dies out."""
    dz = z_high - z_low
    dtheta = (t_high_c - t_low_c) / dz + GAMMA_DRY
    dudz = (v_high - v_low) / dz
    t_mean = 273.15 + 0.5 * (t_low_c + t_high_c)
    return G / t_mean * dtheta / max(dudz ** 2, 1e-12)


# [start: rews]
def rotor_equivalent(profile, hub: float, radius: float,
                     veer_per_m: float = 0.0, n: int = 400) -> float:
    """Rotor-equivalent wind speed of any profile v(z) (a function of
    height): the uniform speed with the same kinetic power through the
    disc. With veer, each height counts only its component along the hub
    direction."""
    t = np.linspace(-math.pi / 2, math.pi / 2, n + 1)  # z = hub + R sin t
    z = hub + radius * np.sin(t)
    turn = np.cos(np.radians(veer_per_m * (z - hub)))
    v = np.asarray(profile(z), float) * turn
    width = 2 * radius * np.cos(t)                     # chord of the disc
    flux = np.trapezoid(width * v ** 3 * radius * np.cos(t), t)
    return float((flux / (math.pi * radius ** 2)) ** (1 / 3))
# [end: rews]


def gust_factor(series, n_gust: int) -> tuple[float, float]:
    """Mean and largest moving average of n_gust samples of one record:
    returns (gust factor = gust / mean, gust)."""
    x = np.asarray(series, float)
    run = np.convolve(x, np.ones(n_gust) / n_gust, mode="valid")
    return float(run.max() / x.mean()), float(run.max())


# ------------------------------------------------------------ instruments
# [start: dirmean]
def vector_mean_direction(wd, speed=None) -> float:
    """Mean direction of a set of directions (degrees) by averaging unit
    vectors (or speed-weighted vectors): 350 and 10 give 0, not 180."""
    a = np.radians(np.asarray(wd, float))
    w = np.ones_like(a) if speed is None else np.asarray(speed, float)
    s, c = np.sum(w * np.sin(a)), np.sum(w * np.cos(a))
    return float(math.degrees(math.atan2(s, c)) % 360.0)
# [end: dirmean]


def cup_speed(freq_hz, slope: float, offset: float):
    """Cup anemometer transfer function v = slope x f + offset."""
    return slope * np.asarray(freq_hz, float) + offset


def dbs_reconstruct(radial: dict, half_angle_deg: float) -> tuple[float, float, float]:
    """Wind vector (u east, v north, w up) from four tilted beams N, E, S, W
    of a profiling lidar, assuming the same wind at all four beams."""
    s = math.sin(math.radians(half_angle_deg))
    c = math.cos(math.radians(half_angle_deg))
    u = (radial["E"] - radial["W"]) / (2 * s)
    v = (radial["N"] - radial["S"]) / (2 * s)
    w = (radial["N"] + radial["S"] + radial["E"] + radial["W"]) / (4 * c)
    return u, v, w


def dbs_radials(u: float, v: float, w_by_beam: dict, half_angle_deg: float) -> dict:
    """Radial speeds (positive away from the lidar) of the four beams for a
    horizontal wind (u, v) and a vertical wind that may differ by beam."""
    s = math.sin(math.radians(half_angle_deg))
    c = math.cos(math.radians(half_angle_deg))
    return {"N": v * s + w_by_beam["N"] * c, "S": -v * s + w_by_beam["S"] * c,
            "E": u * s + w_by_beam["E"] * c, "W": -u * s + w_by_beam["W"] * c}
