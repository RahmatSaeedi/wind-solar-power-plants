"""Chapter 24 - seventh round: the heater that keeps an outdoor kiosk dry,
the torque on a bolted busbar joint and what it does to the contact,
a thermography survey sorted into actions, the markers and labels a
cable route needs, and the forms of separation of an LV board.

Run from the project root:   python -m companion.ch24.examples_w
Writes companion/ch24/expected/w_*.txt and diagrams/data/ch24-thermo.csv.
Teaching values (A-321..A-325 extended): action thresholds and torques
are the owner's procedure's and the makers'.
"""
from __future__ import annotations

import math

from companion.ch24.common import csv, emit


def heater() -> None:
    area, u = 18.0, 3.5               # m2 of walls and roof, W/(m2 K) (teaching)
    lines = ["anti-condensation heater of an outdoor RMU kiosk (teaching):",
             f"  walls and roof {area:.0f} m2, heat loss {u} W/(m2 K)",
             "  kept above ambient K   heater W"]
    for dt in (3, 5, 8):
        lines.append(f"  {dt:21d}   {area * u * dt:8.0f}")
    lines += ["  a few kelvin above the night air keeps the surfaces above",
              "  the dew point when the desert night cools fast; the heater",
              "  runs from the auxiliary supply with a humidistat, and its",
              "  failure is an alarm - tracking on wet insulation is how",
              "  many outdoor switchgear faults begin"]
    emit("w_heater", lines)


def torque() -> None:
    d, k = 0.012, 0.20                 # M12 bolt, nut factor (teaching)
    lines = ["torque on an M12 busbar joint: clamp force F = T / (K d)",
             "  (teaching: contact resistance ~ 1 / sqrt(F))",
             "  torque N m   clamp kN   relative R   relative heat at same I"]
    f_ref = 70 / (k * d)
    for t in (70, 50, 35, 20):
        f = t / (k * d)
        rel = math.sqrt(f_ref / f)
        lines.append(f"  {t:10d}   {f / 1e3:8.1f}   {rel:10.2f}   {rel:23.2f}")
    lines += ["  half the torque leaves 41 % more resistance and 41 % more",
              "  heat in the joint - which heats, oxidises and loosens it",
              "  further; the torque on the maker's drawing, a torque",
              "  wrench with a calibration record, and a paint mark on each",
              "  bolt are the assembly evidence (lesson C)"]
    emit("w_torque", lines)


SURVEY = [("=WS1-Q1 cable lug L1", 6), ("=WS1-Q1 cable lug L2", 31), ("=WS1-Q1 cable lug L3", 5),
          ("+H01 busbar joint 4", 48), ("=A1-T1 LV bushing", 12), ("LV board main breaker", 3),
          ("+H07 earthing transformer", 9), ("UPS input breaker", 17)]


def thermography() -> None:
    def action(dt: float) -> str:
        if dt >= 40:
            return "act now"
        if dt >= 15:
            return "repair at next outage"
        if dt >= 10:
            return "watch, re-scan"
        return "normal"
    lines = ["infrared survey at full load: rise over a like part (teaching classes)",
             "  item                           rise K   action"]
    for name, dt in SURVEY:
        lines.append(f"  {name:30s} {dt:6d}   {action(dt)}")
    csv("ch24-thermo.csv", "k,item,dt", [(i + 1, n.replace(",", ""), dt) for i, (n, dt) in enumerate(SURVEY)])
    lines += ["  the busbar joint at 48 K and the lug at 31 K are the loose or",
              "  dirty contacts of the torque lesson; the survey is taken at",
              "  high load (the rise grows with I^2), from outside closed",
              "  covers through infrared windows where the gear has them -",
              "  the thresholds and the access are the owner's procedure"]
    emit("w_thermo", lines)


def markers() -> None:
    route_km, bends, crossings, ends = 21.6, 60, 12, 2 * 26
    posts = math.ceil(route_km * 1000 / 50) + bends + 2 * crossings
    lines = ["marking the 33 kV cable routes (teaching spacing):",
             f"  route length {route_km} km (all feeders), {bends} bends, {crossings} crossings",
             f"  marker posts every 50 m, at each bend and both sides of a crossing: {posts}",
             f"  warning tape: {route_km * 1.05:.1f} km; cable labels at both ends: {ends}",
             "  labels also at every joint, manhole and entry into a",
             "  building; each label carries the tag of lesson D's schedule",
             "  the markers are what a digger sees in ten years' time; the",
             "  as-built survey with coordinates is what the office sees"]
    emit("w_markers", lines)


def forms() -> None:
    rows = [("form 1", "no separation inside", "whole board dead for any work"),
            ("form 2", "busbars separated from units", "busbars dead for unit work"),
            ("form 3", "+ units separated from each other", "one unit dead, others live"),
            ("form 4", "+ terminals separated per unit", "cables worked on per unit")]
    lines = ["forms of internal separation of an LV board (concept):"]
    for a, b, c in rows:
        lines += [f"  {a}: {b}", f"    maintenance: {c}"]
    lines += ["  the station-service board feeds the essential loads; a form",
              "  that lets one feeder be worked on with the others running",
              "  saves outages - whether work near live parts is allowed at",
              "  all is the owner's safety rule, not the board's form"]
    emit("w_forms", lines)


if __name__ == "__main__":
    heater()
    torque()
    thermography()
    markers()
    forms()
