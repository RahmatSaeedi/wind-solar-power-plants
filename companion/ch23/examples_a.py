"""Chapter 23, sections A and B - voltage levels and currents, the
inventory of Plant P's one-line, its boundaries, the equipment schedule,
the interface matrix of the equipment packages, the loading of each
33 kV bus section and the feeder currents.

Run from the project root:   python -m companion.ch23.examples_a
Writes companion/ch23/expected/a_*.txt and b_*.txt, diagrams/data/ch23-*.csv.
Teaching values A-316 to A-320.
"""
from __future__ import annotations

import math
from collections import Counter

from companion.ch23 import sources as src
from companion.ch23.common import csv, emit


def amps(mva: float, kv: float, pf: float = 1.0) -> float:
    """Line current of a three-phase load or source (A)."""
    return mva * 1e6 / (math.sqrt(3) * kv * 1e3) / pf


# [start: levels]
LEVELS = [("PV inverter output", 5.0, 0.6),       # (where, MVA, kV)
          ("turbine converter", 5.0, 0.69),
          ("station service board", 0.5, 0.4),
          ("PV feeder (4 blocks)", 20.0, 33.0),
          ("33 kV bus section", 65.0, 33.0),
          ("export at 132 kV", 100.0, 132.0)]
# [end: levels]


def levels() -> None:
    lines = ["current at each voltage level (unity power factor):",
             "  where                     MVA      kV        A    loss vs 33 kV"]
    rows = []
    for name, mva, kv in LEVELS:
        i = amps(mva, kv)
        lines.append(f"  {name:24s} {mva:6.1f} {kv:7.2f} {i:8,.0f}   {(33 / kv) ** 2:10,.2f} x")
        rows.append((name.split()[0], f"{kv}", f"{i:.0f}"))
    lines += ["  (last column: loss in the same conductor relative to 33 kV for",
              "  the same power, I^2 R with I = S / (sqrt 3 U))",
              "  5 MW at 0.6 kV is 4,811 A - a busbar, not a cable run; the",
              "  same 5 MW at 33 kV is 87 A: each level is the cheapest way",
              "  to carry its power the distance it has to go"]
    emit("a_levels", lines)
    csv("ch23-levels.csv", "name,kv,a", rows)


def inventory() -> None:
    g = src.pv_block_detail(src.plant())
    kinds = Counter(b.kind for b in g.branches)
    volts = Counter(b.kv for b in g.buses.values())
    owners = Counter(b.owner for b in g.buses.values())
    lines = ["inventory of Plant P's one-line (with one PV block's DC side):",
             "  branches by kind:",
             "    " + ", ".join(f"{k} {n}" for k, n in sorted(kinds.items())[:4]) + ",",
             "    " + ", ".join(f"{k} {n}" for k, n in sorted(kinds.items())[4:]),
             "  buses by voltage:",
             "    " + ", ".join(f"{v:g} kV {n}" for v, n in sorted(volts.items())),
             "  buses by owner: " + ", ".join(f"{o} {n}" for o, n in sorted(owners.items())),
             f"  protection zones: {len({b.zone for b in g.branches})}",
             f"  isolation points: {sum(b.isolation for b in g.branches)}",
             "  the drawing shows the same facts; the data lets a program",
             "  count, trace and check them, and both must agree"]
    emit("a_inventory", lines)


def boundaries() -> None:
    g = src.plant()
    lines = ["ownership boundaries and the isolation point at each:"]
    for br in g.branches:
        a, b = g.buses[br.a], g.buses[br.b]
        if a.owner != b.owner:
            lines.append(f"  {br.tag:8s} {a.owner} | {b.owner}:"
                         f" {'isolation point' if br.isolation else 'NO isolation point'}")
    lines += ["  two boundaries, both at disconnectors on the line; who owns",
              "  the line between them is open (U-065): the drawing marks it",
              "  open, it does not guess"]
    emit("a_boundaries", lines)


def schedule() -> None:
    g = src.plant()
    rows = g.schedule(kinds=["transformer"])
    seen = Counter()
    lines = ["transformer schedule (grouped; open items flagged):",
             "  group                 n   rating                           open"]
    groups = {}
    for tag, _k, _o, _txt, open_ in rows:
        r = next(b for b in g.branches if b.tag == tag).rating
        size = f"{r['mva']} MVA" if "mva" in r else f"{r['kva']} kVA"
        txt = f"{size} {r['hv_kv']:g}/{r['lv_kv']:g} kV z {r['z_pu']}"
        key = ("main" if tag in ("=T1", "=T2") else "station service" if tag.startswith("=A")
               else tag.split("-")[0].strip("=0123456789").rstrip("F") + " unit")
        groups.setdefault(key, []).append((txt, open_))
        seen[key] += 1
    for key, items in groups.items():
        txt, open_ = items[0]
        lines.append(f"  {key:18s} {len(items):3d}   {txt:30s} {', '.join(open_)}")
    lines += [f"  {len(rows)} transformers; every impedance is provisional until",
              "  the makers' offers and the fault study (ch 25, 26)"]
    emit("b_schedule", lines)


