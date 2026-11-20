"""Document control and design-management arithmetic for chapter 38.

parse_id / id_ok         document numbers PLP-DIS-TYP-nnnn (scheme of chapter 2)
rev_ok                   letters before approval, numbers from approval on
transition_ok            allowed status changes
stale_references         links that point to an older revision than the current one
completeness             share of required metadata fields filled, and what is missing
mismatches               two registers of the same tags that disagree
rvtm                     requirements with design, verification and evidence links
impacted                 everything downstream of a change in a dependency graph
earned_value             SPI, CPI and estimate at completion
ageing                   open items by age bucket
detect_chance            chance a sample check finds at least one of k errors
handover_score           weighted acceptance score of a handover package

All teaching tools; the project's own procedures decide the rules.
"""
from __future__ import annotations

import math
import re
from collections import deque

# [start: scheme]
DISCIPLINES = {"GEN", "ELE", "CIV", "MEC", "CTL", "ENV", "PRJ"}
TYPES = {"CAL", "DWG", "SPC", "REP", "REG", "PRO", "LST"}
PRE = {"WIP", "IFR", "IFI", "IFA"}               # revisions A, B, C ...
POST = {"APP", "IFC", "ASB"}                     # revisions 0, 1, 2 ...
ALLOWED = {"WIP": {"IFR", "IFI"}, "IFR": {"WIP", "IFA", "IFI"},
           "IFI": {"WIP", "IFR"}, "IFA": {"WIP", "APP"},
           "APP": {"IFC", "WIP"}, "IFC": {"ASB", "WIP"}, "ASB": {"WIP"}}
_ID = re.compile(r"^PLP-([A-Z]{3})-([A-Z]{3})-(\d{4})$")


def parse_id(doc_id: str) -> dict | None:
    m = _ID.match(doc_id)
    if not m:
        return None
    return {"discipline": m.group(1), "type": m.group(2),
            "number": int(m.group(3))}


def id_ok(doc_id: str) -> bool:
    p = parse_id(doc_id)
    return bool(p) and p["discipline"] in DISCIPLINES and p["type"] in TYPES


def rev_ok(rev: str, status: str) -> bool:
    """Letters (A, B ...) before approval, numbers (0, 1 ...) from it on;
    a superseded document keeps the revision it had."""
    if status == "SUP":
        return rev.isalpha() or rev.isdigit()
    if status in PRE:
        return rev.isalpha() and rev.isupper()
    return rev.isdigit()


def transition_ok(old: str, new: str) -> bool:
    """Allowed status changes; any document may become SUP (superseded)."""
    return new == "SUP" or new in ALLOWED.get(old, set())
# [end: scheme]


# [start: links]
def stale_references(current: dict[str, str], refs) -> list[tuple]:
    """refs: (from_id, to_id, rev_used). Returns the links whose revision
    is not the current one of the document they point to, or whose
    target is missing from the register."""
    out = []
    for src, dst, rev in refs:
        cur = current.get(dst)
        if cur is None or cur != rev:
            out.append((src, dst, rev, cur))
    return out


def completeness(records, required) -> tuple[float, dict]:
    """Share of required fields filled over all records, and the missing
    fields per record id."""
    missing, filled, total = {}, 0, 0
    for r in records:
        gaps = [f for f in required if r.get(f) in (None, "", [])]
        filled += len(required) - len(gaps)
        total += len(required)
        if gaps:
            missing[r["id"]] = gaps
    return (filled / total if total else 1.0), missing


def mismatches(a: dict, b: dict, fields, rel_tol: float = 0.0) -> list[tuple]:
    """Compare two registers keyed by tag: (tag, field, a value, b value)
    for tags in one only, and fields that differ (numbers within rel_tol
    count as equal)."""
    out = []
    for tag in sorted(set(a) | set(b)):
        if tag not in a or tag not in b:
            out.append((tag, "missing", tag in a, tag in b))
            continue
        for f in fields:
            x, y = a[tag].get(f), b[tag].get(f)
            if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                if not math.isclose(x, y, rel_tol=rel_tol, abs_tol=0.0):
                    out.append((tag, f, x, y))
            elif x != y:
                out.append((tag, f, x, y))
    return out
# [end: links]


# [start: rvtm]
def rvtm(requirements, design, verification, evidence) -> dict:
    """Each argument after the first maps a requirement id to its links.
    Returns per requirement which stages exist, and the coverage shares."""
    rows = {}
    for r in requirements:
        rows[r] = {"design": bool(design.get(r)),
                   "verification": bool(verification.get(r)),
                   "evidence": bool(evidence.get(r))}
    n = max(len(rows), 1)
    share = {k: sum(v[k] for v in rows.values()) / n
             for k in ("design", "verification", "evidence")}
    return {"rows": rows, "share": share}


def impacted(graph: dict[str, list[str]], start: str) -> list[str]:
    """Everything reachable downstream of `start` (breadth first), in the
    order found; graph maps an item to the items that depend on it."""
    seen, order, q = {start}, [], deque([start])
    while q:
        node = q.popleft()
        for nxt in graph.get(node, []):
            if nxt not in seen:
                seen.add(nxt)
                order.append(nxt)
                q.append(nxt)
    return order
# [end: rvtm]


# [start: controls]
def earned_value(pv: float, ev: float, ac: float, bac: float) -> dict:
    """Schedule and cost performance of engineering hours: SPI = EV/PV,
    CPI = EV/AC, estimate at completion = BAC/CPI."""
    spi, cpi = ev / pv, ev / ac
    return {"spi": spi, "cpi": cpi, "eac": bac / cpi, "vac": bac - bac / cpi}


def ageing(open_days, edges=(7, 14, 30, 60)) -> dict[str, int]:
    """Open items by age bucket (days)."""
    out, lo = {}, 0
    for e in edges:
        out[f"{lo}-{e}"] = sum(1 for d in open_days if lo <= d < e)
        lo = e
    out[f">={lo}"] = sum(1 for d in open_days if d >= lo)
    return out


def detect_chance(n_items: int, k_errors: int, sample: int) -> float:
    """Chance that checking `sample` of n_items (without replacement)
    finds at least one of k_errors (hypergeometric)."""
    if k_errors <= 0:
        return 0.0
    if sample >= n_items:
        return 1.0
    miss = math.comb(n_items - k_errors, sample) / math.comb(n_items, sample)
    return 1.0 - miss


def handover_score(items: dict[str, tuple[float, float]]) -> float:
    """items: name -> (weight, share complete 0..1). Weighted score."""
    w = sum(v[0] for v in items.values())
    return sum(v[0] * v[1] for v in items.values()) / w
# [end: controls]
