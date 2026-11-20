"""Tests of plantp.ac (chapter 7). Hand values in comments."""
import math

import pytest

from plantp import ac
from plantp.phasors import complex_power, polar


def test_reactances_and_resonance():
    assert ac.reactance_l(50, 0.1) == pytest.approx(31.4159, rel=1e-5)
    assert ac.reactance_c(50, 100e-6) == pytest.approx(31.8310, rel=1e-5)
    f0 = ac.resonance_hz(0.1, 100e-6)                     # 1/(2 pi sqrt(1e-5))
    assert f0 == pytest.approx(50.329, rel=1e-4)
    z = ac.rlc_series(2.0, 0.1, 100e-6, f0)
    assert abs(z.imag) < 1e-9 and z.real == 2.0         # pure R at resonance
    assert ac.q_series(2.0, 0.1, 100e-6) == pytest.approx(15.81, rel=1e-3)
    assert ac.resonance_order(1000, 10) == pytest.approx(10.0)
    with pytest.raises(ValueError):
        ac.reactance_c(0, 1e-6)


def test_line_current_and_wye_delta():
    # 100 MW at 132 kV, pf 0.95: I = 1e8 / (sqrt3 x 132e3 x 0.95) = 460.4 A
    assert ac.line_current_a(100e6, 132e3, 0.95) == pytest.approx(460.39, rel=1e-4)
    vab = ac.wye_to_line(polar(230.0, 0.0))
    assert abs(vab) == pytest.approx(230 * math.sqrt(3))
    assert ac.phase_angle_deg(vab) == pytest.approx(30.0)
    ia, ib, ic = ac.delta_line_currents(polar(10, 0), polar(10, -120), polar(10, 120))
    assert abs(ia) == pytest.approx(10 * math.sqrt(3))
    assert abs(ia + ib + ic) < 1e-9


def test_unbalanced_star_with_and_without_neutral():
    v = ac.balanced_set(230.0)
    z = [complex(10, 0), complex(20, 0), complex(40, 0)]
    i, i_n, vn = ac.unbalanced_wye(v, z, 0j)            # solid neutral
    assert abs(vn) == 0 and abs(i[0]) == pytest.approx(23.0)
    assert abs(i_n) == pytest.approx(abs(sum(i)))
    assert abs(i_n) > 0
    i2, i_n2, vn2 = ac.unbalanced_wye(v, z, None)       # floating star point
    assert abs(i_n2) < 1e-9 and abs(vn2) > 0            # star point shifts
    i3, _, _ = ac.unbalanced_wye(v, [complex(10, 0)] * 3, None)
    assert abs(i3[0]) == pytest.approx(23.0)            # balanced: no shift


def test_unbalance_factor_and_two_wattmeter():
    va, vb, vc = ac.balanced_set(230.0)
    assert ac.unbalance_factor(va, vb, vc) == pytest.approx(0.0, abs=1e-12)
    assert ac.unbalance_factor(va, vb * 0.95, vc) > 0.01
    ia, ib, ic = [x / complex(8, 6) for x in (va, vb, vc)]   # pf 0.8 lagging
    w1, w2 = ac.two_wattmeter(va, ia, ib, ic)
    total = sum(complex_power(vx, ix).real for vx, ix in zip((va, vb, vc), (ia, ib, ic)))
    assert w1 + w2 == pytest.approx(total)
    q = math.sqrt(3) * (w2 - w1)                          # sign follows meter order
    assert abs(q) == pytest.approx(sum(complex_power(vx, ix).imag
                                       for vx, ix in zip((va, vb, vc), (ia, ib, ic))))


def test_power_factor_tools():
    qc = ac.capacitor_for_pf(100e3, 0.8, 0.95)            # 100 kW: 75 - 32.87 kvar
    assert qc == pytest.approx(42.13e3, rel=1e-3)
    assert ac.q_capability(5.0, 4.0) == pytest.approx(3.0)
    with pytest.raises(ValueError):
        ac.q_capability(5.0, 6.0)
    assert ac.rms_from_harmonics([100, 4, 3]) == pytest.approx(math.sqrt(10025))
    assert ac.thd_f([100, 4, 3]) == pytest.approx(0.05)
    assert ac.power_factor_true(0.95, 0.05) == pytest.approx(0.95 / math.sqrt(1.0025))
    assert ac.k_factor([1, 5, 7], [100, 4, 3]) == pytest.approx(
        (100 ** 2 + 25 * 16 + 49 * 9) / (100 ** 2 + 16 + 9))
