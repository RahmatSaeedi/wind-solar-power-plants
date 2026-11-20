"""Chapter 6 DC functions against hand-calculated reference cases."""
import math

import numpy as np
import pytest

from plantp import dc


def test_ohm_and_power_hand_cases():
    assert dc.ohm_voltage(2.0, 5.0) == 10.0
    assert dc.ohm_current(12.0, 4.0) == 3.0
    assert dc.ohm_resistance(12.0, 3.0) == 4.0
    assert dc.power_vi(12.0, 3.0) == 36.0
    assert dc.power_i2r(3.0, 4.0) == 36.0
    assert dc.power_v2r(12.0, 4.0) == 36.0
    assert dc.energy_wh(1500.0, 4.0) == 6000.0
    with pytest.raises(ValueError):
        dc.ohm_current(1.0, 0.0)
    with pytest.raises(ValueError):
        dc.ohm_resistance(1.0, 0.0)
    with pytest.raises(ValueError):
        dc.energy_wh(1.0, -1.0)


def test_series_parallel_divider():
    assert dc.series(1.0, 2.0, 3.0) == 6.0
    assert dc.parallel(6.0, 3.0) == pytest.approx(2.0)
    assert dc.parallel(10.0, 10.0, 10.0) == pytest.approx(10.0 / 3)
    assert dc.divider_voltage(12.0, 1000.0, 1000.0) == 6.0
    with pytest.raises(ValueError):
        dc.parallel()
    with pytest.raises(ValueError):
        dc.parallel(1.0, -2.0)


def test_voltmeter_loading():
    # 12 V across 1 MOhm + 1 MOhm; a 10 MOhm meter across the lower resistor
    # sees 1 MOhm || 10 MOhm = 0.909 MOhm -> 12 * 0.909/(1 + 0.909) = 5.714 V instead of 6 V
    assert dc.voltmeter_reading(12.0, 1e6, 1e6, 10e6) == pytest.approx(5.7143, abs=1e-3)
    # an ideal meter (very large resistance) reads the true value
    assert dc.voltmeter_reading(12.0, 1e6, 1e6, 1e15) == pytest.approx(6.0, abs=1e-6)


def test_conductor_resistance_hand_case():
    # 100 m of 2.5 mm2 copper at 20 C: 1.72e-8 * 100 / 2.5e-6 = 0.688 ohm
    assert dc.conductor_resistance(100.0, 2.5, "copper", 20.0) == pytest.approx(0.688)
    # at 70 C: * (1 + 0.00393 * 50) = * 1.1965
    assert dc.conductor_resistance(100.0, 2.5, "copper", 70.0) == pytest.approx(0.688 * 1.1965)
    assert dc.resistivity_at("aluminium", 20.0) == 2.82e-8
    with pytest.raises(ValueError):
        dc.resistivity_at("gold", 20.0)
    with pytest.raises(ValueError):
        dc.conductor_resistance(10.0, 0.0)


def test_feeder_hand_case():
    # 10 A, 50 m one way, 2.5 mm2 copper, 20 C: loop R = 2 * 0.344 = 0.688 ohm
    r = dc.feeder(10.0, 50.0, 2.5, "copper", 20.0, source_voltage_v=48.0)
    assert r.loop_resistance_ohm == pytest.approx(0.688)
    assert r.drop_v == pytest.approx(6.88)
    assert r.loss_w == pytest.approx(68.8)
    assert r.drop_fraction == pytest.approx(6.88 / 48.0)
    assert dc.feeder(0.0, 50.0, 2.5).drop_v == 0.0


def test_area_for_drop_inverts_feeder():
    area = dc.area_for_drop(10.0, 50.0, 6.88, "copper", 20.0)
    assert area == pytest.approx(2.5)
    assert dc.next_standard_area(2.5) == 2.5
    assert dc.next_standard_area(2.6) == 4
    with pytest.raises(ValueError):
        dc.next_standard_area(1000.0)


def test_conductor_temperature_converges_and_exceeds_cold_estimate():
    # 20 A in 10 m of 2.5 mm2 copper, R_th = 2 K/W: cold heat = 20^2 * 0.0688 = 27.5 W -> +55 K;
    # the hot conductor has more resistance, so the steady rise is larger than 55 K
    t = dc.conductor_temperature(20.0, 10.0, 2.5, "copper", 30.0, 2.0)
    assert t > 30.0 + 55.0
    r_hot = dc.conductor_resistance(10.0, 2.5, "copper", t)
    assert t == pytest.approx(30.0 + 20.0 ** 2 * r_hot * 2.0, abs=1e-4)   # self-consistent
    with pytest.raises(ValueError):
        dc.conductor_temperature(200.0, 10.0, 2.5, "copper", 30.0, 2.0)   # thermal runaway


