"""Chapter 35, last deeper round: duplicate events from a redundant pair of
gateways, the round trip of a grid operator's set point, the event log
over the plant's life, and the hierarchy of operator displays.

Run from the project root:   python -m companion.ch35.examples_r
Writes companion/ch35/expected/r_*.txt.
Synthetic data and teaching values (A-397, A-398).
"""
from __future__ import annotations

import numpy as np

from companion.ch35.common import emit


def duplicates(seed: int = 362) -> None:
    rng = np.random.default_rng(seed)
    n = 500                                        # events in a day
    both = rng.random(n) < 0.95                    # both gateways forward the event
    received = n + int(both.sum())
    lines = ["one day of events through a redundant pair of gateways (synthetic)",
             f"  events at the source: {n}; received at SCADA: {received}",
             "  kept when duplicates are recognised by source, point and",
             f"    source time stamp: {n}",
             "  kept if the stamp were taken on arrival: up to"
             f" {received} - the copies",
             "    arrive milliseconds apart and look like two events",
             "  the source stamp of lesson B is also what lets redundancy",
             "  work without doubling the event list and the work requests"]
    emit("r_dupes", lines)


STEPS = [  # step, seconds (teaching)
    ("grid operator to gateway (WAN)", 0.4),
    ("gateway to plant controller", 0.05),
    ("validation and next controller cycle", 0.2),
    ("units start to move", 0.5),
    ("ramp 20 MW at 10 MW a minute", 120.0),
    ("telemetry of the new value back", 0.8)]


def round_trip() -> None:
    total = sum(s for _, s in STEPS)
    comm = sum(s for name, s in STEPS if "ramp" not in name and "units" not in name)
    lines = ["a new export limit from the grid operator: round trip (teaching)",
             "  step                                       s"]
    for name, s in STEPS:
        lines.append(f"  {name:40s} {s:7.2f}")
    lines += [f"  total {total:.1f} s, of which communication and control {comm:.2f} s",
              "  the network and the controller take under two seconds; the",
              "  ramp the plant is allowed takes two minutes. A requirement",
              "  on response time is checked against the whole chain, and",
              "  the acknowledgement (set point received) is sent at once,",
              "  long before the plant has reached the new value"]
    emit("r_trip", lines)


def event_log() -> None:
    per_day, size_b, years = 2000, 200, 25
    gb = per_day * size_b * 365 * years / 1e9
    lines = ["the sequence-of-events and alarm log over the plant's life",
             f"  {per_day:,} events a day of {size_b} bytes for {years} years: {gb:.1f} GB",
             "  small next to the 12 TB of measurements (lesson C): the",
             "  event log is kept for the plant's life, with operator",
             "  actions and acknowledgements, because it answers 'what",
             "  happened in what order, and who did what' long after"]
    emit("r_events", lines)


def displays() -> None:
    levels = [("1 plant overview", 1),
              ("2 areas: substation, wind, PV, battery, auxiliaries, met", 6),
              ("3 equipment: 12 turbines, 10 PV blocks, 8 containers,", 0),
              ("  2 transformers, 8 feeders", 40),
              ("4 diagnostics: one per equipment type", 8)]
    total = sum(n for _, n in levels)
    lines = ["the hierarchy of operator displays (teaching)",
             "  level                                                   displays"]
    for name, n in levels:
        lines.append(f"  {name:55s} {n if n else '':>8}")
    lines += [f"  {total} displays, each reached from the one above in one click",
              "  the overview shows the plant's state and what needs action;",
              "  detail is one level down, never crowded onto the overview,",
              "  and every value shows its quality and age (lab D)"]
    emit("r_displays", lines)


if __name__ == "__main__":
    duplicates()
    round_trip()
    event_log()
    displays()
