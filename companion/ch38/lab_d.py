"""Chapter 38, lab D (integrated document control): inconsistencies across
linked registers, references to old revisions, a requirements-to-
verification matrix, and one controlled change followed through every
document it touches to the as-built record.

Run from the project root:   python -m companion.ch38.lab_d
Writes companion/ch38/expected/d_*.txt.
Synthetic registers (A-418, A-420).
"""
from __future__ import annotations

from companion.ch38 import sources as src
from companion.ch38.common import emit
from plantp import docctl as dc


# [start: crosscheck]
def crosscheck():
    """All disagreements between the linked registers, as (pair, tag,
    field, first value, second value)."""
    pairs = [("one-line / equipment list", src.ONE_LINE, src.EQUIPMENT,
              ["a", "ka", "mva", "vector"]),
             ("one-line / cable schedule", {k: v for k, v in src.ONE_LINE.items()
                                            if "-W" in k}, src.CABLES,
              ["mm2", "km"]),
             ("settings / CT data sheets", src.PROTECTION, src.CT_LIST, ["ct"])]
    out = []
    for name, a, b, fields in pairs:
        common = {t: a[t] for t in a if t in b}
        for tag, f, x, y in dc.mismatches(common, {t: b[t] for t in common}, fields):
            if x is not None or y is not None:
                out.append((name, tag, f, x, y))
    return out
# [end: crosscheck]


def inconsistencies() -> None:
    found = crosscheck()
    lines = ["linked registers checked against each other (planted, A-418)",
             "  pair                        tag          field    first    second"]
    for name, tag, f, x, y in found:
        lines.append(f"  {name:27s} {tag:12s} {f:7s} {str(x):>7s}  {str(y):>7s}")
    lines += [f"  {len(found)} disagreements; who is right is a rule, not a vote:",
              "  ratings come from the approved one-line (rev 2 carries the",
              "  1,600 A incomers of ch 26), CT ratios from the switchgear",
              "  data sheets, lengths from the route survey. Each finding",
              "  becomes a correction of the other document, with a new",
              "  revision"]
    emit("d_inconsistencies", lines)


def stale_refs() -> None:
    out = dc.stale_references(src.CURRENT, src.REFS)
    lines = ["cross-references that use an old revision or a missing document",
             "  from               to                 rev used   current"]
    for a, b, r, cur in out:
        lines.append(f"  {a:18s} {b:18s} {r:>8s}   {str(cur):>7s}")
    lines += ["  the protection study was made on one-line rev 1, before the",
              "  incomers were raised - its results must be re-checked; the",
              "  network drawing lists points from an old I/O list; the",
              "  foundation drawing cites a drawing the register does not",
              "  know. A link carries the revision it used, so a new",
              "  revision shows who must look again"]
    emit("d_stale", lines)


def matrix() -> None:
    reqs = list(src.REQS)
    design = {r: v[1] for r, v in src.REQS.items()}
    verif = {r: [v[2]] if v[2] else [] for r, v in src.REQS.items()}
    evid = {r: v[3] for r, v in src.REQS.items()}
    m = dc.rvtm(reqs, design, verif, evid)
    lines = ["requirements-to-verification matrix, detailed design (A-418)",
             "  requirement  design  verification   evidence   text"]
    for r in reqs:
        row = m["rows"][r]
        meth = src.REQS[r][2] or "-"
        lines.append(f"  {r:11s}  {'yes' if row['design'] else 'NO':6s}  {meth:12s}"
                     f"   {'yes' if row['evidence'] else '-':8s}   {src.REQS[r][0]}")
    s = m["share"]
    lines += [f"  covered: design {s['design'] * 100:.0f} %, verification method"
              f" {s['verification'] * 100:.0f} %, evidence {s['evidence'] * 100:.0f} %",
              "  at detailed design, missing evidence is normal - it comes",
              "  from FAT, SAT and commissioning (ch 48, 50); a requirement",
              "  without a design document or without a verification",
              "  method is not normal: fire detection and water use have",
              "  no design owner yet, noise and water no method"]
    emit("d_rvtm", lines)


def change_to_asbuilt() -> None:
    start = "unit transformer rating"
    hit = dc.impacted(src.DEPENDS, start)
    hours = sum(src.REWORK_H[h] for h in hit)
    lines = ["change C-017: PV unit transformers 5.5 -> 5.6 MVA (ch 25 finding)",
             f"  documents touched, in order of the dependency graph ({len(hit)}):"]
    for k, h in enumerate(hit, start=1):
        lines.append(f"    {k:2d} {h:28s} {src.REWORK_H[h]:3d} h")
    lines += [f"  rework {hours} engineering hours before the first purchase order",
              "  the change request names the reason, the documents, the",
              "  hours and the date; each document gets a new revision",
              "  that cites C-017; after construction the as-built set",
              "  shows what was built, and the change log closes when the",
              "  last as-built revision is issued"]
    emit("d_change", lines)


if __name__ == "__main__":
    inconsistencies()
    stale_refs()
    matrix()
    change_to_asbuilt()
