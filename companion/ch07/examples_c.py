"""Chapter 7, section C - power and non-ideal waveforms: instantaneous, active,
reactive and apparent power, power factor, ratings and P-Q capability,
harmonics, the neutral, voltage distortion and meters.

Run from the project root:   python -m companion.ch07.examples_c
Writes companion/ch07/expected/c_*.txt and diagrams/data/ch07-*.csv.
Teaching values A-040, A-100, A-101, A-105 (fictional, not vendor data).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch07.common import csv, emit
from plantp import ac, signals

W = 2 * math.pi * 50.0
LED = {1: 1.00, 3: 0.80, 5: 0.55, 7: 0.30, 9: 0.15, 11: 0.08}      # A-105, per unit
INV = {1: 1.00, 5: 0.04, 7: 0.03}                                    # A-040


def waveform(spec, th, peaky=False):
    """Sum of RMS harmonics; peaky=True lines the odd harmonics up at 90 deg,
    the shape of a rectifier (LED driver) current."""
    out = 0.0
    for h, a in spec.items():
        sign = (-1) ** ((h - 1) // 2) if peaky else 1
        out = out + sign * a * math.sqrt(2) * np.sin(h * th)
    return out


def instantaneous() -> None:
    v, i, phi = 230.0, 100.0, math.radians(30)
    p, q = v * i * math.cos(phi), v * i * math.sin(phi)
    t = np.linspace(0, 0.02, 200, endpoint=False)
    pt = 2 * v * i * np.sin(W * t) * np.sin(W * t - phi)
    emit("c_instant", [
        "single phase, 230 V and 100 A RMS, current 30 deg behind:",
        "  p(t) = P (1 - cos 2wt) - Q sin 2wt",
        f"  P = V I cos(phi) = {p / 1e3:.2f} kW, Q = V I sin(phi) = {q / 1e3:.2f} kvar",
        f"  mean of p(t) over a period {pt.mean() / 1e3:.2f} kW; peak {pt.max() / 1e3:.2f} kW; "
        f"minimum {pt.min() / 1e3:.2f} kW",
        "  Q is the amplitude of the part that flows back and forth twice per cycle:",
        "  no net energy, but current, so heating and voltage drop",
    ])
    csv("ch07-pinst.csv", "t_ms,p,pbar",
        [(f"{1000 * x:.2f}", f"{y / 1e3:.3f}", f"{p / 1e3:.3f}") for x, y in zip(t, pt)])


def triangle() -> None:
    lines = ["P, Q, S and pf (load convention: Q > 0 for lagging current):"]
    for name, p, q in (("auxiliary board", 180.0, 135.0), ("motor at light load", 20.0, 30.0),
                       ("resistive heater", 15.0, 0.0), ("capacitor bank", 0.0, -75.0)):
        s = math.hypot(p, q)
        pf = p / s if s else float("nan")
        kind = "lagging" if q > 0 else ("leading" if q < 0 else "unity")
        lines.append(f"  {name:19s} {p:6.1f} kW {q:6.1f} kvar {s:6.1f} kVA "
                     f"pf {pf:5.3f} {kind}")
    lines += ["plant convention (A-024): export P > 0; the plant 'supplies' Q when it",
              "  acts like a capacitor towards the grid and 'absorbs' Q like an",
              "  inductor: always state which convention a number uses"]
    emit("c_triangle", lines)


def pf_correction() -> None:
    p, pf1, pf2 = 180e3, 0.80, 0.95
    qc = ac.capacitor_for_pf(p, pf1, pf2)
    i1 = ac.line_current_a(p, 400, pf1)
    i2 = ac.line_current_a(p, 400, pf2)
    emit("c_pf", [
        f"auxiliary board 180 kW at pf {pf1}: Q = {p * math.tan(math.acos(pf1)) / 1e3:.1f} kvar",
        f"  to reach pf {pf2}: Q_c = P (tan phi1 - tan phi2) = {qc / 1e3:.1f} kvar",
        f"  current {i1:.1f} A -> {i2:.1f} A ({100 * (i2 / i1 - 1):+.1f} %); I^2 R losses "
        f"{100 * ((i2 / i1) ** 2 - 1):+.1f} %",
        "  the capacitor changes no active power: it supplies locally the",
        "  reactive power that otherwise flows through transformer and cables",
    ])


def capability() -> None:
    s_inv = 5.5                                            # MVA per 5 MW inverter, A-101
    lines = [f"inverter rated 5.0 MW and {s_inv} MVA (A-101): Q available = "
             "sqrt(S^2 - P^2)"]
    for pmw in (5.0, 4.0, 2.5, 0.0):
        lines.append(f"  P = {pmw:3.1f} MW: |Q| <= {ac.q_capability(s_inv, pmw):4.2f} Mvar; "
                     f"pf range down to {pmw / s_inv if pmw else 0:.3f}")
    lines += ["  with S equal to the active rating, no reactive power at full output",
              "  (the real P-Q chart comes from the manufacturer and depends on voltage)"]
    emit("c_capability", lines)
    ang = np.linspace(-90, 90, 181)
    csv("ch07-pq.csv", "q,p", [(f"{s_inv * math.sin(math.radians(a)):.3f}",
                                f"{min(5.0, s_inv * math.cos(math.radians(a))):.3f}")
                               for a in ang])


def harmonics() -> None:
    n = 4096
    th = np.linspace(0, 2 * math.pi, n, endpoint=False)
    lines = []
    for name, spec in (("PV inverter current (A-040)", INV), ("LED driver current (A-105)", LED)):
        wave = waveform(spec, th, peaky=(spec is LED))
        amps = signals.harmonic_amplitudes(wave, 13) / math.sqrt(2)
        thd = signals.thd(amps)
        r = signals.rms(wave)
        pf_true = ac.power_factor_true(1.0, thd)
        k = ac.k_factor(list(spec), list(spec.values()))
        lines.append(f"{name}:")
        lines.append(f"  THD {100 * thd:.1f} %, RMS {r:.3f} pu, crest "
                     f"{np.abs(wave).max() / r:.2f}, true pf {pf_true:.3f} "
                     f"(cos phi1 = 1), K {k:.2f}")
    i3 = LED[3]
    phase_rms = ac.rms_from_harmonics(list(LED.values()))
    triplen = math.sqrt(sum((3 * a) ** 2 for h, a in LED.items() if h % 3 == 0))
    lines += ["three phases of LED lighting, 1.0 pu fundamental each, balanced:",
              f"  phase current {phase_rms:.3f} pu RMS; the neutral carries the",
              "  triplen orders (3rd, 9th) of all three phases",
              f"  neutral = 3 x sqrt(0.80^2 + 0.15^2) = {triplen:.3f} pu: "
              f"{triplen / phase_rms:.2f} times a phase current",
              "  a neutral sized for 'balanced load = no neutral current' overheats"]
    emit("c_harmonics", lines)
    wave = waveform(LED, th, peaky=True)
    csv("ch07-led.csv", "deg,i,i1",
        [(f"{math.degrees(x):.1f}", f"{y:.3f}", f"{math.sqrt(2) * math.sin(x):.3f}")
         for x, y in zip(th[::32], wave[::32])])


def voltage_distortion() -> None:
    s_sc, v = 500e6, 33e3                                   # A-100
    x_sc = v ** 2 / s_sc
    i1 = 50e6 / (math.sqrt(3) * v)                          # whole PV plant, rated
    vph = v / math.sqrt(3)
    lines = [f"33 kV bus, S_sc 500 MVA (A-100): X_sc = V^2 / S_sc = {x_sc:.3f} ohm at 50 Hz",
             f"PV plant 50 MW: fundamental {i1:.1f} A; harmonic current = per-unit x {i1:.1f} A"]
    vh = []
    for h, a in INV.items():
        if h == 1:
            continue
        v_h = a * i1 * h * x_sc
        vh.append(v_h)
        lines.append(f"  order {h}: I {a * i1:5.1f} A, h X_sc {h * x_sc:6.2f} ohm, "
                     f"V {v_h:4.0f} V = {100 * v_h / vph:.2f} % of 19.05 kV")
    thd_v = math.sqrt(sum(x * x for x in vh)) / vph
    lines += [f"  voltage THD {100 * thd_v:.2f} % if all inverters inject in phase "
              "(worst case);",
              "  inverters partly cancel each other and the network impedance is not pure X:",
              "  a harmonic study with measured background distortion decides (ch 27)"]
    emit("c_vthd", lines)


def meters() -> None:
    n = 4096
    th = np.linspace(0, 2 * math.pi, n, endpoint=False)
    wave = waveform(LED, th, peaky=True)
    true_rms = signals.rms(wave)
    avg_meter = 1.1107 * float(np.mean(np.abs(wave)))
    sine = math.sqrt(2) * np.sin(th)
    emit("c_meters", [
        "an 'average-responding' meter shows 1.1107 x mean(|i|), exact only",
        "  for a sine:",
        f"  sine: true RMS {signals.rms(sine):.3f}, meter {1.1107 * float(np.mean(np.abs(sine))):.3f}",
        f"  LED driver current: true RMS {true_rms:.3f}, meter {avg_meter:.3f} "
        f"({100 * (avg_meter / true_rms - 1):+.0f} %)",
        "  on distorted currents use a true-RMS instrument; for power quality use an",
        "  analyser built to a standardised measurement method",
    ])


if __name__ == "__main__":
    instantaneous()
    triangle()
    pf_correction()
    capability()
    harmonics()
    voltage_distortion()
    meters()
