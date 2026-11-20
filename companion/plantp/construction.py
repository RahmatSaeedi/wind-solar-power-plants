"""Construction and installation helpers (chapter 49).

Work packages scheduled with crew limits and hold points, look-ahead
constraint checks, progress by rules of credit, productivity, completion by
subsystem, installation records checked against their tolerances, and
asset records reconciled with the design. Pure functions on plain data;
teaching models, not a scheduling product.
"""
from __future__ import annotations

import math


# [start: schedule]
def serial_schedule(tasks: dict, crews: dict[str, int],
                    rule: str = "earliest") -> dict:
    """tasks: name -> (days, [predecessors], crew type or None, hold days).
    A hold point adds an inspection wait after the task before any
    successor may start. Each step books one ready task: with rule
    "priority" the one with the longest path to the end; with rule
    "earliest" the one that can start first (ties by that path). A task
    starts when its predecessors are released and a crew of its type is
    free (crews are booked in order, gaps are not back-filled). Returns
    name -> (start, finish, release)."""
    succ = {t: [s for s, v in tasks.items() if t in v[1]] for t in tasks}
    tail: dict[str, float] = {}

    def path(t: str) -> float:                       # longest path to the end
        if t not in tail:
            d, _, _, hold = tasks[t]
            tail[t] = d + hold + max((path(s) for s in succ[t]), default=0.0)
        return tail[t]

    free = {c: [0.0] * n for c, n in crews.items()}  # each crew's free day
    out: dict[str, tuple[float, float, float]] = {}
    while len(out) < len(tasks):
        ready = [t for t, v in tasks.items()
                 if t not in out and all(p in out for p in v[1])]

        def can_start(t: str) -> float:
            s = max((out[p][2] for p in tasks[t][1]), default=0.0)
            c = tasks[t][2]
            return s if c is None else max(s, min(free[c]))

        if rule == "priority":
            t = max(ready, key=path)
        else:
            t = min(ready, key=lambda r: (can_start(r), -path(r)))
        d, pre, crew, hold = tasks[t]
        start = max((out[p][2] for p in pre), default=0.0)
        if crew is not None:
            k = min(range(len(free[crew])), key=lambda i: free[crew][i])
            start = max(start, free[crew][k])
            free[crew][k] = start + d
        out[t] = (start, start + d, start + d + hold)
    return out
# [end: schedule]


# [start: lookahead]
def lookahead(packages: dict, cleared: dict, start_by: dict, today: float,
              weeks: int = 6) -> dict:
    """packages: name -> [constraints]; cleared: constraint -> day cleared
    (None if not yet); start_by: name -> planned start day. A package in
    the look-ahead window is ready if every constraint is cleared on or
    before its start. Returns name -> list of open constraints."""
    out = {}
    for name, cons in packages.items():
        if today <= start_by[name] <= today + 7 * weeks:
            due = start_by[name]
            out[name] = [c for c in cons
                         if cleared.get(c) is None or cleared[c] > due]
    return out
# [end: lookahead]


# [start: credit]
def rules_of_credit(steps: dict[str, float], done: dict[str, float]) -> float:
    """Progress of one item: steps -> weight (summing to 1), done -> share
    of each step complete (0-1)."""
    assert abs(sum(steps.values()) - 1.0) < 1e-9
    return sum(w * min(1.0, done.get(s, 0.0)) for s, w in steps.items())
# [end: credit]


def productivity(quantity: float, crew_hours: float) -> float:
    """Units installed per crew-hour."""
    return quantity / crew_hours if crew_hours else float("nan")


# [start: completion]
def completion(items, required=("A", "B")) -> dict:
    """items: (subsystem, tag, {ITR category: done?}). Returns subsystem ->
    (items, share mechanically complete (all A), share fully checked)."""
    out: dict[str, list] = {}
    for sub, _, itr in items:
        r = out.setdefault(sub, [0, 0, 0])
        r[0] += 1
        r[1] += bool(itr.get("A"))
        r[2] += all(itr.get(c) for c in required)
    return {s: (n, a / n, b / n) for s, (n, a, b) in out.items()}
# [end: completion]


def out_of_tolerance(records, tol: float) -> list:
    """records: (id, measured, design). Ids off by more than tol, or with no
    measurement (None)."""
    return [i for i, m, d in records if m is None or abs(m - d) > tol]


def distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


# [start: assets]
def reconcile(design: dict, field: dict, fields) -> dict:
    """design and field: tag -> record dict. Returns missing tags (in
    design, not in field), extra tags, and (tag, field, design, found)
    for each mismatch."""
    missing = sorted(set(design) - set(field))
    extra = sorted(set(field) - set(design))
    wrong = [(t, f, design[t].get(f), field[t].get(f))
             for t in sorted(set(design) & set(field)) for f in fields
             if design[t].get(f) != field[t].get(f)]
    return dict(missing=missing, extra=extra, wrong=wrong)
# [end: assets]


def duplicates(values) -> list:
    seen, dup = set(), set()
    for v in values:
        if v in seen:
            dup.add(v)
        seen.add(v)
    return sorted(dup)
