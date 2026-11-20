"""Instrumentation and control, chapter 34: the measurement chain (4-20 mA
scaling, loop length, converter resolution, combined uncertainty, Pt100
and thermocouple corrections, clock drift, calibration interval,
filtering), the controller as a sampled machine (response budget,
discrete PI), panels and I/O counts, control-power autonomy,
availability with redundancy, signal quality and setpoint validation.

Teaching tools: every number they produce in the book is checked by
hand in tests/test_ch34_instrumentation.py.
"""
from __future__ import annotations

import math

import numpy as np

# [start: scaling]
def ma_to_eng(ma: float, lo: float, hi: float) -> float:
    """Engineering value of a 4-20 mA signal ranged lo..hi (live zero)."""
    return lo + (ma - 4.0) / 16.0 * (hi - lo)


def eng_to_ma(x: float, lo: float, hi: float) -> float:
    """Loop current (mA) that represents x on a lo..hi range."""
    return 4.0 + 16.0 * (x - lo) / (hi - lo)
# [end: scaling]


# [start: loop]
def loop_max_length(v_supply: float, v_min_tx: float, r_receiver: float,
                    area_mm2: float, i_max_a: float = 0.022,
                    rho: float = 0.0175) -> float:
    """Longest two-wire loop (m, one way) that still leaves the transmitter
    its minimum voltage at the highest loop current (copper, ohm mm2/m)."""
    r_cable_max = (v_supply - v_min_tx) / i_max_a - r_receiver
    return r_cable_max / (2 * rho / area_mm2)
# [end: loop]


def adc_step(span: float, bits: int, used: float = 1.0) -> float:
    """Value of one converter count when a share `used` of the converter
    range carries the signal span."""
    return span / (used * (2 ** bits - 1))


def combine(*parts: float) -> float:
    """Root-sum-square of independent standard uncertainties."""
    return math.sqrt(sum(p * p for p in parts))


# [start: rtd]
A_CVD, B_CVD, C_CVD = 3.9083e-3, -5.775e-7, -4.183e-12


def pt100_r(t: float, r0: float = 100.0) -> float:
    """Resistance (ohm) of a platinum sensor at t deg C
    (Callendar-Van Dusen)."""
    r = r0 * (1 + A_CVD * t + B_CVD * t * t)
    if t < 0:
        r += r0 * C_CVD * (t - 100) * t ** 3
    return r


def pt100_t(r: float, r0: float = 100.0) -> float:
    """Temperature (deg C, >= 0) from the resistance of a platinum sensor."""
    a, b, c = r0 * B_CVD, r0 * A_CVD, r0 - r
    return (-b + math.sqrt(b * b - 4 * a * c)) / (2 * a)
# [end: rtd]


def lead_error_2wire(r_lead_ohm: float, r0: float = 100.0) -> float:
    """Temperature error (K) that two leads of r_lead each add to a
    two-wire platinum sensor (about 0.39 ohm per K for a Pt100)."""
    return 2 * r_lead_ohm / (r0 * A_CVD)


def clock_drift_s(ppm: float, seconds: float) -> float:
    """Time error a free-running clock gathers over `seconds`."""
    return ppm * 1e-6 * seconds


def calibration_interval(tolerance: float, drift_per_year: float,
                         as_left: float = 0.0) -> float:
    """Years until a linear drift takes the error from as_left to the
    tolerance."""
    return (tolerance - as_left) / drift_per_year


def first_order_filter(x, dt: float, tau: float) -> np.ndarray:
    """Discrete first-order low-pass filter (time constant tau)."""
    x = np.asarray(x, float)
    y = np.empty_like(x)
    a = dt / (tau + dt)
    y[0] = x[0]
    for k in range(1, len(x)):
        y[k] = y[k - 1] + a * (x[k] - y[k - 1])
    return y


# [start: response]
def response_budget(input_ms: float, scan_ms: float, output_ms: float,
                    comms_ms: float = 0.0) -> float:
    """Worst-case time from a field change to an output: input filter, up to
    two scans (the change just missed one), output update, network."""
    return input_ms + 2 * scan_ms + output_ms + comms_ms
# [end: response]


# [start: pid]
def pi_loop(kp: float, ki: float, tau: float, dt: float, n: int,
            method: str = "euler", delay: int = 0,
            sp: float = 1.0) -> np.ndarray:
    """Step response of a sampled PI controller on a first-order plant
    (time constant tau) with a dead time of `delay` samples."""
    a = math.exp(-dt / tau)
    y = np.zeros(n)
    u_hist = [0.0] * (delay + 1)
    u, e_prev = 0.0, sp
    for k in range(1, n):
        e = sp - y[k - 1]
        integ = ki * dt * ((e + e_prev) / 2 if method == "tustin" else e)
        u = u + kp * (e - e_prev) + integ
        e_prev = e
        u_hist.append(u)
        y[k] = a * y[k - 1] + (1 - a) * u_hist[-1 - delay]
    return y
# [end: pid]


def panel_rise_k(losses_w: float, area_m2: float, k: float = 5.5) -> float:
    """Inside temperature rise of a closed panel cooled by its surface."""
    return losses_w / (k * area_m2)


def fan_flow_m3h(losses_w: float, rise_k: float) -> float:
    """Air flow that carries the losses away with a given temperature rise."""
    return losses_w / (1.2 * 1005 * rise_k) * 3600


def modules_needed(points: int, spare: float = 0.2,
                   per_module: int = 16) -> int:
    """I/O modules for a number of points plus a spare share."""
    return math.ceil(points * (1 + spare) / per_module)


def autonomy_h(ah: float, load_a: float, usable: float = 0.8) -> float:
    """Hours a battery carries a steady load using a share of its capacity."""
    return ah * usable / load_a


def availability(mtbf_h: float, mttr_h: float) -> float:
    """Steady-state availability of one repairable unit."""
    return mtbf_h / (mtbf_h + mttr_h)


def parallel(a: float, n: int = 2) -> float:
    """Availability of n independent units of which one is enough."""
    return 1 - (1 - a) ** n


# [start: quality]
def quality(ma: float, age_s: float, max_age_s: float = 10.0) -> str:
    """Quality of an analogue value: 'bad' outside 3.6-21 mA (broken or
    failed loop), 'stale' when not refreshed in time, else 'good'."""
    if ma < 3.6 or ma > 21.0:
        return "bad"
    if age_s > max_age_s:
        return "stale"
    return "good"


def validate_setpoint(sp: float, lo: float, hi: float, last: float,
                      max_step: float) -> tuple[float, str]:
    """Accept a received setpoint only inside its range and step limit;
    otherwise keep the last accepted value and say why."""
    if not lo <= sp <= hi:
        return last, "out of range"
    if abs(sp - last) > max_step:
        return last, "step too large"
    return sp, "accepted"
# [end: quality]
