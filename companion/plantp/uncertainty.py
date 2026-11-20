"""Measurement uncertainty in the style of the GUM (JCGM 100:2008), chapter 2.

    from plantp import uncertainty as un
    u_v = un.rectangular(0.1)                      # +-0.1 m/s limits -> 0.0577 m/s
    res = un.combine(lambda rho, v: 0.5 * rho * v**3,
                     {"rho": 1.055, "v": 7.10}, {"rho": 0.010, "v": 0.20})
    print(res.report())                            # uncertainty budget table
    mc = un.monte_carlo(lambda rho, v: 0.5 * rho * v**3,
                        {"rho": ("normal", 1.055, 0.010), "v": ("normal", 7.10, 0.20)})

Contents
  type_a           mean, standard deviation and standard uncertainty of the mean
  rectangular, triangular, from_expanded, from_reading_spec   Type B evaluations
  combine          law of propagation of uncertainty (first-order, uncorrelated or
                   with a correlation matrix), with the uncertainty budget
  monte_carlo      propagation of distributions (the idea of JCGM 101:2008)
  latin_hypercube  stratified uniform samples for variance reduction (chapter 3)
  coverage_factor  Student t factor for a coverage probability and degrees of freedom
  round_result     "y = 1.234(56)"-style rounding: two significant figures in U
  conformity       accept / reject / inconclusive decision with a guard band
  stack_worst_case, stack_rss   tolerance stack-ups

Teaching code: it implements the textbook formulas plainly and is checked by the
tests in companion/tests/test_uncertainty.py against hand calculations.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

SQRT3 = math.sqrt(3.0)
SQRT6 = math.sqrt(6.0)


# ---- Type A ------------------------------------------------------------------------
@dataclass
class TypeA:
    n: int
    mean: float
    s: float             # experimental standard deviation of one observation
    u_mean: float        # standard uncertainty of the mean, s / sqrt(n)
    dof: int             # degrees of freedom, n - 1


def type_a(values) -> TypeA:
    """Type A evaluation from repeated, independent observations."""
    x = np.asarray(values, dtype=float)
    if x.size < 2:
        raise ValueError("a Type A evaluation needs at least two observations")
    s = float(np.std(x, ddof=1))
    return TypeA(int(x.size), float(np.mean(x)), s, s / math.sqrt(x.size), int(x.size - 1))


# ---- Type B ------------------------------------------------------------------------
def rectangular(half_width: float) -> float:
    """Standard uncertainty when the value is equally likely anywhere in +-half_width."""
    if half_width < 0:
        raise ValueError("half-width cannot be negative")
    return half_width / SQRT3


def triangular(half_width: float) -> float:
    """Standard uncertainty for a triangular distribution of half-width a: a / sqrt(6)."""
    if half_width < 0:
        raise ValueError("half-width cannot be negative")
    return half_width / SQRT6


def from_expanded(expanded: float, k: float = 2.0) -> float:
    """Standard uncertainty from a certificate's expanded uncertainty U and coverage factor k."""
    if k <= 0:
        raise ValueError("coverage factor must be positive")
    return expanded / k


def resolution(step: float) -> float:
    """Standard uncertainty from the resolution (last digit) of an indicating instrument:
    the reading is a rounding, so the true value lies within +-step/2."""
    return rectangular(step / 2.0)


def from_reading_spec(reading: float, pct_of_reading: float = 0.0, counts: int = 0,
                      count_size: float = 0.0, pct_of_range: float = 0.0,
                      full_range: float = 0.0) -> tuple[float, float]:
    """A data sheet's accuracy as +-(pct of reading + counts x count size + pct of range).

    Returns (limit a, standard uncertainty a/sqrt(3)); the limit is treated as the
    half-width of a rectangular distribution, which is the usual reading when the
    data sheet gives no distribution.
    """
    a = (abs(reading) * pct_of_reading / 100.0 + counts * count_size
         + full_range * pct_of_range / 100.0)
    return a, rectangular(a)


# ---- propagation -------------------------------------------------------------------
@dataclass
class BudgetRow:
    name: str
    value: float
    u: float             # standard uncertainty of the input
    c: float             # sensitivity coefficient dY/dX
    contribution: float  # |c| * u, in the unit of the result
    share: float         # share of the combined variance (0..1); uncorrelated part only


