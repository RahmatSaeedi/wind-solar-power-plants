"""Chapter 34, lesson B (deeper): the phase margin of the plant
controller's loop against its delay, pulses shorter than the scan, a
start sequence with step timeouts, command-feedback discrepancy timers
and a bumpless change from manual to automatic.

Run from the project root:   python -m companion.ch34.examples_r
Writes companion/ch34/expected/r_*.txt and diagrams/data/ch34-*.csv.
Teaching values (A-387, extended); the tuned PI is the one of ch 20.
"""
from __future__ import annotations

import math

import numpy as np
from scipy import optimize

from companion.ch34.common import csv, emit

KP, KI, TAU = 1.5, 0.8, 2.0          # ch 20 (D-024)


def loop(w: float, d: float) -> complex:
    """Open loop of the PI on the first-order park with a dead time d."""
    s = 1j * w
    return (KP + KI / s) / (1 + TAU * s) * np.exp(-s * d)


def crossover() -> float:
    return optimize.brentq(lambda w: abs(loop(w, 0.0)) - 1, 1e-3, 100)


def margin_deg(d: float) -> float:
    wc = crossover()
    return 180 + math.degrees(np.angle(loop(wc, 0.0))) - math.degrees(wc * d)


def phase_margin() -> None:
    wc = crossover()
    lines = ["phase margin of the tuned PI (kp 1.5, ki 0.8; park tau 2 s)",
             f"  crossover frequency {wc:.3f} rad/s; margin without delay"
             f" {margin_deg(0):.1f} deg",
             "  cycle s   loop delay s (1.5 cycles)   margin deg   ch 34 step test"]
    tests = {0.1: "no overshoot", 0.5: "no overshoot", 1.0: "22-28 % overshoot",
             2.0: "unstable"}
    for dt, seen in tests.items():
        d = 1.5 * dt
        lines.append(f"  {dt:7.1f}   {d:26.2f}   {margin_deg(d):10.1f}   {seen}")
    d45 = (margin_deg(0) - 45) / math.degrees(wc)
    rows = [(round(d, 2), round(margin_deg(d), 2)) for d in np.arange(0, 3.21, 0.1)]
    csv("ch34-margin.csv", "d,pm", rows)
    lines += [f"  a 45 deg margin allows {d45:.2f} s of loop delay: a cycle of"
              f" {d45 / 1.5:.2f} s at most",
              "  (delay = one cycle of computing + half a cycle of hold)",
              "  a delay costs phase in proportion to the crossover",
              "  frequency, so the faster a loop is tuned, the less delay",
              "  it tolerates; the margin gives the same verdict as the",
              "  step tests of lesson B before any test is run"]
    emit("r_margin", lines)


def pulse_missed(seed: int = 342) -> None:
    rng = np.random.default_rng(seed)
    scan = 50.0
    lines = ["a pulse read by an input that is sampled once a 50 ms scan",
             "  pulse ms   missed (theory)   missed (10,000 random phases)"]
    for w in (5.0, 10.0, 20.0, 50.0, 100.0):
        start = rng.uniform(0, scan, 10_000)
        # a sample at a multiple of the scan falls inside [start, start + w)
        seen = np.floor((start + w) / scan) > np.floor(start / scan)
        seen |= np.isclose(start % scan, 0)
        theory = max(0.0, 1 - w / scan)
        lines.append(f"  {w:8.0f}   {theory * 100:13.0f} %   {(1 - seen.mean()) * 100:24.1f} %")
    lines += [f"  counting pulses: each pulse and each gap must last a scan,",
              f"  so the fastest countable rate is {1000 / (2 * scan):.0f} pulses a second",
              "  a short pulse - a relay's trip contact, a meter's energy",
              "  pulse - is latched by the input card, stretched at the",
              "  source, or read by a counter or event module; it is",
              "  never left to the luck of the scan"]
    emit("r_pulse", lines)


