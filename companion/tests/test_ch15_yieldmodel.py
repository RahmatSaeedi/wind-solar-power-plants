"""Tests of plantp.yieldmodel (chapter 15). Hand values in comments."""
import numpy as np
import pytest

from plantp import yieldmodel as ym


def test_waterfall_balances_and_shows_why_percentages_do_not_add():
    base = np.full(10, 100.0)
    wf = ym.Waterfall("t").start("gross", base)
    wf.apply("a 10 %", base * 0.9).apply("b 20 %", base * 0.9 * 0.8)
    t = wf.totals()
    assert t[1][2] == pytest.approx(10.0) and t[2][2] == pytest.approx(20.0)
    total, simple_sum = wf.check()
    # 1 - 0.9 x 0.8 = 0.28, not 0.30
    assert total == pytest.approx(0.28) and simple_sum == pytest.approx(0.30)


def test_monthly_export_and_soiling():
    m = ym.monthly([1, 2, 3, 4], [0, 0, 1, 11])
    assert m[0] == 3 and m[1] == 3 and m[11] == 4
    d, c = ym.export_limit([90, 110], 100.0)
    assert d.tolist() == [90, 100] and c.tolist() == [0, 10]
    rain = np.zeros(10)
    rain[5] = 10.0
    s = ym.soiling_loss(10, 0.01, rain, clean_days=[], recovery=1.0)
    # 0.01 .. 0.05 then reset on day 5, then 0.01 ..
    assert s[4] == pytest.approx(0.05) and s[5] == 0.0 and s[6] == pytest.approx(0.01)


def test_forecast_baselines_and_scores():
    obs = np.array([1.0, 2.0, 3.0, 4.0])
    f = ym.persistence(obs, 1)
    assert np.isnan(f[0]) and f[1:].tolist() == [1.0, 2.0, 3.0]
    sc = ym.scores(f, obs)
    assert sc["bias"] == pytest.approx(-1.0) and sc["rmse"] == pytest.approx(1.0) and sc["n"] == 3
    assert ym.skill(0.5, 1.0) == pytest.approx(0.5)
    clear = np.array([1.0, 2.0, 4.0, 4.0])
    sp = ym.smart_persistence(np.array([0.5, 1.0, 2.0, 2.0]), clear, 1)
    assert sp[2] == pytest.approx(2.0)                   # 4 x 1.0 / 2


def test_pinball_coverage_and_ramps():
    # tau 0.9, forecast 10, observation 12: loss 0.9 x 2 = 1.8; observation 8: 0.1 x 2 = 0.2
    assert ym.pinball([10, 10], [12, 8], 0.9) == pytest.approx(1.0)
    assert ym.coverage([0, 0], [1, 1], [0.5, 2.0]) == pytest.approx(0.5)
    ev = ym.ramps([0, 0, 10, 10, 0], 5.0)
    assert ev.tolist() == [0, 0, 1, 0, -1]
    t = ym.ramp_table(ev, np.array([0, 0, 1, 0, 0]))
    assert t["hits"] == 1 and t["misses"] == 1 and t["false"] == 0


def test_ac_from_dc_inverts_the_loss_model():
    c = (0.004, 0.006, 0.010)
    y = np.array([0.05, 0.3, 0.7, 1.0])
    x = y + c[0] + c[1] * y + c[2] * y * y
    assert np.allclose(ym.ac_from_dc(x, c), y)
    assert ym.ac_from_dc([0.003], c)[0] == 0.0          # below the no-load loss
