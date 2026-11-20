"""Power-quality and service-performance tools (chapter 27).

Teaching forms of the quantities a plant engineer computes from
measurements: distortion relative to the fundamental and to the demand
current, spectral leakage of an unsynchronised window, aggregation of
short values into 10-minute values and a weekly percentile, summation of
harmonic currents from many units, the frequency scan of a network with
cable capacitance and a tuned filter, rapid voltage change, and the
metrics of a step response, a droop and a ramp limit.

These are teaching forms. Real assessments follow the measurement and
assessment standards and the operator's requirements.
"""
from __future__ import annotations

import math

import numpy as np

W50 = 2 * math.pi * 50


# [start: distortion]
def thd(harmonics: dict, i1: float) -> float:
    """Total harmonic distortion: sqrt(sum I_h^2) over the fundamental at
    the moment of measurement."""
    return math.sqrt(sum(v * v for v in harmonics.values())) / i1


def tdd(harmonics: dict, i_demand: float) -> float:
    """Total demand distortion: the same harmonic sum over the maximum
    demand current - it does not grow when the plant runs at low power."""
    return math.sqrt(sum(v * v for v in harmonics.values())) / i_demand
# [end: distortion]


def spectrum(samples: np.ndarray, fs: float) -> tuple:
    """Frequencies and RMS amplitudes of a sampled window (rectangular)."""
    n = len(samples)
    amp = np.abs(np.fft.rfft(samples)) * 2 / n / math.sqrt(2)
    freq = np.fft.rfftfreq(n, 1 / fs)
    return freq, amp


def aggregate(values: np.ndarray, block: int) -> np.ndarray:
    """RMS aggregation of consecutive values in blocks (the way short
    measurement intervals are combined into longer ones)."""
    v = np.asarray(values, dtype=float)
    m = len(v) // block
    return np.sqrt(np.mean(v[: m * block].reshape(m, block) ** 2, axis=1))


def percentile(values, q: float) -> float:
    """The q-th percentile of a set of aggregated values."""
    return float(np.percentile(np.asarray(values, dtype=float), q))


# [start: summation]
def summation(currents, alpha: float) -> float:
    """Combined harmonic current of several sources with a summation
    exponent alpha: alpha 1 adds magnitudes (in phase), alpha 2 adds
    powers (random phases)."""
    return float(sum(abs(c) ** alpha for c in currents) ** (1 / alpha))
# [end: summation]


def scan(h: np.ndarray, s_sc_mva: float, xr: float, q_c_mvar: float, kv: float,
         filt: tuple | None = None) -> np.ndarray:
    """Driving-point impedance magnitude (ohm) seen from a bus at harmonic
    orders h: grid R + jX in parallel with the cable capacitance and, if
    given, a series-tuned filter (q_mvar, h_tune, quality)."""
    z_base = kv ** 2 / s_sc_mva
    x1 = z_base / math.sqrt(1 + 1 / xr ** 2)
    r1 = x1 / xr
    out = []
    for hh in h:
        zg = complex(r1, x1 * hh)
        yc = 1j * hh * q_c_mvar / kv ** 2
        y = 1 / zg + yc
        if filt is not None:
            q_f, h_t, qual = filt
            xc1 = kv ** 2 / q_f * (h_t ** 2 - 1) / h_t ** 2
            xl1 = xc1 / h_t ** 2
            rf = xl1 * h_t / qual
            y += 1 / complex(rf, xl1 * hh - xc1 / hh)
        out.append(abs(1 / y))
    return np.array(out)


# [start: filter]
def tuned_filter(q_mvar: float, h_tune: float, kv: float) -> tuple:
    """Single-tuned filter giving q_mvar at 50 Hz, tuned to h_tune:
    returns (C in uF per phase, L in mH per phase, X_C and X_L at 50 Hz)."""
    x_net = kv ** 2 / q_mvar                     # X_C - X_L at 50 Hz
    xc = x_net * h_tune ** 2 / (h_tune ** 2 - 1)
    xl = xc / h_tune ** 2
    return 1e6 / (W50 * xc), 1e3 * xl / W50, xc, xl
# [end: filter]


def voltage_change(dp_mw: float, dq_mvar: float, s_sc_mva: float, xr: float) -> float:
    """Relative voltage change at a bus for a change of injected power,
    dU/U ~ (dP R + dQ X) / U^2, written with the short-circuit power."""
    z = 1 / s_sc_mva
    x = z / math.sqrt(1 + 1 / xr ** 2)
    r = x / xr
    return dp_mw * r + dq_mvar * x


# [start: step]
def step_metrics(t: np.ndarray, y: np.ndarray, y0: float, y1: float,
                 band: float = 0.05) -> dict:
    """Rise time (10 to 90 %), settling time (inside +/- band of the
    change for good) and overshoot of a measured step response."""
    span = y1 - y0
    frac = (np.asarray(y) - y0) / span
    t10 = t[np.argmax(frac >= 0.1)]
    t90 = t[np.argmax(frac >= 0.9)]
    outside = np.where(np.abs(frac - 1) > band)[0]
    t_settle = t[0]
    if outside.size and outside[-1] + 1 < len(t):
        t_settle = t[outside[-1] + 1]
    return {"rise": float(t90 - t10), "settle": float(t_settle),
            "overshoot": float(max(0.0, frac.max() - 1))}
# [end: step]


def droop_fit(df_hz: np.ndarray, dp_pu: np.ndarray, deadband: float) -> float:
    """Measured droop (%): least-squares slope of -dP against the
    frequency deviation outside the deadband, as % of 50 Hz per 1 pu."""
    df = np.asarray(df_hz, dtype=float)
    dp = np.asarray(dp_pu, dtype=float)
    eff = np.sign(df) * np.maximum(np.abs(df) - deadband, 0.0)
    mask = eff != 0
    k = float(np.sum(eff[mask] * -dp[mask]) / np.sum(eff[mask] ** 2))   # pu per Hz
    return 100 / (50 * k)


def ramp_exceedance(p_mw: np.ndarray, limit_mw_per_min: float) -> float:
    """Share of one-minute steps whose change exceeds the ramp limit."""
    d = np.abs(np.diff(np.asarray(p_mw, dtype=float)))
    return float(np.mean(d > limit_mw_per_min))


def completeness(n_expected: int, n_received: int) -> float:
    """Share of expected telemetry samples that arrived."""
    return n_received / n_expected
