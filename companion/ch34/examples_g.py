"""Chapter 34, lesson G: grid-service control interfaces - who may send
which set point and with what priority, validation of what arrives,
stale set points and the fallback of chapter 20, the latency and
accuracy budget of telemetry, priority when two limits meet, and the
tests that prove each control mode. Only services required by the
connection or permitted by the project are built (REQ-S01 is the
hypothetical service of ch 20).

Run from the project root:   python -m companion.ch34.examples_g
Writes companion/ch34/expected/g_*.txt and diagrams/data/ch34-modes.csv.
Teaching values (A-391); the connection agreement and the grid
operator's requirements decide the real ones (U-115).
"""
from __future__ import annotations

import numpy as np

from companion.ch34 import sources as src
from companion.ch34.common import csv, emit
from plantp import instrumentation as ic


def sources_table() -> None:
    rows = [("grid operator (RTU)", "export limit, Q or V set point", "1", "required (placeholder)"),
            ("service call (REQ-S01)", "upward reserve 5 MW, 18-22 h", "2", "hypothetical"),
            ("EMS schedule", "battery plan, export plan", "3", "project"),
            ("local operator", "test values, maintenance limits", "by permit", "project")]
    lines = ["set-point sources of the plant controller (teaching; ch 20 priorities)",
             "  source                   set points                       priority"]
    for s, sp, pr, st in rows:
        lines.append(f"  {s:24s} {sp:32s} {pr}")
        lines.append(f"      status: {st}")
    lines += ["  safety and protection sit above all of them; a source",
              "  that is neither required nor permitted is not wired in",
              "  'in case' - an unused input is a door left open (ch 36)"]
    emit("g_sources", lines)


def validation() -> None:
    lo, hi, step = src.SERVICE["p_limit"]
    received = [(0, 100.0), (60, 80.0), (120, 140.0), (180, 40.0), (240, 70.0), (300, 60.0)]
    last = 100.0
    lines = ["export-limit set points as received and as accepted (MW, teaching)",
             f"  range {lo:.0f}-{hi:.0f} MW; ramp {step:.0f} MW a minute, so one message",
             f"  may move the limit by at most {step * 3:.0f} MW (messages 60 s apart, 3x margin)",
             "  time s   received   accepted   reason"]
    for t, sp in received:
        acc, why = ic.validate_setpoint(sp, lo, hi, last, step * 3)
        lines.append(f"  {t:6d}   {sp:8.0f}   {acc:8.0f}   {why}")
        last = acc
    lines += ["  a set point outside its range is a corrupted or wrong",
              "  message; a jump larger than allowed may be real (an",
              "  emergency) - the rule and what happens next (reject and",
              "  alarm, or ramp to it) is agreed with the grid operator,",
              "  written in the interface specification and tested"]
    emit("g_validation", lines)


def stale() -> None:
    s = src.SERVICE
    events = [(0, "link healthy, set points every 4 s"), (100, "link lost"),
              (100 + s["stale_s"], "set point stale: hold last value, alarm"),
              (100 + s["hold_s"], "1 h without link: fallback schedule (ch 20)"),
              (100 + s["hold_s"] + 1800, "link back: wait for a fresh set point"),
              (100 + s["hold_s"] + 1804, "fresh set point accepted, normal mode")]
    out = []
    lines = ["a lost link to the grid operator, step by step (teaching timings)",
             "  t s     mode"]
    for k, (t, m) in enumerate(events, 1):
        lines.append(f"  {t:6.0f}  {m}")
        out.append((k, t))
    csv("ch34-modes.csv", "k,t", out)
    lines += ["  the plant never invents a set point: it holds, then",
              "  follows a pre-agreed fallback, and returns only on a",
              "  fresh, valid message - each mode change is time-stamped",
              "  and sent to the operator when the link returns"]
    emit("g_stale", lines)


def telemetry() -> None:
    parts = [("meter and transducer", 100.0), ("PPC cycle", 200.0),
             ("plant network to RTU", 100.0), ("RTU to control centre", 400.0)]
    total = sum(ms for _, ms in parts)
    u_p = ic.combine(0.2 / 3 ** 0.5, 0.2 / 3 ** 0.5, 0.2 / 3 ** 0.5)   # CT, VT, meter class 0.2
    lines = ["telemetry of active power to the grid operator (teaching budget)",
             "  part                         ms"]
    for name, ms in parts:
        lines.append(f"  {name:28s} {ms:4.0f}")
    lines += [f"  total {total:.0f} ms against a placeholder of 1,000 ms",
              f"  accuracy, CT + VT + meter of class 0.2: +/-{2 * u_p:.2f} % (k = 2)",
              "  the operator needs both numbers: how old the value is and",
              "  how good it is - each value travels with its quality and",
              "  a time stamp from the synchronised clock (lesson A)"]
    emit("g_telemetry", lines)


def conflict() -> None:
    p_avail, limit, reserve = 92.0, 80.0, 5.0
    sched = min(p_avail - reserve, limit)
    lines = ["two limits at once at 19:00 (teaching): which wins?",
             f"  available {p_avail:.0f} MW; grid operator export limit {limit:.0f} MW;"
             f" REQ-S01 reserve {reserve:.0f} MW",
             f"  export set point = min(available - reserve, limit) = {sched:.0f} MW",
             f"  headroom above the set point: {p_avail - sched:.0f} MW, more than the"
             f" {reserve:.0f} MW reserve",
             "  both are honoured because they ask for compatible things;",
             "  when they cannot both be met, the priority of ch 20",
             "  decides (operator limit above the service) and the",
             "  shortfall is reported to the service buyer at once"]
    emit("g_conflict", lines)


def mode_tests() -> None:
    modes = [("export limit", 4), ("Q set point", 5), ("V control (droop)", 5),
             ("power factor", 3), ("REQ-S01 reserve (if contracted)", 4),
             ("fallback schedule", 2), ("ramp limit", 3)]
    y = ic.pi_loop(1.5, 0.8, 2.0, 0.1, 301)
    out = np.where(np.abs(y - 1.0) > 0.02)[0]
    ts = (out[-1] + 1) * 0.1
    n = sum(k for _, k in modes)
    lines = ["control-mode verification: test points per mode (teaching)",
             "  mode                               test points"]
    for m, k in modes:
        lines.append(f"  {m:34s} {k:11d}")
    lines += [f"  {n} test points; each with a pass criterion, e.g. a Q step:",
              f"    settled to 2 % in {ts:.1f} s against a placeholder of 10 s - pass",
              "  tests run first in the simulator, then at site under a",
              "  test plan agreed with the grid operator; only modes the",
              "  connection requires or the project offers are tested and",
              "  enabled - the others stay disabled and are recorded so"]
    emit("g_tests", lines)


if __name__ == "__main__":
    sources_table()
    validation()
    stale()
    telemetry()
    conflict()
    mode_tests()
