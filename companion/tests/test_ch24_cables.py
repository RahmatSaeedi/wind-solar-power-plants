"""Tests for plantp.cables (chapter 24) against hand calculations."""
import math

import pytest

from plantp import cables as cb


def test_resistance_and_rating():
    assert cb.r_at(0.125, 90) == pytest.approx(0.125 * (1 + 0.00393 * 70))
    i, k = cb.rating(400, {"depth": 0.97, "soil": 0.9, "group": 0.8})
    assert k == pytest.approx(0.6984) and i == pytest.approx(279.36)


def test_drop_and_loss():
    d = cb.drop_pct(100, 2.0, 0.2, 0.1, 1.0, 33)
    assert d == pytest.approx(math.sqrt(3) * 100 * 2 * 0.2 / 33e3 * 100)
    assert cb.loss_kw(100, 0.2, 2.0) == pytest.approx(12.0)
    assert cb.annual_loss_mwh([100] * 10, 0.2, 2.0) == pytest.approx(0.12)


def test_fault_duties():
    assert cb.adiabatic_mm2(20, 1.0, 143) == pytest.approx(139.86, rel=1e-4)
    assert cb.withstand_ka(240, 1.0, 94) == pytest.approx(22.56)
    assert cb.peak_ka(10, 1e9) == pytest.approx(2.0 * math.sqrt(2) * 10, rel=1e-6)
    assert cb.short_time_ok(20, 1.0, 25, 1.0)
    assert not cb.short_time_ok(20, 3.0, 25, 1.0)


def test_cable_effects():
    ic = cb.charging_a(33, 0.25, 10)
    assert ic == pytest.approx(33e3 / math.sqrt(3) * 2 * math.pi * 50 * 2.5e-6)
    e = cb.sheath_v(400, 70, 35, 500)
    assert e == pytest.approx(2 * math.pi * 50 * 2e-7 * math.log(4) * 400 * 500)
    assert cb.conductor_temp(400, 1e-4, 20, 2.5) == pytest.approx(60)
    assert cb.sag_m(10, 300, 20_000) == pytest.approx(5.625)


def test_economic_section():
    out = cb.economic_section([(240, 0.16, 100.0), (400, 0.10, 150.0)],
                              [200] * 8760, 1.0, 70, 25, 0.075)
    e240 = 3 * 200 ** 2 * 0.16 * 8760 / 1e6
    af = (1 - 1.075 ** -25) / 0.075
    assert out[0][2] == pytest.approx(e240)
    assert out[0][3] == pytest.approx(100 + e240 * 0.070 * af)
