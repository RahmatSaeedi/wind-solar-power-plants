"""Chapter 4, second part — centrifugal and gravity loads on blades, magnetic circuits,
battery arithmetic, cooling air, combined stress in bolts, buckling, composites, hardness,
insulation ageing, semiconductors, concrete heat, embodied energy, measurement capability,
acceptance sampling and tolerance stacks.

Run from the project root:   python -m companion.ch04.examples_more
Writes companion/ch04/expected/r_*.txt and diagrams/data/ch04-r-*.csv.
Values marked "assumed" (A-063 .. A-068) are teaching values, not a design.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch04.common import csv, emit
from plantp import datapack, materials as mt, physics as ph, screening as sc

W_ROTOR = 10.5 * 2 * math.pi / 60


def blade_loads() -> None:
    m, length = 20e3, 73.0
    r_cg = length / 3                                   # linear taper: centroid at L/3
    f_c = m * W_ROTOR ** 2 * r_cg
    m_g = m * ph.G0 * r_cg
    cycles = 10.5 * 60 * 24 * 365 * 20
    emit("r_blade", [
        "one blade of 20 t, 73 m, mass tapering to zero at the tip (A-048), 10.5 rpm",
        f"  centre of mass at L/3 = {r_cg:.1f} m from the root",
        f"  centrifugal pull m omega^2 r = {f_c / 1e3:.0f} kN (blade weight {m * ph.G0 / 1e3:.0f} kN)",
        f"  gravity moment at the root m g r = {m_g / 1e6:.2f} MN m, reversing every turn",
        f"  turns in 20 years of operation at rated speed: {cycles:.2e}",
        "  every turn is one full gravity cycle: blade roots are designed for fatigue",
    ])


def magnetic_circuit() -> None:
    b, n, l_fe, mu_r = 1.7, 175, 6.0, 30000.0           # A-063
    i_rated = 100e6 / (3 * 33e3)
    lines = ["export transformer core of a_transformer: B 1.7 T, LV winding 175 turns",
             "  iron path 6 m, relative permeability 30 000 (assumed, A-063)"]
    for gap in (0.0, 0.2e-3, 1.0e-3):
        i_m = ph.magnetising_current(b, l_fe, mu_r, gap, n)
        lines.append(f"  joint gap {gap * 1000:.1f} mm: magnetising current peak {i_m:4.1f} A "
                     f"= {100 * i_m / math.sqrt(2) / i_rated:.2f} % of rated {i_rated:.0f} A")
    lines.append("  a fraction of a millimetre of air needs as much magnetising as metres of")
    lines.append("    iron: core joints are stacked and interleaved to keep gaps tiny")
    emit("r_magnetic", lines)


def battery() -> None:
    cap = 96485.0 / (3.6 * 157.76)                       # mAh per g, LiFePO4
    r_int, i_c = 0.25e-3, 140.0                          # ohm per cell, A at 0.5C (A-064)
    heat = i_c ** 2 * r_int
    cells = 40e3 / (3.2 * 280 / 1000)
    emit("r_battery", [
        "theoretical specific capacity of LiFePO4 (one electron per formula unit):",
        f"  F / (3.6 M) = 96485 / (3.6 x 157.76) = {cap:.1f} mAh/g",
        f"  a 280 Ah cell needs at least {280 / cap:.2f} kg of cathode material (theory only)",
        "cell internal resistance 0.25 milliohm, current 140 A (0.5 C) (A-064):",
        f"  heat I^2 R = {heat:.1f} W per cell; for {cells:,.0f} cells "
        f"{heat * cells / 1e3:.0f} kW to remove",
        f"  ohmic loss one way {100 * heat / (3.2 * i_c):.2f} % of the cell power; round trip"
        f" about {200 * heat / (3.2 * i_c):.1f} %",
        "  doubling the current quadruples the heat: fast cycling needs more cooling",
    ])


def cooling() -> None:
    p_inv, eta = 4.2e6, 0.985                            # inverter of chapter 3 (A-064)
    loss = p_inv * (1 - eta) / eta
    lines = [f"inverter 4.2 MW at 98.5 % efficiency: losses {loss / 1e3:.0f} kW at full power",
             "  air warms 15 K; 300 Pa at sea level; fan efficiency 0.6 (A-064)"]
    for rho, label in ((1.20, "sea level"), (1.05, "Plant P, 1200 m")):
        q = ph.air_flow_for_heat(loss, 15.0, rho)
        dp = 300.0 * rho / 1.20 * (q / ph.air_flow_for_heat(loss, 15.0, 1.20)) ** 2
        p_fan = q * dp / 0.6
        lines.append(f"  {label:16s} rho {rho:.2f}: air {q:.2f} m3/s, fan {p_fan / 1e3:.2f} kW")
    lines.append(f"  thin air: the same heat needs {1.20 / 1.05:.3f} x the volume and "
                 f"{(1.20 / 1.05) ** 2:.2f} x the fan power")
    lines.append("  manufacturers derate equipment above a stated altitude for this reason")
    emit("r_cooling", lines)


def bolt_combined() -> None:
    f0, p_pitch, d2, d3, mu = 475e3, 4.0e-3, 33.402e-3, 31.093e-3, 0.12   # M36 (A-056)
    a_s = 817e-6
    t_thread = f0 * (0.16 * p_pitch + 0.58 * mu * d2)
    d_s = (d2 + d3) / 2
    tau = 16 * t_thread / (math.pi * d_s ** 3)
    sig = f0 / a_s
    vm = mt.von_mises(sig, tau)
    emit("r_bolt", [
        "M36 grade 10.9 bolt at 475 kN preload (b_stress), thread friction 0.12:",
        f"  tensile stress F / A_s = {sig / 1e6:.0f} MPa",
        f"  thread torque F (0.16 P + 0.58 mu d2) = {t_thread:.0f} N m (common approximation)",
        f"  torsional stress 16 T / (pi d_s^3) = {tau / 1e6:.0f} MPa during tightening",
        f"  von Mises sqrt(s^2 + 3 t^2) = {vm / 1e6:.0f} MPa = {vm / 830e6:.0%} of the proof stress",
        "  the twist adds about a fifth to the stress while tightening: preload targets",
        "    leave room for it, and part of the twist relaxes afterwards",
    ])


def buckling() -> None:
    e = 210e9
    post = mt.tube_section(0.150, 0.005)
    p_post = mt.euler_buckling(e, post.second_moment, 2.0, 2.0)
    i_l, a_l = 4.6e-8, 480e-6                           # angle 50 x 50 x 5 (approximate)
    rows, lines = [], ["Euler load pi^2 E I / (K L)^2 (ideal elastic column):",
                       f"  tracker post, tube 150 x 5 mm, 2 m free cantilever (K = 2): "
                       f"{p_post / 1e3:,.0f} kN"]
    for length in (1.0, 2.0, 3.0):
        p_b = mt.euler_buckling(e, i_l, length, 1.0)
        lines.append(f"  angle brace 50 x 50 x 5, pinned, {length:.0f} m: {p_b / 1e3:6.1f} kN "
                     f"(yield load {a_l * 355e6 / 1e3:.0f} kN)")
    lines.append("  short stocky parts yield first; long slender ones buckle long before")
    lines.append("  real columns have imperfections: design curves sit below Euler (chapter 30)")
    emit("r_buckling", lines)
    for length in np.linspace(0.5, 4.0, 36):
        rows.append((f"{length:.2f}", f"{min(mt.euler_buckling(e, i_l, length, 1.0) / 1e3, 400):.2f}",
                     f"{a_l * 355e6 / 1e3:.2f}"))
    csv("ch04-r-buckling.csv", "l,euler,yield", rows)


def composites() -> None:
    lines = ["unidirectional laminate, rule of mixtures (fibre and resin values assumed):"]
    rows = []
    for name, e_f, rho_f in (("glass", 72e9, 2550.0), ("carbon", 230e9, 1800.0)):
        el, et = mt.rule_of_mixtures(e_f, 3.2e9, 0.55)
        rho = 0.55 * rho_f + 0.45 * 1150.0
        lines.append(f"  {name:6s} V_f 0.55: E along {el / 1e9:5.1f} GPa, across {et / 1e9:4.1f} GPa, "
                     f"density {rho:.0f} kg/m3")
    for vf in np.linspace(0, 0.7, 36):
        el, et = mt.rule_of_mixtures(72e9, 3.2e9, vf)
        rows.append((f"{vf:.3f}", f"{el / 1e9:.3f}", f"{et / 1e9:.3f}"))
    lines += ["  stiff along the fibres, weak across: plies run in several directions",
              "  where loads demand it; voids and wrinkles cut the resin-dominated values"]
    emit("r_composite", lines)
    csv("ch04-r-mixtures.csv", "vf,el,et", rows)


def hardness_ageing() -> None:
    lines = ["hardness as a screening check (steels; UTS ~ 3.45 HB MPa, approximate):"]
    for hb in (150, 180, 300):
        lines.append(f"  HB {hb}: tensile strength roughly {3.45 * hb:.0f} MPa")
    lines.append("  a quick check on a flange or bolt; the certificate's tensile test decides")
    emit("r_hardness", lines)
    hourly = datapack.load_hourly()
    curve = datapack.load_power_curve()
    vs, pk = curve["wind_speed_ms"].to_numpy(), curve["power_kw"].to_numpy()
    pv = np.asarray(sc.pv_ac_power_mw(hourly["ghi_wm2"], 60, 50))
    wind = np.asarray(sc.wind_power_mw(hourly["ws_100m_ms"].to_numpy(), vs, pk, 12))
    i = np.minimum(pv + wind, 100.0) * 1e6 / (math.sqrt(3) * 33e3 * 0.95)
    t_room = hourly["t_air_c"].to_numpy() + 15.0
    ea, ref = 100e3, 90.0                                # A-065
    lines = [f"insulation ageing, Arrhenius with Ea = 100 kJ/mol, reference 90 C (A-065):",
             f"  near 90 C the rate doubles every {mt.halving_interval_k(ea, 90):.1f} K"]
    for name, r20, perim in (("Cu 80 x 10", 1.72e-8 / 8e-4, 0.18),
                             ("Cu 2 x (80 x 10)", 1.72e-8 / 16e-4, 0.36)):
        temps = np.array([ph.conductor_temperature(a, r20, 0.00393, 10, perim, b)[0]
                          for a, b in zip(i, t_room)])
        used = mt.life_consumed(temps, np.ones(temps.size), ref, ea)
        hot = np.sort(temps)[::-1]
        top = mt.life_consumed(hot[:100], np.ones(100), ref, ea)
        lines.append(f"  {name:17s}: {used:7.0f} equivalent hours at 90 C per year "
                     f"(hottest 100 h: {100 * top / used:.0f} % of it)")
    lines.append("  a few hot hours use most of the life: ageing follows the peaks, not the mean")
    emit("r_ageing", lines)


def materials_c() -> None:
    lines = ["intrinsic carriers grow as T^1.5 exp(-Eg / 2kT); ratio 150 C / 25 C:"]
    for name, eg in (("silicon", 1.12), ("silicon carbide", 3.26)):
        lines.append(f"  {name:16s} Eg {eg} eV: x {ph.intrinsic_ratio(eg, 25, 150):.3g}")
    k_ev = ph.K_BOLTZ / ph.Q_E
    rel = (423.15 / 298.15) ** 1.5 * math.exp(-3.26 / (2 * k_ev * 423.15) + 1.12 / (2 * k_ev * 298.15))
    lines += [f"  SiC at 150 C has {rel:.1e} x the intrinsic carriers of Si at 25 C",
              "  a wide gap keeps the material insulating when hot: higher blocking voltage",
              "    and junction temperature for wide-gap power devices (chapters 9 and 44)"]
    emit("r_semiconductor", lines)
    rise = mt.adiabatic_rise(380, 330)                  # A-066
    emit("r_concrete", [
        "turbine foundation concrete: 380 kg/m3 cement, 330 kJ/kg heat of hydration (A-066)",
        f"  fully insulated core would rise {rise:.0f} K; placed at 25 C -> about {25 + rise:.0f} C",
        "  the surface cools to the air: a large core-surface difference cracks it",
        "  mitigations: lower-heat binders, cooling pipes, night placement,",
        "  insulation, and a measured temperature-difference limit in the specification",
    ])
    e_steel, e_comp, e_cu, e_conc = 25.0, 100.0, 60.0, 1.5   # MJ/kg, indicative (A-067)
    tower, rna = 494e3, 350e3
    found = 600 * 2400.0
    gj = (tower * e_steel + 255e3 * e_steel + 60e3 * e_comp + 35e3 * e_cu
          + found * e_conc + 60e3 * e_steel) / 1e3
    annual_gj = 16.68e6 * 3.6 / 1e3
    emit("r_embodied", [
        "embodied energy of one turbine with INDICATIVE intensities (A-067):",
        "  steel 25, composite 100, copper 60, concrete 1.5 MJ/kg; tower 494 t,",
        "  rotor-nacelle 350 t (255 t steel, 60 t blade composite, 35 t copper),",
        "  foundation 600 m3 concrete and 60 t of reinforcement",
        f"  total about {gj:,.0f} GJ; yearly electricity {annual_gj:,.0f} GJ (int_wind)",
        f"  simple energy payback {12 * gj / annual_gj:.1f} months; no conversion factors,",
        "  transport, installation or end of life: a screening number only",
    ])


def inspection() -> None:
    tol = 0.021
    lines = [f"hole tolerance {tol} mm; test uncertainty ratio TUR = tolerance / (2 U):"]
    for name, u in (("caliper", 0.030), ("micrometer", 0.004), ("coordinate machine", 0.002)):
        tur = tol / (2 * u)
        acc = tol - 2 * u
        lines.append(f"  {name:19s} U = {u:.3f} mm: TUR {tur:4.2f}; guarded acceptance zone "
                     f"{max(acc, 0):.3f} mm")
    lines.append("  a ratio of 4 or more is a common aim; below 1 the instrument cannot decide")
    emit("r_tur", lines)
    plans = [(20, 0), (50, 1), (125, 3)]
    lines = ["single sampling plans: accept the lot if the sample has at most c defectives",
             "  plan        p = 0.5 %   1 %     2 %     5 %"]
    for n, c in plans:
        pa = mt.accept_probability(n, c, [0.005, 0.01, 0.02, 0.05])
        lines.append(f"  n {n:3d}, c {c}  " + "  ".join(f"{x:6.3f}" for x in pa))
    lines.append("  bigger samples separate good and bad lots more sharply (steeper curve)")
    emit("r_sampling", lines)
    p = np.linspace(0, 0.10, 51)
    csv("ch04-r-oc.csv", "p,a,b,c", [(f"{100 * x:.2f}", *(f"{float(mt.accept_probability(n, c, x)):.4f}"
                                                         for n, c in plans)) for x in p])
    tols = [20.0, 3.0, 2.0, 1.5]                        # mm, uniform each (A-068)
    rng = np.random.default_rng(20260303)
    samples = sum(rng.uniform(-t, t, 200_000) for t in tols)
    emit("r_stack", [
        "PV mounting chain (A-068): pile +-20, bracket +-3, rail hole +-2, clamp +-1.5 mm",
        f"  worst case {mt.stack(tols):.1f} mm; root-sum-square {mt.stack(tols, 'rss'):.1f} mm",
        f"  Monte Carlo (uniform parts): 99.73 % of assemblies within "
        f"+-{np.quantile(np.abs(samples), 0.9973):.1f} mm",
        "  the pile dominates: slotted brackets absorb it; tighter parts elsewhere",
        "  buy almost nothing (a tolerance budget spends on the largest term first)",
    ])


def main() -> None:
    blade_loads()
    magnetic_circuit()
    battery()
    cooling()
    bolt_combined()
    buckling()
    composites()
    hardness_ageing()
    materials_c()
    inspection()


if __name__ == "__main__":
    main()
