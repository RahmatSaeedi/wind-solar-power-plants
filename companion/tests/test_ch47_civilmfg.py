"""Chapter 47 civil and structural manufacture checks against hand values
and planted faults. Pure helpers only."""
from datetime import date

import pytest

from plantp import civilmfg as cv


def test_cev_by_hand():
    assert cv.cev(0.20, 1.55, cr=0.10, cu=0.10) == pytest.approx(
        0.20 + 1.55 / 6 + 0.10 / 5 + 0.10 / 15)


def test_cert_findings():
    order = dict(grade="S355", t_range=(20, 50), impact_c=-20, impact_j=27,
                 cev_max=0.43)
    good = dict(grade="S355", t_mm=40, impact_c=-20, impact_j=(40, 41, 42),
                chem=dict(c=0.15, mn=1.40))
    assert cv.check_cert(good, order) == []
    bad = dict(good, grade="S275", t_mm=60, impact_c=0, impact_j=(40, 20, 42),
               chem=dict(c=0.22, mn=1.6))
    out = " ".join(cv.check_cert(bad, order))
    for word in ("grade", "thickness", "impact tested", "impact energy", "CEV"):
        assert word in out


def test_welder_qualification():
    w = dict(quals={"SAW": dict(positions={"PA"}, expires=date(2027, 1, 1))})
    assert cv.qualified(w, "SAW", "PA", date(2026, 12, 1)) == "ok"
    assert "expired" in cv.qualified(w, "SAW", "PA", date(2027, 2, 1))
    assert "position" in cv.qualified(w, "SAW", "PF", date(2026, 12, 1))
    assert "FCAW" in cv.qualified(w, "FCAW", "PA", date(2026, 12, 1))


def test_bbs_checker_and_mass():
    rows = [dict(mark="A", dia=16, shape="00", length_mm=1000, number=10),
            dict(mark="A", dia=22, shape="99", length_mm=1.5, number=1),
            dict(mark="C", dia=16, shape="", length_mm=1000, number=1)]
    kinds = " ".join(p for _, p in cv.check_bbs(rows, {16}, {"00"}))
    for word in ("duplicate", "diameter", "shape code", "metres", "missing shape"):
        assert word in kinds
    assert cv.bar_mass(16) == pytest.approx(256 / 162)
    assert cv.bbs_mass(rows[:1]) == pytest.approx(10 * 256 / 162)


def test_ticket_and_conformity():
    t = dict(discharged_min=95, temp_c=33, water_added_l=20)
    assert len(cv.check_ticket(t, 90, 32, 0)) == 3
    c = cv.conformity([40.8, 30.2, 41.5], 35)
    assert not c["ok_mean"] and not c["ok_each"]
    assert cv.conformity([40, 41, 42], 35)["ok_mean"]


def test_straightness_and_ageing():
    off, x = cv.straightness([0, 5, 10], [0.0, 3.0, 0.0])
    assert off == pytest.approx(3.0) and x == 5
    ncrs = [dict(raised=date(2027, 1, 1), closed=False),
            dict(raised=date(2026, 9, 1), closed=False),
            dict(raised=date(2026, 9, 1), closed=True)]
    assert cv.ageing(ncrs, date(2027, 1, 15)) == {"<30": 1, "30-90": 0, ">90": 1}
