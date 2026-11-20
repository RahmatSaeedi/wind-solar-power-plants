"""Chapter 20, section A - control hierarchy and the loops inside it: the
time scales of each layer, a plant-controller loop on a first-order
plant (three tunings and a rate limit), and frequency and voltage droop.

Run from the project root:   python -m companion.ch20.examples_a
Writes companion/ch20/expected/a_*.txt and diagrams/data/ch20-*.csv.
Teaching values A-299.
"""
from __future__ import annotations

import numpy as np

from companion.ch20 import sources as src
from companion.ch20.common import csv, emit
from plantp import control as ct


def layers() -> None:
    lines = ["control layers of Plant P and their time scales (teaching):",
             "  layer                   decides                         every",
             "  device (inverter, WTG)  current, pitch, torque          ms",
             "  subsystem (park, BMS)   unit set points, limits         100 ms-1 s",
             "  plant controller (PPC)  P, Q at the POC, ramps          100 ms-1 s",
             "  energy management       battery plan, curtailment       1-15 min",
             "  scheduling              day-ahead, intraday plans       hours",
             "  each layer follows the one above within its own limits and",
             "  reports what it can do; a slower layer never asks a faster",
             "  one for more than its capability (chapters 9, 11, 19)"]
    emit("a_layers", lines)


def loops() -> None:
    """Plant-controller loop on a park that answers with tau = 2 s."""
    dt, n = 0.05, 600
    cases = {"slow (kp 0.5, ki 0.2)": (0.5, 0.2, None, False),
             "tuned (kp 1.5, ki 0.8)": (1.5, 0.8, None, False),
             "aggressive (kp 6, ki 8)": (6.0, 8.0, None, False),
             "tuned, rate 0.1 pu/s": (1.5, 0.8, 0.1, False),
             "tuned, rate, anti-windup": (1.5, 0.8, 0.1, True)}
    lines = ["a step of the POC set point (normalised to 1); park tau 2 s:",
             "  tuning                        rise 10-90 % s  overshoot %  settle 2 % s"]
    rows = {}
    for name, (kp, ki, rate, aw) in cases.items():
        y, u = ct.pi_response(kp, ki, 2.0, dt, n, setpoint=1.0, rate=rate,
                              anti_windup=aw)
        t = np.arange(1, n + 1) * dt
        r10 = t[np.argmax(y >= 0.1)]
        r90 = t[np.argmax(y >= 0.9)]
        over = max(0.0, (y.max() - 1.0) * 100)
        out = np.where(np.abs(y - 1.0) > 0.02)[0]
        settle = t[out[-1]] if len(out) else 0.0
        lines.append(f"  {name:28s}  {r90 - r10:13.2f}   {over:10.1f}   {settle:11.1f}")
        rows[name] = y
    lines += ["  a stronger loop is faster but overshoots and rings; a rate",
              "  limit turns the response into a ramp, but the integral keeps",
              "  growing while the command is held back (windup) and the plant",
              "  overshoots badly; anti-windup stops the integral while a",
              "  limit holds the command; tuning is checked in simulation and",
              "  in a step test (section C)"]
    emit("a_loops", lines)
    keys = list(rows)
    csv("ch20-pi.csv", "t," + ",".join(f"c{k}" for k in range(len(keys))),
        [(f"{(i + 1) * dt:.2f}",) + tuple(f"{rows[k][i]:.4f}" for k in keys)
         for i in range(0, n, 4)])


# [start: delay]
def delayed_loop(kp: float, ki: float, tau: float, delay_s: float,
                 dt: float = 0.05, n: int = 1200):
    """PI loop on a first-order plant whose measurement arrives delay_s
    late (communication and filtering): returns the response."""
    lag = int(round(delay_s / dt))
    y = integ = 0.0
    hist = [0.0] * (lag + 1)
    ys = []
    for _ in range(n):
        e = 1.0 - hist[0]                    # the controller sees old y
        integ += e * dt
        u = kp * e + ki * integ
        y += dt * (u - y) / tau
        hist = hist[1:] + [y]
        ys.append(y)
    return np.array(ys)
# [end: delay]


def delays() -> None:
    lines = ["the same tunings with a measurement delay (park tau 2 s):",
             "  tuning                   delay s   overshoot %   still moving at 60 s"]
    for name, kp, ki in (("tuned (1.5, 0.8)", 1.5, 0.8),
                         ("aggressive (6, 8)", 6.0, 8.0)):
        for dl in (0.0, 0.2, 0.5, 1.0):
            y = delayed_loop(kp, ki, 2.0, dl)
            over = max(0.0, (y.max() - 1.0) * 100)
            moving = np.abs(y[-100:] - 1.0).max() > 0.02
            over_txt = f"{over:11.1f}" if over < 1000 else "   unstable"
            lines.append(f"  {name:22s} {dl:7.1f}   {over_txt}   {'yes' if moving else 'no':>20s}")
    lines += ["  a 0.2 s delay that the tuned loop shrugs off makes the",
              "  aggressive loop overshoot by half, and at 0.5 s it grows",
              "  without bound; even the tuned loop rings at 1 s: delay, not",
              "  gain alone, sets how fast a plant controller may be; the",
              "  delay of the real path is measured at commissioning"]
    emit("a_delay", lines)


def droop() -> None:
    lines = ["frequency droop of Plant P (teaching settings, A-299):",
             "  frequency Hz   change MW (4 % droop, 0.02 Hz deadband, 110 MW)"]
    for f in (49.8, 49.9, 49.97, 50.0, 50.1, 50.3):
        dp = round(float(ct.droop_power(f - 50.0, 110.0, 0.04, 0.02)), 1) + 0.0
        lines.append(f"  {f:12.2f}   {dp:+8.1f}")
    lines += ["  a fall in frequency asks for more power: a plant at full",
              "  output has none to give unless it was held below its",
              "  available power (headroom) or a battery gives it; a rise",
              "  is met by curtailing (section B)",
              "voltage-reactive droop at the POC (4 % slope, 33 Mvar):",
              "  voltage pu   reactive Mvar (+ export)"]
    for v in (0.96, 0.98, 1.00, 1.01, 1.03):
        q = round(float(ct.droop_reactive(v - 1.0, 33.0, 0.04)), 1) + 0.0
        lines.append(f"  {v:10.2f}   {q:+8.1f}")
    lines += ["  settings, deadbands and whether the service is wanted at all",
              "  come from the operator and the contract (chapter 28)"]
    emit("a_droop", lines)


if __name__ == "__main__":
    layers()
    loops()
    delays()
    droop()
