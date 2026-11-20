"""Chapter 38, lesson A (design maturity and deliverables): the master
document register checked against the numbering, revision and status
scheme of chapter 2, its metadata, the illegal status changes, and the
maturity of the design by discipline at week 40.

Run from the project root:   python -m companion.ch38.examples_a
Writes companion/ch38/expected/a_*.txt and diagrams/data/ch38-*.csv.
Synthetic register (A-417).
"""
from __future__ import annotations

from collections import Counter

from companion.ch38 import sources as src
from companion.ch38.common import csv, emit
from plantp import docctl as dc


def register_checks() -> None:
    docs = src.DOCS
    bad_id = [d["id"] for d in docs if not dc.id_ok(d["id"])]
    bad_rev = [(d["id"], d["rev"], d["status"]) for d in docs
               if not dc.rev_ok(d["rev"], d["status"])]
    no_check = [d["id"] for d in docs
                if d["status"] in ("APP", "IFC") and not d["approved_by"]]
    share, missing = dc.completeness(docs, ["owner"])
    lines = [f"the master document register at week {src.STATUS_DATE_WEEK}: {len(docs)} deliverables",
             f"  numbers outside the scheme: {len(bad_id)} - " + ", ".join(bad_id),
             f"  revision that does not fit the status: {len(bad_rev)}"]
    for i, r, s in bad_rev:
        lines.append(f"    {i}  rev {r} with status {s}")
    lines += [f"  approved or issued without a checker's name: {len(no_check)} - "
              + ", ".join(no_check),
              f"  documents without an owner: {len(missing)}",
              "  each finding goes back to its owner with a date; a register",
              "  that is not checked drifts from the documents it lists,",
              "  and the drawing a builder uses is the one in the register"]
    emit("a_register", lines)


def illegal_transitions() -> None:
    lines = ["status histories in the common data environment (A-417)"]
    for doc, hist in src.HISTORY.items():
        bad = [(a, b) for a, b in zip(hist, hist[1:]) if not dc.transition_ok(a, b)]
        flag = "  <- " + ", ".join(f"{a} to {b}" for a, b in bad) if bad else ""
        lines.append(f"  {doc}: " + " > ".join(hist) + flag)
    lines += ["  a calculation that went from review straight to 'for",
              "  construction' was never approved; a drawing issued 'for",
              "  information' was then built from. The workflow tool",
              "  blocks both - a register on paper does not"]
    emit("a_transitions", lines)


def maturity() -> None:
    docs = [d for d in src.DOCS if dc.id_ok(d["id"])]
    by = {}
    for d in docs:
        dis = d["id"][4:7]
        by.setdefault(dis, Counter())[d["status"]] += 1
    lines = [f"design maturity by discipline at week {src.STATUS_DATE_WEEK} (counts)",
             "  discipline   WIP   IFR   IFA   APP   IFC   share IFC"]
    rows = []
    for i, (dis, c) in enumerate(sorted(by.items())):
        n = sum(c.values())
        rows.append((i, c["WIP"], c["IFR"], c["IFA"] + c["APP"], c["IFC"]))
        lines.append(f"  {dis:10s} {c['WIP']:5d} {c['IFR']:5d} {c['IFA']:5d} {c['APP']:5d}"
                     f" {c['IFC']:5d}   {c['IFC'] / n * 100:8.0f} %")
    csv("ch38-maturity.csv", "i,wip,ifr,ifa,ifc", rows)
    late = [d for d in docs if d["planned_week"] < src.STATUS_DATE_WEEK
            and d["status"] in ("WIP", "IFR")]
    lines += [f"  planned before week {src.STATUS_DATE_WEEK} but still WIP or IFR: {len(late)}",
              "  maturity is read from the statuses, not from the hours",
              "  spent; a discipline with many documents in review is",
              "  waiting for comments, one with many in WIP has not",
              "  started - two different problems with two cures"]
    emit("a_maturity", lines)


def review_cycles() -> None:
    rows = [("approved at the first review", 0.55),
            ("approved by the second review", 0.80),
            ("approved by the third review", 0.97)]
    days_cycle = 14
    lines = ["review cycles of a drawing (teaching shares)",
             "  cycle                                    share done   days"]
    for k, (name, share) in enumerate(rows, start=1):
        lines.append(f"  {name:40s} {share * 100:8.0f} %   {k * days_cycle:4d}")
    mean = sum((k + 1) * days_cycle * (b - a) for k, (a, b) in
               enumerate(zip([0.0] + [r[1] for r in rows][:-1], [r[1] for r in rows])))
    lines += [f"  mean time to approval of those approved in three cycles:"
              f" {mean / 0.97:.0f} days",
              "  a schedule that allows one review cycle for every",
              "  drawing is late by design; the plan allows two, and the",
              "  comment sheet records each comment with its reply"]
    emit("a_reviews", lines)


if __name__ == "__main__":
    register_checks()
    illegal_transitions()
    maturity()
    review_cycles()
