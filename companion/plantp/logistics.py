"""Transport, lifting and installation logistics (chapter 31).

Teaching forms a student can check by hand: axle loads of a multi-axle
trailer, a simple bridge check, convoy travel time, a crane's capacity
read from its load chart, lift utilisation, wind force on a suspended
load, weather windows in an hourly wind series, desiccant for packed
equipment, laydown area and emergency response time.

These are planning tools only. An approved lift plan uses the crane's
own load charts, the maker's lifting instructions and a competent lift
engineer's review; routes follow the authority's permit.
"""
from __future__ import annotations

import math

import numpy as np

G = 9.81


# [start: route]
def axle_loads(payload_t: float, tractor_t: float, trailer_t: float,
               trailer_axles: int, tractor_axles: int = 3,
               tractor_share: float = 0.25) -> tuple[float, float]:
    """(kN per tractor axle, kN per trailer axle): the tractor carries a
    share of the payload on its axles, the trailer the rest."""
    on_tractor = tractor_t + tractor_share * payload_t
    on_trailer = trailer_t + (1 - tractor_share) * payload_t
    return on_tractor * G / tractor_axles, on_trailer * G / trailer_axles


def bridge_moment_ratio(load_kn: float, group_m: float, span_m: float,
                        design_kn_m: float) -> float:
    """Mid-span moment of an axle group spread uniformly over group_m on
    a simple span, P (L/4 - a/8), over the bridge's allowed moment."""
    a = min(group_m, span_m)
    return load_kn * (span_m / 4 - a / 8) / design_kn_m
# [end: route]


def convoy_time(km_by_speed: list[tuple[float, float]],
                stops_h: float = 0.0) -> float:
    """Hours for a convoy over (km, km/h) stretches plus stops."""
    return sum(km / v for km, v in km_by_speed) + stops_h


# [start: crane]
def chart_capacity(radius_m: float, chart: list[tuple[float, float]]) -> float:
    """Capacity (t) at a radius by straight-line interpolation of a load
    chart [(radius m, capacity t)], zero beyond its last radius."""
    r = np.array([p[0] for p in chart])
    c = np.array([p[1] for p in chart])
    if radius_m > r[-1]:
        return 0.0
    return float(np.interp(radius_m, r, c))


def lift_utilisation(load_t: float, rigging_t: float, radius_m: float,
                     chart: list[tuple[float, float]]) -> float:
    """(load + rigging) / chart capacity at the radius."""
    cap = chart_capacity(radius_m, chart)
    return math.inf if cap == 0 else (load_t + rigging_t) / cap


def wind_on_load(v: float, area_m2: float, cd: float = 1.2,
                 rho: float = 1.225) -> float:
    """Wind force on a suspended load (N)."""
    return 0.5 * rho * v * v * cd * area_m2
# [end: crane]


def weather_windows(speed, limit: float, hours_needed: int) -> int:
    """Number of non-overlapping runs of at least hours_needed consecutive
    hours with speed below limit (each run counted once per full block)."""
    ok = np.asarray(speed) < limit
    count, run = 0, 0
    for flag in ok:
        run = run + 1 if flag else 0
        if run == hours_needed:
            count += 1
            run = 0
    return count


def desiccant_kg(volume_m3: float, months: float,
                 kg_per_m3_month: float = 0.25) -> float:
    """Teaching desiccant quantity for a sealed package (kg)."""
    return volume_m3 * months * kg_per_m3_month


def laydown_area(footprints_m2: list[float],
                 access_factor: float = 1.6) -> float:
    """Laydown area for stored items with access aisles (m2)."""
    return sum(footprints_m2) * access_factor


def response_time(km: float, speed_kmh: float, mobilise_min: float,
                  access_min: float) -> float:
    """Minutes from call to reaching a casualty: mobilise + drive + access."""
    return mobilise_min + km / speed_kmh * 60 + access_min
