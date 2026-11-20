"""Chapter 44 converter manufacture arithmetic and the educational state
machine against hand values, boundaries and injected faults. Pure helpers
only: no test calls a function that rewrites an expected/ file."""
import math

import pytest

from plantp import convmfg as cm


def test_tim_resistance_by_hand():
    # 100 um / (0.8 W/m K x 80e-4 m2) = 0.015625 K/W
    assert cm.tim_r(100, 0.8, 80) == pytest.approx(0.015625)
    # voids remove area: 40 % voids -> 1 / 0.6 of the resistance
    assert cm.tim_r(100, 0.8, 80, 0.4) == pytest.approx(0.015625 / 0.6)
    # twice as thick -> twice the resistance
    assert cm.tim_r(200, 0.8, 80) == pytest.approx(2 * cm.tim_r(100, 0.8, 80))


def test_junction_temperature_series_stack():
    assert cm.tj(494, 0.028, 0.0156, 0.016, 45) == pytest.approx(45 + 494 * 0.0596)
    assert cm.tj(0, 0.1, 0.1, 0.1, 30) == 30


def test_shares_sum_to_one_and_follow_inverse():
    sh = cm.shares([1.0, 2.0])
    assert sum(sh) == pytest.approx(1.0)
    assert sh[0] == pytest.approx(2 / 3)
    assert cm.shares([1.0] * 12) == pytest.approx([1 / 12] * 12)


def test_solder_strain_and_life_monotonic():
    e = cm.solder_strain(3.2, 11, 40, 0.1)
    assert e == pytest.approx(3.2 * 11e-6 * 40 / 0.1)
    # doubling the swing doubles the strain and shortens the life
    assert cm.solder_strain(3.2, 11, 80, 0.1) == pytest.approx(2 * e)
    assert cm.cycles_to_failure(2 * e) < cm.cycles_to_failure(e)
    # at strain 2 eps_f the life is half a cycle by construction
    assert cm.cycles_to_failure(2 * 0.325) == pytest.approx(0.5)


def test_escapes_by_hand():
    out = cm.escapes({"bridge": 800.0},
                     {"a": {"bridge": 0.85}, "b": {"bridge": 0.6}, "c": {}})
    assert out["bridge"] == pytest.approx(800 * 0.15 * 0.4)
    # a defect no station looks for passes untouched
    assert cm.escapes({"x": 10.0}, {"a": {"y": 0.9}})["x"] == 10.0


def test_fingerprint_order_independent_and_sensitive():
    a = {"p": 1, "q": "on"}
    b = {"q": "on", "p": 1}
    assert cm.fingerprint(a) == cm.fingerprint(b)
    assert len(cm.fingerprint(a)) == 16
    assert cm.fingerprint(a) != cm.fingerprint({"p": 1, "q": "off"})
    assert cm.fingerprint({"v": 1}) != cm.fingerprint({"v": 1.0001})


def test_derating_flags_parts_over_rule():
    rows = [("a", "V", 80.0, 100.0), ("b", "V", 81.0, 100.0)]
    res = cm.derating(rows, {"V": 0.80})
    assert res[0][3] is True and res[1][3] is False
    assert res[1][1] == pytest.approx(0.81)


def _run(sim, events):
    for ev, kw in events:
        sim.event(ev, **kw)
    return sim.state


def test_state_machine_normal_start_and_log():
    sim = cm.ConverterSim()
    st = _run(sim, [("start", {}), ("tick", {"v_dc": 900}), ("grid_ok", {}),
                    ("synced", {})])
    assert st == "RUN"
    assert [x[1] for x in sim.log] == ["PRECHARGE", "READY", "SYNC", "RUN"]


@pytest.mark.parametrize("v, want", [(849.9, "PRECHARGE"), (850.0, "READY"),
                                     (1300.0, "READY"), (1300.1, "FAULT")])
def test_state_machine_dc_boundaries(v, want):
    assert _run(cm.ConverterSim(), [("start", {}), ("tick", {"v_dc": v})]) == want


def test_precharge_timeout_boundary():
    ten = [("start", {})] + [("tick", {"v_dc": 300})] * 10
    assert _run(cm.ConverterSim(), ten) == "PRECHARGE"
    assert _run(cm.ConverterSim(), ten + [("tick", {"v_dc": 300})]) == "FAULT"


def test_fault_latches_until_cause_cleared():
    sim = cm.ConverterSim()
    sim.event("fault", kind="overtemp")
    assert _run(sim, [("reset", {}), ("start", {}), ("stop", {})]) == "FAULT"
    assert sim.event("reset", cause_cleared=True) == "OFF"


def test_overvoltage_in_run_and_grid_loss_fault():
    base = [("start", {}), ("tick", {"v_dc": 900}), ("grid_ok", {}), ("synced", {})]
    assert _run(cm.ConverterSim(), base + [("tick", {"v_dc": 1350})]) == "FAULT"
    sim = cm.ConverterSim()
    assert _run(sim, base + [("grid_lost", {})]) == "FAULT"
    assert sim.fault == "grid lost"


def test_injected_fault_version_is_caught():
    class NoTimeout(cm.ConverterSim):
        PRECHARGE_MAX_S = math.inf
    slow = [("start", {})] + [("tick", {"v_dc": 300})] * 12
    assert _run(cm.ConverterSim(), slow) == "FAULT"
    assert _run(NoTimeout(), slow) == "PRECHARGE"


def test_ch44_lab_cases_pass_and_planted_fault_fails():
    from companion.ch44 import lab_d
    good = lab_d.run_cases(cm.ConverterSim)
    bad = lab_d.run_cases(lab_d.FaultySim)
    assert all(r[3] for r in good)
    assert [r[0] for r in bad if not r[3]] == ["precharge too slow"]


def test_canonical_form_equal_settings_equal_fingerprint():
    from companion.ch44.examples_t import canonical
    a = {"d": 4.0, "f": [47.5, 51.5]}
    b = {"d": 4, "f": (47.5, 51.5)}
    assert cm.fingerprint(a) != cm.fingerprint(b)
    assert cm.fingerprint(canonical(a)) == cm.fingerprint(canonical(b))
    assert cm.fingerprint(canonical(a)) != cm.fingerprint(canonical({"d": 4.01,
                                                                      "f": [47.5, 51.5]}))


def test_camera_reads_true_when_emissivity_matches():
    from companion.ch44.examples_t import apparent
    assert apparent(80.0, 0.95, eps_set=0.95) == pytest.approx(80.0)
    # low emissivity reads towards the surroundings
    assert apparent(90.0, 0.10) < apparent(55.0, 0.90)


def test_magnus_saturation_pressure():
    from companion.ch44.examples_t import p_sat
    assert p_sat(0.0) == pytest.approx(6.112)
    assert p_sat(20.0) == pytest.approx(23.37, rel=0.01)


def test_drift_free_tracker_holds_the_ramp():
    from companion.ch44 import lab_d
    t = lab_d.DriftFreePO(v_ref=900.0, step=4.0)
    # perturb, measure, hold: three updates return to the perturb phase
    t.update(900.0, 10.0)
    t.update(t.v_ref, 10.0)
    t.update(t.v_ref, 10.0)
    assert t.phase == "perturb"
