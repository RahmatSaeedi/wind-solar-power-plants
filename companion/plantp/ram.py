"""Reliability, availability and maintainability helpers (chapter 52).

Availability types, series/parallel/k-out-of-n blocks, reliability block
diagrams as nested tuples, fault trees with minimal cut sets, a
beta-factor common-cause model, Weibull life, age-replacement cost rate,
inspection intervals from a P-F interval, Poisson spares, and a small
Monte Carlo of repairable blocks with spares and logistics delay.
Teaching models on plain data, not a substitute for a reliability study.
"""
from __future__ import annotations

import heapq
import itertools
import math

import numpy as np


# [start: avail]
def a_inherent(mtbf: float, mttr: float) -> float:
    """Corrective repair only: MTBF / (MTBF + MTTR)."""
    return mtbf / (mtbf + mttr)


def a_achieved(mtbm: float, m_active: float) -> float:
    """Preventive and corrective active maintenance, no delays."""
    return mtbm / (mtbm + m_active)


def a_operational(mtbm: float, mdt: float) -> float:
    """All down time: active work plus logistics and admin delays."""
    return mtbm / (mtbm + mdt)
# [end: avail]


# [start: blocks]
def series(values) -> float:
    return float(np.prod(list(values)))


def parallel(values) -> float:
    return 1.0 - float(np.prod([1.0 - v for v in values]))


def k_of_n(k: int, n: int, a: float) -> float:
    """At least k of n identical, independent units up."""
    return sum(math.comb(n, i) * a ** i * (1 - a) ** (n - i)
               for i in range(k, n + 1))
# [end: blocks]


# [start: rbd]
def rbd(node, value: dict) -> float:
    """node: a leaf name, ("s", [..]), ("p", [..]) or ("k", k, [..]);
    value: leaf name -> availability (or reliability). Independence is
    assumed between leaves; a shared cause must be its own leaf."""
    if isinstance(node, str):
        return value[node]
    kind = node[0]
    if kind == "s":
        return series(rbd(c, value) for c in node[1])
    if kind == "p":
        return parallel(rbd(c, value) for c in node[1])
    if kind == "k":
        k, kids = node[1], node[2]
        vals = [rbd(c, value) for c in kids]
        n = len(vals)
        tot = 0.0
        for up in itertools.product((0, 1), repeat=n):
            if sum(up) >= k:
                p = [v if u else 1 - v for u, v in zip(up, vals)]
                tot += float(np.prod(p))
        return tot
    raise ValueError(f"unknown node {kind!r}")
# [end: rbd]


# [start: tree]
def cut_sets(gate) -> list:
    """Minimal cut sets of a fault tree. gate: an event name,
    ("or", [..]) or ("and", [..])."""
    if isinstance(gate, str):
        return [frozenset([gate])]
    kind, kids = gate
    sets = [cut_sets(k) for k in kids]
    if kind == "or":
        out = [c for s in sets for c in s]
    elif kind == "and":
        out = [frozenset().union(*combo) for combo in itertools.product(*sets)]
    else:
        raise ValueError(kind)
    out = set(out)
    return sorted((c for c in out if not any(o < c for o in out)),
                  key=lambda c: (len(c), sorted(c)))


def top_rare(cuts, q: dict) -> float:
    """Rare-event approximation: sum over cut sets of the product of q."""
    return sum(float(np.prod([q[e] for e in c])) for c in cuts)


def top_exact(gate, q: dict) -> float:
    """Exact top probability by enumerating the basic events (small trees)."""
    events = sorted({e for c in cut_sets(gate) for e in c})

    def occurs(g, state):
        if isinstance(g, str):
            return state[g]
        kind, kids = g
        vals = [occurs(k, state) for k in kids]
        return any(vals) if kind == "or" else all(vals)

    tot = 0.0
    for bits in itertools.product((False, True), repeat=len(events)):
        state = dict(zip(events, bits))
        if occurs(gate, state):
            tot += float(np.prod([q[e] if b else 1 - q[e] for e, b in state.items()]))
    return tot
