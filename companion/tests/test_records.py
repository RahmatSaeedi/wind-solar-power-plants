"""Tests of plantp.records (chapter 2)."""
import pytest

from plantp import records as rec


def test_doc_number_round_trip():
    n = rec.doc_number("GEN", "CAL", 2)
    assert n == "PLP-GEN-CAL-0002"
    assert rec.parse_doc_number(n) == ("GEN", "CAL", 2)
    for bad in ("PLP-XYZ-CAL-0002", "PLP-GEN-CAL-2", "PLQ-GEN-CAL-0002"):
        with pytest.raises(ValueError):
            rec.parse_doc_number(bad)
    with pytest.raises(ValueError):
        rec.doc_number("GEN", "CAL", 0)


def test_revision_sequence():
    assert rec.next_revision(None) == "A"
    assert rec.next_revision("A") == "B"
    assert rec.next_revision("Z") == "AA"
    assert rec.next_revision("AZ") == "BA"
    assert rec.next_revision("C", approve=True) == "0"
    assert rec.next_revision("0") == "1"
    with pytest.raises(ValueError):
        rec.next_revision("b")


def test_status_transitions():
    rec.check_transition("WIP", "IFR")
    rec.check_transition("IFA", "APP")
    with pytest.raises(ValueError):
        rec.check_transition("WIP", "IFC")          # cannot build from a draft
    with pytest.raises(ValueError):
        rec.check_transition("SUP", "APP")          # superseded stays superseded


def test_digest_is_stable_and_sensitive():
    a = rec.digest({"x": 1.0, "y": [1, 2]})
    b = rec.digest({"y": [1, 2], "x": 1.0})
    c = rec.digest({"x": 1.0000001, "y": [1, 2]})
    assert a == b and a != c


def test_input_needs_status_and_source():
    with pytest.raises(ValueError):
        rec.Input("I1", "PV capacity", 60, "MWp", "guessed", "SR-01")
    with pytest.raises(ValueError):
        rec.Input("I1", "PV capacity", 60, "MWp", "assumed", "")


def _sheet(**kw):
    base = dict(
        number="PLP-GEN-CAL-0002", title="t", purpose="p",
        revisions=[rec.Revision("A", "2026-11-14", "IFR", "first issue", "author")],
        inputs=[rec.Input("I1", "PV capacity", 60, "MWp", "assumed", "SR-01")],
        method=["m"], results=[("r", "1 GWh")], checks=[("c", "ok", "PASS")])
    base.update(kw)
    return rec.CalcSheet(**base)


def test_calc_sheet_renders_within_width():
    sheet = _sheet(comments=[rec.Comment("C1", "checker", "line 3", "x" * 200, "major",
                                         "fixed " * 30, "closed")])
    lines = sheet.render()
    assert max(len(line) for line in lines) <= 78
    assert sheet.open_comments() == []


def test_calc_sheet_rejects_duplicate_inputs_and_bad_number():
    i = rec.Input("I1", "a", 1, "m", "assumed", "s")
    with pytest.raises(ValueError):
        _sheet(inputs=[i, i])
    with pytest.raises(ValueError):
        _sheet(number="CALC-2")
    with pytest.raises(ValueError):
        _sheet(revisions=[])
