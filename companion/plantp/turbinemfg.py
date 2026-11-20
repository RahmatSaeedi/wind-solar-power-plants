"""Wind-turbine component manufacturing arithmetic (chapter 42), at
textbook level and without process recipes: fibre volume from mass
fraction, void content from density, blade-root insert tension, blade
set matching by first mass moments, probability of detection of an
inspection, filter removal, back-to-back test power, an amplitude
spectrum with band amplitudes, shrink-fit temperature, insulation life
by the halving rule, and two-plane alignment corrections.

Rule of mixtures and Arrhenius life live in plantp.materials (ch 4).
Every function is checked by hand in companion/tests/test_ch42_mfg.py.
"""
from __future__ import annotations

import cmath
import itertools
import math

import numpy as np


# [start: composite]
def fibre_volume(w_f: float, rho_f: float, rho_m: float) -> float:
    """Fibre volume fraction from the fibre mass fraction (no voids)."""
    return (w_f / rho_f) / (w_f / rho_f + (1 - w_f) / rho_m)


def void_content(rho_meas: float, w_f: float, rho_f: float,
                 rho_m: float) -> float:
    """Void volume share: 1 - measured / void-free density."""
    rho_th = 1 / (w_f / rho_f + (1 - w_f) / rho_m)
    return 1 - rho_meas / rho_th
# [end: composite]


# [start: inserts]
def insert_tension(moment_nm: float, n: int, circle_m: float) -> float:
    """Largest bolt tension from a bending moment on a bolt circle
    (linear distribution): 4 M / (n D)."""
    return 4 * moment_nm / (n * circle_m)
# [end: inserts]


def set_unbalance(moments) -> float:
    """Residual unbalance of three blades 120 degrees apart (kg m or t m)."""
    z = sum(m * cmath.exp(1j * 2 * math.pi * k / 3)
            for k, m in enumerate(moments))
    return abs(z)


def match_sets(moments: list[float]) -> list[tuple[int, int, int]]:
    """Group blades into sets of three with small unbalance: sort by
    moment and take neighbours (a simple, near-optimal rule)."""
    order = sorted(range(len(moments)), key=lambda k: moments[k])
    return [tuple(order[i:i + 3]) for i in range(0, len(order) - 2, 3)]


def best_sets_bruteforce(moments: list[float]) -> float:
    """Smallest total unbalance over all partitions of six blades."""
    idx = range(len(moments))
    best = math.inf
    for a in itertools.combinations(idx, 3):
        b = [k for k in idx if k not in a]
        tot = set_unbalance([moments[k] for k in a]) + \
            set_unbalance([moments[k] for k in b])
        best = min(best, tot)
    return best


# [start: pod]
def pod(a_mm, a50_mm: float, beta: float):
    """Probability of detecting a flaw of size a (log-normal POD)."""
    from statistics import NormalDist
    nd = NormalDist()
    a = np.atleast_1d(np.asarray(a_mm, dtype=float))
    return np.array([nd.cdf((math.log(x) - math.log(a50_mm)) / beta)
                     for x in a])
# [end: pod]


def filter_removal(beta_ratio: float) -> float:
    """Share of particles above the rated size removed in one pass."""
    return 1 - 1 / beta_ratio


def back_to_back_power(p_test_kw: float, eta_each: float) -> float:
    """Grid power to run two gearboxes back to back: only the losses."""
    return p_test_kw * (1 / eta_each ** 2 - 1)


# [start: spectrum]
def amplitude_spectrum(x, fs: float):
    """One-sided amplitude spectrum with a Hann window (amplitude-
    corrected): a sine of amplitude A shows as about A at its bin."""
    x = np.asarray(x, dtype=float)
    w = np.hanning(len(x))
    spec = np.fft.rfft((x - x.mean()) * w)
    amp = 2 * np.abs(spec) / w.sum()
    freqs = np.fft.rfftfreq(len(x), 1 / fs)
    return freqs, amp


def band_peak(freqs, amp, f0: float, half_width: float = 2.0) -> float:
    m = (freqs >= f0 - half_width) & (freqs <= f0 + half_width)
    return float(amp[m].max())
# [end: spectrum]


def shrink_delta_t(interference_m: float, d_m: float,
                   alpha: float = 12e-6, clearance_m: float = 0.0) -> float:
    """Temperature rise that opens a bore by the interference plus an
    assembly clearance (thermal expansion of the outer part)."""
    return (interference_m + clearance_m) / (alpha * d_m)


def halving_life(t_c: float, t_ref: float, life_ref: float,
                 halving_k: float = 10.0) -> float:
    """Insulation life by the halving rule: life halves for every
    halving_k above the reference temperature."""
    return life_ref * 2 ** ((t_ref - t_c) / halving_k)


def alignment_moves(offset_mm: float, angle_mm_per_m: float,
                    front_m: float, back_m: float) -> tuple[float, float]:
    """Shim changes at the front and back feet that remove an offset at
    the coupling and an angle (mm per m) of the moving machine."""
    return (-(offset_mm + angle_mm_per_m * front_m),
            -(offset_mm + angle_mm_per_m * back_m))
