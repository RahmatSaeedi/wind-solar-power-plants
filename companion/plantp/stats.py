"""Statistics for resource data, chapter 3 (used again in chapters 13, 15 and 16).

    describe        count, mean, standard deviation, quartiles, extremes
    iqr_outliers    Tukey's fences
    weibull_*       pdf, cdf, mean, mean of v^3, and three fitting methods
    linear_fit      least-squares line with standard errors and a confidence interval
    pearson         correlation coefficient
    effective_n     sample size corrected for lag-1 autocorrelation
    mean_ci         confidence interval of a mean (Student t)

Two-parameter Weibull distribution of wind speed v >= 0, shape k, scale c:
    f(v) = (k/c) (v/c)^(k-1) exp(-(v/c)^k),   F(v) = 1 - exp(-(v/c)^k)
    mean = c Gamma(1 + 1/k),  mean of v^3 = c^3 Gamma(1 + 3/k)
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy import special, stats as sps

from .numerics import bisection


@dataclass
class Summary:
    n: int
    mean: float
    std: float
    minimum: float
    q1: float
    median: float
    q3: float
    maximum: float


def describe(x) -> Summary:
    x = np.asarray(x, dtype=float)
    q1, med, q3 = np.quantile(x, [0.25, 0.5, 0.75])
    return Summary(int(x.size), float(x.mean()), float(x.std(ddof=1)), float(x.min()),
                   float(q1), float(med), float(q3), float(x.max()))


def iqr_outliers(x, k: float = 1.5) -> np.ndarray:
    """Boolean mask of points outside [Q1 - k IQR, Q3 + k IQR] (Tukey's fences).
    An outlier is a point to INVESTIGATE, not to delete."""
    x = np.asarray(x, dtype=float)
    q1, q3 = np.quantile(x, [0.25, 0.75])
    iqr = q3 - q1
    return (x < q1 - k * iqr) | (x > q3 + k * iqr)


# ---- Weibull ---------------------------------------------------------------------------
def weibull_pdf(v, k: float, c: float):
    v = np.asarray(v, dtype=float)
    out = (k / c) * (v / c) ** (k - 1) * np.exp(-(v / c) ** k)
    return np.where(v < 0, 0.0, out)


def weibull_cdf(v, k: float, c: float):
    v = np.asarray(v, dtype=float)
    return np.where(v < 0, 0.0, 1.0 - np.exp(-(np.maximum(v, 0) / c) ** k))


def weibull_mean(k: float, c: float) -> float:
    return c * math.gamma(1.0 + 1.0 / k)


def weibull_mean_cube(k: float, c: float) -> float:
    return c ** 3 * math.gamma(1.0 + 3.0 / k)


def weibull_fit_moments(v) -> tuple[float, float]:
    """Method of moments: choose k so that std/mean of the Weibull equals the data's,
    then c from the mean. Solves Gamma(1+2/k)/Gamma(1+1/k)^2 - 1 = (s/mean)^2 by bisection."""
    v = np.asarray(v, dtype=float)
    cv2 = (v.std(ddof=1) / v.mean()) ** 2

    def g(k):
        return math.gamma(1 + 2 / k) / math.gamma(1 + 1 / k) ** 2 - 1 - cv2
    k = bisection(g, 0.5, 20.0, tol=1e-10).root
    c = v.mean() / math.gamma(1 + 1 / k)
    return k, c


def weibull_fit_mle(v) -> tuple[float, float]:
    """Maximum likelihood (zero speeds removed): solve for k, then c in closed form.
    1/k + mean(ln v) - sum(v^k ln v)/sum(v^k) = 0."""
    v = np.asarray(v, dtype=float)
    v = v[v > 0]
    lv = np.log(v)

    def g(k):
        vk = v ** k
        return 1.0 / k + lv.mean() - (vk * lv).sum() / vk.sum()
    k = bisection(g, 0.2, 20.0, tol=1e-10).root
    c = float(np.mean(v ** k) ** (1.0 / k))
    return k, c


def weibull_fit_lsq(v) -> tuple[float, float]:
    """Least squares on the linearised CDF: ln(-ln(1-F)) = k ln v - k ln c."""
    v = np.sort(np.asarray(v, dtype=float))
    v = v[v > 0]
    n = v.size
    f = (np.arange(1, n + 1) - 0.3) / (n + 0.4)        # median-rank plotting positions
    x, y = np.log(v), np.log(-np.log(1.0 - f))
    k, b = np.polyfit(x, y, 1)
    return float(k), float(math.exp(-b / k))


# ---- regression and correlation ------------------------------------------------------
@dataclass
class LinearFit:
    slope: float
    intercept: float
    se_slope: float
    se_intercept: float
    r2: float
    s_resid: float
    n: int

    def predict(self, x):
        return self.slope * np.asarray(x, dtype=float) + self.intercept

    def slope_ci(self, p: float = 0.95) -> tuple[float, float]:
        t = sps.t.ppf((1 + p) / 2, self.n - 2)
        return self.slope - t * self.se_slope, self.slope + t * self.se_slope


def linear_fit(x, y) -> LinearFit:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = x.size
    if n < 3:
        raise ValueError("need at least three points")
    xm, ym = x.mean(), y.mean()
    sxx = np.sum((x - xm) ** 2)
    slope = np.sum((x - xm) * (y - ym)) / sxx
    intercept = ym - slope * xm
    resid = y - (slope * x + intercept)
    s = math.sqrt(np.sum(resid ** 2) / (n - 2))
    r2 = 1 - np.sum(resid ** 2) / np.sum((y - ym) ** 2)
    return LinearFit(float(slope), float(intercept), float(s / math.sqrt(sxx)),
                     float(s * math.sqrt(1 / n + xm ** 2 / sxx)), float(r2), s, n)


def pearson(x, y) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    return float(np.corrcoef(x, y)[0, 1])


def lag1_autocorrelation(x) -> float:
    x = np.asarray(x, dtype=float) - np.mean(x)
    return float(np.sum(x[1:] * x[:-1]) / np.sum(x * x))


def effective_n(x) -> float:
    """Number of independent observations an autocorrelated series is worth:
    n_eff = n (1 - r1) / (1 + r1) for lag-1 autocorrelation r1 (AR(1) approximation)."""
    r1 = lag1_autocorrelation(x)
    return len(x) * (1 - r1) / (1 + r1)


def mean_ci(x, p: float = 0.95, n_eff: float | None = None) -> tuple[float, float, float]:
    """(mean, low, high): t-interval of the mean; n_eff replaces n when the data are
    autocorrelated (hourly wind speeds are)."""
    x = np.asarray(x, dtype=float)
    n = x.size if n_eff is None else n_eff
    se = x.std(ddof=1) / math.sqrt(n)
    t = sps.t.ppf((1 + p) / 2, max(n - 1, 1))
    m = float(x.mean())
    return m, m - t * se, m + t * se


def gamma_fn(x):
    return special.gamma(x)


# ---- extremes: Gumbel distribution of annual maxima ---------------------------------
EULER_GAMMA = 0.5772156649015329


def gumbel_cdf(x, mu: float, beta: float):
    """F(x) = exp(-exp(-(x - mu) / beta)), beta > 0."""
    return np.exp(-np.exp(-(np.asarray(x, dtype=float) - mu) / beta))


def gumbel_fit_moments(x) -> tuple[float, float]:
    """mu, beta from the sample mean and standard deviation: beta = s sqrt(6) / pi."""
    x = np.asarray(x, dtype=float)
    beta = float(x.std(ddof=1) * math.sqrt(6.0) / math.pi)
    return float(x.mean() - EULER_GAMMA * beta), beta


def gumbel_plot_positions(x) -> tuple[np.ndarray, np.ndarray]:
    """Sorted maxima and reduced variates y = -ln(-ln F), F = i / (n + 1)."""
    xs = np.sort(np.asarray(x, dtype=float))
    f = np.arange(1, xs.size + 1) / (xs.size + 1.0)
    return xs, -np.log(-np.log(f))


def gumbel_fit_lsq(x) -> tuple[float, float]:
    """mu, beta from a straight line x = mu + beta y on the Gumbel plot."""
    xs, y = gumbel_plot_positions(x)
    fit = linear_fit(y, xs)
    return fit.intercept, fit.slope


def return_level(mu: float, beta: float, period_years: float) -> float:
    """Value exceeded on average once in period_years (annual maxima)."""
    if period_years <= 1:
        raise ValueError("return period must exceed one year")
    return mu - beta * math.log(-math.log(1.0 - 1.0 / period_years))


def prob_exceed_in_life(period_years: float, life_years: int) -> float:
    """Chance that the T-year value is exceeded at least once in the life (independent years)."""
    return 1.0 - (1.0 - 1.0 / period_years) ** life_years


# ---- two-state Markov model of a repairable unit -----------------------------------
def markov_stationary(p) -> np.ndarray:
    """Stationary distribution pi of a transition matrix P (rows sum to 1): pi P = pi."""
    p = np.asarray(p, dtype=float)
    if not np.allclose(p.sum(axis=1), 1.0):
        raise ValueError("rows of a transition matrix must sum to 1")
    n = p.shape[0]
    a = np.vstack([p.T - np.eye(n), np.ones(n)])
    b = np.zeros(n + 1)
    b[-1] = 1.0
    pi, *_ = np.linalg.lstsq(a, b, rcond=None)
    return pi


def bayes_posterior(prior: float, sensitivity: float, false_alarm: float) -> float:
    """P(condition | positive test) from P(condition), P(positive | condition) and
    P(positive | no condition), by Bayes' theorem."""
    for v in (prior, sensitivity, false_alarm):
        if not 0.0 <= v <= 1.0:
            raise ValueError("probabilities must lie in [0, 1]")
    num = sensitivity * prior
    return num / (num + false_alarm * (1.0 - prior))


def series_availability(avails) -> float:
    """All blocks needed: product of availabilities (independent failures)."""
    return float(np.prod(np.asarray(avails, dtype=float)))


def parallel_availability(avails) -> float:
    """Any one block suffices: 1 - product of unavailabilities (independent failures)."""
    return float(1.0 - np.prod(1.0 - np.asarray(avails, dtype=float)))


def availability(mtbf_h: float, mttr_h: float) -> float:
    """Long-run fraction of time in service: MTBF / (MTBF + MTTR)."""
    return mtbf_h / (mtbf_h + mttr_h)
