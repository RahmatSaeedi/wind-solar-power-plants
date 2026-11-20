"""Periodic signals, harmonics and simple frequency response, chapter 3 (used again in
chapters 7, 9, 26 and 34).

    rms                    root-mean-square value of samples
    harmonic_amplitudes    peak amplitude of each harmonic from one sampled period (DFT)
    thd                    total harmonic distortion from harmonic amplitudes
    alias_frequency        apparent frequency of a sampled sinusoid
    first_order_gain       amplitude ratio of a first-order lag, 1 / sqrt(1 + (w tau)^2)
    first_order_lag_deg    phase lag of a first-order lag, atan(w tau), in degrees

A periodic signal sampled N times over exactly one fundamental period has the discrete
Fourier transform X_h; the peak amplitude of harmonic h (1 <= h < N/2) is 2 |X_h| / N.
"""
from __future__ import annotations

import math

import numpy as np


def rms(x) -> float:
    x = np.asarray(x, dtype=float)
    return float(math.sqrt(np.mean(x * x)))


def harmonic_amplitudes(samples, n_max: int) -> np.ndarray:
    """Peak amplitudes A_0..A_n_max from samples covering exactly one period.

    A_0 is the mean (DC) value. Requires n_max < len(samples) / 2 (Nyquist).
    """
    x = np.asarray(samples, dtype=float)
    n = x.size
    if not 0 <= n_max < n / 2:
        raise ValueError(f"n_max must be below N/2 = {n / 2}")
    spec = np.fft.rfft(x)
    amp = 2.0 * np.abs(spec[: n_max + 1]) / n
    amp[0] /= 2.0
    return amp


def thd(amplitudes) -> float:
    """sqrt(sum of A_h^2 for h >= 2) / A_1; amplitudes[0] is the DC term (ignored)."""
    a = np.asarray(amplitudes, dtype=float)
    if a.size < 2 or a[1] == 0:
        raise ValueError("need a non-zero fundamental amplitudes[1]")
    return float(math.sqrt(np.sum(a[2:] ** 2)) / a[1])


def alias_frequency(f: float, fs: float) -> float:
    """Frequency (Hz, 0..fs/2) at which a sinusoid of f Hz appears when sampled at fs Hz."""
    if fs <= 0:
        raise ValueError("sampling frequency must be positive")
    return abs(f - fs * round(f / fs))


def first_order_gain(f, tau: float):
    w = 2.0 * math.pi * np.asarray(f, dtype=float)
    return 1.0 / np.sqrt(1.0 + (w * tau) ** 2)


def first_order_lag_deg(f, tau: float):
    w = 2.0 * math.pi * np.asarray(f, dtype=float)
    return np.degrees(np.arctan(w * tau))
