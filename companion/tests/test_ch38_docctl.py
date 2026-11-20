"""Chapter 38 document-control tools against hand-worked cases."""
import math

from plantp import docctl as dc


def test_ids_and_revisions():
    assert dc.id_ok("PLP-ELE-DWG-0005")
    assert not dc.id_ok("PLP-ELX-DWG-0005")
    assert not dc.id_ok("PLP-ELE-DWG-05")
    assert dc.rev_ok("B", "IFR") and not dc.rev_ok("1", "IFR")
    assert dc.rev_ok("0", "IFC") and not dc.rev_ok("C", "IFC")


def test_transitions():
    assert dc.transition_ok("IFA", "APP")
    assert not dc.transition_ok("IFR", "IFC")      # skips approval
    assert dc.transition_ok("IFC", "SUP")


def test_stale_and_missing_references():
    cur = {"A": "2", "B": "0"}
    refs = [("X", "A", "2"), ("X", "A", "1"), ("X", "C", "0")]
    out = dc.stale_references(cur, refs)
    assert out == [("X", "A", "1", "2"), ("X", "C", "0", None)]


def test_completeness_and_mismatches():
    share, miss = dc.completeness([{"id": 1, "a": 1, "b": ""}, {"id": 2, "a": 2, "b": 3}],
                                  ["a", "b"])
    assert share == 0.75 and miss == {1: ["b"]}
    a = {"T1": {"mva": 6.3}, "T2": {"mva": 6.3}}
    b = {"T1": {"mva": 6.3}, "T2": {"mva": 5.0}, "T3": {"mva": 1.0}}
    out = dc.mismatches(a, b, ["mva"])
    assert ("T2", "mva", 6.3, 5.0) in out and ("T3", "missing", False, True) in out


def test_rvtm_and_impact():
    r = dc.rvtm(["R1", "R2"], {"R1": ["D1"]}, {"R1": ["T1"], "R2": ["T2"]}, {})
    assert r["share"] == {"design": 0.5, "verification": 1.0, "evidence": 0.0}
    g = {"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}
    assert dc.impacted(g, "a") == ["b", "c", "d"]


def test_controls():
    e = dc.earned_value(100, 80, 100, 1000)
    assert math.isclose(e["spi"], 0.8) and math.isclose(e["cpi"], 0.8)
    assert math.isclose(e["eac"], 1250)
    assert dc.ageing([1, 8, 40, 70]) == {"0-7": 1, "7-14": 1, "14-30": 0, "30-60": 1, ">=60": 1}
    # 2 errors in 10, check 1: chance 0.2
    assert math.isclose(dc.detect_chance(10, 2, 1), 0.2)
    assert dc.detect_chance(10, 2, 10) == 1.0
    assert math.isclose(dc.handover_score({"a": (1, 1.0), "b": (3, 0.5)}), 0.625)
