"""Tests for plantp.commissioning (chapter 50): hand-checked cases and edges."""
from __future__ import annotations

import pytest

from plantp import commissioning as cm
from plantp import pvcell


def test_string_expected_matches_module_model():
    v, i = cm.string_expected(26, 1000.0, 25.0)
    assert v == pytest.approx(26 * pvcell.PVM_550_DS.voc, rel=2e-3)
    assert i == pytest.approx(pvcell.PVM_550_DS.isc, rel=2e-3)
    v2, i2 = cm.string_expected(26, 500.0, 25.0)
    assert i2 == pytest.approx(i / 2, rel=0.01) and v2 < v


def test_string_check_verdicts():
    v, i = 1217.0, 11.58
    assert cm.string_check(v, i, v, i, 26) == "ok"
    assert cm.string_check(-v, i, v, i, 26) == "reversed polarity"
    assert "1 module" in cm.string_check(v * 25 / 26, i, v, i, 26)
    assert "2 module" in cm.string_check(v * 24 / 26, i, v, i, 26)
    assert cm.string_check(v * 0.5, i, v, i, 26) == "voltage off"
    assert cm.string_check(v, 0.9 * i, v, i, 26) == "low current"


def test_below_and_relays():
    assert cm.below({"a": 50, "b": 3, "c": None}, 40) == ["b", "c"]
    t = 0.2 * 0.14 / (5 ** 0.02 - 1)
    ok = [("r1", 5.0, 1.0, 0.2, t)]
    assert cm.relay_check(ok) == []
    edge = [("r2", 5.0, 1.0, 0.2, t + 0.05 * t + 0.039)]
    assert cm.relay_check(edge) == []
    out = [("r3", 5.0, 1.0, 0.2, t + 0.05 * t + 0.041), ("r4", 5.0, 1.0, 0.2, None)]
    assert [b[0] for b in cm.relay_check(out)] == ["r3", "r4"]


def test_cause_effect_and_validate():
    share, miss = cm.cause_effect({"c1": {"e1", "e2"}, "c2": {"e1"}}, {("c1", "e1"), ("c2", "e1")})
    assert share == pytest.approx(2 / 3) and miss == [("c1", "e2")]
    rows = [dict(k="a", f="x", r="ok"), dict(k="a", f="", r="bad")]
    out = cm.validate(rows, ["f"], "k", {"r": {"ok"}})
    assert out["missing"] == [("a", "f")]
    assert out["duplicate"] == [("a", "k")]
    assert out["dangling"] == [("a", "r")]


def test_trace_and_autonomy():
    t = cm.trace({"R1": "", "R2": "", "R3": ""}, {"R1": ("p", "pass"), "R2": ("p", None)})
    assert t == dict(untested=["R3"], open=["R2"], failed=[])
    assert cm.autonomy_ok(30, 30) and not cm.autonomy_ok(29.9, 30)
