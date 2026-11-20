"""Chapter 4 — numerical answers of the end-of-chapter problems (exr-ch04-N).

Run from the project root:   python -m companion.ch04.solutions
Writes companion/ch04/expected/solutions.txt (lines of at most 78 characters).
"""
from __future__ import annotations

import math
import textwrap

import numpy as np

from companion.ch04.common import EXPECTED
from companion.ch04 import lab_rainflow as lr
from plantp import datapack, materials as mt, numerics as nm, physics as ph, screening as sc

LINES: list[str] = []


def p(num, *items) -> None:
    LINES.extend(textwrap.wrap(f"P{num:02d}: " + "; ".join(items), 78, subsequent_indent="     "))


def level_1_2() -> None:
    w = 10.5 * 2 * math.pi / 60
    p(1, f"10.5 rpm = {w:.4f} rad/s", f"tip speed {w * 75:.1f} m/s")
    p(2, f"KE = {0.5 * 2 * 9:.0f} J", f"PE = {1000 * ph.G0 * 100 / 1e6:.3f} MJ = "
      f"{1000 * ph.G0 * 100 / 3.6e6:.3f} kWh")
    p(3, f"rho(900 hPa, 10 C) = {float(ph.air_density(900, 10)):.3f} kg/m3")
    p(4, f"1/2 x 1.05 x 8^3 = {0.5 * 1.05 * 8 ** 3:.1f} W/m2")
    p(5, f"steel 10 m, 60 K: {ph.expansion(10, 12e-6, 60) * 1000:.1f} mm")
    p(6, f"1000 nm: {float(ph.photon_energy_ev(1000)):.3f} eV",
      f"1.12 eV: {1239.84 / 1.12:.0f} nm")
    p(7, f"200 MPa / 210 GPa x 2 m = {200e6 / 210e9 * 2 * 1000:.3f} mm")
    p(8, f"n 1.5: {float(ph.fresnel_reflectance(0, 1, 1.5)):.3f}",
      f"n 1.33: {float(ph.fresnel_reflectance(0, 1, 1.33)):.4f}")
    p(9, f"steel at 0.01 A/m2: {mt.faraday_loss_um_per_yr(0.01, 55.85, 2, 7.87):.1f} um/yr")
    p(11, f"Cp(0.2) = {float(ph.betz_cp(0.2)):.3f}", f"Cp(0.4) = {float(ph.betz_cp(0.4)):.3f}")
    p(12, f"alpha 0.171: {7.10 * 1.5 ** 0.171:.2f} m/s", f"alpha 0.12: {7.10 * 1.5 ** 0.12:.2f} m/s")
    r20 = 1.72e-8 / 8e-4
    t, ka = ph.conductor_temperature(1800, r20, 0.00393, 10, 0.18, 40)
    p(13, f"Cu 80 x 10 at 1800 A: {t:.1f} C (k alpha {ka:.3f})")
    u0 = 132e3 / math.sqrt(3)
    p(14, f"E at 15 mm = {float(ph.coax_field(u0, 0.015, 0.015, 0.033)) / 1e6:.2f} kV/mm",
      f"at 33 mm {float(ph.coax_field(u0, 0.033, 0.015, 0.033)) / 1e6:.2f} kV/mm")
    p(15, f"40 kA, 0.5 m: {float(ph.parallel_force_per_m(40e3, 40e3, 0.5)):.0f} N/m")
    p(16, f"N = 400 / (4.44 x 50 x 0.01 x 1.5) = {400 / (4.44 * 50 * 0.01 * 1.5):.0f} turns")
    sec = mt.tube_section(0.5, 0.01)
    p(17, f"tube 0.5 m x 10 mm, 20 m: f1 = "
      f"{ph.cantilever_f1(210e9, sec.second_moment, 7850 * sec.area, 20):.2f} Hz")
    p(18, f"2 km: {float(ph.spl_at_distance(105, 2000)):.1f} dB(A)",
      f"12 equal at 1 km: {float(ph.spl_at_distance(105, 1000)) + 10 * math.log10(12):.1f} dB(A)")
    p(19, f"40 MPa: {float(mt.basquin_cycles(40, 71, 2e6, 3)):.3g} cycles",
      f"80 MPa: {float(mt.basquin_cycles(80, 71, 2e6, 3)):.3g}")
    p(20, f"a_c = {mt.critical_crack(40e6, 150e6) * 1000:.1f} mm")


