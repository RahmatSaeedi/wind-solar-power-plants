"""Chapter 26 - expansion round 3: line differential over a channel whose
two directions differ in delay, the charging current a differential sees
on a line and on a cable, VT fuse-failure supervision as a logic table,
hidden failures against the test interval, and dependability and
security from a record of events.

Run from the project root:   python -m companion.ch26.examples_p
Writes companion/ch26/expected/p_*.txt and diagrams/data/ch26-hidden.csv.
Teaching values A-331 to A-335.
"""
from __future__ import annotations

import math

from companion.ch26.common import csv, emit


# [start: asymmetry]
def asymmetry_spill(through: float, dt_ms: float, f: float = 50.0) -> float:
    """Differential current a line differential computes for a through
    current when the channel delay differs by dt between the two
    directions: the delay, estimated as the mean of the two, is wrong
    by dt/2, so the remote current is shifted by 360 f dt/2 degrees."""
    angle = math.radians(360 * f * dt_ms / 1e3 / 2)
    return through * 2 * math.sin(angle / 2)
# [end: asymmetry]


def asymmetry() -> None:
    i_load = 437.0
    lines = ["line differential: the channel's delay differs by dt in the two",
             f"  directions; through current {i_load:.0f} A (full export), pickup 200 A",
             "  asymmetry ms   phase error deg   false differential A   trips?"]
    for dt in (0.5, 1.0, 2.0, 4.0):
        s = asymmetry_spill(i_load, dt)
        lines.append(f"  {dt:12.1f}   {360 * 50 * dt / 2e3:15.1f}   {s:20.0f}   {'YES' if s > 200 else 'no'}")
    s4 = asymmetry_spill(i_load, 4.0)
    lines += ["  a route that changes on the telecom network can add",
              "  milliseconds in one direction only: with 4 ms the relay sees",
              f"  {s4:.0f} A of 'fault' at full export and trips; the cures are",
              "  time stamps from a satellite clock at both ends, a fixed",
              "  dedicated fibre, and a bias that grows with the through",
              "  current - the channel is part of the protection"]
    emit("p_asymmetry", lines)


def charging() -> None:
    lines = ["charging current seen by a line differential (no load, teaching):",
             "  circuit                    charging A   % of a 200 A pickup"]
    for name, i in (("132 kV overhead line 7 km", 1.5), ("132 kV cable 7 km", 33.8),
                    ("132 kV cable 20 km", 33.8 * 20 / 7)):
        lines.append(f"  {name:26s} {i:10.1f}   {100 * i / 200:18.0f}")
    lines += ["  charging current enters at one end and does not leave at the",
              "  other: a differential sees it as a fault current; on the",
              "  overhead line it is negligible, on a long cable it eats into",
              "  the margin and the relay compensates it with the measured",
              "  voltage - a setting choice when the export route is cable"]
    emit("p_charging", lines)


def vt_supervision() -> None:
    rows = [("VT fuse blown, one phase", "V2 high", "I2 low", "block 21/67, alarm"),
            ("real earth fault", "V2 high", "I2 high", "allow"),
            ("all three VT phases lost", "V all low", "I unchanged", "block, alarm"),
            ("line energised, far end", "V rising", "I small", "allow after delay")]
    lines = ["VT fuse-failure supervision (concept): what the relay sees and does",
             "  case                        voltage     current       action"]
    for case, v, i, act in rows:
        lines.append(f"  {case:27s} {v:11s} {i:13s} {act}")
    lines += ["  a lost VT voltage looks like a close fault to a distance",
              "  relay (zero voltage, normal current); the supervision tells",
              "  them apart by the current - no current change, no fault;",
              "  the logic and its settings are tested like any function"]
    emit("p_vts", lines)


def hidden() -> None:
    lam = 0.02                    # undetected failures per relay-year (teaching)
    rows = []
    lines = ["hidden failures against the test interval: unavailability ~ lambda T / 2",
             f"  failure rate {lam} per relay-year; self-supervision catches 80 %",
             "  test interval y   without supervision   with supervision"]
    for t in (1, 2, 4, 6, 8):
        u0 = lam * t / 2
        u1 = lam * 0.2 * t / 2
        rows.append((t, f"{100 * u0:.2f}", f"{100 * u1:.2f}"))
        lines.append(f"  {t:15d}   {u0:19.2%}   {u1:16.2%}")
    csv("ch26-hidden.csv", "t,plain,supervised", rows)
    lines += ["  a failure that nothing reports waits for the next test: on",
              "  average half an interval; self-supervision finds most of",
              "  them at once and lets the interval grow - which is why",
              "  numerical relays are tested every 4-6 years (teaching), but",
              "  only if their alarms are seen (lab E)"]
    emit("p_hidden", lines)


def statistics() -> None:
    required, correct, failed, unwanted = 40, 39, 1, 2
    dep = correct / required
    sec = correct / (correct + unwanted)
    lines = ["protection performance from five years of event records (teaching):",
             f"  faults that needed a trip {required}; correct trips {correct}; failures to trip"
             f" {failed};",
             f"  unwanted trips (no fault, or the wrong breaker) {unwanted}",
             f"  dependability = correct / required = {dep:.1%}",
             f"  security = correct / (correct + unwanted) = {sec:.1%}",
             "  every relay design trades one for the other: more backup",
             "  raises dependability and risks security; the event analysis",
             "  of lab E feeds these counts - an unwanted trip is a finding",
             "  like a failure to trip, never 'just a nuisance'"]
    emit("p_stats", lines)


if __name__ == "__main__":
    asymmetry()
    charging()
    vt_supervision()
    hidden()
    statistics()