@dataclass
class Combined:
    y: float
    u_c: float
    rows: list[BudgetRow] = field(default_factory=list)

    @property
    def relative(self) -> float:
        return self.u_c / abs(self.y) if self.y else math.inf

    def expanded(self, k: float = 2.0) -> float:
        return k * self.u_c

    def report(self, unit: str = "", digits: int = 4) -> list[str]:
        lines = [f"{'input':10s} {'value':>11s} {'u(x)':>10s} {'c':>11s} "
                 f"{'|c|u':>10s} {'share':>6s}"]
        for r in self.rows:
            lines.append(f"{r.name:10s} {r.value:11.{digits}g} {r.u:10.3g} {r.c:11.4g} "
                         f"{r.contribution:10.3g} {100 * r.share:5.1f}%")
        lines.append(f"y = {self.y:.{digits + 1}g} {unit}, u_c = {self.u_c:.3g} {unit} "
                     f"({100 * self.relative:.2f} %), U(k=2) = {self.expanded():.3g} {unit}")
        return lines


def sensitivity(f, values: dict, name: str, rel_step: float = 1e-6) -> float:
    """Central-difference estimate of the partial derivative of f with respect to `name`."""
    x0 = values[name]
    h = rel_step * (abs(x0) if x0 else 1.0)
    hi = dict(values, **{name: x0 + h})
    lo = dict(values, **{name: x0 - h})
    return (f(**hi) - f(**lo)) / (2.0 * h)


def combine(f, values: dict, uncertainties: dict, correlation=None) -> Combined:
    """Law of propagation of uncertainty, first order (GUM section 5).

    f              function of keyword arguments, returning the measurand y
    values         best estimates {name: x}
    uncertainties  standard uncertainties {name: u(x)}
    correlation    optional {(name_i, name_j): r_ij}; missing pairs are uncorrelated

    u_c^2 = sum (c_i u_i)^2 + 2 sum_{i<j} c_i c_j u_i u_j r_ij
    """
    names = list(values)
    missing = [n for n in names if n not in uncertainties]
    if missing:
        raise ValueError(f"no uncertainty given for {missing}")
    y = f(**values)
    cs = {n: sensitivity(f, values, n) for n in names}
    var_terms = {n: (cs[n] * uncertainties[n]) ** 2 for n in names}
    variance = sum(var_terms.values())
    if correlation:
        for (a, b), r in correlation.items():
            if not -1.0 <= r <= 1.0:
                raise ValueError("correlation coefficients lie between -1 and 1")
            variance += 2.0 * cs[a] * cs[b] * uncertainties[a] * uncertainties[b] * r
    if variance < 0:
        raise ValueError("negative combined variance: check the correlation matrix")
    u_c = math.sqrt(variance)
    total = sum(var_terms.values()) or 1.0
    rows = [BudgetRow(n, values[n], uncertainties[n], cs[n], abs(cs[n]) * uncertainties[n],
                      var_terms[n] / total) for n in names]
    return Combined(y, u_c, rows)


def relative_power_law(exponents: dict, rel_uncertainties: dict) -> float:
    """Relative standard uncertainty of y = c * prod(x_i ** p_i), uncorrelated inputs:
    (u_y / y)^2 = sum (p_i * u_i / x_i)^2"""
    return math.sqrt(sum((exponents[n] * rel_uncertainties[n]) ** 2 for n in exponents))


# ---- Monte Carlo -------------------------------------------------------------------
@dataclass
class MonteCarlo:
    samples: np.ndarray
    mean: float
    std: float
    low: float           # lower end of the probabilistically symmetric interval
    high: float
    p: float             # coverage probability of [low, high]


def _draw(rng, spec, n):
    kind = spec[0]
    if kind == "normal":
        _, mu, sigma = spec
        return rng.normal(mu, sigma, n)
    if kind == "uniform":                      # ("uniform", centre, half-width)
        _, c, a = spec
        return rng.uniform(c - a, c + a, n)
    if kind == "triangular":                   # ("triangular", centre, half-width)
        _, c, a = spec
        return rng.triangular(c - a, c, c + a, n)
    if kind == "fixed":
        return np.full(n, float(spec[1]))
    raise ValueError(f"unknown distribution {kind!r}")


def monte_carlo(f, distributions: dict, n: int = 200_000, p: float = 0.95,
                seed: int = 20260101) -> MonteCarlo:
    """Propagation of distributions: draw every input from its distribution, evaluate
    f for each draw, and summarise the output distribution.

    distributions  {name: ("normal", mean, std) | ("uniform", centre, half-width) |
                    ("triangular", centre, half-width) | ("fixed", value)}
    The seed is fixed so that the book's numbers can be reproduced exactly.
    """
    if not 0 < p < 1:
        raise ValueError("coverage probability must be between 0 and 1")
    rng = np.random.default_rng(seed)
    draws = {name: _draw(rng, spec, n) for name, spec in distributions.items()}
    y = np.asarray(f(**draws), dtype=float)
    low, high = np.quantile(y, [(1 - p) / 2, (1 + p) / 2])
    return MonteCarlo(y, float(y.mean()), float(y.std(ddof=1)), float(low), float(high), p)


