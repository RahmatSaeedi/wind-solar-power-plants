"""Loads, the grid node and requirements (chapter 17): load metrics from
interval data, duration curves, peaks by resolution, diversity, growth,
critical-load hours from a battery, net flow at a node, bounded
connection checks (thermal, voltage rise, short-circuit ratio), and a
simple requirement record.

Powers in MW, energies in MWh unless stated; one value per interval.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np


# ------------------------------------------------------------ metrics
# [start: metrics]
def metrics(p_mw, dt_h: float = 1.0) -> dict:
    """Energy (MWh), peak and minimum (MW), mean, load factor
    (mean / peak) and the hour of the peak."""
    p = np.asarray(p_mw, float)
    e = float(p.sum() * dt_h)
    peak = float(p.max())
    return {"energy": e, "peak": peak, "min": float(p.min()),
            "mean": float(p.mean()), "load_factor": float(p.mean()) / peak,
            "peak_at": int(p.argmax())}


def duration_curve(p_mw) -> np.ndarray:
    """Values sorted from the highest to the lowest."""
    return np.sort(np.asarray(p_mw, float))[::-1]


def peak_by_resolution(p_fine, steps: int) -> float:
    """Peak of the block means of `steps` intervals (e.g. 15-minute
    data averaged to hours with steps = 4)."""
    p = np.asarray(p_fine, float)
    n = len(p) // steps * steps
    return float(p[:n].reshape(-1, steps).mean(axis=1).max())


def diversity(loads) -> tuple[float, float]:
    """Coincidence factor (peak of the sum / sum of the peaks) and its
    inverse, the diversity factor."""
    loads = [np.asarray(x, float) for x in loads]
    cf = float(np.sum(loads, axis=0).max()) / sum(float(x.max()) for x in loads)
    return cf, 1.0 / cf
# [end: metrics]


def grow(p_mw, rate: float, years: int):
    """Load after `years` of growth at `rate` a year (same shape)."""
    return np.asarray(p_mw, float) * (1.0 + rate) ** years


# ------------------------------------------------------------ resilience
def critical_hours(critical_mw: float, e_mwh: float, p_mw: float,
                   soc: float = 0.9, dod_floor: float = 0.1,
                   eff: float = 0.93) -> float:
    """Hours a battery can carry a constant critical load from the given
    state of charge down to its floor (one-way efficiency eff)."""
    if critical_mw > p_mw:
        return 0.0
    return (soc - dod_floor) * e_mwh * eff / critical_mw


# ------------------------------------------------------------ the node
# [start: checks]
def net_flow(load_mw, gen_mw):
    """Flow from the node to the higher grid (positive = export up)."""
    return np.asarray(gen_mw, float) - np.asarray(load_mw, float)


def voltage_rise(p_mw, q_mvar, r_ohm: float, x_ohm: float, v_kv: float):
    """Approximate voltage rise at the sending end of a line in per cent:
    dV/V = (R P + X Q) / V^2 (Q > 0 exported, inductive line)."""
    return 100.0 * (r_ohm * np.asarray(p_mw) + x_ohm * np.asarray(q_mvar)) / v_kv ** 2


def thermal_ok(s_mva, rating_mva: float) -> bool:
    return bool(np.max(np.abs(np.asarray(s_mva, float))) <= rating_mva)


def short_circuit_ratio(s_sc_mva: float, p_mw: float) -> float:
    """Short-circuit power at the POC over the plant's rated power."""
    return s_sc_mva / p_mw
# [end: checks]


# ------------------------------------------------------------ requirements
# [start: requirement]
@dataclass
class Requirement:
    rid: str
    text: str
    measure: str                      # how it is verified
    source: str                       # stakeholder or document
    status: str = "assumed"           # verified | assumed | open
    priority: str = "must"            # must | should | could
    links: list = field(default_factory=list)

    def is_measurable(self) -> bool:
        """A requirement is measurable when its measure names a quantity
        with a number (a crude check used in the lab)."""
        return any(ch.isdigit() for ch in self.measure)
# [end: requirement]
