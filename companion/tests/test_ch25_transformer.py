"""Tests for plantp.transformer (chapter 25) against hand calculations."""
import math

import pytest

from plantp import transformer as tr


def test_faraday():
    assert tr.volts_per_turn(1.7, 0.2) == pytest.approx(4.44 * 50 * 1.7 * 0.2)
    assert tr.turns(19053, 1.7, 0.2) == pytest.approx(19053 / 75.48, rel=1e-4)
    assert tr.conductor_mm2(1102, 3.0) == pytest.approx(367.33, rel=1e-4)


def test_equivalent_circuit():
    e = tr.from_tests(63000, 132, 35, 0.2, 250, 12)
    assert e["r"] == pytest.approx(250 / 63000)
    assert e["x"] == pytest.approx(math.sqrt(0.12 ** 2 - (250 / 63000) ** 2))
    assert e["g"] == pytest.approx(35 / 63000)


def test_regulation_and_efficiency():
    reg = tr.regulation_pct(0.01, 0.10, 1.0, 1.0)
    assert reg == pytest.approx(1.0 + 0 + (10 * 1 - 0) ** 2 / 200)
    eta = tr.efficiency(1.0, 1000, 1.0, 1.0, 10.0)
    assert eta == pytest.approx(1000 / 1011)


def test_capitalisation():
    a, b = tr.ab_factors(70, 25, 0.075, 0.3)
    af = (1 - 1.075 ** -25) / 0.075
    assert a == pytest.approx(70 * 8760 / 1e6 * af)
    assert b == pytest.approx(a * 0.3)
    assert tr.loss_cost(10, 100, a, b) == pytest.approx(10 * a + 100 * b)


def test_thermal_and_ageing():
    assert tr.hot_spot(1.0, 20) == pytest.approx(20 + 52 + 26)
    assert tr.ageing_rate(98) == pytest.approx(1.0)
    assert tr.ageing_rate(104) == pytest.approx(2.0)


def test_parallel_fault_sound_bund():
    s = tr.share(100, [63, 63], [0.12, 0.10])
    assert s[0] == pytest.approx(100 * (63 / 0.12) / (63 / 0.12 + 63 / 0.10))
    assert tr.sc_current_ka(63, 33, 0.12) == pytest.approx(63 / (math.sqrt(3) * 33 * 0.12))
    assert tr.force_ratio(0.1) == pytest.approx(100)
    assert tr.sound_sum([70, 70]) == pytest.approx(73.0103, rel=1e-4)
    assert tr.sound_at(70, 1, 10) == pytest.approx(50)
    assert tr.bund_m3(20, 50, 100) == pytest.approx(27.0)
