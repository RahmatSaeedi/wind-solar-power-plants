"""Chapter 7, section B - three-phase systems: power of three phases, sequence,
star and delta, balanced and unbalanced loads, the neutral, and measurement.

Run from the project root:   python -m companion.ch07.examples_b
Writes companion/ch07/expected/b_*.txt and diagrams/data/ch07-*.csv.
Teaching values A-092 (export transformer) and A-103 .. A-104 (auxiliary supply).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch07.common import csv, emit
from plantp import ac
from plantp.phasors import (A, complex_power, from_sequences, polar,
                            symmetrical_components, to_polar)

W = 2 * math.pi * 50.0


def three_phase_power() -> None:
    v, i, phi = 230 * math.sqrt(2), 100 * math.sqrt(2), math.radians(30)
    t = np.linspace(0, 0.04, 400, endpoint=False)          # two whole periods
    pa = v * np.sin(W * t) * i * np.sin(W * t - phi)
    pb = v * np.sin(W * t - 2 * math.pi / 3) * i * np.sin(W * t - 2 * math.pi / 3 - phi)
    pc = v * np.sin(W * t + 2 * math.pi / 3) * i * np.sin(W * t + 2 * math.pi / 3 - phi)
    total = pa + pb + pc
    emit("b_power_sum", [
        "230 V, 100 A RMS per phase, current 30 deg behind the voltage:",
        f"  one phase: p(t) swings from {pa.min() / 1e3:.1f} to {pa.max() / 1e3:.1f} kW "
        f"(mean {pa.mean() / 1e3:.2f} kW) at 100 Hz",
        f"  three phases: p(t) = {total.min() / 1e3:.3f} .. {total.max() / 1e3:.3f} kW "
        "(constant)",
        f"  3 V I cos(phi) = {3 * 230 * 100 * math.cos(phi) / 1e3:.3f} kW",
        "a constant total power means a constant torque on a generator shaft",
    ])
    csv("ch07-psum.csv", "t_ms,pa,total",
        [(f"{1000 * x:.2f}", f"{a / 1e3:.3f}", f"{s / 1e3:.3f}")
         for x, a, s in zip(t, pa, total)])


def sequence() -> None:
    va = polar(230, 0)
    abc = (va, va * A * A, va * A)
    acb = (va, va * A, va * A * A)
    lines = ["a = 1 /_ 120 deg; a^2 = 1 /_ 240 deg = 1 /_ -120 deg; "
             f"|1 + a + a^2| = {abs(1 + A + A * A):.0e}"]
    for name, s in (("abc (positive)", abc), ("acb (reversed)", acb)):
        angles = " ".join(f"{to_polar(x)[1]:5.0f}" for x in s)
        _, v1, v2 = symmetrical_components(*s)
        lines.append(f"  {name:15s} angles {angles} deg; |V1| {abs(v1):5.1f} V, "
                     f"|V2| {abs(v2):5.1f} V")
    lines.append("a motor on the reversed set turns backwards; a generator with the")
    lines.append("  wrong sequence cannot be synchronised: check it before first "
                 "energising")
    emit("b_sequence", lines)


def star_delta() -> None:
    v_ll = 400.0
    v_ph = v_ll / math.sqrt(3)
    r = 10.0
    i_star = v_ph / r
    i_branch = v_ll / r
    i_line = i_branch * math.sqrt(3)
    emit("b_star_delta", [
        f"400 V system: phase voltage {v_ph:.1f} V; 33 kV: {33 / math.sqrt(3):.2f} kV; "
        f"132 kV: {132 / math.sqrt(3):.2f} kV",
        f"three 10 ohm resistors in star: I = {i_star:.1f} A, P = "
        f"{3 * v_ph * i_star / 1e3:.2f} kW",
        f"the same resistors in delta: branch {i_branch:.1f} A, line {i_line:.1f} A,",
        f"  P = {3 * v_ll * i_branch / 1e3:.2f} kW (3 x star)",
        f"V_ab from V_an = 230.9 /_ 0 deg: {abs(ac.wye_to_line(polar(v_ph, 0))):.1f} V /_ "
        f"{ac.phase_angle_deg(ac.wye_to_line(polar(v_ph, 0))):.0f} deg",
    ])


def balanced_cases() -> None:
    lines = ["three-phase current I = P / (sqrt3 V_LL pf) and apparent power S = P / pf:"]
    cases = [("auxiliary board 400 V", 180e3, 400.0, 0.80),
             ("auxiliary board 400 V, pf raised", 180e3, 400.0, 0.95),
             ("one 33 kV feeder", 25e6, 33e3, 0.95),
             ("export at 132 kV", 100e6, 132e3, 0.95),
             ("export at 132 kV, pf 0.90", 100e6, 132e3, 0.90)]
    for name, p, v, pf in cases:
        i = ac.line_current_a(p, v, pf)
        s = p / pf
        unit = "kVA" if s < 1e6 else "MVA"
        sv = s / 1e3 if s < 1e6 else s / 1e6
        lines.append(f"  {name:34s} {sv:7.1f} {unit}  I = {i:7.1f} A")
    lines += ["the export transformer (120 MVA, A-092) carries 100 MW at pf 0.90",
              f"  as {100 / 0.9:.1f} MVA:",
              "  heating follows the current, so ratings are in VA, not in W"]
    emit("b_balanced", lines)


def unbalanced() -> None:
    v = ac.balanced_set(230.0)
    loads = [complex(4.0, 1.5), complex(8.0, 3.0), complex(16.0, 0.0)]      # A-103
    i, i_n, _ = ac.unbalanced_wye(v, loads, 0j)
    lines = ["auxiliary single-phase loads (A-103): phase a 4 + j1.5, b 8 + j3, c 16 ohm"]
    for ph, ix, z in zip("abc", i, loads):
        m, a = to_polar(ix)
        s = complex_power(v["abc".index(ph)], ix)
        lines.append(f"  phase {ph}: I = {m:5.1f} A /_ {a:7.1f} deg, P = {s.real / 1e3:5.2f} kW, "
                     f"Q = {s.imag / 1e3:5.2f} kvar")
    lines.append(f"  neutral current {abs(i_n):.1f} A; current unbalance |I2|/|I1| = "
                 f"{ac.unbalance_factor(*i):.3f}")
    i0, i1, i2 = symmetrical_components(*i)
    lines.append(f"  sequence currents: I0 {abs(i0):.1f} A, I1 {abs(i1):.1f} A, I2 "
                 f"{abs(i2):.1f} A (I_N = 3 I0 = {3 * abs(i0):.1f} A)")
    back = from_sequences(i0, i1, i2)
    lines.append(f"  check: rebuilding phase a from sequences gives {abs(back[0]):.1f} A")
    emit("b_unbalanced", lines)
    i_f, _, vn = ac.unbalanced_wye(v, loads, None)                         # broken neutral
    lines = ["the same loads after the neutral conductor breaks (star point floats):",
             f"  star-point voltage {abs(vn):.1f} V"]
    for ph, ix, z, vx in zip("abc", i_f, loads, v):
        lines.append(f"  phase {ph}: voltage across the load {abs(vx - vn):6.1f} V "
                     f"({100 * abs(vx - vn) / 230 - 100:+.0f} %)")
    lines.append("the lightly loaded phase sees far more than 230 V: equipment on it")
    lines.append("  can be damaged;")
    lines.append("  neutral integrity is a design and maintenance item (chapters 24, 52)")
    emit("b_broken_neutral", lines)


def measurement() -> None:
    v = ac.balanced_set(230.0)
    z = complex(8.0, 6.0)                                                 # pf 0.8 lagging
    ia, ib, ic = (x / z for x in v)
    w1, w2 = ac.two_wattmeter(v[0], ia, ib, ic)
    p = sum(complex_power(vx, ix).real for vx, ix in zip(v, (ia, ib, ic)))
    q = sum(complex_power(vx, ix).imag for vx, ix in zip(v, (ia, ib, ic)))
    lines = ["balanced 400 V load, 8 + j6 ohm per phase (pf 0.8):",
             f"  P = {p / 1e3:.2f} kW, Q = {q / 1e3:.2f} kvar",
             f"  two-wattmeter readings W1 = {w1 / 1e3:.2f} kW, W2 = {w2 / 1e3:.2f} kW; "
             f"W1 + W2 = {(w1 + w2) / 1e3:.2f} kW",
             f"  sqrt3 |W1 - W2| = {math.sqrt(3) * abs(w1 - w2) / 1e3:.2f} kvar = |Q|"]
    ct, vt = 400 / 5, 33000 / 110                                          # A-104
    sec_p = 6.94e6 / (ct * vt)
    lines += [f"CT 400/5 A and VT 33000/110 V (A-104): primary = secondary x {ct * vt:,.0f}",
              f"  a secondary three-phase power of {sec_p:.1f} W means {sec_p * ct * vt / 1e6:.2f} MW"]
    i_wrong = (ia, -ib, ic)                                               # CT b reversed
    p_wrong = sum(complex_power(vx, ix).real for vx, ix in zip(v, i_wrong))
    lines += [f"one reversed CT (phase b) makes the meter read {p_wrong / 1e3:.2f} kW "
              f"instead of {p / 1e3:.2f} kW",
              "  (phase b shows negative power: the per-phase readings reveal the error)"]
    emit("b_measurement", lines)


if __name__ == "__main__":
    three_phase_power()
    sequence()
    star_delta()
    balanced_cases()
    unbalanced()
    measurement()
