"""Chapter 20 - control data for Plant P (teaching values, A-299 to
A-302): plant limits, the hypothetical service requirement, imbalance
penalties, day-ahead and intraday forecasts at the POC (chapter 15
forecasts through model 15.1's plant end), and the teaching prices.

No value here is a grid-code requirement: every limit is a teaching
assumption that the grid operator, the contract and the equipment
would replace (chapters 17, 28 and 55-57).
"""
from __future__ import annotations

import math
from functools import lru_cache

import numpy as np

from companion.ch20 import common  # noqa: F401  (puts plantp on the path)
from companion.ch15 import forecast as f15, sources as s15
from plantp import yieldmodel as ym

# [start: limits]
LIMITS = {                       # teaching (A-299)
    "export_mw": 100.0,          # contract export limit at the POC
    "ramp_pct_min": 10.0,        # max change of export, % of 100 MW a minute
    "pf_min": 0.95,              # reactive capability asked at full output
    "bess_mw": 20.0, "e_min": 4.0, "e_max": 36.0,
    "eta": math.sqrt(0.86),
    "comms_timeout_h": 1,        # hold, then fall back
}
SERVICE = {                      # hypothetical requirement REQ-S01 (A-300)
    "name": "upward reserve",
    "mw": 5.0, "hours": 1.0,     # hold 5 MW of upward power for 1 h
    "window": (18, 22),          # every day from 18:00 to 22:00
    "availability": 0.95,        # measured share of window hours held
}
IMBALANCE = {"short": 30.0, "long": 10.0}   # u per MWh penalty (A-301)
# [end: limits]


def prices():
    """Daily-varying teaching prices of chapter 19 (A-273, A-295)."""
    from companion.ch19 import lab_h
    return lab_h.daily_prices().ravel()


@lru_cache(maxsize=4)
def poc_forecast(lead: int) -> np.ndarray:
    """Forecast of the POC power (before the export limit) for a lead
    in hours: chapter 15 wind and PV forecasts through the plant end."""
    w_f, pv_f = f15.nwp(lead)
    poc, _ = ym.plant_end(w_f, pv_f, s15.ModelConfig(), np.zeros(8760, bool))
    return poc


@lru_cache(maxsize=1)
def poc_actual() -> np.ndarray:
    return s15.plant_year()["poc"]
