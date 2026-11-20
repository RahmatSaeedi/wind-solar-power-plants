"""Chapter 39 procurement tools against hand-worked cases."""
import math

from plantp import procure as pr


def test_compliance():
    share, missed = pr.compliance({"r1": "comply", "r2": "deviate", "r3": "no",
                                   "r4": "comply"}, {"r2", "r4"})
    assert share == 0.5 and missed == ["r2"]


def test_evaluated_price():
    v = pr.evaluated_price(1000, 20, 300, 4, 10, 0.5, 0.1)
    assert math.isclose(v, 1000 + 20 + 300 + 40 + 50)


def test_ld_cap():
    amt, capped = pr.ld_amount(10, 0.005, 1000, 0.10)
    assert math.isclose(amt, 50) and not capped
    amt, capped = pr.ld_amount(30, 0.005, 1000, 0.10)
    assert math.isclose(amt, 100) and capped


def test_annuity_and_allocation():
    assert math.isclose(pr.annuity(0.07, 1), 1 / 1.07)
    a = pr.allocate_availability(0.98, 4)
    assert math.isclose(a ** 4, 0.98)


def test_audit_and_schedule():
    s, fails = pr.audit_score({"a": 4, "b": 2}, {"a": 1, "b": 1}, {"b": 3})
    assert s == 3 and fails == ["b"]
    share, bad = pr.schedule_completeness(["x", "y", "z"], {"x": True, "y": False})
    assert math.isclose(share, 1 / 3) and bad == ["y", "z"]


def test_interface_gaps():
    gaps = pr.interface_gaps({"EPC": {"grid tests", "spares"}},
                             {"O&M": {"spares"}, "grid": {"metering"}})
    assert gaps == {"EPC": ["grid tests"]}
