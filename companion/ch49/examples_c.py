"""Chapter 49, lesson C (quality and systemization) and lesson K (asset
data): completion by subsystem, what holds mechanical completion, punch
items by category, and the asset records of block PVF1-3 checked stage by
stage and reconciled with the design register.

Run from the project root:   python -m companion.ch49.examples_c
Writes companion/ch49/expected/c_*.txt and k_*.txt.
"""
from __future__ import annotations

from companion.ch49 import sources as src
from companion.ch49.common import emit
from plantp import construction as con


# [start: mc]
def mc_ready() -> dict:
    comp = con.completion(src.ITEMS)
    open_a = {}
    for _, sub, cat, is_open in src.PUNCH:
        if is_open and cat == "A":
            open_a[sub] = open_a.get(sub, 0) + 1
    ready = {s: c[1] == 1.0 and not open_a.get(s) for s, c in comp.items()}
    return dict(comp=comp, open_a=open_a, ready=ready)
# [end: mc]


def show_mc() -> dict:
    r = mc_ready()
    lines = ["block PVF1-3 by subsystem: check sheets A (installed) and B",
             "  (checked), open category-A punch items, mechanical completion",
             "  subsystem      items  A done  B done  open A  ready"]
    for s, (n, a, b) in r["comp"].items():
        lines.append(f"  {s:13s} {n:5d}  {a:6.0%}  {b:6.0%}  {r['open_a'].get(s, 0):6d}  "
                     f"{'yes' if r['ready'][s] else 'no'}")
    ok = [s for s, v in r["ready"].items() if v]
    lines += [f"  ready for turnover: {', '.join(ok)}",
              "  the station's MV and inverter subsystems can be turned over",
              "  now; the block as a whole would wait for its slowest",
              "  subsystem - turnover by subsystem lets the station's tests",
              "  start while the strings are finished (ch 50)"]
    emit("c_mc", lines)
    return r


def punch() -> dict:
    by = {}
    for _, sub, cat, is_open in src.PUNCH:
        if is_open:
            by.setdefault(cat, []).append(sub)
    lines = ["open punch items by category",
             "  A: must close before mechanical completion (safety, function)",
             "  B: may close after turnover, with an owner and a date"]
    lines += [f"  {c}: {len(v)} open ({', '.join(sorted(set(v)))})" for c, v in sorted(by.items())]
    lines += ["  the category is agreed at the walkdown by both parties; a B",
              "  item that touches safety is an A item, whatever the list",
              "  says"]
    emit("c_punch", lines)
    return by


# ------------------------------------------------ K. asset data
def stages() -> dict:
    out = {}
    for tag, rec in src.ASSETS_FIELD.items():
        gaps = [st for st, fields in src.STAGES.items()
                if any(rec.get(f) in (None, "") or str(rec.get(f)).endswith("pending")
                       for f in fields)]
        out[tag] = gaps
    lines = ["asset records of block PVF1-3: stages with a missing field",
             "  (receipt: type, serial; installation: position, drawing; test:",
             "  baseline; turnover: warranty, spares, maintenance plan)"]
    lines += [f"  {t:14s} {', '.join(g) if g else 'complete'}" for t, g in out.items()]
    n_ok = sum(1 for g in out.values() if not g)
    lines += [f"  {n_ok} of {len(out)} records complete; a record is captured at the",
              "  stage it belongs to - a serial is read at receipt, not",
              "  looked up at handover"]
    emit("k_stages", lines)
    return out


def reconcile() -> dict:
    r = con.reconcile(src.ASSETS_DESIGN, src.ASSETS_FIELD, ["type", "doc"])
    dup = con.duplicates(rec["serial"] for rec in src.ASSETS_FIELD.values())
    far = []
    for t in sorted(set(src.ASSETS_DESIGN) & set(src.ASSETS_FIELD)):
        d, f = src.ASSETS_DESIGN[t], src.ASSETS_FIELD[t]
        e = con.distance((d["x"], d["y"]), (f["x"], f["y"]))
        if e > src.GIS_TOL_M:
            far.append((t, e))
    lines = ["field capture reconciled with the design register",
             f"  in design, not captured: {', '.join(r['missing']) or 'none'}",
             f"  captured, not in design: {', '.join(r['extra']) or 'none'}",
             f"  serial on two tags: {', '.join(dup) or 'none'}"]
    lines += [f"  {t}: {e:.1f} m from its design position (tolerance "
              f"{src.GIS_TOL_M:.0f} m)" for t, e in far]
    lines += ["  SW1 was captured as SW2 - one tag typed wrong makes one",
              "  asset missing and one extra; CB10's serial is CB09's - a",
              "  copied row; CB09 itself sits 11 m off its design spot: the",
              "  as-built drawing or the record is wrong, and only a visit",
              "  tells which"]
    emit("k_reconcile", lines)
    return dict(r=r, dup=dup, far=far)


if __name__ == "__main__":
    show_mc()
    punch()
    stages()
    reconcile()
