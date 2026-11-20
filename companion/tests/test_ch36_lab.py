"""Chapter 36 lab D: the design review finds exactly the planted findings
(synthetic tables only; nothing touches a network)."""
from companion.ch36 import examples_p as p
from companion.ch36 import lab_d
from companion.ch36 import sources as src


def test_unlisted_flows_are_the_two_planted():
    bad = lab_d.unlisted_flows(src.FLOW_LOG, src.CONDUITS)
    assert [(s, d) for s, d, _, _ in bad] == [("business", "control"),
                                              ("field-pv", "business")]


def test_single_points_of_failure():
    targets = ["field-ied", "field-wtg", "field-pv", "field-bes", "dmz", "business"]
    sp = lab_d.single_points(src.LINKS, "control", targets)
    assert sp == {"FW-PAIR": ["dmz", "business"], "SW-CORE-A": ["field-pv", "field-bes"]}


def test_recovery_order_critical_path():
    finish = {}
    for name, h, need in p.DEPS:
        finish[name] = max((finish[n] for n in need), default=0.0) + h
    assert abs(finish["HMIs"] - 13.4) < 1e-9
    assert abs(finish["historian"] - 27.2) < 1e-9
