"""Tests of plantp.windres (chapter 13). Hand values in comments."""
import math

import numpy as np
import pytest

from plantp import windres as wr


def test_profiles_and_fits_recover_their_parameters():
    z = np.array([60.0, 80.0, 100.0])
    v = wr.power_law(8.0, 100.0, z, 0.2)
    assert wr.fit_shear(z, v) == pytest.approx(0.2)
    vl = wr.log_law(8.0, 100.0, z, 0.05)
    z0, ustar = wr.fit_roughness(z, vl)
    assert z0 == pytest.approx(0.05, rel=1e-6)
    # u* = kappa v / ln(z/z0) = 0.4 x 8 / ln(2000) = 0.421 m/s
    assert ustar == pytest.approx(0.4 * 8 / math.log(2000), rel=1e-6)
    s = wr.pair_shear([6.0, 2.0], [6.6, 2.5], 60.0, 100.0)
    assert s[0] == pytest.approx(math.log(1.1) / math.log(100 / 60))
    assert np.isnan(s[1])


def test_turbulence_and_veer():
    ti = wr.turbulence_intensity([10.0, 0.5], [1.2, 0.1])
    assert ti[0] == pytest.approx(0.12) and np.isnan(ti[1])
    m = np.full(20, 10.2)
    sd = np.linspace(0.8, 1.6, 20)
    out = wr.ti_by_bin(m, sd, [10, 11])
    assert out[0][3] == 20 and out[0][1] == pytest.approx(sd.mean() / 10.2)
    assert list(wr.angle_diff([10, 350, 180], [350, 10, 0])) == [20, -20, 180]


def test_sensor_checks_and_recovery():
    wd = np.array([10.0] * 10 + [190.0] * 10)
    v1 = np.r_[np.full(10, 9.0), np.full(10, 10.0)]
    v2 = np.full(20, 10.0)
    rows = wr.sector_ratio(v1, v2, wd)
    assert rows[0][1] == pytest.approx(0.9) and rows[6][1] == pytest.approx(1.0)
    f = wr.icing_flags([5.0, 5.0, 5.0], [0.01, 0.5, 0.01], [-2.0, -2.0, 8.0])
    assert list(f) == [True, False, False]
    st = wr.stuck_runs([1, 2, 3, 3, 3, 3, 3, 3, 4], 6)
    assert list(st) == [False, False, True, True, True, True, True, True, False]
    assert wr.recovery([True, True, False, True]) == pytest.approx(0.75)


def test_mcp_methods():
    rng = np.random.default_rng(1)
    x = rng.uniform(4, 12, 500)
    y = 1.1 * x + rng.normal(0, 0.5, 500)
    lt = rng.uniform(4, 12, 2000)
    yl, a, b = wr.mcp_linear(x, y, lt)
    assert b == pytest.approx(1.1, abs=0.03)
    yv, a2, b2 = wr.mcp_variance_ratio(x, y, lt)
    assert b2 > b                                     # keeps the spread
    ys = wr.mcp_sector_ratio(x, y, np.zeros(500), lt, np.zeros(2000))
    assert ys.mean() == pytest.approx(lt.mean() * y.mean() / x.mean())


def test_energy_sensitivity_cubic_region():
    v = np.full(100, 6.0)
    cv = np.linspace(0, 20, 2001)
    cp = cv ** 3                                      # pure cube law
    assert wr.energy_sensitivity(v, cv, cp) == pytest.approx(3.0, rel=0.02)


def test_richardson_sign_follows_stability():
    # inversion 8.0 -> 9.4 C over 10..92 m: stable; lapse 20.0 -> 18.6: unstable
    assert wr.bulk_richardson(8.0, 9.4, 6.4, 7.6, 10, 92) > 0.25
    assert wr.bulk_richardson(20.0, 18.6, 6.2, 6.6, 10, 92) < 0


def test_rotor_equivalent_uniform_and_power_law():
    flat = wr.rotor_equivalent(lambda z: np.full_like(z, 8.0), 100.0, 75.0)
    assert flat == pytest.approx(8.0, rel=1e-4)
    from plantp import wind
    a = wr.rotor_equivalent(lambda z: 8.0 * (z / 100.0) ** 0.3, 100.0, 75.0)
    b = wind.rotor_equivalent_speed(8.0, 100.0, 75.0, 0.3)
    assert a == pytest.approx(b, rel=1e-4)
    # veer only lowers it
    c = wr.rotor_equivalent(lambda z: np.full_like(z, 8.0), 100.0, 75.0, 0.25)
    assert c < 8.0


def test_vector_mean_direction_crosses_north():
    assert wr.vector_mean_direction([350.0, 10.0]) == pytest.approx(0.0, abs=1e-9) or \
        wr.vector_mean_direction([350.0, 10.0]) == pytest.approx(360.0)
    assert wr.vector_mean_direction([80.0, 100.0]) == pytest.approx(90.0)


def test_gust_factor_and_dbs():
    x = np.r_[np.full(10, 10.0), np.full(3, 13.0), np.full(10, 10.0)]
    g, peak = wr.gust_factor(x, 3)
    assert peak == pytest.approx(13.0) and g == pytest.approx(13.0 / x.mean())
    rad = wr.dbs_radials(5.0, -3.0, {"N": 0.2, "S": 0.2, "E": 0.2, "W": 0.2}, 28.0)
    u, v, w = wr.dbs_reconstruct(rad, 28.0)
    assert (u, v, w) == pytest.approx((5.0, -3.0, 0.2))


def test_mcp_matrix_recovers_a_direction_and_speed_dependent_ratio():
    rng = np.random.default_rng(1)
    x = rng.uniform(2, 14, 20000)
    wd = rng.uniform(0, 360, 20000)
    ratio = np.where(wd < 180, 1.1, 1.2) * np.where(x < 8, 1.0, 1.05)
    y = ratio * x
    out = wr.mcp_matrix(x, y, wd, x, wd)
    assert np.allclose(out, y, rtol=1e-9) or np.mean(np.abs(out / y - 1)) < 0.01
