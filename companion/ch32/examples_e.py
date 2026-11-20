"""Chapter 32, lesson E: verification and lifecycle of fire and safety
systems - the ladder from product certificate to drill, how the test
interval sets the chance a detector fails when needed, what four drills
showed, which changes reopen the fire strategy, and the steps back to
service after an incident.

Run from the project root:   python -m companion.ch32.examples_e
Writes companion/ch32/expected/e_*.txt and diagrams/data/ch32-pfd.csv.
Teaching values (A-372).
"""
from __future__ import annotations

import numpy as np

from companion.ch32 import sources as src  # noqa: F401  (puts plantp on the path)
from companion.ch32.common import csv, emit


def ladder() -> None:
    rungs = [("product certificate", "type test by a lab",
              "the design can work", "this unit, this site"),
             ("factory test (FAT)", "maker, witnessed",
              "this panel works as built", "site wiring, other systems"),
             ("site functional test", "installer, each device",
              "each detector reaches the panel", "the outputs it drives"),
             ("integrated C&E test", "all parties, witnessed",
              "input to every output, with feedback", "people's response"),
             ("emergency drill", "site team, fire service",
              "people respond in time", "a real fire's conditions"),
             ("periodic inspection", "maintainer, by schedule",
              "it still works", "changes since the design")]
    lines = ["the verification ladder of a fire system (what each rung proves)"]
    for name, who, proves, not_ in rungs:
        lines += [f"  {name} - {who}",
                  f"      proves: {proves}",
                  f"      not: {not_}"]
    lines += ["  no rung replaces another: a certified detector wired to the",
              "  wrong output passes three rungs and fails the fourth"]
    emit("e_ladder", lines)


def pfd() -> None:
    lam = 0.02                                       # undetected failures per year
    rows = []
    lines = ["chance a detector is failed when needed (PFD) vs test interval",
             f"  undetected failure rate {lam} per year (teaching)",
             "  interval months   one detector   two (either alarms)"]
    for months in (1, 3, 6, 12, 24, 36):
        t = months / 12
        one = lam * t / 2
        two = (lam * t) ** 2 / 3
        rows.append((months, one, two))
        lines.append(f"  {months:15d}   {one:12.4f}   {two:19.6f}")
    csv("ch32-pfd.csv", "months,one,two", rows)
    r12 = rows[4 - 1][1] / rows[4 - 1][2]
    r3 = rows[1][1] / rows[1][2]
    lines += ["  halving the interval halves the PFD of one detector; a",
              f"  second detector cuts it {r12:.0f} to {r3:.0f} times here - unless",
              "  both share a cause (same dust, same power supply), which",
              "  the simple formula ignores and the design must not"]
    emit("e_pfd", lines)


def drills() -> None:
    d = [("D1 month 2", 41, 39, 17.5, "two contractors not on the list"),
         ("D2 month 5", 52, 52, 12.0, "gate key could not be found"),
         ("D3 month 8", 47, 47, 9.5, "radio dead spot at T07"),
         ("D4 month 11", 44, 44, 8.0, "fire service took the wrong road")]
    lines = ["four drills of the construction site (synthetic)",
             "  drill        people  counted  muster min  finding"]
    for name, n, c, m, f in d:
        lines.append(f"  {name:12s} {n:6d}  {c:7d}  {m:10.1f}  {f}")
    lines += ["  the muster time fell from 17.5 to 8.0 minutes and the count",
              "  became complete after D1; each drill found a new kind of",
              "  gap (people, keys, radio, road) - a drill is judged by what",
              "  it finds and fixes, not by being uneventful"]
    emit("e_drills", lines)


def change() -> None:
    changes = [("a ninth BESS container", "strategy, C&E, spacing, water, access"),
               ("new maker's battery firmware", "BMS alarms, C&E inputs, FAT records"),
               ("control room moved off site", "alarm path, call-out, response times"),
               ("new site road layout", "responder access, meeting point, plan maps"),
               ("detector model replaced", "certificate, site test, spares, training")]
    lines = ["changes that reopen the fire strategy (management of change)"]
    for c, docs in changes:
        lines.append(f"  {c:30s} -> {docs}")
    lines += ["  a change is small or large by what it touches, not by its",
              "  cost: new firmware is cheap and reopens the C&E matrix"]
    emit("e_change", lines)


def restore() -> None:
    steps = [("scene released by the fire service and the investigator", "H"),
             ("damage survey; residue and water handled by the permit", "-"),
             ("cause found, or a stated reason why it cannot be", "H"),
             ("repairs and replaced parts with their records", "-"),
             ("detection and isolation re-tested (rungs 3 and 4)", "H"),
             ("strategy and C&E updated for what was learned", "-"),
             ("return to service approved by the named person", "H")]
    lines = ["back to service after a fire (H = hold point)"]
    for k, (s, h) in enumerate(steps, 1):
        lines.append(f"  {k}. [{h}] {s}")
    lines += ["  restarting a battery or a transformer after a fire is a",
              "  decision of the maker, the insurer and the asset owner,",
              "  with evidence; the plan names who signs each hold point"]
    emit("e_restore", lines)


# [start: evidence]
NEED = ("certificate", "FAT", "site test", "C&E test", "manual")
DOSSIER = {   # item: evidence held (teaching)
    "fire alarm panel": {"certificate", "FAT", "site test", "C&E test",
                         "manual"},
    "aspirating smoke detectors": {"certificate", "site test", "manual"},
    "BESS off-gas detectors": {"certificate", "FAT", "site test", "manual"},
    "BESS container system": {"certificate", "FAT", "manual"},
    "fire-rated wall, transformer bay": {"certificate", "manual"},
    "cable fire stopping": {"certificate"},
    "nacelle detection (maker)": {"certificate", "FAT", "manual"},
    "fire pump set (if specified)": {"certificate", "FAT",
                                     "site test", "C&E test", "manual"},
}
# [end: evidence]

NOT_APPLICABLE = {"aspirating smoke detectors": {"FAT"},
                  "fire-rated wall, transformer bay": {"FAT", "C&E test"},
                  "cable fire stopping": {"FAT", "C&E test"}}


def evidence() -> None:
    lines = ["evidence register of the fire-protection items (teaching)",
             "  item                               missing evidence"]
    gaps = 0
    for item, held in DOSSIER.items():
        miss = [n for n in NEED
                if n not in held and n not in NOT_APPLICABLE.get(item, set())]
        gaps += len(miss)
        lines.append(f"  {item:34s} {', '.join(miss) or '-'}")
    lines += [f"  {gaps} pieces of evidence missing before handover",
              "  a wall or a fire stop has no factory test: its evidence",
              "  is the tested system's certificate plus a record that it",
              "  was installed as tested - photos and an inspection of",
              "  every penetration, before the cables hide it"]
    emit("e_evidence", lines)


if __name__ == "__main__":
    evidence()
    ladder()
    pfd()
    drills()
    change()
    restore()
