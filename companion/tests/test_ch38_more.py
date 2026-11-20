"""Chapter 38, further lessons: queue, cycles, DSM loops, critical path,
estimates at completion and data-quality rules against hand results."""
import pytest

from companion.ch38 import examples_s as es


def test_backlog_by_hand():
    assert es.backlog([30, 30, 10, 10], 25) == [5, 10, 0, 0]


def test_cycles_geometric():
    out = es.cycles()
    assert out["CTL"] == pytest.approx(1 / 0.7)
    assert out["MEC"] == pytest.approx(1 / 0.9)


def test_dsm_loops():
    groups = [sorted(g) for g in es.loops(es.TASKS, es.NEEDS) if len(g) > 1]
    assert sorted(groups) == [["cable sizing", "protection"],
                              ["short circuit", "transformer spec"]]
    order = [t for g in es.loops(es.TASKS, es.NEEDS) for t in g]
    assert order.index("site layout") < order.index("one-line") < \
        order.index("load flow")


def test_critical_path():
    res = es.cpm(es.WORK)
    assert res["earthing study"] == (15, 20, 5)
    assert res["order placed"][0] == 24
    assert all(res[t][2] == 0 for t in es.WORK if t != "earthing study")


def test_eac_and_tcpi():
    out = es.eac()
    assert out["AC + (BAC - EV)"] == pytest.approx(3553 + 7342 - 3012)
    assert out["TCPI"] == pytest.approx((7342 - 3012) / (7342 - 3553))


def test_data_quality_counts():
    q = es.data_quality()
    assert q["tag unique"] == pytest.approx(394 / 400)
    assert q["serial present"] == pytest.approx(388 / 400)


def test_requirement_wording():
    from companion.ch38 import examples_t as et
    assert et.wording("The plant shall limit export to 100 MW.") == []
    assert "vague: 'adequate'" in et.wording("It shall be adequate.")
    assert "2 requirements in one" in et.wording(
        "A shall be done and B shall be done.")
    assert "number without a unit" in et.wording("Data shall be kept 10.")


def test_revision_diff_and_audits():
    from companion.ch38 import examples_t as et
    kinds = dict(et.diff(et.REV1, et.REV2))
    assert kinds["=WS1-W2"] == "removed" and kinds["=WS3-W1"] == "added"
    assert len(kinds) == 4
    assert len(et.cde_audit()) == 4
    assert [m[1] for m in et.transmittals()] == ["PLP-ELE-CAL-0009",
                                                 "PLP-CIV-DWG-0031"]
