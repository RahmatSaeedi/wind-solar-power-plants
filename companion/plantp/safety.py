"""Occupational safety, fire and emergency tools (chapter 32).

Teaching forms a student can check by hand: a likelihood x severity risk
score and its band, an incident rate with a Poisson confidence interval,
the clearance a fall-arrest system needs, air changes and dilution
ventilation, radiant heat from a fire treated as a point source, the
autonomy of a water store, and the share of responses inside a target
time.

These support reasoning about risk; they are not procedures. Isolation,
permits, rescue, fire protection and security follow the project's
management system, the authority having jurisdiction and competent
specialists.
"""
from __future__ import annotations

import math

import numpy as np
from scipy import stats

BANDS = ((4, "low"), (9, "medium"), (16, "high"), (25, "very high"))


# [start: risk]
def risk_score(likelihood: int, severity: int) -> int:
    """Teaching 5 x 5 matrix: score = likelihood x severity (1..25)."""
    if not (1 <= likelihood <= 5 and 1 <= severity <= 5):
        raise ValueError("likelihood and severity run from 1 to 5")
    return likelihood * severity


def risk_band(score: int) -> str:
    """Band of a score in the teaching matrix."""
    for top, name in BANDS:
        if score <= top:
            return name
    return "very high"


def incident_rate(events: int, hours: float, per: float = 200_000.0,
                  conf: float = 0.90) -> tuple[float, float, float]:
    """(rate, low, high) per `per` hours with an exact Poisson interval."""
    a = 1 - conf
    low = stats.chi2.ppf(a / 2, 2 * events) / 2 if events > 0 else 0.0
    high = stats.chi2.ppf(1 - a / 2, 2 * events + 2) / 2
    f = per / hours
    return events * f, low * f, high * f
# [end: risk]


# [start: height]
def fall_clearance(lanyard_m: float, deceleration_m: float,
                   harness_m: float = 0.3, body_m: float = 1.5,
                   margin_m: float = 1.0) -> float:
    """Clear height needed below the anchor for a fall-arrest system:
    lanyard + deceleration + harness stretch + D-ring to feet + margin."""
    return lanyard_m + deceleration_m + harness_m + body_m + margin_m
# [end: height]


def air_changes(volume_m3: float, flow_m3_h: float) -> float:
    """Air changes per hour of a space."""
    return flow_m3_h / volume_m3


def dilution_flow(generation_m3_h: float, limit_fraction: float,
                  mixing: float = 3.0) -> float:
    """Steady fresh-air flow (m3/h) that keeps a released gas below a
    volume fraction, with a mixing (safety) factor for poor mixing."""
    return mixing * generation_m3_h / limit_fraction


# [start: fire]
def heat_flux_point(q_kw: float, radiant_fraction: float, r_m: float) -> float:
    """Radiant heat flux (kW/m2) at distance r from a fire treated as a
    point source: chi Q / (4 pi r^2)."""
    return radiant_fraction * q_kw / (4 * math.pi * r_m * r_m)


def distance_for_flux(q_kw: float, radiant_fraction: float,
                      flux_kw_m2: float) -> float:
    """Distance (m) at which the point-source flux falls to a criterion."""
    return math.sqrt(radiant_fraction * q_kw / (4 * math.pi * flux_kw_m2))


def autonomy_minutes(volume_m3: float, rate_l_min: float) -> float:
    """Minutes a store lasts at a steady draw."""
    return volume_m3 * 1000 / rate_l_min
# [end: fire]


def coverage_fraction(times_min, target_min: float) -> float:
    """Share of response times at or under a target."""
    t = np.asarray(times_min, float)
    return float((t <= target_min).mean())
