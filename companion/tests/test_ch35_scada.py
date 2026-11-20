"""Chapter 35 SCADA and communications module against hand calculations."""
import pytest

from plantp import scada as sc


def test_link():
    assert sc.serialisation_ms(125, 1_000_000) == pytest.approx(1.0)
    assert sc.utilisation(100, 125, 1_000_000) == pytest.approx(0.1)
    # 10 devices, 8 + 25 bytes at 9600 bit/s, 10 ms turnaround
    per_ms = (8 + 25) * 8 / 9600 * 1000 + 10
    assert sc.polling_cycle_s(10, 8, 25, 9600, 10) == pytest.approx(10 * per_ms / 1000)
    assert sc.rbe_rate(3600, 2) == pytest.approx(2.0)


def test_topology():
    assert sc.star_availability(0.99, 1.0, 2) == pytest.approx(0.9801)
    # ring of 4 links, device in the middle: two paths of 2 links each
    a = sc.ring_device_availability(0.99, 3)
    assert a == pytest.approx(1 - (1 - 0.99 ** 2) ** 2)
    assert sc.nines(0.999) == pytest.approx(3.0)


def test_budgets():
    assert sc.fibre_budget_db(10, 4, 2) == pytest.approx(3.5 + 0.4 + 1.0 + 3.0)
    assert sc.sync_budget_us([1, -2, 0.5]) == pytest.approx(3.5)
    assert sc.retention_gb(1000, 1, 1) == pytest.approx(1000 * 31_536_000 * 12 / 1e9)


def test_tags_and_scaling():
    assert sc.tag_ok("PLP-E1-VT.Voltage")
    assert not sc.tag_ok("plp-e1-vt.voltage")
    assert not sc.tag_ok("PLP-E1-VT")
    assert sc.scaling_suspect(1320.0, 0.0, 150.0)          # kV sent x 10
    assert not sc.scaling_suspect(132.0, 0.0, 150.0)
    assert not sc.scaling_suspect(-500.0, 0.0, 150.0)


def test_stale_and_alarm():
    assert sc.stale([0.0, 5.0], 20.0, 10.0)
    assert not sc.stale([0.0, 15.0], 20.0, 10.0)
    states = sc.alarm_states([0, 11, 11, 11, 9.5, 11, 8, 0], 10, 1, 2)
    assert states == [False, False, True, True, True, True, False, False]
    assert sc.transitions(states) == 1