def level_3() -> None:
    hourly = datapack.load_hourly()
    curve = datapack.load_power_curve()
    vs, pk = curve["wind_speed_ms"].to_numpy(), curve["power_kw"].to_numpy()
    v = hourly["ws_100m_ms"].to_numpy()
    e0 = float(np.sum(sc.wind_power_mw(v, vs, pk, 12))) / 1e3
    p2000 = float(ph.standard_pressure(2100.0))
    rho2000 = float(ph.air_density(p2000, 5.0))
    e2000 = float(np.sum(sc.wind_power_mw(v * (rho2000 / 1.225) ** (1 / 3), vs, pk, 12))) / 1e3
    p(21, f"2100 m hub, 5 C: p {p2000:.0f} hPa, rho {rho2000:.3f}",
      f"energy {e2000:.1f} GWh ({100 * (e2000 / e0 - 1):+.1f} %)")
    day = datapack.load_hourly("day_winter")
    g, t = day["ghi_wm2"].to_numpy(), day["t_air_c"].to_numpy()
    tc = np.asarray(ph.pv_cell_temp_noct(t, g, 45.0))
    p(22, f"winter day: max cell {tc.max():.1f} C",
      f"irradiance-weighted change {float(np.sum(g * -0.35 * (tc - 25)) / np.sum(g)):+.1f} %")
    f13 = float(ph.rotor_thrust(1.05, math.pi * 75 ** 2, 13, 0.7))
    s5 = mt.tube_section(5.0, 0.040)
    p(23, f"thrust {f13 / 1e3:.0f} kN", f"moment {f13 * 100 / 1e6:.1f} MN m",
      f"sigma_b {f13 * 100 / s5.modulus / 1e6:.0f} MPa")
    pv = np.asarray(sc.pv_ac_power_mw(hourly["ghi_wm2"], 60, 50))
    wind = np.asarray(sc.wind_power_mw(v, vs, pk, 12))
    i = np.minimum(pv + wind, 100.0) * 1e6 / (math.sqrt(3) * 33e3 * 0.95)
    t_room = hourly["t_air_c"].to_numpy() + 15.0
    r20 = 1.72e-8 / (0.1 * 0.01)
    temps = np.array([ph.conductor_temperature(a, r20, 0.00393, 10, 0.22, b)[0]
                      for a, b in zip(i, t_room)])
    p(24, f"Cu 100 x 10: T max {temps.max():.1f} C, hours above 90 C {int((temps > 90).sum())}")
    p(25, f"115 um at 2 um/yr: {115 / 2:.1f} yr", f"at 4 um/yr: {115 / 4:.1f} yr")
    c = 2 * math.pi * 8.854e-12 * 2.3 / math.log(1.8)
    ic = 2 * math.pi * 50 * c * (33e3 / math.sqrt(3)) * 5000
    p(27, f"5 km: I_c = {ic:.2f} A", f"Q = sqrt3 x 33 kV x I_c = {math.sqrt(3) * 33e3 * ic / 1e3:.0f} kvar")
    z = np.linspace(25.0, 175.0, 3001)
    chord = 2 * np.sqrt(np.maximum(75.0 ** 2 - (z - 100.0) ** 2, 0.0))
    wts = chord / np.trapezoid(chord, z)
    for a_ in (0.25,):
        cube = float(np.trapezoid(wts * (z / 100.0) ** (3 * a_), z))
        p(28, f"alpha {a_}: rotor-equivalent / hub = {cube ** (1 / 3):.4f}")
    dry = float(ph.air_density(1013.25, 35))
    wet = float(ph.air_density(1013.25, 35, rh=0.6))
    p(29, f"35 C sea level: dry {dry:.4f}, 60 % rh {wet:.4f} ({100 * (wet / dry - 1):+.2f} %)")
    r75 = float(ph.fresnel_reflectance(75))
    p(30, f"75 deg: reflectance {r75:.3f}, transmission relative to normal "
      f"{(1 - r75) / (1 - float(ph.fresnel_reflectance(0))):.3f}")


