"""Hand-calculated reference cases for plantp.gridstudy (chapter 28)."""
import math

import numpy as np
import pytest

from plantp import gridstudy as gs


def two_bus(p_load=1.0, r=0.0, x=0.1):
    br = [gs.Branch(0, 1, r, x)]
    y = gs.ybus(2, br)
    res = gs.load_flow(y, ["slack", "pq"], [0, -p_load], [0, 0], [1.0, 1.0])
    return br, res


def test_two_bus_voltage_matches_closed_form():
    # v^4 - v^2 + x^2 P^2 = 0 for a lossless line feeding P at unity pf
    _, res = two_bus()
    v = abs(res["v"][1])
    assert v == pytest.approx(math.sqrt((1 + math.sqrt(1 - 4 * 0.01)) / 2), abs=1e-9)


def test_losses_are_r_i_squared():
    br, res = two_bus(r=0.02)
    f = gs.flows(res["v"], br)[0]
    i = abs(1 / np.conj(res["v"][1]))
    assert f["loss"].real == pytest.approx(0.02 * i ** 2, rel=1e-6)


def test_load_flow_raises_when_impossible():
    br = [gs.Branch(0, 1, 0.0, 0.1)]
    y = gs.ybus(2, br)
    with pytest.raises(RuntimeError):
        gs.load_flow(y, ["slack", "pq"], [0, -8.0], [0, 0], [1.0, 1.0], max_iter=15)


def test_thevenin_magnitude_and_ratio():
    z = gs.thevenin(1500, 8)
    assert abs(z) == pytest.approx(100 / 1500)
    assert z.imag / z.real == pytest.approx(8)


def test_fault_current_without_sources_is_c_over_z():
    z = gs.thevenin(1000, 10)
    zb = np.array([[z]])
    out = gs.fault_current(zb, 0, c=1.1)
    assert out["total"] == pytest.approx(1.1 / abs(z))
    assert out["converters"] == pytest.approx(0.0)


def test_converter_source_adds_current():
    z = complex(0.0, 0.1)
    zb = np.array([[z]])
    out = gs.fault_current(zb, 0, c=1.0, sources=[(0, 1.0)])
    assert out["total"] == pytest.approx(11.0)       # 10 from the grid + 1 injected


def test_ndz_textbook_values():
    d = gs.ndz(0.85, 1.10, 49.0, 51.0, 1.0)
    assert d["dp"][0] == pytest.approx(-0.1736, abs=1e-4)
    assert d["dp"][1] == pytest.approx(0.3841, abs=1e-4)
    assert d["dq"][0] == pytest.approx(-0.0412, abs=1e-4)


def test_wscr_of_one_plant_is_scr():
    assert gs.wscr([1500.0], [100.0]) == pytest.approx(15.0)


def test_phase_jump_and_sync_power():
    assert gs.phase_jump_current(30, 0.2) == pytest.approx(2.588, abs=1e-3)
    assert gs.sync_power(1, 1, 0.5, 30) == pytest.approx(1.0)


def test_frequency_event_initial_rocof():
    t = np.arange(0, 1, 0.001)
    out = gs.freq_event(t, 10000, 5.0, 500, d_load=0.0, gov=(0.05, 1e9, 0.0))
    # no response: df/dt = -dP/S * f0/(2H) = -0.05 * 5 = -0.25 Hz/s
    assert out["rocof"] == pytest.approx(-0.25, rel=1e-2)


def test_frt_steady_state_matches_load_flow():
    t = np.arange(0, 0.5, 0.001)
    out = gs.frt_sim(t, np.ones_like(t), complex(0, 0.1), p0=1.0)
    _, res = two_bus()
    assert out["u"][-1] == pytest.approx(abs(res["v"][1]), abs=1e-4)


def test_validation_errors():
    t = np.arange(0, 3, 0.5)
    e = gs.validation_errors(t, np.ones(6) * 1.1, np.ones(6), {"all": (0, 3)})
    assert e["all"]["me"] == pytest.approx(0.1)
    assert e["all"]["mxe"] == pytest.approx(0.1)
