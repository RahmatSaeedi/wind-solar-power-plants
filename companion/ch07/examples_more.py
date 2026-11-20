"""Chapter 7 - further lessons: the ideal transformer and impedance referral,
complex nodal analysis of a collector network, the symmetrical three-phase
fault current and its DC offset, energy and demand from the meter record,
and a wiring check from the analyser's phasor display.

Run from the project root:   python -m companion.ch07.examples_more
Writes companion/ch07/expected/m_*.txt and diagrams/data/ch07-fault.csv.
Teaching values A-032, A-052, A-091, A-092, A-102, A-106, A-109.
"""
from __future__ import annotations

import cmath
import math

import numpy as np

from companion.ch07 import lab_d
from companion.ch07.common import csv, emit
from plantp import ac
from plantp.phasors import polar

S3 = math.sqrt(3)
W = 2 * math.pi * 50


def transformer() -> None:
    n = 33 / 0.69
    zb_lv, zb_hv = 0.69 ** 2 / 5.5, 33 ** 2 / 5.5
    x_lv, x_hv = 0.06 * zb_lv, 0.06 * zb_hv
    i_r132 = 120e6 / (S3 * 132e3)
    emit("m_transformer", [
        f"unit transformer 33/0.69 kV, 5.5 MVA, 6 % (A-102): ratio n = {n:.2f}, "
        f"n^2 = {n ** 2:,.0f}",
        f"  Z_base LV {1000 * zb_lv:.2f} mohm -> X = {1000 * x_lv:.3f} mohm seen "
        "from 0.69 kV",
        f"  Z_base HV {zb_hv:.1f} ohm -> X = {x_hv:.2f} ohm seen from 33 kV; "
        f"ratio {x_hv / x_lv:,.0f} = n^2",
        f"  a 1.0 mohm LV busbar appears as {n ** 2 * 1e-3:.2f} ohm from the "
        "33 kV side",
        "  the same 6 % on both sides: per unit hides the turns ratio",
        f"export transformer 120 MVA at 132 kV: rated current {i_r132:.1f} A; "
        f"magnetising 0.3 % = {0.003 * i_r132:.2f} A",
        f"  its reactive power {0.003 * 120:.2f} Mvar flows whenever the "
        "transformer is energised",
        "ideal transformer: V1 I1 = V2 I2 (no loss); the real one adds leakage,",
        "  winding resistance and the magnetising branch (chapter 25)",
    ])


def solve_nodal(q3: float, p_bus: float = 0.75, p_end: float = 0.25):
    """Grid (1.0 pu) - z_grid - POC(0) - transformer - 33 kV bus(1) - feeder
    - feeder end(2). Per unit on 100 MVA; constant-power injections solved
    by fixed-point iteration. Returns node voltages and the grid flow."""
    z_g = complex(0.1 / math.sqrt(101), 1.0 / math.sqrt(101))  # A-109
    z_t = complex(0.4 / 120 * 100 / 120, 0.10)                 # A-092, A-102
    z_f = complex(0.125, 0.110) * 6 / (33 ** 2 / 100)          # A-032, A-091
    b_f = 6 * 74.6e-3 / 100                                     # pu, A-052
    y = np.zeros((3, 3), dtype=complex)

    def branch(i, j, z, b=0.0):
        yb = 1 / z
        y[i, i] += yb + 1j * b / 2
        y[j, j] += yb + 1j * b / 2
        y[i, j] -= yb
        y[j, i] -= yb
    y[0, 0] += 1 / z_g
    branch(0, 1, z_t)
    branch(1, 2, z_f, b_f)
    s_inj = np.array([0, p_bus, complex(p_end, q3)])
    i_src = np.array([1 / z_g, 0, 0])              # grid source 1.0 pu
    v = np.ones(3, dtype=complex)
    for _ in range(60):
        v = np.linalg.solve(y, i_src + np.conj(s_inj / v))
    s_grid = v[0] * np.conj((v[0] - 1.0) / z_g)    # flow into the grid
    return v, s_grid, s_inj.sum().real - s_grid.real


def nodal() -> None:
    lines = ["nodal solution, per unit on 100 MVA (75 MW at the bus, 25 MW at "
             "the end of one feeder):"]
    for name, q3 in (("units at pf 1", 0.0),
                     ("feeder-end units absorb 5 Mvar", -0.05)):
        v, s_grid, loss = solve_nodal(q3)
        lines.append(f"  {name}:")
        for k, (lab, kv) in enumerate((("POC 132 kV", 132), ("bus 33 kV", 33),
                                       ("feeder end", 33))):
            m, a = abs(v[k]), math.degrees(cmath.phase(v[k]))
            lines.append(f"    {lab:11s} |V| {m:.4f} pu = {m * kv:7.2f} kV, "
                         f"angle {a:5.2f} deg")
        lines.append(f"    to the grid {s_grid.real * 100:.2f} MW, "
                     f"{s_grid.imag * 100:+.2f} Mvar; losses "
                     f"{loss * 100:.2f} MW")
    lines += ["  pf 1 at the units is not pf 1 at the POC: the transformer "
              "absorbs",
              "  about 10 Mvar, so the POC voltage falls a little instead of "
              "rising",
              "  1 % as with pf 1 at the POC (integrated example 3)"]
    emit("m_nodal", lines)


