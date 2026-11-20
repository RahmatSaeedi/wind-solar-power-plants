"""Tests of plantp.pe and plantp.mppt (chapter 9). Hand values in comments."""
import math

import numpy as np
import pytest

from plantp import mppt as mp
from plantp import pe


def test_dcdc_and_rectifier():
    assert pe.buck_duty(1000, 400) == pytest.approx(0.4)
    assert pe.boost_duty(600, 1000) == pytest.approx(0.4)
    # buck ripple 1000 x 0.4 x 0.6 / (1 mH x 10 kHz) = 24 A
    assert pe.buck_ripple(1000, 0.4, 1e-3, 10e3) == pytest.approx(24.0)
    assert pe.boost_ripple(600, 0.4, 1e-3, 10e3) == pytest.approx(24.0)
    assert pe.boost_cap_ripple(10, 0.4, 100e-6, 10e3) == pytest.approx(4.0)
    with pytest.raises(ValueError):
        pe.buck_duty(400, 1000)
    # six-pulse bridge: 1.3505 x 400 = 540.2 V
    assert pe.rectifier_6p_vdc(400) == pytest.approx(540.2, abs=0.1)
    # 0.1 mH, 100 A, 50 Hz: drop 3 x 314.16 x 1e-4 x 100 / pi = 3.0 V
    assert pe.rectifier_6p_vdc(400, 1e-4, 100) == pytest.approx(537.2, abs=0.1)
    assert pe.rectifier_6p_vdc(400, alpha_deg=60) == pytest.approx(270.1, abs=0.1)


def test_dc_voltage_window():
    # sqrt2 x 690 = 975.8 V; sine-triangle 2 sqrt2 690 / sqrt3 = 1126.8 V
    assert pe.vdc_min(690) == pytest.approx(975.8, abs=0.1)
    assert pe.vdc_min(690, "spwm") == pytest.approx(1126.8, abs=0.1)
    assert pe.vll_max(850) == pytest.approx(601.0, abs=0.1)
    assert pe.vdc_min(690, headroom=0.1) == pytest.approx(1073.4, abs=0.1)
    with pytest.raises(ValueError):
        pe.vdc_min(690, "other")


def test_pwm_spectrum():
    t, s = pe.spwm_leg(0.9, 50, 2550, n=51000)
    h, a = pe.spectrum(s, 50)
    assert a[0] == pytest.approx(0.5, abs=1e-3)            # mean of a 0/1 leg
    assert a[1] == pytest.approx(0.45, abs=2e-3)           # m / 2
    assert a[2:40].max() < 0.01                            # clean low orders
    t3, s3 = pe.spwm_leg(0.9, 50, 2550, n=51000, levels=3)
    h3, a3 = pe.spectrum(s3, 50)
    assert a3[1] == pytest.approx(0.9, abs=3e-3)           # m (levels -1..1)
    assert pe.thd([0, 1.0, 0, 0.3, 0, 0.4]) == pytest.approx(0.5)


def test_losses_closed_form_matches_numeric():
    dev = dict(v_t0=0.8, r_t=0.6e-3, v_d0=0.9, r_d=0.5e-3, e_on_off=0.25,
               e_rr=0.08, i_ref=1000, v_ref=900)
    ct, cd = pe.conduction_losses(1414, 0.95, 0.95, 0.8, 0.6e-3, 0.9, 0.5e-3)
    st, sd = pe.switching_losses(1414, 1100, 3000, 0.25, 0.08, 1000, 900)
    num = pe.leg_losses_numeric(1414, 0.95, math.degrees(math.acos(0.95)),
                                1100, 3000, dev)
    assert num["cond_t"] == pytest.approx(ct, rel=1e-3)
    assert num["cond_d"] == pytest.approx(cd, rel=1e-3)
    assert num["sw_t"] == pytest.approx(st, rel=1e-3)
    assert num["sw_d"] == pytest.approx(sd, rel=1e-3)
    # switching: 3000 x 0.25 x 1.414 x 1.222 / pi = 412.6 W
    assert st == pytest.approx(412.6, abs=0.2)