# [end: tree]


# [start: ccf]
def pair_with_ccf(q: float, beta: float) -> float:
    """Unavailability of a 1-out-of-2 pair when a share beta of each
    unit's unavailability is a cause common to both (beta-factor)."""
    return ((1 - beta) * q) ** 2 + beta * q
# [end: ccf]


# [start: weibull]
def w_reliability(t, beta: float, eta: float):
    return np.exp(-(np.asarray(t, float) / eta) ** beta)


def w_hazard(t, beta: float, eta: float):
    t = np.asarray(t, float)
    return beta / eta * (t / eta) ** (beta - 1)


def w_mean(beta: float, eta: float) -> float:
    return eta * math.gamma(1 + 1 / beta)
# [end: weibull]


# [start: age]
def age_replacement_rate(t_pm: float, beta: float, eta: float,
                         c_pm: float, c_fail: float, n: int = 2000) -> float:
    """Long-run cost per hour of replacing at age t_pm or at failure,
    whichever is first (renewal-reward)."""
    t = np.linspace(0, t_pm, n)
    r = w_reliability(t, beta, eta)
    dt = t[1] - t[0]
    cycle = float(dt * (r.sum() - 0.5 * (r[0] + r[-1])))
    rt = float(w_reliability(t_pm, beta, eta))
    return (c_pm * rt + c_fail * (1 - rt)) / cycle


def best_age(beta: float, eta: float, c_pm: float, c_fail: float,
             grid) -> tuple:
    rates = [(age_replacement_rate(t, beta, eta, c_pm, c_fail), t)
             for t in grid]
    return min(rates)
# [end: age]


# [start: pf]
def inspections_needed(p_detect: float, target: float) -> int:
    """Inspections inside the P-F interval so that a developing failure
    is caught with probability >= target."""
    return math.ceil(math.log(1 - target) / math.log(1 - p_detect))
# [end: pf]


# [start: spares]
def spares_needed(rate_per_h: float, lead_h: float, target: float) -> int:
    """Smallest stock s with P(demand in the lead time <= s) >= target."""
    m = rate_per_h * lead_h
    s, p, term = 0, math.exp(-m), math.exp(-m)
    while p < target:
        s += 1
        term *= m / s
        p += term
    return s
# [end: spares]


# [start: sim]
def simulate(blocks: dict, hours: float, seed: int = 1) -> dict:
    """Monte Carlo of independent repairable units.

    blocks: name -> dict(n units, mtbf h, repair_h median (lognormal,
    sigma 0.5), stock spares, lead_h restock or None when no part is
    needed). Each failure takes the first spare available and reorders
    one at once (one-for-one stock); with the shelf empty it waits for
    the next arrival. The failure clock does not stop while a unit is
    down (a small error while down time << MTBF). Returns per block the
    failures, the down unit-hours and the mean units down."""
    rng = np.random.default_rng(seed)
    out = {}
    for name, b in blocks.items():
        fails = []
        for _ in range(b["n"]):
            t = rng.exponential(b["mtbf"])
            while t < hours:
                fails.append(t)
                t += rng.exponential(b["mtbf"])
        shelf = [0.0] * b.get("stock", 0)          # times each spare is ready
        heapq.heapify(shelf)
        down_h = wait_h = 0.0
        for t in sorted(fails):
            wait = 0.0
            if b.get("lead_h") is not None:
                heapq.heappush(shelf, t + b["lead_h"])   # reorder now
                wait = max(0.0, heapq.heappop(shelf) - t)
            repair = float(rng.lognormal(math.log(b["repair_h"]), 0.5))
            down_h += min(wait + repair, hours - t)
            wait_h += min(wait, hours - t)
        out[name] = dict(failures=len(fails), down_h=down_h, wait_h=wait_h,
                         mean_down=down_h / hours)
    return out
# [end: sim]
