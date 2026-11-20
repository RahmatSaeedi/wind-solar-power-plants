"""Tests of plantp.pvcell (chapter 10). Hand values in comments."""
import math
import warnings

import numpy as np
import pytest

from plantp import pvcell as pc

warnings.simplefilter("ignore", RuntimeWarning)


@pytest.fixture(scope="module")
def ref():
    return pc.fit(pc.PVM_550_DS)


def test_w_exp_matches_scipy_and_large_values():
    from scipy.special import lambertw
    for lx in (-5.0, 0.0, 3.0, 50.0):
        assert pc.w_exp(lx) == pytest.approx(float(np.real(lambertw(math.exp(lx)))))
    # W(e^x) solves w + ln w = x
    w = pc.w_exp(2000.0)
    assert w + math.log(w) == pytest.approx(2000.0)


def test_fit_reproduces_datasheet(ref):
    ds = pc.PVM_550_DS
    assert ref.isc == pytest.approx(ds.isc, rel=1e-6)
    assert ref.voc == pytest.approx(ds.voc, rel=1e-6)
    v, i, p = ref.mpp()
    assert v == pytest.approx(ds.vmp, rel=1e-3)
    assert i == pytest.approx(ds.imp, rel=1e-3)
    assert p == pytest.approx(ds.vmp * ds.imp, rel=1e-4)
    # explicit forms are inverse of each other
    assert float(ref.i(ref.v(7.0))) == pytest.approx(7.0, rel=1e-9)
    # dV_oc/dT matches the data sheet
    v20 = pc.at_conditions(ref, 1000, 20, ds.alpha_isc).voc
    v30 = pc.at_conditions(ref, 1000, 30, ds.alpha_isc).voc
    assert (v30 - v20) / 10 == pytest.approx(ds.beta_voc, rel=1e-3)


def test_translation_trends(ref):
    a = pc.PVM_550_DS.alpha_isc
    hot = pc.at_conditions(ref, 1000, 65, a)
    low = pc.at_conditions(ref, 200, 25, a)
    assert hot.mpp()[2] < 0.9 * 550 and hot.voc < 45.0
    assert low.isc == pytest.approx(0.2 * 13.98, rel=1e-3)
    assert 0.95 < low.mpp()[2] / (0.2 * 550.1) < 1.0     # slightly lower efficiency


def test_reverse_breakdown_and_temperature_models():
    i = pc.cell_reverse_current([-1.0, -10.0, -14.5], 13.0, 10.0)
    assert i[0] < i[1] < i[2]           # more reverse voltage, more current
    assert float(pc.faiman(20, 1000, 0.0)) == pytest.approx(60.0)
    assert float(pc.faiman(20, 800, 1.0)) == pytest.approx(20 + 800 / 31.84)
    assert float(pc.wind_at_height(10.0, 100, 2, 0.2)) == pytest.approx(
        10 * 0.02 ** 0.2)


def test_iam_and_poa():
    assert float(pc.iam_ashrae(1.0)) == pytest.approx(1.0)
    assert float(pc.iam_ashrae(0.5)) == pytest.approx(0.95)
    assert float(pc.iam_ashrae(-0.2)) == 0.0
    # horizontal surface: POA equals GHI split into beam + diffuse
    b, s, g = pc.poa_hay_davies(800, 700, 200, 0.857, 0.857, 1361, 0.0)
    assert float(b + s + g) == pytest.approx(700 * 0.857 + 200, rel=1e-6)
    # vertical surface, no beam: half the isotropic sky plus half the ground
    b, s, g = pc.poa_hay_davies(200, 0, 200, 0.0, 0.5, 1361, 90.0, albedo=0.2)
    assert float(s) == pytest.approx(100.0) and float(g) == pytest.approx(20.0)


def test_string_limits_boundaries():
    """The string checks of section E: each boundary case gives the
    expected verdict (1500 V system, 933 V floor, A-190)."""
    from companion.ch10.examples_c import string_limits
    ok = string_limits(26, -15.0, 72.0)
    assert ok["ok_v_sys"] and ok["v_oc_cold"] < 1440           # 1436 V
    assert not ok["ok_floor"]                     # 918 V: static worst case
    assert string_limits(27, -15.0, 72.0)["ok_floor"]           # 954 V
    assert not string_limits(27, -25.0, 72.0)["ok_v_sys"]       # 1527 V
    assert not string_limits(28, -15.0, 72.0)["ok_v_sys"]       # 1547 V
    hot_roof = string_limits(26, -15.0, 80.0)
    assert hot_roof["v_mp_hot"] < ok["v_mp_hot"]                 # 889 V
    assert ok["i_sc_max"] == pytest.approx(17.09, abs=0.01)
