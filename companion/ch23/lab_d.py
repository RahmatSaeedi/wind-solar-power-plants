"""Chapter 23, lab D - the Plant P drafting lab (worked examples): the
provisional one-line summarised with its open parameters, one PV block
traced from module terminals to the grid meter with every interface and
the verification record that closes it, and the equipment schedule with
unresolved data flagged; plus the route and circuit schedule.

Run from the project root:   python -m companion.ch23.lab_d
Writes companion/ch23/expected/d_*.txt.
"""
from __future__ import annotations

from collections import Counter

from companion.ch23 import sources as src
from companion.ch23.common import emit

# [start: records]
RECORDS = {   # kind of branch -> verification record (purpose, evidence)
    "dc cable": "string record: polarity, open-circuit voltage, insulation",
    "dc switch": "combiner inspection: fuses, labels, torque record",
    "inverter": "maker FAT report; site functional and grid-code tests",
    "transformer": "routine test report; site ratio, insulation, vector",
    "cable": "cable test record after laying; route as-built",
    "breaker": "switchgear FAT; site tests of trip circuits, relay settings",
    "disconnector": "operation and interlock checks; earthing switch record",
    "line": "line as-built, clearances, insulation; utility acceptance",
}
# [end: records]


def oneline_summary() -> None:
    g = src.pv_block_detail(src.plant())
    open_items = Counter()
    status = Counter()
    for b in g.branches:
        for k, s in b.status.items():
            status[s] += 1
            if s != "confirmed":
                open_items[(b.kind, k, s)] += 1
    lines = ["provisional one-line of Plant P (PLP-ELE-DWG-0005 rev A):",
             f"  {len(g.buses)} buses, {len(g.branches)} branches;"
             f" parameter status: provisional {status['provisional']}, open {status['open']}",
             "  provisional or open parameters by kind:"]
    for (kind, k, s), n in sorted(open_items.items()):
        lines.append(f"    {kind:12s} {k:10s} {s:12s} x{n}")
    lines += ["  provisional values are designed with and marked on the",
              "  sheet (a cloud or a P); open ones are unknowns with an",
              "  owner and a date (U-065: who owns the line)"]
    emit("d_oneline", lines)


def trace() -> None:
    g = src.pv_block_detail(src.plant())
    path = g.path("PVF1-1-S01", "GRID")
    notes = g.crossings("PVF1-1-S01", "GRID")
    lines = ["one PV block traced from module terminals to the grid meter:",
             "  step  tag              kind",
             "        verification record"]
    for k, br in enumerate(path, 1):
        rec = RECORDS.get(br.kind, "-")
        lines.append(f"  {k:4d}  {br.tag:16s} {br.kind}")
        lines.append(f"        {rec}")
    lines.append(f"  interfaces crossed ({len(notes)}):")
    lines += [f"    {n}" for n in notes]
    lines += ["  every step has a record that closes it; the records are",
              "  named by purpose and evidence - how the tests are done",
              "  belongs to the testing chapters (ch 48-50) and their",
              "  qualified staff"]
    emit("d_trace", lines)


def unresolved() -> None:
    g = src.pv_block_detail(src.plant())
    rows = [(b.tag, b.kind, k, s) for b in g.branches for k, s in b.status.items()
            if s != "confirmed"]
    by_kind = Counter(r[1] for r in rows)
    lines = ["equipment schedule: unresolved data (first 12 of"
             f" {len(rows)} entries):",
             "  tag             kind          parameter  status"]
    lines += [f"  {t:15s} {k:13s} {p:10s} {s}" for t, k, p, s in rows[:12]]
    lines += ["  by kind: " + ", ".join(f"{k} {n}" for k, n in sorted(by_kind.items())),
              "  each entry names who closes it: the maker's offer, a study",
              "  (fault level, load flow) or the utility's connection offer"]
    emit("d_unresolved", lines)


def circuits() -> None:
    g = src.plant()
    rows = []
    for b in g.branches:
        if b.kind in ("cable", "line"):
            feeder = b.tag.strip("=").rsplit("-W", 1)[0]
            rows.append((feeder, b.kind, b.rating.get("km", 0.0), b.rating.get("mm2", "-")))
    tot = Counter()
    for f, kind, km, _ in rows:
        tot[(f, kind)] += km
    lines = ["route and circuit schedule (lengths provisional, km):",
             "  circuit   type    sections   km"]
    for (f, kind), km in sorted(tot.items()):
        n = sum(1 for r in rows if r[0] == f)
        lines.append(f"  {f:8s}  {kind:6s} {n:8d}  {km:5.2f}")
    cab = sum(km for (f, k), km in tot.items() if k == "cable")
    lines += [f"  33 kV cable {cab:.1f} km; 132 kV line 7.06 km",
              "  the cable lengths come from the layout of ch 14 and stay",
              "  provisional until the route survey; the schedule feeds the",
              "  cable sizing and losses of ch 24"]
    emit("d_circuits", lines)


if __name__ == "__main__":
    oneline_summary()
    trace()
    unresolved()
    circuits()
