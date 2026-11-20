"""Chapter 34 instrumentation module against hand calculations."""
import math

import pytest

from plantp import instrumentation as ic


def test_scaling_and_loop():
    assert ic.ma_to_eng(12.0, 0.0, 150.0) == pytest.approx(75.0)
    assert ic.eng_to_ma(150.0, 0.0, 150.0) == pytest.approx(20.0)
    assert ic.ma_to_eng(ic.eng_to_ma(33.3, 0, 40), 0, 40) == pytest.approx(33.3)
    # 24 V, transmitter needs 12 V, 250 ohm receiver, 22 mA:
    # cable may have 12/0.022 - 250 = 295.45 ohm; 1.5 mm2 copper: 0.02333 ohm/m loop
    length = ic.loop_max_length(24.0, 12.0, 250.0, 1.5)
    assert length == pytest.approx((12 / 0.022 - 250) / (2 * 0.0175 / 1.5))


def test_adc_and_uncertainty():
    assert ic.adc_step(16.0, 16) == pytest.approx(16.0 / 65535)
    assert ic.combine(0.3, 0.4) == pytest.approx(0.5)


def test_rtd():
    assert ic.pt100_r(0.0) == pytest.approx(100.0)
    assert ic.pt100_r(100.0) == pytest.approx(138.5055, abs=1e-3)
    assert ic.pt100_t(ic.pt100_r(65.0)) == pytest.approx(65.0, abs=1e-9)
    assert ic.pt100_r(-50.0) < 100.0
    assert ic.lead_error_2wire(0.5) == pytest.approx(1.0 / 0.39083, rel=1e-6)


def test_time_filter_response():
    assert ic.clock_drift_s(20.0, 86400.0) == pytest.approx(1.728)
    assert ic.calibration_interval(0.5, 0.2, 0.1) == pytest.approx(2.0)
    y = ic.first_order_filter([0.0] + [1.0] * 2000, 0.01, 1.0)
    # after one time constant (100 samples) the discrete filter is near 63 %
    assert y[100] == pytest.approx(1 - math.exp(-1), abs=0.01)
    assert ic.response_budget(20, 50, 10, 30) == pytest.approx(160)


def test_pi_loop():
    y = ic.pi_loop(1.5, 0.8, 2.0, 0.1, 400)
    assert y[-1] == pytest.approx(1.0, abs=1e-3)          # integral action: no offset
    yt = ic.pi_loop(1.5, 0.8, 2.0, 0.1, 400, method="tustin")
    assert yt[-1] == pytest.approx(1.0, abs=1e-3)


def test_panel_io_power():
    assert ic.panel_rise_k(550.0, 10.0) == pytest.approx(10.0)
    assert ic.fan_flow_m3h(1206.0, 10.0) == pytest.approx(360.0, rel=1e-3)
    assert ic.modules_needed(100) == 8                     # 120 points / 16
    assert ic.autonomy_h(200.0, 40.0) == pytest.approx(4.0)
    a = ic.availability(9900.0, 100.0)
    assert a == pytest.approx(0.99)
    assert ic.parallel(a) == pytest.approx(0.9999)


def test_quality_and_setpoint():
    assert ic.quality(2.0, 0.0) == "bad"
    assert ic.quality(12.0, 30.0) == "stale"
    assert ic.quality(12.0, 1.0) == "good"
    assert ic.validate_setpoint(150.0, 0.0, 100.0, 80.0, 20.0) == (80.0, "out of range")
    assert ic.validate_setpoint(50.0, 0.0, 100.0, 80.0, 20.0) == (80.0, "step too large")
    assert ic.validate_setpoint(70.0, 0.0, 100.0, 80.0, 20.0) == (70.0, "accepted")
