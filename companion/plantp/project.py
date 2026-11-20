"""Project-management calculations used from chapter 1 on: critical path,
spending S-curve, risk scoring.

Teaching implementations: small, readable, tested against hand calculations.
Professional schedules use dedicated scheduling software (chapters 22, 38, 49).
"""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class Activity:
    name: str
    duration: float                 # months (any consistent unit)
    predecessors: tuple[str, ...] = ()


@dataclass
class ScheduleResult:
    early_start: dict[str, float]
    early_finish: dict[str, float]
    late_start: dict[str, float]
    late_finish: dict[str, float]
    total_float: dict[str, float]
    project_duration: float
    critical_path: list[str]


def _topological_order(activities: dict[str, Activity]) -> list[str]:
    order, done, visiting = [], set(), set()

    def visit(name: str) -> None:
        if name in done:
            return
        if name in visiting:
            raise ValueError(f"the network has a loop through {name!r}")
        if name not in activities:
            raise ValueError(f"unknown predecessor {name!r}")
        visiting.add(name)
        for p in activities[name].predecessors:
            visit(p)
        visiting.discard(name)
        done.add(name)
        order.append(name)

    for name in activities:
        visit(name)
    return order


def critical_path(activity_list: list[Activity]) -> ScheduleResult:
    """Critical-path method: forward pass for earliest dates, backward pass for
    latest dates; total float = late start - early start; zero float = critical."""
    acts = {a.name: a for a in activity_list}
    if len(acts) != len(activity_list):
        raise ValueError("activity names must be unique")
    if any(a.duration < 0 for a in activity_list):
        raise ValueError("durations cannot be negative")
    order = _topological_order(acts)
    es, ef = {}, {}
    for n in order:
        es[n] = max((ef[p] for p in acts[n].predecessors), default=0.0)
        ef[n] = es[n] + acts[n].duration
    total = max(ef.values())
    successors = {n: [m for m in order if n in acts[m].predecessors] for n in order}
    ls, lf = {}, {}
    for n in reversed(order):
        lf[n] = min((ls[s] for s in successors[n]), default=total)
        ls[n] = lf[n] - acts[n].duration
    tf = {n: ls[n] - es[n] for n in order}
    path, current = [], None
    starts = [n for n in order if not acts[n].predecessors and abs(tf[n]) < 1e-9]
    current = starts[0] if starts else None
    while current is not None:
        path.append(current)
        nxt = [s for s in successors[current] if abs(tf[s]) < 1e-9 and abs(es[s] - ef[current]) < 1e-9]
        current = nxt[0] if nxt else None
    return ScheduleResult(es, ef, ls, lf, tf, total, path)


def s_curve(t, start: float, duration: float, steepness: float = 10.0) -> float:
    """Cumulative fraction (0..1) of a spend that runs from start to start+duration,
    shaped as a normalised logistic curve (slow start, fast middle, slow end)."""
    if duration <= 0:
        raise ValueError("duration must be positive")
    if t <= start:
        return 0.0
    if t >= start + duration:
        return 1.0
    x = (t - start) / duration

    def f(u):
        return 1.0 / (1.0 + math.exp(-steepness * (u - 0.5)))

    return (f(x) - f(0.0)) / (f(1.0) - f(0.0))


def risk_score(likelihood: int, impact: int) -> int:
    """Product score on 1..5 scales; a teaching convention, not a standard."""
    if not (1 <= likelihood <= 5 and 1 <= impact <= 5):
        raise ValueError("likelihood and impact must be 1..5")
    return likelihood * impact


def risk_band(score: int) -> str:
    """Bands used in chapter 1 (an assumption the project would set for itself)."""
    if score >= 15:
        return "high"
    if score >= 8:
        return "medium"
    return "low"