def test_dclink():
    # closed form against the switched simulation (linear range)
    for m, phi in ((1.0, 0), (0.8, 0), (0.5, 60)):
        a = pe.dclink_ripple_current_rms(1.0, m, math.cos(math.radians(phi)))
        assert pe.dclink_ripple_current_numeric(m, phi) == pytest.approx(a, rel=2e-3)
    # 5 MW for 10 ms from 1100 to 1000 V: 2 x 5e6 x 0.01 / 210000 = 0.476 F
    assert pe.dclink_c_for_holdup(5e6, 0.01, 1100, 1000) == pytest.approx(0.476, abs=1e-3)
    assert pe.capacitor_energy_j(0.1, 1000) == pytest.approx(50e3)


def test_thermal():
    assert pe.tj_steady(1000, 0.02, 0.01, 0.04, 40) == pytest.approx(110.0)
    # Foster step settles at sum(R) P
    assert pe.foster_step(100, [0.1, 0.2], [0.01, 1.0], 100.0) == pytest.approx(30.0)
    sim = pe.foster_sim(np.full(20000, 100.0), 1e-3, [0.1, 0.2], [0.01, 1.0])
    ref = pe.foster_step(100, [0.1, 0.2], [0.01, 1.0], 20.0)
    assert sim[-1] == pytest.approx(ref, rel=1e-6)
    assert pe.relative_cycle_life(40, 20) == pytest.approx(1 / 32)


def test_efficiency_and_derating():
    pts = [(0.1, 0.96), (0.5, 0.985), (1.0, 0.982)]
    c = pe.fit_loss_coeffs(pts)
    for p, e in pts:
        assert float(pe.efficiency_from_coeffs(p, c)) == pytest.approx(e, abs=1e-9)
    assert sum(pe.EURO_WEIGHTS.values()) == pytest.approx(1.0)
    assert sum(pe.CEC_WEIGHTS.values()) == pytest.approx(1.0)
    e_euro = pe.weighted_efficiency(c, pe.EURO_WEIGHTS)
    assert 0.96 < e_euro < 0.986
    assert float(pe.derating(40)) == pytest.approx(1.0)
    assert float(pe.derating(50)) == pytest.approx(0.8)          # 2 %/K x 10 K
    assert float(pe.derating(30, altitude_m=2000)) == pytest.approx(0.9)


def test_filter_frt_components():
    # LCL 0.1 mH, 0.05 mH, 100 uF: f = sqrt(1.5e-4 / (5e-9 x 1e-4)) / 2 pi
    f_r = pe.lcl_resonance(1e-4, 5e-5, 1e-4)
    assert f_r == pytest.approx(math.sqrt(1.5e-4 / 5e-13) / (2 * math.pi))
    low = pe.lcl_gain(50.0, 1e-4, 5e-5, 1e-4)
    assert float(low) == pytest.approx(1 / (2 * math.pi * 50 * 1.5e-4), rel=0.02)
    assert float(pe.lcl_gain(f_r, 1e-4, 5e-5, 1e-4, r_d=0.0)) > 1e3 * float(low)
    assert pe.l_for_ripple(1100, 3000, 200) == pytest.approx(1100 / 4.8e6)
    assert pe.frt_currents(1.0) == (0.0, 1.0)
    iq, ip = pe.frt_currents(0.5, k=2.0, i_max=1.1)
    assert iq == pytest.approx(1.0) and ip == pytest.approx(math.sqrt(0.21))
    assert pe.frt_currents(0.2)[0] == pytest.approx(1.1)          # capped
    assert pe.overshoot_v(30e-9, 5e9) == pytest.approx(150.0)
    assert pe.gate_drive_power(10e-6, 23, 3000) == pytest.approx(0.69)
    assert pe.deadtime_error(1100, 3e-6, 3000) == pytest.approx(9.9)


