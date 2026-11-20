"""Chapter 24, lab D - the engineering lab: a 33 kV cable schedule
validated by program (current in place, drop, fault withstand, bending
radius, drum length, tags against the one-line), the 33 kV switchboard
of section A mapped to panels, compartments and terminations with the
factory and site evidence of each (worked example 2), and the
inspection and test plan of the cable work with its hold points.

Run from the project root:   python -m companion.ch24.lab_d
Writes companion/ch24/expected/d_*.txt.
"""
from __future__ import annotations

import math

from companion.ch23 import sources as s23
from companion.ch24 import sources as src
from companion.ch24.common import emit
from plantp import cables as cb

ALPHA_AL = 0.00403

# [start: schedule]
SCHEDULE = [  # tag, mm2, km, units carried, min bend radius on route (m)
    ("=WS1-W1", 630, 1.1, 4, 2.0), ("=WS1-W2", 240, 1.1, 3, 2.0),
    ("=WS1-W3", 240, 1.1, 2, 2.0), ("=WS1-W4", 240, 1.1, 1, 2.0),
    ("=PVF1-W1", 400, 0.6, 4, 1.5), ("=PVF1-W2", 240, 0.6, 3, 2.0),
    ("=PVF1-W3", 240, 0.6, 2, 2.0), ("=PVF1-W4", 240, 0.6, 1, 2.0),
    ("=PVF1-W9", 240, 0.6, 1, 2.0),
]
DIAM_MM = {240: 92.0, 400: 106.0, 630: 121.0}   # overall, 3-core (teaching)
# [end: schedule]


def validate() -> list[str]:
    tags = {b.tag for b in s23.plant().branches}
    out = []
    for tag, mm2, km, units, bend in SCHEDULE:
        d = src.MV_CABLES[mm2]
        i = units * 5e6 / 0.95 / (math.sqrt(3) * 33e3)
        i_in, _ = cb.rating(d["i0"], src.FACTORS)
        if i > i_in:
            out.append(f"{tag}: {i:.0f} A above {i_in:.0f} A in place")
        if cb.withstand_ka(mm2, 1.0, src.K_AL) < 12.5:
            out.append(f"{tag}: fault withstand below 12.5 kA")
        if bend < 15 * DIAM_MM[mm2] / 1e3:
            out.append(f"{tag}: route bend {bend} m below {15 * DIAM_MM[mm2] / 1e3:.2f} m")
        if tag not in tags:
            out.append(f"{tag}: not on the one-line")
    return out


def schedule_check() -> None:
    found = validate()
    lines = [f"33 kV cable schedule check ({len(SCHEDULE)} rows, three errors planted):"]
    lines += [f"  {x}" for x in found]
    lines += ["  the 400 mm2 first section of PVF1 is too small in this",
              "  trench and its route bend too tight; =PVF1-W9 is a cable",
              "  the one-line does not have (a copy-paste row) - a schedule",
              "  is checked against the one-line, not only against itself"]
    emit("d_schedule", lines)


# [start: panels]
PANELS = [  # panel, function, breaker A, cable terminations, CTs
    ("+H01", "incomer from =T1 (=T1-Q2)", 1250, 2, "3 + 3"),
    ("+H02", "feeder =WS1", 630, 1, "3"),
    ("+H03", "feeder =WS2", 630, 1, "3"),
    ("+H04", "feeder =PVF3", 630, 1, "3"),
    ("+H05", "feeder =BESS-A", 630, 1, "3"),
    ("+H06", "station service =A1", 630, 1, "3"),
    ("+H07", "earthing transformer", 630, 1, "3 + 1"),
    ("+H08", "bus coupler =MV-Q0 (normally open)", 2500, 0, "3"),
    ("+H09", "metering and bus VT", 0, 0, "VT"),
]
# [end: panels]


def switchboard() -> None:
    lines = ["worked example 2: 33 kV switchboard, section A, to panels",
             "  panel  function                              A     terms  CTs"]
    for p, f, a, t, ct in PANELS:
        lines.append(f"  {p:5s}  {f:36s} {a if a else '-':>5}  {t:5d}  {ct}")
    lines += ["  every panel has four compartments: busbar, breaker (or",
              "  switch), cable, and low-voltage (relays, wiring); each",
              "  one-line symbol now has a panel, a compartment and",
              "  terminals",
              "  evidence per panel:",
              "    factory: type-test certificates of the design (internal",
              "      arc, short-time, temperature rise), routine tests of",
              "      this unit (power-frequency voltage, resistance of the",
              "      main circuit, function of mechanisms and interlocks)",
              "    site: installation checks, termination records, tests",
              "      of the cables, functional tests of trips and interlocks",
              f"  terminations on section A: {sum(t for *_, t, _ in PANELS)}"]
    emit("d_switchboard", lines)


def itp() -> None:
    steps = [("trench and duct inspection before laying", "hold", "survey, photos"),
             ("drum check: type, length, sealing, test sheet", "witness", "receiving record"),
             ("pulling with tension logging", "witness", "pulling record"),
             ("bending radius and position in the trench", "inspect", "as-laid record"),
             ("backfill, tape, marker before closing", "hold", "photos, levels"),
             ("joints and terminations by qualified jointers", "witness", "jointing record"),
             ("sheath test and cable test after laying", "witness", "test record"),
             ("as-built route survey", "inspect", "as-built drawing")]
    lines = ["inspection and test plan for the 33 kV cable work (concept):",
             "  step                                           point    record"]
    lines += [f"  {s:46s} {p:8s} {r}" for s, p, r in steps]
    lines += ["  a hold point stops the work until the inspector releases",
              "  it; a witness point is notified and may be attended; the",
              "  methods and the safety of the work belong to the maker's",
              "  instructions and trained staff (ch 47-49)"]
    emit("d_itp", lines)


if __name__ == "__main__":
    schedule_check()
    switchboard()
    itp()
