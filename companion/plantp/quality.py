"""Manufacturing quality arithmetic (chapter 40): process capability and
the share out of tolerance, Shewhart X-bar/R limits with their constants
computed by numerical integration (not copied from a table), yield and
rolled throughput yield, takt and line balance, operating-characteristic
curves of single sampling plans, gauge R&R by two-way ANOVA, FMEA
ranking, power-law (Crow-AMSAA) reliability growth, the escape chain of a
defect through inspection stages, the test uncertainty ratio and the
tension in a sling leg.

Plain Python plus numpy; every function is checked by hand in
companion/tests/test_ch40_quality.py.
"""
from __future__ import annotations

import math
from statistics import mean, stdev

import numpy as np

from plantp.performance import crow_amsaa_beta


# [start: capability]
def cp_cpk(values, lsl, usl) -> tuple[float, float, float, float]:
    """Mean, standard deviation, Cp and Cpk of a measured characteristic;
    a limit may be None (one-sided: Cp is then nan)."""
    m, s = mean(values), stdev(values)
    sides = [x for x in ((usl - m) if usl is not None else None,
                         (m - lsl) if lsl is not None else None)
             if x is not None]
    cp = (usl - lsl) / (6 * s) if None not in (lsl, usl) else math.nan
    return m, s, cp, min(sides) / (3 * s)


def phi(z: float) -> float:
    """Standard normal cumulative distribution."""
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def ppm_out(m: float, s: float, lsl, usl) -> float:
    """Parts per million outside the limits (None = no limit), for a
    normal process."""
    low = phi((lsl - m) / s) if lsl is not None else 0.0
    high = 1 - phi((usl - m) / s) if usl is not None else 0.0
    return 1e6 * (low + high)
# [end: capability]


def d2_d3(n: int, step: float = 0.02, lim: float = 7.0) -> tuple[float, float]:
    """Mean (d2) and standard deviation (d3) of the range of n standard
    normal values, by numerical integration of the range distribution."""
    if n < 2:
        raise ValueError("a subgroup needs at least two values")
    x = np.arange(-lim, lim + step / 2, step)
    erf = np.vectorize(math.erf)
    F = 0.5 * (1 + erf(x / math.sqrt(2)))
    d2 = float(np.sum(1 - F ** n - (1 - F) ** n) * step)
    Fx, Fy = np.meshgrid(F, F, indexing="ij")        # Fx = F(x), Fy = F(y)
    upper = np.triu(np.ones_like(Fx, dtype=bool), k=1)   # x < y
    g = 1 - Fy ** n - (1 - Fx) ** n + np.clip(Fy - Fx, 0, 1) ** n
    diag = np.diagonal(g).sum()                  # x = y, half weight (trapezoid)
    e_r2 = float(2 * (np.sum(g[upper]) + 0.5 * diag) * step * step)
    return d2, math.sqrt(max(e_r2 - d2 * d2, 0.0))


# [start: chart]
def xbar_r_limits(subgroups) -> dict[str, float]:
    """Centre lines and 3-sigma limits of X-bar and R charts."""
    n = len(subgroups[0])
    d2, d3 = d2_d3(n)
    xbars = [mean(g) for g in subgroups]
    ranges = [max(g) - min(g) for g in subgroups]
    xbb, rbar = mean(xbars), mean(ranges)
    a2 = 3 / (d2 * math.sqrt(n))
    return dict(x_centre=xbb, x_ucl=xbb + a2 * rbar, x_lcl=xbb - a2 * rbar,
                r_centre=rbar, r_ucl=rbar * (1 + 3 * d3 / d2),
                r_lcl=rbar * max(0.0, 1 - 3 * d3 / d2),
                sigma=rbar / d2)
# [end: chart]


def rty(yields) -> float:
    """Rolled throughput yield: the chance a unit passes every step first time."""
    out = 1.0
    for y in yields:
        out *= y
    return out


def takt(available_h: float, demand: float) -> float:
    """Hours available per unit demanded."""
    return available_h / demand


def line_balance(times: dict[str, float]) -> dict[str, float | str]:
    """Bottleneck, its cycle time and the balance efficiency of a line."""
    neck = max(times, key=times.get)
    cyc = times[neck]
    return dict(bottleneck=neck, cycle=cyc,
                efficiency=sum(times.values()) / (len(times) * cyc))


