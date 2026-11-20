"""Chapter 50, lesson C (defect closure and handover): the commissioning
punch list burned down, deviations and who accepts them, training by
role, spares received.

Run from the project root:   python -m companion.ch50.examples_c
Writes companion/ch50/expected/c_*.txt and diagrams/data/ch50-punch.csv.
"""
from __future__ import annotations

from companion.ch50 import sources as src
from companion.ch50.common import csv, emit


def punch(target_week: int = 18) -> dict:
    open_ = src.PUNCH_OPEN_START
    rows = []
    for w, (o, c) in src.PUNCH50.items():
        open_ += o - c
        rows.append((w, o, c, open_))
    csv("ch50-punch.csv", "week,opened,closed,open", rows)
    net = [c - o for _, o, c, _ in rows[-3:]]
    rate = sum(net) / len(net)
    last_w = rows[-1][0]
    weeks = open_ / rate if rate > 0 else float("inf")
    lines = ["commissioning punch list by week (opened, closed, still open)",
             "  week  opened  closed  open"]
    lines += [f"  {w:4d}  {o:6d}  {c:6d}  {n:4d}" for w, o, c, n in rows]
    lines += [f"  net closing over the last three weeks {rate:.1f} a week: the list",
              f"  empties in about {weeks:.1f} weeks, week {last_w + weeks:.0f} against the "
              f"target week {target_week}",
              "  new items are still being found (testing finds them); the",
              "  list closes when finding slows - the net rate, not the",
              "  closing rate, is the one that forecasts"]
    emit("c_punch", lines)
    return dict(open=open_, rate=rate, week=last_w + weeks)


def deviations() -> list:
    lines = ["deviations: what was accepted, by whom, on what condition"]
    for d, item, ok, cond in src.DEVIATIONS:
        st = {True: "accepted", False: "rejected", None: "open"}[ok]
        lines.append(f"  {d}: {item}")
        lines.append(f"    {st}; {cond}")
    lines += ["  a deviation is a recorded decision, not a forgotten defect:",
              "  DEV-11 belongs to the network operator (the POC is theirs),",
              "  DEV-14 is rejected and becomes a punch item with a date"]
    emit("c_dev", lines)
    return [d for d, _, ok, _ in src.DEVIATIONS if ok is not True]


def training() -> dict:
    rows = [(r, n, t, a) for r, (n, t, a) in src.TRAINING.items()]
    short = [(r, n - a) for r, n, t, a in rows if a < n]
    lines = ["training by role: people needed, trained, assessed competent",
             "  role                         need  trained  assessed"]
    lines += [f"  {r:28s} {n:4d}  {t:7d}  {a:8d}" for r, n, t, a in rows]
    lines += ["  short of assessed people:"]
    lines += [f"    {r}: {k}" for r, k in short]
    lines += ["  attendance is not competence: a role is staffed by people",
              "  assessed in it, and an authorised person is appointed in",
              "  writing (lesson A) - the wind technicians are the largest gap"]
    emit("c_training", lines)
    return dict(short=short)


def spares() -> list:
    short = [(k, n - r) for k, (n, r) in src.SPARES.items() if r < n]
    lines = ["commissioning and first-year spares: listed against received"]
    lines += [f"  {k:24s} {n:4d} listed, {r:4d} received" for k, (n, r) in src.SPARES.items()]
    lines += ["  short:"]
    lines += [f"    {k}: {m}" for k, m in short]
    lines += ["  the UPS battery string is the one DEV-14 needs; spares are",
              "  part of handover and of the asset records (ch 18 spares,",
              "  ch 49 K)"]
    emit("c_spares", lines)
    return short


if __name__ == "__main__":
    punch()
    deviations()
    training()
    spares()
