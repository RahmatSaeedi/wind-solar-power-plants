"""Chapter 35, another round: ring recovery and what each function loses,
condition-monitoring files on the turbine ring, heartbeat detection on the
fire-alarm link, integer scaling in a gateway, the quality of a plant
total, the length of point-to-point checks, loss-of-comms behaviour at the
PPC, report queries on raw and aggregated data, and interoperability tests
with and without a profile.

Run from the project root:   python -m companion.ch35.examples_s
Writes companion/ch35/expected/s_*.txt and diagrams/data/ch35-*.csv.
Synthetic data and teaching values (A-393 to A-400); no live system.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch35.common import csv, emit


def ring_recovery() -> None:
    funcs = [("protection messages (fast)", 1000.0, 0.004),   # msgs/s, tolerable gap s
             ("telecontrol to the PPC", 10.0, 1.0),
             ("historian samples", 100.0, 60.0)]
    lines = ["what a ring break costs while the ring heals (teaching rates)",
             "  recovery time        messages lost: protection   telecontrol   historian"]
    for t in (0.02, 0.2, 2.0):
        lost = [f"{rate * t:8.0f}" for _, rate, _ in funcs]
        lines.append(f"  {t * 1000:9.0f} ms        {lost[0]:>16}   {lost[1]:>11}   {lost[2]:>9}")
    lines += ["  tolerable gap: protection 4 ms, telecontrol 1 s, historian",
              "    60 s (buffered)",
              "  no ring recovery is fast enough for protection messages,",
              "  which therefore run on paths that need no recovery",
              "  (duplicated, both sent at once - ch 34, ch 35 lesson A);",
              "  telecontrol rides through a 200 ms heal, not a 2 s one;",
              "  the historian rides through all of them from its buffer"]
    emit("s_ring", lines)


def cms_files() -> None:
    link = 100e6                                   # bit/s ring
    turbines = 12
    live = 2_000 * 8 * turbines                    # 2 kB/s of 1 s data each
    file_bits = 50e6 * 8                           # one 50 MB vibration file a turbine
    at_once = turbines * file_bits
    lines = ["condition-monitoring files on the 100 Mbit/s turbine ring",
             f"  live data of 12 turbines: {live / 1e6:.2f} Mbit/s"
             f" ({live / link * 100:.1f} % of the ring)"]
    for name, share in (("all 12 files at once, 60 % of the ring", 0.6),
                        ("one file at a time, 20 % of the ring", 0.2)):
        t = at_once / (link * share)
        lines.append(f"  {name:40s} {t / 60:5.1f} min")
    lines += ["  either way the live data keeps its share if the files go",
              "  in a lower priority class (lesson P, priority); without",
              "  priorities, 12 files at once fill the ring and the 1 s",
              "  telemetry queues behind them. Bulk files are scheduled",
              "  at night and limited in rate - a setting written in the",
              "  network design, not left to the maker's default"]
    emit("s_cms", lines)


def heartbeat() -> None:
    p_loss = 1e-3                                   # one message in a thousand lost
    lines = ["loss of the fire-alarm link found by a heartbeat (teaching)",
             "  period s   missed   detection s   false 'link lost' a year"]
    for period, missed in ((10, 1), (10, 3), (2, 3), (2, 5)):
        det = period * missed
        per_year = 365 * 86400 / period
        false = per_year * p_loss ** missed
        lines.append(f"  {period:8d}   {missed:6d}   {det:11d}   {false:24.3g}")
    lines += ["  with one loss in a thousand, declaring the link lost on a",
              "  single missed heartbeat gives thousands of false alarms a",
              "  year; three in a row gives almost none and still finds a",
              "  real break in 6-30 s. The fire panel keeps its own alarms",
              "  and authority either way; SCADA only shows that its view",
              "  of the panel is lost (lesson E)"]
    emit("s_heartbeat", lines)


def int16_scaling() -> None:
    sigs = [("active power", "MW", 0.01, -20.0, 110.0),
            ("reactive power", "Mvar", 0.01, -60.0, 60.0),
            ("frequency", "Hz", 0.001, 47.0, 53.0),
            ("voltage at POC", "kV", 0.001, 110.0, 150.0),
            ("energy today", "MWh", 0.1, 0.0, 2_400.0)]
    lines = ["signed 16-bit registers in a gateway: scale against range (teaching)",
             "  signal           unit   scale    largest value   fits?   step"]
    bad = []
    for name, unit, scale, lo, hi in sigs:
        top = 32767 * scale
        ok = lo >= -32768 * scale and hi <= top
        if not ok:
            bad.append(f"{name} at {scale:g} {unit}")
        lines.append(f"  {name:15s}  {unit:5s} {scale:6.3f}   {top:13.2f}   {'yes' if ok else 'NO':5s}"
                     f"   {scale:g} {unit}")
    lines += [f"  {bad[0]} and {bad[1]} do not fit:",
              "  50.000 Hz would wrap to a negative number. The fix is a",
              "  scale that fits (0.01 Hz, 0.1 kV), an offset agreed by",
              "  both ends, or a 32-bit value - and the choice is written",
              "  in the interface list, with a test value at each end of",
              "  the range in the acceptance test (lesson B, registers)"]
    emit("s_int16", lines)


def plant_quality() -> None:
    mw = np.array([4.1, 4.3, 3.9, 4.0, 4.2, 4.4, 3.8, 4.1, 4.0, 4.2, 4.3, 3.9])
    good = np.ones(12, bool)
    good[[4, 9]] = False                            # two turbines' values invalid
    total_known = mw[good].sum()
    est_sub = total_known + 2 * mw[good].mean()     # substitute the mean of the others
    true_total = mw.sum()
    lines = ["plant wind total when 2 of 12 turbine values are invalid",
             f"  sum of the 10 good values:            {total_known:6.1f} MW  quality BAD",
             f"  with the 2 replaced by the mean of 10: {est_sub:6.1f} MW  quality"
             " SUBSTITUTED",
             f"  true total (known here, synthetic):   {true_total:6.1f} MW",
             f"  a total that silently drops two turbines is {(1 - total_known / true_total) * 100:.0f} % low and",
             f"  looks good; a substituted total is within {abs(true_total - est_sub):.1f} MW and says",
             "  so. The rule - substitute or flag, and which quality the",
             "  total carries - is part of the data model, written once",
             "  and used by the HMI, the historian and the PPC alike"]
    emit("s_quality", lines)


def sat_duration() -> None:
    points, minutes, teams = 3_200, 4.0, 2
    fail = 0.08
    first = points * minutes / 60 / teams / 8          # 8-hour days
    retest = points * fail * (minutes + 10) / 60 / teams / 8
    lines = ["point-to-point checks of 3,200 points at site acceptance (teaching)",
             f"  {minutes:.0f} min a point, {teams} teams of two, 8-hour days:"
             f" {first:.1f} days",
             f"  {fail * 100:.0f} % fail, found, fixed and retested at 14 min each:"
             f" {retest:.1f} days",
             f"  total {first + retest:.1f} days on site, plus waiting for fixes",
             "  the factory test (lesson P) already checked the logic; at",
             "  site each point is checked from its terminal to the",
             "  operator's display and to the grid operator, with the",
             "  test values and results recorded per point"]
    emit("s_sat", lines)


def loss_of_comms() -> None:
    hold_s, ramp = 60.0, 0.5                        # MW per second asked by the operator
    lines = ["the grid operator's set point is ramping down at 0.5 MW/s when",
             "  the link fails (teaching values)",
             "  behaviour of the PPC          deviation after 60 s   after 5 min"]
    for name, mode in (("hold the last set point", "hold"),
                       ("hold 60 s, then fall back to the schedule", "fallback"),
                       ("go to zero output", "zero")):
        def dev(t):
            asked = 80.0 - ramp * min(t, 80.0)         # the ramp ends at 40 MW
            asked = max(asked, 40.0)
            if mode == "hold":
                got = 80.0
            elif mode == "zero":
                got = 0.0
            else:
                got = 80.0 if t <= hold_s else 60.0    # schedule value (teaching)
            return got - asked
        lines.append(f"  {name:40s} {dev(60):+8.1f} MW   {dev(300):+8.1f} MW")
    lines += ["  no behaviour is right for every case: holding keeps the",
              "  plant steady but misses the ramp, zero output is safe for",
              "  the plant and a large disturbance for the grid. The",
              "  behaviour and its timers are agreed with the grid",
              "  operator (U-115) and tested at acceptance (ch 20, ch 34)"]
    emit("s_comms", lines)


def report_queries() -> None:
    tags, days = 500, 31
    raw = tags * days * 86400                      # 1 s raw values
    agg = tags * days * 144                        # 10-minute aggregates
    lines = ["rows read for one monthly report of 500 tags",
             f"  from 1-second raw data:      {raw:,.0f} rows",
             f"  from 10-minute aggregates:   {agg:,.0f} rows",
             f"  the aggregates read {raw / agg:.0f} times fewer rows; reports and",
             "  dashboards read aggregates made by the historian, and",
             "  raw data is read only for an event investigation. The",
             "  aggregates keep min, max, mean and a quality count, so",
             "  nothing the report needs is lost (lesson M, trend)"]
    emit("s_queries", lines)


def interop(vendors: int = 6, functions: int = 12) -> None:
    pairwise = vendors * (vendors - 1) // 2 * functions
    profile = vendors * functions
    lines = [f"interoperability tests for {vendors} device makers and {functions} functions",
             f"  every pair of makers tested together: {pairwise} test cases",
             f"  each maker tested once against an agreed profile: {profile}",
             "  the protocol's name says how bytes travel, not which data",
             "  objects, options and timings a device uses; a profile",
             "  fixes those choices, each device is tested against it,",
             "  and a short integration test then confirms the plant -",
             "  instead of testing every pair (lesson B, profiles)"]
    emit("s_interop", lines)
    rows = [(n, n * (n - 1) // 2 * functions, n * functions) for n in range(2, 11)]
    csv("ch35-interop.csv", "n,pair,profile", rows)


def event_order() -> None:
    gaps_ms = (0.5, 1.0, 2.0, 5.0, 10.0)
    clocks = (("NTP, WAN", 1.0), ("NTP, LAN", 0.2),
              ("PTP", 0.001))                        # standard error of each clock, ms
    lines = ["chance two events from two relays are logged in the wrong order",
             "  (each clock with an independent normal error; teaching values)",
             "  (standard error: NTP over the WAN 1 ms, in the plant LAN",
             "  0.2 ms, PTP to the relays 1 us)",
             "  true gap ms   " + "   ".join(f"{n:>9s}" for n, _ in clocks)]
    rows = []
    for g in gaps_ms:
        ps = [0.5 * math.erfc(g / (math.sqrt(2) * math.sqrt(2) * s)) for _, s in clocks]
        rows.append((g, *[round(p, 6) for p in ps]))
        lines.append(f"  {g:11.1f}   " + "   ".join(f"{p:9.4f}" for p in ps))
    csv("ch35-order.csv", "g,wan,lan,ptp", rows)
    p05, p2 = rows[0][1], rows[2][1]
    lines += ["  a breaker and the relay that tripped it act a few ms apart;",
              f"  with WAN time their order is wrong {p05 * 100:.0f} % of the time at",
              f"  0.5 ms and once in {1 / p2:.0f} at 2 ms; with PTP it is never wrong.",
              "  The sequence of events that a fault investigation needs",
              "  is a design requirement on the time chain (lesson A)"]
    emit("s_order", lines)


def poll_drift() -> None:
    ppm = 20.0                                       # quartz drift of a device clock
    lines = ["a device clock that drifts 20 ppm, corrected at each time poll",
             "  poll every   largest error just before the poll"]
    for every in (16, 64, 1024, 3600):
        err_ms = ppm * 1e-6 * every * 1000
        lines.append(f"  {every:6d} s    {err_ms:10.2f} ms")
    lines += ["  the error between polls grows with the interval; a",
              "  device that time-stamps its own events needs a poll short",
              "  enough for its accuracy class, and its holdover (lesson",
              "  N) covers the time server's loss, not the poll gap"]
    emit("s_poll", lines)


def latency_percentiles(seed: int = 355) -> None:
    rng = np.random.default_rng(seed)
    base = 40.0 + rng.gamma(2.0, 10.0, 10_000)       # ms, round trip (synthetic)
    burst = rng.random(10_000) < 0.02                # 2 % meet a file transfer
    rt = np.where(burst, base + rng.uniform(100, 400, 10_000), base)
    mean, p95, p99 = rt.mean(), np.percentile(rt, 95), np.percentile(rt, 99)
    lines = ["10,000 round trips of a set point to the PPC and back (synthetic)",
             f"  mean {mean:.0f} ms   95th percentile {p95:.0f} ms"
             f"   99th percentile {p99:.0f} ms",
             f"  a requirement of 'under 200 ms' is met on average and by"
             f" {np.mean(rt < 200) * 100:.1f} %",
             "    of the round trips",
             "  the rare slow trips come from queues behind bulk traffic;",
             "  a latency requirement names its percentile and its",
             "  window, and the acceptance test measures that percentile",
             "  over enough trips to see the tail (lesson A, latency)"]
    emit("s_latency", lines)


if __name__ == "__main__":
    event_order()
    poll_drift()
    latency_percentiles()
    ring_recovery()
    cms_files()
    heartbeat()
    int16_scaling()
    plant_quality()
    sat_duration()
    loss_of_comms()
    report_queries()
    interop()
