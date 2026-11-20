"""Chapter 40, lesson A (production system) and its stages: the bill of
materials exploded for ten skids, the route with hours, yields and rework,
takt and line balance with the frame-welding bottleneck, the learning
curve of the first skids, competency coverage, the test uncertainty ratio
of the torque wrench, traceability levels, and make/buy for the frames.

Run from the project root:   python -m companion.ch40.examples_a
Writes companion/ch40/expected/a_*.txt and diagrams/data/ch40-*.csv.
Teaching values (A-434, A-435); a fictional integrator.
"""
from __future__ import annotations

import math

from companion.ch40 import sources as src
from companion.ch40.common import csv, emit
from plantp import quality as qa


def bom() -> None:
    n = len(src.SERIALS)
    lines = [f"bill of materials, level 1, exploded for {n} skids"]
    lines.append("  item                                     qty  make/buy  lead wk")
    for item, qty, unit, mb, source, lead in src.SKID:
        lines.append(f"  {item:40s} {qty * n:4d}  {mb:8s}  {lead:4d}")
    longest = max(src.SKID, key=lambda r: r[5])
    lines += [f"  longest lead: {longest[0]} ({longest[5]} weeks) - the",
              "  skid line cannot start before it arrives (ch 39, week 30)",
              "  each line points to a level-2 list held by its maker:",
              "  the integrator controls the interfaces, not the insides"]
    emit("a_bom", lines)


def route() -> dict[str, float]:
    hours = sum(r[3] for r in src.ROUTE)
    rework = sum((1 - r[4]) * r[5] for r in src.ROUTE)
    y = qa.rty([r[4] for r in src.ROUTE])
    lines = ["route of one skid: hours, first-pass yield, rework",
             "  op    work                                station  h    FPY"]
    for op, work, st, h, fpy, _ in src.ROUTE:
        lines.append(f"  {op}  {work:35s} {st:7s} {h:4.1f}  {fpy:.2f}")
    lines += [f"  touch hours a skid: {hours:.0f}; expected rework: "
              f"{rework:.2f} h",
              f"  rolled throughput yield: {y:.3f} - {1 - y:.0%} of skids",
              "  need rework somewhere, though no step is worse than 92 %",
              "  the FAT yield (92 %) finds the faults of earlier steps:",
              "  it measures the line, it does not make quality"]
    csv("ch40-route.csv", "k,op,hours,fpy",
        [(k + 1, r[0], r[3], r[4]) for k, r in enumerate(src.ROUTE)])
    emit("a_route", lines)
    return dict(hours=hours, rework=rework, rty=y)


def station_times(frames_bought: bool = False) -> dict[str, float]:
    times: dict[str, float] = {}
    for op, _, st, h, fpy, rw in src.ROUTE:
        if op == "OP10" and frames_bought:
            h, fpy, rw = 2.0, 0.99, 6.0          # receive and inspect a bought frame
        times[st] = times.get(st, 0.0) + h + (1 - fpy) * rw
    return times


def takt_balance() -> dict[str, float]:
    d = src.DEMAND
    t = qa.takt(d["weeks"] * d["hours_week"], d["skids"])
    lines = [f"takt: {d['skids']} skids in {d['weeks']} weeks of "
             f"{d['hours_week']:.0f} h = {t:.1f} h a skid",
             "  station load (hours a skid, rework included)"]
    out = {"takt": t}
    for label, bought in (("frames made", False), ("frames bought", True)):
        times = station_times(bought)
        lb = qa.line_balance(times)
        ok = "meets takt" if lb["cycle"] <= t else "misses takt"
        lines.append(f"  {label}: " + ", ".join(f"{s} {v:.1f}"
                                                for s, v in times.items()))
        lines.append(f"      bottleneck {lb['bottleneck']} {lb['cycle']:.2f} h"
                     f" -> {ok}; balance {lb['efficiency']:.0%}")
        out[label] = lb["cycle"]
    over = out["frames made"] - t
    lines += [f"  with frames made S1 is {over:.2f} h a skid over takt: no",
              "  margin at all, and the slow first skids (learning curve)",
              "  and any bad weld day push it further; buying frames moves",
              f"  the bottleneck to S3 (OP40) at {out['frames bought']:.2f} h",
              "  takt comes from demand, cycle time from the line: the plan",
              "  works only if every station's cycle stays under takt"]
    csv("ch40-stations.csv", "k,made,bought",
        [(k + 1, round(a, 2), round(b, 2)) for k, (a, b) in enumerate(
            zip(station_times(False).values(), station_times(True).values()))])
    emit("a_takt", lines)
    return out


# [start: learning]
def unit_hours(first: float, n: int, rate: float = 0.85,
               floor: float = 0.0) -> float:
    """Hours of the n-th unit on a learning curve: each doubling of
    output multiplies the hours by `rate`, down to the standard time."""
    return max(first * n ** math.log2(rate), floor)
