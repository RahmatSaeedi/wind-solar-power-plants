"""Chapter 45 battery manufacture arithmetic and the educational SOC
simulator: hand values, invariants and boundary tests. Pure helpers only."""
import pytest

from plantp import cellmfg as cf


def test_areal_capacity_and_balance_by_hand():
    assert cf.areal_capacity(40.0, 0.95, 155.0) == pytest.approx(5.89)
    assert cf.np_ratio(6.17, 5.89) == pytest.approx(6.17 / 5.89)
    assert cf.cell_capacity_ah(5.0, 1000.0, 0.9) == pytest.approx(4.5)


def test_k_value_sign_and_size():
    assert cf.k_value(3.3150, 3.3143, 14) == pytest.approx(0.05)
    assert cf.k_value(3.3, 3.3, 7) == 0.0


def test_string_and_matching():
    assert cf.string_capacity([316, 317, 314.5]) == 314.5
    caps = [310, 320, 311, 319]
    srt = cf.match(caps, 2, "sorted")
    rnd = cf.match(caps, 2, "random")
    assert [min(m) for m in srt] == [310, 319]
    assert [min(m) for m in rnd] == [310, 311]
    assert len(cf.match(list(range(10)), 3)) == 3          # leftover dropped


def test_pack_limits():
    lim = cf.pack_limits(416, 1, 314.0, 2.5, 3.2, 3.65, 0.5)
    assert lim["v_min"] == pytest.approx(1040.0)
    assert lim["v_max"] == pytest.approx(1518.4)
    assert lim["e_kwh"] == pytest.approx(416 * 314 * 3.2 / 1000)
    assert lim["i_max"] == pytest.approx(157.0)


def test_bms_check_margins():
    res = cf.bms_check({"v_max": ("hi", 3.60), "t": ("hi", 58.0), "v_min": ("lo", 2.6)},
                       {"v_max": 3.65, "t": 55.0, "v_min": 2.5},
                       {"v_max": 0.03, "t": 3.0, "v_min": 0.05})
    ok = {r[0]: r[3] for r in res}
    assert ok == {"v_max": True, "t": False, "v_min": True}


def test_soc_sim_stays_in_window_and_balances():
    sim = cf.SocSim(q_ah=314.0, soc=0.5)
    for i in [400.0] * 4 + [-500.0] * 8 + [200.0] * 3:
        sim.step(i, 900.0)
        assert sim.lo - 1e-12 <= sim.soc <= sim.hi + 1e-12
    assert abs(sim.balance_error(0.5)) < 1e-9


def test_soc_sim_boundaries():
    full = cf.SocSim(q_ah=100.0, soc=0.90)
    assert full.step(50.0, 60.0) == 0.0                    # refuses charge at hi
    assert full.refused_ah == pytest.approx(50.0 / 60)
    empty = cf.SocSim(q_ah=100.0, soc=0.10)
    assert empty.step(-50.0, 60.0) == 0.0                  # refuses at lo
    assert empty.step(50.0, 60.0) == pytest.approx(50.0)   # charging allowed
    with pytest.raises(ValueError):
        empty.step(1.0, 0.0)


def test_soc_sim_cut_is_partial_and_logged():
    sim = cf.SocSim(q_ah=100.0, soc=0.89, eta_c=1.0)
    got = sim.step(100.0, 3600.0)                          # asks 100 Ah, room 1 Ah
    assert got == pytest.approx(1.0)
    assert sim.soc == pytest.approx(0.90)
    assert sim.log and sim.log[0][0] == "cut"


def test_dew_point_water():
    assert cf.abs_humidity_g_m3(10.0) == pytest.approx(9.4, abs=0.1)
    assert cf.abs_humidity_g_m3(-40.0) < 0.2


def test_recovered_rates():
    r = cf.recovered({"a": 10.0, "b": 5.0}, {"a": 0.5})
    assert r == {"a": 5.0, "b": 0.0}


def test_property_test_passes_v10_and_catches_v11():
    from companion.ch45.examples_u import SocSimV11
    from companion.ch45.examples_w import property_test
    a = property_test(cf.SocSim, runs=20, steps=20)
    b = property_test(SocSimV11, runs=20, steps=20)
    assert a["window"] == 0 and a["balance"] == 0
    assert b["balance"] > 0


def test_charge_rule_edges_and_missing_reading():
    from companion.ch45.examples_w import charge_allowed
    assert charge_allowed(2.0) and charge_allowed(52.0)
    assert not charge_allowed(1.99) and not charge_allowed(52.01)
    assert not charge_allowed(float("nan"))


def test_config_rules_find_planted_faults():
    from companion.ch45.examples_u import CONFIG, RULES
    broken = [name for name, rule in RULES if not rule(CONFIG)]
    assert broken == ["alarm before trip, high voltage", "alarm before trip, current"]
