"""Chapter 4, section A — energy and fields: mechanics, fluids, heat, electromagnetism,
light, vibration, sound and storage, applied to Plant P.

Run from the project root:   python -m companion.ch04.examples_a
Writes companion/ch04/expected/a_*.txt and diagrams/data/ch04-*.csv.
Values marked "assumed" (A-046 .. A-055) are teaching values, not a design.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch04.common import csv, emit
from plantp import datapack, materials as mt, physics as ph, screening as sc

D_ROTOR, HUB = 150.0, 100.0
AREA = math.pi * (D_ROTOR / 2) ** 2


def mechanics() -> None:
    rho, v, ct = 1.05, 11.0, 0.8                      # site-like density; A-046
    thrust = float(ph.rotor_thrust(rho, AREA, v, ct))
    m_rna = 350e3                                     # rotor-nacelle mass, A-046
    emit("a_thrust", [
        f"rotor area pi (150/2)^2 = {AREA:,.0f} m2; rho {rho} kg/m3, v {v} m/s, C_T {ct} "
        "(A-046)",
        f"  thrust F = 1/2 rho A v^2 C_T = {thrust / 1e3:,.0f} kN",
        f"  overturning moment at the tower base F x {HUB:.0f} m = {thrust * HUB / 1e6:.1f} MN m",
        f"  weight of rotor and nacelle 350 t x 9.81 = {m_rna * ph.G0 / 1e6:.2f} MN (downward)",
        f"  check: the moment of the weight about the base is zero only if the mass sits on "
        "the axis; an offset of 2 m adds "
        f"{m_rna * ph.G0 * 2 / 1e6:.1f} MN m",
    ])
    rpm, eta_dt, ratio = 10.5, 0.94, 110.0            # A-047
    w = rpm * 2 * math.pi / 60
    p_mech = 5.0e6 / eta_dt
    t_rotor = p_mech / w
    emit("a_torque", [
        f"rated 5 MW electrical, drivetrain efficiency {eta_dt} (A-047): mechanical "
        f"{p_mech / 1e6:.2f} MW",
        f"  rotor speed {rpm} rpm = {w:.4f} rad/s; torque T = P / omega = {t_rotor / 1e6:.2f} MN m",
        f"  gearbox 1:{ratio:.0f}: generator {rpm * ratio:.0f} rpm, torque "
        f"{t_rotor / ratio / 1e3:.1f} kN m (losses ignored)",
        f"  blade tip speed omega R = {w * 75:.1f} m/s; tip-speed ratio at 10 m/s: "
        f"{w * 75 / 10:.2f}",
    ])
    v10, cp = 10.0, 0.45
    p_wind = 0.5 * rho * AREA * v10 ** 3
    stages = [("wind through the rotor area", p_wind), ("rotor (C_p 0.45)", p_wind * cp)]
    for name, eta in (("gearbox", 0.97), ("generator", 0.97), ("converter", 0.975),
                      ("turbine transformer", 0.99)):
        stages.append((name, stages[-1][1] * eta))
    lines = [f"energy chain at 10 m/s, rho {rho} kg/m3 (efficiencies assumed, A-047):"]
    for name, p in stages:
        lines.append(f"  after {name:28s} {p / 1e6:6.3f} MW")
    lines.append(f"  overall wind -> grid {stages[-1][1] / p_wind:.3f}; product of the "
                 f"electrical stages {stages[-1][1] / stages[1][1]:.3f}")
    emit("a_chain", lines)
    csv("ch04-chain.csv", "stage,mw", [(i, f"{p / 1e6:.3f}") for i, (_, p) in enumerate(stages)])
    m_blade, length = 20e3, 73.0                       # A-048
    i_uniform = 3 * m_blade * length ** 2 / 3
    i_taper = 3 * m_blade * length ** 2 / 6
    r = np.linspace(0, length, 2001)
    lam0 = 2 * m_blade / length
    i_num = 3 * np.trapezoid(lam0 * (1 - r / length) * r ** 2, r)
    ke = 0.5 * i_taper * w ** 2
    emit("a_inertia", [
        "three blades of 20 t, 73 m (A-048); hub and generator neglected",
        f"  uniform rod about the root: I = 3 m L^2 / 3 = {i_uniform:.3e} kg m2",
        f"  mass tapering linearly to zero at the tip: I = 3 m L^2 / 6 = {i_taper:.3e} kg m2 "
        f"(numerical {i_num:.3e})",
        f"  kinetic energy at {rpm} rpm: 1/2 I omega^2 = {ke / 1e6:.1f} MJ "
        f"= {ke / 3.6e6:.1f} kWh",
        f"  inertia constant H = E / S = {ke / 1e6:.1f} MJ / 5.5 MVA = {ke / 5.5e6:.1f} s",
        "  a converter-connected rotor does not share this energy with the grid by itself",
    ])


def fluids() -> None:
    hourly = datapack.load_hourly()
    curve = datapack.load_power_curve()
    vs, pk = curve["wind_speed_ms"].to_numpy(), curve["power_kw"].to_numpy()
    p, t = hourly["p_hpa"].to_numpy(), hourly["t_air_c"].to_numpy()
    v = hourly["ws_100m_ms"].to_numpy()
    rho2 = ph.air_density(p, t)
    p_hub = p * (1 - 0.0065 * HUB / (t + 273.15)) ** (ph.G0 / (ph.R_DRY * 0.0065))
    rho_hub = ph.air_density(p_hub, t - 0.0065 * HUB)
    rho_hum = ph.air_density(p_hub, t - 0.0065 * HUB, rh=0.4)
    e0 = float(np.sum(sc.wind_power_mw(v, vs, pk, 12))) / 1e3

    def energy_veq(rho):
        veq = v * (rho / 1.225) ** (1 / 3)
        return float(np.sum(sc.wind_power_mw(veq, vs, pk, 12))) / 1e3

    def energy_scaled(rho):
        return float(np.sum(np.asarray(sc.wind_power_mw(v, vs, pk, 12)) * rho / 1.225)) / 1e3
    e_hub = energy_veq(rho_hub)
    e_mean = energy_veq(np.full_like(v, rho_hub.mean()))
    e_hum = energy_veq(rho_hum)
    e_scaled = energy_scaled(rho_hub)
    z = ph.standard_pressure(1200.0)
    lines = [f"standard atmosphere at 1200 m: p = {float(z):.1f} hPa; rho at 15 C would be "
             f"{float(ph.air_density(z, 15 - 0.0065 * 1200)):.3f} kg/m3",
             f"data pack, hourly: rho at 2 m mean {rho2.mean():.3f} (range {rho2.min():.3f} .. "
             f"{rho2.max():.3f}) kg/m3",
             f"  moved to 100 m (lapse 6.5 K/km): mean {rho_hub.mean():.3f}; with 40 % "
             f"humidity {rho_hum.mean():.3f} kg/m3",
             "annual wind energy of the farm (12 turbines, 0.88 losses):",
             f"  power curve at 1.225 kg/m3 (no correction):       {e0:6.1f} GWh",
             f"  equivalent speed v (rho/1.225)^(1/3), hourly rho: {e_hub:6.1f} GWh "
             f"({100 * (e_hub / e0 - 1):+.1f} %)",
             f"  same with the annual mean density:                {e_mean:6.1f} GWh "
             f"({100 * (e_mean / e0 - 1):+.1f} %)",
             f"  with 40 % relative humidity:                      {e_hum:6.1f} GWh "
             f"({100 * (e_hum / e0 - 1):+.1f} %)",
             f"  power scaled by rho/1.225 at every speed (wrong): {e_scaled:6.1f} GWh "
             f"({100 * (e_scaled / e0 - 1):+.1f} %)"]
    emit("a_density", lines)
    mon = np.repeat(np.arange(1, 13), np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31,
                                                30, 31]) * 24)
    csv("ch04-density.csv", "month,rho",
        [(m_, f"{rho_hub[mon == m_].mean():.4f}") for m_ in range(1, 13)])
    q = 0.5 * 1.225 * 30.0 ** 2                        # A-049
    a_mod = 2.278 * 1.134
    f_mod = q * a_mod * 1.2
    emit("a_windload", [
        "dynamic pressure q = 1/2 rho v^2 at a 30 m/s gust (A-049, rho 1.225 kg/m3):",
        f"  q = {q:.0f} Pa; module 2.278 x 1.134 m = {a_mod:.3f} m2; force coefficient 1.2:",
        f"  F = q A C_f = {f_mod / 1e3:.2f} kN against a module weight of "
        f"{28 * ph.G0 / 1e3:.2f} kN",
        "  doubling the gust speed quadruples the load; codes set the design values (ch. 30)",
    ])
    a = np.linspace(0, 0.5, 51)
    csv("ch04-betz.csv", "a,cp,ct", [(f"{x:.2f}", f"{float(ph.betz_cp(x)):.4f}",
                                      f"{float(ph.betz_ct(x)):.4f}") for x in a])
    emit("a_betz", [
        "actuator disc: induction a slows the wind to (1 - a) v at the disc, (1 - 2a) v far "
        "behind",
        "  C_p = 4 a (1 - a)^2, C_T = 4 a (1 - a)",
        f"  dC_p/da = 4 (1 - a)(1 - 3a) = 0 -> a = 1/3: C_p = 16/27 = {16 / 27:.4f}, "
        f"C_T = 8/9 = {8 / 9:.4f}",
        "  wake speed at a = 1/3: v/3; a > 1/2 would need a reversed wake (model fails)",
        f"  the turbine of A-046 (C_p 0.45 at 10 m/s) reaches {0.45 / (16 / 27):.0%} of the "
        "Betz limit",
    ])
    v60, v80, v100 = (hourly[c].to_numpy() for c in ("ws_60m_ms", "ws_80m_ms", "ws_100m_ms"))
    ok = (v60 > 3) & (v100 > 3)
    alpha_h = np.asarray(ph.shear_exponent(v60[ok], 60, v100[ok], 100))
    hour = np.tile(np.arange(24), 365)[ok]
    by_h = [float(np.median(alpha_h[hour == h_])) for h_ in range(24)]
    a_mean = float(ph.shear_exponent(v60.mean(), 60, v100.mean(), 100))
    z0 = 60 * math.exp(-(math.log(100 / 60)) / (v100.mean() / v60.mean() - 1))
    csv("ch04-shear.csv", "hour,alpha", [(h_, f"{x:.4f}") for h_, x in enumerate(by_h)])
    emit("a_shear", [
        f"mean speeds 60 / 80 / 100 m: {v60.mean():.2f} / {v80.mean():.2f} / {v100.mean():.2f} m/s",
        f"  power-law exponent from the means: {a_mean:.3f}",
        f"  hourly exponent (speeds above 3 m/s), median by hour: night max {max(by_h):.3f}, "
        f"day min {min(by_h):.3f}",
        f"  extrapolated mean at the blade tip (175 m): {v100.mean() * 1.75 ** a_mean:.2f} m/s; "
        f"at the lowest tip (25 m): {v100.mean() * 0.25 ** a_mean:.2f} m/s",
        f"  log law through the 60 and 100 m means: roughness length z0 = {z0:.3f} m",
        "  daytime sun mixes the air (small exponent); calm nights let layers slide (large)",
    ])


def heat() -> None:
    day = datapack.load_hourly("day_summer")
    g, t = day["ghi_wm2"].to_numpy(), day["t_air_c"].to_numpy()
    tc = np.asarray(ph.pv_cell_temp_noct(t, g, 45.0))
    loss = -0.35 * (tc - 25.0)
    e_ref = np.sum(g)
    e_loss = float(np.sum(g * loss)) / e_ref
    k = int(np.argmax(g))
    emit("a_pvtemp", [
        "summer subset day, NOCT model T_cell = T_air + (45 - 20) G / 800, gamma -0.35 %/K",
        f"  noon hour {k}: G {g[k]:.0f} W/m2, air {t[k]:.1f} C -> cell {tc[k]:.1f} C, "
        f"power change {loss[k]:+.1f} %",
        f"  irradiance-weighted change over the day: {e_loss:+.1f} %",
        f"  hottest cell temperature of the day {tc.max():.1f} C",
        "  NOCT assumes 1 m/s wind and open-rack mounting; roof-mounted modules run hotter",
    ])
    csv("ch04-pvtemp.csv", "hour,tair,tcell,ghi",
        [(h_, f"{t[h_]:.2f}", f"{tc[h_]:.2f}", f"{g[h_]:.1f}") for h_ in range(24)])
    emit("a_expansion", [
        f"steel torque tube 100 m, alpha 12e-6 /K, -20 .. +70 C: "
        f"{ph.expansion(100, 12e-6, 90) * 1000:.0f} mm",
        f"aluminium busbar 3 m, alpha 23e-6 /K, 80 K: {ph.expansion(3, 23e-6, 80) * 1000:.1f} mm",
        f"copper cable conductor 500 m, alpha 17e-6 /K, 50 K: "
        f"{ph.expansion(500, 17e-6, 50) * 1000:.0f} mm",
        f"fully restrained steel, 50 K: stress E alpha dT = "
        f"{mt.mismatch_stress(210e9, 12e-6, 50) / 1e6:.0f} MPa (a third of S355 yield)",
        "  expansion joints, slotted holes and cable snaking exist for this reason",
    ])
    rho_cu, alpha_cu = 1.72e-8, 0.00393
    area, perim, h, t_amb = 0.080 * 0.010, 2 * (0.080 + 0.010), 10.0, 40.0   # A-051
    r20 = rho_cu / area
    rows, lines = [], [f"copper busbar 80 x 10 mm: R20 = {r20 * 1e6:.2f} micro-ohm/m, surface "
                       f"{perim:.2f} m2 per m, h = {h} W/m2K, ambient {t_amb} C (A-051)"]
    for i_a in (500, 1000, 1500, 2000, 2500, 3000):
        tt, ka = ph.conductor_temperature(i_a, r20, alpha_cu, h, perim, t_amb)
        lines.append(f"  {i_a:5d} A: steady {tt:6.1f} C  (k alpha = {ka:.3f})")
    i_run = math.sqrt(h * perim / (r20 * alpha_cu))
    lines.append(f"  linear model: no steady state above I = sqrt(h A / (R20 alpha)) = {i_run:,.0f} A")
    t_it, it = t_amb, 0
    for it in range(1, 50):
        t_new = t_amb + 2000 ** 2 * r20 * (1 + alpha_cu * (t_it - 20)) / (h * perim)
        if abs(t_new - t_it) < 0.01:
            break
        t_it = t_new
    lines.append(f"  fixed-point iteration at 2000 A: {t_new:.1f} C after {it} steps "
                 "(converges because k alpha < 1)")
    emit("a_conductor", lines)
    for i_a in range(100, 4001, 100):
        tt, _ = ph.conductor_temperature(i_a, r20, alpha_cu, h, perim, t_amb)
        rows.append((i_a, f"{tt:.2f}" if tt < 400 else "nan"))
    csv("ch04-heating.csv", "current,temp", rows)


def electromagnetism() -> None:
    u0 = 33e3 / math.sqrt(3)
    r_in, r_out, eps_r = 0.010, 0.018, 2.3                # A-052
    e_in = float(ph.coax_field(u0, r_in, r_in, r_out))
    e_out = float(ph.coax_field(u0, r_out, r_in, r_out))
    c = 2 * math.pi * 8.854e-12 * eps_r / math.log(r_out / r_in)
    emit("a_coax", [
        f"33 kV cable, U0 = 33/sqrt(3) = {u0 / 1e3:.2f} kV; insulation from r = 10 to 18 mm "
        "(A-052)",
        f"  E at the conductor screen {e_in / 1e6:.2f} kV/mm; at the insulation screen "
        f"{e_out / 1e6:.2f} kV/mm",
        f"  mean field U0 / thickness = {u0 / (r_out - r_in) / 1e6:.2f} kV/mm (the peak is "
        f"{e_in / (u0 / (r_out - r_in)):.2f} x the mean)",
        f"  capacitance 2 pi eps0 eps_r / ln(R/r) = {c * 1e6 * 1000:.3f} microfarad/km; "
        f"charging current {2 * math.pi * 50 * c * u0 * 1000:.2f} A/km",
    ])
    r = np.linspace(r_in, r_out, 41)
    csv("ch04-coax.csv", "r_mm,e", [(f"{x * 1000:.2f}", f"{float(ph.coax_field(u0, x, r_in, r_out)) / 1e6:.4f}")
                                    for x in r])
    i_k, kappa, d = 21.9e3, 1.8, 0.3                     # A-054
    i_p = kappa * math.sqrt(2) * i_k
    f = float(ph.parallel_force_per_m(i_p, i_p, d))
    emit("a_busforce", [
        f"fault at bus 1 of chapter 3: I'' = {i_k / 1e3:.1f} kA; peak factor kappa {kappa} "
        "(A-054)",
        f"  peak current i_p = kappa sqrt(2) I'' = {i_p / 1e3:.1f} kA",
        f"  two parallel bars {d} m apart: F/L = mu0 i_p^2 / (2 pi d) = {f / 1e3:.2f} kN/m",
        f"  with supports every 1.2 m: about {f * 1.2 / 1e3:.1f} kN per support, for a few "
        "milliseconds",
        f"  at normal current (1750 A peak {1750 * math.sqrt(2):.0f} A): "
        f"{float(ph.parallel_force_per_m(1750 * math.sqrt(2), 1750 * math.sqrt(2), d)):.1f} N/m",
    ])
    area_c, b_pk = 0.5, 1.7                               # A-053
    n_hv = 132e3 / math.sqrt(3) / (4.44 * 50 * area_c * b_pk)
    n_lv = 33e3 / (4.44 * 50 * area_c * b_pk)
    emit("a_transformer", [
        f"export transformer 132 kV star / 33 kV delta, core 0.5 m2, B 1.7 T (A-053)",
        f"  volts per turn 4.44 f A B = {4.44 * 50 * area_c * b_pk:.1f} V",
        f"  HV phase winding 76.2 kV: {n_hv:.0f} turns; LV phase winding 33 kV: {n_lv:.0f} turns",
        f"  ratio check {n_hv / n_lv:.3f} = 76.2 / 33 = {132 / math.sqrt(3) / 33:.3f}",
        f"  flux density at 110 % voltage {1.1 * b_pk:.2f} T: near saturation of grain-oriented "
        "steel",
        f"  eddy loss ~ t^2: 0.27 mm sheet instead of 0.35 mm -> {(0.27 / 0.35) ** 2:.2f} x",
    ])


def light_vibration_sound() -> None:
    lines = ["photon energy E = h c / lambda:"]
    for lam in (400, 550, 700, 1107):
        lines.append(f"  {lam:5d} nm: {float(ph.photon_energy_ev(lam)):.2f} eV")
    lines += [f"silicon band gap 1.12 eV -> photons longer than "
              f"{1239.84 / 1.12:.0f} nm pass through unused",
              f"blackbody sun (5778 K): power in photons above 1.12 eV {ph.planck_fraction_above(1.12):.3f}",
              f"  'ultimate' efficiency (each photon gives exactly 1.12 eV): "
              f"{ph.ultimate_efficiency(1.12):.3f}"]
    gaps = np.arange(0.5, 3.01, 0.05)
    u = [ph.ultimate_efficiency(e) for e in gaps]
    lines.append(f"  best gap for this limit: {gaps[int(np.argmax(u))]:.2f} eV "
                 f"({max(u):.3f})")
    emit("a_photon", lines)
    csv("ch04-gap.csv", "eg,u", [(f"{e:.2f}", f"{x:.4f}") for e, x in zip(gaps, u)])
    th = np.array([0, 30, 45, 60, 70, 80, 85])
    rr = ph.fresnel_reflectance(th)
    t0 = 1 - float(ph.fresnel_reflectance(0))
    lines = ["air-glass interface, n = 1.5, unpolarised:"]
    for a_, r_ in zip(th, rr):
        lines.append(f"  {a_:3d} deg: reflectance {r_:.3f}, transmission relative to normal "
                     f"{(1 - r_) / t0:.3f}")
    n_c = math.sqrt(1.5)
    lines.append(f"  quarter-wave anti-reflection layer: n = sqrt(1.5) = {n_c:.3f}, thickness "
                 f"550 / (4 n) = {550 / (4 * n_c):.0f} nm")
    emit("a_fresnel", lines)
    ang = np.arange(0, 90, 2)
    csv("ch04-fresnel.csv", "deg,r", [(a_, f"{float(ph.fresnel_reflectance(a_)):.4f}") for a_ in ang])
    e_st, rho_st = 210e9, 7850.0                           # A-050
    p1, p3 = 10.5 / 60, 3 * 10.5 / 60
    lines = ["tower as a uniform steel tube of 100 m with a 350 t top mass (A-050):",
             f"  rotor at 10.5 rpm: 1P = {p1:.3f} Hz, 3P = {p3:.3f} Hz"]
    f1 = 0.0
    for label, d_, t_ in (("first try", 4.25, 0.030), ("second try", 4.50, 0.045)):
        sec = mt.tube_section(d_, t_)
        m_tower = rho_st * sec.area * HUB
        k_tip = 3 * e_st * sec.second_moment / HUB ** 3
        m_eff = 350e3 + 0.24 * m_tower
        f1 = math.sqrt(k_tip / m_eff) / (2 * math.pi)
        lines += [f"  {label}: D {d_} m, t {t_ * 1000:.0f} mm: I = {sec.second_moment:.3f} m4, "
                  f"tower {m_tower / 1e3:.0f} t, k = 3EI/L^3 = {k_tip / 1e3:.0f} kN/m",
                  f"    m_eff = m_top + 0.24 m_tower = {m_eff / 1e3:.0f} t -> f1 = {f1:.3f} Hz; "
                  f"f1/1P = {f1 / p1:.2f}, 3P/f1 = {p3 / f1:.2f}"]
    sec = mt.tube_section(4.50, 0.045)
    f_bare = ph.cantilever_f1(e_st, sec.second_moment, rho_st * sec.area, HUB)
    lines += [f"  the bare second tube without the top mass: {f_bare:.3f} Hz",
              "  the first try sits 4 % above 1P (resonance risk); the second lies between",
              "    1P and 3P with margin ('soft-stiff')"]
    emit("a_tower", lines)
    rpm = np.linspace(0, 14, 29)
    csv("ch04-campbell.csv", "rpm,p1,p3,f1", [(f"{x:.1f}", f"{x / 60:.4f}", f"{3 * x / 60:.4f}",
                                               f"{f1:.4f}") for x in rpm])
    lines = ["sound power 105 dB(A) per turbine (assumed, as in chapter 3); spherical "
             "spreading only:"]
    for r_ in (150, 300, 500, 1000):
        lines.append(f"  {r_:5d} m: Lp = 105 - 20 log10 r - 11 = {float(ph.spl_at_distance(105, r_)):.1f} dB(A)")
    lines.append("  every doubling of distance: -6 dB; ground, air absorption, screening and")
    lines.append("    the governing assessment method change these numbers (chapter 33)")
    emit("a_sound", lines)


def storage() -> None:
    e_bess = 40e6 * 3600
    head, g = 100.0, ph.G0
    m_w = e_bess / (g * head)
    cell = 3.2 * 280 / 1000                                 # kWh, assumed LFP cell
    w = 10.5 * 2 * math.pi / 60
    ke = 0.5 * (3 * 20e3 * 73 ** 2 / 6) * w ** 2
    c_bank = 2 * 1e6 * 3600 / 800 ** 2
    emit("a_storage", [
        "the 40 MWh battery of scenario S1 expressed in other forms of stored energy:",
        f"  water lifted 100 m: m = E / (g h) = {m_w / 1e3:,.0f} t = {m_w / 1e3:,.0f} m3",
        f"  cells of 3.2 V x 280 Ah = {cell:.3f} kWh (assumed): {40e3 / cell:,.0f} cells",
        f"  turbine rotors at 10.5 rpm hold {ke / 1e6:.1f} MJ each: "
        f"{e_bess / ke:,.0f} rotors",
        f"  a capacitor bank at 800 V storing 1 MWh needs C = 2E/V^2 = {c_bank:,.0f} F",
        "  chemical bonds pack energy densely; motion and fields store little per kg",
    ])


def main() -> None:
    mechanics()
    fluids()
    heat()
    electromagnetism()
    light_vibration_sound()
    storage()


if __name__ == "__main__":
    main()