# [end: learning]


def learning() -> None:
    first = 125.0                                  # pilot skid S-01 (A-435)
    std = sum(r[3] for r in src.ROUTE)
    lines = ["learning curve of the first skids (85 %, first skid 125 h,",
             f"down to the standard {std:.0f} h of the route)", "  skid   hours"]
    rows = []
    total = 0.0
    for n in range(1, 11):
        h = unit_hours(first, n, floor=std)
        total += h
        rows.append((n, round(h, 1)))
        lines.append(f"  S-{n:02d}  {h:6.1f}")
    lines += [f"  ten skids: {total:.0f} h against {10 * std:.0f} h at the "
              f"standard {std:.0f} h ({total - 10 * std:.0f} h more)",
              "  the first skids are slow because people, jigs and work",
              "  instructions are new; the plan books the pilot skids",
              "  apart and does not set takt from the first unit"]
    csv("ch40-learning.csv", "n,hours", rows)
    emit("a_learning", lines)


# [start: competency]
SKILLS = {  # operation: people qualified (A-435)
    "OP10": ["W1", "W2", "W3"], "OP40": ["E1", "E2", "E4"],
    "OP50": ["J1"], "OP60": ["E2", "E3", "E4"], "OP70": ["E1", "E3"],
    "OP80": ["T1", "T2"],
}
# [end: competency]


def competency() -> None:
    lines = ["competency coverage (at least two qualified people an op)"]
    single = []
    for op, people in SKILLS.items():
        flag = "" if len(people) >= 2 else "  <- single point"
        if not flag == "":
            single.append(op)
        lines.append(f"  {op}  {len(people)}  {', '.join(people)}{flag}")
    lines += [f"  single points: {', '.join(single)} - the MV termination",
              "  rests on one certified jointer; leave, illness or a",
              "  second shift stops the line at OP50",
              "  fix: a second jointer certified by the termination-kit",
              "  maker before serial production (a hold in the ITP)"]
    emit("a_competency", lines)


def calibration() -> None:
    tol, u_wrench = 7.0, 0.04 * 70.0           # +/- 10 % spec, +/- 4 % wrench
    r = qa.tur(tol, u_wrench)
    lo, hi = 70 - tol + u_wrench, 70 + tol - u_wrench
    lines = ["calibration and the test uncertainty ratio (TUR)",
             f"  joint torque spec 70 +/- {tol:.0f} N m; wrench "
             f"+/- {u_wrench:.1f} N m (95 %)",
             f"  TUR = {tol:.1f} / {u_wrench:.1f} = {r:.1f}  (a common aim"
             " is 4 or more)",
             f"  guard-banded acceptance: {lo:.1f} to {hi:.1f} N m",
             "  a better wrench (+/- 1 %) gives TUR "
             f"{qa.tur(tol, 0.7):.0f} and the full band",
             "  calibration says the tool was right on the day of its",
             "  check; the daily check on an analyser says it still is"]
    emit("a_calibration", lines)


def traceability() -> None:
    rows = [("serial", "transformer, inverter, RMU, panel", 4),
            ("lot", "lugs, fasteners, busbar copper", 3),
            ("batch", "paint, sealant", 2),
            ("tool and person", "torque wrench, crimp die, jointer", 3),
            ("record", "traveler, test dossier, concessions", 3)]
    n = sum(r[2] for r in rows)
    lines = ["traceability levels of one skid"]
    for lvl, what, k in rows:
        lines.append(f"  {lvl:16s} {k} links  {what}")
    lines += [f"  {n} links a skid, {10 * n} for the plant; a link that is",
              "  missing makes a recall cover every skid instead of three",
              "  (lesson C shows the query)"]
    emit("a_trace", lines)


def make_buy() -> None:
    make = dict(cost=9.5, hours=station_times(False)["S1"],
                know="welding procedures, own")
    buy = dict(cost=11.0, hours=station_times(True)["S1"],
               know="maker's, by specification")
    extra = (buy["cost"] - make["cost"]) * 10
    lines = ["make or buy the base frames (k u a frame, hours at S1)",
             f"  make: {make['cost']:.1f} k u, {make['hours']:.2f} h; "
             f"{make['know']}",
             f"  buy:  {buy['cost']:.1f} k u, {buy['hours']:.2f} h; "
             f"{buy['know']}",
             f"  buying costs {extra:.0f} k u more for ten frames and frees",
             "  the bottleneck; the integrator keeps the frame drawing,",
             "  the weld inspection plan and a first-article inspection",
             "  so design ownership stays where it was (ch 39)"]
    emit("a_makebuy", lines)


if __name__ == "__main__":
    bom()
    route()
    takt_balance()
    learning()
    competency()
    calibration()
    traceability()
    make_buy()
