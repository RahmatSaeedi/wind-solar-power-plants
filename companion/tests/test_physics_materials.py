"""Tests of plantp.physics and plantp.materials against hand calculations (chapter 4)."""
import math

import numpy as np
import pytest

from plantp import materials as mt, physics as ph


# ---- physics ------------------------------------------------------------------------
def test_air_density_sea_level_and_humidity():
    rho = float(ph.air_density(1013.25, 15.0))
    assert rho == pytest.approx(1.2250, abs=2e-4)          # ISA sea level
    assert float(ph.air_density(1013.25, 30.0, rh=0.8)) < float(ph.air_density(1013.25, 30.0))


def test_standard_pressure():
    assert float(ph.standard_pressure(0.0)) == pytest.approx(1013.25)
    assert float(ph.standard_pressure(1200.0)) == pytest.approx(877.6, abs=0.5)


def test_betz_optimum():
    a = np.linspace(0, 0.5, 50001)
    cp = ph.betz_cp(a)
    assert cp.max() == pytest.approx(16 / 27, rel=1e-6)
    assert a[np.argmax(cp)] == pytest.approx(1 / 3, abs=1e-4)
    assert float(ph.betz_ct(1 / 3)) == pytest.approx(8 / 9)


def test_shear_and_log_law():
    assert float(ph.shear_exponent(8.0, 50, 8.0 * 2 ** 0.2, 100)) == pytest.approx(0.2)
    assert float(ph.log_law_speed(10.0, 100, 100, 0.03)) == pytest.approx(10.0)


def test_noct_and_expansion():
    assert float(ph.pv_cell_temp_noct(20, 800, 45)) == pytest.approx(45.0)
    assert ph.expansion(100.0, 12e-6, 60.0) == pytest.approx(0.072)


def test_conductor_temperature_linear_solution_and_runaway():
    t, ka = ph.conductor_temperature(100.0, 1e-3, 0.004, 10.0, 0.5, 20.0)
    # k = 10 / 5 = 2 K; T - 20 = 2 / (1 - 0.008)
    assert t == pytest.approx(20 + 2 / 0.992)
    assert ka == pytest.approx(0.008)
    t2, ka2 = ph.conductor_temperature(2000.0, 1e-3, 0.004, 10.0, 0.5, 20.0)
    assert ka2 >= 1 and math.isinf(t2)


def test_fields_and_forces():
    e = ph.coax_field(19052.0, 0.01, 0.01, 0.0188)
    assert float(e) == pytest.approx(19052.0 / (0.01 * math.log(1.88)))
    f = ph.parallel_force_per_m(1000.0, 1000.0, 1.0)
    assert float(f) == pytest.approx(0.2)                 # 2e-7 x 1e6
    assert ph.core_flux_density(230.0, 50.0, 100, 0.01) == pytest.approx(230 / 222)


def test_photon_and_planck():
    assert float(ph.photon_energy_ev(1240.0)) == pytest.approx(1.0, rel=1e-3)
    assert ph.planck_fraction_above(0.0001) == pytest.approx(1.0, abs=1e-3)
    f_si = ph.planck_fraction_above(1.12)
    assert 0.74 < f_si < 0.80                 # power carried by photons above the gap
    u = [ph.ultimate_efficiency(e) for e in np.arange(0.5, 3.0, 0.01)]
    assert max(u) == pytest.approx(0.44, abs=0.01)   # Shockley-Queisser 'ultimate' peak
    assert ph.ultimate_efficiency(1.12) == pytest.approx(0.44, abs=0.02)


def test_fresnel_and_cantilever_and_spl():
    assert float(ph.fresnel_reflectance(0.0)) == pytest.approx(0.04)
    assert float(ph.fresnel_reflectance(89.9)) > 0.9
    f1 = ph.cantilever_f1(2e11, 1e-4, 100.0, 10.0)
    assert f1 == pytest.approx(1.8751 ** 2 / (2 * math.pi) * math.sqrt(2e7 / 1e6))
    assert float(ph.spl_at_distance(105.0, 100.0)) == pytest.approx(54.0)


# ---- materials ----------------------------------------------------------------------
def test_tube_section_thin_wall_limit():
    s = mt.tube_section(4.0, 0.02)
    r = (4.0 - 0.02) / 2
    assert s.second_moment == pytest.approx(math.pi * r ** 3 * 0.02, rel=1e-3)
    with pytest.raises(ValueError):
        mt.tube_section(0.1, 0.06)


def test_cantilever_and_fatigue():
    assert mt.cantilever_tip(1000, 2.0, 2e11, 1e-6) == pytest.approx(8000 / 6e5)
    assert float(mt.basquin_cycles(50.0, 100.0, 2e6, 3)) == pytest.approx(1.6e7)
    d = mt.miner_damage([100.0, 50.0], [1e6, 8e6], 100.0, 2e6, 3)
    assert d == pytest.approx(0.5 + 0.5)


