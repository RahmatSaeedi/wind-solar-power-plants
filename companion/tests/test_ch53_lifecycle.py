"""Chapter 53 lifecycle helpers against hand calculations."""
import math

import numpy as np
import pytest

from plantp import lifecycle as lc


def test_option_pv_and_eac():
    # 100 now, 10 a year for 2 years at 10 %: 100 + 10/1.1 + 10/1.21
    assert lc.option_pv(100, 10, 0, 0, 2, 0.10) == pytest.approx(100 + 10 / 1.1 + 10 / 1.21)
    # lost energy is valued like a cost
    assert lc.option_pv(0, 0, 1, 50, 1, 0.10) == pytest.approx(50 / 1.1)
    # salvage reduces the cost
    assert lc.option_pv(0, 0, 0, 0, 1, 0.10, salvage=11) == pytest.approx(-10)
    # EAC of the annuity it came from returns the payment
    pv = 10 * (1 - 1.1 ** -5) / 0.1
    assert lc.eac(pv, 5, 0.10) == pytest.approx(10)


def test_remaining_life():
    # exponential (k = 1): no memory
    r = float(lc.conditional_reliability(1000, 500, 1.0, 1000))
    assert r == pytest.approx(math.exp(-0.5))
    assert lc.median_remaining(5000, 1.0, 1000) == pytest.approx(1000 * math.log(2))
    # wear-out: an old unit has less median life left than a new one
    assert lc.median_remaining(50_000, 2.5, 60_000) < lc.median_remaining(0, 2.5, 60_000)


def test_trend():
    b, h = lc.trend([0, 1, 2, 3, 4], [10, 9.5, 9, 8.5, 8])
    assert b == pytest.approx(-0.5)
    assert h == pytest.approx(0.0, abs=1e-9)


def test_sinking_fund():
    # payment p for 2 years at 10 % grows to p * 1.1 + p
    p = lc.sinking_fund(210, 2, 0.10)
    assert p * 1.1 + p == pytest.approx(210)


def test_waste_and_footprint():
    w = lc.waste_balance({"steel": (100, 0.9, 0.0, False), "oil": (10, 0.5, 0.0, True)})
    assert w["total"] == 110 and w["recycled"] == pytest.approx(95)
    assert w["landfill"] == pytest.approx(15) and w["hazardous"] == 10
    g = lc.footprint_mc({"a": (1000.0, 0.0001)}, 1_000_000.0, n=200)
    # 1000 t over 1,000,000 MWh = 1 g/kWh
    assert np.median(g) == pytest.approx(1.0, rel=1e-3)
