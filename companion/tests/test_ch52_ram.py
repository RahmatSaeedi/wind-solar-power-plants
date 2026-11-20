"""Chapter 52 RAM helpers against hand calculations."""
import math

import pytest

from plantp import ram


def test_availability_types():
    assert ram.a_inherent(990, 10) == pytest.approx(0.99)
    assert ram.a_achieved(900, 12) == pytest.approx(900 / 912)
    assert ram.a_operational(900, 60) == pytest.approx(0.9375)


def test_blocks_by_hand():
    assert ram.series([0.9, 0.95]) == pytest.approx(0.855)
    assert ram.parallel([0.9, 0.9]) == pytest.approx(0.99)
    # 2 of 3 at 0.9: 3*0.81*0.1 + 0.729 = 0.972
    assert ram.k_of_n(2, 3, 0.9) == pytest.approx(0.972)
    assert ram.k_of_n(1, 2, 0.9) == pytest.approx(0.99)


def test_rbd_matches_blocks():
    v = {"a": 0.9, "b": 0.9, "c": 0.95}
    node = ("s", [("p", ["a", "b"]), "c"])
    assert ram.rbd(node, v) == pytest.approx(0.99 * 0.95)
    k = ("k", 2, ["a", "b", "c"])
    # by hand: all up + exactly one down
    hand = 0.9 * 0.9 * 0.95 + 0.1 * 0.9 * 0.95 * 2 + 0.9 * 0.9 * 0.05
    assert ram.rbd(k, v) == pytest.approx(hand)


def test_cut_sets_and_top():
    tree = ("or", [("and", ["p1", "p2"]), "bus", ("and", ["p1", "bus"])])
    cuts = ram.cut_sets(tree)
    assert cuts == [frozenset({"bus"}), frozenset({"p1", "p2"})]
    q = {"p1": 0.1, "p2": 0.1, "bus": 0.01}
    assert ram.top_rare(cuts, q) == pytest.approx(0.02)
    # exact: 1 - (1 - 0.01)(1 - 0.01) = 0.0199
    assert ram.top_exact(tree, q) == pytest.approx(0.0199)


def test_ccf_pair():
    # beta 0 gives q^2; beta 1 gives q
    assert ram.pair_with_ccf(0.1, 0.0) == pytest.approx(0.01)
    assert ram.pair_with_ccf(0.1, 1.0) == pytest.approx(0.1)
    # (0.9 x 0.01)^2 + 0.1 x 0.01 = 0.000081 + 0.001: the common part dominates
    assert ram.pair_with_ccf(0.01, 0.1) == pytest.approx(0.001081)


def test_weibull_and_age():
    assert float(ram.w_reliability(100, 1.0, 100)) == pytest.approx(math.exp(-1))
    assert ram.w_mean(1.0, 500) == pytest.approx(500)
    # constant hazard: replacing early never pays (rate falls as t grows)
    r1 = ram.age_replacement_rate(100, 1.0, 1000, 1, 5)
    r2 = ram.age_replacement_rate(2000, 1.0, 1000, 1, 5)
    assert r2 < r1
    # wear-out with dear failures: an optimum below the mean life exists
    rate, t = ram.best_age(3.0, 1000, 1, 10, range(100, 2001, 50))
    assert 200 < t < ram.w_mean(3.0, 1000)


def test_inspections_and_spares():
    # 1 - 0.5^n >= 0.9 -> n = 4
    assert ram.inspections_needed(0.5, 0.9) == 4
    # mean demand 0.5 in the lead time: P(0)=0.607, P(<=1)=0.910 -> 1 for 90 %
    assert ram.spares_needed(0.5 / 1000, 1000, 0.9) == 1
    assert ram.spares_needed(0.5 / 1000, 1000, 0.95) == 2


def test_simulate_spares_reduce_waiting():
    blk = {"x": dict(n=10, mtbf=2000, repair_h=10, stock=0, lead_h=500)}
    none = ram.simulate(blk, 87600, seed=3)["x"]
    blk["x"]["stock"] = 3
    some = ram.simulate(blk, 87600, seed=3)["x"]
    assert some["wait_h"] < none["wait_h"]
    assert some["failures"] == none["failures"]
