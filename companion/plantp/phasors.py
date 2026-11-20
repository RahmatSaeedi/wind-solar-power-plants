"""Complex numbers for AC work: phasors, impedance, complex power, three-phase
transformations (chapter 3; developed into circuits in chapter 7).

Conventions (book-wide): phasors are RMS values; angles in degrees in the
interface, radians inside; complex power S = V I* (conjugate of the current), so a
lagging (inductive) current gives Q > 0; the a-operator a = 1/120 deg.
"""
from __future__ import annotations

import cmath
import math

import numpy as np

A = cmath.rect(1.0, math.radians(120.0))          # the operator a = 1 /_ 120 deg


def polar(magnitude: float, angle_deg: float) -> complex:
    """Phasor from magnitude and angle in degrees."""
    return cmath.rect(magnitude, math.radians(angle_deg))


def to_polar(z: complex) -> tuple[float, float]:
    """(magnitude, angle in degrees) of a complex number."""
    return abs(z), math.degrees(cmath.phase(z))


def series(*z: complex) -> complex:
    return complex(sum(z))


def parallel(*z: complex) -> complex:
    if any(zi == 0 for zi in z):
        return 0j
    return 1.0 / sum(1.0 / zi for zi in z)


def complex_power(v: complex, i: complex) -> complex:
    """S = V I*  (P = Re S, Q = Im S; Q > 0 for a lagging current)."""
    return v * i.conjugate()


def three_phase_power(v_ln: complex, i: complex) -> complex:
    """Total complex power of a balanced three-phase set from one phase."""
    return 3.0 * complex_power(v_ln, i)


def voltage_drop_approx(p_w: float, q_var: float, r_ohm: float, x_ohm: float,
                        v_ll: float) -> float:
    """Approximate three-phase voltage drop magnitude (line-to-line, volts):
    dV ~ (R P + X Q) / V_LL. Valid for small drops (a few percent)."""
    return (r_ohm * p_w + x_ohm * q_var) / v_ll


def symmetrical_components(ia: complex, ib: complex, ic: complex):
    """Fortescue: (zero, positive, negative) sequence components of a three-phase set."""
    i0 = (ia + ib + ic) / 3
    i1 = (ia + A * ib + A * A * ic) / 3
    i2 = (ia + A * A * ib + A * ic) / 3
    return i0, i1, i2


def from_sequences(i0: complex, i1: complex, i2: complex):
    ia = i0 + i1 + i2
    ib = i0 + A * A * i1 + A * i2
    ic = i0 + A * i1 + A * A * i2
    return ia, ib, ic


CLARKE = (2.0 / 3.0) * np.array([[1.0, -0.5, -0.5],
                                 [0.0, math.sqrt(3) / 2, -math.sqrt(3) / 2],
                                 [0.5, 0.5, 0.5]])


def clarke(xa, xb, xc):
    """Amplitude-invariant Clarke transform: (alpha, beta, zero)."""
    return CLARKE @ np.array([xa, xb, xc], dtype=float)


def park(x_alpha, x_beta, theta):
    """Park transform: rotate (alpha, beta) by -theta into the (d, q) frame.

    With theta = omega t following phase a, a balanced positive-sequence set of
    amplitude X and phase phi gives constant d = X cos(phi), q = X sin(phi)."""
    c, s = np.cos(theta), np.sin(theta)
    x_alpha, x_beta = np.asarray(x_alpha, dtype=float), np.asarray(x_beta, dtype=float)
    return c * x_alpha + s * x_beta, -s * x_alpha + c * x_beta