# [start: interfaces]
PACKAGES = ["wind turbine", "PV block", "battery block", "MV switchgear",
            "main transformer", "station service", "DC and UPS",
            "PPC and SCADA", "HV bay and meter", "export line"]
TYPES = ["power", "grounding", "control", "comms", "mechanical", "cooling",
         "aux supply"]
ALL = "power grounding control comms mechanical cooling aux supply"
NEEDS = {   # package -> interface types it has (A-319)
    "wind turbine": ALL,
    "PV block": ALL,
    "battery block": ALL,
    "MV switchgear": ALL.replace(" cooling", ""),
    "main transformer": ALL.replace(" comms", ""),
    "station service": "power grounding control comms mechanical",
    "DC and UPS": ALL.replace(" aux supply", ""),
    "PPC and SCADA": "control comms mechanical cooling aux supply",
    "HV bay and meter": ALL.replace(" cooling", ""),
    "export line": "power grounding comms mechanical",
}
# [end: interfaces]


def interfaces() -> None:
    lines = ["interface matrix of the equipment packages (x = an interface):",
             "  package            pow   gnd   ctl   com  mech  cool   aux"]
    total = 0
    rows = []
    for p in PACKAGES:
        have = NEEDS[p].replace("aux supply", "aux").split()
        marks = []
        for t in TYPES:
            on = (t if t != "aux supply" else "aux") in have
            total += on
            marks.append("x" if on else ".")
        lines.append(f"  {p:17s} " + " ".join(m.rjust(5) for m in marks))
        rows.append((p.replace(" ", "_"), *[int(m == "x") for m in marks]))
    lines += [f"  {total} interfaces across {len(PACKAGES)} packages; each one gets a",
              "  drawing or a schedule, an owner on both sides and a test",
              "  (the register of ch 18 carries them, PLP-GEN-REG-0004)"]
    emit("b_interfaces", lines)
    csv("ch23-interfaces.csv", "package," + ",".join(t.replace(" ", "_") for t in TYPES), rows)


def sections() -> None:
    lines = ["loading of each 33 kV bus section (all sources at full output):",
             "  section  feeders                         MW   MVA pf .95  T rating"]
    for sec, fe in src.SECTIONS.items():
        mw = sum(n * src.UNIT_MW[f.rstrip("AB0123456789-")] for f, n in fe.items())
        txt = ", ".join(f"{f} {n}" for f, n in fe.items())
        lines.append(f"  {sec:7s}  {txt:30s} {mw:4.0f}  {mw / 0.95:9.1f}  63 MVA")
    lines += ["  each section can exceed its transformer when wind, PV and the",
              "  battery peak together: the plant controller limits each",
              "  transformer, not only the 100 MW at the POC (ch 20), or the",
              "  battery charges in those hours; with one transformer out,",
              "  the other carries the plant through the bus coupler, so the",
              "  export falls to about 60 MW until the repair (ch 18)"]
    emit("b_sections", lines)


def feeders() -> None:
    lines = ["feeder currents at full output against the provisional ratings:",
             "  feeder   MW    A at 33 kV  cable 410 A  breaker 630 A"]
    for sec, fe in src.SECTIONS.items():
        for f, n in fe.items():
            mw = n * src.UNIT_MW[f.rstrip("AB0123456789-")]
            i = amps(mw / 0.95, 33.0)
            lines.append(f"  {f:7s} {mw:4.0f}   {i:10.0f}  {i / 410:10.0%}  {i / 630:12.0%}")
    top = amps(20 / 0.95, 33.0) / 410
    lines += [f"  the heaviest feeder uses {top:.0%} of the 240 mm2 cable at full",
              "  output and pf 0.95 before any derating; installation",
              "  derating (depth, grouping, soil) is chapter 24's work and",
              "  may push the first section to a larger size"]
    emit("b_feeders", lines)


if __name__ == "__main__":
    levels()
    inventory()
    boundaries()
    schedule()
    interfaces()
    sections()
    feeders()
