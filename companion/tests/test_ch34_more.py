"""Chapter 34, deeper lessons: hand checks of the phase margin, debounce,
CT class limits, hold-up time and bumpless transfer."""
import math

from companion.ch34 import examples_q as q
from companion.ch34 import examples_r as r
from companion.ch34 import examples_t as t


def test_crossover_and_margin_by_hand():
    # 4 w^4 - 1.25 w^2 - 0.64 = 0 for kp 1.5, ki 0.8, tau 2
    x = (1.25 + math.sqrt(1.25 ** 2 + 4 * 4 * 0.64)) / 8
    assert abs(r.crossover() - math.sqrt(x)) < 1e-6
    assert abs(r.margin_deg(0.0) - 88.3) < 0.1
    assert r.margin_deg(3.0) < 0 < r.margin_deg(1.5)


def test_debounce_gives_one_edge_after_the_hold():
    ticks, raw, _ = q.bounce_signal()
    out = q.debounce(raw, 100)
    assert int(abs(out[1:] - out[:-1]).sum()) == 1
    assert abs(ticks[out.argmax()] - 113.6) < 1e-9


def test_class_limits_interpolate_and_stop_below_range():
    assert q.class_limit(q.CLASS_02, 3.0) is None
    assert abs(q.class_limit(q.CLASS_02S, 3.0) - 0.55) < 1e-9
    assert q.class_limit(q.CLASS_02S, 100.0) == 0.2


def test_holdup_by_energy():
    ms = t.holdup_ms(940.0, 325.0, 200.0, 480.0)
    assert abs(ms - 0.5 * 940e-6 * 65625 / (480 / 0.9) * 1000) < 1e-9
    assert abs(t.holdup_ms(940.0, 325.0, 200.0, 240.0) - 2 * ms) < 1e-9


def test_bumpless_transfer_has_no_step():
    assert r.transfer("set point ramps")[0] == 40.0
    assert r.transfer("integrator tracks")[0] == 70.0
    assert r.transfer("no tracking")[0] == 30.0
