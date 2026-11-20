"""Chapter 32, lesson U: four human-factors checks - how long an injured
lone worker waits to be missed, how often vehicles and walkers meet at a
gate, how much shade a hot day needs, and what climbing a 100 m tower
asks of the body.

Run from the project root:   python -m companion.ch32.examples_u
Writes companion/ch32/expected/u_*.txt and diagrams/data/ch32-lone.csv.
Teaching values (A-371, A-374, A-375).
"""
from __future__ import annotations

import math

from companion.ch32 import sources as src
from companion.ch32.common import csv, emit


def lone_working() -> None:
    response = 35.0                                     # min for the site team to reach a pad
    rows = []
    lines = ["an injured lone worker: when are they missed? (teaching)",
             "  check-in interval min   mean wait to be missed   + response   worst case"]
    for interval in (15, 30, 60, 120, 240):
        mean = interval / 2
        rows.append((interval, mean + response, interval + response))
        lines.append(f"  {interval:21d}   {mean:22.0f}   {mean + response:10.0f}"
                     f"   {interval + response:10.0f}")
    csv("ch32-lone.csv", "interval,mean,worst", rows)
    lines += ["  a two-hour check-in leaves an injured worker an hour on",
              "  average before anyone looks: lone work at a remote pad",
              "  is avoided, and where it cannot be, a check-in of about",
              "  30 minutes or a man-down alarm on the radio is used"]
    emit("u_lone", lines)


def gate_conflicts() -> None:
    lines = ["vehicles and walkers meeting at the laydown gate (Poisson, teaching)",
             "  conflict: a walker crosses within 10 s of a vehicle passing",
             "  vehicles/h   walkers/h   conflicts/h   per 10-hour day"]
    tau = 10 / 3600
    for v, p in [(10, 20), (40, 60), (40, 0)]:
        c = v * p * 2 * tau
        lines.append(f"  {v:10d}   {p:9d}   {c:11.2f}   {c * 10:15.1f}")
    lines += ["  a busy shared gate sees over a hundred near-meetings a",
              "  day; a separate pedestrian gate (last row) removes them -",
              "  the engineering control beats any amount of attention"]
    emit("u_gate", lines)


def shade() -> None:
    peak = src.WORKFORCE["peak"]
    lines = ["shade on a hot day (teaching: heavy work 45 min, rest 15 min an hour)",
             f"  peak workforce {peak}; share in heavy work 60 %",
             f"  people resting at any moment: {peak * 0.6 * 15 / 60:.0f}",
             f"  seats in shade at 1.5 m2 each: {peak * 0.6 * 15 / 60 * 1.5:.0f} m2"
             " spread over the fronts",
             "  shade only at the welfare cabins sends people on a walk",
             "  in the sun for every break; shelters move with the work",
             "  fronts, with water (lesson G); the work-rest pattern",
             "  comes from the site's heat procedure"]
    emit("u_shade", lines)


def climb() -> None:
    m, h = 90.0, 100.0                                  # kg with tools; m
    work = m * 9.81 * h / 1000                          # kJ
    metabolic = work / 0.2
    lines = ["climbing a 100 m tower by ladder (teaching, 90 kg with tools)",
             f"  mechanical work m g h = {work:.0f} kJ; at 20 % efficiency {metabolic:.0f} kJ"
             f" ({metabolic / 4.184:.0f} kcal)",
             "  climb time min   average power W   effort"]
    for t in (10, 15, 25):
        pw = metabolic * 1000 / (t * 60)
        effort = "very heavy" if pw > 450 else ("heavy" if pw > 300 else "moderate")
        lines.append(f"  {t:14d}   {pw:15.0f}   {effort}")
    lines += ["  a ladder climb is very heavy work before the job starts,",
              "  worse in a hot nacelle: the service lift is a safety",
              "  device, a fit-for-climbing check is part of competence,",
              "  and a tired climber is the one who misses a clip"]
    emit("u_climb", lines)


if __name__ == "__main__":
    lone_working()
    gate_conflicts()
    shade()
    climb()
