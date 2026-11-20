"""Chapter 8, section C - design and production assurance: conceptual
electromagnetic sizing, thermal check, balancing, and the evaluation of
factory-test results (heat run by resistance, insulation resistance and
polarisation index, open-circuit and short-circuit tests, loss summation).

Run from the project root:   python -m companion.ch08.examples_c
Writes companion/ch08/expected/c_*.txt and diagrams/data/ch08-*.csv.
Teaching values A-111, A-112, A-115, A-121 (fictional test results).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch08.common import csv, emit
from plantp import machines as m


def sizing() -> None:
    shear = 40e3                                               # A-112
    lines = ["conceptual size from torque, T = 2 sigma V_r, V_r = pi D^2 L / 4 "
             "(A-112):"]
    for name, n, ratio in (("geared 1:110", 1155.0, 1.4),
                           ("geared 1:40", 420.0, 1.0),
                           ("direct drive", 10.5, 0.2)):
        t = m.torque_nm(5.32e6, n)
        vr = m.rotor_volume_m3(t, shear)
        d = (4 * vr / (math.pi * ratio)) ** (1 / 3)
        length = ratio * d
        lines.append(f"  {name:13s} T {t / 1e3:7.0f} kN m: V_r {vr:5.2f} m3; "
                     f"L/D {ratio}: D {d:4.2f} m, L {length:4.2f} m")
    lines += ["  the 0.8 m x 1.1 m of A-111 sits close to the geared result;",
              "  shear stress, cooling and the gap set the real numbers: a",
              "  machine designer's task (C.6)"]
    emit("c_sizing", lines)


def thermal() -> None:
    p_loss_w, r_th = 0.40 * 158.7e3, 0.0007                     # winding share
    t_amb = 40.0
    tau = 45 * 60.0
    rise = p_loss_w * r_th
    lines = [f"stator copper loss {p_loss_w / 1e3:.1f} kW, winding-to-coolant "
             f"resistance {r_th * 1000:.1f} K/kW (A-121):",
             f"  rise {rise:.1f} K over {t_amb:.0f} C coolant -> winding "
             f"{t_amb + rise:.1f} C (average)",
             f"  a hot spot about 10 K above average: {t_amb + rise + 10:.1f} C"]
    for over in (1.0, 1.1, 1.2):
        r = rise * over ** 2
        lines.append(f"  at {100 * over:.0f} % current: rise {r:.1f} K, "
                     f"life x {m.life_factor(t_amb + r + 10, t_amb + rise + 10, 1e5):.2f}")
    lines.append(f"thermal time constant {tau / 60:.0f} min: a short overload "
                 "heats slowly")
    emit("c_thermal", lines)
    t = np.linspace(0, 4 * 3600, 97)
    csv("ch08-heat.csv", "t_min,rise100,rise120",
        [(f"{x / 60:.0f}", f"{rise * (1 - math.exp(-x / tau)):.2f}",
          f"{1.44 * rise * (1 - math.exp(-x / tau)):.2f}") for x in t])


def balance() -> None:
    mass, grade = 3000.0, 2.5                                   # A-115
    u = m.residual_unbalance(mass, grade, 1155)
    emit("c_balance", [
        f"rotor {mass / 1e3:.0f} t at 1155 rpm, balance grade G {grade} mm/s "
        "(A-115):",
        f"  permissible specific unbalance e = G / omega = {u['e_um']:.1f} "
        "micrometres",
        f"  residual unbalance U = m e = {u['u_gmm'] / 1e3:,.1f} kg mm",
        f"  rotating force U omega^2 = {u['force_n'] / 1e3:.2f} kN at the "
        "bearings",
        "  the centre of mass may sit only about 0.02 mm from the axis; the",
        "  grade itself is chosen from the balancing standard's table",
    ])


def heat_run() -> None:
    r_cold, t_cold = 1.842e-3, 18.0                            # A-121
    r_hot = 2.296e-3
    t_hot = m.temperature_from_resistance(r_cold, t_cold, r_hot)
    t_cool = 36.0
    emit("c_heatrun", [
        f"heat run, resistance method (A-121): cold {r_cold * 1e3:.3f} mohm at "
        f"{t_cold:.0f} C,",
        f"  hot {r_hot * 1e3:.3f} mohm at shut-down -> winding "
        f"{t_hot:.1f} C average",
        f"  coolant {t_cool:.0f} C: temperature rise {t_hot - t_cool:.1f} K",
        "  compare with the rise the specification allows for the thermal",
        "  class: the specification, not this book, states the limit",
    ])


def insulation_tests() -> None:
    ir = {1: 820.0, 10: 2050.0}                                # A-121
    pi = ir[10] / ir[1]
    ir40 = ir[1] * 2 ** ((30 - 40) / 10)
    emit("c_ir", [
        "insulation resistance of a stator phase to earth (A-121):",
        f"  1 min {ir[1]:.0f} Mohm, 10 min {ir[10]:.0f} Mohm: polarisation "
        f"index {pi:.2f}",
        "  measured at 30 C; with the common halving-per-10-K practice,",
        f"  at 40 C about {ir40:.0f} Mohm",
        "  a rising reading over 10 minutes means a dry, clean insulation; a",
        "  flat one points to moisture or dirt; acceptance values come from",
        "  the manufacturer's procedure and the specification",
    ])


def oc_sc() -> None:
    v_oc, i_f_oc = 400.0, 32.0                                 # A-121
    i_sc_at_if = 116.0
    s_r, v_r = 200e3, 400.0
    i_r = s_r / (math.sqrt(3) * v_r)
    xs = (v_oc / math.sqrt(3)) / i_sc_at_if
    z_b = v_r ** 2 / s_r
    i_f_sc = i_f_oc * i_r / i_sc_at_if
    emit("c_ocsc", [
        "backup generator, open- and short-circuit tests (A-121):",
        f"  open circuit: rated {v_oc:.0f} V at field current {i_f_oc:.0f} A",
        f"  short circuit at the same field current: {i_sc_at_if:.0f} A",
        f"  X_s = (V/sqrt3) / I_sc = {xs:.2f} ohm = {xs / z_b:.2f} pu "
        f"(Z_base {z_b:.2f} ohm)",
        f"  rated current {i_r:.1f} A needs {i_f_sc:.1f} A of field in "
        "short circuit;",
        f"  short-circuit ratio {i_f_oc / i_f_sc:.2f} = 1 / x_d (unsaturated)",
        "  a test confirms (or not) the design value x_d 2.5 pu of A-113",
    ])


def loss_summation() -> None:
    p_out = 5.13e6                                              # A-121
    parts = {"stator I^2 R at 95 C": 64.1e3, "core (no-load test)": 41.0e3,
             "friction and windage": 15.2e3, "rotor and magnet": 7.5e3,
             "additional load losses": 30.4e3}
    total = sum(parts.values())
    lines = ["summation of segregated losses at rated load (A-121):"]
    for k, v in parts.items():
        lines.append(f"  {k:26s} {v / 1e3:6.1f} kW")
    lines += [f"  total {total / 1e3:.1f} kW; efficiency "
              f"{p_out / (p_out + total):.4f} (design 0.970)",
              "  the method and what counts as 'additional' are set by the",
              "  efficiency-test standard; a converter-fed machine adds "
              "harmonic",
              "  losses that a sine test does not show"]
    emit("c_losses", lines)


if __name__ == "__main__":
    sizing()
    thermal()
    balance()
    heat_run()
    insulation_tests()
    oc_sc()
    loss_summation()