def test_pv_curve_model():
    c = mp.PVM_550.at(1000, 25)
    assert float(c.i(0)) == pytest.approx(13.98)
    assert float(c.i(41.96)) == pytest.approx(13.11, rel=1e-6)
    assert float(c.i(49.90)) == pytest.approx(0.0, abs=1e-6)
    assert float(c.v(13.11)) == pytest.approx(41.96, rel=1e-6)
    v, p = c.mpp()
    assert p == pytest.approx(550.1, abs=0.5)
    s = mp.PVM_550.at(1000, 71, 26)
    # P_mp follows gamma: 0.35 %/K over 46 K -> 0.839 of 14.30 kW (+-1 %)
    assert s.vmp * s.imp == pytest.approx(14302.5 * 0.839, rel=0.01)
    with pytest.raises(ValueError):
        mp.PVM_550.at(0, 25)
    assert float(mp.cell_temperature(20, 800)) == pytest.approx(45.0)


def test_partial_shading_and_trackers():
    sun = mp.PVM_550.at(1000, 50, 13)
    shade = mp.PVM_550.at(300, 35, 13)
    v, i, p = mp.pv_curve_partial([sun, shade])
    # two peaks: one near the full-string voltage, one near half of it
    k = int(np.argmax(p))
    assert p[k] > 0.9 * sun.vmp * sun.imp            # the global peak
    # P&O converges near the MPP of an unshaded curve
    c = mp.PVM_550.at(800, 45, 26)
    v_mpp, p_mpp = c.mpp()
    po = mp.PerturbObserve(v_ref=0.8 * c.voc, step=2.0)
    v_op = po.v_ref
    for _ in range(400):
        v_op = po.update(v_op, float(c.i(v_op)))
    assert float(c.p(v_op)) == pytest.approx(p_mpp, rel=0.005)
    ic = mp.IncrementalConductance(v_ref=0.8 * c.voc, step=2.0)
    v_op = ic.v_ref
    for _ in range(400):
        v_op = ic.update(v_op, float(c.i(v_op)))
    assert float(c.p(v_op)) == pytest.approx(p_mpp, rel=0.005)
    assert mp.global_scan(lambda x: float(c.i(x)), 0, c.voc, 200) == \
        pytest.approx(v_mpp, rel=0.02)


def test_switched_leg_and_npc():
    dev = dict(v_t0=0.9, r_t=0.55e-3, v_d0=0.95, r_d=0.45e-3, e_on_off=1.6,
               e_rr=0.35, i_ref=3600, v_ref=900)
    i_pk, m, phi = 6224.0, 0.98, math.degrees(math.acos(0.95))
    ct, cd = pe.conduction_losses(i_pk, m, 0.95, 0.9, 0.55e-3, 0.95, 0.45e-3)
    st, sd = pe.switching_losses(i_pk, 1150, 2500, 1.6, 0.35, 3600, 900)
    r = pe.leg_losses_switched(i_pk, m, phi, 1150, 2500, 100e-6, dev)
    total = r["cond_t"] + r["cond_d"] + r["sw_t"] + r["sw_d"]
    assert total == pytest.approx(ct + cd + st + sd, rel=0.03)
    # one leg against the DC midpoint: at most V_dc / (4 L f) peak-to-peak
    assert r["ripple_pp"] < 1.01 * 1150 / (4 * 100e-6 * 2500)
    npc = dict(v_t0=0.75, r_t=0.35e-3, v_d0=0.8, r_d=0.3e-3, e_on_off=0.9,
               e_rr=0.2, i_ref=2800, v_ref=600)
    leg = pe.npc_leg_losses(1871, 0.9, 0.0, 1000, 3000, npc)
    assert leg["T1"] == pytest.approx(leg["T4"], rel=1e-3)
    assert leg["T2"] == pytest.approx(leg["T3"], rel=1e-3)
    assert leg["D5"] == pytest.approx(leg["D6"], rel=1e-3)
    for d in ("D1", "D2", "D3", "D4"):
        assert leg[d] == pytest.approx(0.0, abs=1e-9)    # unity power factor
    lagging = pe.npc_leg_losses(1871, 0.9, 30.0, 1000, 3000, npc)
    assert lagging["D1"] > 0 and lagging["T3"] > leg["T3"] * 0.5