def hot_joint_months(ha: float, ea: float, rc0: float = 30e-6):
    hourly = datapack.load_hourly()
    curve = datapack.load_power_curve()
    vs, pk = curve["wind_speed_ms"].to_numpy(), curve["power_kw"].to_numpy()
    pv = np.asarray(sc.pv_ac_power_mw(hourly["ghi_wm2"], 60, 50))
    wind = np.asarray(sc.wind_power_mw(hourly["ws_100m_ms"].to_numpy(), vs, pk, 12))
    i = np.minimum(pv + wind, 100.0) * 1e6 / (math.sqrt(3) * 33e3 * 0.95) / 2
    hours = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]) * 24
    edges = np.concatenate([[0], np.cumsum(hours)])
    i_peak = np.array([np.quantile(i[a:b], 0.99) for a, b in zip(edges[:-1], edges[1:])])
    t_room = np.array([np.mean(hourly["t_air_c"].to_numpy()[a:b]) for a, b in
                       zip(edges[:-1], edges[1:])]) + 15.0
    rc = rc0
    for month in range(120):
        t_j = t_room[month % 12] + i_peak[month % 12] ** 2 * rc / ha
        if t_j > 105:
            return month
        rc *= math.exp(0.08 * mt.arrhenius_factor(ea, 40.0, t_j) / 12)
    return None


def level_3b_4() -> None:
    m1 = hot_joint_months(2.0, 70e3)
    p(26, f"h A = 2.0 W/K: 30 micro-ohm joint exceeds 105 C in month {m1}")
    e_st, rho_st, top = 210e9, 7850.0, 350e3

    def f1_of(t):
        sec = mt.tube_section(4.5, t)
        k = 3 * e_st * sec.second_moment / 100 ** 3
        return math.sqrt(k / (top + 0.24 * rho_st * sec.area * 100)) / (2 * math.pi)
    root = nm.bisection(lambda t: f1_of(t) - 0.25, 0.02, 0.10)
    p(31, f"D 4.5 m, f1 = 0.25 Hz needs t = {root.root * 1000:.1f} mm "
      f"({root.iterations} bisection steps)")
    f0 = 0.7 * 830e6 * 817e-6
    tq = mt.bolt_torque(0.15, f0, 0.036)
    p(32, f"torque {tq / 1e3:.2f} kN m", f"K 0.12 .. 0.18 -> preload "
      f"{tq / (0.18 * 0.036) / 1e3:.0f} .. {tq / (0.12 * 0.036) / 1e3:.0f} kN")
    mat = [[4, 2, 5, 5], [4, 4, 4, 4], [4, 5, 1, 2]]
    s_ = mt.weighted_scores(mat, [0.3, 0.25, 0.35, 0.1])
    p(33, "weights 0.30/0.25/0.35/0.10: HDG {:.2f}, thicker HDG {:.2f}, stainless {:.2f}".format(*s_))
    n_be = mt.break_even_volume((4.0, 60.0, 0.25, 0.0), (0.8, 80.0, 0.01, 40_000.0))
    p(34, f"tool 40 000: break-even {n_be:,.0f} parts")
    p(35, "shaft 600.090 .. 600.100 mm gives interference 0.020 .. 0.100 mm (tolerance 10 um)")
    p(36, f"sigma 13 kN, half tolerance 47.5 kN: Cpk = 1 when the mean has moved "
      f"47.5 - 3 x 13 = {47.5 - 3 * 13:.1f} kN from the centre")
    p(37, f"stress factor for D = 0.5 from 1.09: (0.5/1.09)^(1/3) = {(0.5 / 1.09) ** (1 / 3):.3f}")
    p(38, f"a50 1.0, s 0.3: a90 = {1.0 * math.exp(0.3 * math.log(9)):.2f} mm")
    p(39, f"Al frame on glass, 80 K: {(23e-6 - 9e-6) * 80 * 1000:.2f} mm per m")
    r20 = 2.82e-8 / 1e-3
    p(40, f"Al 100 x 10, h 10: runaway above {math.sqrt(10 * 0.22 / (r20 * 0.00403)):,.0f} A "
      "(linear model)")


