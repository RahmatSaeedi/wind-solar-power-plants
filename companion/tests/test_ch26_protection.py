"""Tests for plantp.protection (chapter 26) against hand calculations."""
import math

import pytest

from plantp import protection as pr


def test_fault_currents():
    f = pr.fault_currents(19053, 2j, 2j, 2j)
    assert f["3ph"] == pytest.approx(19053 / 2)
    assert f["LL"] == pytest.approx(math.sqrt(3) * 19053 / 4)
    assert f["SLG"] == pytest.approx(3 * 19053 / 6)
    g = pr.fault_currents(19053, 2j, 2j, 2j, zf=47.6)
    assert g["SLG"] == pytest.approx(3 * 19053 / abs(6j + 142.8))


def test_idmt_and_grading():
    t = pr.trip_time(2000, 400, 0.1)
    assert t == pytest.approx(0.1 * 0.14 / (5 ** 0.02 - 1))
    assert pr.trip_time(300, 400, 0.1) == math.inf
    assert pr.trip_time(4000, 400, 1.0, "very inverse") == pytest.approx(13.5 / 9)
    assert pr.grading_ok(0.4, 0.75) and not pr.grading_ok(0.4, 0.6)


def test_ct_diff_distance():
    assert pr.ct_knee_ok(200, 20, 2.0, 1.0)          # 200 >= 2*20*3 = 120
    assert not pr.ct_knee_ok(100, 20, 2.0, 1.0)
    assert not pr.diff_trips(1.0, -1.0)              # through current
    assert pr.diff_trips(1.0, 0.0)                   # internal fault
    z = pr.distance_zones(10, 4)
    assert z == {"Z1": 8.0, "Z2": 12.0, "Z3": pytest.approx(14.8)}


def test_sequence_and_settings():
    ia, ib, ic = pr.phasor(1, 0), pr.phasor(1, -120), pr.phasor(1, 120)
    i0, i1, i2 = pr.sequence(ia, ib, ic)
    assert abs(i0) < 1e-12 and abs(i1) == pytest.approx(1) and abs(i2) < 1e-12
    i0, i1, i2 = pr.sequence(3, 0, 0)          # single-phase current
    assert abs(i0) == abs(i1) == abs(i2) == pytest.approx(1)
    lo, hi, ok = pr.pickup_window(300, 3000)
    assert (lo, hi, ok) == (360, 2000, True)
    tms = pr.tms_for(0.5, 4000, 450)
    assert pr.trip_time(4000, 450, tms) == pytest.approx(0.5)


def test_earth_physics_and_surge():
    assert pr.hemisphere_v(100, 1000, 1) == pytest.approx(100e3 / (2 * math.pi))
    assert pr.foot_resistance(100) == pytest.approx(312.5)
    assert pr.body_current(1000, 1000, 312.5) == pytest.approx(1000 / 1156.25)
    assert pr.body_current(1000, 1000, 312.5, "step") == pytest.approx(1000 / 1625)
    assert pr.rolling_sphere_r(20, 20) == pytest.approx(20)
    assert pr.rolling_sphere_r(10, 45) == pytest.approx(math.sqrt(800))
    assert pr.loop_voltage(1, 1, 1e10) == pytest.approx(2e3)
    assert pr.at_equipment(330, 15, 1000) == pytest.approx(430)
    assert pr.fuse_needed(3, 14, 25) and not pr.fuse_needed(2, 14, 25)
    assert pr.p_fail_to_clear(0.01, 0.02) == pytest.approx(2e-4)


def test_earthing_and_lightning():
    r = pr.grid_resistance(100, math.pi * 50 ** 2, 2000)
    assert r == pytest.approx(100 / 200 + 100 / 2000)
    assert pr.gpr(1000, 0.55) == pytest.approx(550)
    assert pr.collection_area(100) == pytest.approx(9 * math.pi * 1e4)
    assert pr.strikes_per_year(2.0, 1e6) == pytest.approx(2.0)
    assert pr.collection_area(10, 20, 10) == pytest.approx(200 + 60 * 30 + 900 * math.pi)
