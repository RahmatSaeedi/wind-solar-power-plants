"""Chapter 8 - numerical answers of the end-of-chapter problems.

Run from the project root:   python -m companion.ch08.solutions
Writes companion/ch08/expected/solutions.txt; each line starts with the
problem id (P01 ...). Teaching values only (A-111 .. A-122).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch08.common import emit
from companion.ch08.examples_a import MOTOR
from companion.ch08.lab_d import generator_year
from plantp import machines as m
from plantp.phasors import polar, to_polar

OUT: list[str] = []
MU0 = 4e-7 * math.pi
S3 = math.sqrt(3)


def p(pid: str, text: str) -> None:
    OUT.append(f"{pid}: {text}")


def af(rate, years):
    return (1 - (1 + rate) ** -years) / rate


def dip(z_lr, z_src, k=1.0):
    v = abs(230 * (z_lr / k) / (z_lr / k + z_src))
    return 100 - 100 * v / 230


def level_1() -> None:
    p("P01", "; ".join(f"{q} poles {m.sync_speed_rpm(50, q):.0f}/"
                       f"{m.sync_speed_rpm(60, q):.0f} rpm" for q in (4, 6, 8)))
    p("P02", f"s = {m.slip(1500, 1470):.3f}; rotor frequency "
             f"{m.slip(1500, 1470) * 50:.1f} Hz")
    p("P03", f"{m.electrical_freq_hz(900, 6):.1f} Hz")
    p("P04", f"3 MW: {m.torque_nm(3e6, 1500) / 1e3:.1f} kN m at 1500 rpm, "
             f"{m.torque_nm(3e6, 15) / 1e6:.2f} MN m at 15 rpm")
    p("P05", f"e = 1.0 x 0.5 x 30 = {1.0 * 0.5 * 30:.0f} V")
    p("P06", f"F = 1.2 x 200 x 2 = {1.2 * 200 * 2:.0f} N")
    p("P07", f"E = {m.emf_rms(50, 50, 0.02, 0.95):.1f} V")
    r_air = 0.001 / (MU0 * 0.01)
    r_fe = 1.0 / (MU0 * 5000 * 0.01)
    p("P08", f"air {r_air:,.0f}, iron {r_fe:,.0f} A/Wb: ratio {r_air / r_fe:.1f}")
    p("P09", f"rotor copper {0.02 * 31:.2f} kW; mechanical {0.98 * 31:.2f} kW")
    p("P10", f"efficiency {100 / 103:.3f}")
    p("P11", f"3 MVA: {3e6 / (S3 * 690):.0f} A at 690 V, {3e6 / (S3 * 3300):.1f} A "
             "at 3.3 kV")
    p("P12", "P_max = E V / X_s = 1.0 pu")
    p("P13", f"2 sin(15 deg) = {2 * math.sin(math.radians(15)):.3f} pu")
    p("P14", f"V_r = {m.rotor_volume_m3(80e3, 40e3):.2f} m3")
    u = m.residual_unbalance(1.0, 6.3, 3000)
    p("P15", f"e = 6.3 / omega = {u['e_um']:.2f} micrometres")
    p("P16", f"{m.r_at_temperature(2.0, 20, 75):.3f} mohm")
    p("P17", f"PI = 500 / 450 = {500 / 450:.2f}")
    p("P18", f"BPFO = 10/2 x 25 x (1 - 0.2) = {5 * 25 * 0.8:.0f} Hz")
    p("P19", f"air {50e3 / (1.2 * 1005 * 15):.2f} m3/s")
    p("P20", f"life x {m.life_factor(140, 130, 1e5):.2f}")
    p("P21", f"(0.50/0.35)^2 = {(0.5 / 0.35) ** 2:.2f}")
    p("P22", f"k_p1 = sin(5/6 x 90 deg) = {math.sin(5 / 6 * math.pi / 2):.3f}")
    p("P23", f"Br = 1.2 x (1 - 0.0012 x 80) = {1.2 * (1 - 0.0012 * 80):.3f} T")
    p("P24", "about 25 % of rating")


def level_2() -> None:
    im = m.InductionMachine(**MOTOR)
    op = im.operate(0.03)
    p("P25", f"s 3 %: torque {op['torque']:.0f} N m, current {abs(op['i1']):.1f} A, "
             f"pf {op['pf']:.3f}, shaft {op['p_shaft'] / 1e3:.1f} kW")
    st = im.operate(1.0)
    p("P26", f"90 % voltage: start current {0.9 * abs(st['i1']):.0f} A (x0.9), "
             f"torque {0.81 * st['torque']:.0f} N m (x0.81)")
    for pid, pf, sgn in (("P27", 0.8, -1), ("P28", 1.0, 0)):
        i = polar(1.0, sgn * math.degrees(math.acos(pf)))
        e = m.sm_emf(complex(1, 0), i, 1.2)
        mag, ang = to_polar(e)
        p(pid, f"pf {pf}: E {mag:.3f} pu, delta {ang:.1f} deg")
    d = math.asin(0.5 * 1.2 / 0.8)
    p("P29", f"delta {math.degrees(d):.1f} deg, Q "
             f"{m.sm_reactive(0.8, 1.0, 1.2, d):+.3f} pu (absorbed)")
    s = m.slip(1500, 1200)
    p("P30", f"s {s:.2f}; rotor power {m.dfig_rotor_power(2.73e6, s) / 1e6:+.2f} MW "
             "(from the grid)")
    for n in (12, 1500):
        t = m.torque_nm(3e6, n)
        p("P31", f"3 MW at {n} rpm: T {t / 1e3:,.1f} kN m, V_r "
                 f"{m.rotor_volume_m3(t, 40e3):.2f} m3")
    p("P32", f"eta(25 %) = {m.efficiency(0.25, 1.0, 0.96, 0.3):.3f}")
    p("P33", f"x = sqrt(100/200) = {math.sqrt(0.5):.3f} pu")
    kd1 = math.sin(math.radians(30)) / (2 * math.sin(math.radians(15)))
    kd5 = math.sin(math.radians(150)) / (2 * math.sin(math.radians(75)))
    p("P34", f"k_d1 {kd1:.3f}, k_d5 {abs(kd5):.3f}")
    p("P35", f"40 K final; after 30 min {40 * (1 - math.exp(-30 / 45)):.1f} K")
    p("P36", f"{m.temperature_from_resistance(3.0, 20, 3.69):.1f} C")
    xs = (400 / S3) / 150
    p("P37", f"X_s {xs:.3f} ohm = {xs / 0.8:.2f} pu; SCR {0.8 / xs:.2f}")
    p("P38", f"L10 {20 ** 3 * 1e6 / (1500 * 60):,.0f} h")
    u = m.residual_unbalance(2000, 2.5, 1500)
    p("P39", f"e {u['e_um']:.1f} um, U {u['u_gmm'] / 1e3:.1f} kg mm, F "
             f"{u['force_n']:.0f} N")
    p("P40", f"{100e3 / (4180 * 6):.2f} kg/s")
    g = im.operate(-0.03)
    p("P41", f"s -3 %: delivers {-g['p_in'] / 1e3:.1f} kW, absorbs "
             f"{g['q_in'] / 1e3:.1f} kvar")
    z_lr = 230 / st["i1"]
    zb = 0.4 ** 2 / 0.5
    z_tx = complex(0.012 * zb, math.sqrt(0.06 ** 2 - 0.012 ** 2) * zb)
    p("P42", f"500 kVA 6 %: dip {dip(z_lr, z_tx):.1f} %")
    v_pk = 690 * 1.2 * math.sqrt(2)
    p("P43", f"{690 * 1.2:.0f} V line, peak {v_pk:.0f} V > 1100 V DC link")
    p("P44", f"2000 / {400 * math.sqrt(2):.0f} = {2000 / (400 * math.sqrt(2)):.1f}")
    p("P45", f"15 GWh x (1/0.97 - 1) = {15e3 * (1 / 0.97 - 1):.0f} MWh")
    p("P46", f"AF {af(0.08, 20):.3f}; value {100 * 60 * af(0.08, 20):,.0f} u")
    b = m.bearing_freqs(900, 14, 0.04, 0.22)
    p("P47", f"BPFI at 900 rpm {b['bpfi']:.1f} Hz")
    p("P48", "1 / 4 s = 0.25 Hz")
    p("P49", f"(2 - 0.5) per day -> {math.ceil(5 / 1.5)} days")
    p("P50", f"1/0.15 = {1 / 0.15:.2f} pu = {288.7 / 0.15:,.0f} A")


def level_3() -> None:
    p("P51", f"3.3 kV: {5.4e6 / (S3 * 3300):.0f} A vs 4518 A (ratio "
             f"{4518 / (5.4e6 / (S3 * 3300)):.2f})")
    p("P52", f"1000 rpm / 10.5 = {1000 / 10.5:.1f}")
    p("P53", f"660-1320 rpm; {m.electrical_freq_hz(660, 6):.0f}-"
             f"{m.electrical_freq_hz(1320, 6):.0f} Hz")
    im = m.InductionMachine(**MOTOR)
    st = im.operate(1.0)
    z_lr = 230 / st["i1"]
    zb_g = 0.4 ** 2 / 0.2
    zg = complex(0.01 * zb_g, 0.20 * zb_g)
    p("P54", f"converter start (1 x rated): dip "
             f"{dip(z_lr, zg, 53.8 / abs(st['i1'])):.1f} %")
    for kva in range(200, 801, 25):
        zb = 0.4 ** 2 / (kva / 1000)
        if dip(z_lr, complex(0.01 * zb, 0.20 * zb)) <= 15.0:
            p("P55", f"smallest rating with DOL dip <= 15 % (x_d' 0.20): {kva} kVA")
            break
    p_gen, _ = generator_year()
    load = p_gen / 5.13e6
    loss = np.where(p_gen > 0, [m.loss_model(x, 5.13e6, 0.975, 0.35) for x in load],
                    0.0)
    p("P56", f"eta_r 0.975: losses {loss.sum() / 1e6:.1f} MWh/yr (723.8 at 0.970)")
    p("P57", f"723.8 / 18700 = {100 * 723.8 / 18700:.2f} %; plant "
             f"{12 * 723.8:,.0f} MWh/yr")
    p("P58", f"hot spot at 110 %: {40 + 44.4 * 1.21 + 10:.1f} C")
    b = m.bearing_freqs(600, 14, 0.04, 0.22)
    p("P59", f"BPFO at 600 rpm {b['bpfo']:.1f} Hz")
    p("P60", f"{110.2 * 86400 / 1e6:.2f} million impacts per day")
    i_up = 1 / (1 - 0.0012 * 100)
    p("P61", f"Br x {1 - 0.0012 * 100:.2f}; current x {i_up:.3f}; copper loss x "
             f"{i_up ** 2:.3f}")
    scores = {"DFIG": [4.3, 3, 3, 5, 5], "HS-PMSG": [3.0, 5, 3, 5, 3],
              "MS-PMSG": [4.2, 5, 4, 4, 3], "DD-PMSG": [4.5, 5, 4, 2, 2]}
    w = [20, 30, 20, 15, 15]
    p("P62", "weighted: " + ", ".join(
        f"{k} {sum(a * b for a, b in zip(w, v)) / 100:.2f}" for k, v in scores.items()))
    p("P63", f"s/(1-s) = 0.2 / 1.2 = {100 * 0.2 / 1.2:.0f} % of shaft power")
    eta10 = m.efficiency(0.1, 5.13e6, 0.97, 0.35)
    p("P64", f"eta(10 %) {eta10:.3f}; losses "
             f"{m.loss_model(0.1, 5.13e6, 0.97, 0.35) / 1e3:.1f} kW")
    p("P65", f"1521 MWh x 40 u x 11.65 = {1521 * 40 * af(0.07, 25):,.0f} u")
    p("P66", f"life x {m.life_factor(104.4, 94.4, 1e5):.2f}")
    p("P67", f"k 0.30 -> 0.345: +{100 * (0.345 / 0.30 - 1):.0f} %")
    p("P68", f"4 x 907 = {4 * 907 / 1e3:.2f} kN")
    p("P69", f"57.75 Hz: {120 * 57.75 / 6:.0f} rpm; 50 Hz: {120 * 50 / 6:.0f} rpm")
    s_half = im.slip_for_shaft_power(15e3)
    for name, s in (("full", im.slip_for_shaft_power(30e3)), ("half", s_half)):
        op = im.operate(s)
        p("P70", f"{name} load: efficiency {op['p_shaft'] / op['p_in']:.3f}, pf "
                 f"{op['pf']:.3f}")
    p("P71", f"N k_w 5.89 x 3300/690 = {5.89 * 3300 / 690:.1f}")
    p("P72", f"star-delta on the generator: dip {dip(z_lr, zg, 1 / 3):.1f} %")


def level_4_5() -> None:
    d = (4 * 0.55 / (math.pi * 1.375)) ** (1 / 3)
    p("P76", f"V_r 0.55 m3, L/D 1.375: D {d:.2f} m, L {1.375 * d:.2f} m")
    p("P78", f"5.13 / (5.13 + 0.1582) = {5.13 / (5.13 + 0.1582):.4f}")
    p("P80", "band up to 4 kHz -> sample at 10 kHz or more (above 2 x 4 kHz)")
    v_fixed = 8760 * 0.92 * 50 / 1e3 * af(0.07, 25)
    p("P84", f"1 kW fixed loss: 8760 h x 0.92 x 50 u/MWh x 11.65 = {v_fixed:,.0f} u/kW")
    p_gen, _ = generator_year()
    load = p_gen / 5.13e6
    h_eq = float((load[p_gen > 0] ** 2).sum())
    p("P85", f"sum of load^2 over the year {h_eq:,.0f} h; 1 kW of rated load loss "
             f"= {h_eq * 50 / 1e3 * af(0.07, 25):,.0f} u")


def further() -> None:
    xd2, xd1, xd, td2, td1 = 0.12, 0.20, 2.5, 0.03, 0.40           # A-113, A-123
    t = 0.2
    env = ((1 / xd2 - 1 / xd1) * math.exp(-t / td2)
           + (1 / xd1 - 1 / xd) * math.exp(-t / td1) + 1 / xd)
    p("P101", f"i_k(0.2 s) = {env:.2f} pu = {env * 288.7:.0f} A")
    psi = math.sqrt(2) * 230 / (2 * math.pi * 50)
    p("P102", f"psi {psi:.3f} Wb; T = 1.5 x 2 x psi x 100 = {1.5 * 2 * psi * 100:.1f} N m")
    p("P103", f"H = 2 MJ / 500 kVA = {2e6 / 500e3:.1f} s")
    p("P104", f"df/dt = 0.05 x 50 / (2 x 4) = {0.05 * 50 / 8:.4f} Hz/s")
    d0 = math.asin(0.6)
    ks = math.cos(d0)
    wn = math.sqrt(2 * math.pi * 50 * ks / (2 * 2.0))
    p("P105", f"K_s {ks:.3f} pu/rad; f_n = {wn / (2 * math.pi):.2f} Hz")
    damper, vfd = 15 * 0.85, 15 * 0.8 ** 3 / 0.97
    p("P106", f"80 %: {100 * 0.8 ** 3:.1f} % power; saving "
              f"{(damper - vfd) * 5000 / 1e3:.1f} MWh/yr")
    p("P107", f"100 mm2 Cu -> {100 * 2.82 / 1.72:.0f} mm2 Al")
    p("P108", f"72 x 1500/60 = {72 * 25:.0f} Hz")
    p("P109", f"tau = 16 x 10e3 / (pi x 0.1^3) = {16 * 10e3 / (math.pi * 1e-3) / 1e6:.1f} MPa")
    p("P110", f"0.1 x 30 / 365 = {100 * 0.1 * 30 / 365:.2f} %")
    p("P111", f"(1 -+ 0.06) x 50 = {50 * 0.94:.0f} and {50 * 1.06:.0f} Hz")
    stages = [(0.970, 0.30), (0.970, 0.35), (0.975, 0.20), (0.990, 0.50)]
    ch = 1.0
    for eta, sh in stages:
        ch *= m.efficiency(0.5, 1.0, eta, sh)
    p("P112", f"chain at 50 % load {ch:.3f}")
    p("P113", "0.1 Hz bins need 1 / 0.1 = 10 s; lines a few bins apart "
              "need 20-30 s")
    p("P114", f"(0.908 - 0.873) / 0.908 x 1.25 MW x 2000 h = "
              f"{(0.908 - 0.873) / 0.908 * 1.25 * 2000:.0f} MWh")
    p("P115", f"total with 80 kW battery HVAC: {112 + 20:.0f} kW")
    s_r, v_r = 2.2e6, 690.0
    e_ph = v_r / S3
    psi2 = math.sqrt(2) * e_ph / (2 * math.pi * 50)
    t2 = m.torque_nm(2.0e6, 1500)
    iq = t2 / (1.5 * 2 * psi2)
    p("P120", f"psi {psi2:.3f} Wb, T {t2 / 1e3:.2f} kN m, i_q {iq / math.sqrt(2):,.0f} A "
              f"RMS vs rated {s_r / (S3 * v_r):,.0f} A")


def further2() -> None:
    p("P121", f"T = 1.5 x 3 x 0.9 x 6000 = {1.5 * 3 * 0.9 * 6000 / 1e3:.1f} kN m")
    n_th = 603 / (2 * math.pi * 3 * 1.553 / 60)
    p("P122", f"n = 603 / (omega per rpm x psi) = {n_th:.0f} rpm")
    i = 15 / 0.93 * 1e3 / (S3 * 400 * 0.84)
    p("P123", f"I = {i:.1f} A")
    z = 60 / S3 / 30
    r = 900 / (3 * 30 ** 2)
    p("P124", f"|Z| {z:.3f}, R {r:.3f}, X {math.sqrt(z * z - r * r):.3f} ohm")
    tc = 40 + 70e3 / 5000
    p("P125", f"T_c {tc:.0f} C, T_w {tc + 40e3 / 2000:.0f} C")
    p("P126", f"P_eq = ((0.5^3 + 1)/2)^(1/3) = {((0.125 + 1) / 2) ** (1 / 3):.3f}")
    p("P127", f"{100 * (math.sqrt(1 + 1.5 / 32.2) - 1):.1f} %")
    p("P128", f"300 x 2^((20 - 40)/10) = {300 * 2 ** (-2):.0f} Mohm")
    p("P129", f"4 x 87.48 x 1.1 = {4 * 87.48 * 1.1:.0f} A more")


def further3() -> None:
    mu0 = 4e-7 * math.pi
    p("P133", f"B^2/(2 mu0) at 1.0 T = {1.0 / (2 * mu0) / 1e3:.0f} kPa")
    f_ump = 0.1 * 0.9 ** 2 / (2 * mu0) * math.pi * 1.2 * 1.2 / 2
    p("P134", f"0.1 x 322 kPa x {math.pi * 1.2 * 1.2 / 2:.2f} m2 = {f_ump / 1e3:.1f} kN")
    p("P135", f"V_r x 0.5 -> D x {0.5 ** (1 / 3):.3f}: {0.79 * 0.5 ** (1 / 3):.2f} m")
    p("P136", f"J 6 vs 4.5: copper mass x {4.5 / 6:.2f}, copper loss x {6 / 4.5:.3f} "
              f"= {60.6 * 6 / 4.5:.1f} kW")
    p("P137", f"5 MW at 1000 V: {5e6 / (S3 * 1000):,.0f} A")
    p("P139", f"4.60 x 80/50 = {4.60 * 80 / 50:.2f} million u")
    gain = 0.01 * 18.7e3 * 12
    af = (1 - 1.07 ** -20) / 0.07
    p("P140", f"1 % of 18.7 GWh x 12 = {gain:,.0f} MWh/yr; PV {gain * 50 * af / 1e6:.2f} "
              "million u")
    p("P144", f"N at 3.3 kV: 6.4 x 3300/690 = {6.4 * 3300 / 690:.1f}")


def further4() -> None:
    from companion.ch08.examples_more3 import (capability_limits,
                                               negative_sequence)
    im = m.InductionMachine(**MOTOR)
    s = im.slip_for_shaft_power(30e3)
    i_pos = abs(im.operate(s)["i1"])
    i_neg = abs(negative_sequence(4, s)["i1"])
    p("P148", f"4 %: I_neg {i_neg:.1f} A = {100 * i_neg / i_pos:.1f} % of "
              f"{i_pos:.1f} A; hot phase Cu x {((i_pos + i_neg) / i_pos) ** 2:.2f}")
    w_s = 2 * math.pi * 1500 / 60
    p("P149", f"1/2 x 3 x {w_s:.2f}^2 = {0.5 * 3 * w_s ** 2 / 1e3:.1f} kJ")
    p("P150", f"torque ~ V^2: 0.813^2 = {0.813 ** 2:.3f}")
    p("P151", f"centre -1/2.5 = -0.40, radius 2.0/2.5 = 0.80; Q max at P 0 = "
              f"{0.8 - 0.4:.2f} pu")
    e_max = abs(m.sm_emf(1 + 0j, complex(0.8, -0.6), 2.5))
    lo, _ = capability_limits(0.115, 2.5, e_max, 70.0)
    q75 = (12 * math.tan(math.acos(0.9)) + 8 * math.tan(math.acos(0.95))
           + 3 * math.tan(math.acos(0.95)) - 75) / 200
    p("P152", f"75 kvar: Q {q75:.3f} pu, limit {lo:.3f} pu -> "
              f"{'inside' if q75 >= lo else 'outside'}, margin "
              f"{q75 - lo:.3f} pu")
    kw = m.winding_factor(72, 10, 7)
    p("P153", f"72/8: lcm, gcd {m.cogging_periods(72, 8)}; 72/10: "
              f"{m.cogging_periods(72, 10)}, q 2.4, k_w1 (span 7) {kw:.3f}")
    p("P154", f"72 slots, 8 poles: slot pitch 5 deg mech = 20 deg el; "
              f"k_skew {m.skew_factor(20):.4f}")


if __name__ == "__main__":
    level_1()
    level_2()
    level_3()
    level_4_5()
    further()
    further2()
    further3()
    further4()
    emit("solutions", OUT)
