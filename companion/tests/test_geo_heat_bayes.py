"""Tests of plantp.geo, the diffusion and Newton helpers of plantp.numerics and Bayes'
theorem in plantp.stats, against hand calculations (chapter 3, fourth expansion)."""
import math

import numpy as np
import pytest

from plantp import geo, numerics as nm, stats as st


def test_one_degree_of_latitude_and_equator():
    d = float(geo.haversine_m(34.0, 50.0, 35.0, 50.0))
    assert d == pytest.approx(geo.R_EARTH_M * math.pi / 180, rel=1e-12)
    assert float(geo.haversine_m(0, 0, 0, 1)) == pytest.approx(d, rel=1e-12)
    assert float(geo.haversine_m(34, 50, 34, 50)) == 0.0


def test_bearings():
    assert geo.bearing_deg(0, 0, 0, 1) == pytest.approx(90.0)
    assert geo.bearing_deg(10, 20, 11, 20) == pytest.approx(0.0)
    assert geo.bearing_deg(10, 20, 9, 20) == pytest.approx(180.0)


def test_enu_matches_haversine_for_short_distances():
    lat0, lon0 = 34.0, 50.0
    e, n = geo.enu_offsets_m(lat0, lon0, 34.01, 50.012)
    flat = math.hypot(float(e), float(n))
    assert flat == pytest.approx(float(geo.haversine_m(lat0, lon0, 34.01, 50.012)), rel=1e-4)


def test_heat_step_rejects_unstable_ratio_and_keeps_linear_profile():
    with pytest.raises(ValueError):
        nm.heat_explicit_step(np.zeros(5), 0.6, 0.0)
    u = np.linspace(10, 20, 11)
    v = nm.heat_explicit_step(u, 0.4, 10.0, 20.0)
    assert np.allclose(u, v)                    # a straight line is a steady state


def test_heat_step_decay_of_sine_mode():
    # u = sin(pi z / L) with fixed zero ends decays as exp(-alpha (pi/L)^2 t)
    n, length, alpha = 41, 1.0, 1.0
    z = np.linspace(0, length, n)
    dz = z[1] - z[0]
    r = 0.25
    dt = r * dz * dz / alpha
    u = np.sin(math.pi * z / length)
    steps = 400
    for _ in range(steps):
        u = nm.heat_explicit_step(u, r, 0.0, 0.0)
    expected = math.exp(-alpha * (math.pi / length) ** 2 * steps * dt)
    assert u[n // 2] == pytest.approx(expected, rel=2e-3)


def test_newton_minimise_quadratic_in_one_step():
    f = lambda x: (x[0] - 1) ** 2 + 10 * (x[1] + 2) ** 2 + x[0] * x[1]   # noqa: E731
    x, it, hist = nm.newton_minimise(f, [5.0, 5.0], h=1e-3, tol=1e-6)
    # exact minimum: 2(x-1) + y = 0, 20(y+2) + x = 0
    xs = np.linalg.solve([[2, 1], [1, 20]], [2, -40])
    assert np.allclose(x, xs, atol=1e-6)
    assert it <= 2


def test_bayes_posterior_hand_case():
    # 1 % prevalence, 90 % sensitivity, 9 % false alarms -> 0.009 / (0.009 + 0.0891)
    assert st.bayes_posterior(0.01, 0.9, 0.09) == pytest.approx(0.009 / 0.0981)
    assert st.bayes_posterior(0.5, 1.0, 0.0) == 1.0
    with pytest.raises(ValueError):
        st.bayes_posterior(1.2, 0.9, 0.1)


def test_series_and_parallel_availability():
    assert st.series_availability([0.99, 0.98]) == pytest.approx(0.9702)
    assert st.parallel_availability([0.9, 0.9]) == pytest.approx(0.99)
    assert st.parallel_availability([0.95]) == pytest.approx(0.95)


def test_latin_hypercube_one_point_per_stratum():
    from plantp import uncertainty as un
    rng = np.random.default_rng(1)
    u = un.latin_hypercube(50, 3, rng)
    assert u.shape == (50, 3)
    for j in range(3):
        strata = np.sort(np.floor(u[:, j] * 50).astype(int))
        assert np.array_equal(strata, np.arange(50))
    assert u.min() >= 0.0 and u.max() < 1.0


def test_park_turns_balanced_set_into_constants():
    from plantp import phasors as ph
    w = 2 * math.pi * 50
    t = np.linspace(0, 0.04, 801)
    phi = math.radians(30)
    xa = np.cos(w * t + phi)
    xb = np.cos(w * t + phi - 2 * math.pi / 3)
    xc = np.cos(w * t + phi + 2 * math.pi / 3)
    al, be, ze = ph.clarke(xa, xb, xc)
    d, q = ph.park(al, be, w * t)
    assert np.allclose(d, math.cos(phi)) and np.allclose(q, math.sin(phi))
    assert np.allclose(ze, 0.0)
    # a negative-sequence set appears at twice the frequency with the same amplitude
    na = 0.1 * np.cos(w * t)
    nb = 0.1 * np.cos(w * t + 2 * math.pi / 3)
    nc = 0.1 * np.cos(w * t - 2 * math.pi / 3)
    d2, q2 = ph.park(*ph.clarke(na, nb, nc)[:2], w * t)
    assert np.allclose(np.hypot(d2, q2), 0.1)
    assert d2.max() == pytest.approx(0.1, abs=1e-3)
