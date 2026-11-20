"""Chapter 46 cable, switchgear and panel checks against hand values and
planted faults. Pure helpers only."""
import pytest

from plantp import cablemfg as km


def test_resistance_correction_by_hand():
    assert km.r_to_20(0.0826, 25.0) == pytest.approx(0.0826 / (1 + 0.00403 * 5))
    assert km.r_to_20(0.08, 20.0) == pytest.approx(0.08)
    assert km.r_to_20(0.0748, 9.0) > 0.0748          # a cold reading rises


def test_schedule_checker_finds_each_fault():
    ends = {"A", "B", "C"}
    rows = [dict(id="W1", **{"from": "A"}, to="B", type="t", size_mm2=240,
                 length_m=500, cores=3),
            dict(id="W2", **{"from": "A"}, to="Z", type="t", size_mm2=240,
                 length_m=1.2, cores=3),
            dict(id="W2", **{"from": "B"}, to="C", type="", size_mm2="400mm2",
                 length_m=300, cores=3),
            dict(id="W4", **{"from": "B"}, to="C", type="t", size_mm2=300,
                 length_m=300, cores=3)]
    probs = km.check_schedule(rows, ends, {240, 400})
    kinds = sorted(p for _, p in probs)
    assert "length looks like km, not m" in kinds
    assert "unknown to 'Z'" in kinds
    assert "duplicate id" in kinds
    assert "missing type" in kinds
    assert "size as text '400mm2'" in kinds
    assert "size 300 not a design size" in kinds
    assert not [p for c, p in probs if c == "W1"]


def test_interlocks_correct_and_faulty():
    good = km.reachable()
    assert not (km.FORBIDDEN & good)
    assert len(good) == 6
    assert km.FORBIDDEN & km.reachable(faulty=True)
    assert not km.allowed((1, 0, 0), "ds_close")      # CB closed: DS locked
    assert not km.allowed((0, 1, 0), "es_close")      # DS closed: ES locked


def test_point_to_point_and_terminals():
    design = {frozenset(("A", "B")), frozenset(("C", "D"))}
    meas = {frozenset(("A", "B")), frozenset(("C", "E"))}
    r = km.point_to_point(design, meas)
    assert r["missing"] == [("C", "D")] and r["extra"] == [("C", "E")]
    out = km.terminal_check([("1", "X:1", "K:1"), ("2", "X:1", "K:2"), ("3", "", "K:3")])
    assert len(out) == 2


def test_pole_spread():
    assert km.pole_spread((55.3, 59.8, 55.2)) == pytest.approx(4.6)


def test_field_hand_values():
    import math
    # E at the conductor screen: U0 / (rc ln(ri/rc))
    assert km.field_kv_mm(19.05, 10.0, 10.0, 18.0) == pytest.approx(
        19.05 / (10.0 * math.log(1.8)))
    # the field falls as 1/r across the insulation
    e1 = km.field_kv_mm(19.05, 10.0, 10.0, 18.0)
    e2 = km.field_kv_mm(19.05, 18.0, 10.0, 18.0)
    assert e1 / e2 == pytest.approx(1.8)


def test_holm_scaling():
    r1 = km.holm_r(10e3, 2.8e-8, 0.4e9)
    assert km.holm_r(40e3, 2.8e-8, 0.4e9) == pytest.approx(r1 / 2)
    assert km.holm_r(10e3, 2.8e-8, 0.4e9, spots=4) == pytest.approx(r1 / 2)


def test_trend_exact_line():
    b, se = km.trend([0, 1, 2, 3], [1.0, 0.9, 0.8, 0.7])
    assert b == pytest.approx(-0.1) and se == pytest.approx(0.0, abs=1e-12)


def test_circuits_groups():
    g = km.circuits([("a", "b"), ("b", "c"), ("x", "y")])
    assert g == [{"a", "b", "c"}, {"x", "y"}]