def test_crack_corrosion_mismatch():
    a = mt.critical_crack(50e6, 200e6, 1.0)
    assert a == pytest.approx(0.0625 / math.pi)
    # zinc: 1 A/m2 -> about 1.5 mm/yr (65.38 g/mol, n = 2, 7.14 g/cm3)
    assert mt.faraday_loss_um_per_yr(1.0, 65.38, 2, 7.14) == pytest.approx(1497, rel=0.01)
    assert mt.mismatch_stress(70e9, 10e-6, 100) == pytest.approx(70e6)


def test_dielectric_scores_costs():
    p = mt.dielectric_loss_w_per_m(19052.0, 50, 2e-10, 4e-4)
    assert p == pytest.approx(2 * math.pi * 50 * 2e-10 * 19052 ** 2 * 4e-4)
    s = mt.weighted_scores([[5, 3], [4, 4]], [0.6, 0.4])
    assert np.allclose(s, [4.2, 4.0])
    with pytest.raises(ValueError):
        mt.weighted_scores([[1, 2]], [0.5, 0.6])
    a, b = (10.0, 60.0, 0.5, 0.0), (8.0, 60.0, 0.05, 30000.0)
    n = mt.break_even_volume(a, b)
    assert float(mt.cost_per_part(n, *a)) == pytest.approx(float(mt.cost_per_part(n, *b)))


def test_fits_roughness_capability():
    assert mt.fit_limits((30.000, 30.021), (29.980, 29.993))[2] == "clearance"
    assert mt.fit_limits((30.000, 30.021), (30.035, 30.048))[2] == "interference"
    assert mt.fit_limits((30.000, 30.021), (30.002, 30.015))[2] == "transition"
    ra, rq = mt.roughness([1, -1, 1, -1])
    assert ra == pytest.approx(1.0) and rq == pytest.approx(1.0)
    rng = np.random.default_rng(0)
    x = rng.normal(10.0, 0.1, 100000)
    cp, cpk, ppm = mt.capability(x, 9.4, 10.6)
    assert cp == pytest.approx(2.0, rel=0.02) and cpk == pytest.approx(2.0, rel=0.02)
    assert ppm < 0.01


def test_bolt_weld_arrhenius():
    assert mt.bolt_torque(0.2, 100e3, 0.02) == pytest.approx(400.0)
    assert mt.weld_heat_input(25, 200, 5.0, 0.8) == pytest.approx(0.8)
    assert mt.arrhenius_factor(50e3, 25, 25) == pytest.approx(1.0)
    assert mt.arrhenius_factor(50e3, 25, 35) > 1.8


# ---- second part ------------------------------------------------------------------------
def test_magnetising_current_and_air_flow():
    # 1 T over 1 m of iron with mu_r 1000 and no gap: H = 1 / (mu0 1000) A/m, N = 100
    i = ph.magnetising_current(1.0, 1.0, 1000.0, 0.0, 100)
    assert i == pytest.approx(1.0 / (ph.MU0 * 1000) / 100)
    # a 1 mm gap needs as much MMF as 1 m of iron with mu_r 1000
    assert ph.magnetising_current(1.0, 0.0, 1000.0, 1e-3, 100) == pytest.approx(i)
    assert ph.air_flow_for_heat(1105.5, 1.0, 1.1, 1005.0) == pytest.approx(1.0)


def test_module_energy_balance_limits():
    t_dark = ph.module_temperature_balance(0.0, 20.0, 2.0)
    assert t_dark < 20.0                       # radiates to the colder sky at night
    t_sun = ph.module_temperature_balance(1000.0, 20.0, 1.0)
    t_wind = ph.module_temperature_balance(1000.0, 20.0, 5.0)
    assert t_sun > t_wind > 20.0
    assert ph.module_temperature_balance(800, 20, 1, h_scale=0.5) > ph.module_temperature_balance(800, 20, 1)


def test_intrinsic_ratio_grows_with_temperature_and_falls_with_gap():
    assert ph.intrinsic_ratio(1.12, 25, 25) == pytest.approx(1.0)
    assert ph.intrinsic_ratio(1.12, 25, 150) > 100
    assert ph.intrinsic_ratio(3.26, 25, 150) > ph.intrinsic_ratio(1.12, 25, 150)


def test_von_mises_buckling_mixtures():
    assert mt.von_mises(100.0, 0.0) == pytest.approx(100.0)
    assert mt.von_mises(0.0, 100.0) == pytest.approx(100 * math.sqrt(3))
    assert mt.euler_buckling(2e11, 1e-6, 2.0, 2.0) == pytest.approx(math.pi ** 2 * 2e5 / 16)
    el, et = mt.rule_of_mixtures(70e9, 3e9, 0.5)
    assert el == pytest.approx(36.5e9) and et == pytest.approx(1 / (0.5 / 70e9 + 0.5 / 3e9))
    with pytest.raises(ValueError):
        mt.rule_of_mixtures(70e9, 3e9, 1.2)


