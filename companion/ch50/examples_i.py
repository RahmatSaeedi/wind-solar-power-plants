"""Chapter 50, lessons I and J: the operational information handover
validated before import (required fields, unique keys, references,
revisions), an import into the owner's maintenance system, a backup and
restore test; and emergency readiness before handover (roles, contacts,
drills).

Run from the project root:   python -m companion.ch50.examples_i
Writes companion/ch50/expected/i_*.txt and j_*.txt.
"""
from __future__ import annotations

from companion.ch50 import sources as src
from companion.ch50.common import emit
from plantp import commissioning as cm

REQUIRED = ["tag", "floc", "serial", "doc", "doc_rev", "warranty", "maint", "class_"]


# [start: handover]
def check_rows() -> dict:
    out = cm.validate(src.HANDOVER_ROWS, REQUIRED, "tag",
                      {"floc": src.FLOCS, "doc": set(src.DOCS)})
    out["revision"] = [(r["tag"], r["doc_rev"], src.DOCS[r["doc"]])
                       for r in src.HANDOVER_ROWS if r["doc"] in src.DOCS
                       and r["doc_rev"] != src.DOCS[r["doc"]]]
    return out
# [end: handover]


def show_rows() -> dict:
    r = check_rows()
    bad_tags = {t for k in ("missing", "duplicate", "dangling") for t, _ in r[k]}
    bad_tags |= {t for t, *_ in r["revision"]}
    rows = len(src.HANDOVER_ROWS)
    lines = [f"handover data of block PVF1-3 before import: {rows} rows, "
             f"{len(REQUIRED)} required fields",
             f"  missing fields:    {', '.join(f'{t} {f}' for t, f in r['missing']) or 'none'}",
             f"  duplicate keys:    {', '.join(t for t, _ in r['duplicate']) or 'none'}",
             f"  dangling refs:     {', '.join(f'{t} {f}' for t, f in r['dangling']) or 'none'}",
             "  revision differs from the document register:"]
    lines += [f"    {t}: row says {a}, register says {b}" for t, a, b in r["revision"]]
    lines += [f"  {len(bad_tags)} of {rows} rows have a defect; an import would load them",
              "  as they are - a maintenance plan for nothing, a location that",
              "  does not exist, a drawing revision that was replaced; the",
              "  rows are corrected at the source and the check run again"]
    emit("i_rows", lines)
    return dict(r=r, bad=len(bad_tags), rows=rows)


def import_test() -> dict:
    r = check_rows()
    bad = {t for k in ("missing", "dangling") for t, _ in r[k]}
    seen, accepted, rejected = set(), 0, 0
    for row in src.HANDOVER_ROWS:
        if row["tag"] in bad or row["tag"] in seen:
            rejected += 1
        else:
            accepted += 1
        seen.add(row["tag"])
    lines = ["trial import into the owner's maintenance system (a test copy)",
             f"  accepted {accepted}, rejected {rejected} (missing field, unknown",
             "  location or document, duplicate key)",
             "  the system accepts INV1 with its old drawing revision: an",
             "  import that 'works' is not a check - the revision rule is",
             "  ours to run before it (ch 38 revision rules)",
             "  then: search for three assets by tag, open their drawings,",
             "  raise a test work order, and delete the test copy"]
    emit("i_import", lines)
    return dict(accepted=accepted, rejected=rejected)


def restore() -> dict:
    r = src.RESTORE
    ok = r["measured_h"] <= r["rto_h"]
    lines = ["backup and restore test of the maintenance system and document store",
             f"  restored in {r['measured_h']} h against a recovery time objective of "
             f"{r['rto_h']:.0f} h - {'pass' if ok else 'FAIL'}",
             f"  data lost: {r['data_loss_h']:.0f} h",
             "  the restore that was never tried takes longest on the day it",
             "  is needed (ch 36 recovery); this one is repeated after the",
             "  restore procedure is fixed, and its time is recorded"]
    emit("i_restore", lines)
    return dict(ok=ok)


# ------------------------------------------------ J. emergency readiness
def readiness() -> dict:
    no_role = [k for k, v in src.ROLES.items() if v is None]
    stale = [(k, (src.TODAY - d).days) for k, d in src.CONTACTS.items()
             if (src.TODAY - d).days > src.CONTACT_MAX_DAYS]
    drills = [k for k, v in src.DRILLS.items() if not v]
    lines = [f"emergency readiness before operational handover ({src.TODAY})",
             f"  roles without a name: {', '.join(no_role)}",
             "  contacts not verified in the last "
             f"{src.CONTACT_MAX_DAYS} days:"]
    lines += [f"    {k}: {d} days" for k, d in stale]
    lines += [f"  drills not yet done: {', '.join(drills)}",
              "  the plant changes hands with its emergency plan working:",
              "  a night with no incident controller, a hospital number",
              "  nobody has rung since November and an untested night",
              "  casualty drill are three reasons to wait (ch 32)"]
    emit("j_ready", lines)
    return dict(no_role=no_role, stale=stale, drills=drills)


if __name__ == "__main__":
    show_rows()
    import_test()
    restore()
    readiness()
