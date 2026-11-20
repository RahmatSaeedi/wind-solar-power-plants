"""Chapter 35, lesson F: the boundary between real-time data and the
asset and maintenance systems (CMMS/EAM) - asset IDs that disagree, the
source of truth of each item, governed flows, alarms turned into work
requests without duplicates, time in UTC against local time, a queue
when the interface is down, and the interface acceptance.

Run from the project root:   python -m companion.ch35.examples_f
Writes companion/ch35/expected/f_*.txt.
Synthetic data and teaching values (A-399); nothing connects to a plant.
"""
from __future__ import annotations

import numpy as np

from companion.ch35 import sources as src
from companion.ch35.common import emit
from plantp import scada as sc


def id_check() -> None:
    lines = ["asset register against SCADA tag prefixes (synthetic extract)",
             "  asset ID            SCADA prefix        result"]
    issues = 0
    for aid, desc, tag in src.ASSETS:
        if tag is None:
            res = "NO SCADA POINTS"
        elif tag != aid:
            res = "ID MISMATCH"
        else:
            res = "ok"
        issues += res != "ok"
        lines.append(f"  {aid:19s} {tag or '-':19s} {res}")
    lines += [f"  {issues} of {len(src.ASSETS)} assets do not line up",
              "  'C1' against 'C01' breaks every automatic link: the",
              "  battery's alarms never reach its work orders, and its",
              "  running hours never reach its maintenance plan; T2 has",
              "  no points at all - a missing interface, not a typo. The",
              "  asset ID is set once, in the register, and copied, never",
              "  retyped"]
    emit("f_ids", lines)


def truth() -> None:
    rows = [("asset identity and attributes", "asset register (EAM)", "asset engineer"),
            ("measurements and states", "SCADA / historian", "control engineer"),
            ("topology (what feeds what)", "one-line (ch 23)", "electrical lead"),
            ("work orders and history", "CMMS", "maintenance lead"),
            ("settings and configurations", "settings register", "protection/control")]
    lines = ["source of truth of each kind of data (teaching)",
             "  data                           authoritative source     owner"]
    for d, s, o in rows:
        lines.append(f"  {d:30s} {s:24s} {o}")
    lines += ["  every other copy is a copy: it is refreshed from the",
              "  source, carries the source's time stamp, and is never",
              "  edited where it is read"]
    emit("f_truth", lines)


def flows() -> None:
    rows = [("historian aggregates -> reports", "daily", "read only"),
            ("alarms -> CMMS work requests", "on event, deduplicated", "one way"),
            ("running hours, cycles -> CMMS", "daily", "one way"),
            ("asset register -> SCADA tag list", "on change, reviewed", "one way"),
            ("CMMS -> SCADA control", "never", "no path")]
    lines = ["governed data flows across the boundary (teaching)",
             "  flow                                  update                   direction"]
    for f, u, d in rows:
        lines.append(f"  {f:37s} {u:24s} {d}")
    lines += ["  business systems read from the control side and never",
              "  write into it; the one flow into SCADA - tag names from",
              "  the register - passes a review, not an automatic sync"]
    emit("f_flows", lines)


def dedup(seed: int = 352) -> None:      # same hour as lesson C
    rng = np.random.default_rng(seed)
    t = np.arange(0, 3600)
    temp = 79.0 + 1.5 * np.sin(2 * np.pi * t / 1800) + rng.normal(0, 0.6, t.size)
    raw = sc.transitions(sc.alarm_states(temp, 80.0, 0.0, 1))
    lines = ["alarms turned into work requests (synthetic hour of ch 35 lesson C)",
             f"  one work request per alarm: {raw} requests in an hour",
             "  one open request per asset and alarm type, updated while",
             "  open: 1 request",
             "  a maintenance system flooded by chattering alarms is",
             "  ignored like an alarm list; the rule lives in the",
             "  interface specification and is tested with a chattering",
             "  series"]
    emit("f_dedup", lines)


def utc() -> None:
    lines = ["time in UTC or local time: the day the clocks go back (teaching)",
             "  local-time day with a repeated hour: 25 hours of data",
             "  a daily report summing local hours: 25/24 = 4.2 % more energy",
             "    that day, and two values for every minute of one hour",
             "  stored in UTC and shown in local time: 25 distinct hours,",
             "  each once",
             "  every interface states its time base and every value",
             "  carries it; reports convert at the edge, never in storage"]
    emit("f_utc", lines)


def queue() -> None:
    per_hour, hours, size_kb = 40, 72, 2
    lines = ["the CMMS interface is down for three days: the queue (teaching)",
             f"  {per_hour} messages an hour x {hours} h = {per_hour * hours:,} messages,"
             f" {per_hour * hours * size_kb / 1024:.1f} MB",
             "  the sender queues and replays in order when the link",
             "  returns; each message has an ID so a replayed one is",
             "  recognised and not booked twice - and the queue's age is",
             "  an alarm, so three days of silence are noticed in hours"]
    emit("f_queue", lines)


def acceptance() -> None:
    rows = [("every asset with points has a matching ID", "register vs tag list"),
            ("a test alarm creates one request, not many", "chattering series"),
            ("running hours arrive and add up", "known counter steps"),
            ("a dropped link queues and replays once", "link pulled for 1 h"),
            ("times arrive in UTC with their source", "DST change in test data"),
            ("no write path into SCADA exists", "network and rights check")]
    lines = ["acceptance of the SCADA - CMMS/EAM interface (teaching)",
             "  test                                          with"]
    for a, b in rows:
        lines.append(f"  {a:45s} {b}")
    lines += ["  the interface has an owner on each side and a written",
              "  specification; its tests run on a test copy with",
              "  synthetic data before production data flows"]
    emit("f_accept", lines)


if __name__ == "__main__":
    id_check()
    truth()
    flows()
    dedup()
    utc()
    queue()
    acceptance()
