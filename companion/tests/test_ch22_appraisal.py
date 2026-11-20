"""Tests for plantp.appraisal (chapter 22) against hand calculations."""
import numpy as np
import pytest

from plantp import appraisal as ap


def test_fatal_flaws():
    opts = {"A": {"grid_km": 5}, "B": {"grid_km": 80}}
    out = ap.fatal_flaws(opts, {"grid too far": lambda f: f["grid_km"] > 50})
    assert out == {"A": [], "B": ["grid too far"]}


def test_normalise_and_weighted():
    assert list(ap.normalise([1, 2, 3])) == [0, 0.5, 1]
    assert list(ap.normalise([1, 2, 3], False)) == [1, 0.5, 0]
    s = [[1, 0], [0, 1]]
    assert list(ap.weighted(s, [3, 1])) == pytest.approx([0.75, 0.25])


def test_dominated():
    assert ap.dominated([[1, 1], [0.5, 1], [0, 0.2]]) == [1, 2]


def test_rank_stability_extreme():
    share = ap.rank_stability([[1, 1], [0, 0]], [0.5, 0.5], n=200)
    assert share[0] == 1.0


def test_quality_adjusted():
    assert float(ap.quality_adjusted(1.0, 0.0)) == pytest.approx(0.5)
    assert float(ap.quality_adjusted(1.0, 1.0)) == pytest.approx(1.0)


def test_critical_path():
    tasks = {"a": (3, []), "b": (2, ["a"]), "c": (4, ["a"]), "d": (1, ["b", "c"])}
    total, crit, slack = ap.critical_path(tasks)
    assert total == 8
    assert crit == ["a", "c", "d"]
    assert slack["b"] == 2


def test_risk_and_range():
    assert ap.risk_cost([(0.1, 100), (0.5, 10)]) == pytest.approx(15)
    assert ap.estimate_range(100, -0.3, 0.5) == pytest.approx((70, 150))
