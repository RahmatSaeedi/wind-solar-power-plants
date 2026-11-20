"""Chapter 33, lesson R (assessment, deeper): the chance a raptor flying
through the rotor is struck, by radius and over the disc (simplified
single-transit model), and how large the nearest turbine looks from each
receptor (vertical angle of the blade tip).

Run from the project root:   python -m companion.ch33.examples_r
Writes companion/ch33/expected/r_*.txt and diagrams/data/ch33-transit.csv.
Teaching blade and bird values (A-378); a collision study uses the
maker's blade and the species' measured flight (U-113).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch33 import sources as src
from companion.ch33.common import csv, emit
from companion.ch14 import sources as s14
from plantp import envsocial as es

R = s14.RADIUS                      # m
BLADES, RPM = 3, 11.5               # rated rotor speed (ch 11)
BIRD = dict(length=0.6, span=1.8, speed=12.0)     # a medium raptor (teaching)


def chord(r: float) -> float:
    return 4.0 - 3.0 * (r / R - 0.2) / 0.8           # 4 m near the root, 1 m at the tip


def pitch(r: float) -> float:
    return 15.0 - 13.0 * (r / R - 0.2) / 0.8         # local blade angle, deg


def transit() -> None:
    om = RPM * 2 * math.pi / 60
    rs = np.linspace(0.2 * R, R, 41)
    p = np.array([es.transit_probability(r, chord(r), pitch(r), BLADES, om,
                                         BIRD["speed"], BIRD["length"], BIRD["span"])
                  for r in rs])
    w = 2 * rs / (R ** 2 - (0.2 * R) ** 2)           # area weight over the swept ring
    mean = float(np.trapezoid(p * w, rs))
    csv("ch33-transit.csv", "r,p", [(round(float(r), 1), round(float(x), 4))
                                    for r, x in zip(rs[::4], p[::4])])
    lines = ["chance a raptor flying through the rotor is struck (single transit)",
             f"  rotor {R:.0f} m, {BLADES} blades at {RPM} rpm; bird {BIRD['length']} m"
             f" long, {BIRD['span']} m span, {BIRD['speed']:.0f} m/s",
             "  radius m   chord m   angle deg   chance"]
    for r in (0.2 * R, 0.4 * R, 0.6 * R, 0.8 * R, R):
        pr = es.transit_probability(r, chord(r), pitch(r), BLADES, om, BIRD["speed"],
                                    BIRD["length"], BIRD["span"])
        lines.append(f"  {r:8.0f}   {chord(r):7.1f}   {pitch(r):9.1f}   {pr:6.3f}")
    lines += [f"  averaged over the swept area: {mean:.3f}",
              "  the root is the dangerous part (wide, slow-turning",
              "  chord), but most of the area is out near the tip, where",
              f"  the chance is small: the disc average, {mean:.2f}, is close to the",
              "  0.08 used in lesson A - a check of the teaching value,",
              "  not a replacement for the study (U-113)"]
    emit("r_transit", lines)


def visual_angle() -> None:
    rec = dict(src.DWELLINGS, **{"village centre": src.VILLAGE_CENTRE})
    lines = ["how large the nearest turbine looks (blade tip, flat ground, teaching)",
             "  receptor                       nearest m   tip angle deg   reading"]
    for name, (x, y) in rec.items():
        d = float(np.hypot(src.TURBINES[:, 0] - x, src.TURBINES[:, 1] - y).min())
        ang = math.degrees(math.atan(s14.TIP / d))
        if ang >= 10:
            read = "dominant"
        elif ang >= 5:
            read = "prominent"
        elif ang >= 2:
            read = "noticeable"
        else:
            read = "minor"
        lines.append(f"  {name:30s} {d:9.0f}   {ang:13.1f}   {read}")
    lines += ["  a 175 m tip at 800 m stands about as tall as a fist held",
              "  at arm's length (about 10 deg): the camp and farmhouse A see the farm",
              "  as a dominant feature, the village as a noticeable one;",
              "  the bands are teaching readings - the landscape study and",
              "  the photomontages agreed with the village judge them"]
    emit("r_visual", lines)


def audits() -> None:
    rows = [  # audit, findings, major, closed in 60 days, repeated from the last audit
        ("audit 1 (construction month 6)", 14, 3, 9, 0),
        ("audit 2 (construction month 12)", 9, 1, 8, 2)]
    lines = ["two independent E&S audits of the construction (synthetic)",
             "  audit                              findings  major  closed 60 d  repeated"]
    for name, n, mj, cl, rp in rows:
        lines.append(f"  {name:34s} {n:8d}  {mj:5d}  {cl / n * 100:9.0f} %  {rp:8d}")
    lines += ["  fewer findings and faster closure say the system works;",
              "  the two repeated findings say two fixes did not hold - a",
              "  repeat is raised one level (a major becomes a lender",
              "  notice) and its root cause is re-opened; the auditor is",
              "  independent of the contractor and reports to the owner",
              "  and the lenders, and the summary goes to the village"]
    emit("r_audits", lines)


if __name__ == "__main__":
    transit()
    visual_angle()
    audits()
