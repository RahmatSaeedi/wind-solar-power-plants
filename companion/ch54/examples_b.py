"""Chapter 54, more lessons A-C on the fictional Country Z: what kind of
text a clause is, which edition and amendments apply to an application,
the map of authorities, research records, ownership changes what applies,
the register's columns, who prepares, reviews and approves, two register
revisions compared, and interpretations kept in writing.

Run from the project root:   python -m companion.ch54.examples_b
Writes companion/ch54/expected/a_clauses.txt and others.
Fictional teaching data (A-546 to A-548).
"""
from __future__ import annotations

from datetime import date

from companion.ch54 import sources as src
from companion.ch54.common import emit
from plantp import compliance as cp
from plantp import docctl


def filled(records: dict, fields) -> tuple[float, dict]:
    """Share of all cells filled (docctl.completeness) and per field."""
    share, _ = docctl.completeness([dict(v, id=k) for k, v in records.items()],
                                   fields)
    per = {f: sum(bool(v.get(f)) for v in records.values()) / len(records)
           for f in fields}
    return share, per


# ------------------------------------------------ A4. what kind of text
def clauses() -> dict:
    kinds = {}
    vague = []
    for cl, text, kind in src.CLAUSES:
        kinds[kind] = kinds.get(kind, 0) + 1
        if kind.startswith("normative") and any(v in text for v in src.VAGUE):
            vague.append(cl)
    binding = sum(v for k, v in kinds.items() if k.startswith("normative"))
    lines = [f"{len(src.CLAUSES)} pieces of one grid-code extract, by kind"]
    lines += [f"  {k:18s} {v}" for k, v in sorted(kinds.items(), key=lambda kv: -kv[1])]
    lines += [f"  binding (normative text and normative annex): {binding} of"
              f" {len(src.CLAUSES)}",
              f"  normative but vague: {', '.join(vague)} ('as appropriate',",
              "  'adequate') - binding words with no number: each needs a",
              "  written interpretation before design can verify it"]
    emit("a_clauses", lines)
    return dict(kinds=kinds, binding=binding, vague=vague)


# ------------------------------------------------ A5. which edition applies
def transition() -> dict:
    at_file = cp.consolidated(src.GCZ_CLAUSES, src.FILED)
    at_conn = cp.consolidated(src.GCZ_CLAUSES, src.CONNECT)
    lines = [f"GCZ text in force on the filing date {src.FILED} and on first",
             f"energisation {src.CONNECT} (base 2024 + amendments)"]
    diff = []
    for cl in sorted(set(at_file) | set(at_conn)):
        a = at_file.get(cl, ("-", "not yet in force"))
        b = at_conn.get(cl, ("-", "not yet in force"))
        lines.append(f"  {cl}: filing   {a[0]:4s} {a[1]}")
        lines.append(f"       energise {b[0]:4s} {b[1]}")
        if a != b:
            diff.append(cl)
    lines += [f"  clauses that differ between the two readings: {', '.join(diff)}",
              "  the transitional clause does not say which date fixes the",
              "  text - CQ-04 asks it; meanwhile the design takes the",
              "  stricter text where it is cheap (8 %/min is a setting) and",
              "  records where it is not (4-second telemetry is a contract)"]
    emit("a_transit", lines)
    return dict(diff=diff)


# ------------------------------------------------ B4. map of authorities
def authorities() -> dict:
    by = {}
    for topic, auth, level, st in src.AUTHORITIES:
        by[st] = by.get(st, 0) + 1
    gaps = [t for t, a, _, s in src.AUTHORITIES if s != "verified"]
    lines = [f"who decides what for Plant P ({len(src.AUTHORITIES)} topics, fictional)"]
    for topic, auth, level, st in src.AUTHORITIES:
        lines.append(f"  {topic:34s} {level:10s} {st}")
        lines.append(f"      {auth or '(not identified)'}")
    lines += [f"  verified {by.get('verified', 0)}, project-dependent "
              f"{by.get('project-dependent', 0)}, to-confirm {by.get('to-confirm', 0)}",
              f"  open: {len(gaps)} topics - an unidentified authority is an",
              "  approval nobody has asked for yet"]
    emit("b_auth", lines)
    return dict(by=by, gaps=gaps)


