"""Chapter 38, lessons F and G (grid-connection interface baseline and
information requirements): the responsibility matrix of the connection,
a change on the grid side that reaches the plant, the states of the common
data environment, the owner's information requirements as measurable
checks, and the score of a handover package.

Run from the project root:   python -m companion.ch38.examples_g
Writes companion/ch38/expected/g_*.txt.
Synthetic registers and teaching values (A-421, A-423).
"""
from __future__ import annotations

import re

from companion.ch38 import sources as src
from companion.ch38.common import emit
from plantp import docctl as dc

RACI = {   # interface item -> {party: role}; R does, A answers for it (planted gaps)
    "connection boundary diagram": {"plant": "R", "grid": "A"},
    "line route and circuit data": {"plant": "R", "grid": "C"},
    "grid bay protection settings": {"grid": "R"},
    "telemetry point list to the operator": {"plant": "R", "grid": "A"},
    "revenue metering": {"plant": "C", "grid": "R", "regulator": "A"},
    "earthing at the boundary": {"plant": "A", "grid": "A"},
    "land and permits for the line": {"plant": "R", "regulator": "A"},
}


def raci() -> None:
    lines = ["responsibility matrix of the grid connection (planted gaps)",
             "  item                                      accountable"]
    bad = []
    for item, roles in RACI.items():
        acc = [p for p, r in roles.items() if r == "A"]
        flag = "" if len(acc) == 1 else ("  <- none" if not acc else "  <- two")
        if flag:
            bad.append(item)
        lines.append(f"  {item:40s}  {', '.join(acc) or '-':12s}{flag}")
    lines += [f"  {len(bad)} items without exactly one accountable party; each is",
              "  settled at the next interface meeting and the matrix is",
              "  re-issued - an item with two owners has none"]
    emit("g_raci", lines)


def grid_change() -> None:
    graph = {"grid bay CT ratio 600/1 -> 800/1": ["line differential settings",
                                                   "plant-end protection study"],
             "line differential settings": ["intertrip scheme test"],
             "plant-end protection study": ["relay settings file", "one-line diagram"],
             "relay settings file": ["FAT procedure"], "one-line diagram": [],
             "intertrip scheme test": [], "FAT procedure": []}
    hit = dc.impacted(graph, "grid bay CT ratio 600/1 -> 800/1")
    lines = ["a change in the grid operator's bay that reaches the plant",
             "  change: grid bay CT ratio 600/1 -> 800/1 (teaching)",
             f"  plant documents and tests touched: {len(hit)}"]
    for h in hit:
        lines.append(f"    {h}")
    lines += ["  the operator owns the bay, the plant owns what depends on",
              "  it; the interface schedule names both, and a change on",
              "  either side is notified to the other before it is",
              "  issued (ch 28, line differential and intertrip)"]
    emit("g_gridchange", lines)


def cde_states() -> None:
    rows = [("work in progress", "author's team only", "WIP"),
            ("shared", "project teams, for coordination", "IFR, IFI, IFA"),
            ("published", "everyone who builds or buys", "APP, IFC"),
            ("archived", "record of what was used and built", "ASB, SUP")]
    lines = ["states of the common data environment and the statuses of ch 2",
             "  state              who may use it                       statuses"]
    for a, b, c in rows:
        lines.append(f"  {a:18s} {b:36s} {c}")
    lines += ["  information moves from one state to the next only through",
              "  a check and an approval; nobody builds from 'shared', and",
              "  nothing is deleted from 'archived' (STD-031 concept)"]
    emit("g_cde", lines)


TAG = re.compile(r"^=[A-Z]{1,4}\d?(-[A-Z])?(-\d{1,2})?(-[A-Z]{1,2}\d{1,2})?$")


def info_requirements() -> None:
    # locations in the local grid of the fictional site (ch 14), metres
    assets = [("=WS1-2-T1", "wind unit transformer", "TX-0412", "E6420 N3180"),
              ("=PVF2-3-T1", "PV unit transformer", "TX-0377", "E4150 N2960"),
              ("=PVF2-3-U1", "PV inverter", "", "E4150 N2960"),
              ("=T1", "main transformer", "TX-0001", ""),
              ("PVF2-Q1", "feeder breaker", "CB-0102", "E5300 N3050"),
              ("=BESS-A-1", "battery container", "BC-0001", "E5420 N3010")]
    lines = ["owner's information requirements checked on six asset records",
             "  tag           tag rule   asset id   location   item"]
    ok_all = 0
    for tag, item, aid, loc in assets:
        t = bool(TAG.match(tag))
        ok = t and bool(aid) and bool(loc)
        ok_all += ok
        lines.append(f"  {tag:13s} {'ok' if t else 'NO':9s}  {'ok' if aid else 'NO':9s}"
                     f"  {'ok' if loc else 'NO':9s}  {item}")
    lines += [f"  complete records: {ok_all} of {len(assets)}",
              "  (locations in the local grid of the fictional site, ch 14)",
              "  the requirement is written as a check a program can run:",
              "  tag pattern, stable asset id (ch 35), a location in the",
              "  site's GIS - and the acceptance is the share that passes"]
    emit("g_info", lines)


def handover() -> None:
    items = {k: (w, s) for k, (w, s, _) in src.HANDOVER.items()}
    score = dc.handover_score(items)
    lines = ["handover package against its acceptance criteria (A-421)",
             "  item                              weight   complete   critical"]
    fails = []
    for k, (w, s, crit) in src.HANDOVER.items():
        lines.append(f"  {k:32s} {w:6d}   {s * 100:7.0f} %   {'yes' if crit else ''}")
        if crit and s < 0.98:
            fails.append(k)
    lines += [f"  weighted score {score * 100:.1f} %",
              "  rule: every critical item at 98 % or better, the rest",
              f"  scored; critical items short: {len(fails)}",
              f"  a weighted score of {score * 100:.0f} % sounds nearly done; the rule",
              "  says the package is not accepted until the as-built",
              "  drawings, the asset attributes and the backups are"]
    emit("g_handover", lines)


if __name__ == "__main__":
    raci()
    grid_change()
    cde_states()
    info_requirements()
    handover()
