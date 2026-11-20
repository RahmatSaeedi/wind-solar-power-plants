"""Chapter 4, section B — materials behaviour: stress and strain, beams, fatigue, fracture,
creep and relaxation, corrosion, thermal mismatch, dielectric loss and data sheets.

Run from the project root:   python -m companion.ch04.examples_b
Writes companion/ch04/expected/b_*.txt and diagrams/data/ch04-*.csv.
Values marked "assumed" (A-050, A-056 .. A-058) are teaching values, not a design.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch04.common import csv, emit
from plantp import materials as mt, physics as ph


def tower_stress() -> None:
    sec = mt.tube_section(5.0, 0.040)                  # tower base, A-050
    m_tower, m_top = 7850 * mt.tube_section(4.5, 0.045).area * 100, 350e3
    n_axial = (m_tower + m_top) * ph.G0
    moment = 89.8e6                                    # from a_thrust
    s_ax = n_axial / sec.area
    s_b = moment / sec.modulus
    emit("b_tower", [
        "tower base: steel tube D 5.0 m, t 40 mm (A-050)",
        f"  A = {sec.area:.4f} m2, I = {sec.second_moment:.3f} m4, S = I / (D/2) = "
        f"{sec.modulus:.3f} m3",
        f"  axial force (tower {m_tower / 1e3:.0f} t + top 350 t): {n_axial / 1e6:.2f} MN -> "
        f"sigma_a = {s_ax / 1e6:.1f} MPa",
        f"  bending moment 89.8 MN m (thrust example) -> sigma_b = M / S = {s_b / 1e6:.1f} MPa",
        f"  extreme fibres: {(s_ax + s_b) / 1e6:.1f} MPa compression, "
        f"{(s_b - s_ax) / 1e6:.1f} MPa tension",
        f"  against a yield strength of 355 MPa: utilisation {(s_ax + s_b) / 355e6:.2f} "
        "before safety factors",
        "  thin shells fail first by local buckling and by fatigue at welds (chapter 30)",
    ])


def stress_strain() -> None:
    e, fy, fu, eps_u = 210e9, 355e6, 510e6, 0.15        # synthetic S355-like, A-056
    eps = np.concatenate([np.linspace(0, 0.0017, 30), np.linspace(0.0017, 0.02, 40),
                          np.linspace(0.02, 0.22, 80)])
    sig = np.where(eps * e < fy, eps * e, 0.0)
    pl = eps * e >= fy
    hard = fy + (fu - fy) * (1 - np.exp(-(eps - fy / e) / 0.04))
    sig = np.where(pl, hard, sig)
    neck = eps > eps_u
    sig = np.where(neck, hard - 2.5e9 * (eps - eps_u) ** 2, sig)
    offset = e * (eps - 0.002)
    k = int(np.argmax(offset >= sig))
    rp02 = sig[k]
    csv("ch04-stress-strain.csv", "strain_pct,mpa",
        [(f"{100 * a:.3f}", f"{b / 1e6:.1f}") for a, b in zip(eps, sig) if b > 0 or a == 0])
    as_, proof, kn, d, grip = 817e-6, 830e6, 0.15, 0.036, 0.20      # M36 grade 10.9, A-056
    f0 = 0.7 * proof * as_
    elong = f0 * grip / (e * as_)
    lines = ["synthetic tensile curve of an S355-like steel (A-056):",
             f"  E = 210 GPa; 0.2 % offset yield read from the curve: {rp02 / 1e6:.0f} MPa; "
             f"maximum {sig.max() / 1e6:.0f} MPa at {100 * eps[int(np.argmax(sig))]:.0f} % strain",
             f"M36 bolt, grade 10.9 (assumed proof stress 830 MPa, stress area 817 mm2):",
             f"  preload 70 % of proof: F = {f0 / 1e3:.0f} kN; elongation over a 200 mm grip "
             f"{elong * 1000:.3f} mm",
             f"  torque T = K F d with K = {kn}: {mt.bolt_torque(kn, f0, d) / 1e3:.2f} kN m"]
    for kk in (0.12, 0.18):
        lines.append(f"  same torque with K = {kk}: preload {mt.bolt_torque(kn, f0, d) / (kk * d) / 1e3:.0f} kN "
                     f"({100 * (kn / kk - 1):+.0f} %)")
    lines.append("  friction controls most of the torque: tension-controlled methods exist")
    emit("b_stress", lines)


def beam() -> None:
    sec = mt.tube_section(0.140, 0.004)               # torque tube, A-057
    q, width, span, e = 551.0, 2.278, 7.0, 210e9
    w = q * width * 1.2
    m_max = w * span ** 2 / 8
    delta = 5 * w * span ** 4 / (384 * e * sec.second_moment)
    emit("b_beam", [
        "tracker torque tube D 140 mm, t 4 mm, simply supported over 7 m (A-057)",
        f"  I = {sec.second_moment * 1e8:.1f} x 10^-8 m4, S = {sec.modulus * 1e6:.1f} x 10^-6 m3",
        f"  wind load of a_windload spread along the tube: w = q b C_f = {w:.0f} N/m",
        f"  M_max = w L^2 / 8 = {m_max / 1e3:.2f} kN m -> sigma = {m_max / sec.modulus / 1e6:.0f} MPa",
        f"  deflection 5 w L^4 / (384 E I) = {delta * 1000:.0f} mm = span / {span / delta:.0f}",
        "  overloaded: a bigger tube, shorter spans or stowing the tracker flat in",
        "    high wind are the design options (chapter 30)",
    ])


def fatigue() -> None:
    s_ref, n_ref, m = 71.0, 2e6, 3.0                   # detail category style, A-058
    ranges = np.array([10, 20, 30, 40, 50, 60, 70, 80], dtype=float)
    counts = np.array([2.0e8, 3.0e7, 6.0e6, 1.5e6, 4.0e5, 1.0e5, 2.0e4, 4.0e3])
    d = mt.miner_damage(ranges, counts, s_ref, n_ref, m)
    lines = ["welded detail: 71 MPa at 2 million cycles, slope m = 3 (A-058)",
             "  stress range histogram for 20 years (synthetic):",
             "  range (MPa)  cycles        N allowed     n/N"]
    for s_, n_ in zip(ranges, counts):
        nn = float(mt.basquin_cycles(s_, s_ref, n_ref, m))
        lines.append(f"  {s_:8.0f} {n_:14.3g} {nn:14.3g} {n_ / nn:8.3f}")
    lines += [f"  Miner sum D = {d:.2f} (failure expected near D = 1)",
              f"  all ranges 10 % higher: D x 1.1^3 = {d * 1.1 ** 3:.2f}",
              f"  with slope m = 5 instead of 3: D = {mt.miner_damage(ranges, counts, s_ref, n_ref, 5):.2f}",
              "  most damage comes from the many small and medium cycles, not the largest"]
    emit("b_fatigue", lines)
    s = np.logspace(1, np.log10(300), 40)
    csv("ch04-sn.csv", "n,s", [(f"{float(mt.basquin_cycles(x, s_ref, n_ref, m)):.4g}", f"{x:.2f}") for x in s])
    csv("ch04-sn-load.csv", "n,s", [(f"{n_:.4g}", f"{s_:.0f}") for s_, n_ in zip(ranges, counts)])


def fracture_relaxation() -> None:
    lines = ["edge crack in a plate, K = 1.12 sigma sqrt(pi a):"]
    for kic in (100e6, 50e6, 30e6):
        a = mt.critical_crack(kic, 200e6)
        lines.append(f"  K_IC {kic / 1e6:3.0f} MPa sqrt(m), sigma 200 MPa: critical crack "
                     f"{a * 1000:6.1f} mm")
    lines.append("  toughness falls in the cold for many steels: the same crack can be safe in")
    lines.append("    summer and critical in winter (impact-tested grades, chapter 30)")
    emit("b_fracture", lines)
    tau40 = 20.0                                      # years at 40 C (assumed, A-058)
    ea = 70e3
    lines = ["relaxation of a bolted aluminium lug, F(t) = F0 exp(-t / tau) (A-058):"]
    for t_c in (40, 60, 90):
        tau = tau40 / mt.arrhenius_factor(ea, 40, t_c)
        lines.append(f"  {t_c:3d} C: tau = {tau:6.2f} years; preload after 5 years "
                     f"{100 * math.exp(-5 / tau):5.1f} %")
    lines.append("  a joint that runs hot loses its clamping force fastest: heat feeds back")
    emit("b_relax", lines)


def corrosion() -> None:
    zn = mt.faraday_loss_um_per_yr(0.1, 65.38, 2, 7.14)
    fe = mt.faraday_loss_um_per_yr(0.1, 55.85, 2, 7.87)
    al = mt.faraday_loss_um_per_yr(0.1, 26.98, 3, 2.70)
    lines = ["Faraday's law: thickness loss = i M t / (n F rho)",
             f"  0.1 A/m2 (10 microamp/cm2): zinc {zn:.1f}, steel {fe:.1f}, aluminium {al:.1f} "
             "micrometre/yr",
             "hot-dip galvanised coating 85 micrometre (A-058); zinc loss rates assumed:"]
    for env, rate in (("dry inland", 0.7), ("industrial", 2.0), ("coastal", 4.0)):
        lines.append(f"  {env:12s} {rate:3.1f} um/yr -> about {85 / rate:5.0f} years to the steel")
    lines.append("  the real rates come from measured corrosivity of the site (chapter 29)")
    lines.append("galvanic couple: the cathodic current is collected by the anode area,")
    lines.append("  so the anode current density scales with the cathode/anode area ratio:")
    lines.append("  ratio 0.1 -> x 0.1; ratio 1 -> x 1; ratio 10 -> x 10 (small anode, large")
    lines.append("  cathode is the dangerous case: a steel bolt in a copper plate)")
    emit("b_corrosion", lines)


def thermal_electrical() -> None:
    d_alpha = 17e-6 - 2.6e-6
    strain = d_alpha * 100
    lines = ["copper ribbon soldered to a silicon cell, cycling -40 .. +60 C (100 K):",
             f"  mismatch strain (17 - 2.6) e-6 x 100 = {strain * 1000:.2f} x 10^-3",
             f"  fully restrained copper: E d_alpha dT = {mt.mismatch_stress(110e9, d_alpha, 100) / 1e6:.0f}"
             " MPa, above the yield of annealed copper",
             "  each cycle bends the joint plastically: thermal-cycling tests target this"]
    emit("b_mismatch", lines)
    u0 = 33e3 / math.sqrt(3)
    c = 2 * math.pi * 8.854e-12 * 2.3 / math.log(1.8)
    p33 = mt.dielectric_loss_w_per_m(u0, 50, c, 4e-4) * 1000
    u132 = 132e3 / math.sqrt(3)
    p132 = mt.dielectric_loss_w_per_m(u132, 50, c, 4e-4) * 1000
    emit("b_dielectric", [
        "dielectric loss per phase W = omega C U0^2 tan(delta), tan(delta) = 4e-4 (A-052):",
        f"  33 kV cable of a_coax: {p33:.1f} W/km per phase, {3 * p33:.0f} W/km for three",
        f"  same geometry at 132 kV: {p132:.0f} W/km per phase (U0^2: 16 x)",
        "  conductor loss of the feeder at peak was 614 kW over 5 km = 123 kW/km",
        "  dielectric loss matters at high voltage and when tan(delta) grows with ageing",
    ])
    emit("b_datasheet", [
        "unit traps on material data sheets:",
        f"  dielectric strength 500 V/mil = {500 / 25.4e-6 / 1e6:.1f} kV/mm",
        f"  tensile strength 3600 psi = {3600 * 6894.757 / 1e6:.1f} MPa",
        f"  thermal conductivity 0.2 BTU/(h ft F) = {0.2 * 1.730735:.3f} W/(m K)",
        f"  volume resistivity 1e16 ohm cm = {1e16 / 100:.0e} ohm m",
        "  'typical' is not 'minimum'; values hold at the stated temperature and test method",
    ])


def main() -> None:
    tower_stress()
    stress_strain()
    beam()
    fatigue()
    fracture_relaxation()
    corrosion()
    thermal_electrical()


if __name__ == "__main__":
    main()
