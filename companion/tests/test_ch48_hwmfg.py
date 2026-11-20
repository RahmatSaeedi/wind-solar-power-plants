"""Chapter 48 hardware checks against hand values and planted faults.
Pure helpers only."""
import math

import pytest

from plantp import hwmfg as hw


def test_error_budget_by_hand():
    spec = dict(acc_rdg=1.5, tc_rdg=0.04, t_ref=20, drift_rdg_yr=0.5, nl_fs=0.2)
    b = hw.error_budget(spec, 45.0, 2.0, 1000.0, 2000.0)
    assert b["terms"]["accuracy"] == pytest.approx(15.0)
    assert b["terms"]["temperature"] == pytest.approx(10.0)
    assert b["terms"]["drift"] == pytest.approx(10.0)
    assert b["terms"]["linearity"] == pytest.approx(4.0)
    assert b["rss"] == pytest.approx(math.sqrt(15**2 + 10**2 + 10**2 + 4**2))
    assert b["worst"] == pytest.approx(39.0)


def test_tag_checker_finds_each_fault():
    units = {"power": {"MW"}, "speed": {"m/s"}}
    good = dict(tag="A", kind="power", unit="MW", lo=0, hi=100, alarm_lo=5,
                alarm_hi=90, deadband=1)
    rows = [good,
            dict(good, tag="B", unit="km/h", kind="speed"),
            dict(good, tag="C", lo=100, hi=0),
            dict(good, tag="D", alarm_lo=95, alarm_hi=90),
            dict(good, tag="E", deadband=20),
            dict(good, tag="A"),
            dict(good, tag="F", deadband="")]
    kinds = " ".join(p for _, p in hw.check_tags(rows, units))
    for word in ("does not fit", "low >= high", "out of order", "deadband 20",
                 "duplicate", "missing deadband"):
        assert word in kinds
    assert not [p for t, p in hw.check_tags([good], units)]


def test_port_diff():
    plan = {("S", 1): dict(far="a", vlan=10), ("S", 2): dict(far="b", vlan=20)}
    act = {("S", 1): dict(far="a", vlan=20), ("S", 3): dict(far="c", vlan=1)}
    d = hw.diff_ports(plan, act)
    assert d["missing"] == [("S", 2)] and d["extra"] == [("S", 3)]
    assert d["changed"] == [(("S", 1), "vlan", 10, 20)]


def test_link_firmware_clocks_chain():
    assert hw.link_check(1.4, 7.0, 1.5) == "ok"
    assert hw.link_check(1.4, 7.0, 2.9) == "suspect"
    assert hw.link_check(5.0, 7.0, 7.4) == "fail"
    f = hw.firmware_check({"a": ("M", "1"), "b": ("M", "2"), "c": ("N", "1")},
                          {"M": "1"})
    assert f == [("b", "2 (approved 1)"), ("c", "model N not in the baseline")]
    o = hw.offsets({"x": 0.5, "y": -3.0}, 2.0)
    assert o["beyond"] == ["y"] and o["worst"] == pytest.approx(3.0)
    rss, worst = hw.chain_error(0.2, 0.2, 0.2)
    assert rss == pytest.approx(math.sqrt(0.12)) and worst == pytest.approx(0.6)
