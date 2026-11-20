"""Chapter 32 labs I (site security) and J (readiness exercise) against
hand counts and hand calculations."""
import pytest

from companion.ch32 import lab_i, lab_j


def test_gate_reconciliation_counts():
    res = lab_i.reconcile(lab_i.gate_records())
    # 6 days x (30 employees + 23 contractors + 6 + 2 substation) = 366,
    # plus 10 visitors and 2 unauthorised substation entries
    assert res["n"] == 378
    assert len(res["expired"]) == 6          # B02, B05, B07 on days 5-6
    assert {r["who"] for r in res["expired"]} == {"B02", "B05", "B07"}
    assert len(res["no_host"]) == 2
    assert {r["who"] for r in res["area"]} == {"A03", "A08"}
    assert len(res["open_exit"]) == 4
    assert {r["day"] for r in res["open_exit"]} == {5}


def test_expected_annual_loss_by_hand():
    assert lab_i.eal() == pytest.approx(1.0 * 3 + 0.5 * 25 + 0.3 * 8.5)
    f = lab_i.factors_of(["marking and records", "stores control"])
    assert f["spare cable drums from the store"] == pytest.approx(0.14)
    assert f["earth conductor at a PV station"] == pytest.approx(0.7)
    # stores control alone: 0.5 x 25 x 0.8 = 10 avoided, cost 6
    assert lab_i.saving(["stores control"]) == pytest.approx(4.0)


def test_overlapping_measures_and_best_set():
    best = lab_i.best_sets(1)[0]
    assert best[0] == ("stores control",)
    alone = sum(lab_i.eal() - lab_i.eal(lab_i.factors_of([m]))
                for m in lab_i.MEASURES)
    assert alone > lab_i.eal()               # benefits overlap
    assert lab_i.saving(["longer fence at PV stations"]) == pytest.approx(-18.5)


def test_partial_evidence():
    assert lab_i.partial("12 of 16 files")
    assert not lab_i.partial("3 of 3 closed by liaison")
    assert not lab_i.partial("contract and rota")
    assert not lab_i.partial(None)


def test_inject_roles_and_tracker():
    assert lab_j.clarity([]) == "none"
    assert lab_j.clarity(["a"]) == "one"
    assert lab_j.clarity(["a", "b"]) == "two+"
    res = lab_j.injects()
    assert (res["one"], res["none"], res["two+"]) == (6, 2, 1)
    assert res["on_time"] == 6 and res["recorded"] == 5
    t = lab_j.tracker(90)
    assert len(t["evidence"]) == 6
    assert t["claimed"] == ["A4", "A6"]
    assert t["overdue"] == ["A10"]
    assert t["open"] == ["A2", "A11"]        # due on day 90 is not overdue
