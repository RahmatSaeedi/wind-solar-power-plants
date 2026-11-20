"""Chapter 32, lesson S: the control room and the materials on site - an
alarm flood during an event, the hazardous-materials inventory of Plant
P, and how many spill kits each area needs.

Run from the project root:   python -m companion.ch32.examples_s
Writes companion/ch32/expected/s_*.txt and diagrams/data/ch32-alarms.csv.
Teaching values (A-369, A-372); thresholds for permits and reporting
come from local law (ch 33, 55-57).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch32 import sources as src  # noqa: F401  (puts plantp on the path)
from companion.ch32.common import csv, emit


def alarm_flood(seed: int = 32) -> None:
    rng = np.random.default_rng(seed)
    minutes = np.arange(0, 60)
    base = rng.poisson(0.1, minutes.size)
    flood = np.where((minutes >= 20) & (minutes < 30), rng.poisson(12, minutes.size), 0)
    alarms = base + flood
    csv("ch32-alarms.csv", "minute,alarms", list(zip(minutes.tolist(), alarms.tolist())))
    in_flood = int(alarms[20:30].sum())
    lines = ["alarms in the control room around a fire at BESS-1 (synthetic)",
             f"  normal: about {alarms[:20].mean() * 10:.0f} alarms in ten minutes",
             f"  minutes 20-30: {in_flood} alarms - about {in_flood / 10:.0f} a minute",
             "  an operator handles roughly one considered action a minute:",
             "  in a flood the few alarms that matter (fire, isolation",
             "  feedback, people) are lost among consequential ones - the",
             "  alarm system gives fire and life-safety alarms the top",
             "  priority, suppresses the expected follow-on alarms, and",
             "  the emergency plan gives the operator a short checklist"]
    emit("s_alarms", lines)


def hazmat() -> None:
    items = [("transformer oil (2 main + 26 unit)", "22 x 2 + 3 x 26 m3", 44 + 78, "m3"),
             ("SF6 in 132 kV and 33 kV switchgear", "teaching", 0.6, "t"),
             ("battery electrolyte (in cells)", "8 containers", 40.0, "t"),
             ("diesel (crane campaign store)", "ch 31", 60.0, "m3"),
             ("lubricants and greases", "turbines, cranes", 8.0, "m3"),
             ("paints and solvents", "construction", 3.0, "m3")]
    lines = ["hazardous materials on site at the peak of construction (teaching)",
             "  material                               basis                 amount"]
    for name, basis, q, unit in items:
        lines.append(f"  {name:38s} {basis:20s} {q:6.1f} {unit}")
    lines += ["  each has a safety data sheet, a storage rule (bund, cover,",
              "  separation), a spill response and a waste route; whether",
              "  an amount triggers a permit or a major-hazard regime is",
              "  local law (ch 33, 55-57) - the inventory is kept current",
              "  because the fire service and the permit both ask for it"]
    emit("s_hazmat", lines)


def spill_kits() -> None:
    lines = ["spill kits by area (teaching: absorb the largest likely spill)",
             "  area                      largest likely spill L   kit L   kits"]
    for name, spill, kit in [("refuelling point", 200, 120), ("crane on its pad", 150, 120),
                             ("transformer bay", 400, 240), ("workshop and store", 60, 50),
                             ("each turbine during service", 40, 50)]:
        lines.append(f"  {name:28s} {spill:18d}   {kit:5d}   {math.ceil(spill / kit):4d}")
    lines += ["  a kit sized for a drip is useless at a burst hose: the",
              "  largest likely spill sets the kit, the bund catches the",
              "  rest, and used absorbent is hazardous waste (ch 33)"]
    emit("s_spill", lines)


if __name__ == "__main__":
    alarm_flood()
    hazmat()
    spill_kits()
