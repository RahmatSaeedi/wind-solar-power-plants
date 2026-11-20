"""Chapter 34, lesson B: the control system as a set of machines with
clocks - the layers and their speeds, the response budget of a PLC,
a PI loop run at three sample times, a breaker-close permissive with
bad-quality inputs, a heartbeat watchdog and its false alarms,
fail-safe output states, redundancy with a common cause, and the
actuators that set the pace.

Run from the project root:   python -m companion.ch34.examples_b
Writes companion/ch34/expected/b_*.txt and diagrams/data/ch34-sample.csv.
Teaching values (A-387); makers' data and the design decide.
"""
from __future__ import annotations

import itertools
import math

import numpy as np

from companion.ch34 import sources as src
from companion.ch34.common import csv, emit
from plantp import instrumentation as ic


def layers() -> None:
    rows = [("protection relays (ch 26)", "1-10 ms", "trip on faults"),
            ("equipment controllers", "1-100 ms", "inverter, PCS, pitch"),
            ("PLC / RTU", "50 ms scan", "interlocks, sequences, I/O"),
            ("plant controller (PPC)", "100-200 ms", "P, Q, V, f at the POC"),
            ("EMS / SCADA", "1 s - 15 min", "schedules, operators"),
            ("grid operator", "s - minutes", "limits, set points")]
    lines = ["layers of Plant P's control and how fast each one acts (teaching)",
             "  layer                         cycle          job"]
    for a, b, c in rows:
        lines.append(f"  {a:29s} {b:14s} {c}")
    lines += ["  each layer is about ten times slower than the one below",
              "  it and trusts it to do its own job: a PLC never replaces",
              "  protection, and the PPC never drives an inverter's",
              "  current loop - it sends set points the inverter's own",
              "  controller follows (ch 9, ch 20)"]
    emit("b_layers", lines)


def response() -> None:
    p = src.PLC
    t = ic.response_budget(p["input_ms"], p["scan_ms"], p["output_ms"], p["comms_ms"])
    needs = [("trip a breaker on a fault", 100.0), ("stop HVAC on a fire alarm", 1000.0),
             ("fast frequency response (hypothetical)", 500.0),
             ("follow an export-limit set point", 5000.0)]
    lines = ["worst-case response through the PLC (input + 2 scans + output + network)",
             f"  {p['input_ms']:.0f} + 2 x {p['scan_ms']:.0f} + {p['output_ms']:.0f}"
             f" + {p['comms_ms']:.0f} = {t:.0f} ms",
             "  function                                 needs ms   PLC fits?"]
    for name, need in needs:
        ok = "yes" if t <= need else "NO - protection"
        lines.append(f"  {name:40s} {need:8.0f}   {ok}")
    lines += ["  the change may arrive just after an input scan, so two",
              "  scans count; a fault trip belongs to protection relays",
              "  wired to the breaker, the rest fits the PLC with margin"]
    emit("b_response", lines)


def sampled_pi() -> None:
    tau, n_s = 2.0, 20.0
    rows, out = [], []
    lines = ["the tuned PI (kp 1.5, ki 0.8; park tau 2 s, ch 20) at four controller",
             "  cycles, each output applied one cycle after its sample",
             "  dt s   method    overshoot %   settled (2 %) s"]
    for dt in (0.1, 0.5, 1.0, 2.0):
        for meth in ("euler", "tustin"):
            n = int(n_s / dt) + 1
            y = ic.pi_loop(1.5, 0.8, tau, dt, n, method=meth, delay=1)
            ov = max(0.0, (y.max() - 1.0) * 100)
            outside = np.where(np.abs(y - 1.0) > 0.02)[0]
            ts = (outside[-1] + 1) * dt if len(outside) else 0.0
            rows.append((dt, meth, ov, ts))
            if ov > 100:
                lines.append(f"  {dt:4.1f}   {meth:7s}   {'unstable':>11s}   {'-':>15s}")
            else:
                ts_txt = f"{ts:15.1f}" if ts < n_s else f"{'> 20':>15s}"
                lines.append(f"  {dt:4.1f}   {meth:7s}   {ov:11.1f}   {ts_txt}")
            if meth == "euler" and dt <= 1.0:
                out.append((dt, y))
    grid = np.arange(0, n_s + 1e-9, 0.1)
    held = {dt: [float(y[min(int(round(t / dt - 0.5 + 1e-9)), len(y) - 1)]) for t in grid]
            for dt, y in out}
    csv("ch34-sample.csv", "t,y01,y05,y10",
        [(round(float(t), 1), round(held[0.1][i], 4), round(held[0.5][i], 4),
          round(held[1.0][i], 4)) for i, t in enumerate(grid)])
    ov1 = [r[2] for r in rows if r[0] == 1.0]
    lines += ["  while the cycle is short against the park's time constant",
              "  (dt/tau 0.05 to 0.25) the loop keeps the shape it was",
              f"  tuned for; at dt = tau/2 the one-cycle lag gives"
              f" {min(ov1):.0f}-{max(ov1):.0f} %",
              "  overshoot, at dt = tau the loop is unstable - ten or more",
              "  cycles per time constant, and the tuning is checked at",
              "  the real cycle with its computing delay"]
    emit("b_sampled", lines)


