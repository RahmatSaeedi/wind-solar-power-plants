"""Chapter 39 lab: the evaluation reaches the documented recommendation."""
from companion.ch39 import lab_d, sources as src
from plantp import procure as pr


def test_ub_not_acceptable():
    _, missed = pr.compliance(src.OFFERS["U-B"]["answers"], lab_d.CRITICAL)
    assert missed == ["T07", "T14"]
    _, fails = pr.audit_score(src.AUDITS["U-B"], src.AUDIT_WEIGHTS, src.AUDIT_FLOORS)
    assert fails == ["process control"]


def test_ranking():
    rows = lab_d.evaluated()
    order = sorted(rows, key=lambda k: rows[k]["total"])
    assert order == ["U-A", "U-C", "U-B"]
    assert min(rows, key=lambda k: rows[k]["price"]) == "U-B"


def test_data_schedule():
    share, bad = pr.schedule_completeness(src.DATA_ITEMS, src.DATA_COMMIT["U-A"])
    assert len(bad) == 1 and bad[0].startswith("I13")
