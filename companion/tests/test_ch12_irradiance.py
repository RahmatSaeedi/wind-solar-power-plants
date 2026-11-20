"""Tests of plantp.irradiance (chapter 12). Hand values in comments."""
import math

import numpy as np
import pytest

from plantp import irradiance as ir


def test_extraterrestrial_and_air_mass():
    # perihelion early January is about 3 % above the mean, aphelion below
    assert float(ir.g0n(3)) == pytest.approx(1361 * (1 + 0.033 * math.cos(2 * math.pi * 3 / 365)))
    assert float(ir.g0n(3)) > 1400 > 1361 > float(ir.g0n(185))
    am = ir.air_mass([0.0, 60.0, 95.0])
    assert am[0] == pytest.approx(1.0, abs=0.002)
    assert am[1] == pytest.approx(1.99, abs=0.01)        # about 1 / cos 60
    assert np.isnan(am[2])


def test_clearness_and_clear_sky():
    kt = ir.clearness_index([700.0, 10.0], [0.7, 0.05], 1361.0)
    assert kt[0] == pytest.approx(700 / (1361 * 0.7))
    assert np.isnan(kt[1])                               # sun too low
    # Haurwitz at the zenith: 1098 exp(-0.057) = 1037.2 W/m2
    assert float(ir.clear_sky_haurwitz(1.0)) == pytest.approx(1037.2, abs=0.1)
    assert float(ir.clear_sky_haurwitz(-0.1)) == 0.0


def test_erbs_pieces_join_and_decomposition_closes():
    kd = ir.erbs_diffuse_fraction([0.22, 0.2200001, 0.80, 0.8000001])
    assert kd[0] == pytest.approx(kd[1], abs=1e-3)       # 0.980 both sides
    assert kd[2] == pytest.approx(kd[3], abs=1e-3)       # 0.165 both sides
    ghi, cz = np.array([600.0, 200.0]), np.array([0.8, 0.4])
    dni, dhi = ir.decompose(ghi, cz, 1361.0)
    assert np.allclose(dni * cz + dhi, ghi)
    assert np.all(dhi > 0) and np.all(dni >= 0)


def test_isotropic_transposition_horizontal_is_ghi():
    beam, sky, ground = ir.poa_isotropic(600.0, 500.0, 200.0, 0.8, 0.0)
    assert float(beam + sky + ground) == pytest.approx(500 * 0.8 + 200)


def test_qc_flags():
    cz = np.array([0.5, 0.5, 0.5, -0.2, 0.5])
    ghi = np.array([1500.0, 600.0, 600.0, -20.0, np.nan])
    dni = np.array([800.0, 700.0, 700.0, 0.0, 700.0])
    dhi = np.array([100.0, 250.0, 100.0, 0.0, 100.0])
    f = ir.qc_flags(ghi, dni, dhi, cz, 1361.0)
    assert f[0] & ir.FLAG_PHYS                             # 1500 W/m2 at z = 60
    assert f[1] == 0                                       # 700 x 0.5 + 250 = 600
    assert f[2] & ir.FLAG_CLOSURE                          # 450 vs 600
    assert f[3] & ir.FLAG_NIGHT_NEG
    assert f[4] & ir.FLAG_MISSING


def test_lag_gaps_drift_and_long_term():
    t = np.arange(200)
    ref = np.sin(2 * np.pi * t / 24).clip(0)
    late = np.roll(ref, 2)
    assert ir.best_lag(late, ref, 5) == 2
    x = np.array([0.5, np.nan, np.nan, 0.8, np.nan, np.nan, np.nan, np.nan, 0.2])
    y = ir.fill_short_gaps(x, 3)
    assert y[1] == pytest.approx(0.6) and y[2] == pytest.approx(0.7)
    assert np.isnan(y[5])                                  # gap of 4 stays open
    r = ir.ratio_by_block(np.r_[np.ones(10), 0.9 * np.ones(10)], np.ones(20), 10)
    assert list(r) == pytest.approx([1.0, 0.9])
    assert ir.long_term_ratio([100.0], [110.0], [105.0]) == pytest.approx(95.4545, abs=1e-3)


def test_statistics_and_p90():
    assert ir.mbe([2.0, 4.0], [1.0, 1.0]) == pytest.approx(2.0)
    assert ir.rmse([2.0, 4.0], [1.0, 1.0]) == pytest.approx(math.sqrt(5))
    a = np.arange(100.0)
    assert ir.distribution_distance(a, a[::-1]) == pytest.approx(0.0)
    assert ir.combine_uncertainty(0.03, 0.04) == pytest.approx(0.05)
    assert ir.p_value(100.0, 0.05) == pytest.approx(100 * (1 - 1.2816 * 0.05), abs=1e-3)
