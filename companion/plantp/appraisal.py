"""Feasibility and option appraisal (chapter 22): fatal-flaw screening,
normalised weighted scores, dominance, rank stability under uncertain
weights, evidence-quality adjusted scores, expected values, the critical
path of a development plan, a risk register's expected cost, and cost
estimate ranges by maturity.

All weights, scores, probabilities and ranges are teaching values; a
real appraisal records who set each one and on what evidence.
"""
from __future__ import annotations

import numpy as np


# [start: screen]
def fatal_flaws(options: dict, tests: dict) -> dict:
    """options: name -> dict of facts; tests: name -> function(facts)
    returning True when the option fails the test. Returns name -> list
    of failed tests (empty list = passes)."""
    return {o: [t for t, f in tests.items() if f(facts)]
            for o, facts in options.items()}
# [end: screen]


# [start: score]
def normalise(values, higher_is_better: bool = True) -> np.ndarray:
    """Min-max scale to 0..1 (1 = best); equal values give 1."""
    v = np.asarray(values, float)
    lo, hi = v.min(), v.max()
    if hi - lo < 1e-12:
        return np.ones_like(v)
    s = (v - lo) / (hi - lo)
    return s if higher_is_better else 1.0 - s


def weighted(scores, weights) -> np.ndarray:
    """scores: options x criteria (0..1); weights summing to 1."""
    w = np.asarray(weights, float)
    return np.asarray(scores, float) @ (w / w.sum())


def dominated(scores) -> list[int]:
    """Indices of options no better than another in every criterion and
    worse in at least one."""
    s = np.asarray(scores, float)
    out = []
    for i in range(len(s)):
        for j in range(len(s)):
            if i != j and (s[j] >= s[i]).all() and (s[j] > s[i]).any():
                out.append(i)
                break
    return out
# [end: score]


def rank_stability(scores, weights, spread: float = 20.0, n: int = 5000,
                   seed: int = 22) -> np.ndarray:
    """Share of random weight sets (Dirichlet around the given weights,
    concentration 'spread' per unit weight) in which each option ranks
    first."""
    rng = np.random.default_rng(seed)
    w0 = np.asarray(weights, float) / np.sum(weights)
    wins = np.zeros(len(scores))
    for w in rng.dirichlet(w0 * spread, n):
        wins[int(np.argmax(weighted(scores, w)))] += 1
    return wins / n


def quality_adjusted(score, quality, floor: float = 0.5):
    """Shrink a 0..1 score toward the middle (0.5) when its evidence is
    weak: quality 1 keeps it, quality 0 gives 0.5 (teaching rule)."""
    q = np.clip(np.asarray(quality, float), 0, 1)
    return floor + q * (np.asarray(score, float) - floor)


# [start: cpm]
def critical_path(tasks: dict) -> tuple[float, list[str], dict]:
    """tasks: name -> (duration, [predecessors]). Forward pass for the
    earliest finish, backward pass for slack; returns (duration, the
    critical tasks in order, slack by task)."""
    order, done = [], set()
    while len(order) < len(tasks):
        for t, (_, pre) in tasks.items():
            if t not in done and all(p in done for p in pre):
                order.append(t)
                done.add(t)
    ef = {}
    for t in order:
        d, pre = tasks[t]
        ef[t] = d + max((ef[p] for p in pre), default=0.0)
    total = max(ef.values())
    lf = {t: total for t in tasks}
    for t in reversed(order):
        for s, (_, pre) in tasks.items():
            if t in pre:
                lf[t] = min(lf[t], lf[s] - tasks[s][0])
    slack = {t: lf[t] - ef[t] for t in tasks}
    crit = [t for t in order if abs(slack[t]) < 1e-9]
    return total, crit, slack
# [end: cpm]


def risk_cost(register) -> float:
    """Expected cost of a register of (probability, impact) pairs."""
    return float(sum(p * c for p, c in register))


def estimate_range(base: float, low: float, high: float) -> tuple[float, float]:
    """Cost range for an estimate class given its accuracy bounds
    (e.g. low -0.3, high +0.5 for an early screening estimate)."""
    return base * (1 + low), base * (1 + high)
