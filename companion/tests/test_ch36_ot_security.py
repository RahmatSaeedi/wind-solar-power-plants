"""Chapter 36: the defensive review tools against hand-worked cases."""
import math

import pytest

from plantp import ot_security as ot


def test_risk_scale_and_bands():
    assert ot.risk_score(3, 4) == 12
    assert [ot.risk_band(s) for s in (4, 5, 10, 15)] == ["low", "medium", "high", "very high"]
    with pytest.raises(ValueError):
        ot.risk_score(0, 3)


def test_default_deny_conduits():
    c = [{"src": "SCADA", "dst": "historian", "service": "historian-write"}]
    assert ot.allowed(c, "SCADA", "historian", "historian-write")
    assert not ot.allowed(c, "historian", "SCADA", "historian-write")


def test_rule_review_finds_each_kind():
    rules = [
        {"id": "R1", "src": "SCADA", "dst": "historian", "service": "hist", "action": "allow",
         "hits": 900, "purpose": "historian writes"},
        {"id": "R2", "src": "any", "dst": "any", "service": "remote", "action": "allow",
         "hits": 3, "purpose": ""},
        {"id": "R3", "src": "vendor", "dst": "any", "service": "remote", "action": "allow",
         "hits": 0, "purpose": "vendor access"},
    ]
    out = ot.review_rules(rules)
    assert out["any-any"] == ["R2"]
    assert out["shadowed"] == ["R3"]          # R2 matches everything R3 matches
    assert out["unused"] == ["R3"]
    assert out["undocumented"] == ["R2"]


def test_access_and_accounts():
    roles = {"operator": {"view", "ack", "operate"}}
    users = {"a": ("operator", {"view", "ack"}), "b": ("operator", {"view", "settings"})}
    assert ot.excess_rights(users, roles) == {"b": {"settings"}}
    assert ot.dormant({"a": 10, "b": 200}) == ["b"]


def test_inventory_patch_logs_recovery():
    items = [{"owner": "x", "firmware": "1.0"}, {"owner": "", "firmware": "2.1"}]
    assert ot.inventory_gaps(items, ("owner", "firmware")) == {"owner": 1, "firmware": 0}
    assert ot.patch_exposure_days(14, 90) == (59, 104)
    assert abs(ot.log_volume_gb(1e6, 500, 365) - 182.5) < 1e-9
    assert ot.recovery_time_h({"detect": 1, "rebuild": 6, "verify": 2}) == 9


def test_series_entropy_score():
    a, spof = ot.series_availability({"fw": 0.999, "sw": 0.9995})
    assert abs(a - 0.999 * 0.9995) < 1e-12 and spof == ["fw", "sw"]
    assert abs(ot.entropy_bits(26, 8) - 8 * math.log2(26)) < 1e-12
    assert ot.weighted_score({"q": 4, "s": 2}, {"q": 3, "s": 1}) == 3.5
