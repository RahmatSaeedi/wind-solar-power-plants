"""Chapter 33 environmental and social module against hand calculations."""
import math

import pytest

from plantp import envsocial as es


def test_sound():
    assert es.db_sum([40, 40]) == pytest.approx(43.01, abs=0.01)
    assert es.db_sum([50, 40]) == pytest.approx(50.41, abs=0.01)
    lp = es.noise_at(105, 500, alpha_db_km=2.0)
    assert lp == pytest.approx(105 - 20 * math.log10(500) - 11 - 1.0)


def test_birds_and_livelihood():
    assert es.collision_estimate(1000, 0.05, 0.98) == pytest.approx(1.0)
    assert es.livelihood_income(10, 2, 50) == pytest.approx(1000)


def test_lca():
    items = {"a": (10.0, 2.0), "b": (5.0, 1.0)}
    assert es.inventory_total(items) == pytest.approx(25.0)
    assert es.per_kwh(1000.0, 1e6) == pytest.approx(1.0)
    mc = es.inventory_mc({"a": (10.0, 2.0, 0.0)}, n=100)
    assert mc.mean() == pytest.approx(20.0)


def test_kpi():
    assert es.kpi_rag(95, 90, 5) == "green"
    assert es.kpi_rag(87, 90, 5) == "amber"
    assert es.kpi_rag(80, 90, 5) == "red"
    assert es.kpi_rag(12, 10, 5, higher_is_better=False) == "amber"


def test_carcass_and_background():
    # interval much shorter than persistence: nearly every carcass stays
    assert es.persistence_share(1000.0, 1.0) == pytest.approx(1.0, abs=1e-3)
    # interval equal to the mean persistence: (1 - e^-1) / 1
    assert es.persistence_share(10.0, 10.0) == pytest.approx(1 - math.exp(-1))
    est = es.fatality_estimate(2, 0.5, 10.0, 10.0, 0.5)
    assert est == pytest.approx(2 / (0.25 * (1 - math.exp(-1))))
    # 43 dB total over a 40 dB background leaves 40 dB for the source
    assert es.energy_difference_db(43.0103, 40.0) == pytest.approx(40.0, abs=0.01)


def test_transit():
    # zero pitch, bird as fast as the blade (a = 1): depth = chord
    p = es.transit_probability(10.0, 2.0, 0.0, 3, 1.0, 10.0, 0.5, 1.0)
    assert p == pytest.approx(3 * 1.0 / (2 * math.pi * 10.0) * (2.0 + 1.0))
    # a nearly stopped rotor: the share of the circle the blades block
    p0 = es.transit_probability(50.0, 2.0, 5.0, 3, 1e-6, 12.0, 0.6, 1.8)
    block = 3 * (2.0 * math.cos(math.radians(5.0)) + 1.8) / (2 * math.pi * 50.0)
    assert p0 == pytest.approx(block, rel=1e-3)
