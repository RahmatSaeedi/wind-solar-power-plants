"""Chapter 23, section C - reviewing a draft one-line: eight errors are
planted in a copy of Plant P's network; the generic checks of the
one-line module and four project checks (duplicate tags, station-service
rating against demand, feeder current against cable rating, a revenue
meter at the boundary) find them; a revision log shows the drawing's
status from review to construction.

Run from the project root:   python -m companion.ch23.examples_c
Writes companion/ch23/expected/c_*.txt.
"""
from __future__ import annotations

import copy
import math
from collections import Counter

from companion.ch23 import sources as src
from companion.ch23.common import emit
from plantp import auxpower as ax
from plantp import oneline as ol

CABLE_A = 410.0        # 33 kV 240 mm2 rating before derating (ch 18)


def draft() -> ol.OneLine:
    """Plant P with eight planted errors (the answer key is PLANTED)."""
    g = src.plant()
    by = {b.tag: b for b in g.branches}
    by["=T2"].rating["lv_kv"] = 34.5                       # 1 windings
    by["=WS2-W3"].zone = ""                                # 2 no zone
    g.add(ol.Branch("=E1-W2", "line", "E1", "GRID-BAY", zone="Z-L1"))   # 3 boundary
    by["=PVF2-W3"].b = "PVF2-30"                           # 4 undefined bus
    g.add(copy.deepcopy(by["=PVF3-Q1"]))                    # 5 duplicate tag
    by["=A1-T1"].rating["kva"] = 160                       # 6 SST too small
    g.add_bus(ol.Bus("WS2-5", 33.0, zone="Z-WS2"))
    g.add(ol.Branch("=WS2-W5", "cable", "WS2-4", "WS2-5", zone="Z-WS2",
                    rating={"mm2": 240}))                  # 7 fifth turbine
    for b in g.branches:                                   # 8 no meter
        b.meter = ""
    return g


PLANTED = ["T2 windings 132/34.5", "WS2-W3 no zone", "E1-W2 boundary",
           "PVF2-W3 undefined bus", "duplicate PVF3-Q1", "A1-T1 160 kVA",
           "WS2 five turbines", "no revenue meter"]


# [start: project]
def project_checks(g: ol.OneLine) -> list[str]:
    out = []
    dup = [t for t, n in Counter(b.tag for b in g.branches).items() if n > 1]
    out += [f"{t}: tag used twice" for t in dup]
    p, q, s = ax.demand(src.AUX, "normal", src.DIVERSITY)
    for b in g.branches:
        kva = b.rating.get("kva")
        if kva and kva < s * 1.2:          # N-1: one SST carries all
            out.append(f"{b.tag}: {kva} kVA below {s * 1.2:.0f} kVA needed")
    for sec in ("MV-A", "MV-B"):
        for br, head in g.neighbours(sec):
            if br.kind != "breaker" or "-0" not in head:
                continue
            n = sum(1 for b in g.buses if b.startswith(head[:-2] + "-")
                    and not b.endswith(("-0", "-LV")))
            i = n * 5.0e6 / 0.95 / (math.sqrt(3) * 33e3)
            if i > CABLE_A:
                out.append(f"{br.tag}: {n} units, {i:.0f} A"
                           f" above {CABLE_A:.0f} A")
    if not any(b.meter.startswith("revenue") for b in g.branches):
        out.append("no revenue meter on the one-line")
    return out
# [end: project]


def review() -> None:
    g = draft()
    generic = g.checks()
    proj = project_checks(g)
    lines = [f"review of a draft one-line ({len(PLANTED)} errors planted):",
             "  generic one-line checks:"]
    lines += [f"    {x}" for x in generic]
    lines.append("  project checks:")
    lines += [f"    {x}" for x in proj]
    lines += [f"  findings {len(generic) + len(proj)} for {len(PLANTED)} planted errors;",
              "  one fault no check sees: the line E1-W2 also closes a loop",
              "  around the line bay - only a person who knows the plant",
              "  is radial sees it",
              "  a check found by a program is cheap; one found on site is",
              "  not - but a program checks only what someone wrote down"]
    emit("c_review", lines)


def revisions() -> None:
    log = [("A", "IFR", "first issue for internal review"),
           ("B", "IFR", "battery moved to its own bays; SST 250 kVA"),
           ("C", "IFA", "issued to the utility with POC options A/B"),
           ("0", "IFC", "after the grid offer: line owner, meter, CTs"),
           ("1", "IFC", "turbine maker's transformer impedance")]
    lines = ["revision log of the plant one-line (PLP-ELE-DWG-0005, teaching):",
             "  rev  status  change"]
    lines += [f"  {r:3s}  {st:6s}  {c}" for r, st, c in log]
    lines += ["  letters before construction, numbers after; each revision",
              "  says what changed and why, and clouds the change on the",
              "  sheet; the status (IFR, IFA, IFC: ch 2) says what the",
              "  drawing may be used for"]
    emit("c_revisions", lines)


if __name__ == "__main__":
    review()
    revisions()
