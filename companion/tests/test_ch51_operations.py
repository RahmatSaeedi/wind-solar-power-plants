"""Tests for plantp.operations (chapter 51): hand-checked cases and edges."""
from __future__ import annotations

import math
from datetime import date

import numpy as np
import pytest

from plantp import operations as op


def test_check_log():
    entries = [dict(hour=1, a="x", b=""), dict(hour=3, a="y", b="z")]
    out = op.check_log(entries, ["a", "b"], hours=range(4))
    assert out["missing"] == [(1, "b")]
    assert out["silent"] == [0, 2]


def test_lost_energy_by_cause():
    avail = [10, 10, 10, 10]
    exp = [10, 8, 5, 12]
    out = op.lost_energy(avail, exp, {1: "cap"})
    assert out == {"cap": 2.0, "unexplained": 5.0}          # a surplus is not a loss


def test_rolling_bias_and_service():
    b = op.rolling_bias([2, 2, 2, 4], [1, 1, 1, 1], 2)
    assert np.allclose(b, [1, 1, 2])
    assert op.service_availability([1, 0, 1, 1], [1, 1, 0, 0]) == 0.5
    assert math.isnan(op.service_availability([1], [0]))


def test_stale_and_autonomy():
    recs = {"a": date(2029, 1, 1), "b": date(2027, 1, 1), "c": None}
    assert op.stale(recs, date(2029, 6, 1), 365) == ["b", "c"]
    assert op.autonomy_h(10.0, 2.0) == pytest.approx(4.0)
    assert op.autonomy_h(10.0, 2.0, reserve=0.0) == pytest.approx(5.0)
