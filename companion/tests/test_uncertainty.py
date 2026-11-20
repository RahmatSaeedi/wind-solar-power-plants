"""Tests of plantp.uncertainty against hand calculations (chapter 2)."""
import math

import pytest

from plantp import uncertainty as un


def test_type_a_of_five_readings():
    r = un.type_a([7.02, 7.10, 7.05, 7.12, 7.06])
    assert r.mean == pytest.approx(7.07)
    assert r.s == pytest.approx(0.04, abs=1e-3)
    assert r.u_mean == pytest.approx(r.s / math.sqrt(5))
    assert r.dof == 4
    with pytest.raises(ValueError):
        un.type_a([1.0])


def test_type_b_distributions():
    assert un.rectangular(0.1) == pytest.approx(0.057735, rel=1e-5)
    assert un.triangular(0.6) == pytest.approx(0.6 / math.sqrt(6))
    assert un.from_expanded(0.04, 2) == pytest.approx(0.02)
    assert un.resolution(0.01) == pytest.approx(0.005 / math.sqrt(3))


def test_reading_spec():
    a, u = un.from_reading_spec(230.0, pct_of_reading=0.5, counts=2, count_size=0.1)
    assert a == pytest.approx(1.35)
    assert u == pytest.approx(1.35 / math.sqrt(3))


def test_combine_matches_power_law_for_wind_power_density():
    f = lambda rho, v: 0.5 * rho * v ** 3          # noqa: E731
    res = un.combine(f, {"rho": 1.055, "v": 7.10}, {"rho": 0.0105, "v": 0.142})
    rel = un.relative_power_law({"rho": 1, "v": 3}, {"rho": 0.0105 / 1.055, "v": 0.02})
    assert res.relative == pytest.approx(rel, rel=1e-6)
    assert res.rows[1].share > 0.95                 # the speed dominates
    assert res.y == pytest.approx(0.5 * 1.055 * 7.10 ** 3)


def test_combine_with_full_positive_correlation_adds_linearly():
    f = lambda a, b: a + b                          # noqa: E731
    res = un.combine(f, {"a": 1.0, "b": 2.0}, {"a": 0.3, "b": 0.4}, {("a", "b"): 1.0})
    assert res.u_c == pytest.approx(0.7)
    res0 = un.combine(f, {"a": 1.0, "b": 2.0}, {"a": 0.3, "b": 0.4})
    assert res0.u_c == pytest.approx(0.5)


def test_combine_requires_every_uncertainty():
    with pytest.raises(ValueError):
        un.combine(lambda a, b: a * b, {"a": 1.0, "b": 2.0}, {"a": 0.1})


def test_monte_carlo_agrees_with_linear_for_small_uncertainty():
    f = lambda rho, v: 0.5 * rho * v ** 3           # noqa: E731
    lin = un.combine(f, {"rho": 1.055, "v": 7.10}, {"rho": 0.0105, "v": 0.071})
    mc = un.monte_carlo(f, {"rho": ("normal", 1.055, 0.0105), "v": ("normal", 7.10, 0.071)})
    assert mc.std == pytest.approx(lin.u_c, rel=0.02)
    assert mc.low < lin.y < mc.high


def test_monte_carlo_is_reproducible_with_a_seed():
    f = lambda x: x ** 2                            # noqa: E731
    a = un.monte_carlo(f, {"x": ("uniform", 1.0, 0.5)}, n=1000)
    b = un.monte_carlo(f, {"x": ("uniform", 1.0, 0.5)}, n=1000)
    assert a.mean == b.mean
    with pytest.raises(ValueError):
        un.monte_carlo(f, {"x": ("lognormal", 1.0, 0.5)}, n=10)


def test_coverage_factor():
    assert un.coverage_factor(0.95) == pytest.approx(1.96, abs=0.005)
    assert un.coverage_factor(0.95, dof=4) == pytest.approx(2.776, abs=0.001)


def test_round_result():
    assert un.round_result(289.8123, 16.27) == ("290", "16")
    assert un.round_result(1.05463, 0.01234) == ("1.055", "0.012")
    assert un.round_result(2898.1, 162.7) == ("2900", "160")
    assert un.round_result(5.0, 0.0996) == ("5.00", "0.10")


def test_conformity_guarded_and_simple():
    d = un.conformity(98.4, 0.3, lower=98.5)
    assert d.verdict == "inconclusive"
    assert un.conformity(98.9, 0.3, lower=98.5).verdict == "accept"
    assert un.conformity(98.1, 0.3, lower=98.5).verdict == "reject"
    assert un.conformity(98.4, 0.3, lower=98.5, rule="simple").verdict == "reject"
    assert un.conformity(1.2, 0.1, upper=1.5).verdict == "accept"
    with pytest.raises(ValueError):
        un.conformity(1.0, 0.1)


def test_tolerance_stacks():
    tols = [0.5, 0.5, 0.5, 0.5]
    assert un.stack_worst_case(tols) == pytest.approx(2.0)
    assert un.stack_rss(tols) == pytest.approx(1.0)
