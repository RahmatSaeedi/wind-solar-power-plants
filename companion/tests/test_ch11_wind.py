"""Tests of plantp.wind (chapter 11). Hand values in comments."""
import math

import numpy as np
import pytest

from plantp import wind as w


@pytest.fixture(scope="module")
def blade():
    return w.design_blade()


def test_polar_attached_and_stalled():
    cl, cd = w.polar([-2.0, 4.0])
    assert cl[0] == pytest.approx(0.0, abs=1e-6)        # zero-lift angle
    assert cl[1] == pytest.approx(0.66, abs=1e-3)       # 0.11 x 6
    cl90, cd90 = w.polar(90.0)
    assert abs(float(cl90)) < 0.05 and float(cd90) > 1.9   # flat plate


def test_bem_below_betz_and_optimum(blade):
    res = [w.bem(blade, lam) for lam in (6.0, 8.5, 11.0)]
    assert all(r.cp < 16 / 27 for r in res)             # Betz limit
    assert res[1].cp > res[0].cp and res[1].cp > res[2].cp
    assert 0.45 < res[1].cp < 0.50 and 0.7 < res[1].ct < 0.95


def test_operating_regions(blade):
    t = w.Turbine(blade, tsr_opt=8.5)
    low = w.operate(t, 6.0)
    assert low.pitch == 0.0 and low.tsr == pytest.approx(8.5)
    high = w.operate(t, 20.0)
    assert high.power_w == pytest.approx(5.0e6, rel=1e-3)
    assert high.pitch > 10.0 and high.omega == pytest.approx(t.omega_max)
    assert w.operate(t, 2.0).power_w == 0.0 and w.operate(t, 26.0).power_w == 0.0


def test_density_and_smoothing():
    v = w.density_equivalent_speed(8.0, 1.056)
    assert float(v) == pytest.approx(8 * (1.056 / 1.225) ** (1 / 3))
    vs = np.arange(3, 20.5, 0.5)
    flat = np.full_like(vs, 7.0)
    assert np.allclose(w.smooth_power_curve(vs, flat), 7.0)


def test_jensen_and_farm():
    # (1 - sqrt(0.2)) x (1 / 1.5)^2 = 0.2457 at five diameters, k 0.05
    assert w.jensen_deficit(0.8, 5 * 150, 150) == pytest.approx(0.2457, abs=1e-4)
    assert w.jensen_deficit(0.8, 0.0, 150) == 0.0
    xy = np.array([[0.0, 0.0], [0.0, -750.0], [750.0, 0.0]])
    v = w.farm_speeds(xy, 10.0, 0.0, 0.8, 150.0)       # wind from north
    assert v[0] == 10.0 and v[2] == 10.0 and v[1] < 8.0


def test_rainflow_astm_example():
    # ASTM E1049 example: ranges 3 (0.5), 4 (1.5), 6 (0.5), 8 (1.0), 9 (0.5)
    cyc = w.rainflow([-2, 1, -3, 5, -1, 3, -4, 4, -2])
    tally = {}
    for s, c in cyc:
        tally[round(s, 6)] = tally.get(round(s, 6), 0.0) + c
    assert tally == {3.0: 0.5, 4.0: 1.5, 6.0: 0.5, 8.0: 1.0, 9.0: 0.5}
    assert w.miner_damage([(100.0, 1.0)], 100.0, 1e6, 4.0) == pytest.approx(1e-6)
    assert w.damage_equivalent_load([(2.0, 1.0), (2.0, 1.0)], 4.0, 2.0) == \
        pytest.approx(2.0)


def test_tower_frequency_against_cantilever():
    e, i, m, length = 210e9, w.tube_inertia(4.0, 0.03), 3000.0, 100.0
    exact = 1.875 ** 2 / (2 * math.pi) * math.sqrt(e * i / (m * length ** 4))
    assert w.tower_frequency(e, i, m, length, 0.0) == pytest.approx(exact,
                                                                   rel=0.02)
    assert w.tower_frequency(e, i, m, length, 3e5) < exact


def test_thrust_and_torque_definitions(blade):
    t = w.Turbine(blade, tsr_opt=8.5)
    op = w.operate(t, 8.0, 1.225)
    area = math.pi * 75.0 ** 2
    assert op.thrust_n == pytest.approx(op.ct * 0.5 * 1.225 * area * 64.0)
    assert op.torque_nm == pytest.approx(op.power_w / t.eta / op.omega)


def test_bem_annulus_loads_sum_to_coefficients(blade):
    res = w.bem(blade, 8.5)
    area = math.pi * 75.0 ** 2
    assert res.dt.sum() / (0.5 * area) == pytest.approx(res.ct)
    assert (8.5 / 75.0) * res.dq.sum() / (0.5 * area) == pytest.approx(res.cp)
    same = w.bem(blade, 8.5, polar_fn=w.polar)          # explicit clean polar
    assert same.cp == pytest.approx(res.cp)


def test_glauert_optimum_with_wake_rotation():
    # rises with tip-speed ratio towards Betz 16/27 = 0.5926 from below
    vals = [w.glauert_cp_max(x) for x in (0.5, 1.0, 2.0, 5.0, 10.0)]
    assert all(b > a for a, b in zip(vals, vals[1:]))
    assert vals[1] == pytest.approx(0.416, abs=2e-3)
    assert vals[-1] < 16 / 27 and vals[-1] > 0.58


def test_buhl_thrust_is_continuous_and_reaches_two():
    ct = w.thrust_coefficient([0.3, 0.4 - 1e-9, 0.4 + 1e-9, 1.0])
    assert ct[0] == pytest.approx(4 * 0.3 * 0.7)          # 0.84 momentum
    assert ct[1] == pytest.approx(ct[2], abs=1e-6)        # 0.96 both sides
    assert ct[3] == pytest.approx(2.0)


def test_rotor_equivalent_speed_and_moments():
    assert w.rotor_equivalent_speed(10.0, 100.0, 75.0, 0.0) == pytest.approx(10.0)
    m = w.flap_moments(np.array([0.0, 1.0, 2.0]), np.array([0.0, 1.0, 1.0]))
    assert list(m) == [3.0, 1.0, 0.0]                   # 1 x 1 + 1 x 2


def test_gears_bearings_bins_and_sound():
    assert w.planetary_ratio(21, 99) == pytest.approx(120 / 21)
    assert w.bearing_life_mrev(2.0, 1.0, 3.0) == pytest.approx(8.0)
    v = np.repeat([4.9, 5.1, 5.2], 10)
    bins = w.bin_power_curve(v, np.repeat([100.0, 200.0, 300.0], 10))
    assert len(bins) == 2 and bins[0][3] == 10 and bins[1][3] == 20
    # 106 dB at 100 m without absorption: 106 - 10 log10(2 pi 1e4) = 57.0 dB
    assert float(w.sound_pressure_level(106.0, 100.0, 0.0)) == \
        pytest.approx(106 - 10 * math.log10(2 * math.pi * 1e4))
    assert w.sum_levels([40.0, 40.0]) == pytest.approx(43.01, abs=0.01)
