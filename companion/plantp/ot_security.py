"""Defensive OT-security arithmetic for chapter 36 (teaching tools only).

risk_score / risk_band   likelihood x consequence on 1-5 teaching scales
allowed                  is a flow listed in the conduit table?
covers / review_rules    rule-set review: any-any, shadowed, unused, undocumented
excess_rights            rights held beyond a role's allowed set
dormant                  accounts unused for longer than a limit
inventory_gaps           missing fields in an asset inventory
patch_exposure_days      days from a maker's fix to installation
log_volume_gb            storage of security logs
recovery_time_h          sum of the steps of a restore
series_availability      availability of a chain; single points of failure
entropy_bits             strength of a random secret (defensive sizing)
weighted_score           supplier scorecard

Nothing here touches a network or a device; inputs are synthetic tables.
"""
from __future__ import annotations

import math

ANY = "any"


def risk_score(likelihood: int, consequence: int) -> int:
    """Teaching risk score: likelihood (1-5) times consequence (1-5)."""
    if not (1 <= likelihood <= 5 and 1 <= consequence <= 5):
        raise ValueError("scales run from 1 to 5")
    return likelihood * consequence


def risk_band(score: int) -> str:
    """Teaching bands of the 1-25 score."""
    if score >= 15:
        return "very high"
    if score >= 10:
        return "high"
    if score >= 5:
        return "medium"
    return "low"


# [start: conduits]
def allowed(conduits, src: str, dst: str, service: str) -> bool:
    """True when a flow is listed in the conduit table (default deny)."""
    return any(c["src"] == src and c["dst"] == dst and c["service"] == service
               for c in conduits)
# [end: conduits]


# [start: rules]
FIELDS = ("src", "dst", "service")


def covers(a: dict, b: dict) -> bool:
    """Rule a matches every packet rule b matches."""
    return all(a[f] == ANY or a[f] == b[f] for f in FIELDS)


def review_rules(rules: list[dict]) -> dict[str, list[str]]:
    """Findings of a first-match rule set: any-any, shadowed, unused,
    undocumented. Each rule: id, src, dst, service, action, hits, purpose."""
    out = {"any-any": [], "shadowed": [], "unused": [], "undocumented": []}
    for i, r in enumerate(rules):
        if r["action"] == "allow" and sum(r[f] == ANY for f in FIELDS) >= 2:
            out["any-any"].append(r["id"])
        if any(covers(rules[j], r) for j in range(i)):
            out["shadowed"].append(r["id"])
        if r["hits"] == 0:
            out["unused"].append(r["id"])
        if not r.get("purpose"):
            out["undocumented"].append(r["id"])
    return out
# [end: rules]


def excess_rights(users: dict[str, tuple[str, set[str]]],
                  roles: dict[str, set[str]]) -> dict[str, set[str]]:
    """Rights each user holds beyond the set allowed for the role."""
    return {u: rights - roles[role] for u, (role, rights) in users.items()
            if rights - roles[role]}


def dormant(last_use_days: dict[str, int], limit: int = 90) -> list[str]:
    """Accounts not used for longer than limit days."""
    return sorted(u for u, d in last_use_days.items() if d > limit)


def inventory_gaps(items: list[dict], required: tuple[str, ...]) -> dict[str, int]:
    """How many inventory rows miss each required field."""
    return {f: sum(1 for it in items if not it.get(f)) for f in required}


def patch_exposure_days(test_days: float, window_days: float) -> tuple[float, float]:
    """Mean and worst days from a maker's fix to installation, when it is
    tested first and installed in the next maintenance window."""
    return test_days + window_days / 2, test_days + window_days


def log_volume_gb(events_per_day: float, bytes_each: int, days: int) -> float:
    """Storage of security logs kept for days (GB)."""
    return events_per_day * bytes_each * days / 1e9


def recovery_time_h(steps: dict[str, float]) -> float:
    """Recovery time as the sum of its steps (h)."""
    return sum(steps.values())


def series_availability(parts: dict[str, float]) -> tuple[float, list[str]]:
    """Availability of parts in series and the single points of failure
    (every part of a series chain is one)."""
    a = math.prod(parts.values())
    return a, sorted(parts)


def entropy_bits(alphabet: int, length: int) -> float:
    """Bits of a randomly chosen secret: length x log2(alphabet)."""
    return length * math.log2(alphabet)


def weighted_score(scores: dict[str, float], weights: dict[str, float]) -> float:
    """Supplier scorecard: weighted mean of 0-5 scores."""
    w = sum(weights.values())
    return sum(scores[k] * weights[k] for k in weights) / w
