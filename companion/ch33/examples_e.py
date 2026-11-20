"""Chapter 33, lesson E: the environment after a fire - telling the
community, sampling the burnt yard, the wastes a battery fire leaves,
what to do with the water in the closed pond, and restoring the ground.

Run from the project root:   python -m companion.ch33.examples_e
Writes companion/ch33/expected/e_*.txt.
Teaching values (A-383); screening values, waste classes and discharge
routes come from the environmental permit and the authority (U-114).
"""
from __future__ import annotations

import math

from companion.ch33 import sources as src  # noqa: F401  (puts plantp on the path)
from companion.ch33.common import emit


def communication() -> None:
    steps = [(0, "fire reported; site emergency plan (ch 32)"),
             (15, "village leader and authority told: what, where, wind"),
             (30, "advice to stay indoors comes from the authority"),
             (60, "first update: smoke, roads closed, next update time"),
             (180, "update every 2-3 h while smoke lasts"),
             (1440, "public meeting: what happened, sampling plan, contacts"),
             (10080, "sampling results shared in plain language")]
    lines = ["telling the community during and after a fire (teaching timeline)",
             "  minutes   message"]
    for m, t in steps:
        lines.append(f"  {m:7d}   {t}")
    lines += ["  silence fills with rumour: the site tells people early,",
              "  says what is not yet known, and passes on the advice of",
              "  the authority - it does not invent its own; the same",
              "  grievance channel takes questions and claims (lesson H)"]
    emit("e_comms", lines)


def sampling() -> None:
    yard = 2400.0
    per = 100.0
    n = math.ceil(yard / per)
    lines = ["sampling the burnt battery yard (teaching grid)",
             f"  yard {yard:,.0f} m2, one composite sample per {per:.0f} m2: {n} samples",
             "  plus 3 background samples upwind and 2 at the pond outlet",
             "  analytes (teaching): metals (Ni, Co, Mn, Cu, Al), lithium,",
             "  fluoride, hydrocarbons, PAH from burnt plastics",
             "  each result is compared with the screening values of the",
             "  permit (PLACEHOLDERS here): below -> no action; above ->",
             "  excavation of that cell and re-test - the grid tells",
             "  where, the background tells what was there before"]
    emit("e_sampling", lines)


def wastes() -> None:
    rows = [("damaged battery modules", 40.0, "t", "hazardous; maker's take-back"),
            ("container steel, cleaned", 12.0, "t", "scrap, after testing"),
            ("contaminated soil", 60.0, "m3", "licensed disposal"),
            ("pond water", 160.0, "m3", "test, then treat or tanker"),
            ("absorbents, PPE", 1.5, "t", "hazardous")]
    lines = ["wastes a container fire leaves (teaching quantities)",
             "  waste                         amount    route"]
    for w, q, u, r in rows:
        lines.append(f"  {w:29s} {q:6.1f} {u:3s}  {r}")
    lines += ["  stranded energy in the modules (ch 32) makes their removal",
              "  a specialist job; each waste is classified, packed and",
              "  tracked to a licensed receiver - the waste record is part",
              "  of the incident file the authority will ask for"]
    emit("e_wastes", lines)


def pond_options() -> None:
    v = 160.0
    rows = [("treat on site, discharge under permit", 18.0, "if limits met after treatment"),
            ("tanker to a licensed facility", 45.0, f"{math.ceil(v / 20)} loads of 20 m3"),
            ("evaporate in the lined pond", 4.0, "concentrates salts and metals")]
    lines = ["the water in the closed pond after a fire (teaching costs, k u)",
             "  option                                  cost"]
    for o, c, n in rows:
        lines += [f"  {o:39s} {c:5.0f}", f"      note: {n}"]
    lines += ["  the cheapest option leaves a residue that is itself a",
              "  hazardous waste; the permit and the test results decide,",
              "  and nothing leaves the pond untested"]
    emit("e_pond", lines)


def restoration() -> None:
    lines = ["restoring the yard after a fire (teaching steps)",
             "  1 scene released by the fire service and investigator",
             "  2 wastes removed and recorded",
             "  3 soil sampled, hot spots excavated, re-tested",
             "  4 drains and pond cleaned, outlet tested",
             "  5 new foundations or the yard capped, as the owner decides",
             "  6 results and the closure report shared with the village",
             "  the plant may restart before step 6, but the community",
             "  hears the result of steps 3 and 4 before the yard is",
             "  called clean"]
    emit("e_restore", lines)


if __name__ == "__main__":
    communication()
    sampling()
    wastes()
    pond_options()
    restoration()
