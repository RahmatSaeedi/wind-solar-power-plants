"""Chapter 27, section A - power-quality quantities in numbers: THD
against TDD at low output, spectral leakage of an unsynchronised window,
10-minute aggregation and the weekly 95th percentile, voltage unbalance
from three phase voltages, rapid voltage change from a cloud passage, and
the limits of the measuring chain.

Run from the project root:   python -m companion.ch27.examples_a
Writes companion/ch27/expected/a_*.txt and diagrams/data/ch27-*.csv.
Teaching values A-336 to A-340.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch27 import sources as src
from companion.ch27.common import csv, emit
from plantp import ac
from plantp import pq


def thd_tdd() -> None:
    i_rated = 5.5e6 / (math.sqrt(3) * 600)            # one PV inverter at 0.6 kV
    h_full = {h: v / 100 * i_rated for h, v in src.EMISSION["PV inverter"].items()}
    lines = ["THD against TDD for one PV inverter (harmonic currents roughly",
             "  fixed in amperes, as many converters behave; teaching):",
             "  output   fundamental A   THD     TDD"]
    for load in (0.05, 0.1, 0.3, 0.6, 1.0):
        i1 = load * i_rated
        lines.append(f"  {load:6.0%}   {i1:13.0f}   {pq.thd(h_full, i1):5.1%}   {pq.tdd(h_full, i_rated):5.1%}")
    lines += ["  at a cloudy dawn the THD looks alarming while the harmonic",
              "  amperes - and their effect on the network voltage - are the",
              "  same as at noon: a limit stated against the demand current",
              "  (TDD) or in amperes judges the plant fairly; a report that",
              "  quotes THD at low power must say so"]
    emit("a_thdtdd", lines)


def leakage() -> None:
    fs = 10240.0
    n = int(fs * 0.2)                                # 200 ms window
    t = np.arange(n) / fs
    rows, lines = [], ["a 200 ms window (5 Hz bins) on a 49.8 Hz signal with a 5th harmonic",
                       "  of 1.2 % and an interharmonic of 0.3 % at 182 Hz (teaching):",
                       "  window                      bin 250 Hz %   bin 180 Hz %   largest stray %"]
    for name, f1 in (("synchronised to 49.8 Hz", 49.8), ("fixed at 50 Hz", 50.0)):
        n_win = int(round(fs * 10 / f1))
        tt = t[:n_win] if n_win <= n else np.arange(n_win) / fs
        x = (math.sqrt(2) * (np.sin(2 * math.pi * 49.8 * tt) + 0.012 * np.sin(2 * math.pi * 5 * 49.8 * tt)
                             + 0.003 * np.sin(2 * math.pi * 182 * tt)))
        freq, amp = pq.spectrum(x, fs)
        amp = 100 * amp / amp.max()
        def at(f):
            return float(amp[np.argmin(np.abs(freq - f))])
        mask = (freq > 300) & (freq < 1000) & (np.abs(freq - 5 * 49.8) > 10)
        lines.append(f"  {name:27s} {at(5 * 49.8):12.2f}   {at(182):12.2f}   {amp[mask].max():15.2f}")
        if f1 == 50.0:
            rows = [(f"{a:.1f}", f"{b:.4f}") for a, b in zip(freq, amp) if a <= 400]
    csv("ch27-leakage.csv", "f,amp", rows)
    lines += ["  a window that is not exactly ten cycles of the actual",
              "  frequency smears the fundamental into its neighbours and",
              "  spills into the harmonic and interharmonic bins; the",
              "  measurement method (STD-035) locks the window to the",
              "  measured frequency and groups the bins - an instrument",
              "  that does not is not comparable"]
    emit("a_leakage", lines)


def aggregation() -> None:
    w = src.week()
    v5 = w["v5_pct"]
    lines = ["a week of 10-minute 5th-harmonic voltages at the POC (A-338):",
             f"  1,008 values: mean {v5.mean():.2f} %, 95th percentile {pq.percentile(v5, 95):.2f} %,"
             f" maximum {v5.max():.2f} %",
             "  the 95th percentile ignores the highest 5 % (about 8 hours)",
             "  - the usual form of a weekly assessment; one high 10-minute",
             "  value is not a breach, a high percentile is",
             f"  2-hour aggregation (12 values) raises nothing: max {pq.aggregate(v5, 12).max():.2f} %"]
    emit("a_aggregation", lines)


def unbalance() -> None:
    lines = ["voltage unbalance from three phase voltages (negative / positive):",
             "  phase magnitudes pu        angles deg           unbalance %"]
    for mags, angs in (((1.0, 1.0, 1.0), (0, -120, 120)), ((1.0, 0.98, 1.01), (0, -120, 120)),
                       ((1.0, 0.97, 1.0), (0, -121, 119.5))):
        va, vb, vc = (m * complex(math.cos(math.radians(a)), math.sin(math.radians(a)))
                      for m, a in zip(mags, angs))
        u = ac.unbalance_factor(va, vb, vc)
        lines.append(f"  {str(mags):24s}   {str(angs):18s}   {100 * u:10.2f}")
    lines += ["  a converter plant draws balanced currents and adds little",
              "  unbalance itself; but its converters see the network's",
              "  unbalance as a negative-sequence voltage, and their control",
              "  and DC links respond to it (ripple at 100 Hz) - the",
              "  unbalance at the POC is measured before and after"]
    emit("a_unbalance", lines)


def rapid_change() -> None:
    lines = ["rapid voltage change when a cloud takes 30 MW of PV in a minute",
             "  bus (S_sc MVA, X/R)            dU %, Q held   Q to cancel Mvar"]
    for name, s_sc, xr in (("POC, strong (1,500, 8)", 1500.0, 8.0), ("POC, weak (500, 5)", 500.0, 5.0),
                           ("33 kV bus (365, 10)", 365.0, 10.0)):
        du = pq.voltage_change(-30.0, 0.0, s_sc, xr)
        q = 30.0 / xr
        lines.append(f"  {name:30s} {100 * du:12.2f}   {q:16.1f}")
    lines += ["  a resistive grid feels active power, a reactive one the",
              "  reactive power: on a weak, resistive network a cloud is a",
              "  visible step; the converters' fast Q (lesson B) can cancel",
              "  it - the limit for rapid changes and flicker is the",
              "  operator's (the flicker report of the STD-130 family)"]
    emit("a_rvc", lines)


def chain() -> None:
    rows = [("capacitive VT (CVT)", "resonant: wrong at harmonics", "no"),
            ("inductive VT", "good to a few kHz", "voltages"),
            ("protection CT core", "phase error, saturates", "no"),
            ("metering CT core", "good to kHz, low burden", "currents"),
            ("PQ instrument", "class of the method", "certificate, sync")]
    lines = ["the measuring chain sets what can be trusted (concept):",
             "  element               at harmonics                     use for harmonics"]
    for a, b, c in rows:
        lines.append(f"  {a:21s} {b:32s} {c}")
    lines += ["  a 132 kV bay often has only capacitive VTs: harmonic",
              "  voltages measured through them are wrong at the 5th and",
              "  beyond - the monitoring plan names the transducer, not only",
              "  the instrument"]
    emit("a_chain", lines)


if __name__ == "__main__":
    thd_tdd()
    leakage()
    aggregation()
    unbalance()
    rapid_change()
    chain()
