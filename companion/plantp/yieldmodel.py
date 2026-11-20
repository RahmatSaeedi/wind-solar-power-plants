"""Energy-yield modelling and short-term forecasting (chapter 15): a loss
waterfall that applies losses in order and checks their interaction, the
monthly energy balance, the export limit, soiling with cleaning, and the
forecast tools: persistence baselines, error metrics by horizon, skill,
quantile (pinball) loss and interval coverage, and ramp events.

Teaching implementation: a bankable model is configured in validated
software with documented settings; the structure here (inputs, ordered
steps, energy balance, version) is what a reviewer checks in any of them.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


# ------------------------------------------------------------ waterfall
# [start: waterfall]
@dataclass
class Waterfall:
    """Ordered loss steps on an hourly energy series. Each step stores the
    series after it, so step losses are exact and add up to the total;
    percentages are of the energy entering each step."""
    name: str
    steps: list = field(default_factory=list)          # (label, series)

    def start(self, label: str, series) -> "Waterfall":
        self.steps = [(label, np.asarray(series, float))]
        return self

    def apply(self, label: str, series_after) -> "Waterfall":
        self.steps.append((label, np.asarray(series_after, float)))
        return self

    def totals(self) -> list[tuple[str, float, float]]:
        """(label, energy after the step, loss % of the energy entering)."""
        out, prev = [], None
        for label, s in self.steps:
            e = float(s.sum())
            pct = 0.0 if prev is None else 100 * (1 - e / prev)
            out.append((label, e, pct))
            prev = e
        return out

    def check(self, tol: float = 1e-9) -> tuple[float, float]:
        """Total loss two ways: from the first and last energy, and as the
        product of the step factors; they must agree (energy balance)."""
        t = self.totals()
        total = 1 - t[-1][1] / t[0][1]
        prod = 1 - np.prod([1 - x[2] / 100 for x in t[1:]])
        assert abs(total - prod) < tol, "waterfall does not balance"
        return total, sum(x[2] for x in t[1:]) / 100
# [end: waterfall]


def monthly(series, month_index) -> np.ndarray:
    """Sum of an hourly series in each of 12 months (month_index 0..11)."""
    return np.bincount(np.asarray(month_index), weights=np.asarray(series, float),
                       minlength=12)


# ------------------------------------------------------------ inverter
# [start: inverter]
def ac_from_dc(x, c):
    """AC output y (per unit of rated AC) for the DC input x (per unit)
    when the loss is c0 + c1 y + c2 y^2 of the output: x = y + loss, so
    c2 y^2 + (1 + c1) y + (c0 - x) = 0; take the positive root. Below
    the no-load loss c0 the inverter gives nothing."""
    x = np.asarray(x, float)
    c0, c1, c2 = c
    b = 1.0 + c1
    root = np.sqrt(np.maximum(b * b - 4.0 * c2 * (c0 - x), 0.0))
    return np.where(x > c0, (-b + root) / (2.0 * c2), 0.0)
# [end: inverter]


# ------------------------------------------------------------ plant end
# [start: plantend]
def plant_end(w_mv, pv_mv, cfg, outage):
    """MV to POC: electrical losses (no-load + load ~ P^2), own use,
    export limit and grid outages. Returns (poc, net), MW."""
    pv_mv = np.asarray(pv_mv, float)
    mv = np.asarray(w_mv, float) + pv_mv
    load = cfg.loadloss * cfg.export_mw * (mv / cfg.export_mw) ** 2
    after_el = mv - (cfg.noload_mw + load)
    poc = after_el - (cfg.aux_wind_mw + cfg.aux_pv * pv_mv)
    delivered = np.minimum(poc, cfg.export_mw)
    net = np.where(outage, np.minimum(delivered, 0.0), delivered)
    return poc, net
# [end: plantend]


def export_limit(p_mw, limit_mw: float):
    """Delivered and curtailed power at the point of connection."""
    p = np.asarray(p_mw, float)
    return np.minimum(p, limit_mw), np.clip(p - limit_mw, 0, None)


# ------------------------------------------------------------ soiling
# [start: soiling]
def soiling_loss(days: int, rate: float, rain_mm, clean_days,
                 rain_clean: float = 5.0,
                 recovery: float = 0.95, cap: float = 0.25) -> np.ndarray:
    """Daily soiling loss: grows by `rate` a day, reset (to 1 - recovery of
    itself) by rain above rain_clean mm or by a cleaning on clean_days;
    capped at `cap`."""
    loss = np.zeros(days)
    clean = set(int(d) for d in clean_days)
    s = 0.0
    for d in range(days):
        s = min(s + rate, cap)
        if rain_mm[d] >= rain_clean or d in clean:
            s *= 1 - recovery
        loss[d] = s
    return loss
# [end: soiling]


# ------------------------------------------------------------ forecasting
# [start: forecast]
def persistence(obs, horizon: int) -> np.ndarray:
    """Forecast for t + h is the observation at t (NaN where unknown)."""
    o = np.asarray(obs, float)
    f = np.full_like(o, np.nan)
    f[horizon:] = o[:-horizon] if horizon else o
    return f


def smart_persistence(obs, clear, horizon: int) -> np.ndarray:
    """Persist the clear-sky index (or capacity factor ratio) instead of
    the value: forecast = clear(t + h) x obs(t) / clear(t)."""
    o, c = np.asarray(obs, float), np.asarray(clear, float)
    k = np.where(c > 1e-6, o / np.maximum(c, 1e-6), 0.0)
    f = np.full_like(o, np.nan)
    f[horizon:] = c[horizon:] * k[:-horizon]
    return f


def scores(fc, obs, mask=None) -> dict:
    """Bias, MAE and RMSE over the finite pairs (and an optional mask)."""
    f, o = np.asarray(fc, float), np.asarray(obs, float)
    ok = np.isfinite(f) & np.isfinite(o)
    if mask is not None:
        ok &= np.asarray(mask, bool)
    e = f[ok] - o[ok]
    return {"bias": float(e.mean()), "mae": float(np.abs(e).mean()),
            "rmse": float(np.sqrt(np.mean(e ** 2))), "n": int(ok.sum())}


def skill(score: float, reference: float) -> float:
    """Skill against a reference: 1 - score / reference (1 is perfect,
    0 no better than the reference, negative worse)."""
    return 1.0 - score / reference


def pinball(q_fc, obs, tau: float) -> float:
    """Mean pinball (quantile) loss of a tau-quantile forecast."""
    q, o = np.asarray(q_fc, float), np.asarray(obs, float)
    ok = np.isfinite(q) & np.isfinite(o)
    d = o[ok] - q[ok]
    return float(np.mean(np.maximum(tau * d, (tau - 1) * d)))


def coverage(lo, hi, obs) -> float:
    """Share of observations inside a forecast interval."""
    lo, hi, o = (np.asarray(x, float) for x in (lo, hi, obs))
    ok = np.isfinite(lo) & np.isfinite(hi) & np.isfinite(o)
    return float(np.mean((o[ok] >= lo[ok]) & (o[ok] <= hi[ok])))


def ramps(series, threshold: float, window: int = 1) -> np.ndarray:
    """Ramp events: change over `window` steps larger than threshold
    (+1 up, -1 down, 0 none)."""
    s = np.asarray(series, float)
    d = np.full_like(s, 0.0)
    d[window:] = s[window:] - s[:-window]
    return np.where(d > threshold, 1, np.where(d < -threshold, -1, 0))


def ramp_table(obs_events, fc_events) -> dict:
    """Hits, misses and false alarms of ramp events (same sign, same step)."""
    o, f = np.asarray(obs_events), np.asarray(fc_events)
    hits = int(np.sum((o != 0) & (f == o)))
    misses = int(np.sum((o != 0) & (f != o)))
    false = int(np.sum((o == 0) & (f != 0)))
    pod = hits / max(hits + misses, 1)
    far = false / max(hits + false, 1)
    return {"hits": hits, "misses": misses, "false": false,
            "pod": pod, "far": far}
# [end: forecast]
