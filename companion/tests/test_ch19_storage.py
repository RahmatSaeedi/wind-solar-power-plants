"""Tests for plantp.storage (chapter 19) against hand calculations."""
import math

import numpy as np
import pytest

from plantp import storage as st


def test_ocv_monotonic_and_plateau():
    s = np.linspace(0, 1, 101)
    for chem in ("LFP", "NMC"):
        v = st.ocv(s, chem)
        assert np.all(np.diff(v) > 0)
    # LFP plateau: about 0.1 V per unit SOC in the middle
    assert st.ocv_slope(0.5, "LFP") == pytest.approx(0.10, abs=0.01)
    assert st.soc_from_ocv(st.ocv(0.3, "NMC"), "NMC") == pytest.approx(0.3, abs=1e-3)


def test_build_up_hand_numbers():
    b = st.build_up(st.Cell(), 3.2, 52, 8, 12, 8)
    assert b["rack_v_nom"] == pytest.approx(416 * 3.2)
    assert b["rack_v_max"] == pytest.approx(416 * 3.6)
    assert b["cells"] == 8 * 12 * 416
    assert b["system_mwh"] == pytest.approx(39936 * 314 * 3.2 / 1e6)


def test_simulate_rest_and_steady_state():
    c = st.Cell()
    v, s = st.simulate(c, np.zeros(10), 1.0, 0.5)
    assert v[-1] == pytest.approx(float(st.ocv(0.5)))
    # long constant current: drop tends to (r0 + r1) i (OCV moves a little)
    i = 100.0
    v, s = st.simulate(c, np.full(600, i), 1.0, 0.5)
    drop = float(st.ocv(s[-1])) - v[-1]
    assert drop == pytest.approx((c.r0 + c.r1) * i, rel=1e-3)


def test_coulomb_count_bias():
    soc = st.coulomb_count(np.zeros(24), 3600.0, 314.0, 0.5, bias_a=1.0)
    assert 0.5 - soc[-1] == pytest.approx(24.0 / 314.0)


def test_fade_models():
    assert st.calendar_fade(4.0, 25.0, 0.5) == pytest.approx(0.02 * 1.0 * 2.0)
    assert st.calendar_fade(1.0, 35.0, 0.5) > st.calendar_fade(1.0, 25.0, 0.5)
    assert st.cycle_fade([(1.0, 4000)]) == pytest.approx(0.2)
    assert st.cycle_fade([(0.5, 4000)]) < 0.2


def test_drift_and_chain():
    assert st.ocv_drift_mv(0.0, 314, 7, 0.5) == pytest.approx(0.0)
    assert st.ocv_drift_mv(60, 314, 7, 0.15) > st.ocv_drift_mv(60, 314, 7, 0.5)
    r = st.chain_expected(52, 0.0, 8, 0.0)
    assert r["cells_in_module"] == 1.0 and r["modules"] == 1.0


def test_sizing_and_augmentation():
    e = st.size_nominal(20.0, 0.8, 0.927, 0.0, 0.8)
    assert e == pytest.approx(20.0 / (0.8 * 0.927 * 0.8))
    adds, _ = st.augmentation(40.0, 32.0, 0.8, lambda y: 0.0, 10, 4.0)
    assert adds == []
    adds, _ = st.augmentation(40.0, 30.0, 0.8, lambda y: 0.02 * y, 10, 4.0)
    assert adds and adds[0] == math.ceil((1 - 30 / 32) / 0.02 - 1e-9)
