"""Chapter 4, fourth part — resistivity across materials, line inductance, wind drag on the
tower, vibration isolation, transient and short-circuit heating, bolted-joint load
sharing, fillet welds and resin infusion.

Run from the project root:   python -m companion.ch04.examples_final
Writes companion/ch04/expected/t_*.txt and diagrams/data/ch04-t-*.csv.
Values marked "assumed" (A-075 .. A-079) are teaching values, not a design.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch04.common import csv, emit
from plantp import materials as mt, numerics as nm, physics as ph

RESISTIVITY = [                                          # ohm m, orders of magnitude (A-075)
    ("silver", 1.6e-8), ("copper", 1.72e-8), ("aluminium", 2.82e-8), ("structural steel", 1.7e-7),
    ("stainless steel", 7e-7), ("sea water", 0.2), ("moist soil", 1e2), ("pure silicon", 2.3e3),
    ("dry sand", 1e5), ("porcelain", 1e12), ("glass", 1e12), ("polyethylene", 1e16),
]


def resistivity() -> None:
    lines = ["resistivity, orders of magnitude only (indicative, A-075):"]
    for name, r in RESISTIVITY:
        lines.append(f"  {name:17s} {r:9.1e} ohm m")
    span = math.log10(RESISTIVITY[-1][1] / RESISTIVITY[0][1])
    lines.append(f"  from silver to polyethylene: {span:.0f} orders of magnitude")
    lines.append("  no other common property spans such a range: conductors and insulators")
    lines.append("    are different worlds, and soil sits in between (earthing, chapter 26)")
    emit("t_resistivity", lines)
    csv("ch04-t-resistivity.csv", "k,logr", [(i, f"{math.log10(r):.2f}") for i, (_, r) in
                                             enumerate(RESISTIVITY)])


def inductance() -> None:
    r_c = math.sqrt(240 / math.pi) / 1000
    l_cable = ph.line_inductance_per_m(0.050, r_c)
    l_ohl = ph.line_inductance_per_m(1.0 * 2 ** (1 / 3), 0.009)
    x = lambda l: 2 * math.pi * 50 * l * 1000       # noqa: E731  ohm per km
    emit("t_inductance", [
        "per-phase inductance mu0/(2 pi) ln(GMD / 0.7788 r):",
        f"  cable trefoil, centres 50 mm apart, conductor radius {r_c * 1000:.2f} mm:",
        f"    L = {l_cable * 1e6:.3f} microhenry/m, X = {x(l_cable):.3f} ohm/km "
        "(A-032 assumed 0.110)",
        f"  overhead line, flat 1.0 m spacing (GMD {2 ** (1 / 3):.2f} m), radius 9 mm:",
        f"    L = {l_ohl * 1e6:.3f} microhenry/m, X = {x(l_ohl):.3f} ohm/km",
        f"  the overhead line has {l_ohl / l_cable:.1f} x the reactance (wide spacing);",
        "  cables have the opposite: more capacitance",
    ])


def tower_drag() -> None:
    rho, v_hub, alpha, cd = 1.05, 11.0, 0.171, 0.6        # A-076
    z = np.linspace(0.5, 100.0, 400)
    d = 5.0 - 1.5 * z / 100.0
    v = v_hub * (z / 100.0) ** alpha
    w = 0.5 * rho * v ** 2 * cd * d
    force = nm.trapezoid(w, z[1] - z[0])
    moment = nm.trapezoid(w * z, z[1] - z[0])
    lines = ["tower 100 m tapering from 5.0 to 3.5 m, C_d 0.6, power-law wind 11 m/s at hub",
             f"  (A-076): drag {force / 1e3:.0f} kN, base moment {moment / 1e6:.2f} MN m",
             f"  rotor thrust 898 kN at 100 m gives 89.8 MN m: the tower adds "
             f"{100 * moment / 89.8e6:.0f} %"]
    v50 = 36.6
    w50 = 0.5 * 1.225 * (v50 * (z / 100.0) ** alpha) ** 2 * cd * d
    lines.append(f"  50-year wind {v50} m/s at hub (p_gumbel), dense air: drag "
                 f"{nm.trapezoid(w50, z[1] - z[0]) / 1e3:.0f} kN, moment "
                 f"{nm.trapezoid(w50 * z, z[1] - z[0]) / 1e6:.1f} MN m")
    lines.append("  in a storm the parked rotor's thrust falls and the tower's own drag matters")
    emit("t_tower", lines)
    csv("ch04-t-drag.csv", "z,w", [(f"{a:.1f}", f"{b:.1f}") for a, b in zip(z[::8], w[::8])])


def isolation() -> None:
    lines = ["transformer hum at 100 Hz on resilient pads (damping ratio 0.05):"]
    for fn in (10.0, 25.0, 80.0):
        t = float(ph.transmissibility(100.0, fn, 0.05))
        lines.append(f"  pad natural frequency {fn:4.0f} Hz: transmissibility {t:6.3f} "
                     f"({20 * math.log10(t):+.1f} dB)")
    lines.append("  isolation works only well above the mount's natural frequency; a mount")
    lines.append("    tuned near 100 Hz would amplify the hum it was meant to stop")
    emit("t_isolation", lines)


def transient() -> None:
    a_b, perim, h, ta = 8e-4, 0.18, 10.0, 40.0             # busbar of a_conductor (A-051)
    r20, al = 1.72e-8 / a_b, 0.00393
    c = 8960 * 385 * a_b
    tau = c / (h * perim)

    def rhs(t, y):
        i = 2500.0 if t >= 0 else 1500.0
        return (i ** 2 * r20 * (1 + al * (y - 20)) - h * perim * (y - ta)) / c
    t0, _ = ph.conductor_temperature(1500, r20, al, h, perim, ta)
    t_inf, _ = ph.conductor_temperature(2500, r20, al, h, perim, ta)
    out = []
    for minutes in (10, 30, 60):
        _, y = nm.rk4(rhs, t0, 0.0, minutes * 60.0, 5.0)
        out.append(f"{minutes} min {float(np.asarray(y)[-1]):.1f} C")
    emit("t_transient", [
        f"copper busbar 80 x 10 mm: rho c A = {c:.0f} J/(K m), h A = {h * perim:.1f} W/(K m)",
        f"  thermal time constant C / (h A) = {tau:.0f} s = {tau / 60:.1f} min",
        f"  step from 1500 A ({t0:.1f} C) to 2500 A (steady {t_inf:.1f} C), RK4:",
        "  " + "; ".join(out),
        "  short overloads are carried by the thermal mass; a rating for continuous",
        "    current is not a rating for a 10-minute overload, and the reverse",
    ])


def short_circuit() -> None:
    k_al = ph.adiabatic_k(2.5e6, 2.82e-8, 228.0)
    k_cu = ph.adiabatic_k(3.45e6, 1.72e-8, 234.5)
    t_f = ph.adiabatic_final_temp(21.9e3, 1.0, 240e-6, 90.0, 2.5e6, 2.82e-8, 228.0)
    t_s = ph.adiabatic_final_temp(2.0e3, 1.0, 35e-6, 70.0, 3.45e6, 1.72e-8, 234.5)   # A-077
    t_max = (k_al * 240e-6 / 21.9e3) ** 2 * math.log((250 + 228) / (90 + 228))
    emit("t_fault", [
        "no cooling during a fault: c_v dT = (I/A)^2 rho(T) dt, rho ~ (T + beta)",
        f"  K = sqrt(c_v (20 + beta) / rho20): aluminium {k_al / 1e6:.0f}, copper "
        f"{k_cu / 1e6:.0f} A s^0.5 per mm2",
        f"  240 mm2 Al conductor, 21.9 kA for 1 s from 90 C: ends at {t_f:.0f} C",
        f"  time to reach 250 C (assumed limit) from 90 C: {t_max:.2f} s",
        f"  35 mm2 Cu screen, 2 kA earth fault for 1 s from 70 C (A-077): {t_s:.0f} C",
        "  the protection clearing time is part of the cable's design: a slow relay",
        "    can melt what a fast one leaves cold (chapters 24 and 26)",
    ])


def bolted_joint() -> None:
    e, a_s, grip = 210e9, 817e-6, 0.20                     # M36 of b_stress
    k_b = e * a_s / grip
    k_c = 5 * k_b                                            # A-078
    phi = mt.joint_load_factor(k_b, k_c)
    n, d_bc, dm = 140, 4.7, 20e6                             # A-078
    df = 4 * dm / (n * d_bc)
    s_tight = phi * df / a_s
    s_loose = df / a_s
    d_ratio = (s_loose / s_tight) ** 3
    emit("t_joint", [
        f"tower flange: {n} bolts M36 on a 4.7 m circle; moment swings +-20 MN m (A-078)",
        f"  load change per bolt 4 dM / (n D) = {df / 1e3:.0f} kN",
        f"  bolt stiffness E A / L = {k_b / 1e6:.0f} MN/m; clamped parts 5 x stiffer",
        f"  load factor k_b / (k_b + k_c) = {phi:.3f}: the bolt feels {phi:.1%} of the change",
        f"  bolt stress swing: preloaded {s_tight / 1e6:.1f} MPa; preload lost "
        f"{s_loose / 1e6:.1f} MPa",
        f"  with S-N slope 3, losing the preload multiplies bolt fatigue damage by {d_ratio:.0f}",
        "  preload is not a detail: it is what makes the joint survive (re-tightening",
        "    and checks in chapters 49 and 52)",
    ])


def weld_and_infusion() -> None:
    sig = mt.fillet_weld_stress(50e3, 6e-3, 0.200)
    sig2 = mt.fillet_weld_stress(50e3, 6e-3, 0.400)
    emit("t_weld", [
        "fillet weld: leg 6 mm, throat 0.707 x 6 = 4.24 mm, 200 mm long, 50 kN",
        f"  throat stress F / (a L) = {sig / 1e6:.0f} MPa; with 400 mm of weld {sig2 / 1e6:.0f} MPa",
        "  the code check compares this with the design strength of the weld with",
        "    partial factors; size, length and the toe detail (fatigue) all matter",
    ])
    mu, phi_p, k_p, dp = 0.25, 0.5, 2e-10, 0.9e5             # A-079
    lines = ["resin infusion of a blade shell, Darcy flow t = mu phi L^2 / (2 K dP) (A-079):",
             "  viscosity 0.25 Pa s, porosity 0.5, permeability 2e-10 m2, vacuum 0.9 bar"]
    for length in (0.5, 1.0, 2.0, 3.0):
        t = mt.infusion_time(mu, phi_p, length, k_p, dp)
        lines.append(f"  flow length {length:.1f} m: {t / 60:6.0f} min")
    lines.append("  the resin thickens after about two hours (assumed): one inlet line cannot")
    lines.append("    fill a wide shell; many inlets and flow media cut the flow length")
    emit("t_infusion", lines)


def main() -> None:
    resistivity()
    inductance()
    tower_drag()
    isolation()
    transient()
    short_circuit()
    bolted_joint()
    weld_and_infusion()


if __name__ == "__main__":
    main()
