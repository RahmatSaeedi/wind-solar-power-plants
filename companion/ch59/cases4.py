"""Chapter 59, last dossier lessons: the documents a change reopens, the
energy envelope of a frequency service, the retirement migration of the
asset records, and the full list of grid-study inputs.

Run from the project root:   python -m companion.ch59.cases4
"""
from __future__ import annotations

import math

from companion.ch59 import common  # noqa: F401  (path)
from companion.ch59.common import emit

# [start: graph]
WIND, EXP = "wind resource basis (D-017)", "export limit"
YIELD, UNC = "yield model (D-019)", "uncertainty statement (D-020)"
FIN, GRID = "finance model (D-025)", "grid study (D-032)"
PPC, PROT = "PPC settings (D-024)", "protection study (D-030)"
TURB = "turbine selection (D-015)"
GRAPH = {   # dossier data -> documents that use it (teaching, A-573)
    WIND: [YIELD, TURB],
    EXP: [YIELD, GRID, PPC],
    YIELD: [UNC, FIN, "O&M budget (D-056)"],
    UNC: [FIN],
    FIN: ["CP register", "PPA price bid"],
    GRID: [PROT, "PQ study (D-031)", "connection agreement"],
    PPC: ["FAT and SAT procedures (D-054)"],
    PROT: ["relay settings files"],
    TURB: ["foundation design (D-034)", "transport plan (D-035)"],
}
# [end: graph]


def d_impact() -> dict:
    from plantp import docctl
    out = {}
    lines = ["what a change reopens in the dossier (ch 38 helper on a teaching graph)"]
    for start in ("wind resource basis (D-017)", "export limit"):
        hit = docctl.impacted(GRAPH, start)
        out[start] = hit
        lines.append(f"  {start}: {len(hit)} documents")
        lines += [f"    {h}" for h in hit]
    lines += ["  the finance model and the CP register are reached from both:",
              "  every change case ends at the lenders' conditions"]
    emit("d_impact", lines)
    return out


def f_envelope() -> dict:
    from companion.ch20 import sources as s20
    lim = s20.LIMITS
    p = lim["bess_mw"]
    usable_dn = lim["e_max"] - 4.0 - lim["e_min"]          # from a mid state of 4 MWh margin
    lines = ["energy a 20 MW frequency service needs, against the battery's window",
             f"  usable window {lim['e_min']:.0f}-{lim['e_max']:.0f} MWh (ch 20 limits, A-299)",
             f"  {'hold (min)':>10s} {'energy MWh':>11s} {'from 20 MWh':>12s}"]
    out = {}
    for minutes in (5, 15, 30, 60):
        e = p * minutes / 60
        ok = e <= 20.0 - lim["e_min"]
        out[minutes] = (e, ok)
        lines.append(f"  {minutes:10d} {e:11.1f} {'yes' if ok else 'NO':>12s}")
    longest = (20.0 - lim["e_min"]) / p * 60
    lines += [f"  from a half-full battery (20 MWh) the service holds {longest:.0f} min down",
              "  and the same up; a contract asking for an hour needs a fuller",
              "  state or a larger battery - the envelope is written from this"]
    emit("f_envelope", lines)
    return dict(out=out, longest=longest, usable=usable_dn)


def j_migration() -> dict:
    from companion.ch18 import sources as s18
    root = s18.breakdown()
    equip = sum(n for node, n, d in root.walk() if node.level == "equipment")
    k = math.ceil(math.log(0.05) / math.log(0.99))
    hours = equip * 2 / 60
    lines = ["moving the asset records to a new CMMS at mid-life (teaching)",
             f"  equipment records to move: {equip:,d} (ch 18 hierarchy)",
             f"  sample checked with zero errors for < 1 % at 95 %: {k} records",
             f"  checking all at 2 min a record: {hours:,.0f} hours; the sample: {k * 2 / 60:.0f} h",
             "  the sample proves the migration, not each record: errors found",
             "  stop it and send it back to the mapping rules (ch 53, ch 58)"]
    emit("j_migration", lines)
    return dict(equip=equip, k=k, hours=hours)


def g_inputs_list() -> dict:
    from companion.ch28 import register as r28
    lines = ["grid-study and protection inputs, item by item (ch 28 register)",
             f"  {'id':6s} {'owner':9s} {'status':10s} item"]
    for i, item, owner, st, q, need in r28.INPUTS:
        lines.append(f"  {i:6s} {owner:9s} {st:10s} {item[:48]}")
    emit("g_inputs_list", lines)
    return dict(n=len(r28.INPUTS))


def main() -> dict:
    out = {}
    for f in (d_impact, f_envelope, j_migration, g_inputs_list):
        out[f.__name__] = f()
    return out


if __name__ == "__main__":
    main()