def fault() -> None:
    r_g, x_g = 0.1 / math.sqrt(101), 1.0 / math.sqrt(101)
    r_t, x_t = 0.4 / 120 * 100 / 120, 0.10
    cases = (("132 kV POC", complex(r_g, x_g), 132),
             ("33 kV bus", complex(r_g + r_t, x_g + x_t), 33))
    lines = ["symmetrical three-phase fault, grid side only (per unit, 100 MVA):"]
    for name, z, kv in cases:
        i_b = 100e6 / (S3 * kv * 1e3)
        i_f = i_b / abs(z)
        xr = z.imag / z.real
        tau = xr / W
        theta = math.atan(xr)
        t = np.linspace(0, 0.06, 6001)
        best = 0.0
        for alpha in np.radians(np.arange(0, 180, 1)):
            i = (np.sin(W * t + alpha - theta)
                 - math.sin(alpha - theta) * np.exp(-t / tau))
            best = max(best, float(np.abs(i).max()))
        lines.append(f"  {name}: |z| {abs(z):.4f} pu, X/R {xr:.1f}, I_k "
                     f"{i_f / 1e3:.2f} kA RMS ({100 / abs(z):.0f} MVA)")
        lines.append(f"    worst first peak {best:.2f} x sqrt2 I_k = "
                     f"{best * math.sqrt(2) * i_f / 1e3:.1f} kA; tau "
                     f"{1000 * tau:.1f} ms")
        if kv == 33:
            i = (np.sin(W * t - math.pi / 2) - math.sin(-math.pi / 2)
                 * np.exp(-t / tau))
            env = 1 + np.exp(-t / tau)
            csv("ch07-fault.csv", "t_ms,i,env,dc",
                [(f"{1000 * a:.2f}", f"{b:.4f}", f"{c:.4f}", f"{d:.4f}")
                 for a, b, c, d in zip(t[::20], i[::20], env[::20],
                                       np.exp(-t / tau)[::20])])
    lines += ["  converter units add a limited current (manufacturer data); "
              "breakers,",
              "  busbars and earthing are checked against both values "
              "(chapter 26)"]
    emit("m_fault", lines)


def energy() -> None:
    r = lab_d.meter_record()
    p = r["p_a"] - r["p_b"] + r["p_c"]                 # corrected, kW
    q = r["q_a"] - r["q_b"] + r["q_c"]
    p_rec = r["p_a"] + r["p_b"] + r["p_c"]
    q_rec = r["q_a"] + r["q_b"] + r["q_c"]
    kwh, kvarh = p.sum() / 6, q.sum() / 6
    pf_day = kwh / math.hypot(kwh, kvarh)
    pf_rec = (p_rec.sum() / 6) / math.hypot(p_rec.sum() / 6, q_rec.sum() / 6)
    d30 = p.reshape(48, 3).mean(axis=1)
    d60 = p.reshape(24, 6).mean(axis=1)
    lines = ["energy and demand of 23 June at the auxiliary board (corrected, "
             "A-106):",
             f"  {kwh:.1f} kWh and {kvarh:.1f} kvarh; mean power "
             f"{kwh / 24:.1f} kW",
             f"  period power factor kWh / sqrt(kWh^2 + kvarh^2) = {pf_day:.3f}",
             f"  maximum demand: 10-min {p.max():.1f} kW, 30-min block "
             f"{d30.max():.1f} kW, 60-min block {d60.max():.1f} kW",
             f"  load factor (mean / 30-min peak) {kwh / 24 / d30.max():.2f}",
             f"the record with the reversed CT gives pf {pf_rec:.3f}: the same,",
             "  because P and Q are wrong by the same factor; a ratio cannot",
             "  reveal a scaling or polarity error that hits both alike"]
    emit("m_energy", lines)


def phasor_check() -> None:
    pf = 0.85
    phi = math.degrees(math.acos(pf))
    v = {"a": 0.0, "b": -120.0, "c": 120.0}
    i_true = {k: a - phi for k, a in v.items()}
    cases = {
        "correct": ({"a": "a", "b": "b", "c": "c"}, {}, {}),
        "CT b reversed": ({"a": "a", "b": "b", "c": "c"}, {"b": 180}, {}),
        "CTs b and c swapped": ({"a": "a", "b": "c", "c": "b"}, {}, {}),
        "VTs b and c swapped": ({"a": "a", "b": "b", "c": "c"}, {},
                                {"b": "c", "c": "b"}),
    }
    lines = [f"balanced load, pf {pf} lagging; the analyser shows each current "
             "angle",
             "against its own voltage, and the per-phase power in pu of V I:"]
    for name, (ct, flip, vt) in cases.items():
        parts, tot = [], 0.0
        for ph in "abc":
            ang_i = i_true[ct[ph]] + flip.get(ph, 0)
            ang_v = v[vt.get(ph, ph)]
            d = (ang_i - ang_v + 180) % 360 - 180
            pw = math.cos(math.radians(d))
            tot += pw
            parts.append(f"{ph} {d:7.1f} deg {pw:+.3f}")
        lines.append(f"  {name}:")
        lines.append("    " + "; ".join(parts) + f"; total {tot:+.3f} of "
                     f"{3 * pf:.3f}")
    lines += ["signatures: a reversed CT shifts one angle by 180 deg; swapped "
              "CTs or",
              "  swapped VTs move two angles by 120 deg and the total power "
              "collapses;",
              "  swapped VTs also show a reversed voltage sequence on the "
              "analyser"]
    emit("m_phasorcheck", lines)


if __name__ == "__main__":
    transformer()
    nodal()
    fault()
    energy()
    phasor_check()
