"""Chapter 41 lessons and lab against hand calculations and planted faults."""
import math

import pytest

from plantp import pvfab as f
from plantp.mppt import Curve


def test_shunt_lowers_fill_factor():
    ff_rs = f.fill_factor(0.69, 0.64, 0.0418)
    assert f.fill_factor(0.69, 0.64, 0.0418, rsh_ohm_cm2=math.inf) == ff_rs
    assert f.fill_factor(0.69, 0.64, 0.0418, rsh_ohm_cm2=300) < ff_rs


def test_cells_in_series_limited_by_weakest():
    good = Curve(6.99, 0.693, 6.555, 0.583)
    weak = Curve(6.99 * 0.9, 0.693, 6.555 * 0.9, 0.583)
    assert f.cell_mismatch_loss([good] * 24) == pytest.approx(0.0, abs=1e-3)
    loss = f.cell_mismatch_loss([good] * 23 + [weak])
    assert 0.0 < loss < 0.10


def test_auger_caps_implied_voc():
    from companion.ch41.examples_a import implied_voc
    v_good = implied_voc(1e-2, 1)[1]
    assert 0.74 < v_good < 0.77            # near the 0.761 V silicon limit
    assert implied_voc(1e-3, 1000)[1] < implied_voc(1e-3, 10)[1]


def test_scheil_and_grid():
    from companion.ch41.examples_a import grid_loss
    from companion.ch41.examples_b import scheil
    assert scheil(0.0, 0.8) == pytest.approx(0.8)
    assert scheil(0.5, 0.008) / scheil(0.0, 0.008) == pytest.approx(
        0.5 ** -0.992)
    g = grid_loss(0.13)
    assert g["shade"] == pytest.approx(0.003 / 0.13)


def test_lab_finds_the_planted_faults():
    from companion.ch41 import lab_d
    lab_d.write_lot()
    good, golden, problems = lab_d.parse()
    kinds = sorted(p[1].split(" -")[0].split(" ")[0] for p in problems)
    assert len(problems) == 5 and kinds.count("duplicate") == 2
    d = lab_d.drift_quiet()
    assert d["first"] == 2400 and 2.0 < d["shift"] < 3.0
    fixed = lab_d.corrected(good, d)
    mv = sorted(r["voc"] for r in fixed)[len(fixed) // 2]
    mi = sorted(r["isc"] for r in fixed)[len(fixed) // 2]
    diodes = [r for r in fixed if r["p"] < 400]
    assert all("diode" in lab_d.diagnose(r, mv, mi) for r in diodes)


def test_clamp_optimum_and_sample_size():
    from companion.ch41 import examples_c, examples_e
    c = examples_c.clamping()
    assert c["a"] / 2.278 == pytest.approx(1 / (2 + 2 * math.sqrt(2)))
    assert examples_e.el_sample()[0.01] == 299


def test_rounds_s_to_u():
    from companion.ch41 import examples_s, examples_t, examples_u
    c = examples_s.classes()
    assert c["cells sorted into bins"][560] > c["cells as they come"][560]
    tr = examples_t.trapping()
    assert tr["light trapping (4n2)"][100] > tr["one pass"][180]
    assert examples_t.luhn_ok(examples_t.check_digit("12345678"))
    w = examples_u.warranty()
    assert w["another lab, new reference"][100] > 3.0
    assert w["same lab, kept control modules"][100] < 1.0


def test_rounds_v_w():
    from companion.ch41 import examples_v, examples_w
    r = examples_v.resistances()
    assert r["shunted cells"][1] < 30 and r["weak joints"][0] > 0.3
    assert examples_v.el_image()["worst"] > 0.30
    assert examples_w.stackup()["rss"] < examples_w.stackup()["worst"]
    assert examples_w.lots()["first"] == 23


def test_round_x():
    from companion.ch41 import examples_x
    r = examples_x.routes()
    assert r["pulled mono (Cz)"][0] > r["multi (cast)"][0]
    f = examples_x.flashers()
    assert f["after golden-module match"]["grr"] < f["as found (B reads +1.2 W)"]["grr"]
