"""Tests for plantp.control (chapter 20) against hand calculations."""
import math

import numpy as np
import pytest

from plantp import control as ct


def test_pi_reaches_setpoint_and_rate_limit():
    y, u = ct.pi_response(2.0, 1.0, 2.0, 0.01, 3000)
    assert y[-1] == pytest.approx(1.0, abs=1e-3)
    y2, u2 = ct.pi_response(2.0, 1.0, 2.0, 0.01, 200, rate=0.1)
    assert np.max(np.abs(np.diff(u2))) <= 0.1 * 0.01 + 1e-12


def test_rate_limit():
    x = ct.rate_limit([0, 10, 10, 10], 3.0)
    assert list(x) == [0, 3, 6, 9]


def test_droop():
    # 0.2 Hz high, 4 % droop, 100 MW, no deadband: -0.2/50/0.04*100 = -10 MW
    assert float(ct.droop_power(0.2, 100.0, 0.04)) == pytest.approx(-10.0)
    assert float(ct.droop_power(0.01, 100.0, 0.04, deadband_hz=0.02)) == 0.0
    assert float(ct.droop_reactive(0.10, 30.0, 0.04)) == pytest.approx(-30.0)


def test_q_limit_and_rooms():
    assert float(ct.q_limit(0.0, 10.0, 0.33)) == pytest.approx(3.3)
    assert float(ct.q_limit(10.0, 10.0, 0.33)) == pytest.approx(0.0)
    up, down = ct.soc_room(20.0, 4.0, 36.0, 0.9, 2.0)
    assert up == pytest.approx(16 * 0.9 / 2)
    assert down == pytest.approx(16 / 0.9 / 2)


def test_dp_schedule_respects_caps():
    price = np.array([10, 10, 50, 50], float)
    rev, e, p = ct.dp_schedule(price, [20, 20, 0, 0], [0, 0, 20, 20], 20.0,
                               0.0, 20.0, 0.0, 1.0, 1.0)
    assert rev == pytest.approx(20 * 50 - 20 * 10)
    assert (p[:2] <= 0).all() and (p[2:] >= 0).all()
    rev2, _, _ = ct.dp_schedule(price, [20, 20, 0, 0], [0, 0, 5, 5], 20.0,
                                0.0, 20.0, 0.0, 1.0, 1.0)
    assert rev2 == pytest.approx(10 * 50 - 10 * 10)



def test_dp_floor_holds_reserve():
    price = np.array([10, 50, 10, 50], float)
    rev, e, p = ct.dp_schedule(price, [20] * 4, [20] * 4, 20.0, 0.0, 20.0, 0.0,
                               1.0, 1.0)
    assert rev == pytest.approx(1600)
    rev2, e2, _ = ct.dp_schedule(price, [20] * 4, [20] * 4, 20.0, 0.0, 20.0,
                                 0.0, 1.0, 1.0, floor=[0, 10, 0, 0])
    assert rev2 == pytest.approx(1200)
    assert e2[1] >= 10 and e2[2] >= 10

def test_controller_limits_and_fallback():
    c = ct.Controller(e=4.0)
    r = c.step(0, 50.0, -30.0, None, True)               # charge request too big
    assert r["charge"] == pytest.approx(20.0)
    assert any("beyond rating" in a for _, a in c.alarms)
    r = c.step(1, 95.0, 20.0, None, True)                 # cap leaves 5 MW
    assert r["discharge"] == pytest.approx(5.0)
    c.step(2, 50.0, 10.0, None, False)
    r = c.step(3, 50.0, 10.0, None, False)                # timeout passed
    assert r["discharge"] == 0.0


def test_imbalance():
    assert ct.imbalance([10, 10], [8, 12], 30.0, 10.0) == pytest.approx(2 * 30 + 2 * 10)