def test_closed_form_heating_matches_iteration():
    r20 = dc.conductor_resistance(1.0, 4.0, "copper", 20.0)        # ohm per metre
    for i in (14.0, 40.0, 60.0):
        exact = dc.conductor_temperature_closed_form(i, r20, dc.TEMP_COEFF["copper"], 30.0, 5.3)
        iterated = dc.conductor_temperature(i, 1.0, 4.0, "copper", 30.0, 5.3)
        assert exact == pytest.approx(iterated, abs=1e-4)
    # runaway current: 1 / sqrt(R20 alpha R_th)
    i_c = dc.runaway_current(r20, dc.TEMP_COEFF["copper"], 5.3)
    assert i_c == pytest.approx(1.0 / (r20 * 0.00393 * 5.3) ** 0.5)
    with pytest.raises(ValueError):
        dc.conductor_temperature_closed_form(1.01 * i_c, r20, dc.TEMP_COEFF["copper"], 30.0, 5.3)


def test_operating_point_lies_on_both_curves():
    m = dc.PVM_550
    v, i = dc.pv_resistive_operating_point(m, 26, 80.0)
    assert i == pytest.approx(v / 80.0)
    assert i == pytest.approx(float(dc.pv_iv_curve(m, 26, v)), abs=1e-6)
    v_small, i_small = dc.pv_resistive_operating_point(m, 26, 1.0)   # nearly a short circuit
    assert i_small == pytest.approx(13.98, rel=1e-3)
    with pytest.raises(ValueError):
        dc.pv_resistive_operating_point(m, 26, 0.0)


def test_max_modules_in_series():
    assert dc.max_modules_in_series(dc.PVM_550, 1500.0, -10.0) == 27
    assert dc.max_modules_in_series(dc.PVM_550, 1500.0, -20.0) == 26     # 1500 / 55.96 = 26.8
    assert dc.max_modules_in_series(dc.PVM_550, 1000.0, -10.0) == 18


def test_adiabatic_k_reproduces_the_published_order_of_magnitude():
    # first-principles k for copper 90 -> 250 C and aluminium 90 -> 250 C
    k_cu = dc.adiabatic_k("copper", 90.0, 250.0)
    k_al = dc.adiabatic_k("aluminium", 90.0, 250.0)
    assert 140 < k_cu < 146
    assert 90 < k_al < 97
    assert k_al < k_cu
    # withstand time: (k A / I)^2
    assert dc.adiabatic_withstand_time(10_000.0, 100.0, 143.0) == pytest.approx((143 * 100 / 10_000) ** 2)
    with pytest.raises(ValueError):
        dc.adiabatic_withstand_time(0.0, 100.0, 143.0)


def test_adiabatic_k_matches_a_numerical_integration():
    # integrate dT/dt = J^2 rho(T) / c_v step by step for a known current density
    material, a_mm2, i = "copper", 10.0, 2000.0
    j = i / (a_mm2 * 1e-6)
    t, temp, dt = 0.0, 90.0, 1e-4
    while temp < 250.0:
        temp += dt * j * j * dc.resistivity_at(material, temp) / dc.VOLUMETRIC_HEAT_CAPACITY[material]
        t += dt
    k = dc.adiabatic_k(material, 90.0, 250.0)
    assert t == pytest.approx(dc.adiabatic_withstand_time(i, a_mm2, k), rel=2e-3)


def test_insulation_resistance_and_parallel_scaling():
    r = dc.cylinder_insulation_resistance(1e13, 1.13e-3, 2.9e-3, 100.0)
    assert r == pytest.approx(1e13 * math.log(2.9 / 1.13) / (2 * math.pi * 100))
    # doubling the length halves the resistance (more leakage paths in parallel)
    assert dc.cylinder_insulation_resistance(1e13, 1.13e-3, 2.9e-3, 200.0) == pytest.approx(r / 2)
    with pytest.raises(ValueError):
        dc.cylinder_insulation_resistance(1e13, 3e-3, 2e-3, 1.0)


def test_diode_bridge_and_pt100():
    assert float(dc.diode_current(0.0)) == 0.0
    i1, i2 = dc.diode_current([0.6, 0.6 + 0.0257 * math.log(10)])
    assert i2 / i1 == pytest.approx(10.0, rel=0.01)          # ~60 mV per decade at 25 C
    assert dc.pt100_resistance(0.0) == 100.0
    assert dc.pt100_resistance(50.0) == pytest.approx(119.25)
    assert dc.bridge_output(5.0, 100, 100, 100, 100) == pytest.approx(0.0)
    assert dc.bridge_output(5.0, 100, 100, 100, 119.25) == pytest.approx(5 * (119.25 / 219.25 - 0.5))


def test_rc_and_inductor_energy():
    assert dc.capacitor_energy(0.01, 1100.0) == pytest.approx(6050.0)
    assert dc.inductor_energy(180e-6, 315.0) == pytest.approx(0.5 * 180e-6 * 315 ** 2)
    tau = 10e3 * 1000e-6                                       # 10 s
    assert float(dc.rc_discharge(9.0, 10e3, 1000e-6, tau)) == pytest.approx(9.0 / math.e)
    assert float(dc.rc_charge(9.0, 10e3, 1000e-6, tau)) == pytest.approx(9.0 * (1 - 1 / math.e))
    assert dc.rc_time_to_discharge(1100.0, 50.0, 50e3, 0.01) == pytest.approx(500 * math.log(22))
    with pytest.raises(ValueError):
        dc.rc_time_to_discharge(10.0, 20.0, 1.0, 1.0)