STEPS = [  # battery container start sequence: step, nominal s, timeout s
    ("S1 permissives (fire healthy, HVAC on)", 2, 10),
    ("S2 DC pre-charge", 15, 30),
    ("S3 main DC contactor closed", 1, 5),
    ("S4 converter started, synchronised", 20, 60),
    ("S5 AC breaker closed", 1, 5),
    ("S6 ramp to the set point", 30, 90)]


def sequence() -> None:
    nominal = sum(n for _, n, _ in STEPS)
    worst = sum(t for _, _, t in STEPS)
    lines = ["start sequence of a battery container as steps with timeouts",
             "  step                                     nominal s   timeout s"]
    for name, n, t in STEPS:
        lines.append(f"  {name:40s} {n:9d}   {t:9d}")
    lines += [f"  nominal {nominal} s; the longest a healthy-looking start can",
              f"  take before a timeout ends it: {worst} s",
              "  every step has a timeout and every timeout a defined exit:",
              "  open what the sequence closed, in reverse order, and say",
              "  which step failed; a step without one waits for ever",
              "  (the dead end of the ch 20 state machine), and the",
              "  timeout is set from the measured time in the factory test"]
    emit("r_sequence", lines)


def discrepancy() -> None:
    rows = [("132 kV breaker close", 0.1, 0.5),
            ("motorised disconnector", 8.0, 15.0),
            ("HVAC damper", 60.0, 90.0),
            ("coolant pump: flow proven", 5.0, 15.0)]
    lines = ["command against feedback: discrepancy timers (teaching)",
             "  device                         travel s   timer s   alarm"]
    for name, travel, timer in rows:
        lines.append(f"  {name:30s} {travel:8.1f}   {timer:7.1f}   failed to operate")
    hidden_days = 7 / 2
    lines += ["  the same feedback, watched while no command is given,",
              "  catches an uncommanded change in one scan; without it, a",
              "  disconnector that opened by itself is found at the next",
              f"  weekly round - {hidden_days:.1f} days later on average",
              "  timers sit between the slowest healthy travel and the",
              "  shortest time anyone would wait; both alarms are tested"]
    emit("r_discrepancy", lines)


def transfer(case: str, dt: float = 0.1, t_end: float = 180.0) -> list[float]:
    """Output of the PI (MW) after the change to automatic at t = 0."""
    p_man, sp = 40.0, 60.0          # MW: manual output, operator's set point
    a = math.exp(-dt / TAU)
    y, integ = p_man, (0.0 if case == "no tracking" else p_man)
    out = []
    for k in range(int(t_end / dt) + 1):
        if case == "set point ramps":
            target = min(sp, p_man + 10.0 / 60.0 * k * dt)   # 10 MW a minute
        else:
            target = sp
        e = target - y
        u = min(100.0, max(0.0, KP * e + integ))
        integ += KI * dt * e
        out.append(u)
        y = a * y + (1 - a) * u
    return out


def bumpless() -> None:
    p_man = 40.0
    cases = ("no tracking", "integrator tracks", "set point ramps")
    traces = {c: transfer(c) for c in cases}
    lines = ["changing from manual (40 MW) to automatic with a 60 MW set point",
             "  case                      first output MW   step MW   peak MW"]
    for case, out in traces.items():
        lines.append(f"  {case:24s} {out[0]:16.1f}   {out[0] - p_man:+7.1f}"
                     f"   {max(out):7.1f}")
    rows = [(round(k * 0.1, 1), *(round(traces[c][k], 2) for c in cases))
            for k in range(0, 1801, 20)]
    csv("ch34-bumpless.csv", "t,none,track,ramp", rows)
    lines += ["  without tracking the controller starts from its own empty",
              "  integrator and drops the plant; tracking alone still",
              "  kicks by the gain times the error; tracking plus a set",
              "  point that starts at the measured value and ramps at the",
              "  allowed rate (10 MW a minute, lesson G) changes nothing at",
              "  the moment of transfer - the test of lesson G checks it"]
    emit("r_bumpless", lines)


if __name__ == "__main__":
    phase_margin()
    pulse_missed()
    sequence()
    discrepancy()
    bumpless()