def test_ageing_and_halving_interval():
    assert mt.life_consumed([90, 90], [1, 1], 90, 100e3) == pytest.approx(2.0)
    d = mt.halving_interval_k(100e3, 90)
    assert mt.life_consumed([90 + d], [1], 90, 100e3) == pytest.approx(2.0)
    assert mt.adiabatic_rise(350, 350) == pytest.approx(350 * 350 / 2400)


def test_sampling_and_stacks():
    assert float(mt.accept_probability(50, 1, 0.0)) == pytest.approx(1.0)
    assert float(mt.accept_probability(10, 0, 0.1)) == pytest.approx(0.9 ** 10)
    assert mt.stack([0.1, 0.2, 0.2]) == pytest.approx(0.5)
    assert mt.stack([0.3, 0.4], "rss") == pytest.approx(0.5)
    with pytest.raises(ValueError):
        mt.stack([1], "mean")


# ---- third part -----------------------------------------------------------------------
def test_skin_effect():
    d = ph.skin_depth(1.72e-8, 50.0)
    assert d == pytest.approx(9.33e-3, rel=0.01)
    assert ph.ac_dc_ratio_round(1e-4, 1.72e-8, 50.0) == pytest.approx(1.0, abs=1e-6)
    r = 0.1                                   # far beyond the skin depth
    x = math.sqrt(2) * r / d
    assert ph.ac_dc_ratio_round(r, 1.72e-8, 50.0) == pytest.approx(x / (2 * math.sqrt(2)) + 0.25, rel=0.01)


def test_air_mass_and_beam():
    assert float(ph.air_mass(90)) == pytest.approx(1.0)
    assert float(ph.air_mass(30)) == pytest.approx(2.0)
    assert float(ph.meinel_dni(90)) == pytest.approx(1353 * 0.7)


def test_inflow_kennelly_levels():
    w, phi = ph.inflow(10.0, 0.0, 1.0, 10.0)
    assert w == pytest.approx(math.sqrt(200)) and phi == pytest.approx(45.0)
    r = ph.kennelly_resistance(1.0, 1.0, 0.1)
    assert r == pytest.approx(math.acosh(20) / (2 * math.pi))
    assert ph.sum_levels_db([40, 40]) == pytest.approx(40 + 10 * math.log10(2))


# ---- fourth part ----------------------------------------------------------------------
def test_inductance_transmissibility():
    l = ph.line_inductance_per_m(1.0, 1.0 / 0.7788)
    assert l == pytest.approx(0.0)
    assert ph.line_inductance_per_m(math.e * 0.7788 * 0.01, 0.01) == pytest.approx(2e-7, rel=1e-6)
    assert float(ph.transmissibility(0.0, 10.0)) == pytest.approx(1.0)
    assert float(ph.transmissibility(100.0, 10.0)) == pytest.approx(1 / 99)
    assert float(ph.transmissibility(10 * math.sqrt(2), 10.0, 0.3)) == pytest.approx(1.0)


def test_adiabatic_heating():
    k_cu = ph.adiabatic_k(3.45e6, 1.72e-8, 234.5)
    assert k_cu / 1e6 == pytest.approx(226, rel=0.01)     # A s^0.5 per mm2
    t = ph.adiabatic_final_temp(0.0, 1.0, 1e-4, 90.0, 3.45e6, 1.72e-8, 234.5)
    assert t == pytest.approx(90.0)
    # small step: dT ~ (I/A)^2 rho(T) t / c_v
    i, a, tt = 1000.0, 1e-4, 0.01
    t_end = ph.adiabatic_final_temp(i, tt, a, 20.0, 3.45e6, 1.72e-8, 234.5)
    assert t_end - 20 == pytest.approx((i / a) ** 2 * 1.72e-8 * tt / 3.45e6, rel=1e-3)


def test_joint_weld_infusion():
    assert mt.joint_load_factor(1.0, 4.0) == pytest.approx(0.2)
    assert mt.fillet_weld_stress(7071.0, 0.01, 1.0) == pytest.approx(1.0e6, rel=1e-4)
    assert mt.infusion_time(0.2, 0.5, 1.0, 1e-10, 1e5) == pytest.approx(0.2 * 0.5 / (2e-5))


# ---- fifth part -----------------------------------------------------------------------
def test_wien_thermography_density():
    assert ph.wien_peak_um(5778) == pytest.approx(0.5015, rel=1e-3)
    assert ph.wien_peak_um(300) == pytest.approx(9.66, rel=1e-3)
    # correct emissivity setting returns the true temperature
    assert ph.apparent_temperature(80, 0.6, 0.6, 30) == pytest.approx(80.0)
    # a shiny surface read with a high setting looks close to the surroundings
    t = ph.apparent_temperature(80, 0.05, 0.95, 30)
    assert 30 < t < 40
    assert ph.relative_air_density(1013.25, 20.0) == pytest.approx(1.0)
