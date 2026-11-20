"""Chapter 43 transformer design and test arithmetic against hand values."""
import math

import numpy as np
import pytest

from plantp import xfmrdesign as xd


def test_stepped_fill_known_values():
    assert xd.stepped_fill(1)[0] == pytest.approx(2 / math.pi, rel=1e-6)
    assert xd.stepped_fill(2)[0] == pytest.approx(0.7869, abs=2e-4)
    f = [xd.stepped_fill(n)[0] for n in (3, 5, 9)]
    assert f[0] < f[1] < f[2] < 1.0


def test_core_section_by_hand():
    c = xd.core_section(110.0, 1.7, f=50.0, stacking=0.97, fill=0.94)
    assert c["a_net"] == pytest.approx(110.0 / (4.44 * 50 * 1.7))
    assert c["d"] == pytest.approx(math.sqrt(4 * c["a_net"] / 0.97 / (math.pi * 0.94)))


def test_tap_table_whole_turns():
    tab = xd.tap_table(693, 1.25, 8, 9)
    assert len(tab) == 17
    principal = [r for r in tab if r[0] == 0.0][0]
    assert principal[1] == 693 and principal[2] == pytest.approx(0.0)
    low = tab[0]
    assert low[1] == 693 - 72
    assert low[2] == pytest.approx(100 * (621 / (693 * 0.9) - 1))


def test_resistance_and_reference_temperature():
    r = xd.resistance_ohm(300, 0.753, 181.8)
    assert r == pytest.approx(0.0211e-6 * 300 * math.pi * 0.753 / 181.8e-6)
    assert xd.r_to_ref(1.0, 22.0) == pytest.approx(310 / 257)


def test_ux_by_hand():
    ni, e_t, d_m = 300 * 636.4, 110.0, 0.893
    a12, a1, a2, h = 0.075, 0.065, 0.110, 2.05
    k_r = 1 - (a1 + a2 + a12) / (math.pi * h)
    want = (100 * 2 * math.pi * 50 * xd.MU0 * ni * math.pi * d_m
            * (a12 + (a1 + a2) / 3) / (e_t * h / k_r))
    assert xd.ux_pct(50, ni, e_t, d_m, a12, a1, a2, h) == pytest.approx(want)


def test_eddy_grows_with_thickness_squared():
    r1 = xd.eddy_ratio(50, 0.166, 1e-3, 3.5e6)
    r2 = xd.eddy_ratio(50, 0.166, 2e-3, 3.5e6)
    assert r2 / r1 == pytest.approx(4.0)


def test_hoop_and_buckling_by_hand():
    ni, h, d, n, a = 4.0e6, 2.0, 1.0, 700, 80.0
    b = xd.MU0 * ni / h
    f_r = ni * b / 2 * math.pi * d
    assert xd.hoop_stress_mpa(ni, h, d, n, a) == pytest.approx(
        f_r / (2 * math.pi * n * a * 1e-6) / 1e6)
    assert xd.buckling_free_mpa(110e9, 0.01, 1.0) == pytest.approx(11.0)
    assert xd.buckling_supported_mpa(110e9, 0.01, 0.1) == pytest.approx(
        math.pi ** 2 * 110e9 * 1e-4 / 3e-2 / 1e6)


def test_series_gap():
    e_oil, e_pb = xd.field_in_gap(100.0, 75.0, 0.0)
    assert e_oil == pytest.approx(100 / 75)
    e_oil, e_pb = xd.field_in_gap(100.0, 66.0, 9.0)
    assert e_pb == pytest.approx(e_oil / 2)
    # displacement continuity: eps E equal in both
    assert 2.2 * e_oil == pytest.approx(4.4 * e_pb)


def test_water_and_waveform_and_sound():
    assert xd.water_solubility_ppm(20.0) == pytest.approx(10 ** (7.42 - 1670 / 293.15))
    assert xd.waveform_corrected(40.0, 1.0, 1.0) == pytest.approx(40.0)
    assert xd.waveform_corrected(43.5, 1.03, 1.0) == pytest.approx(43.5 * 0.97)
    assert xd.sound_power_db(68.0, 84.0) == pytest.approx(68 + 10 * math.log10(84))


def test_cooling_curve_recovers_exact_exponential():
    t = np.array([2, 4, 6, 8, 10, 12, 15, 20], float)
    r = 0.62 + 0.04 * np.exp(-t / 8.0)
    fit = xd.cooling_curve(t, r)
    assert fit["r0"] == pytest.approx(0.66, abs=1e-6)
    assert fit["tau"] == pytest.approx(8.0, rel=1e-4)


def test_delta_phases_inverse():
    from companion.ch43 import examples_x as ex
    a, b, c = 0.071, 0.069, 0.070
    s = a + b + c
    lines = (a * (b + c) / s, b * (c + a) / s, c * (a + b) / s)
    back = ex.delta_phases(*lines)
    assert back == pytest.approx([a, b, c], rel=1e-6)
    # symmetric delta: phase = 1.5 x line
    assert ex.delta_phases(0.02, 0.02, 0.02)[0] == pytest.approx(0.03, rel=1e-6)


def test_process_fmea_order():
    from companion.ch43 import examples_v as ev
    from plantp import quality as qa
    rows = [dict(step=a, mode=b, s=s, o=o, d=d) for a, b, s, o, d in ev.PFMEA]
    ranked = qa.fmea_rank(rows)
    assert ranked[0]["mode"] == "poor brazed joint"
    assert all(r["s"] >= 9 for r in ranked[:3])


def test_factory_schedule_critical_path():
    from companion.ch43 import examples_t as et
    acts = et.ACTS
    early = {}
    for a, (d, pre) in acts.items():
        early[a] = max((early[p] for p in pre), default=0) + d
    assert max(early.values()) == 32
    assert early["windings"] == 22 and early["core cut and stacked"] == 24


def test_loss_temperature_calculator():
    k = np.zeros(8760)
    amb = np.full(8760, 20.0)
    calc = xd.LossTempCalc(42.0, 290.0, k, amb)
    out = calc.run()
    assert out["loss_mwh"] == pytest.approx(42.0 * 8760 / 1000)
    res = calc.sensitivity({"hot": dict(ambient=5.0), "pk": dict(pk=2.0)})
    assert res["hot"]["hs_max"] == pytest.approx(out["hs_max"] + 5.0)
    assert res["pk"]["loss_mwh"] == pytest.approx(out["loss_mwh"])
