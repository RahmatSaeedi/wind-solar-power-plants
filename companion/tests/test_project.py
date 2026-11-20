"""Chapter 1 project calculations against hand-worked cases."""
import pytest

from plantp import project as pj

DEV = [
    pj.Activity("A", 3),
    pj.Activity("B", 14, ("A",)),
    pj.Activity("C", 12, ("A",)),
    pj.Activity("D", 8, ("A",)),
    pj.Activity("E", 12, ("A",)),
    pj.Activity("F", 6, ("D", "E")),
    pj.Activity("G", 2, ("B",)),
    pj.Activity("H", 6, ("G", "C")),
    pj.Activity("I", 4, ("F", "H")),
]


def test_critical_path_hand_case():
    r = pj.critical_path(DEV)
    assert r.project_duration == 29                      # 3 + 14 + 2 + 6 + 4
    assert r.critical_path == ["A", "B", "G", "H", "I"]
    assert r.total_float["C"] == 4                       # H can wait for G until month 19
    assert r.total_float["D"] == 8                       # F waits for E anyway (month 15), then 4 more
    assert r.total_float["E"] == 4
    assert r.total_float["F"] == 4
    assert r.early_start["F"] == 15 and r.early_start["I"] == 25


def test_critical_path_errors():
    with pytest.raises(ValueError):
        pj.critical_path([pj.Activity("A", 1, ("B",)), pj.Activity("B", 1, ("A",))])
    with pytest.raises(ValueError):
        pj.critical_path([pj.Activity("A", 1, ("Z",))])
    with pytest.raises(ValueError):
        pj.critical_path([pj.Activity("A", -1)])


def test_s_curve_shape():
    assert pj.s_curve(0, 10, 20) == 0.0
    assert pj.s_curve(30, 10, 20) == 1.0
    assert pj.s_curve(20, 10, 20) == pytest.approx(0.5)
    values = [pj.s_curve(t, 0, 10) for t in range(11)]
    assert all(b >= a for a, b in zip(values, values[1:]))


def test_risk_scoring():
    assert pj.risk_score(3, 5) == 15 and pj.risk_band(15) == "high"
    assert pj.risk_band(8) == "medium" and pj.risk_band(7) == "low"
    with pytest.raises(ValueError):
        pj.risk_score(0, 3)
