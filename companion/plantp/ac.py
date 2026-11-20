"""AC circuits and three-phase power, chapter 7 (builds on phasors.py, chapter 3).

    reactance_l, reactance_c       X_L = w L, X_C = 1 / (w C)
    rlc_series                     Z = R + j (X_L - X_C)
    resonance_hz, q_series         f0 = 1 / (2 pi sqrt(L C)), Q = X_L(f0) / R
    resonance_order                h = sqrt(S_sc / Q_c) (capacitor bank on a network)
    line_current_a                 I = P / (sqrt3 V_LL pf), balanced three-phase
    wye_to_line, delta_line_currents   line/phase relations
    star_point_voltage             Millman: voltage of a floating or earthed star point
    unbalanced_wye                 phase and neutral currents of an unbalanced star load
    unbalance_factor               |V2| / |V1| (negative / positive sequence)
    two_wattmeter                  readings of the two-wattmeter method
    capacitor_for_pf               reactive power to raise a power factor
    q_capability                   largest |Q| at active power P inside a rating S
    rms_from_harmonics, thd_f      RMS and total harmonic distortion of a current
    power_factor_true              displacement x distortion factor
    k_factor                       sum h^2 I_h^2 / sum I_h^2 (transformer heating)

Conventions as phasors.py: RMS phasors, angles in degrees at the interface, S = V I*,
a lagging (inductive) current gives Q > 0 (load convention).
"""
from __future__ import annotations

import cmath
import math

import numpy as np

from plantp.phasors import A, polar, symmetrical_components

SQRT3 = math.sqrt(3.0)


def reactance_l(f_hz: float, l_h: float) -> float:
    return 2 * math.pi * f_hz * l_h


def reactance_c(f_hz: float, c_f: float) -> float:
    if f_hz <= 0 or c_f <= 0:
        raise ValueError("frequency and capacitance must be positive")
    return 1.0 / (2 * math.pi * f_hz * c_f)


def rlc_series(r_ohm: float, l_h: float, c_f: float | None, f_hz: float) -> complex:
    x = reactance_l(f_hz, l_h) - (reactance_c(f_hz, c_f) if c_f else 0.0)
    return complex(r_ohm, x)


def resonance_hz(l_h: float, c_f: float) -> float:
    return 1.0 / (2 * math.pi * math.sqrt(l_h * c_f))


def q_series(r_ohm: float, l_h: float, c_f: float) -> float:
    return reactance_l(resonance_hz(l_h, c_f), l_h) / r_ohm


def resonance_order(s_sc_mva: float, q_c_mvar: float) -> float:
    """Harmonic order of the parallel resonance of a capacitor bank with the
    network inductance, h = sqrt(S_sc / Q_c) (simple screening estimate)."""
    if s_sc_mva <= 0 or q_c_mvar <= 0:
        raise ValueError("short-circuit power and capacitor size must be positive")
    return math.sqrt(s_sc_mva / q_c_mvar)


def line_current_a(p_w: float, v_ll_v: float, pf: float) -> float:
    """Balanced three-phase line current I = P / (sqrt3 V_LL pf)."""
    if v_ll_v <= 0 or not 0 < pf <= 1:
        raise ValueError("voltage must be positive and 0 < pf <= 1")
    return p_w / (SQRT3 * v_ll_v * pf)


def wye_to_line(v_phase: complex) -> complex:
    """Line-to-line voltage V_ab from the phase voltage V_an of a positive-
    sequence set: V_ab = sqrt3 V_an at +30 degrees."""
    return v_phase * (1 - A * A)


def delta_line_currents(i_ab: complex, i_bc: complex, i_ca: complex):
    """Line currents of a delta load from its branch currents."""
    return i_ab - i_ca, i_bc - i_ab, i_ca - i_bc


def star_point_voltage(v_phases, z_phases, z_neutral: complex | None) -> complex:
    """Millman: voltage of the load star point against the source neutral.

    z_neutral None means no neutral conductor (floating star point);
    z_neutral 0 means a solid neutral (star point held at zero)."""
    y = [1 / z for z in z_phases]
    num = sum(v * yi for v, yi in zip(v_phases, y))
    den = sum(y)
    if z_neutral is not None:
        if z_neutral == 0:
            return 0j
        den += 1 / z_neutral
    return num / den


def unbalanced_wye(v_phases, z_phases, z_neutral: complex | None = 0j):
    """(phase currents, neutral current, star-point voltage) of a star load."""
    vn = star_point_voltage(v_phases, z_phases, z_neutral)
    i = [(v - vn) / z for v, z in zip(v_phases, z_phases)]
    return i, sum(i), vn


def unbalance_factor(va: complex, vb: complex, vc: complex) -> float:
    """Voltage (or current) unbalance |negative| / |positive| sequence."""
    _, v1, v2 = symmetrical_components(va, vb, vc)
    return abs(v2) / abs(v1)


def two_wattmeter(v_an: complex, i_a: complex, i_b: complex, i_c: complex):
    """Readings W1 = Re(V_ac I_a*), W2 = Re(V_bc I_b*) of the two-wattmeter
    method (meters in lines a and b, common point on line c)."""
    v_bn, v_cn = v_an * A * A, v_an * A
    w1 = (( v_an - v_cn) * i_a.conjugate()).real
    w2 = ((v_bn - v_cn) * i_b.conjugate()).real
    return w1, w2


def capacitor_for_pf(p_w: float, pf_from: float, pf_to: float) -> float:
    """Reactive power (var) a capacitor must supply to raise pf_from to pf_to."""
    if not 0 < pf_from <= pf_to <= 1:
        raise ValueError("need 0 < pf_from <= pf_to <= 1")
    return p_w * (math.tan(math.acos(pf_from)) - math.tan(math.acos(pf_to)))


def q_capability(s_rated: float, p: float) -> float:
    """Largest |Q| available at active power p inside an apparent-power rating."""
    if abs(p) > s_rated:
        raise ValueError("active power exceeds the apparent-power rating")
    return math.sqrt(s_rated ** 2 - p ** 2)


def rms_from_harmonics(amplitudes_rms) -> float:
    """RMS of a waveform from the RMS values of its harmonics (index 1 = fundamental)."""
    a = np.asarray(amplitudes_rms, dtype=float)
    return float(math.sqrt(np.sum(a ** 2)))


def thd_f(amplitudes) -> float:
    """THD relative to the fundamental; amplitudes[0] is the fundamental."""
    a = np.asarray(amplitudes, dtype=float)
    return float(math.sqrt(np.sum(a[1:] ** 2)) / a[0])


def power_factor_true(displacement_pf: float, thd_current: float) -> float:
    """True pf = cos(phi1) x 1 / sqrt(1 + THD_I^2) (sinusoidal voltage)."""
    return displacement_pf / math.sqrt(1 + thd_current ** 2)


def k_factor(orders, currents) -> float:
    """sum(h^2 I_h^2) / sum(I_h^2) for harmonic orders and RMS currents."""
    h = np.asarray(orders, dtype=float)
    i = np.asarray(currents, dtype=float)
    return float(np.sum(h ** 2 * i ** 2) / np.sum(i ** 2))


def balanced_set(v_rms: float, angle_deg: float = 0.0):
    """Positive-sequence phasors (a, b, c) of magnitude v_rms."""
    va = polar(v_rms, angle_deg)
    return va, va * A * A, va * A


def phase_angle_deg(z: complex) -> float:
    return math.degrees(cmath.phase(z))
