"""Uncertainty of an energy yield (chapter 16; the measurement tools of
chapters 2 and 3 are in plantp.uncertainty): exceedance values,
combination of components with correlation, variance shares, the
year-to-year term over n years, sampling for Monte Carlo, quantiles and
their convergence, and a simple debt size from a cover ratio.

All uncertainties are standard uncertainties (one sigma), relative to
the P50 unless a function says otherwise.
"""
from __future__ import annotations

import math
from statistics import NormalDist

import numpy as np


# ------------------------------------------------------------ exceedance
# [start: exceedance]
def z_exceed(p: float) -> float:
    """z such that a normal value is exceeded with probability p:
    P90 -> 1.2816, P99 -> 2.3263, P50 -> 0."""
    return NormalDist().inv_cdf(p)


def p_value(p50: float, u_rel: float, p: float = 0.90) -> float:
    """Value exceeded with probability p, normal spread u_rel."""
    return p50 * (1.0 - z_exceed(p) * u_rel)


def p_value_lognormal(median: float, u_rel: float, p: float = 0.90) -> float:
    """Same for a lognormal spread whose log has sd ln(1 + u_rel)."""
    s = math.log(1.0 + u_rel)
    return median * math.exp(-z_exceed(p) * s)
# [end: exceedance]


# ------------------------------------------------------------ combination
# [start: combine]
def combine(u, r=None) -> float:
    """Combined uncertainty of a sum of components u (same units) with
    correlation matrix r (identity if None): sqrt(u' R u)."""
    u = np.asarray(u, float)
    if r is None:
        return float(math.sqrt(float(u @ u)))
    r = np.asarray(r, float)
    return float(math.sqrt(float(u @ r @ u)))


def shares(u, r=None) -> np.ndarray:
    """Share of the variance of each component (independent: u_i^2 /
    sum; correlated: u_i (R u)_i / u' R u, which still sums to one)."""
    u = np.asarray(u, float)
    r = np.eye(len(u)) if r is None else np.asarray(r, float)
    return u * (r @ u) / float(u @ r @ u)


def n_year(u_long: float, u_iav: float, n: int) -> float:
    """Uncertainty of the mean of n future years: the long-term part
    stays, the year-to-year part falls with the square root of n."""
    return math.sqrt(u_long ** 2 + u_iav ** 2 / n)
# [end: combine]


# [start: sens]
def sensitivity_ratio(speeds, curve_v, curve_p, step: float = 0.01) -> float:
    """Percent change of energy per percent change of every speed."""
    e0 = float(np.interp(speeds, curve_v, curve_p).sum())
    v1 = np.asarray(speeds) * (1 + step)
    e1 = float(np.interp(v1, curve_v, curve_p).sum())
    return (e1 / e0 - 1.0) / step
# [end: sens]


# ------------------------------------------------------------ sampling
# [start: sample]
def sample(kind: str, u: float, n: int, rng) -> np.ndarray:
    """Multiplicative factors with mean 1 and standard deviation u:
    normal, lognormal, uniform (half-width u sqrt 3) or symmetric
    triangular (half-width u sqrt 6)."""
    if kind == "normal":
        return 1.0 + u * rng.standard_normal(n)
    if kind == "lognormal":
        s = math.sqrt(math.log(1.0 + u * u))
        return np.exp(-0.5 * s * s + s * rng.standard_normal(n))
    if kind == "uniform":
        a = u * math.sqrt(3.0)
        return 1.0 + rng.uniform(-a, a, n)
    if kind == "triangular":
        a = u * math.sqrt(6.0)
        return 1.0 + rng.triangular(-a, 0.0, a, n)
    raise ValueError(kind)


def exceedance(values, p: float = 0.90) -> float:
    """Value exceeded by a share p of the samples (P90: 10th percentile)."""
    return float(np.quantile(np.asarray(values, float), 1.0 - p))
# [end: sample]


# [start: converge]
def convergence(draw, sizes, repeats: int, seed: int, p: float = 0.90):
    """Mean and spread of the sample P-value for each sample size:
    draw(n, rng) returns n samples."""
    rng = np.random.default_rng(seed)
    out = []
    for n in sizes:
        est = [exceedance(draw(n, rng), p) for _ in range(repeats)]
        out.append((n, float(np.mean(est)), float(np.std(est, ddof=1))))
    return out
# [end: converge]


# ------------------------------------------------------------ finance
# [start: debt]
def annuity(rate: float, years: int) -> float:
    """Present value of 1 a year for the given years."""
    return (1.0 - (1.0 + rate) ** -years) / rate


def debt_size(cfads_by_case: dict, dscr_by_case: dict, rate: float,
              years: int) -> tuple[float, str]:
    """Largest level-annuity debt that every case can serve at its
    cover ratio: debt service <= CFADS / DSCR in each case."""
    best = None
    for case, cf in cfads_by_case.items():
        ds = cf / dscr_by_case[case]
        if best is None or ds < best[0]:
            best = (ds, case)
    return best[0] * annuity(rate, years), best[1]
# [end: debt]
