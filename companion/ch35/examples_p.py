"""Chapter 35, third deeper round: control traffic with and without
priority behind a back-fill burst, one or two carriers for the grid
operator's link, data completeness over the whole tag list, the priority
mix of an alarm list and the operator's time in a flood, a message queue
replayed with and without message IDs, historian compression by a
swinging door, a SCADA server switchover, and the factory test of the
network.

Run from the project root:   python -m companion.ch35.examples_p
Writes companion/ch35/expected/p_*.txt.
Teaching values and synthetic data (A-393 to A-400).
"""
from __future__ import annotations

import numpy as np

from companion.ch35.common import emit


def priority() -> None:
    frame_ms, burst = 0.12, 1000                  # 1,500-byte frames at 100 Mbit/s
    lines = ["a control message behind a back-fill burst of 1,000 frames",
             f"  one queue for all: it waits up to {burst * frame_ms:.0f} ms",
             f"  control traffic in a higher priority queue: at most one"
             f" frame, {frame_ms:.2f} ms",
             "  the switch ports carry priority classes: protection and",
             "  control first, SCADA next, back-fill and file transfer",
             "  last; a burst then fills the spare capacity, not the time",
             "  budget of the control loop (ch 34)"]
    emit("p_priority", lines)


def carriers() -> None:
    a = 0.995                                     # one carrier's link, teaching
    beta = 0.10                                   # share of outages in a shared duct
    single = (1 - a) * 8760
    indep = (1 - a) ** 2 * 8760
    shared = (beta * (1 - a) + (1 - a) ** 2) * 8760
    lines = ["telemetry link to the grid operator: one or two carriers",
             f"  one carrier at {a}: {single:.1f} h a year without telemetry",
             f"  two independent carriers: {indep:.2f} h a year",
             f"  two carriers in one duct for the last km (10 % shared):"
             f" {shared:.1f} h",
             "  a second carrier helps only if its route is different;",
             "  the routes are drawn on the physical diagram and the",
             "  grid operator's own requirement for redundancy decides",
             "  (U-115)"]
    emit("p_carriers", lines)


def completeness(seed: int = 358) -> None:
    rng = np.random.default_rng(seed)
    n = 22_300
    gaps_h = rng.exponential(1.5, n) * (rng.random(n) < 0.6)     # hours lost in a month
    gaps_h[rng.choice(n, 120, replace=False)] += rng.uniform(24, 200, 120)  # dead devices
    comp = 1 - gaps_h / (30 * 24)
    lines = ["data completeness of every tag over a month (synthetic)",
             f"  median completeness {np.median(comp) * 100:.2f} %",
             f"  tags below 99 %: {int(np.sum(comp < 0.99)):,}",
             f"  tags below 90 %: {int(np.sum(comp < 0.90)):,}",
             "  a plant-wide average hides the few tags that are nearly",
             "  empty - the dead devices; completeness is reported per",
             "  tag and per device, and the worst list goes to",
             "  maintenance every week (ch 37 uses it to judge data)"]
    emit("p_complete", lines)


def alarm_mix() -> None:
    draft = {"high": 800, "medium": 700, "low": 500}
    rational = {"high": 120, "medium": 380, "low": 1100}
    seconds = 30                                   # operator's time per alarm (teaching)
    lines = ["the priority mix of the alarm list, before and after review",
             "  priority   draft   reviewed"]
    for k in draft:
        lines.append(f"  {k:8s} {draft[k]:7d}   {rational[k]:8d}")
    lines += [f"  draft: {draft['high'] / sum(draft.values()) * 100:.0f} % high; reviewed:"
              f" {rational['high'] / sum(rational.values()) * 100:.0f} % high",
              f"  operator's time for the flood of 151 alarms at {seconds} s each:"
              f" {151 * seconds / 60:.0f} min",
              f"    for the 13 left after suppression: {13 * seconds / 60:.1f} min",
              "  when most alarms are 'high', priority tells the operator",
              "  nothing; the review gives each alarm a consequence and a",
              "  time to act, from which its priority follows (teaching",
              "  targets are set in the alarm philosophy, not here)"]
    emit("p_mix", lines)


def replay(seed: int = 359) -> None:
    rng = np.random.default_rng(seed)
    sent = 2880
    acked = rng.random(sent) < 0.97                # 3 % of acknowledgements lost
    resent = int(np.sum(~acked))
    lines = ["a queue replayed after a 3-day outage (synthetic)",
             f"  messages queued: {sent:,}; acknowledgements lost: {resent}",
             f"  without message IDs: {resent} work requests booked twice",
             "  with message IDs: 0 - the receiver recognises the repeat",
             "  and acknowledges it again without booking it",
             "  'at least once' delivery needs an idempotent receiver;",
             "  the ID is set at the source and never changes on the way"]
    emit("p_replay", lines)


