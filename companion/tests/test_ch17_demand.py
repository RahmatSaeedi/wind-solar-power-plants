"""Tests of plantp.demand (chapter 17). Hand values in comments."""
import numpy as np
import pytest

from plantp import demand as dm


def test_metrics_and_duration():
    p = np.array([10.0, 20.0, 30.0, 40.0])
    m = dm.metrics(p)
    assert m["energy"] == 100.0 and m["peak"] == 40.0 and m["min"] == 10.0
    assert m["load_factor"] == pytest.approx(25 / 40)           # mean 25
    assert m["peak_at"] == 3
    assert list(dm.duration_curve(p)) == [40, 30, 20, 10]
    assert dm.metrics(p, dt_h=0.25)["energy"] == 25.0           # quarter hours


def test_peak_by_resolution_and_diversity():
    q = np.array([10, 30, 10, 30, 20, 20, 20, 20], float)
    assert q.max() == 30
    assert dm.peak_by_resolution(q, 4) == 20.0                   # both hour means 20
    a = np.array([10.0, 0.0])
    b = np.array([0.0, 10.0])
    cf, df = dm.diversity([a, b])
    assert cf == pytest.approx(0.5) and df == pytest.approx(2.0)


def test_growth_and_critical_hours():
    assert dm.grow([100.0], 0.03, 10)[0] == pytest.approx(134.39, abs=0.01)
    # 40 MWh x 0.8 x 0.93 / 0.2 MW = 148.8 h
    assert dm.critical_hours(0.2, 40, 20) == pytest.approx(148.8)
    assert dm.critical_hours(25, 40, 20) == 0.0                  # above the power


def test_node_checks():
    assert dm.net_flow([30.0], [100.0])[0] == 70.0
    # (0.847 x 100) / 132^2 = 0.486 %
    assert float(dm.voltage_rise(100, 0, 0.847, 2.824, 132)) == pytest.approx(0.486, abs=1e-3)
    assert dm.thermal_ok([105.3, -50], 140) and not dm.thermal_ok([150], 140)
    assert dm.short_circuit_ratio(1500, 100) == 15.0


def test_requirement_measurable():
    r = dm.Requirement("R1", "export", "<= 100 MW", "offer")
    w = dm.Requirement("R2", "easy to run", "", "O&M")
    assert r.is_measurable() and not w.is_measurable()
    assert r.status == "assumed" and r.links == []
