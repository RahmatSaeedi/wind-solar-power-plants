"""Environmental and social management tools (chapter 33).

Teaching forms a student can check by hand: adding sound levels, sound at
a receiver from a point source with air absorption, an expected collision
count from passages, collision probability and avoidance, a lifecycle
inventory per kWh with a Monte Carlo of its uncertainty, the income a
land-based livelihood loses, and a red/amber/green status of an indicator.

These support assessment and planning; permits, studies and decisions
belong to the authorities, qualified specialists and affected people.
"""
from __future__ import annotations

import math

import numpy as np


# [start: sound]
def db_sum(levels) -> float:
    """Energy sum of sound levels in dB."""
    return 10 * math.log10(sum(10 ** (lv / 10) for lv in levels))


def noise_at(lw_db: float, r_m: float, alpha_db_km: float = 2.0,
             ground_db: float = 0.0) -> float:
    """Sound pressure level at r from a point source: geometric spreading
    (20 log r + 11), air absorption alpha r and a ground term."""
    return (lw_db - 20 * math.log10(r_m) - 11 - alpha_db_km * r_m / 1000
            - ground_db)
# [end: sound]


# [start: birds]
def collision_estimate(passages: float, p_collision: float,
                       avoidance: float) -> float:
    """Expected collisions a year: passages through the rotor-swept zone x
    chance of a strike for one passage x (1 - avoidance)."""
    return passages * p_collision * (1 - avoidance)
# [end: birds]


# [start: lca]
def inventory_total(items: dict[str, tuple[float, float]]) -> float:
    """Sum of amount x factor over the items {name: (amount, factor)}."""
    return sum(a * f for a, f in items.values())


def per_kwh(total_kg: float, energy_kwh: float) -> float:
    """Grams of CO2e per kWh delivered."""
    return total_kg * 1000 / energy_kwh


def inventory_mc(items: dict[str, tuple[float, float, float]], n: int = 20_000,
                 seed: int = 33) -> np.ndarray:
    """Monte Carlo totals; items {name: (amount, factor, cov of factor)},
    each factor lognormal with its median and coefficient of variation."""
    rng = np.random.default_rng(seed)
    tot = np.zeros(n)
    for a, f, cov in items.values():
        sig = math.sqrt(math.log(1 + cov * cov))
        tot += a * f * np.exp(rng.normal(0, sig, n))
    return tot
# [end: lca]


def livelihood_income(area_ha: float, animals_per_ha: float,
                      income_per_animal: float) -> float:
    """Yearly income a grazing area supports (teaching carrying capacity)."""
    return area_ha * animals_per_ha * income_per_animal


def kpi_rag(value: float, target: float, tolerance: float,
            higher_is_better: bool = True) -> str:
    """Green within target, amber within tolerance of it, red beyond."""
    gap = (target - value) if higher_is_better else (value - target)
    if gap <= 0:
        return "green"
    return "amber" if gap <= tolerance else "red"


# [start: carcass]
def persistence_share(mean_days: float, interval_days: float) -> float:
    """Chance a carcass is still there at the next search, averaged over
    the interval (exponential removal with mean persistence mean_days)."""
    x = interval_days / mean_days
    return (1 - math.exp(-x)) / x


def fatality_estimate(found: float, searcher: float, mean_days: float,
                      interval_days: float, area_share: float) -> float:
    """Fatalities from carcasses found: divide by the chance of finding
    one (searcher efficiency x persistence x share of area searched)."""
    p = searcher * persistence_share(mean_days, interval_days) * area_share
    return found / p
# [end: carcass]


# [start: transit]
def transit_probability(r: float, chord: float, pitch_deg: float,
                        blades: int, omega: float, v_bird: float,
                        length: float, span: float) -> float:
    """Chance a bird flying straight through the rotor at radius r is
    struck (simplified single-transit model, flapping flight)."""
    a = v_bird / (r * omega)                   # bird speed / blade speed
    g = math.radians(pitch_deg)
    depth = abs(chord * math.sin(g) + a * chord * math.cos(g))
    rate = blades * omega / (2 * math.pi * v_bird)
    return min(rate * (depth + max(length, span * a)), 1.0)
# [end: transit]


def energy_difference_db(total_db: float, background_db: float) -> float:
    """Level of a source alone from a measured total and its background."""
    return 10 * math.log10(10 ** (total_db / 10) - 10 ** (background_db / 10))