def swinging_door(seed: int = 360) -> None:
    rng = np.random.default_rng(seed)
    t = np.arange(3600.0)
    x = 70.0 + 5.0 * np.sin(2 * np.pi * t / 3600) + rng.normal(0, 0.05, t.size)
    lines = ["historian compression of a slowly moving signal (synthetic hour)",
             "  method                        stored points   largest error K"]
    for dev in (0.1, 0.3, 0.7):
        # deadband: store when the value moves by dev from the last stored
        kept_db, last = [0], x[0]
        for i in range(1, len(x)):
            if abs(x[i] - last) > dev:
                kept_db.append(i)
                last = x[i]
        rec = np.interp(t, t[kept_db], x[kept_db])
        e_db = np.max(np.abs(rec - x))
        # straight-line (swinging-door family) compression: keep a segment
        # while one line from the last stored point stays within +/- dev
        # of every point since; store the end of that line, not the raw value
        kt, kv = [0.0], [x[0]]
        a_t, a_v = 0.0, x[0]
        up, lo = np.inf, -np.inf
        for i in range(1, len(x)):
            dt = t[i] - a_t
            nu = min(up, (x[i] + dev - a_v) / dt)
            nl = max(lo, (x[i] - dev - a_v) / dt)
            if nl > nu:                              # no line fits: close at i - 1
                s = (up + lo) / 2
                a_v = a_v + s * (t[i - 1] - a_t)
                a_t = t[i - 1]
                kt.append(a_t)
                kv.append(a_v)
                dt = t[i] - a_t
                up, lo = (x[i] + dev - a_v) / dt, (x[i] - dev - a_v) / dt
            else:
                up, lo = nu, nl
        kt.append(t[-1])
        kv.append(a_v + (up + lo) / 2 * (t[-1] - a_t))
        rec2 = np.interp(t, kt, kv)
        e_sd = np.max(np.abs(rec2 - x))
        kept = kt
        lines.append(f"  deadband {dev:.1f} K (as stored)     {len(kept_db):13d}   {e_db:15.2f}")
        lines.append(f"  swinging door {dev:.1f} K           {len(kept):13d}   {e_sd:15.2f}")
    lines += ["  the door keeps the points where the trend bends and draws",
              "  straight lines between them, and its error never leaves",
              "  the band it is given; a deadband read back with straight",
              "  lines can miss by half again its setting (1.03 K for",
              "  0.7 K). Method and setting are chosen together from the",
              "  instrument's uncertainty and recorded with the tag"]
    emit("p_door", lines)


def switchover() -> None:
    detect_s, takeover_s = 3.0, 2.0
    gap = detect_s + takeover_s
    lines = ["the main SCADA server fails: the standby takes over (teaching)",
             f"  failure detected after {detect_s:.0f} s, take-over {takeover_s:.0f} s:"
             f" {gap:.0f} s without",
             "    a live screen",
             "  data in that gap: kept in the devices' and gateways'",
             "    buffers and sent when the standby asks",
             "  commands in that gap: refused, not queued - an old",
             "    command must not run five seconds late",
             "  switch-over is tested in the site test by stopping the",
             "  main server, with a recorded event before, during and",
             "  after; the alarm list, shelving and operator logins",
             "  must come across, not only the values"]
    emit("p_switch", lines)


def network_fat() -> None:
    devices = 28
    per_device = [("firmware and configuration fingerprint", 0.25),
                  ("port settings, priority classes, address", 0.5),
                  ("time synchronisation and its alarm", 0.25)]
    system = [("ring broken at each span (14 spans)", 14 * 0.25),
              ("server switch-over", 1.0), ("back-fill rate limit", 0.5),
              ("general interrogation burst", 0.5)]
    dev_h = devices * sum(h for _, h in per_device)
    sys_h = sum(h for _, h in system)
    lines = ["factory test of the network (teaching durations)",
             "  per device (x 28):"]
    for name, h in per_device:
        lines.append(f"    {name:42s} {h:5.2f} h")
    lines.append("  whole system:")
    for name, h in system:
        lines.append(f"    {name:42s} {h:5.2f} h")
    lines += [f"  total {dev_h + sys_h:.1f} h of testing, about"
              f" {(dev_h + sys_h) / 7:.0f} working days",
              "  the network is assembled once in the factory as it will",
              "  stand on site; what is not tested there is found by the",
              "  commissioning team at the turbine base (ch 48, ch 50)"]
    emit("p_fat", lines)


if __name__ == "__main__":
    priority()
    carriers()
    completeness()
    alarm_mix()
    replay()
    swinging_door()
    switchover()
    network_fat()