# [start: sampling]
def p_accept(n: int, c: int, p: float) -> float:
    """Chance a lot with defective share p passes a plan: sample n,
    accept if at most c defectives (binomial)."""
    return sum(math.comb(n, k) * p ** k * (1 - p) ** (n - k)
               for k in range(c + 1))


def find_plan(aql: float, ltpd: float, alpha: float = 0.05,
              beta: float = 0.10, n_max: int = 1000) -> tuple[int, int]:
    """Smallest single plan (n, c) that accepts good lots (p = aql) with
    chance >= 1 - alpha and bad lots (p = ltpd) with chance <= beta."""
    for n in range(1, n_max + 1):
        for c in range(0, n + 1):
            if p_accept(n, c, ltpd) > beta:
                break
            if p_accept(n, c, aql) >= 1 - alpha:
                return n, c
    raise ValueError("no plan within n_max")
# [end: sampling]


# [start: grr]
def grr_anova(data) -> dict[str, float]:
    """Gauge R&R from data[part][operator][repeat] by two-way ANOVA with
    interaction; returns variance components, %GRR and distinct categories."""
    x = np.asarray(data, dtype=float)
    a, b, n = x.shape
    g = x.mean()
    pm, om, cm = x.mean(axis=(1, 2)), x.mean(axis=(0, 2)), x.mean(axis=2)
    ss_p = b * n * np.sum((pm - g) ** 2)
    ss_o = a * n * np.sum((om - g) ** 2)
    ss_c = n * np.sum((cm - g) ** 2)
    ss_e = np.sum((x - cm[:, :, None]) ** 2)
    ms_p, ms_o = ss_p / (a - 1), ss_o / (b - 1)
    ms_i = (ss_c - ss_p - ss_o) / ((a - 1) * (b - 1))
    ms_e = ss_e / (a * b * (n - 1))
    rep = ms_e
    inter = max(0.0, (ms_i - ms_e) / n)
    oper = max(0.0, (ms_o - ms_i) / (a * n))
    part = max(0.0, (ms_p - ms_i) / (b * n))
    grr = rep + oper + inter
    return dict(repeatability=rep, reproducibility=oper + inter, part=part,
                grr_pct=100 * math.sqrt(grr / (grr + part)),
                ndc=math.floor(1.41 * math.sqrt(part / grr)))
# [end: grr]


def rpn(s: int, o: int, d: int) -> int:
    """Risk priority number, each rating 1-10."""
    for v in (s, o, d):
        if not 1 <= v <= 10:
            raise ValueError("ratings run from 1 to 10")
    return s * o * d


def severity_class(s: int) -> int:
    """2 for severity 9-10 (safety or law), 1 for 7-8, 0 below."""
    return 2 if s >= 9 else (1 if s >= 7 else 0)


def fmea_rank(rows):
    """Order FMEA rows by severity class first, then by severity x
    occurrence (criticality), then by detection; RPN only breaks ties."""
    return sorted(rows, key=lambda r: (-severity_class(r["s"]),
                                       -r["s"] * r["o"], -r["d"],
                                       -rpn(r["s"], r["o"], r["d"])))


# [start: growth]
def crow_amsaa(times, T: float) -> dict[str, float]:
    """Power-law growth model fitted by maximum likelihood to cumulative
    failure times of a test stopped at time T (beta as in ch 37)."""
    n = len(times)
    beta = float(crow_amsaa_beta(times, T))
    lam = n / T ** beta
    return dict(n=n, beta=beta, lam=lam, mtbf_now=T / (n * beta),
                mtbf_cum=T / n)
# [end: growth]


def escape(p_defect: float, detections) -> float:
    """Share of units that leave the factory with the defect, after
    stages that each find it with the given chance."""
    out = p_defect
    for d in detections:
        out *= 1 - d
    return out


def tur(tol_half: float, u95: float) -> float:
    """Test uncertainty ratio: half the tolerance over the expanded
    uncertainty of the measurement."""
    return tol_half / u95


def sling_leg(weight_kn: float, legs: int, angle_deg: float) -> float:
    """Tension in each leg of a symmetric sling, the angle measured from
    the horizontal (a planning number; lifts are planned by competent people)."""
    if not 0 < angle_deg <= 90:
        raise ValueError("angle from the horizontal must be in (0, 90]")
    return weight_kn / (legs * math.sin(math.radians(angle_deg)))