# ------------------------------------------------ B5. research records
def research() -> dict:
    need = ("official_ref", "accessed", "verifier", "second_check")
    share, per = filled(src.RESEARCH, need)
    full = sum(all(v[f] for f in need) for v in src.RESEARCH.values())
    weak = [r for r, v in src.RESEARCH.items() if not v["official_ref"]
            or not v["second_check"]]
    lines = ["research record of each requirement: official reference, date",
             "accessed, who read it, who checked it"]
    lines += [f"  {f:14s} {per[f]:.0%} filled" for f in need]
    lines += [f"  cells filled {share:.0%}; records with all four: {full} of"
              f" {len(src.RESEARCH)}",
              f"  weak records: {', '.join(weak)}",
              "  Z-011 rests on a consultant's slide - not a source; Z-004",
              "  was read once, from an edition since replaced"]
    emit("b_research", lines)
    return dict(share=share, weak=weak, full=full)


# ------------------------------------------------ B6. ownership changes what applies
def ownership() -> dict:
    lines = ["requirements added by who builds and owns the 132 kV line"]
    out = {}
    for sc, extra in src.OWNERSHIP.items():
        out[sc] = len(extra)
        lines.append(f"  {sc:38s} +{len(extra)}")
    o3 = list(src.OWNERSHIP)[-1]
    lines += ["  under O3 the plant takes on:"]
    lines += [f"    - {x}" for x in src.OWNERSHIP[o3]]
    lines += ["  the ownership scenario is an input to the register, decided",
              "  before the search, not found out at the line's handover"]
    emit("b_owner", lines)
    return out


# ------------------------------------------------ C4. columns of the register
def fields() -> dict:
    share, per = filled(src.RECORDS, src.FIELDS)
    lines = ["the register's columns, filled share over six requirements"]
    lines += [f"  {f:14s} {per[f]:4.0%}" for f in src.FIELDS]
    worst = min(per, key=per.get)
    full = [r for r, v in src.RECORDS.items() if all(v.get(f) for f in src.FIELDS)]
    lines += [f"  cells filled {share:.0%}; complete rows: {len(full)} of"
              f" {len(src.RECORDS)} ({', '.join(full)})",
              f"  emptiest column: {worst} - a requirement without",
              "  evidence or approver is a claim, not compliance"]
    emit("c_fields", lines)
    return dict(per=per, full=full, share=share)


# ------------------------------------------------ C5. who prepares, reviews, approves
def raci() -> dict:
    issues = []
    for rid, (prep, rev, app) in src.RACI.items():
        if not app:
            issues.append((rid, "no approver named"))
        if prep == rev:
            issues.append((rid, "reviewer is the preparer"))
        if rev == app and app:
            issues.append((rid, "owner's engineer approves a requirement it reviews"))
    lines = ["preparer, reviewer and approver of six requirements"]
    for rid, (p, r, a) in src.RACI.items():
        lines.append(f"  {rid}: {p} / {r} / {a or '-'}")
    lines += ["  problems:"] + [f"    {rid}: {t}" for rid, t in issues]
    lines += ["  Z-012 may be fine if the owner is the approver by contract;",
              "  Z-004 and Z-009 are not: no independent eye, no named approver"]
    emit("c_raci", lines)
    return dict(issues=issues)


# ------------------------------------------------ C6. two revisions compared
def revisions() -> dict:
    d = cp.register_diff(src.REV_R2, src.REV_R3)
    lines = ["register R2 (2026-09) against R3 (2027-02)",
             f"  added:   {', '.join(d['added'])}",
             f"  removed: {', '.join(d['removed'])}"]
    for rid in d["removed"]:
        lines.append(f"    {rid}: {src.REV_NOTES.get(rid, 'NO REASON RECORDED')}")
    lines.append("  changed:")
    lines += [f"    {rid} {f}: {a} -> {b}" for rid, f, a, b in d["changed"]]
    lines += [f"  {len(d['changed'])} changes, each to be traced to a source",
              "  (contract draft 3, permit issued); a removal keeps its",
              "  reason - a requirement that disappears silently is the",
              "  one that returns at acceptance"]
    emit("c_rev", lines)
    return d


# ------------------------------------------------ C7. interpretations in writing
def interpretations() -> dict:
    oral = [i for i, *_, w in src.INTERPRETATIONS if not w]
    lines = ["interpretations the design depends on"]
    for i, rid, text, basis, by, w in src.INTERPRETATIONS:
        lines += [f"  {i} {rid} {'written' if w else 'NOT WRITTEN'}  agreed: {by or '-'}",
                  f"      {text}"]
    lines += [f"  {len(oral)} of {len(src.INTERPRETATIONS)} rest on a call, unsigned"
              " minutes or nobody:",
              f"  {', '.join(oral)} - each goes out as a written request",
              "  (INT-05 decides the ride-through conflict of CQ-01)"]
    emit("c_interp", lines)
    return dict(oral=oral)


if __name__ == "__main__":
    clauses()
    transition()
    authorities()
    research()
    ownership()
    fields()
    raci()
    revisions()
    interpretations()