def level_5() -> None:
    rng = np.random.default_rng(20260201)
    t = np.arange(0, 600, 0.1)
    noise = np.convolve(rng.normal(0, 6, t.size), np.ones(5) / 5, mode="same")
    base = 40 + 15 * np.sin(2 * math.pi * t / 300) + 8 * np.sin(2 * math.pi * 0.525 * t)
    d_ref = lr.damage(lr.rainflow(lr.turning_points(base + noise)))
    out = []
    for f in (0.5, 0.0):
        d = lr.damage(lr.rainflow(lr.turning_points(base + f * noise)))
        out.append(f"turbulence x {f}: damage {d / d_ref:.2f} of reference")
    p(47, *out)
    for ea in (50e3, 90e3):
        p(48, f"Ea {ea / 1e3:.0f} kJ/mol: 30 micro-ohm joint fails in month {hot_joint_months(1.2, ea)}")


def part_two() -> None:
    """Problems 51-85 on the second to fifth parts of the chapter."""
    w = 60 * 2 * math.pi / 60
    p(51, f"1 kg, 1 m, 60 rpm: m omega^2 r = {w ** 2:.1f} N")
    p(52, f"B 1.5 T, 2 m iron, mu_r 5000, 200 turns: i = "
      f"{ph.magnetising_current(1.5, 2.0, 5000.0, 0.0, 200):.2f} A peak")
    p(53, f"M 100 g/mol, n 2: {2 * 96485 / (3.6 * 100):.0f} mAh/g")
    p(54, f"copper at 400 Hz: skin depth {ph.skin_depth(1.72e-8, 400) * 1000:.2f} mm")
    p(55, f"500 C: Wien peak {ph.wien_peak_um(773.15):.2f} um")
    p(56, "Kt 3 x 50 MPa = 150 MPa at the hole edge")
    p(57, f"dx 0.2, dy 0.1: true position {2 * math.hypot(0.2, 0.1):.3f} mm (accept)")
    p(58, f"sigma 300, tau 100: von Mises {mt.von_mises(300, 100):.0f} MPa")
    p(59, f"angle brace, 1.5 m pinned: {mt.euler_buckling(210e9, 4.6e-8, 1.5) / 1e3:.1f} kN")
    el, et = mt.rule_of_mixtures(72e9, 3e9, 0.6)
    p(60, f"V_f 0.6: E along {el / 1e9:.1f} GPa, across {et / 1e9:.1f} GPa")
    p(61, f"Ea 80 kJ/mol near 105 C: rate doubles every {mt.halving_interval_k(80e3, 105):.1f} K")
    p(62, f"45 deg: air mass {float(ph.air_mass(45)):.3f}, model DNI {float(ph.meinel_dni(45)):.0f} W/m2")
    t50 = float(ph.transmissibility(100.0, 50.0, 0.05))
    p(63, f"f_n 50 Hz at 100 Hz: transmissibility {t50:.3f} ({20 * math.log10(t50):+.1f} dB)")
    p(64, f"Cu 95 mm2, 10 kA, 0.5 s from 90 C: "
      f"{ph.adiabatic_final_temp(10e3, 0.5, 95e-6, 90.0, 3.45e6, 1.72e-8, 234.5):.0f} C")
    loss = 3e6 * 0.015 / 0.985
    q = ph.air_flow_for_heat(loss, 15.0, 1.05)
    p(65, f"3 MW inverter: losses {loss / 1e3:.1f} kW, air {q:.2f} m3/s at 1200 m")
    r = ph.kennelly_resistance(2.0, 1.0, 0.05)
    p(66, f"rho_soil 2.0, depth 1.0 m: R_th {r:.2f} K m/W, rise {r * 572 ** 2 * 0.125e-3:.0f} K")
    hourly = datapack.load_hourly()
    curve = datapack.load_power_curve()
    vs, pk = curve["wind_speed_ms"].to_numpy(), curve["power_kw"].to_numpy()
    pv = np.asarray(sc.pv_ac_power_mw(hourly["ghi_wm2"], 60, 50))
    wind = np.asarray(sc.wind_power_mw(hourly["ws_100m_ms"].to_numpy(), vs, pk, 12))
    i = np.minimum(pv + wind, 100.0) * 1e6 / (math.sqrt(3) * 33e3 * 0.95)
    t_room = hourly["t_air_c"].to_numpy() + 15.0
    temps = np.array([ph.conductor_temperature(a, 1.72e-8 / 1e-3, 0.00393, 10, 0.22, b)[0]
                      for a, b in zip(i, t_room)])
    p(67, f"Cu 100 x 10: {mt.life_consumed(temps, np.ones(temps.size), 90, 100e3):.0f} "
      "equivalent hours at 90 C per year")
    p(68, f"45 MPa: annealed {1 - math.exp(-(45 / 50) ** 7):.3f}, tempered "
      f"{1 - math.exp(-(45 / 150) ** 7):.1e}")
    pa = mt.accept_probability(32, 1, [0.01, 0.05])
    p(69, f"plan n 32, c 1: P(accept) {pa[0]:.3f} at 1 %, {pa[1]:.3f} at 5 %")
    xs, ys = np.arange(4) * 750.0, np.arange(3) * 1050.0
    d = np.array([math.hypot(x + 1200.0, y - 1050.0) for x in xs for y in ys])
    p(70, f"house 1200 m west: total {ph.sum_levels_db(ph.spl_at_distance(105.0, d)):.1f} dB(A)")
    p(71, f"absorptance 0.3: {0.3 * 1000 * 0.05:.0f} W/m = "
      f"{100 * 15 / (572 ** 2 * 0.125e-3):.0f} % of the Joule loss")
    f0 = 475e3
    t_th = f0 * (0.16 * 4e-3 + 0.58 * 0.16 * 33.402e-3)
    tau = 16 * t_th / (math.pi * ((33.402e-3 + 31.093e-3) / 2) ** 3)
    vm = mt.von_mises(f0 / 817e-6, tau)
    p(72, f"thread friction 0.16: thread torque {t_th:.0f} N m, von Mises {vm / 1e6:.0f} MPa "
      f"= {vm / 830e6:.0%} of proof")
    phi3 = mt.joint_load_factor(1.0, 3.0)
    p(73, f"k_c = 3 k_b: load factor {phi3:.2f}; losing preload multiplies damage by "
      f"{(1 / phi3) ** 3:.0f}")
    t06 = mt.infusion_time(0.25, 0.5, 0.6, 2e-10, 0.9e5)
    p(74, f"inlets 1.2 m apart (0.6 m each way): {t06 / 60:.0f} min")
    z = np.linspace(0.5, 100.0, 400)
    dd = 5.0 - 1.5 * z / 100.0
    wv = 0.5 * 1.225 * (36.6 * (z / 100.0) ** 0.171) ** 2 * 1.0 * dd
    p(75, f"C_d 1.0 in the 50-year wind: drag {nm.trapezoid(wv, z[1] - z[0]) / 1e3:.0f} kN, moment "
      f"{nm.trapezoid(wv * z, z[1] - z[0]) / 1e6:.1f} MN m")
    p(76, f"tolerance 0.05 mm, micrometer U 0.004: TUR {0.05 / 0.008:.2f}")
    p(77, f"pile +-10: worst {mt.stack([10, 3, 2, 1.5]):.1f} mm, RSS "
      f"{mt.stack([10, 3, 2, 1.5], 'rss'):.1f} mm")
    p(78, f"60 C joint, eps 0.6: set 0.6 reads {ph.apparent_temperature(60, 0.6, 0.6, 25):.1f} C, "
      f"set 0.95 reads {ph.apparent_temperature(60, 0.6, 0.95, 25):.1f} C")
    seg = math.sqrt(500 / math.pi) / 1000
    whole = math.sqrt(2000 / math.pi) / 1000
    p(80, f"2000 mm2 solid: R_ac/R_dc {ph.ac_dc_ratio_round(whole, 1.72e-8, 50):.3f}; "
      f"500 mm2 segment {ph.ac_dc_ratio_round(seg, 1.72e-8, 50):.3f} (isolated segments)")
    k_cu = ph.adiabatic_k(3.45e6, 1.72e-8, 234.5)
    t_lim = (k_cu * 35e-6 / 2e3) ** 2 * math.log((250 + 234.5) / (70 + 234.5))
    p(81, f"35 mm2 Cu screen, 2 kA, 70 to 250 C: {t_lim:.1f} s")
    p(82, f"V/A 7.5 cm: {2.5 * 7.5 ** 2:.0f} min to solidify")
    kwh = hourly["ghi_wm2"].to_numpy().sum() / 1000.0
    site_h = kwh * 0.05 * 1000.0 / 60.0
    p(83, f"6000 h chamber = {6000 / site_h:.1f} site-years of UV dose")
    gj = (494e3 * 35 + 255e3 * 35 + 60e3 * 100 + 35e3 * 60 + 600 * 2400 * 1.5 + 60e3 * 35) / 1e3
    p(84, f"steel 35 MJ/kg: {gj:,.0f} GJ, payback {12 * gj / (16.68e6 * 3.6 / 1e3):.1f} months")


