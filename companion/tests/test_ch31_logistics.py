"""Chapter 31 logistics module against hand calculations."""
import pytest

from plantp import logistics as lg


def test_axles_and_bridge():
    t, r = lg.axle_loads(60.0, 25.0, 30.0, 8)
    assert t == pytest.approx((25 + 15) * 9.81 / 3)
    assert r == pytest.approx((30 + 45) * 9.81 / 8)
    # point load (zero-length group) on a 20 m span: M = P L / 4
    assert lg.bridge_moment_ratio(1000.0, 0.0, 20.0, 5000.0) == pytest.approx(1.0)
    # uniform group over the whole span: M = P L / 8
    assert lg.bridge_moment_ratio(1000.0, 20.0, 20.0, 2500.0) == pytest.approx(1.0)


def test_convoy_and_crane():
    assert lg.convoy_time([(100, 50), (20, 10)], 1.0) == pytest.approx(5.0)
    chart = [(10, 100.0), (20, 50.0), (30, 20.0)]
    assert lg.chart_capacity(15, chart) == pytest.approx(75.0)
    assert lg.chart_capacity(35, chart) == 0.0
    assert lg.lift_utilisation(70, 5, 15, chart) == pytest.approx(1.0)
    assert lg.wind_on_load(10.0, 10.0, 1.0, 1.0) == pytest.approx(500.0)


def test_windows_and_misc():
    s = [5, 5, 5, 12, 5, 5, 5, 5, 5, 5]
    assert lg.weather_windows(s, 10, 3) == 3
    assert lg.desiccant_kg(10, 6) == pytest.approx(15.0)
    assert lg.laydown_area([10, 20], 1.5) == pytest.approx(45.0)
    assert lg.response_time(60, 60, 15, 30) == pytest.approx(105.0)
