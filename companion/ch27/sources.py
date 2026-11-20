"""Chapter 27 - teaching data for Plant P's power quality and service
performance (A-336 to A-340): the units' harmonic emission, the network
at the 33 kV bus and the POC, a synthetic measurement week, synthetic
service tests, and filter and meter data.

Values are illustrative of their kind, not a maker's data, an
operator's limit or a standard's table.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch27 import common  # noqa: F401  (puts plantp on the path)

# [start: emission]
# harmonic current of one unit at full power, % of its rated current (A-336)
EMISSION = {
    "PV inverter": {5: 1.2, 7: 0.8, 11: 0.5, 13: 0.4, 23: 0.3, 25: 0.3},
    "wind converter": {5: 1.5, 7: 1.0, 11: 0.6, 13: 0.5, 23: 0.2, 25: 0.2},
    "BESS PCS": {5: 1.0, 7: 0.7, 11: 0.4, 13: 0.3, 23: 0.3, 25: 0.3},
}
UNITS = {"PV inverter": 10, "wind converter": 12, "BESS PCS": 4}   # 5 MW class each
# [end: emission]

NET = dict(   # network (A-337): POC from ch 17, 33 kV bus from ch 23/26
    s_sc_poc=1500.0, xr_poc=8.0, s_sc_33=365.0, xr_33=10.0,
    q_cables=1.77, kv_33=33.0, kv_132=132.0,
    background_v5=1.0, background_v7=0.6)     # % of nominal at the POC, before the plant

FILTER = dict(q_mvar=5.0, h_tune=4.7, quality=40.0, cap_tol=0.05)   # A-340


def week(seed: int = 271) -> dict:
    """A synthetic week of 10-minute values at the POC (A-338): plant
    output from a daily PV shape and a wind random walk, background 5th
    harmonic voltage with an evening peak from the local network, and the
    plant's own contribution growing with its output."""
    rng = np.random.default_rng(seed)
    n = 7 * 144
    t = np.arange(n) / 144.0                    # days
    hour = (t % 1) * 24
    pv = np.clip(np.sin(math.pi * (hour - 6) / 12), 0, None) * 45 * (0.7 + 0.3 * rng.random(n))
    wind = np.clip(30 + np.cumsum(rng.normal(0, 1.5, n)), 0, 55)
    p = np.clip(pv + wind, 0, 100)
    bg = 1.0 + 0.9 * np.exp(-((hour - 20) / 2.0) ** 2) + rng.normal(0, 0.05, n)
    plant = 0.008 * p                           # % per MW at the POC (teaching)
    v5 = np.sqrt(bg ** 2 + plant ** 2)          # random-phase combination
    q = rng.normal(0, 1.0, n)
    return {"t_day": t, "hour": hour, "p_mw": p, "q_mvar": q, "v5_pct": v5,
            "bg5_pct": bg, "plant5_pct": plant}


def voltage_step(seed: int = 272) -> dict:
    """Synthetic record of a voltage set-point step at the POC (A-339):
    reactive power response sampled every 0.1 s, with noise."""
    rng = np.random.default_rng(seed)
    t = np.arange(0, 20, 0.1)
    tau, delay = 0.9, 0.3
    resp = np.where(t < delay, 0.0, 1 - np.exp(-(t - delay) / tau) * (np.cos(1.2 * (t - delay))
                                                                       - 0.25 * np.sin(1.2 * (t - delay))))
    q = 20.0 * resp + rng.normal(0, 0.2, len(t))
    return {"t": t, "q": q, "q0": 0.0, "q1": 20.0}


def frequency_event(seed: int = 273) -> dict:
    """Synthetic over-frequency event (A-339): 1-s samples of frequency
    and the plant's active power (droop 4 %, deadband 0.2 Hz, from 80 MW,
    on 100 MW), with measurement noise."""
    rng = np.random.default_rng(seed)
    t = np.arange(0, 300)
    f = 50 + 0.5 * np.exp(-((t - 120) / 60.0) ** 2) + rng.normal(0, 0.005, len(t))
    eff = np.maximum(np.abs(f - 50) - 0.2, 0) * np.sign(f - 50)
    p = 80 - 100 * eff / (50 * 0.04) + rng.normal(0, 0.3, len(t))
    return {"t": t, "f": f, "p": p}