def test_euler_converges_to_the_exact_discharge():
    errors = []
    for dt in (2.0, 1.0, 0.5):
        t, v = dc.rc_discharge_euler(9.0, 10e3, 1000e-6, 30.0, dt)
        errors.append(abs(v[-1] - float(dc.rc_discharge(9.0, 10e3, 1000e-6, t[-1]))))
    assert errors[0] > errors[1] > errors[2]
    assert errors[1] / errors[2] == pytest.approx(2.0, rel=0.15)   # first-order method


def test_cell_temperature_and_kelvin():
    assert float(dc.cell_temperature_noct(20.0, 800.0, 45.0)) == pytest.approx(45.0)
    assert float(dc.cell_temperature_noct(30.0, 0.0)) == pytest.approx(30.0)
    a = dc.kelvin_optimum_area(1_000_000.0, 0.05, 5.4, 0.08)
    cost = lambda x: 0.08 * 5.4 * x + 0.05 * 1_000_000.0 / x
    assert cost(a) < cost(0.9 * a) and cost(a) < cost(1.1 * a)


def test_solver_simple_divider_with_parallel_load():
    # 12 V source (node1 to ground); 2 ohm node1-node2; 4 ohm and 4 ohm node2-ground
    sol = dc.solve_dc(3, [(1, 2, 2.0), (2, 0, 4.0), (2, 0, 4.0)], [(1, 0, 12.0)])
    assert sol.node_voltages[1] == pytest.approx(12.0)
    assert sol.node_voltages[2] == pytest.approx(6.0)
    assert sol.source_currents[0] == pytest.approx(3.0)


def test_solver_two_sources_two_loops():
    # Classic two-loop circuit: 10 V -- 2 ohm -- node2 -- 3 ohm -- 5 V (node3), 4 ohm from node2 to ground.
    # Node equation at node2: (10-V)/2 + (5-V)/3 = V/4  ->  V (1/2+1/3+1/4) = 5 + 5/3 -> V = 6.1538
    sol = dc.solve_dc(4, [(1, 2, 2.0), (2, 3, 3.0), (2, 0, 4.0)], [(1, 0, 10.0), (3, 0, 5.0)])
    assert sol.node_voltages[2] == pytest.approx(80.0 / 13.0)
    assert sol.source_currents[0] == pytest.approx((10.0 - 80.0 / 13.0) / 2.0)


def test_solver_current_source_and_errors():
    sol = dc.solve_dc(2, [(1, 0, 5.0)], current_sources=[(0, 1, 2.0)])
    assert sol.node_voltages[1] == pytest.approx(10.0)
    with pytest.raises(ValueError):
        dc.solve_dc(3, [(1, 0, 1.0)])                      # node 2 floating -> singular
    with pytest.raises(ValueError):
        dc.solve_dc(2, [(1, 0, -1.0)])


def test_thevenin_of_a_divider():
    v_th, r_th = dc.thevenin(3, [(1, 2, 4.0), (2, 0, 4.0)], [(1, 0, 12.0)], terminal_a=2)
    assert v_th == pytest.approx(6.0)
    assert r_th == pytest.approx(2.0, abs=1e-6)


def test_pv_string_voltage_limits():
    m = dc.PVM_550
    assert dc.string_voc(m, 26, 25.0) == pytest.approx(26 * 49.90)
    # -10 C: 49.90 * (1 + 0.0027 * 35) = 54.6156 per module
    assert dc.string_voc(m, 26, -10.0) == pytest.approx(26 * 54.6156, rel=1e-6)
    assert dc.string_voc(m, 28, -10.0) > 1500.0            # too many modules for a 1500 V system
    assert dc.string_isc(m, 1000.0, 25.0) == pytest.approx(13.98)
    assert dc.string_isc(m, 500.0, 25.0) == pytest.approx(6.99)
    assert dc.string_pmax(m, 26, 1000.0, 25.0) == pytest.approx(26 * 41.96 * 13.11)
    assert dc.string_pmax(m, 26, 1000.0, 65.0) == pytest.approx(26 * 41.96 * 13.11 * (1 - 0.0035 * 40))


def test_pv_iv_curve_shape():
    m = dc.PVM_550
    v = np.linspace(0, dc.string_voc(m, 26, 25.0), 200)
    i = dc.pv_iv_curve(m, 26, v)
    assert i[0] == pytest.approx(13.98, abs=1e-6)          # short circuit
    assert i[-1] == pytest.approx(0.0, abs=1e-6)           # open circuit
    assert (np.diff(i) <= 1e-9).all()                      # current never rises with voltage
    assert (dc.pv_iv_curve(m, 26, v, irradiance_wm2=0.0) == 0).all()
    p = v * i
    assert 0.9 * 26 * 550 < p.max() <= 26 * 550            # near, and never above, the datasheet P_max