# ---- coverage and reporting --------------------------------------------------------
def latin_hypercube(n: int, dims: int, rng) -> np.ndarray:
    """n points in [0, 1)^dims, exactly one in each of n equal strata of every column.

    Each column is a random permutation of the strata with a uniform jitter inside the
    stratum; transform columns with an inverse CDF (e.g. scipy.stats.norm.ppf)."""
    u = np.empty((n, dims))
    for j in range(dims):
        u[:, j] = (rng.permutation(n) + rng.random(n)) / n
    return u


def coverage_factor(p: float = 0.95, dof: float = math.inf) -> float:
    """Coverage factor k for a coverage probability p: from the normal distribution when
    the degrees of freedom are infinite, from Student's t otherwise."""
    from scipy import stats
    if math.isinf(dof):
        return float(stats.norm.ppf((1 + p) / 2))
    if dof < 1:
        raise ValueError("degrees of freedom must be at least 1")
    return float(stats.t.ppf((1 + p) / 2, dof))


def welch_satterthwaite(u_c: float, contributions: list[tuple[float, float]]) -> float:
    """Effective degrees of freedom: u_c^4 / sum(u_i^4 / nu_i), contributions = [(|c_i|u_i, nu_i)]."""
    denom = sum(ui ** 4 / nu for ui, nu in contributions if not math.isinf(nu))
    return math.inf if denom == 0 else u_c ** 4 / denom


def round_result(y: float, U: float, sig: int = 2) -> tuple[str, str]:
    """Round an expanded uncertainty to `sig` significant figures and the result to the
    same decimal place: round_result(289.8123, 16.27) -> ('290', '16')."""
    if U <= 0:
        raise ValueError("uncertainty must be positive")
    exponent = int(math.floor(math.log10(U)))
    decimals = sig - 1 - exponent
    U_r = round(U, decimals)
    if U_r >= 10 ** (exponent + 1):          # 9.96 -> 10.0 gains a digit
        decimals -= 1
        U_r = round(U, decimals)
    fmt = f"{{:.{max(decimals, 0)}f}}"
    y_r = round(y, decimals)
    return fmt.format(y_r), fmt.format(U_r)


# ---- conformity decisions ------------------------------------------------------------
@dataclass
class Decision:
    verdict: str          # "accept", "reject" or "inconclusive"
    acceptance_limit: float
    reason: str


def conformity(measured: float, U: float, lower: float | None = None,
               upper: float | None = None, rule: str = "guarded") -> Decision:
    """Decide whether a measured value meets a one-sided specification limit.

    rule "simple":  accept if the measured value itself is inside the limit
                    (the risk is shared between buyer and seller).
    rule "guarded": accept only if the whole interval measured +- U is inside the
                    limit, reject only if the whole interval is outside; otherwise
                    the result is inconclusive (guard band w = U).
    Give exactly one of `lower` (value must be >= lower) or `upper` (<= upper).
    """
    if (lower is None) == (upper is None):
        raise ValueError("give exactly one specification limit")
    if U < 0:
        raise ValueError("expanded uncertainty cannot be negative")
    if rule not in ("simple", "guarded"):
        raise ValueError("rule is 'simple' or 'guarded'")
    if lower is not None:
        if rule == "simple":
            ok = measured >= lower
            return Decision("accept" if ok else "reject", lower, "measured value vs limit")
        if measured - U >= lower:
            return Decision("accept", lower + U, "whole interval above the lower limit")
        if measured + U < lower:
            return Decision("reject", lower + U, "whole interval below the lower limit")
        return Decision("inconclusive", lower + U, "interval straddles the lower limit")
    if rule == "simple":
        ok = measured <= upper
        return Decision("accept" if ok else "reject", upper, "measured value vs limit")
    if measured + U <= upper:
        return Decision("accept", upper - U, "whole interval below the upper limit")
    if measured - U > upper:
        return Decision("reject", upper - U, "whole interval above the upper limit")
    return Decision("inconclusive", upper - U, "interval straddles the upper limit")


# ---- tolerance stack-ups -----------------------------------------------------------
def stack_worst_case(tolerances) -> float:
    """Worst-case tolerance of a sum of parts: every part at its limit at once."""
    return float(sum(abs(t) for t in tolerances))


def stack_rss(tolerances) -> float:
    """Root-sum-square tolerance of a sum of independent parts (all limits taken at the
    same confidence): sqrt(sum t_i^2)."""
    return float(math.sqrt(sum(t * t for t in tolerances)))
