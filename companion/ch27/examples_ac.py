"""Chapter 27 - expansion round 13: the plant's own switching events as
rapid voltage changes at the POC, and a power-oscillation-damping
function: how much damping a modulation gain adds and what power swing
the plant must provide.

Run from the project root:   python -m companion.ch27.examples_ac
Writes companion/ch27/expected/ac_*.txt and diagrams/data/ch27-pod.csv.
Teaching values (A-337, A-339).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch27 import sources as src
from companion.ch27.common import csv, emit
from plantp import pq


def switching_events() -> None:
    n = src.NET
    events = [
        ("5 Mvar filter switched in", 0.0, 5.0),
        ("one wind feeder trips (20 MW)", -20.0, 0.0),
        ("battery 20 MW charge to discharge", 40.0, 0.0),
        ("whole plant trips, Q 0", -100.0, 0.0),
        ("whole plant trips, giving 33 Mvar", -100.0, -33.0),
    ]
    lines = ["the plant's own events as voltage steps at the POC (1,500 MVA, X/R 8)",
             "  and at the 33 kV bus (365 MVA, X/R 10); teaching RVC limit 3 %",
             "  event                               POC dU %   33 kV dU %   POC vs limit"]
    for name, dp, dq in events:
        u_poc = 100 * pq.voltage_change(dp, dq, n["s_sc_poc"], n["xr_poc"])
        u_33 = 100 * pq.voltage_change(dp, dq, n["s_sc_33"], n["xr_33"])
        s33 = "     (off)" if "whole" in name else f"{u_33:10.2f}"
        lines.append(f"  {name:35s} {u_poc:8.2f}   {s33}   {abs(u_poc) / 3:11.0%}")
    lines += ["  only a whole-plant trip while giving reactive power reaches",
              "  the limit at the POC; inside the plant the 33 kV bus",
              "  sees steps four times larger - the filter switching is a",
              "  1.4 % event there; the event list (with how often each",
              "  happens) is part of the PQ assessment, and a trip that",
              "  must be rare is designed to be rare (ch 26)"]
    emit("ac_events", lines)


def pod() -> None:
    f, zeta0 = 0.8, 0.06
    w = 2 * math.pi * f
    dt = 0.01
    t = np.arange(0, 10, dt)
    rows = {}
    lines = ["power oscillation damping (modal teaching model: 0.8 Hz mode,",
             "  damping 0.06; the plant modulates P against the mode's speed)",
             "  gain   damping   plant swing peak MW   time to 10 % s"]
    for gain in (0.0, 0.5, 1.0):
        zeta = zeta0 + gain * 0.1
        x, v = 3.0, 0.0
        xs, ps = [], []
        for _ in t:
            p_mod = -gain * 0.2 * v                     # MW (v in MW/s)
            a = -2 * zeta0 * w * v - w * w * x + w * p_mod   # adds 0.1 x gain
            v += a * dt
            x += v * dt
            xs.append(x)
            ps.append(p_mod)
        xs = np.array(xs)
        env = np.abs(xs)
        k10 = next((i for i in range(len(t) - 1, -1, -1) if env[i] > 0.3), 0)
        rows[gain] = xs
        lines.append(f"  {gain:4.1f}   {zeta:7.2f}   {max(abs(p) for p in ps):19.2f}   "
                     f"{t[min(k10 + 1, len(t) - 1)]:14.1f}")
    csv("ch27-pod.csv", "t,g0,g1", [(f"{a:.2f}", f"{b:.3f}", f"{c:.3f}")
                                    for a, b, c in zip(t[::2], rows[0.0][::2], rows[1.0][::2])])
    lines += ["  more gain, more damping - and a larger power swing the",
              "  plant must be able to give at that moment (headroom in",
              "  both directions: curtailed PV or the battery); the",
              "  operator states the mode and the required damping, the",
              "  model (ch 28) shows the gain is stable, and a test shows",
              "  the plant's power swings at the mode's frequency"]
    emit("ac_pod", lines)


if __name__ == "__main__":
    switching_events()
    pod()
