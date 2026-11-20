"""Plant operation helpers (chapter 51).

Shift logs and handovers checked against what they must hold, lost energy
attributed to its cause, forecast bias tracked, a service's availability,
water metered against the model, records that went stale, and the
autonomy left on a backup source. Pure functions on plain data; teaching
models, not an operating procedure.
"""
from __future__ import annotations

import numpy as np


# [start: log]
def check_log(entries, required, hours=range(24)) -> dict:
    """entries: list of dicts with an 'hour' and fields. Returns entries
    missing a required field and the hours with no entry at all."""
    missing = [(e.get("hour"), f) for e in entries for f in required
               if not e.get(f)]
    seen = {e.get("hour") for e in entries}
    silent = [h for h in hours if h not in seen]
    return dict(missing=missing, silent=silent)
# [end: log]


# [start: lost]
def lost_energy(available, exported, cause) -> dict:
    """Energy available but not exported, by the cause recorded for each
    hour (MWh for hourly MW). Hours with a loss and no cause go to
    'unexplained'."""
    gap = np.asarray(available, float) - np.asarray(exported, float)
    lost = np.clip(gap, 0, None)
    out: dict[str, float] = {}
    for h, x in enumerate(lost):
        if x <= 1e-9:
            continue
        c = cause.get(h) or "unexplained"
        out[c] = out.get(c, 0.0) + float(x)
    return out
# [end: lost]


def rolling_bias(forecast, actual, window: int) -> np.ndarray:
    """Mean of (forecast - actual) over the last `window` values."""
    e = np.asarray(forecast, float) - np.asarray(actual, float)
    k = np.ones(window) / window
    return np.convolve(e, k, mode="valid")


def service_availability(held, window) -> float:
    """Share of the service-window hours in which the service was held."""
    held = np.asarray(held, bool)
    window = np.asarray(window, bool)
    return float(held[window].mean()) if window.any() else float("nan")


def stale(records: dict, today, max_days: int) -> list:
    """Records whose last update (a date, or None) is older than max_days."""
    return [k for k, d in records.items()
            if d is None or (today - d).days > max_days]


def autonomy_h(capacity_kwh: float, load_kw: float,
               reserve: float = 0.2) -> float:
    """Hours a backup source carries the load, keeping a reserve share."""
    return capacity_kwh * (1 - reserve) / load_kw