def permissive() -> None:
    conds = ["earth switch open", "no lockout", "DC healthy", "remote mode", "gas OK"]
    allowed = 0
    for combo in itertools.product((True, False), repeat=len(conds)):
        allowed += all(combo)
    lines = ["close permissive of a 33 kV feeder breaker (AND of five conditions)",
             "  " + ", ".join(conds),
             f"  combinations of the five inputs: {2 ** len(conds)}; close allowed in"
             f" {allowed}",
             "  each input has a quality: 'bad' or 'stale' counts as false",
             "  scenario                               result",
             "  all true, all good                      close allowed",
             "  gas pressure input bad (wire broken)    BLOCKED, alarm",
             "  remote mode stale (link lost)           BLOCKED, local only",
             "  a permissive fails safe: an input it cannot trust blocks",
             "  the action and says which input, so the operator is not",
             "  left guessing; the interlock that protects people (the",
             "  earth switch) is also mechanical, not only in the PLC"]
    emit("b_permissive", lines)


def watchdog() -> None:
    timeout_beats = 3
    per_year = 365 * 24 * 3600
    lines = ["heartbeat watchdog between the PPC and a battery PCS (1 beat a second)",
             f"  fallback after {timeout_beats} missed beats in a row; losses independent",
             "  lost beats    false timeouts a year   time to detect a real loss"]
    for p in (0.01, 0.001, 0.0001):
        false = p ** timeout_beats * per_year
        lines.append(f"  {p * 100:9.2f} %   {false:21.2f}   {timeout_beats:9d} s")
    lines += ["  a network that loses 1 % of packets trips the fallback",
              "  about thirty times a year for nothing; at 0.1 % it is",
              "  once in thirty years - the watchdog is set against the",
              "  measured loss rate, and a false timeout is recorded and",
              "  counted, not cleared and forgotten"]
    emit("b_watchdog", lines)


def failsafe() -> None:
    rows = [("breaker trip coil (protection)", "energise to trip",
             "supervised coil and DC; a dead output means no trip"),
            ("feeder 'close' permissive", "energise to permit",
             "a dead output blocks closing - safe"),
            ("HVAC run (BESS container)", "energise to run",
             "a dead output stops HVAC - alarmed"),
            ("fire-panel 'healthy' to plant", "de-energise to alarm",
             "a broken wire raises the alarm"),
            ("PCS run enable", "de-energise to stop",
             "loss of the enable stops the PCS")]
    lines = ["what each output does when its power or wire is lost (teaching)",
             "  output                           principle            on loss"]
    for a, b, c in rows:
        lines.append(f"  {a:32s} {b:20s}")
        lines.append(f"      {c}")
    lines += ["  de-energise-to-act fails safe for alarms and stops;",
              "  trip coils are energise-to-trip so a dead DC cannot trip",
              "  the plant at random - which is why the coil and the DC",
              "  are supervised and their failure is an urgent alarm"]
    emit("b_failsafe", lines)


def redundancy() -> None:
    p = src.PLC
    a = ic.availability(p["mtbf_h"], p["mttr_h"])
    pair = ic.parallel(a)
    beta = 0.05
    pair_cc = 1 - ((1 - beta) * (1 - a) ** 2 + beta * (1 - a))
    lines = ["the plant controller PLC: one or a redundant pair (teaching rates)",
             f"  one PLC: MTBF {p['mtbf_h']:,.0f} h, MTTR {p['mttr_h']:.0f} h:"
             f" A = {a:.6f}, {(1 - a) * 8760 * 60:.1f} min down a year",
             f"  independent pair: {(1 - pair) * 8760 * 3600:.2f} s down a year",
             f"  pair with 5 % common cause: {(1 - pair_cc) * 8760 * 60:.2f} min a year",
             "  the common cause (one power supply, one firmware bug, one",
             "  cabinet) sets the result, not the second CPU: separate",
             "  supplies, separate cabinets and a tested switch-over are",
             "  what make redundancy real (lesson E)"]
    emit("b_redundancy", lines)


def actuators() -> None:
    rows = [("PV inverter active power", 0.1), ("battery PCS", 0.1),
            ("turbine pitch (ch 11)", 2.0), ("on-load tap changer step", 5.0),
            ("33 kV breaker close", 0.08), ("capacitor bank switching (ch 27)", 30.0)]
    lines = ["the actuators behind the set points and how long they take (teaching)",
             "  actuator                               typical response s"]
    for name, t in rows:
        lines.append(f"  {name:38s} {t:8.2f}")
    lines += ["  the plant's response is set by its slowest actuator in the",
              "  loop: a voltage loop through tap changers acts in tens of",
              "  seconds, through inverters in fractions of one - the PPC",
              "  uses the fast ones first and the slow ones to restore",
              "  their reserve (ch 27, ch 28)"]
    emit("b_actuators", lines)


if __name__ == "__main__":
    layers()
    response()
    sampled_pi()
    permissive()
    watchdog()
    failsafe()
    redundancy()
    actuators()
