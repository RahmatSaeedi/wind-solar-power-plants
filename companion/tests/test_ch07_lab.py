"""Tests of the chapter 7 lab (auxiliary load schedule, meter record)."""
import math

import numpy as np
import pytest

from companion.ch07 import lab_d
from companion.ch07.lab_d import LOADS, Load, phase_currents
from plantp.phasors import complex_power


def test_balanced_loads_give_no_neutral_current():
    loads = [Load("fan", 30.0, 0.85, "abc", 1.0)]
    ia, ib, ic = phase_currents(loads, "S0")
    assert abs(ia + ib + ic) < 1e-9
    # hand: 30 kW / (3 x 230 V x 0.85) = 51.15 A (the lab uses 230 V phase)
    assert abs(ia) == pytest.approx(30e3 / (3 * 230 * 0.85))
    assert math.degrees(-np.angle(ia)) == pytest.approx(
        math.degrees(math.acos(0.85)))               # lagging by 31.79 deg


def test_power_of_the_schedule_adds_up():
    for sc, extra in (("S0", 0.0), ("S1", 60.0)):
        ia, ib, ic = phase_currents(LOADS, sc)
        v = (lab_d.VA, lab_d.VB, lab_d.VC)
        s = sum(complex_power(x, i) for x, i in zip(v, (ia, ib, ic)))
        p_hand = sum(ld.p_kw * ld.diversity for ld in LOADS
                     if ld.scenario == "S0") + extra
        assert s.real / 1e3 == pytest.approx(p_hand)


def test_single_phase_load_returns_through_the_neutral():
    loads = [Load("lamp", 2.3, 1.0, "a", 1.0)]
    ia, ib, ic = phase_currents(loads, "S0")
    assert abs(ia) == pytest.approx(10.0)          # 2300 W / 230 V
    assert abs(ib) == 0 and abs(ic) == 0
    assert abs(ia + ib + ic) == pytest.approx(10.0)


def test_meter_record_has_the_planted_faults():
    r = lab_d.meter_record()
    assert np.all(r["p_b"] < 0)                    # reversed CT, phase b
    assert np.all(r["p_a"] > 0) and np.all(r["p_c"] > 0)
    k = int(np.argmin(r["vmin_a"]))
    assert k == 14 * 6 + 2                         # dip at 14:20
    assert len(r["hour"]) == 144                   # 10-min values, one day
