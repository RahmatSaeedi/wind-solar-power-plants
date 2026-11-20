"""Tests of plantp.machines (chapter 8). Hand values in comments."""
import math

import pytest

from plantp import machines as m


def test_speeds_and_torque():
    assert m.sync_speed_rpm(50, 4) == 1500
    assert m.electrical_freq_hz(1155, 6) == pytest.approx(57.75)
    assert m.slip(1500, 1470) == pytest.approx(0.02)
    assert m.slip(1500, 1530) == pytest.approx(-0.02)       # generating
    # 5.32 MW at 10.5 rpm: 5.32e6 / 1.0996 = 4.84 MN m (chapter 4)
    assert m.torque_nm(5.32e6, 10.5) == pytest.approx(4.838e6, rel=1e-3)
    assert m.rotor_volume_m3(80e3, 40e3) == pytest.approx(1.0)
    assert m.emf_rms(50, 100, 0.01) == pytest.approx(222.0)
    with pytest.raises(ValueError):
        m.sync_speed_rpm(50, 3)


def test_induction_machine_balances_power():
    im = m.InductionMachine(230, 50, 4, 0.07, 0.25, 8.0, 0.06, 0.25)
    op = im.operate(0.02)
    # input = copper losses + air-gap power (no core loss in this model)
    assert op["p_in"] == pytest.approx(op["p_cu1"] + op["p_ag"], rel=1e-9)
    # converted = air gap x (1 - s); rotor copper = s x air gap
    assert op["p_cu2"] == pytest.approx(0.02 * op["p_ag"], rel=1e-9)
    assert op["torque"] > 0 and op["pf"] > 0
    gen = im.operate(-0.02)                                 # above synchronous
    assert gen["p_in"] < 0 and gen["q_in"] > 0              # gives P, takes Q
    s = im.slip_for_shaft_power(op["p_shaft"])
    assert s == pytest.approx(0.02, rel=1e-4)


def test_synchronous_machine_relations():
    v = 230.0
    e = m.sm_emf(complex(v, 0), complex(100, 0), 1.0)     # E = 230 + j100
    assert abs(e) == pytest.approx(math.hypot(230, 100))
    d = math.atan2(e.imag, e.real)
    assert m.sm_power(abs(e), v, 1.0, d) == pytest.approx(230 * 100)
    assert m.sm_reactive(abs(e), v, 1.0, d) == pytest.approx(0.0, abs=1e-9)
    assert m.dfig_rotor_power(3e6, -0.2) == pytest.approx(0.5e6)
    # stator + rotor = shaft (lossless energy balance)
    assert 3e6 / 1.2 + m.dfig_rotor_power(3e6, -0.2) == pytest.approx(3e6)


def test_losses_heat_life():
    # rated: 5 MW at 0.97 -> losses 154.6 kW
    assert m.loss_model(1.0, 5e6, 0.97) == pytest.approx(5e6 * (1 / 0.97 - 1))
    assert m.efficiency(1.0, 5e6, 0.97) == pytest.approx(0.97)
    assert m.efficiency(0.0, 5e6, 0.97) == 0.0
    # copper 20 -> 75 C: (234.5 + 75) / (234.5 + 20) = 1.2161
    assert m.r_at_temperature(1.0, 20, 75) == pytest.approx(1.2161, rel=1e-4)
    assert m.temperature_from_resistance(2.0, 20, 2.54) == pytest.approx(88.7,
                                                                          abs=0.05)
    assert m.life_factor(90, 90, 1e5) == pytest.approx(1.0)
    assert m.life_factor(100, 90, 1e5) < 0.5                # hotter, shorter


def test_balancing_and_bearings():
    u = m.residual_unbalance(1000, 2.5, 1155)
    assert u["e_um"] == pytest.approx(2.5e3 / 120.95, rel=1e-3)
    b = m.bearing_freqs(1155, 14, 0.04, 0.22)
    assert b["fr"] == pytest.approx(19.25)
    assert b["bpfo"] + b["bpfi"] == pytest.approx(14 * 19.25)   # n fr
    assert b["ftf"] < b["fr"] / 2


def test_winding_factor_cogging_skew():
    # integral slot, q = 2 full pitch: k_d = sin(30)/(2 sin 15) = 0.9659
    assert m.winding_factor(24, 4, 6) == pytest.approx(0.9659, abs=1e-4)
    # 5/6 pitch adds k_p = sin(75) = 0.9659: 0.9330
    assert m.winding_factor(24, 4, 5) == pytest.approx(0.9330, abs=1e-4)
    # q = 3 full pitch: sin(30)/(3 sin 10) = 0.9598
    assert m.winding_factor(54, 6, 9) == pytest.approx(0.9598, abs=1e-4)
    # tooth-coil windings: 12/10 -> 0.933, 9/8 -> 0.945 (textbook values)
    assert m.winding_factor(12, 10, 1) == pytest.approx(0.933, abs=1e-3)
    assert m.winding_factor(9, 8, 1) == pytest.approx(0.945, abs=1e-3)
    with pytest.raises(ValueError):
        m.winding_factor(10, 4, 2)                 # 10 slots, 2 pole pairs
    assert m.cogging_periods(54, 6) == (54, 6)
    assert m.cogging_periods(12, 10) == (60, 2)
    # skew 20 deg electrical: sin(10 deg) / 0.17453 = 0.9949
    assert m.skew_factor(20) == pytest.approx(0.9949, abs=1e-4)
    assert m.skew_factor(0) == 1.0
