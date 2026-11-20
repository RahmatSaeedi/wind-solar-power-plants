"""Chapter 7 - numerical answers of the end-of-chapter problems.

Run from the project root:   python -m companion.ch07.solutions
Writes companion/ch07/expected/solutions.txt; each line starts with the
problem id (P01 ...). Teaching values only (A-100 .. A-109).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch07 import lab_d
from companion.ch07.common import emit
from plantp import ac
from plantp.phasors import complex_power, polar, symmetrical_components, to_polar

OUT: list[str] = []
S3 = math.sqrt(3)
W = 2 * math.pi * 50


def p(pid: str, text: str) -> None:
    OUT.append(f"{pid}: {text}")


def pol(z: complex, nd: int = 3) -> str:
    m, a = to_polar(z)
    return f"{m:.{nd}f} /_ {a:.2f} deg"


def level_1() -> None:
    p("P01", f"400 V -> {400 / S3:.1f} V phase; 230 V RMS -> peak {230 * math.sqrt(2):.1f} V;"
             f" 33 kV -> phase peak {33 / S3 * math.sqrt(2):.2f} kV")
    p("P02", f"50 Hz: T {1000 / 50:.2f} ms, omega {2 * math.pi * 50:.2f} rad/s; 60 Hz: "
             f"T {1000 / 60:.2f} ms, omega {2 * math.pi * 60:.2f} rad/s")
    v4 = 311 * math.sin(W * 0.004 + math.radians(30))
    p("P03", f"RMS {311 / math.sqrt(2):.1f} V, f 50 Hz, phasor {311 / math.sqrt(2):.1f} /_ 30 "
             f"deg; v(4 ms) = {v4:.1f} V")
    p("P04", f"2.5 ms at 50 Hz = {360 * 50 * 2.5e-3:.0f} deg")
    p("P05", f"RMS {20 / math.sqrt(2):.2f} A; mean {10:.0f} A")
    p("P06", f"RMS sqrt(10^2 + 10^2) = {math.hypot(10, 10):.2f} A")
    p("P07", f"5 /_ -36.87 = {polar(5, -36.87).real:.2f} {polar(5, -36.87).imag:+.2f}j; "
             f"-4 + j3 = {pol(complex(-4, 3), 0)}")
    p("P08", f"(2/_30)(3/_60) = {pol(polar(2, 30) * polar(3, 60), 1)}; (6/_90)/(2/_30) = "
             f"{pol(polar(6, 90) / polar(2, 30), 1)}; (3+j4)+(1-j2) = "
             f"{pol(complex(4, 2))}")
    p("P09", f"50 mH: {ac.reactance_l(50, 0.05):.2f} ohm at 50 Hz, "
             f"{ac.reactance_l(60, 0.05):.2f} ohm at 60 Hz")
    p("P10", f"10 uF: {ac.reactance_c(50, 10e-6):.1f} ohm at 50 Hz, "
             f"{ac.reactance_c(250, 10e-6):.2f} ohm at 250 Hz")
    z = complex(3, 4)
    p("P11", f"Z = {pol(z, 1)} ohm; Y = {(1 / z).real:.2f} {(1 / z).imag:+.2f}j S")
    p("P12", f"f0 = {ac.resonance_hz(0.01, 1e-6):.1f} Hz; with 4 C: "
             f"{ac.resonance_hz(0.01, 4e-6):.1f} Hz (half)")
    p("P13", f"line current {10 * S3:.2f} A")
    p("P14", "star equivalent 2 + j3 ohm")
    pin = 15 / 0.92
    p("P15", f"input {pin:.2f} kW; I = {pin * 1e3 / (S3 * 400 * 0.85):.2f} A")
    p("P16", f"250 kVA at 400 V: {250e3 / (S3 * 400):.1f} A")
    a_op = polar(1, 120)
    p("P17", f"a^2 + a = {(a_op ** 2 + a_op).real:.0f}{(a_op ** 2 + a_op).imag:+.0f}j; "
             f"a^4 = {pol(a_op ** 4, 0)} = a")
    p("P18", f"S = {math.hypot(40, 30):.0f} kVA, pf {40 / 50:.2f} lagging")
    q = -230 ** 2 / 20
    p("P19", f"I = {230 / 20:.1f} A; Q = {q:.0f} var (load convention: supplies "
             f"{-q / 1e3:.3f} kvar)")
    thd = math.sqrt(20 ** 2 + 14 ** 2) / 100
    p("P20", f"THD {100 * thd:.2f} %; RMS {100 * math.sqrt(1 + thd ** 2):.2f} A; true pf "
             f"{0.95 / math.sqrt(1 + thd ** 2):.3f}")
    seq = {0: "zero", 1: "positive", 2: "negative"}
    p("P21", f"order 11: {seq[11 % 3]}; order 19: {seq[19 % 3]}")
    p("P22", f"primary {3.2 * 600 / 5:.0f} A")
    p("P23", f"I_base (33 kV, 10 MVA) {10e6 / (S3 * 33e3):.2f} A; 6 % on 5.5 MVA -> "
             f"{0.06 * 100 / 5.5:.3f} pu on 100 MVA")
    p("P24", f"residual 40 % -> depth 60 %; 10 cycles = {10 / 50:.1f} s")


def level_2() -> None:
    s = polar(10, 0) + polar(10, -120)
    p("P25", f"sum {pol(s, 1)} A (arithmetic 20 A)")
    z = polar(10, 36.87)
    i = polar(325 / math.sqrt(2), 0) / z
    pw = complex_power(polar(325 / math.sqrt(2), 0), i)
    p("P26", f"I = {pol(i, 2)} A (peak {abs(i) * math.sqrt(2):.1f} A); P = "
             f"{pw.real / 1e3:.3f} kW, Q = {pw.imag / 1e3:.3f} kvar")
    zp = 1 / (1 / 10 + 1 / complex(0, 10))
    p("P27", f"Z = {zp.real:.1f} {zp.imag:+.1f}j = {pol(zp, 3)} ohm")
    zs, zl = complex(0.1, 0.3), complex(5, 0)
    vl = 230 * zl / (zs + zl)
    p("P28", f"V_load = {pol(vl, 1)} V; drop {100 * (1 - abs(vl) / 230):.2f} %; "
             f"I = {230 / abs(zs + zl):.2f} A")
    r, l, c = 5.0, 0.05, 200e-6
    zr = ac.rlc_series(r, l, c, 50)
    ir = 230 / abs(zr)
    p("P29", f"f0 {ac.resonance_hz(l, c):.2f} Hz, Q_f {ac.q_series(r, l, c):.3f}; at 50 Hz "
             f"Z = {zr.real:.2f} {zr.imag:+.3f}j, I = {ir:.2f} A, V_C = "
             f"{ir * ac.reactance_c(50, c):.0f} V")
    p("P30", f"h = {ac.resonance_order(1000, 10):.2f}; S_sc 2000 MVA: "
             f"{ac.resonance_order(2000, 10):.2f}")
    u0 = 132e3 / S3
    ich = u0 * W * 0.2e-6 * 20
    p("P31", f"I_c = {ich:.1f} A per phase; Q = {3 * u0 * ich / 1e6:.2f} Mvar")
    for pid, pf in (("P32", 1.0), ("P33", 0.9)):
        pw = 20e6
        i = ac.line_current_a(pw, 33e3, pf)
        zf = complex(0.125, 0.110) * 5
        v_end = polar(33e3 / S3, 0)
        v_st = v_end + zf * polar(i, -math.degrees(math.acos(pf)))
        exact = (abs(v_st) - abs(v_end)) * S3
        qv = pw * math.tan(math.acos(pf))
        approx = (zf.real * pw + zf.imag * qv) / 33e3
        p(pid, f"20 MW pf {pf}: I = {i:.1f} A; drop exact {exact:.1f} V "
               f"({100 * exact / 33e3:.3f} %), approx {approx:.1f} V; losses "
               f"{3 * i ** 2 * zf.real / 1e3:.1f} kW")
    v = ac.balanced_set(230.0)
    zl3 = [complex(10, 0), complex(20, 0), complex(40, 0)]
    i3, i_n, _ = ac.unbalanced_wye(v, zl3, 0j)
    p("P34", f"currents {abs(i3[0]):.2f}, {abs(i3[1]):.2f}, {abs(i3[2]):.2f} A; "
             f"neutral {pol(i_n, 2)} A")
    _, _, vn = ac.unbalanced_wye(v, zl3, None)
    loads = [abs(x - vn) for x in v]
    p("P35", f"star point {abs(vn):.1f} V; load voltages {loads[0]:.1f}, {loads[1]:.1f}, "
             f"{loads[2]:.1f} V")
    i0, i1, i2 = symmetrical_components(10, 0, 0)
    p("P36", f"I0 = {pol(i0, 3)}, I1 = {pol(i1, 3)}, I2 = {pol(i2, 3)}")
    vab, vbc, vca = 400.0, 390.0, 410.0
    mean = (vab + vbc + vca) / 3
    dev = max(abs(x - mean) for x in (vab, vbc, vca)) / mean
    beta = (vab ** 4 + vbc ** 4 + vca ** 4) / (vab ** 2 + vbc ** 2 + vca ** 2) ** 2
    u2 = math.sqrt((1 - math.sqrt(3 - 6 * beta)) / (1 + math.sqrt(3 - 6 * beta)))
    p("P37", f"deviation index {100 * dev:.2f} %; u2 {100 * u2:.3f} %")
    phi = math.radians(60)
    w1 = 400 * 20 * math.cos(math.radians(30) + phi)
    w2 = 400 * 20 * math.cos(math.radians(30) - phi)
    p("P38", f"W1 = {abs(w1):.0f} W, W2 = {w2:.0f} W; P = {S3 * 400 * 20 * 0.5:.0f} W")
    p("P39", f"P = 12.0 kW; Q = {S3 * 6:.2f} kvar; pf {12 / math.hypot(12, S3 * 6):.3f}")
    q_tot = 50 * math.tan(math.acos(0.8)) + 30 * math.tan(math.acos(0.6)) - 20
    p("P40", f"P 80 kW, Q {q_tot:.1f} kvar, S {math.hypot(80, q_tot):.1f} kVA, pf "
             f"{80 / math.hypot(80, q_tot):.3f} lagging")
    p("P41", f"Q_c = {ac.capacitor_for_pf(50e3, 0.7, 0.9) / 1e3:.2f} kvar")
    p("P42", f"current {100 * (0.8 - 1):+.0f} %; losses {100 * (0.8 ** 2 - 1):+.0f} %")
    pa, sa = 230 * 50 * 0.5, 230 * 50
    p("P43", f"P {pa / 1e3:.2f} kW, Q {sa * math.sin(phi) / 1e3:.3f} kvar; p(t) from "
             f"{(pa - sa) / 1e3:.2f} to {(pa + sa) / 1e3:.2f} kW")
    p("P44", f"Q at 3 MW: {ac.q_capability(3.3, 3.0):.3f} Mvar; at 1 MW: "
             f"{ac.q_capability(3.3, 1.0):.3f} Mvar")
    p("P45", f"V7 = 10 x 7 x 2 = {10 * 7 * 2:.0f} V")
    p("P46", f"I7 {7 * 0.03:.2f} pu; RMS {math.sqrt(1 + (7 * 0.03) ** 2):.3f} pu")
    p("P47", f"K = {ac.k_factor([1, 3, 5], [1, 0.3, 0.2]):.3f}")
    p("P48", f"square wave: meter 1.1107 x 1 = 1.1107; error {100 * (1.1107 - 1):+.2f} %")
    p("P49", f"50th harmonic = {50 * 50} Hz; sampling above {2 * 50 * 50} Hz "
             f"({2 * 50} samples per cycle); 256 per cycle is enough")
    p("P50", f"0.5 % of 273.3 GWh = {0.005 * 273.3e3:.0f} MWh")


def level_3() -> None:
    i = ac.line_current_a(100e6, 132e3, 0.85)
    p("P51", f"I = {i:.1f} A; S = {100 / 0.85:.1f} MVA; loading "
             f"{100 * 100 / 0.85 / 120:.0f} %")
    for pid, length in (("P52", 9.0),):
        i = ac.line_current_a(25e6, 33e3, 0.95)
        zf = complex(0.125, 0.110) * length
        v_end = polar(33e3 / S3, 0)
        v_st = v_end + zf * polar(i, -math.degrees(math.acos(0.95)))
        exact = (abs(v_st) - abs(v_end)) * S3
        p(pid, f"9 km: drop {exact:.0f} V ({100 * exact / 33e3:.2f} %), x "
               f"{exact / 734.0:.2f} of the 6 km value")
    p("P53", f"5 MW pf 1: {5e6 / (S3 * 33e3):.2f} A at 33 kV, {5e6 / (S3 * 690):.0f} A "
             f"at 0.69 kV")
    qc = 77.1 - 138.2 * math.tan(math.acos(0.95))
    p("P54", f"pf {138.2 / math.hypot(138.2, 77.1):.3f}; Q_c {qc:.1f} kvar")
    p("P55", f"loading {100 * math.hypot(138.2, 77.1) / 250:.0f} % -> "
             f"{100 * 138.2 / 0.95 / 250:.0f} % with pf 0.95")
    i1 = 2000 / (230 * 0.95)
    trip = 3 * math.sqrt(0.80 ** 2 + 0.15 ** 2) * i1
    p("P56", f"2 kW per phase: I1 {i1:.2f} A; neutral triplen {trip:.1f} A (one-phase "
             f"6 kW case: 28.3 A of harmonics)")
    a_, b_, c_ = 816.2, 596.1, 656.4
    rec = a_ + b_ - c_
    p("P57", f"recorded {rec:.1f} kWh = {100 * rec / (a_ + b_ + c_):.1f} % of "
             f"{a_ + b_ + c_:.1f} kWh")
    p("P58", f"200/5 set on a 400/5 CT: shows half; true {2 * 1034.4:.1f} kWh")
    q_req = 100 * math.tan(math.acos(0.90))
    s = 100 / 0.90
    q_tx = 0.12 * (s / 120) ** 2 * 120 + 0.003 * 120
    need = q_req + 1.52 + 4.96 + q_tx - 1.79
    p("P59", f"pf 0.90: |Q| {q_req:.2f} Mvar; transformer {q_tx:.2f} Mvar; units need "
             f"{need:.2f} of 62.8 Mvar -> short by {need - 62.8:.2f} Mvar")
    moved = [lab_d.Load(x.name, x.p_kw, x.pf,
                        "b" if x.name == "SCADA and telecom" else x.phases,
                        x.diversity, x.scenario) for x in lab_d.LOADS]
    ia, ib, ic = lab_d.phase_currents(moved, "S0")
    i0, i1_, i2 = symmetrical_components(ia, ib, ic)
    p("P60", f"SCADA to phase b: phases {abs(ia):.1f}, {abs(ib):.1f}, {abs(ic):.1f} A; "
             f"neutral {3 * abs(i0):.1f} A; |I2|/|I1| {abs(i2) / abs(i1_):.3f} "
             "(was 32.8 A and 0.127)")
    r_pu = 0.1 / math.sqrt(101)
    x_pu = 10 * r_pu
    p("P61", f"dV = {100 * (r_pu - 0.2 * x_pu):+.2f} %")
    p("P62", f"SCR {500 / 100:.0f}; z {100 / 500:.2f} pu")
    p("P63", f"h = {ac.resonance_order(500, 11.79):.2f}")
    sums = {al: 0.2 * 10 ** (1 / al) for al in (1, 1.4, 2)}
    p("P64", f"alpha 1: {sums[1]:.2f} %, 1.4: {sums[1.4]:.2f} %, 2: {sums[2]:.2f} %")
    qcab = 40 * 74.6e-3
    p("P65", f"40 km: {qcab:.2f} Mvar; net {qcab - 0.36:.2f} Mvar")
    p("P66", f"110 MW at pf 0.95: {ac.line_current_a(110e6, 33e3, 0.95):.0f} A")
    p("P67", f"true {120 + 95 + 110:.0f} kW; recorded {120 - 95 + 110:.0f} kW = "
             f"{100 * 135 / 325:.1f} %")
    p("P68", f"residual {100 * 150 / 230:.1f} %, depth {100 - 100 * 150 / 230:.1f} %, "
             f"{0.08 * 50:.0f} cycles")
    e_aux = 60 * 8760 / 1e3
    p("P69", f"{e_aux:.1f} MWh/yr = {100 * e_aux / 273.3e3:.2f} % of export")
    p("P70", f"losses x {1.031 ** 2:.3f} ({100 * (1.031 ** 2 - 1):+.1f} %)")
    s_av = 0.95 * 5.5
    p("P71", f"S {s_av:.3f} MVA; Q at 5 MW {math.sqrt(s_av ** 2 - 25):.3f} Mvar")
    for pf in (0.95, 1.0):
        i = ac.line_current_a(25e6, 33e3, pf)
        p("P72", f"pf {pf}: I {i:.1f} A, losses {3 * i ** 2 * 0.75 / 1e3:.1f} kW")


def level_4_5() -> None:
    s_sc_lv = 250 / 0.06
    p("P75", f"3 steps of 10 kvar (30 kvar); LV S_sc ~ {s_sc_lv / 1e3:.2f} MVA; h = "
             f"{math.sqrt(s_sc_lv / 30):.1f}")
    s = 100 / 0.95
    p("P77", f"0.12 x ({s:.2f}/120)^2 x 120 = {0.12 * (s / 120) ** 2 * 120:.2f} Mvar")
    p("P78", f"5 MW at pf 1, 33 kV: {5e6 / (S3 * 33e3):.2f} A")
    p("P79", f"neutral / phase = {2.442 / 1.436:.2f}")
    z = 100 / 800 + 0.1
    p("P81", f"z {z:.3f} pu -> S_sc at 33 kV {100 / z:.0f} MVA")
    p("P82", f"506.4 A on a 600 A primary: {100 * 506.4 / 600:.0f} %")
    p("P83", f"without sqrt3: {25e6 / (33e3 * 0.95):.1f} A instead of "
             f"{ac.line_current_a(25e6, 33e3, 0.95):.1f} A")
    need_unit = 49.0 / 22
    pu = 100 / 110 * 5
    p("P86", f"per unit {need_unit:.3f} Mvar at {pu:.3f} MW -> S >= "
             f"{math.hypot(pu, need_unit):.2f} MVA")
    p("P98", f"uniformly spread load: drop ~ {734.0 / 2:.0f} V instead of 734 V")


def further() -> None:
    from companion.ch07.examples_more import solve_nodal
    n = 20 / 0.4
    p("P101", f"n = {n:.0f}; 0.5 ohm -> {n ** 2 * 0.5:.0f} ohm from 20 kV")
    p("P102", f"4000 A at 0.69 kV -> {4000 * 0.69 / 33:.1f} A at 33 kV")
    i_r = 5.5e6 / (S3 * 33e3)
    q_mag = 0.005 * 5.5
    p("P103", f"rated {i_r:.1f} A; magnetising {0.005 * i_r:.2f} A, {1000 * q_mag:.1f} "
              f"kvar each; 22 units {22 * q_mag:.3f} Mvar")
    p("P104", "Y = [[-j10, +j10], [+j10, -j10]] pu")
    p("P105", f"250 MVA at 33 kV: {250e6 / (S3 * 33e3) / 1e3:.2f} kA")
    w = 2 * math.pi * 50
    t = np.linspace(0, 0.06, 6001)
    for xr in (3.0, 10.0, 15.7):
        tau, th = xr / w, math.atan(xr)
        best = max(float(np.abs(np.sin(w * t + a - th) - math.sin(a - th)
                                * np.exp(-t / tau)).max())
                   for a in np.radians(np.arange(0, 180, 1)))
        p("P106", f"X/R {xr}: worst first peak {best:.2f} x sqrt2 I_k")
    p("P107", f"pf {1200 / math.hypot(1200, 900):.2f}")
    p("P108", f"60 MWh in 30 days, peak 150 kW: load factor "
              f"{60e3 / (720 * 150):.3f}")
    d = math.cos(math.radians(148))
    p("P109", f"a reversed: {d:+.3f} + 0.848 + 0.848 = {d + 2 * 0.848:+.3f} of "
              f"{3 * 0.848:.3f} (one third)")
    r1 = 12.1 * 0.030
    p("P113", f"2 x 10 x {r1:.3f} = {2 * 10 * r1:.2f} V = {100 * 2 * 10 * r1 / 230:.2f} %")
    dv = 100 * 0.050 * (0.193 * 0.9 + 0.080 * math.sqrt(1 - 0.81))
    p("P114", f"per phase {dv:.3f} V = {100 * dv / 230:.2f} %; line {S3 * dv:.2f} V")
    p("P115", f"6 / 300 = {100 * 6 / 300:.1f} %")
    p("P116", f"sqrt3 x 400 x 3200 = {S3 * 400 * 3200 / 1e6:.3f} MVA < 2.5; 2500 kVA "
              f"needs {2.5e6 / (S3 * 400):.0f} A")
    p("P117", f"S >= 5.0 / 0.95 = {5 / 0.95:.3f} MVA")
    ia, ib, ic = lab_d.phase_currents(lab_d.LOADS, "S0")
    vv = (lab_d.VA, lab_d.VB, lab_d.VC)
    s_ph = [complex_power(x, i) for x, i in zip(vv, (ia, ib, ic))]
    p_t = sum(x.real for x in s_ph)
    p("P118", f"S0: vector {abs(sum(s_ph)) / 1e3:.2f} kVA (pf "
              f"{p_t / abs(sum(s_ph)):.4f}), arithmetic "
              f"{sum(abs(x) for x in s_ph) / 1e3:.2f} kVA (pf "
              f"{p_t / sum(abs(x) for x in s_ph):.4f})")
    s_inv = math.sqrt(1 + 0.04 ** 2 + 0.03 ** 2)
    p("P119", f"S {s_inv:.5f} pu; D = sqrt(S^2 - 1) = {math.sqrt(s_inv ** 2 - 1):.3f} pu")
    r = lab_d.meter_record()
    pw = r["p_a"] - r["p_b"] + r["p_c"]
    slide = np.convolve(pw, np.ones(3) / 3, mode="valid")
    block = pw.reshape(48, 3).mean(axis=1)
    p("P120", f"30-min demand: sliding {slide.max():.1f} kW, block {block.max():.1f} kW")
    v, s_grid, _ = solve_nodal(-0.10)
    p("P110", f"feeder end absorbs 10 Mvar: |V| {abs(v[2]):.4f} pu, bus "
              f"{abs(v[1]):.4f}, POC {abs(v[0]):.4f}; grid Q "
              f"{s_grid.imag * 100:+.2f} Mvar")


if __name__ == "__main__":
    level_1()
    level_2()
    level_3()
    level_4_5()
    further()
    emit("solutions", OUT)
