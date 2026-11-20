"""Tests of plantp.stats, plantp.phasors and plantp.solar (chapter 3)."""
import cmath
import math

import numpy as np
import pytest
from scipy import stats as sps

from plantp import phasors as ph, solar, stats as st


# ---- stats -------------------------------------------------------------------------
def test_describe_and_outliers():
    x = [1, 2, 3, 4, 100]
    s = st.describe(x)
    assert s.median == 3 and s.n == 5
    assert st.iqr_outliers(x).tolist() == [False, False, False, False, True]


def test_weibull_moments_of_rayleigh():
    # k = 2 is the Rayleigh distribution: mean = c sqrt(pi)/2
    assert st.weibull_mean(2.0, 8.0) == pytest.approx(8 * math.sqrt(math.pi) / 2)
    assert st.weibull_mean_cube(2.0, 8.0) == pytest.approx(512 * 3 * math.sqrt(math.pi) / 4)
    v = np.linspace(0, 40, 4001)
    assert np.trapezoid(st.weibull_pdf(v, 2.0, 8.0), v) == pytest.approx(1.0, abs=1e-6)


@pytest.mark.parametrize("fit", [st.weibull_fit_moments, st.weibull_fit_mle, st.weibull_fit_lsq])
def test_weibull_fits_recover_parameters(fit):
    v = sps.weibull_min.rvs(2.2, scale=8.0, size=20000, random_state=7)
    k, c = fit(v)
    assert k == pytest.approx(2.2, rel=0.04)
    assert c == pytest.approx(8.0, rel=0.02)


def test_linear_fit_exact_line_and_ci():
    x = np.arange(10.0)
    y = 3 * x + 2 + np.random.default_rng(1).normal(0, 0.1, 10)
    f = st.linear_fit(x, y)
    lo, hi = f.slope_ci()
    assert lo < 3 < hi and f.r2 > 0.999


def test_effective_n_for_autocorrelated_series():
    rng = np.random.default_rng(3)
    e = rng.normal(size=5000)
    x = np.empty_like(e)
    x[0] = e[0]
    for i in range(1, len(e)):
        x[i] = 0.9 * x[i - 1] + e[i]
    assert st.effective_n(x) == pytest.approx(5000 * 0.1 / 1.9, rel=0.15)


# ---- phasors ------------------------------------------------------------------------
def test_polar_and_power_triangle():
    v = ph.polar(230, 0)
    i = ph.polar(10, -30)                 # lagging current
    s = ph.complex_power(v, i)
    assert s.real == pytest.approx(2300 * math.cos(math.radians(30)))
    assert s.imag > 0                      # inductive: Q > 0


def test_series_parallel():
    z = ph.parallel(10 + 0j, 10 + 0j)
    assert z == pytest.approx(5 + 0j)
    assert ph.series(1 + 2j, 3 - 1j) == pytest.approx(4 + 1j)


def test_symmetrical_components_of_balanced_set():
    ia, ib, ic = ph.polar(100, 0), ph.polar(100, -120), ph.polar(100, 120)
    i0, i1, i2 = ph.symmetrical_components(ia, ib, ic)
    assert abs(i0) < 1e-9 and abs(i2) < 1e-9 and abs(i1) == pytest.approx(100)
    back = ph.from_sequences(i0, i1, i2)
    assert np.allclose(back, (ia, ib, ic))


def test_clarke_of_balanced_set():
    t = np.radians(30)
    a, b, z = ph.clarke(math.cos(t), math.cos(t - 2 * math.pi / 3), math.cos(t + 2 * math.pi / 3))
    assert a == pytest.approx(math.cos(t)) and b == pytest.approx(math.sin(t)) and abs(z) < 1e-12


# ---- solar --------------------------------------------------------------------------
def test_equinox_noon_elevation_and_azimuth():
    el, az = solar.sun_position(34.0, 81, 12.0)     # declination ~ 0 on day 81
    assert float(el) == pytest.approx(56.0, abs=0.5)
    assert float(az) == pytest.approx(180.0, abs=0.5)


def test_morning_sun_in_the_east():
    el, az = solar.sun_position(34.0, 172, 8.0)
    assert 0 < float(el) < 50 and 60 < float(az) < 110


def test_day_length_at_solstices():
    summer = 2 * abs(float(solar.sunrise_hour_angle(34.0, 172))) / 15
    winter = 2 * abs(float(solar.sunrise_hour_angle(34.0, 355))) / 15
    assert 14.0 < summer < 14.6 and 9.6 < winter < 10.2


def test_incidence_equals_dot_product():
    el, az = 40.0, 150.0
    c1 = solar.incidence_cos(el, az, 30.0, 180.0)
    c2 = solar.sun_vector(el, az) @ solar.surface_normal(30.0, 180.0)
    assert float(c1) == pytest.approx(float(c2))
