"""Chapter 41 PV manufacturing arithmetic against hand calculations."""
import math

import pytest

from plantp import pvfab as f


def test_device_by_hand():
    vt = f.thermal_voltage(25.0)
    assert vt == pytest.approx(0.025693, rel=1e-4)
    assert f.voc(0.040, 1e-13) == pytest.approx(vt * math.log(4e11 + 1))
    v = 0.70 / vt
    assert f.fill_factor(0.70) == pytest.approx((v - math.log(v + 0.72)) / (v + 1))
    assert f.fill_factor(0.70, 1.0, 0.040) == pytest.approx(
        f.fill_factor(0.70) * (1 - 0.040 / 0.70))
    assert f.absorption_depth_um(1e4) == pytest.approx(1.0)
    assert f.diffusion_length_um(30, 1e-3) == pytest.approx(1e4 * math.sqrt(0.03))


def test_budget_binning_mismatch():
    b = f.loss_budget([("a", 0.5), ("b", 0.8)])
    assert b[-1][2] == pytest.approx(0.4)
    assert f.bin_of(13.95, [13.8, 13.9, 14.0, 14.1]) == 1
    with pytest.raises(ValueError):
        f.bin_of(15.0, [13.8, 13.9])
    assert f.series_mismatch([10.0, 10.0]) == pytest.approx(0.0)
    assert f.series_mismatch([9.0, 11.0]) == pytest.approx(0.1)


def test_module_and_data_rules():
    assert f.ctm(540.0, [3.8] * 144) == pytest.approx(540 / 547.2)
    # half-cut: three quarters of the ribbon loss saved
    assert f.half_cut_gain(14.0, 0.002, 72) == pytest.approx(
        0.75 * 14.0 ** 2 * 0.002 * 72)
    z = f.robust_z([1, 2, 3, 4, 100])
    assert z[2] == pytest.approx(0.0)
    assert f.flag_outliers([1, 2, 3, 4, 100]) == [4]
    assert f.to_stc(500.0, 1000.0, 25.0) == pytest.approx(500.0)
    assert f.to_stc(500.0, 1000.0, 35.0) == pytest.approx(500 / (1 - 0.035))
    n = f.max_string_length(49.9, -0.27, -10.0, 1500.0)
    assert 49.9 * (1 + 0.0027 * 35) * n <= 1500 < 49.9 * (1 + 0.0027 * 35) * (n + 1)
