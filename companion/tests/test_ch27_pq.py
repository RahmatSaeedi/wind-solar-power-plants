"""Tests for plantp.pq (chapter 27) against hand calculations."""
import math

import numpy as np
import pytest

from plantp import pq


def test_thd_tdd():
    h = {5: 3.0, 7: 4.0}
    assert pq.thd(h, 50.0) == pytest.approx(0.10)
    assert pq.tdd(h, 100.0) == pytest.approx(0.05)


def test_summation():
    assert pq.summation([1.0, 1.0, 1.0, 1.0], 1.0) == pytest.approx(4.0)
    assert pq.summation([1.0, 1.0, 1.0, 1.0], 2.0) == pytest.approx(2.0)


def test_tuned_filter():
    c_uf, l_mh, xc, xl = pq.tuned_filter(5.0, 4.7, 33.0)
    assert xc - xl == pytest.approx(33.0 ** 2 / 5.0)
    assert math.sqrt(xc / xl) == pytest.approx(4.7)
    assert 1 / (2 * math.pi * 50 * c_uf * 1e-6) == pytest.approx(xc)


def test_scan_resonance():
    h = np.arange(1, 40, 0.05)
    z = pq.scan(h, 365.0, 10.0, 5.0, 33.0)
    assert h[np.argmax(z)] == pytest.approx(math.sqrt(365 / 5), abs=0.2)


def test_step_metrics():
    t = np.linspace(0, 5, 501)
    y = 1 - np.exp(-t / 0.5)
    m = pq.step_metrics(t, y, 0.0, 1.0)
    assert m["rise"] == pytest.approx(0.5 * math.log(9), abs=0.02)
    assert m["settle"] == pytest.approx(0.5 * math.log(20), abs=0.02)
    assert m["overshoot"] == 0.0


def test_droop_and_ramp():
    df = np.array([-0.3, -0.2, 0.2, 0.3])
    dp = -(np.sign(df) * (np.abs(df) - 0.1)) / (50 * 0.04)
    assert pq.droop_fit(df, dp, 0.1) == pytest.approx(4.0)
    assert pq.ramp_exceedance(np.array([0, 5, 6, 20]), 10.0) == pytest.approx(1 / 3)


def test_voltage_change_and_aggregate():
    assert pq.voltage_change(0.0, 10.0, 1000.0, 1e9) == pytest.approx(0.01)
    agg = pq.aggregate(np.array([3.0, 4.0, 3.0, 4.0]), 2)
    assert agg[0] == pytest.approx(math.sqrt(12.5))
