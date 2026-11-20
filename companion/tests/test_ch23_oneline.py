"""Tests for plantp.oneline and plantp.auxpower (chapter 23) against hand
calculations."""
import math

import pytest

from plantp import auxpower as ax
from plantp import oneline as ol


def small() -> ol.OneLine:
    g = ol.OneLine()
    g.add_bus(ol.Bus("G", 0.69, zone="Z1"), ol.Bus("MV", 33.0, zone="Z2"),
              ol.Bus("HV", 132.0, zone="Z3"),
              ol.Bus("POC", 132.0, owner="utility", zone="Z4"))
    g.add(ol.Branch("T1", "transformer", "G", "MV", zone="Z2",
                    rating={"hv_kv": 33.0, "lv_kv": 0.69}),
          ol.Branch("T2", "transformer", "MV", "HV", zone="Z3",
                    rating={"hv_kv": 132.0, "lv_kv": 33.0},
                    status={"z_pu": "provisional"}),
          ol.Branch("Q1", "breaker", "HV", "POC", zone="Z4", isolation=True,
                    meter="revenue", test="utility witnesses"))
    return g


def test_path_and_crossings():
    g = small()
    assert [b.tag for b in g.path("G", "POC")] == ["T1", "T2", "Q1"]
    notes = g.crossings("G", "POC")
    assert "T1: voltage 0.69 -> 33 kV" in notes
    assert "Q1: owner plant -> utility" in notes
    assert "Q1: isolation point" in notes and "Q1: revenue meter" in notes


def test_checks_find_planted_errors():
    g = small()
    assert g.checks() == []
    g.add(ol.Branch("T3", "transformer", "MV", "HV", rating={"hv_kv": 132.0, "lv_kv": 34.5}))
    g.add(ol.Branch("L9", "line", "HV", "POC", zone="Z4"))
    found = g.checks()
    assert any("T3: windings" in f for f in found)
    assert any("T3: in no protection zone" in f for f in found)
    assert any("L9: owner boundary without isolation point" in f for f in found)


def test_open_items_in_schedule():
    rows = small().schedule(kinds=["transformer"])
    assert rows[1][0] == "T2" and rows[1][4] == ["z_pu"]


def test_demand_kva():
    loads = [ax.Load("a", 10, 0.8, duty={"normal": 1.0}),
             ax.Load("b", 10, 1.0, duty={"normal": 0.5})]
    p, q, s = ax.demand(loads, "normal")
    assert p == pytest.approx(15.0) and q == pytest.approx(7.5)
    assert s == pytest.approx(math.hypot(15, 7.5))


def test_sizes_and_fault_current():
    assert ax.next_size(400, 0.2) == 500
    assert ax.sc_current_ka(1000, 0.4, 0.06) == pytest.approx(24.056, rel=1e-4)
    assert ax.start_dip(300, 1000, 0.06) == pytest.approx(300 / (1000 / 0.06 + 300))


def test_dc_and_ups():
    raw, sized = ax.battery_ah([(50, 60), (200, 1)])
    assert raw == pytest.approx(53.333, rel=1e-4)
    assert sized == pytest.approx(53.333 * 1.11 * 1.25 * 1.10, rel=1e-4)
    assert ax.charger_a(50, 100, 8) == pytest.approx(63.75)
    kva, kwh = ax.ups(10, 0.9, 30)
    assert kva == pytest.approx(13.889, rel=1e-4) and kwh == pytest.approx(5.435, rel=1e-3)


def test_shed_keeps_priorities():
    loads = [ax.Load("pump", 30, 1.0, duty={"emergency": 1}, priority=5),
             ax.Load("scada", 5, 1.0, duty={"emergency": 1}, priority=1),
             ax.Load("light", 10, 1.0, duty={"emergency": 1}, priority=3)]
    kept, cut, kva = ax.shed(loads, "emergency", 20)
    assert kept == ["scada", "light"] and cut == ["pump"] and kva == pytest.approx(15)


def test_hvac_and_timeline():
    q, e = ax.hvac_kw(20, 0.5, 45, 25, solar_kw=2)
    assert q == pytest.approx(32) and e == pytest.approx(32 / 3)
    rows, tot = ax.timeline([(0, "UPS", 6), (10, "gen", 0), (60, "end", 0)])
    assert tot == pytest.approx(1.0)
