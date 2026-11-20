"""Performance, availability and reliability arithmetic for chapter 37.

performance_ratio       PR = (E / P_dc) / (H / G_stc)
pr_temperature          PR corrected to 25 C with a power temperature coefficient
time_availability       up time over the period, with excluded hours removed
energy_availability     actual over potential energy, with exclusions
merge_events            sort, drop duplicates, merge overlaps, clip to a window
event_hours             hours of merged events inside a window
cusum                   one-sided CUSUM of residuals (drift detection)
mtbf_censored           exponential MLE with censored (still running) items
rate_interval           chi-square confidence interval of a failure rate
weibull_mle             two-parameter Weibull fit with right censoring
crow_amsaa_beta         reliability-growth slope of failure times (time-truncated)
tracking_error          RMS and largest error of a response against its demand
response_times          time to 90 % and to settle within a band after a step

Forecast scores live in plantp.yieldmodel (ch 15) and are reused.
"""
from __future__ import annotations

import math

import numpy as np
from scipy import optimize, stats


# [start: pr]
def performance_ratio(e_kwh: float, p_dc_kwp: float, h_kwh_m2: float,
                      g_stc: float = 1.0) -> float:
    """PR: final yield (kWh/kWp) over reference yield (kWh/m2 / 1 kW/m2)."""
    return (e_kwh / p_dc_kwp) / (h_kwh_m2 / g_stc)


def pr_temperature(pr: float, t_cell_mean: float,
                   gamma: float = -0.0035) -> float:
    """PR corrected to 25 C cell temperature (gamma per K, negative)."""
    return pr / (1 + gamma * (t_cell_mean - 25.0))
# [end: pr]


# [start: availability]
def time_availability(up_h: float, period_h: float,
                      excluded_h: float = 0.0) -> float:
    """Time-based availability: up time over the period less excluded time."""
    return up_h / (period_h - excluded_h)


def energy_availability(actual_mwh: float, lost_mwh: float,
                        excluded_lost_mwh: float = 0.0) -> float:
    """Production-based availability: actual over potential energy, where the
    losses charged to the plant exclude those excluded by agreement."""
    charged = lost_mwh - excluded_lost_mwh
    return actual_mwh / (actual_mwh + charged)
# [end: availability]


# [start: events]
def merge_events(events, start: float, end: float):
    """Events (t0, t1) in hours: drop exact duplicates and those without an
    end, merge overlaps, clip to [start, end]. Returns merged intervals."""
    clean = sorted({(a, b) for a, b in events
                    if a is not None and b is not None and b > a})
    out = []
    for a, b in clean:
        a, b = max(a, start), min(b, end)
        if b <= a:
            continue
        if out and a <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        else:
            out.append((a, b))
    return out


def event_hours(events, start: float, end: float) -> float:
    return sum(b - a for a, b in merge_events(events, start, end))
# [end: events]


# [start: cusum]
def cusum(residuals, k: float, h: float):
    """One-sided lower CUSUM: index where the sum of (-r - k) first exceeds h,
    or None. Detects a sustained drop of the residual below zero."""
    s = 0.0
    for i, r in enumerate(residuals):
        s = max(0.0, s + (-r - k))
        if s > h:
            return i
    return None
# [end: cusum]


# [start: mtbf]
def mtbf_censored(failure_hours, running_hours) -> float:
    """Exponential MLE: all exposure (failed and still running) over
    the number of failures."""
    n = len(failure_hours)
    if n == 0:
        raise ValueError("no failures: give a bound, not an estimate")
    return (sum(failure_hours) + sum(running_hours)) / n


def rate_interval(failures: int, exposure_h: float, conf: float = 0.9):
    """Two-sided interval of a constant failure rate (per hour)."""
    a = 1 - conf
    lo = 0.0
    if failures:
        lo = stats.chi2.ppf(a / 2, 2 * failures) / (2 * exposure_h)
    hi = stats.chi2.ppf(1 - a / 2, 2 * failures + 2) / (2 * exposure_h)
    return lo, hi
# [end: mtbf]


# [start: weibull]
def weibull_mle(failures, censored):
    """Two-parameter Weibull (shape k, scale lam) by maximum likelihood with
    right-censored items."""
    t_f = np.asarray(failures, float)
    t_c = np.asarray(censored, float)

    def nll(p):
        k, lam = np.exp(p)
        z_f, z_c = t_f / lam, t_c / lam
        ll = np.sum(np.log(k / lam) + (k - 1) * np.log(z_f) - z_f ** k)
        return -(ll - np.sum(z_c ** k))
    x0 = [0.0, math.log(np.mean(np.r_[t_f, t_c]))]
    res = optimize.minimize(nll, x0=x0, method="Nelder-Mead")
    k, lam = np.exp(res.x)
    return float(k), float(lam)


def crow_amsaa_beta(times, t_end: float) -> float:
    """Reliability-growth slope (time-truncated): beta < 1 improving,
    > 1 deteriorating, about 1 steady."""
    t = np.asarray(times, float)
    n = len(t)
    return n / np.sum(np.log(t_end / t))
# [end: weibull]


# [start: service]
def tracking_error(demand, response):
    """RMS and largest absolute error of a response against its demand."""
    e = np.asarray(response, float) - np.asarray(demand, float)
    return float(np.sqrt(np.mean(e ** 2))), float(np.max(np.abs(e)))


def response_times(t, response, start: float, final: float, band: float):
    """After a step at t = 0 from start to final: time to reach 90 % of the
    change and time after which the response stays within +/- band."""
    t = np.asarray(t, float)
    r = np.asarray(response, float)
    target90 = start + 0.9 * (final - start)
    up = final > start
    hit = np.where(r >= target90)[0] if up else np.where(r <= target90)[0]
    t90 = float(t[hit[0]]) if len(hit) else math.inf
    outside = np.where(np.abs(r - final) > band)[0]
    if not len(outside):
        t_settle = 0.0
    elif outside[-1] + 1 < len(t):
        t_settle = float(t[outside[-1] + 1])
    else:
        t_settle = math.inf
    return t90, t_settle
# [end: service]
