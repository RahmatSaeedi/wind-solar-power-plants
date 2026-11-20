"""Compliance-register helpers (chapter 54).

Requirement records with their source type and status, a ranking of
source types, conflicts between sources on one parameter, applicability
by voltage, ownership and location, freshness of the verification and
supersession of editions, completeness of a requirement's trace,
clarification ageing, a status summary and the impact of an edition
change. Teaching helpers on plain data, not legal advice.
"""
from __future__ import annotations

from datetime import date

# [start: rank]
RANK = {"law": 1, "regulation": 2, "permit condition": 3, "grid code": 4,
        "utility rule": 5, "national standard": 6, "contract": 7,
        "owner specification": 8, "project procedure": 9}
STATUSES = ("verified", "project-dependent", "to-confirm")


def rank(source_type: str) -> int:
    """Lower is higher in the hierarchy (teaching order; the real order
    and any exceptions are a legal question for the jurisdiction)."""
    return RANK[source_type]
# [end: rank]


# [start: conflict]
def conflicts(reqs: list[dict], parameter: str) -> dict:
    """reqs: dicts with id, source_type, parameter, kind ('min'/'max'/
    'equal'), value. Returns the governing value for each kind - the
    strictest that every source allows - and the pairs that disagree."""
    rows = [r for r in reqs if r["parameter"] == parameter]
    mins = [r["value"] for r in rows if r["kind"] == "min"]
    maxs = [r["value"] for r in rows if r["kind"] == "max"]
    eqs = {r["value"] for r in rows if r["kind"] == "equal"}
    lo = max(mins) if mins else None
    hi = min(maxs) if maxs else None
    feasible = lo is None or hi is None or lo <= hi
    if eqs:
        feasible = feasible and len(eqs) == 1 and all(
            (lo is None or v >= lo) and (hi is None or v <= hi) for v in eqs)
    return dict(lo=lo, hi=hi, equal=sorted(eqs), feasible=feasible,
                sources=[r["id"] for r in rows])
# [end: conflict]


# [start: applies]
def applies(req: dict, project: dict) -> bool:
    """A requirement applies when the project's voltage, ownership,
    location and technology fall inside its stated scope (None = any)."""
    s = req.get("scope", {})
    v = project["voltage_kv"]
    if s.get("v_min") is not None and v < s["v_min"]:
        return False
    if s.get("v_max") is not None and v > s["v_max"]:
        return False
    for key in ("ownership", "location", "technology"):
        allowed = s.get(key)
        if allowed and project[key] not in allowed:
            return False
    return True
# [end: applies]


# [start: fresh]
def freshness(req: dict, today: date, max_days: int,
              current_edition: dict) -> list:
    """Problems with a requirement's source: verified too long ago, an
    edition other than the current one, or no official source."""
    out = []
    last = req.get("verified")
    if last is None or (today - last).days > max_days:
        out.append("verification stale")
    cur = current_edition.get(req["document"])
    if cur is not None and req.get("edition") != cur:
        out.append(f"edition {req.get('edition')} superseded by {cur}")
    if not req.get("official_source"):
        out.append("no official source")
    return out
# [end: fresh]


# [start: trace]
STAGES = ("source", "design", "procurement", "construction", "test",
          "approval", "retained")


def trace_gaps(trace: dict) -> list:
    """trace: stage -> evidence reference (or None). Returns the missing
    stages in order; a trace is closed when none is missing."""
    return [s for s in STAGES if not trace.get(s)]
# [end: trace]


# [start: consolidated]
def consolidated(clauses: dict, on: date) -> dict:
    """clauses: clause -> list of (in force from, issue, text), any order.
    Returns clause -> (issue, text) in force on the date: the base text
    with every amendment in force by then - never the base alone."""
    out = {}
    for cl, versions in clauses.items():
        live = [v for v in versions if v[0] <= on]
        if live:
            d, issue, text = max(live, key=lambda v: v[0])
            out[cl] = (issue, text)
    return out
# [end: consolidated]


# [start: diff]
def register_diff(old: dict, new: dict) -> dict:
    """old, new: requirement id -> dict of fields. Added, removed, and
    changed (id, field, old value, new value) between two revisions."""
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    changed = []
    for rid in sorted(set(old) & set(new)):
        for f in sorted(set(old[rid]) | set(new[rid])):
            a, b = old[rid].get(f), new[rid].get(f)
            if a != b:
                changed.append((rid, f, a, b))
    return dict(added=added, removed=removed, changed=changed)
# [end: diff]


def summary(reqs: list[dict]) -> dict:
    out = {s: 0 for s in STATUSES}
    for r in reqs:
        out[r["status"]] += 1
    return out


def clarification_ageing(requests: list[tuple], today: date,
                         limit: int) -> list:
    """requests: (id, sent date, answered date or None). Open ones older
    than limit days."""
    return [(i, (today - sent).days) for i, sent, ans in requests
            if ans is None and (today - sent).days > limit]


def edition_impact(links: dict, document: str) -> list:
    """links: requirement id -> (document, [design and test records]).
    Records to re-check when a document's edition changes."""
    out = []
    for rid, (doc, recs) in links.items():
        if doc == document:
            out += [(rid, r) for r in recs]
    return out
