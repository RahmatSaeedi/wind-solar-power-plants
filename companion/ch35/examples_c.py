"""Chapter 35, lesson C: SCADA operations and design in numbers - which
diagram answers which question, an alarm that chatters and the rule
that calms it, the buffer a device needs when the historian is away,
retention of raw data, aggregates and events, network recovery against
the controller's watchdog, roles and rights, and the acceptance tests.

Run from the project root:   python -m companion.ch35.examples_c
Writes companion/ch35/expected/c_*.txt and diagrams/data/ch35-chatter.csv.
Synthetic data and teaching values (A-398); nothing connects to a plant.
"""
from __future__ import annotations

import numpy as np

from companion.ch35.common import csv, emit
from plantp import scada as sc


def diagrams() -> None:
    rows = [("physical topology", "where are the boxes and cables?"),
            ("logical topology", "who can talk to whom, in which subnet?"),
            ("communication path", "which hops does one message take?"),
            ("interface / data flow", "which data cross which boundary?"),
            ("point-to-point wiring", "which terminal goes to which?"),
            ("zones and conduits", "where are the security boundaries? (ch 36)"),
            ("redundancy / failover", "what happens when this link fails?"),
            ("time synchronisation", "where does each clock get its time?")]
    lines = ["the diagram types of a SCADA design and the question each answers",
             "  diagram                    answers"]
    for d, q in rows:
        lines.append(f"  {d:26s} {q}")
    lines += ["  no single drawing answers all of these; each is a",
              "  controlled document with an owner, and the same device",
              "  carries the same tag on every one of them (lesson F)"]
    emit("c_diagrams", lines)


def chatter(seed: int = 352) -> None:
    rng = np.random.default_rng(seed)
    t = np.arange(0, 3600)                          # one hour of 1 s values
    temp = 79.0 + 1.5 * np.sin(2 * np.pi * t / 1800) + rng.normal(0, 0.6, t.size)
    raw = sc.alarm_states(temp, 80.0, 0.0, 1)
    tuned = sc.alarm_states(temp, 80.0, 1.0, 10)
    n_raw, n_tuned = sc.transitions(raw), sc.transitions(tuned)
    csv("ch35-chatter.csv", "t,temp", [(int(k), round(float(temp[k]), 2)) for k in t[::20]])
    lines = ["a transformer oil-temperature alarm at 80 C, one hour (synthetic)",
             f"  no deadband, no delay: {n_raw} alarms in the hour",
             f"  1 K deadband and 10 s delay: {n_tuned} alarm(s)",
             "  the raw rule chatters on noise around the limit and buries",
             "  the operator; a delay before raising and a deadband before",
             "  clearing turn the same hour into what really happened -",
             "  both are written in the alarm philosophy and tested"]
    emit("c_chatter", lines)


def buffers() -> None:
    tags, per, b, hours = 2_000, 1.0, 20, 24
    gb = tags / per * b * hours * 3600 / 1e9
    lines = ["buffer a device needs when the historian is away (teaching)",
             f"  {tags:,} tags at {per:.0f} s, {b} bytes each, {hours} h outage:"
             f" {gb:.1f} GB",
             "  data buffered at the source and sent when the link returns",
             "  keeps the record whole; without a buffer the hours of an",
             "  outage - often the interesting ones - are a hole in every",
             "  trend and in the availability evidence (ch 37)"]
    emit("c_buffers", lines)


def retention() -> None:
    rows = [("raw values, 1 s, 22,300 tags", 22_300, 1.0, 2, 0.1),
            ("1-min aggregates (min, mean, max)", 22_300 * 3, 60.0, 25, 1.0),
            ("events and alarms", 2_000, 3600.0, 25, 1.0)]
    lines = ["retention plan of the historian (teaching; 12 bytes a value)",
             "  data                                   years   kept     GB"]
    total = 0.0
    for name, n, per, yrs, keep in rows:
        gb = sc.retention_gb(n, per, yrs, keep=keep)
        total += gb
        lines.append(f"  {name:38s} {yrs:5d}   {keep * 100:4.0f} %  {gb:7,.0f}")
    lines += [f"  total about {total:,.0f} GB",
              "  raw seconds for two years serve fault and dispute",
              "  analysis; aggregates for the plant's life serve trends,",
              "  warranties and the repowering study (ch 53) - the plan",
              "  is set with the owner, lenders and grid operator's rules"]
    emit("c_retention", lines)


def failover() -> None:
    watchdog_s = 3.0                               # ch 34 heartbeat: 3 missed beats
    rows = [("redundant parallel networks", 0.0), ("ring protocol (fast)", 0.02),
            ("rapid spanning tree (typical)", 2.0), ("classic spanning tree", 30.0)]
    lines = ["network recovery after a fibre cut against the 3 s watchdog of ch 34",
             "  recovery method                     recovery s   fallback triggered?"]
    for name, s in rows:
        lines.append(f"  {name:35s} {s:10.2f}   {'YES' if s >= watchdog_s else 'no'}")
    lines += ["  a network that heals in seconds is close to the watchdog;",
              "  one that heals in half a minute throws every battery PCS",
              "  into its fallback at each cut - recovery time and",
              "  watchdog are specified together, and the failover is",
              "  tested by pulling a fibre in the site acceptance test"]
    emit("c_failover", lines)


def roles() -> None:
    funcs = ["view", "ack", "operate", "settings", "software"]
    roles_ = {"viewer": [1, 0, 0, 0, 0], "operator": [1, 1, 1, 0, 0],
              "maintenance": [1, 1, 1, 0, 0], "control engineer": [1, 1, 1, 1, 1],
              "vendor (remote, escorted)": [1, 0, 0, 0, 0]}
    lines = ["roles and rights on the SCADA (teaching; least privilege)",
             "  role                     " + "".join(f"{f:>9s}" for f in funcs)]
    for r, v in roles_.items():
        lines.append(f"  {r:25s}" + "".join(f"{'x' if x else '-':>9s}" for x in v))
    lines += ["  each person gets the smallest set of rights the job needs;",
              "  changing settings and loading software stay with named",
              "  engineers under management of change, and remote vendor",
              "  access is view-only unless a permit says otherwise (ch 36)"]
    emit("c_roles", lines)


def acceptance() -> None:
    hw, net_sample = 300, 0.10
    net = 22_000
    rows = [(f"point-to-point, all {hw} hard-wired points", "field to HMI and back"),
            (f"network points, {net * net_sample:,.0f} of {net:,} by sample", "mapping, scaling"),
            ("time alignment, events on two IEDs", "clocks agree"),
            ("alarms: raise, clear, priority", "the alarm philosophy"),
            ("failover: fibre pulled, server stopped", "recovery, buffers"),
            ("data quality: stale, bad, substituted", "flags survive")]
    lines = ["acceptance of the SCADA (teaching counts)",
             "  test                                        what it proves"]
    for a, b in rows:
        lines.append(f"  {a:43s} {b}")
    lines += ["  every result is kept with the configuration fingerprint",
              "  and the test plan of IEC 62381 (STD-148): factory test,",
              "  site test, then the integration test with the grid",
              "  operator's control centre"]
    emit("c_acceptance", lines)


if __name__ == "__main__":
    diagrams()
    chatter()
    buffers()
    retention()
    failover()
    roles()
    acceptance()
