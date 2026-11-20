"""Chapter 32 safety module against hand calculations."""
import pytest

from plantp import safety as sf


def test_risk_matrix():
    assert sf.risk_score(3, 4) == 12
    assert sf.risk_band(12) == "high"
    assert sf.risk_band(4) == "low"
    assert sf.risk_band(20) == "very high"
    with pytest.raises(ValueError):
        sf.risk_score(0, 3)


def test_incident_rate():
    r, lo, hi = sf.incident_rate(4, 400_000.0)
    assert r == pytest.approx(2.0)
    assert lo < r < hi
    r0, lo0, hi0 = sf.incident_rate(0, 200_000.0)
    assert r0 == 0.0 and lo0 == 0.0
    assert hi0 == pytest.approx(2.996, rel=1e-3)      # -ln(0.05) for 90 %


def test_height_and_air():
    assert sf.fall_clearance(1.8, 1.75) == pytest.approx(1.8 + 1.75 + 0.3 + 1.5 + 1.0)
    assert sf.air_changes(50.0, 300.0) == pytest.approx(6.0)
    assert sf.dilution_flow(0.1, 0.01, 2.0) == pytest.approx(20.0)


def test_fire_and_coverage():
    q = sf.heat_flux_point(10_000.0, 0.3, 10.0)
    assert q == pytest.approx(0.3 * 10_000 / (4 * 3.14159265 * 100), rel=1e-6)
    assert sf.distance_for_flux(10_000.0, 0.3, q) == pytest.approx(10.0)
    assert sf.autonomy_minutes(180.0, 3_000.0) == pytest.approx(60.0)
    assert sf.coverage_fraction([10, 20, 30, 40], 25) == pytest.approx(0.5)
