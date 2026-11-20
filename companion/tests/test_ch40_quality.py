"""Chapter 40 quality module and labs against hand calculations."""
import math

import pytest

from plantp import quality as qa


def test_capability_by_hand():
    v = [9.0, 10.0, 11.0, 10.0, 10.0]
    m, s, cp, cpk = qa.cp_cpk(v, 7.0, 13.0)
    assert m == pytest.approx(10.0)
    assert s == pytest.approx(math.sqrt(0.5))
    assert cp == pytest.approx(6 / (6 * s))
    assert cpk == pytest.approx(3 / (3 * s))
    _, _, cp1, cpk1 = qa.cp_cpk(v, None, 13.0)
    assert math.isnan(cp1) and cpk1 == pytest.approx(cpk)
    # 3 sigma either side: 2,700 ppm out in total
    assert qa.ppm_out(0.0, 1.0, -3.0, 3.0) == pytest.approx(2699.8, abs=0.5)


def test_range_constants_match_the_textbook():
    for n, d2, d3 in ((2, 1.128, 0.853), (5, 2.326, 0.864), (10, 3.078, 0.797)):
        a, b = qa.d2_d3(n)
        assert a == pytest.approx(d2, abs=0.002)
        assert b == pytest.approx(d3, abs=0.003)
    with pytest.raises(ValueError):
        qa.d2_d3(1)


def test_chart_limits_by_hand():
    groups = [[10, 12], [11, 13], [9, 11]]       # ranges 2, 2, 2; means 11, 12, 10
    lim = qa.xbar_r_limits(groups)
    d2, _ = qa.d2_d3(2)
    assert lim["x_centre"] == pytest.approx(11.0)
    assert lim["x_ucl"] == pytest.approx(11 + 3 / (d2 * math.sqrt(2)) * 2)
    assert lim["sigma"] == pytest.approx(2 / d2)


def test_yield_takt_balance():
    assert qa.rty([0.9, 0.9, 0.5]) == pytest.approx(0.405)
    assert qa.takt(160, 10) == 16
    lb = qa.line_balance({"a": 10, "b": 20, "c": 15})
    assert lb["bottleneck"] == "b" and lb["efficiency"] == pytest.approx(0.75)


def test_sampling_plans():
    assert qa.p_accept(10, 0, 0.1) == pytest.approx(0.9 ** 10)
    assert qa.p_accept(2, 1, 0.5) == pytest.approx(0.75)
    n, c = qa.find_plan(0.01, 0.05)
    assert qa.p_accept(n, c, 0.01) >= 0.95
    assert qa.p_accept(n, c, 0.05) <= 0.10
    assert (n, c) == (132, 3)


def test_grr_pure_part_variation():
    # identical repeats and operators: all variation is the parts'
    data = [[[v, v], [v, v], [v, v]] for v in (1.0, 2.0, 3.0, 4.0)]
    g = qa.grr_anova([[[x + 1e-9 * (k + r) for r, x in enumerate(op)]
                       for k, op in enumerate(part)] for part in data])
    assert g["grr_pct"] < 0.01
    assert g["part"] == pytest.approx(1.6667, rel=1e-3)


def test_fmea_and_growth():
    rows = [dict(s=8, o=5, d=9), dict(s=10, o=1, d=2), dict(s=5, o=9, d=9)]
    ranked = qa.fmea_rank(rows)
    assert ranked[0]["s"] == 10 and ranked[1]["s"] == 8
    with pytest.raises(ValueError):
        qa.rpn(0, 3, 3)
    fit = qa.crow_amsaa([100.0, 400.0], 1000.0)
    assert fit["beta"] == pytest.approx(2 / (math.log(10) + math.log(2.5)))
    assert fit["mtbf_now"] == pytest.approx(1000 / (2 * fit["beta"]))


def test_escape_tur_sling():
    assert qa.escape(1.0, [0.5, 0.5]) == pytest.approx(0.25)
    assert qa.tur(7.0, 2.8) == pytest.approx(2.5)
    assert qa.sling_leg(100.0, 2, 30.0) == pytest.approx(100.0)
    with pytest.raises(ValueError):
        qa.sling_leg(100.0, 2, 0.0)


def test_ch40_labs():
    from companion.ch40 import examples_c, lab_d, sources as src
    assert examples_c.suspect_skids("TW-14", 11, 16) == ["S-05", "S-06", "S-07"]
    found = lab_d.audit(src.DOSSIER, src.ITP, src.CAL_DUE, src.PROCEDURE_REV,
                        src.GENEALOGY, src.TOOL_CHECKS)
    assert len(found) == 8
    tr = lab_d.defect_trace()
    assert tr["mwh"] == pytest.approx(5 * 0.27 * 24 * 9)
    assert tr["before"] / tr["after"] == pytest.approx(40.0)


def test_ch40_more_lessons():
    from companion.ch40 import examples_s as es, examples_t as et
    r = es.oee(160, 22, 8, 13, 12)
    assert r["oee"] == pytest.approx((138 / 160) * (104 / 138) * (12 / 13))
    st = es.assign(es.TASKS, 16.0)
    assert len(st) == 3
    for s_ in st:
        assert sum(es.TASKS[t][0] for t in s_) <= 16.0
    span, _ = es.flow_shop([1.0, 3.0, 2.0], 4)
    assert span == pytest.approx(1 + 3 * 4 + 2)       # bottleneck-paced
    assert et.kappa([1, 1, 0, 0], [1, 1, 0, 0]) == pytest.approx(1.0)
    assert et.kappa([1, 0, 1, 0], [0, 1, 0, 1]) == pytest.approx(-1.0)
    pc = et.p_chart()
    assert pc["out"] == [9]
    m = et.mtbf_interval()
    assert m["mtbf"] == pytest.approx(10950.0) and m["lower"] < m["mtbf"]


def test_ch40_third_round():
    import math
    from companion.ch40 import examples_u as eu
    t = eu.time_study()
    assert t["std"] == pytest.approx(t["normal"] * 1.15)
    assert eu.kanban()["cards"] == math.ceil(0.625 * 3 * 1.2)
    assert eu.eoq()["q"] == pytest.approx(math.sqrt(2 * 40 * 0.6 / 2.2))
    lay = eu.layout()
    assert lay["as built"] == pytest.approx(360) and lay["straight line"] == pytest.approx(220)
    assert eu.coverage()["gaps"] == 2
    arl = eu.arl()
    assert arl[0.0] == pytest.approx(370.4, rel=1e-3)
    assert eu.demo_test()[0.9] == pytest.approx(1000 * math.log(10))


def test_ch40_fourth_round():
    from companion.ch40 import examples_v as ev
    d = ev.factorial()
    assert d["a"] == pytest.approx(0.61, abs=1e-6)
    assert d["ab"] == pytest.approx(0.20, abs=1e-6)
    n, k = ev.variables_plan(0.01, 0.05)
    assert n < 132 and 1.5 < k < 2.5
    ss = ev.stress_strength()
    assert ss[(300.0, 50.0)] > ss[(300.0, 25.0)]
    assert ev.first_article()["missing"] == 3


def test_ch40_fifth_round():
    from companion.ch40 import examples_w as ew
    rules = ew.all_or_none()
    assert rules["relay secondary injection"] == "all"
    assert rules["MV cable insulation test"] == "none"
    vc = ew.variance_components()
    assert vc["good"]["share_between"] < 0.05 < vc["all"]["share_between"]
    ir = ew.ir_corrected()
    assert min(ir, key=ir.get) == "S-09"
    assert ir["S-03"] == pytest.approx(2900.0)
