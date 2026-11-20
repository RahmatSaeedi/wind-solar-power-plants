"""Chapter 11, section A - aerodynamics and operation: power in the wind at
the site density, the fictional aerofoil and blade, BEM against momentum
theory, Cp-lambda curves, the operating regions and the power curve, the
torque law, yaw misalignment, density, and the energy of a stop.

Run from the project root:   python -m companion.ch11.examples_a
Writes companion/ch11/expected/a_*.txt and diagrams/data/ch11-*.csv.
Teaching values A-211 .. A-214 (fictional); data pack 1.1.0 (S0).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch11 import rotor
from companion.ch11.common import csv, emit
from plantp import datapack, wind as w


def power_in_wind() -> None:
    lines = ["kinetic power through the 150 m rotor (A = "
             f"{rotor.AREA:,.0f} m2):",
             "  v m/s   at 1.225 kg/m3   at 1.056 kg/m3   Betz share at 1.056"]
    for v in (4, 6, 8, 10, 12, 15):
        p0 = 0.5 * 1.225 * rotor.AREA * v ** 3 / 1e6
        p1 = 0.5 * rotor.RHO_SITE * rotor.AREA * v ** 3 / 1e6
        lines.append(f"  {v:5d}   {p0:11.2f} MW   {p1:11.2f} MW   "
                     f"{16 / 27 * p1:11.2f} MW")
    lines += [f"  specific rating 5 MW / {rotor.AREA:,.0f} m2 = "
              f"{5e6 / rotor.AREA:.0f} W/m2 of swept area",
              "  power grows with v^3: doubling the speed gives eight times"]
    emit("a_power", lines)


def aerofoil() -> None:
    a = np.arange(-6.0, 20.01, 0.5)
    cl, cd = w.polar(a)
    k = int(np.argmax(cl / cd))
    lines = ["the fictional aerofoil of plantp.wind (A-212):",
             "  alpha deg    Cl      Cd       L/D"]
    for x in (-2, 0, 4, 6, 8, 10, 12, 14, 16):
        c1, c2 = w.polar(float(x))
        lines.append(f"  {x:9d}  {float(c1):6.3f}  {float(c2):7.4f}  "
                     f"{float(c1) / float(c2):7.1f}")
    lines += [f"  best lift-to-drag {cl[k] / cd[k]:.0f} at {a[k]:.1f} deg; stall"
              " begins near 12 deg",
              "  real blades use measured polars for each thickness and"
              " Reynolds", "  number; roughness and erosion lower L/D"]
    emit("a_aerofoil", lines)
    csv("ch11-polar.csv", "a,cl,cd", [(f"{x:.1f}", f"{y:.4f}", f"{z:.5f}")
                                      for x, y, z in zip(a, cl, cd)])


def blade_design() -> None:
    b = rotor.blade()
    lines = ["blade designed for tip-speed ratio 8 at 6 deg (Schmitz, A-212):",
             "  r m     r/R    chord m   twist deg"]
    for target in (5, 10, 20, 30, 45, 60, 70, 74):
        k = int(np.argmin(abs(b.r - target)))
        lines.append(f"  {b.r[k]:5.1f}   {b.r[k] / b.radius:4.2f}   "
                     f"{b.chord[k]:7.2f}   {b.twist[k]:8.1f}")
    lines += ["  chord is capped at 4.8 m near the root for transport and",
              "  manufacture; the root region carries load, not power"]
    emit("a_blade", lines)
    csv("ch11-blade.csv", "r,chord,twist",
        [(f"{r:.2f}", f"{c:.3f}", f"{t:.2f}")
         for r, c, t in zip(b.r, b.chord, b.twist)])


def bem_vs_momentum() -> None:
    b = rotor.blade()
    lam = rotor.tsr_opt()
    res = w.bem(b, lam)
    mid = (b.r > 0.3 * b.radius) & (b.r < 0.9 * b.radius)
    emit("a_bem", [
        f"BEM at the optimum tip-speed ratio {lam:.2f} (pitch 0):",
        f"  Cp {res.cp:.4f}, Ct {res.ct:.3f}; momentum ideal Cp 16/27 = "
        f"{16 / 27:.4f}, Ct 8/9 = {8 / 9:.3f}",
        f"  axial induction over 30 .. 90 % of R: {res.a[mid].min():.3f} .."
        f" {res.a[mid].max():.3f} (ideal 1/3)",
        f"  angle of attack there: {res.alpha[mid].min():.1f} .."
        f" {res.alpha[mid].max():.1f} deg (design 6)",
        "  the shortfall from Betz: tip and hub losses, drag (finite L/D),",
        "  wake rotation and the capped root chord"])


def cp_lambda() -> None:
    b = rotor.blade()
    lams = np.arange(2.0, 14.01, 0.25)
    rows = []
    tab = {}
    for pitch in (0.0, 2.0, 5.0, 10.0):
        tab[pitch] = [max(w.bem(b, float(x), pitch).cp, 0.0) for x in lams]
    for k, x in enumerate(lams):
        rows.append((f"{x:.2f}",) + tuple(f"{tab[p][k]:.4f}" for p in tab))
    csv("ch11-cplambda.csv", "lam,p0,p2,p5,p10", rows)
    lines = ["power coefficient against tip-speed ratio and pitch:",
             "  pitch deg   Cp max   at lambda"]
    for p in tab:
        k = int(np.argmax(tab[p]))
        lines.append(f"  {p:9.0f}   {tab[p][k]:6.3f}   {lams[k]:8.2f}")
    lines += ["  pitching the blade lowers Cp at every lambda: the lever that",
              "  holds rated power above rated wind (region 3)"]
    emit("a_cplambda", lines)


def regions() -> None:
    v, p, sm, ct = rotor.curve_arrays()
    pc = datapack.load_power_curve()
    pack = np.interp(v, pc.wind_speed_ms, pc.power_kw, right=0.0)
    ops = {o.v: o for o in rotor.curve()}
    lines = ["steady operating points of WT-5.0-150 at 1.225 kg/m3 (A-211):",
             "  v m/s   P kW  rpm    TSR  pitch   Ct   thrust kN   torque kNm"]
    for vv in (3, 5, 7, 9, 10, 10.5, 11, 12, 15, 20, 25):
        o = ops[float(vv)]
        lines.append(f"  {vv:5.1f}  {o.power_w / 1e3:5.0f}  {o.omega * 30 / math.pi:5.2f}"
                     f"  {o.tsr:5.2f}  {o.pitch:5.1f}  {o.ct:5.3f}  {o.thrust_n / 1e3:9.0f}"
                     f"  {o.torque_nm / 1e3:9.0f}")
    lines += ["  region 2: TSR held at the optimum (variable speed); 2.5: rotor",
              "  at 11.5 rpm, TSR falls; 3: pitch holds 5 MW; thrust peaks",
              "  just below rated wind and falls as the blades feather"]
    emit("a_regions", lines)
    csv("ch11-curve.csv", "v,steady,smooth,pack",
        [(f"{a:.1f}", f"{b:.1f}", f"{c:.1f}", f"{d:.1f}")
         for a, b, c, d in zip(v, p, sm, pack) if a <= 26])
    csv("ch11-regions.csv", "v,rpm,pitch,thrust",
        [(f"{o.v:.1f}", f"{o.omega * 30 / math.pi:.3f}", f"{o.pitch:.2f}",
          f"{o.thrust_n / 1e3:.1f}") for o in rotor.curve()])
    lines = ["steady curve against the data-pack curve (measured-style):",
             "  v m/s   steady kW   steady + turbulence 10 %   data pack kW"]
    for vv in (4, 6, 8, 9, 10, 10.5, 11, 11.5, 12, 13):
        k = int(round(vv / 0.5))
        lines.append(f"  {vv:5.1f}   {p[k]:9.0f}   {sm[k]:24.0f}   {pack[k]:12.0f}")
    lines += ["  a ten-minute mean averages the knee of the curve: with 10 %",
              "  turbulence the model is within about 3 % of the pack from",
              "  6 m/s up; near cut-in the two differ (start-up behaviour):",
              "  the power curve is a statistical object, not a single physics"]
    emit("a_curve", lines)


def torque_law() -> None:
    t = rotor.turbine()
    cp = w.bem(t.blade, t.tsr_opt).cp
    k = 0.5 * rotor.RHO0 * rotor.AREA * rotor.RADIUS ** 3 * cp / t.tsr_opt ** 3
    o = w.operate(t, 8.0)
    emit("a_torque", [
        "region-2 control law: generator torque Q = k omega^2 (A-211):",
        f"  k = 0.5 rho A R^3 Cp / lambda^3 = {k / 1e3:,.0f} kN m s2",
        f"  at 8 m/s: omega {o.omega:.3f} rad/s, k omega^2 = "
        f"{k * o.omega ** 2 / 1e6:.3f} MN m;",
        f"  aerodynamic torque from BEM {o.torque_nm / 1e6:.3f} MN m",
        "  equal torques hold the rotor at the optimum TSR without any",
        "  wind measurement: if the wind rises, aero torque exceeds k w^2",
        "  and the rotor speeds up until the two meet again"])


def yaw_loss() -> None:
    lines = ["yaw misalignment: power falls roughly with cos^n (A-213):",
             "  error deg   cos^2 loss %   cos^3 loss %"]
    for e in (2, 5, 8, 10, 15, 20):
        c = math.cos(math.radians(e))
        lines.append(f"  {e:9d}   {100 * (1 - c ** 2):12.2f}   "
                     f"{100 * (1 - c ** 3):12.2f}")
    lines += ["  a vane error of 5 deg costs about 1 %; the nacelle vane",
              "  sits in the rotor wake, so its offset is calibrated (yaw",
              "  offset checks with lidar or by power, chapters 13 and 52)"]
    emit("a_yaw", lines)


def density() -> None:
    v0, p0, s0, _ = rotor.curve_arrays(rotor.RHO0)
    v1, p1, s1, _ = rotor.curve_arrays(rotor.RHO_SITE)
    eq = np.interp(w.density_equivalent_speed(v0, rotor.RHO_SITE), v0, s0)
    lines = [f"power curve at site density {rotor.RHO_SITE} kg/m3 (D-008):",
             "  v m/s   at 1.225   BEM at site   equivalent-speed method"]
    for vv in (6, 8, 9, 10, 11, 12, 13):
        k = int(round(vv / 0.5))
        lines.append(f"  {vv:5.1f}   {s0[k]:8.0f}   {s1[k]:11.0f}   {eq[k]:23.0f}")
    r0 = next(o.v for o in rotor.curve(rotor.RHO0) if o.pitch > 0)
    r1 = next(o.v for o in rotor.curve(rotor.RHO_SITE) if o.pitch > 0)
    lines += [f"  rated wind (first pitched point): {r0:.1f} m/s at 1.225, "
              f"{r1:.1f} at site",
              "  the rotor model and the standard's equivalent-speed method",
              "  agree within about half a per cent; the vendor's curve for",
              "  the site density stays the evidence to obtain (U-013)"]
    emit("a_density", lines)
    csv("ch11-density.csv", "v,p0,p1,eq",
        [(f"{a:.1f}", f"{b:.1f}", f"{c:.1f}", f"{d:.1f}")
         for a, b, c, d in zip(v0, s0, s1, eq) if a <= 20])


def stop_energy() -> None:
    m_blade, r_gyr = 22e3, 22.0                  # A-214 teaching values
    j_rotor = 3 * m_blade * r_gyr ** 2 + 45e3 * 1.5 ** 2
    om = rotor.turbine().omega_max
    e = 0.5 * j_rotor * om ** 2
    t_pitch = 90 / 8.0
    emit("a_stop", [
        "kinetic energy of the rotor at 11.5 rpm (A-214):",
        f"  J = 3 x 22 t x 22^2 + hub 45 t x 1.5^2 = {j_rotor / 1e6:.1f}e6 kg m2",
        f"  E = J omega^2 / 2 = {e / 1e6:.1f} MJ "
        f"({e / 3.6e6:.1f} kWh)",
        f"  pitching 90 deg at 8 deg/s takes {t_pitch:.1f} s: the blades",
        "  brake the rotor aerodynamically; the mechanical brake holds a",
        "  stopped rotor and is not sized to absorb a full-speed stop in",
        "  storm conditions (each design states its own limits)"])


if __name__ == "__main__":
    power_in_wind()
    aerofoil()
    blade_design()
    bem_vs_momentum()
    cp_lambda()
    regions()
    torque_law()
    yaw_loss()
    density()
    stop_energy()
