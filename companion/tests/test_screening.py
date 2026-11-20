"""Screening models of chapter 1 against hand-calculated reference cases."""
import math

import numpy as np
import pytest

from plantp import screening as sc


def test_pv_below_the_inverter_limit():
    # 60 MWp * (1000/1000) * 0.85 = 51.0 MW DC ; * 0.98 = 49.98 MW AC  (< 50 MW)
    assert sc.pv_ac_power_mw(1000.0, 60, 50) == pytest.approx(49.98)


def test_pv_is_clipped_at_the_inverter_rating():
    # 60 * 1.04 * 0.85 * 0.98 = 51.98 MW  -> limited to 50 MW
    assert sc.pv_ac_power_mw(1040.0, 60, 50) == pytest.approx(50.0)


def test_pv_dark_and_array_input():
    out = sc.pv_ac_power_mw([0.0, 500.0], 60, 50)
    assert out == pytest.approx([0.0, 24.99])           # 60*0.5*0.85*0.98


def test_pv_rejects_negative_irradiance():
    with pytest.raises(ValueError):
        sc.pv_ac_power_mw(-1.0, 60, 50)


def test_pv_dc_power_is_the_unclipped_value():
    # 60 * 1.04 * 0.85 = 53.04 MW DC, no inverter limit applied
    assert sc.pv_dc_power_mw(1040.0, 60) == pytest.approx(53.04)


def test_land_screening_hand_cases():
    assert sc.pv_land_area_ha(60, 1.8) == pytest.approx(108.0)
    # 12 turbines, D = 150 m, cell 7D x 4D = 1050 m x 600 m = 0.63 km2 each
    assert sc.wind_envelope_km2(12, 150.0) == pytest.approx(7.56)
    with pytest.raises(ValueError):
        sc.pv_land_area_ha(0, 1.8)
    with pytest.raises(ValueError):
        sc.wind_envelope_km2(12, -1.0)


CURVE_V = [0.0, 3.0, 8.0, 13.0, 25.0, 25.5]
CURVE_P = [0.0, 65.0, 2522.0, 5000.0, 5000.0, 0.0]


def test_wind_at_a_tabulated_speed():
    # 2522 kW * 12 / 1000 = 30.264 MW ; * (1 - 0.12) = 26.632 MW
    assert sc.wind_power_mw(8.0, CURVE_V, CURVE_P, 12) == pytest.approx(26.63232)


def test_wind_interpolates_between_bins_and_stops_outside():
    # half-way between 8 and 13 m/s: (2522 + 5000)/2 = 3761 kW per turbine
    assert sc.wind_power_mw(10.5, CURVE_V, CURVE_P, 12, loss=0.0) == pytest.approx(45.132)
    assert sc.wind_power_mw([0.0, 30.0], CURVE_V, CURVE_P, 12) == pytest.approx([0.0, 0.0])
    with pytest.raises(ValueError):
        sc.wind_power_mw(-2.0, CURVE_V, CURVE_P, 12)


def test_export_limit_splits_generation():
    export, cut = sc.export_and_curtailment_mw([80.0, 100.0, 103.5], 100.0)
    assert export == pytest.approx([80.0, 100.0, 100.0])
    assert cut == pytest.approx([0.0, 0.0, 3.5])


def test_capacity_factor():
    # 100 MW running at full power for a quarter of the year
    assert sc.capacity_factor(219_000.0, 100.0) == pytest.approx(0.25)
    with pytest.raises(ValueError):
        sc.capacity_factor(1.0, 0.0)


def test_battery_shift_hand_case():
    # 32 MWh usable, 20 MW, round trip 0.86 -> one-way eta = 0.92736
    eta = math.sqrt(0.86)
    surplus = [10.0, 30.0, 0.0, 0.0]
    headroom = [0.0, 0.0, 5.0, 50.0]
    r = sc.shift_surplus_with_battery(surplus, headroom, 20.0, 32.0, 0.86)
    # hour 1: charge 10 MW        -> stored 10*eta          =  9.2736 MWh
    # hour 2: charge min(30, 20, (32-9.2736)/eta = 24.51) = 20 MW -> stored 27.8208 MWh
    # hour 3: discharge min(5, 20, 27.8208*eta = 25.80) = 5 MW    -> stored 27.8208 - 5/eta
    # hour 4: discharge min(50, 20, soc*eta = 20.80) = 20 MW
    assert r.charged_mwh == pytest.approx(30.0)
    assert r.soc_mwh[0] == pytest.approx(10 * eta)
    assert r.soc_mwh[1] == pytest.approx(30 * eta)
    assert r.soc_mwh[2] == pytest.approx(30 * eta - 5 / eta)
    assert r.delivered_mwh == pytest.approx(25.0)
    assert r.soc_mwh[3] == pytest.approx(30 * eta - 25 / eta)


def test_battery_never_exceeds_its_limits_and_never_creates_energy():
    rng = np.random.default_rng(1)
    surplus = np.where(rng.random(500) < 0.3, rng.random(500) * 40, 0.0)
    headroom = np.where(surplus > 0, 0.0, rng.random(500) * 40)
    r = sc.shift_surplus_with_battery(surplus, headroom, 20.0, 32.0, 0.86)
    assert (r.soc_mwh >= 0).all() and (r.soc_mwh <= 32.0 + 1e-9).all()
    assert r.delivered_mwh <= 0.86 * r.charged_mwh + 1e-9
    assert r.charged_mwh <= surplus.sum() + 1e-9


def test_battery_input_checks():
    with pytest.raises(ValueError):
        sc.shift_surplus_with_battery([1.0], [1.0, 2.0], 20, 32, 0.86)
    with pytest.raises(ValueError):
        sc.shift_surplus_with_battery([1.0], [1.0], 20, 32, 1.2)
