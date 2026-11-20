"""Chapter 39 further lessons against hand results and lab D."""
import math

import pytest

from companion.ch39 import examples_s as es
from companion.ch39 import examples_t as et
from companion.ch39 import lab_d


def test_dual_source_by_hand():
    out = es.dual_source()
    own = 0.04 / 0.94
    assert out["indep"] == pytest.approx(0.01)
    assert out["shared"] == pytest.approx(0.06 + 0.94 * own ** 2)


def test_lead_time_quantiles():
    assert es.lognormal_quantile(30, 0.15, 0.5) == pytest.approx(30, abs=1e-6)
    q90 = es.lognormal_quantile(30, 0.15, 0.9)
    assert q90 == pytest.approx(30 * math.exp(0.15 * 1.28155), rel=1e-4)


def test_evaluated_price_matches_lab_d():
    ev = es.evaluated_at(70.0)
    lab = lab_d.evaluated()
    for o in ev:
        assert ev[o] == pytest.approx(lab[o]["total"])
    assert 50 < es.crossing("U-C") < 55


def test_exposure_and_spares():
    ex = es.exposure()
    assert ex["week"] == 8
    assert ex["peak"] == pytest.approx((0.40 - 0.15) * 1160)
    sp = es.spares()
    assert sp["mu"] == pytest.approx(10 * 0.01 * 30 / 52)
    assert es.poisson_cdf(0, 1.0) == pytest.approx(math.exp(-1))


def test_witness_hypergeometric():
    out = es.witness_plan()
    assert out[1] == pytest.approx(0.2)
    assert out[3] == pytest.approx(1 - math.comb(8, 3) / math.comb(10, 3))


def test_ram_split_and_ltb():
    allowed = et.allowed_hours()
    assert sum(allowed.values()) == pytest.approx(0.03 * 8760)
    ltb = et.last_time_buy()
    assert ltb["mu"] == pytest.approx(24.0)
    assert es.poisson_cdf(ltb["k"], 24.0) >= 0.95 > es.poisson_cdf(ltb["k"] - 1, 24.0)


def test_audits_and_interval():
    assert et.audits_needed(0.20) == 11
    lo, hi = et.wilson(9, 120)
    assert lo < 9 / 120 < hi


def test_guarantees_and_chain():
    g = et.guarantees()
    assert g["epc"] == pytest.approx(1 - 120 / 8460)
    assert g["ppa"] == pytest.approx(0.955)
    ch = et.ld_chain()
    assert ch["epc"] == pytest.approx(1200.0)
    assert ch["sub"] == pytest.approx(46.4)


def test_third_round():
    from companion.ch39 import examples_u as eu
    pq = eu.prequal()
    assert pq["U-D"] and not pq["U-A"] and not pq["U-B"] and not pq["U-C"]
    assert eu.wait_weeks(0.5) == pytest.approx(2.0)
    assert eu.wait_weeks(1.0) == math.inf
    assert eu.applies(eu.REPORTS["U-C"], eu.OUR) == []
    assert "different design" in eu.applies(eu.REPORTS["U-B"], eu.OUR)
    rows = eu.check_rows()
    assert rows["tag known"] == [9] and rows["impedance in per cent"] == [10]
    sec = eu.securities()
    assert sec[0] == ["warranty -4 wk"]


def test_manufacturing_lessons():
    from companion.ch39 import examples_v as ev
    v = ev.verification()
    assert v["points"] == 18 and v["days"] == pytest.approx(27.0)
    m = ev.module_power()
    assert m["lower"] < 550.0
    assert ev.inspection_value()["saved"] == pytest.approx(96.0)


def test_interruption_cover():
    from companion.ch39 import examples_v as ev
    out = ev.interruption()
    day = 5.0 * 0.22 * 24 * 70 / 1000
    assert out["no spare (new unit)"] == pytest.approx(60 * day)
    assert out["spare on site"] == pytest.approx(14 * day)
