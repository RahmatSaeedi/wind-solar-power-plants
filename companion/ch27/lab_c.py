"""Chapter 27, lab C - the investigation workflow for a power-quality
complaint: the steps and their records, what the sign of a 'harmonic
power' can and cannot say, the measurement plan, and the time quality of
the records.

Run from the project root:   python -m companion.ch27.lab_c
Writes companion/ch27/expected/c_*.txt. The complaint is fictional
(A-338).
"""
from __future__ import annotations

import math

from companion.ch27.common import emit


def workflow() -> None:
    steps = [("1 define the symptom", "neighbour's capacitor fuses blow in the evening",
              "complaint record, dates, equipment"),
             ("2 measurement location", "POC, the neighbour's bus, plant 33 kV bus",
              "single-line with transducers"),
             ("3 time quality", "all instruments on one clock source",
              "time-sync record, clock offsets"),
             ("4 separate source from symptom", "same hours with plant on and off",
              "on/off comparison, currents"),
             ("5 compare with a baseline", "before the plant, or a similar bus",
              "baseline data set"),
             ("6 corrective action", "filter, settings, or not the plant",
              "before/after with acceptance")]
    lines = ["investigation of a power-quality complaint (fictional, A-338):"]
    for a, b, c in steps:
        lines += [f"  {a}: {b}", f"      record: {c}"]
    lines += ["  each step ends in a record; a conclusion that skips step 4",
              "  blames whatever was connected last"]
    emit("c_workflow", lines)


def direction() -> None:
    lines = ["sign of the 5th-harmonic power P5 = V5 I5 cos(theta) under a",
             "  +/- 10 deg phase error of the transducers at the 5th (teaching):",
             "  true theta deg   P5 sign   sign with errors   conclusive?"]
    for th in (30, 60, 80, 88, 95):
        lo, hi = math.cos(math.radians(th - 10)), math.cos(math.radians(th + 10))
        signs = {math.copysign(1, lo), math.copysign(1, hi)}
        true = "+" if math.cos(math.radians(th)) > 0 else "-"
        both = "+ or -" if len(signs) > 1 else true
        lines.append(f"  {th:14d}   {true:>7s}   {both:>16s}   {'yes' if len(signs) == 1 else 'NO':>11s}")
    lines += ["  near 90 degrees a small phase error flips the sign: the",
              "  'direction of harmonic power' points the finger only when",
              "  the angle is far from 90 degrees and the transducers are",
              "  known at the 5th; otherwise it is one clue among several,",
              "  never the verdict"]
    emit("c_direction", lines)


def plan() -> None:
    rows = [("POC 132 kV", "V harmonics, flicker, unbalance", "inductive VT or divider", "4 weeks"),
            ("POC 132 kV", "I harmonics, P, Q", "metering CT core", "4 weeks"),
            ("33 kV bus A and B", "V and I harmonics", "VT, CT", "4 weeks"),
            ("one PV and one wind unit", "I harmonics vs power", "unit transducers", "2 weeks"),
            ("neighbour's bus", "V harmonics", "their VT, agreed", "4 weeks")]
    lines = ["measurement plan for the investigation (teaching):"]
    for a, b, c, d in rows:
        lines += [f"  {a}: {b}", f"      through {c}, for {d}"]
    lines += ["  class A instruments on the method of STD-034, one time",
              "  source, 10-minute aggregation, plant output and switching",
              "  log recorded alongside; the plan is agreed with the",
              "  operator and the neighbour before the first reading"]
    emit("c_plan", lines)


if __name__ == "__main__":
    workflow()
    direction()
    plan()
