"""Hand-calculated reference cases for plantp.civil (chapter 29)."""
import math

import pytest

from plantp import civil as cv


def test_refraction_depth():
    assert cv.refraction_depth(30, 500, 2000) == pytest.approx(15 * math.sqrt(1500 / 2500))
    with pytest.raises(ValueError):
        cv.refraction_depth(30, 2000, 500)


def test_bearing_factors_at_30_degrees():
    nc, nq, ng = cv.bearing_factors(30)
    assert nq == pytest.approx(18.40, abs=0.01)
    assert nc == pytest.approx(30.14, abs=0.01)
    assert ng == pytest.approx(22.40, abs=0.01)


def test_bearing_square_sand():
    q = cv.bearing_square(0.0, 30, 18.0, 2.0, 1.0)
    assert q == pytest.approx(18 * 18.40 + 0.4 * 18 * 2 * 22.40, rel=1e-3)


def test_settlement_and_spread():
    assert cv.elastic_settlement(200, 2.0, 20000, 0.3, 1.0) == pytest.approx(0.0182)
    assert cv.spread_pressure(1000, 1, 1, 1) == pytest.approx(250)


def test_rational_and_manning():
    assert cv.rational_peak(0.5, 50, 1.0) == pytest.approx(6.95)
    assert cv.manning_q(0.015, 0.5, 2.0, 0.01) == pytest.approx(1.323, abs=1e-3)
    d = 0.6
    assert cv.pipe_full_q(0.013, d, 0.01) == pytest.approx(
        math.pi * d * d / 4 * (d / 4) ** (2 / 3) * 0.1 / 0.013)


def test_kirpich_and_usle():
    assert cv.kirpich_tc(1000, 0.01) == pytest.approx(0.0195 * 1000 ** 0.77 * 0.01 ** -0.385)
    assert cv.usle(100, 0.3, 1.0, 0.1, 1.0) == pytest.approx(3.0)
    assert cv.ls_factor(22.13, 9.0) == pytest.approx(1.0, abs=0.06)


def test_acceptance():
    ok, m = cv.lot_accept([96, 98, 97, 99], 95, k=1.0)
    assert ok and m == pytest.approx(97.5 - 1.2910, abs=1e-3)
    assert cv.characteristic([30, 30, 30, 30.0001], 1.645) == pytest.approx(30, abs=1e-3)


def test_wells_and_returns():
    s = cv.cooper_jacob(0.005, 0.001, 1e-4, 10, 86400)
    assert s == pytest.approx(0.005 / (4 * math.pi * 0.001) * math.log(2.25 * 0.001 * 86400 / (100 * 1e-4)))
    assert cv.trench_inflow(1e-5, 3, 1, 20) == pytest.approx(1e-5 * 8 / 40)
    assert cv.gumbel_return(10, 2, 100) == pytest.approx(10 + 2 * 4.6001, abs=1e-3)
