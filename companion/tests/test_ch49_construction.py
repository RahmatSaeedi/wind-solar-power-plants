"""Tests for plantp.construction (chapter 49): hand-checked cases and edges."""
from __future__ import annotations

import math

import pytest

from plantp import construction as con


def test_schedule_chain_and_hold():
    tasks = {"a": (2, [], "x", 1), "b": (3, ["a"], "x", 0)}
    out = con.serial_schedule(tasks, {"x": 1})
    assert out["a"] == (0, 2, 3)
    assert out["b"] == (3, 6, 6)          # waits for the hold, not just the finish


def test_schedule_crew_limit_and_rules():
    # c is ready at 0 but shares a crew with a; b is long and only follows a
    tasks = {"a": (2, [], "x", 0), "b": (10, ["a"], None, 0), "c": (1, [], "x", 0)}
    out = con.serial_schedule(tasks, {"x": 1})
    assert max(v[2] for v in out.values()) == 12
    two = con.serial_schedule(tasks, {"x": 2})
    assert two["c"][0] == 0 and two["a"][0] == 0


def test_schedule_priority_can_be_later():
    # the priority rule books the long-tail task first and leaves a gap unused
    tasks = {"s": (1, [], None, 0), "t": (5, ["s"], None, 0),
             "e": (1, ["s"], "x", 0), "l": (2, ["t"], "x", 0), "m": (1, ["e"], None, 0)}
    early = con.serial_schedule(tasks, {"x": 1}, rule="earliest")
    prio = con.serial_schedule(tasks, {"x": 1}, rule="priority")
    assert early["e"][0] == 1
    assert max(v[2] for v in prio.values()) >= max(v[2] for v in early.values())


def test_lookahead_window_and_dates():
    pk = {"p": ["c1", "c2"], "q": ["c3"], "far": ["c4"]}
    cleared = {"c1": 5, "c2": None, "c3": 12, "c4": 1}
    start = {"p": 10, "q": 11, "far": 100}
    out = con.lookahead(pk, cleared, start, today=0, weeks=6)
    assert out["p"] == ["c2"] and out["q"] == ["c3"] and "far" not in out


def test_rules_of_credit():
    steps = {"a": 0.5, "b": 0.5}
    assert con.rules_of_credit(steps, {"a": 1.0, "b": 0.5}) == pytest.approx(0.75)
    assert con.rules_of_credit(steps, {"a": 2.0}) == pytest.approx(0.5)   # capped
    with pytest.raises(AssertionError):
        con.rules_of_credit({"a": 0.6}, {})


def test_completion_and_reconcile():
    items = [("S", "t1", {"A": True, "B": True}), ("S", "t2", {"A": True})]
    assert con.completion(items)["S"] == (2, 1.0, 0.5)
    r = con.reconcile({"x": {"k": 1}, "y": {"k": 2}}, {"x": {"k": 1}, "z": {"k": 3}}, ["k"])
    assert r["missing"] == ["y"] and r["extra"] == ["z"] and r["wrong"] == []
    assert con.duplicates(["a", "b", "a"]) == ["a"]
    assert con.out_of_tolerance([("p", 5, 0), ("q", None, 0), ("r", 1, 0)], 2) == ["p", "q"]
    assert con.distance((0, 0), (3, 4)) == 5
    assert math.isnan(con.productivity(10, 0))
