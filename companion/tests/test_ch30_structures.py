"""Chapter 30 structures module against hand calculations."""
import math

import pytest

from plantp import structures as st


def test_wind_and_drag():
    assert st.wind_profile(10.0, 10.0, 100.0, 0.14) == pytest.approx(10 * 10 ** 0.14)
    assert st.dynamic_pressure(30.0) == pytest.approx(551.25)
    assert st.peak_speed(20.0, 0.1) == pytest.approx(27.0)
    assert st.drag_force(500.0, 1.2, 2.0) == pytest.approx(1200.0)
    assert st.vortex_speed(0.5, 4.0) == pytest.approx(10.0)


def test_shell_buckling():
    # E 210 GPa, t 30 mm, r 2 m, knock-down 0.3: 0.3 x 0.605 x 210e9 x 0.015
    assert st.shell_buckling(210e9, 0.030, 2.0, 0.3) == pytest.approx(0.3 * 0.605 * 210e9 * 0.015)
    assert st.rankine(355.0, 355.0) == pytest.approx(177.5)
    assert st.rankine(355.0, 1e12) == pytest.approx(355.0, rel=1e-6)


def test_sn_life_bilinear():
    assert st.sn_life(71.0, 71.0) == pytest.approx(2e6)
    ds_d = 71 * (2 / 5) ** (1 / 3)
    assert st.sn_life(ds_d, 71.0) == pytest.approx(5e6)
    # below the knee the slope is 5
    assert st.sn_life(ds_d / 2, 71.0) == pytest.approx(5e6 * 32)
    # above, slope 3
    assert st.sn_life(142.0, 71.0) == pytest.approx(2e6 / 8)


def test_effective_area():
    r = 10.0
    assert st.effective_area_circle(r, 0.0) == pytest.approx(math.pi * r * r)
    assert st.effective_area_circle(r, r) == 0.0
    a = st.effective_area_circle(r, 5.0)
    assert 0 < a < math.pi * r * r
    e, a2, q = st.foundation_pressure(30_000.0, 150_000.0, r)
    assert e == pytest.approx(5.0) and a2 == pytest.approx(a) and q == pytest.approx(30_000 / a)


def test_rotational_and_frequency():
    k = st.rotational_stiffness(50e6, 10.0, 0.3)
    assert k == pytest.approx(8 * 50e6 * 1000 / (3 * 0.7))
    f = st.frequency_with_foundation(0.30, k, 400e3, 100.0)
    assert f < 0.30
    assert st.frequency_with_foundation(0.30, 1e30, 400e3, 100.0) == pytest.approx(0.30)


def test_piles_and_misc():
    assert st.pile_uplift(0.5, 2.0, 20.0, 1.0) == pytest.approx(21.0)
    assert st.broms_lateral_sand(0.15, 1.5, 18.0, 3.0, 1.0) == pytest.approx(
        0.5 * 18 * 0.15 * 1.5 ** 3 * 3 / 2.5)
    assert st.zinc_life(85.0, 1.7) == pytest.approx(50.0)
    assert st.thermal_expansion(12e-6, 50.0, 60.0) == pytest.approx(0.036)
    assert st.base_shear(1000.0, 0.3, 1.5) == pytest.approx(1000 * 9.81 * 0.2)
    assert st.bolt_slip(8, 0.3, 100e3, 2) == pytest.approx(480e3)
    assert st.rebar_area(1e6, 0.5, 435e6) == pytest.approx(1e6 / (435e6 * 0.45))