def part_three() -> None:
    """Problems 86-110 on the fourth and fifth parts of the chapter."""
    p(86, f"6 poles at 60 Hz: {120 * 60 / 6:.0f} rpm")
    p(87, f"100 um zinc: {100 * 7.14:.0f} g/m2")
    p(88, f"10 microseconds in steel: {5920 * 10e-6 / 2 * 1000:.1f} mm")
    p(89, f"1 m of 2.5 mm2: copper {1.72e-8 / 2.5e-6 * 1000:.2f} milliohm, structural steel "
      f"{1.7e-7 / 2.5e-6 * 1000:.0f} milliohm")
    p(90, f"C 0.20, Mn 1.20: CE {0.20 + 1.20 / 6:.2f}")
    w_r = 10.5 * 2 * math.pi / 60
    wv, phi = ph.inflow(10.0, 1 / 3, w_r, 25.0)
    p(91, f"r 25 m: W {wv:.1f} m/s, inflow angle {phi:.1f} deg")
    p(92, f"R_ha x 1.3 at 50 C: junction {50 + 2000 * (0.020 + 0.010 + 0.015 * 1.3):.0f} C")
    l2 = ph.line_inductance_per_m(2.0 * 2 ** (1 / 3), 0.009)
    p(93, f"2 m flat spacing: X {2 * math.pi * 50 * l2 * 1000:.3f} ohm/km")
    tau2 = 8960 * 385 * 16e-4 / (10 * 0.36)
    p(94, f"2 x (80 x 10): tau {tau2 / 60:.1f} min (mass and surface both double)")
    p(95, f"tip 100 m/s vs 82.5 m/s: erosion x {(100 / 82.5) ** 7:.2f}")
    p(96, f"4 bolts, 200 kN, mu 0.3: slip resistance {0.3 * 4 * 200:.0f} kN")
    p(97, f"870 hPa, 40 C: delta {ph.relative_air_density(870, 40):.3f}")
    area = math.pi / 4 * (0.6 ** 2 - 0.4 ** 2)
    p(98, f"feed 0.2 mm/rev: {area / (0.2e-3 * 150):.1f} min per pass; roughness x {(0.2 / 0.4) ** 2:.2f}")
    cap = 96485 * 2 / 65.38 / 3600 * 1000
    p(99, f"0.2 A for 25 years: {0.2 * 25 * 8760 / (cap * 0.95 * 0.85):.0f} kg of zinc")
    i_r = 100e6 / (3 * 33e3)
    a25 = i_r / 2.5 * 1e-6
    r25 = 1.72e-8 * (1 + 0.00393 * 55) * 175 * 2.5 / a25
    p(100, f"2.5 A/mm2: conductor {a25 * 1e6:.0f} mm2, loss {3 * i_r ** 2 * r25 / 1e3:.0f} kW, "
      f"copper {3 * 8960 * 175 * 2.5 * a25 / 1000:.2f} t")
    r = ph.kennelly_resistance(1.2, 0.6, 0.05)
    p(101, f"depth 0.6 m, rho 1.2: R_th {r:.2f} K m/W, rise {r * 572 ** 2 * 0.125e-3:.0f} K")
    df = 4 * 30e6 / (140 * 4.7)
    phi_j = mt.joint_load_factor(1.0, 5.0)
    p(102, f"+-30 MN m: {df / 1e3:.0f} kN per bolt; stress swing {phi_j * df / 817e-6 / 1e6:.1f} MPa "
      f"preloaded, {df / 817e-6 / 1e6:.0f} MPa if loose")
    p(103, f"leg for 100 MPa: s = F / (0.707 L sigma) = {50e3 / (0.7071 * 0.2 * 100e6) * 1000:.1f} mm")
    l_max = math.sqrt(2 * 2e-10 * 0.9e5 * 7200 / (0.25 * 0.5))
    p(104, f"2 h pot life: longest flow length {l_max:.2f} m")
    p(105, f"low preload with occurrence 7: RPN {8 * 7 * 4} (ties with the thermography mode)")
    p(106, f"tip 75 m/s instead of 82.5: erosion x {(75 / 82.5) ** 7:.2f}")
    am = float(ph.air_mass(77.8)) * 877.2 / 1013.25
    p(107, f"pressure-corrected air mass {am:.3f}: DNI {1353 * 0.7 ** (am ** 0.678):.0f} W/m2 "
      f"(uncorrected {float(ph.meinel_dni(77.8)):.0f})")
    r_al = math.sqrt(1000 / math.pi) / 1000
    p(108, f"Al 1000 mm2 round: R_ac/R_dc {ph.ac_dc_ratio_round(r_al, 2.82e-8, 50):.3f}")
    k_al = ph.adiabatic_k(2.5e6, 2.82e-8, 228.0)
    t_f = ph.adiabatic_final_temp(31.5e3, 1.0, 400e-6, 90.0, 2.5e6, 2.82e-8, 228.0)
    a_min = 31.5e3 * math.sqrt(1.0 / math.log((250 + 228) / (90 + 228))) / k_al
    p(109, f"Al 400 mm2, 31.5 kA 1 s: {t_f:.0f} C; minimum area for 250 C {a_min * 1e6:.0f} mm2")


