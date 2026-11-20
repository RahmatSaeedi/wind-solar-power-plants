"""Chapter 7, section A - sinusoidal steady state: waveforms, RMS, phasors,
inductance, capacitance, impedance and resonance on Plant P.

Run from the project root:   python -m companion.ch07.examples_a
Writes companion/ch07/expected/a_*.txt and diagrams/data/ch07-*.csv.
Cable data A-032 and A-052 (chapters 3 and 4); new assumptions A-100 .. A-102.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch07.common import csv, emit
from plantp import ac, signals
from plantp.phasors import polar, to_polar, voltage_drop_approx

F = 50.0
W = 2 * math.pi * F
R_KM, X_KM, C_KM = 0.125, 0.110, 0.218e-6        # ohm/km, ohm/km, F/km (A-032, A-052)


def waveform() -> None:
    v_rms = 230.0
    vp = v_rms * math.sqrt(2)
    t = 2.5e-3
    lines = [f"230 V RMS, 50 Hz: peak {vp:.1f} V, period {1000 / F:.0f} ms, "
             f"omega {W:.2f} rad/s",
             f"  v(t) = {vp:.1f} sin({W:.2f} t); at t = 2.5 ms: v = "
             f"{vp * math.sin(W * t):.1f} V (angle {math.degrees(W * t):.0f} deg)",
             f"  a 30 deg lag is {30 / 360 * 1000 / F:.3f} ms; one degree is "
             f"{1e6 / F / 360:.1f} microseconds",
             f"33 kV line-to-line RMS: phase {33 / math.sqrt(3):.2f} kV RMS, phase peak "
             f"{33 / math.sqrt(3) * math.sqrt(2):.2f} kV"]
    emit("a_wave", lines)
    t = np.linspace(0, 0.04, 401)
    csv("ch07-wave.csv", "t_ms,v,i",
        [(f"{1000 * x:.2f}", f"{vp * math.sin(W * x):.1f}",
          f"{10 * math.sqrt(2) * math.sin(W * x - math.radians(30)) * 10:.1f}") for x in t])


def rms_values() -> None:
    n = 2000
    th = np.linspace(0, 2 * math.pi, n, endpoint=False)
    sine = np.sin(th)
    square = np.where(np.sin(th) >= 0, 1.0, -1.0)
    tri = 2 / math.pi * np.arcsin(np.sin(th))
    inv = np.sin(th) + 0.04 * np.sin(5 * th) + 0.03 * np.sin(7 * th)        # A-040
    lines = ["RMS / peak and crest factor (peak / RMS), from 2000 samples per period:"]
    for name, x in (("sine", sine), ("square", square), ("triangle", tri),
                    ("inverter current, 4 % 5th + 3 % 7th (A-040)", inv)):
        r = signals.rms(x)
        lines.append(f"  {name:43s} RMS {r:.4f}, crest {np.max(np.abs(x)) / r:.3f}")
    lines.append(f"  theory: sine 1/sqrt2 = {1 / math.sqrt(2):.4f}; triangle 1/sqrt3 = "
                 f"{1 / math.sqrt(3):.4f}")
    lines.append("          inverter sqrt(1 + 0.04^2 + 0.03^2)/sqrt2 = "
                 f"{math.sqrt(1 + 0.04 ** 2 + 0.03 ** 2) / math.sqrt(2):.4f}")
    avg = float(np.mean(np.abs(sine)))
    lines.append(f"mean of the rectified sine {avg:.4f} = 2/pi; form factor RMS/mean "
                 f"{(1 / math.sqrt(2)) / avg:.4f}")
    emit("a_rms", lines)


def cable_lc() -> None:
    l_km = X_KM / W
    xc_km = 1 / (W * C_KM)
    u0 = 33e3 / math.sqrt(3)
    ic_km = u0 * W * C_KM
    q_km = 3 * u0 * ic_km
    length = 4 * 6.0                                   # collector cables, A-091
    emit("a_cable", [
        f"33 kV cable (A-032, A-052): X = {X_KM} ohm/km -> L = X / omega = "
        f"{l_km * 1e3:.3f} mH/km",
        f"  C = 0.218 microfarad/km -> X_C = 1/(omega C) = {xc_km:,.0f} ohm km",
        f"  charging current per phase U0 omega C = {ic_km:.3f} A/km",
        f"  reactive generation 3 U0 I_c = {q_km / 1e3:.1f} kvar/km",
        f"  4 feeders x 6 km = {length:.0f} km: {length * ic_km:.1f} A charging, "
        f"{length * q_km / 1e6:.2f} Mvar even at no load",
        "  energy stored per km, sum of 1/2 C v^2 over the three phases:",
        f"    1.5 C U0^2 = {1.5 * C_KM * u0 ** 2:,.0f} J, constant (the phases never "
        "peak together)",
    ])


def feeder_drop() -> None:
    p, pf, length = 25e6, 0.95, 6.0                    # one feeder (A-091)
    v_ll = 33e3
    i = ac.line_current_a(p, v_ll, pf)
    phi = math.acos(pf)
    z = complex(R_KM, X_KM) * length
    v_end = polar(v_ll / math.sqrt(3), 0.0)
    i_ph = polar(i, -math.degrees(phi))
    v_start = v_end + z * i_ph
    mag, ang = to_polar(v_start)
    exact = (mag - abs(v_end)) * math.sqrt(3)
    q = p * math.tan(phi)
    approx = voltage_drop_approx(p, q, z.real, z.imag, v_ll)
    emit("a_feeder", [
        "one 33 kV feeder, 25 MW at pf 0.95 lagging,",
        f"  6 km of {R_KM} + j{X_KM} ohm/km (conductor at 20 C)",
        f"  I = {i:.1f} A at -{math.degrees(phi):.2f} deg; Z = {z.real:.3f} + j{z.imag:.3f} ohm",
        f"  V_end = {abs(v_end) / 1e3:.3f} kV phase; V_start = V_end + Z I = "
        f"{mag / 1e3:.4f} kV /_ {ang:.3f} deg",
        f"  drop (line-to-line): exact {exact:.1f} V = {100 * exact / v_ll:.3f} %",
        f"  approximation (R P + X Q)/V: {approx:.1f} V",
        "  the angle difference is small; the magnitude difference is the drop",
    ])


def resonance() -> None:
    l, c, r = 0.1, 100e-6, 2.0
    f0 = ac.resonance_hz(l, c)
    lines = [f"series R {r} ohm, L {l} H, C {c * 1e6:.0f} microfarad: f0 = "
             f"{f0:.2f} Hz, Q = {ac.q_series(r, l, c):.1f}"]
    for f in (25, 45, f0, 55, 100):
        z = ac.rlc_series(r, l, c, f)
        lines.append(f"  f {f:7.2f} Hz: |Z| = {abs(z):8.2f} ohm, angle "
                     f"{round(math.degrees(math.atan2(z.imag, z.real)), 2) + 0.0:7.2f} deg")
    lines.append("  at resonance the reactances cancel; the current is limited by R alone")
    emit("a_series_resonance", lines)
    s_sc = 500.0                                       # MVA at the 33 kV bus, A-100
    rows = []
    lines = [f"parallel resonance with the network, h = sqrt(S_sc / Q_c), S_sc = {s_sc:.0f} "
             "MVA", "  at the 33 kV bus (A-100):"]
    for name, qc in (("collector cables at no load", 1.79), ("cables + 5 Mvar bank", 6.79),
                     ("cables + 15 Mvar bank", 16.79)):
        h = ac.resonance_order(s_sc, qc)
        lines.append(f"  {name:28s} Q_c {qc:5.2f} Mvar: h = {h:5.2f} ({h * F:4.0f} Hz)")
    lines.append("  an order near 5, 7, 11 or 13 (where inverters inject current)")
    lines.append("  needs a harmonic study (chapter 27)")
    emit("a_parallel_resonance", lines)
    for f in np.linspace(5, 120, 231):
        z = ac.rlc_series(r, l, c, f)
        rows.append((f"{f:.1f}", f"{abs(z):.3f}"))
    csv("ch07-resonance.csv", "f,z", rows)


if __name__ == "__main__":
    waveform()
    rms_values()
    cable_lc()
    feeder_drop()
    resonance()
