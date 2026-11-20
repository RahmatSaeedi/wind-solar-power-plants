"""Chapter 45, round x: end-of-line tests of a module against its parts,
the hours of a container's factory test, the transport documents of each
container, and module spares from the fleet's return rate.

Run from the project root:   python -m companion.ch45.examples_x
Writes companion/ch45/expected/x_*.txt.
Teaching values (A-476 to A-481).
"""
from __future__ import annotations

import math

from companion.ch45 import examples_u as eu
from companion.ch45 import sources as src
from companion.ch45.common import emit

B = src.BUILD


# ------------------------------------------------ 1. module end-of-line coverage
PARTS = ["cells", "welds", "busbars", "sense wires", "temperature sensors",
         "insulation sheet", "compression frame", "label and lot",
         "cooling contact"]
EOL = [   # test, parts it reaches
    ("OCV of every cell", ["cells", "sense wires"]),
    ("pulse resistance of the module", ["cells", "welds", "busbars"]),
    ("resistance of every weld", ["welds"]),
    ("insulation to frame", ["insulation sheet"]),
    ("sense-line self-test", ["sense wires"]),
    ("sensor plausibility at room temperature", ["temperature sensors"]),
    ("label scan against the record", ["label and lot"]),
]


def module_eol() -> dict:
    covered = {p for _, ps in EOL for p in ps}
    missing = [p for p in PARTS if p not in covered]
    lines = [f"end-of-line tests of a module against its {len(PARTS)} parts",
             "  test                                      reaches"]
    for t, ps in EOL:
        lines.append(f"  {t:41s} {', '.join(ps)}")
    lines += [f"  parts no test reaches: {', '.join(missing)}",
              "  the frame's force is recorded at assembly but not tested at",
              "  the end, and nothing shows that the cells touch the cooling",
              "  plate - a thermal test at load (or a check of the gap pad's",
              "  compression) closes the gap; the same tree-against-tests",
              "  check as for inverters (ch 44)"]
    emit("x_eol", lines)
    return dict(missing=missing)


# ------------------------------------------------ 2. hours of a container test
STEPS = [   # step, hours
    ("visual, documents, torques", 4.0), ("insulation and earth continuity", 3.0),
    ("BMS configuration and fingerprint", 1.0), ("interface signals (round u)", 4.0),
    ("HVAC and fire-system signals", 3.0), ("charge to the top of the window", 3.5),
    ("rest and OCV spread", 12.0), ("discharge, capacity and efficiency", 3.5),
    ("thermal map at load", 2.0), ("records and release", 2.0),
]


def fat_hours(shifts_h: float = 16.0, stations: int = 2) -> dict:
    tot = sum(h for _, h in STEPS)
    per_week = stations * 5 * shifts_h / tot
    lines = [f"factory test of one container (teaching hours), {stations} test "
             "bays,",
             f"  {shifts_h:.0f} h a day, 5 days",
             "  step                                   hours"]
    for name, h in STEPS:
        lines.append(f"  {name:38s} {h:5.1f}")
    lines += [f"  total {tot:.0f} h a container; {per_week:.1f} containers a week",
              f"  the plant's {B['containers']} containers take "
              f"{B['containers'] / per_week:.1f} weeks of the bays",
              "  the twelve-hour rest is the longest step and the first a",
              "  hurried plan cuts; it settles the cells so the OCV spread",
              "  shows a wrong or badly unbalanced cell - it cannot show a",
              "  slow leaker, which needs weeks (lab D)"]
    emit("x_fat", lines)
    return dict(hours=tot, per_week=per_week)


# ------------------------------------------------ 3. transport documents
DOCS = ["cell transport test summary (STD-101)", "SOC at dispatch",
        "shock and tilt logs", "packing and securing record",
        "dangerous-goods declaration", "BMS configuration fingerprint",
        "factory test report", "storage instructions"]
SHIPMENTS = {"C1": set(DOCS), "C2": set(DOCS), "C3": set(DOCS) - {"shock and tilt logs"},
             "C4": set(DOCS), "C5": set(DOCS) - {"SOC at dispatch"},
             "C6": set(DOCS), "C7": set(DOCS) - {"storage instructions"},
             "C8": set(DOCS)}


def transport() -> dict:
    gaps = {c: sorted(set(DOCS) - d) for c, d in SHIPMENTS.items() if set(DOCS) - d}
    lines = [f"transport documents of the {len(SHIPMENTS)} containers "
             f"({len(DOCS)} each, teaching list)"]
    for c, g in gaps.items():
        lines.append(f"  {c}: missing {', '.join(g)}")
    lines += [f"  {len(gaps)} of {len(SHIPMENTS)} containers arrive with a gap; each",
              "  is held at receiving until the document comes - a missing",
              "  shock log means the container is inspected as if it had",
              "  been dropped, a missing SOC that it is measured first"]
    emit("x_docs", lines)
    return dict(gaps=gaps)


# ------------------------------------------------ 4. module spares from returns
def spares(fleet_modules: int = 3000, years: float = 2.0, lead_weeks: float = 16.0,
           cover: float = 0.90) -> dict:
    ret = sum(r[1] for r in eu.RETURNS)
    rate = ret / (fleet_modules * years)                    # a module-year
    ours = B["m_rack"] * B["r_container"] * B["containers"]
    mean = rate * ours * lead_weeks / 52
    k, cum, term = 0, math.exp(-mean), math.exp(-mean)
    while cum < cover:
        k += 1
        term *= mean / k
        cum += term
    lines = [f"returns {ret} in {years:.0f} years of a {fleet_modules:,}-module fleet "
             f"(round u): {rate:.4f} a module-year",
             f"  Plant P's {ours} modules: {rate * ours:.1f} returns a year expected",
             f"  in a {lead_weeks:.0f}-week resupply: {mean:.2f}; stock for "
             f"{cover:.0%}: {k} modules",
             "  the stock is held at the right SOC and age (lesson C) and",
             "  rotated: a spare is part of the battery's record from the",
             "  day it arrives (ch 52)"]
    emit("x_spares", lines)
    return dict(rate=rate, stock=k)


if __name__ == "__main__":
    module_eol()
    fat_hours()
    transport()
    spares()