def part_four() -> None:
    """Problems 111-125 on foundations, errors, lab 3 and inspection."""
    p(111, f"100 m3 under water: uplift {1000 * 9.80665 * 100 / 1e6:.2f} MN")
    p(112, f"base 24 m: B/6 = {24 / 6:.1f} m")
    n_dry = 600 * 24e3 + 800 * 18e3 + 844e3 * 9.80665
    p(113, f"base 22 m, operating, dry: FS {n_dry * 11 / 89.8e6:.2f}, e {89.8e6 / n_dry:.2f} m "
      f"(B/6 = {22 / 6:.2f} m)")
    p(114, f"peak 325 V and 10 A in phase: true mean power {325 * 10 / 2:.0f} W, "
      f"wrong product {325 * 10:.0f} W")
    ce = 0.12 + 1.30 / 6 + (0.30 + 0.20 + 0.0) / 5 + (0.05 + 0.10) / 15
    p(115, f"heat B with Cr 0.30 and Mo 0.20: CE {ce:.3f}")
    year = datapack.load_hourly()
    curve = datapack.load_power_curve()
    vs, pk = curve["wind_speed_ms"].to_numpy(), curve["power_kw"].to_numpy()
    pv = np.asarray(sc.pv_ac_power_mw(year["ghi_wm2"], 60, 50))
    wind = np.asarray(sc.wind_power_mw(year["ws_100m_ms"].to_numpy(), vs, pk, 12))
    i_y = np.minimum(pv + wind, 100.0) * 1e6 / (math.sqrt(3) * 33e3 * 0.95)
    t_y = year["t_air_c"].to_numpy() + 15.0
    d = 190                                               # day 191 (lab_transient)
    cur, room = i_y[24 * d:24 * d + 24], t_y[24 * d:24 * d + 24]
    a2, per2 = 16e-4, 0.36
    r2 = 1.72e-8 / a2
    c2 = 8960 * 385 * a2

    def rhs(t, y):
        h = min(int(t // 3600), 23)
        return (cur[h] ** 2 * r2 * (1 + 0.00393 * (y - 20)) - 10 * per2 * (y - room[h])) / c2
    t0, _ = ph.conductor_temperature(cur[0], r2, 0.00393, 10, per2, room[0])
    _, yy = nm.rk4(rhs, t0, 0.0, 86400.0, 60.0)
    p(116, f"Cu 2 x (80 x 10) on day 191: transient maximum {float(np.max(yy)):.1f} C")
    p(117, f"r 70 m vs tip 75 m: erosion x {(70 / 75) ** 7:.3f}")
    p(118, f"thermography detection 2: RPN {8 * 4 * 2}")
    p(119, f"bright copper (0.05) at 80 C in a 10 C room, set 0.95: reads "
      f"{ph.apparent_temperature(80, 0.05, 0.95, 10):.1f} C")
    n_ext = n_dry
    p(120, f"extreme case dry: e {150e6 / n_ext:.2f} m -> base B >= 6 e = {6 * 150e6 / n_ext:.1f} m "
      "(weights unchanged)")
    kwh = year["ghi_wm2"].to_numpy().sum() / 1000.0
    p(121, f"25 site-years of UV at 60 W/m2: {25 * kwh * 0.05 * 1000 / 60:,.0f} h")
    k_cu = ph.adiabatic_k(3.45e6, 1.72e-8, 234.5)
    a_min = 2e3 * math.sqrt(1.0 / math.log((250 + 234.5) / (70 + 234.5))) / k_cu
    p(122, f"Cu screen for 2 kA 1 s, 70 to 250 C: at least {a_min * 1e6:.1f} mm2")
    sec = mt.tube_section(5.0, 0.040)
    p(123, f"S = I / D instead of I / (D/2): stress {89.8e6 / (sec.second_moment / 5.0) / 1e6:.0f} "
      f"MPa instead of {89.8e6 / sec.modulus / 1e6:.0f} MPa")


def part_five() -> None:
    """Problems 126-129: flatness, foundation and lab 3."""
    rng = np.random.default_rng(20260304)
    ang = np.radians(np.arange(16) * 22.5)
    x, y = 2.35 * np.cos(ang), 2.35 * np.sin(ang)
    z = 0.0004 * x - 0.0002 * y + 0.00025 * np.cos(2 * ang) + rng.normal(0, 0.00005, 16)
    a8 = np.column_stack([np.ones(8), x[::2], y[::2]])
    c8, *_ = np.linalg.lstsq(a8, z[::2], rcond=None)
    r8 = z[::2] - a8 @ c8
    p(126, f"8 of the 16 points: flatness {(r8.max() - r8.min()) * 1000:.2f} mm")
    n = 600 * 24e3 + 800 * 18e3 + 844e3 * 9.80665
    p(127, f"N {n / 1e6:.1f} MN: extreme moment for e = B/6 = 3.33 m: {n * 20 / 6 / 1e6:.0f} MN m")
    p(128, f"FS of question 1 in the self-check: 30 x 9 / 90 = {30 * 9 / 90:.1f}")
    p(129, f"time constant / data step: busbar {25.6 / 60:.2f}; buried cable 3 h -> {180 / 60:.0f}")


def main() -> None:
    level_1_2()
    level_3()
    level_3b_4()
    level_5()
    part_two()
    part_three()
    part_four()
    part_five()
    text = "\n".join(LINES) + "\n"
    (EXPECTED / "solutions.txt").write_text(text, encoding="utf-8", newline="\n")
    print(text)


if __name__ == "__main__":
    main()
