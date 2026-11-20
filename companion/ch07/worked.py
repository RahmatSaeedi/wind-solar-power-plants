"""Chapter 7 - the small worked examples of the lessons (lines E01, E02, ...).

Run from the project root:   python -m companion.ch07.worked
Writes companion/ch07/expected/worked.txt; the text quotes "line Enn".
Teaching values only (A-091, A-092, A-100 .. A-109); no vendor data.
"""
from __future__ import annotations

import cmath
import math

import numpy as np

from companion.ch07.common import emit
from plantp import ac, signals
from plantp.phasors import polar, symmetrical_components, to_polar

OUT: list[str] = []
W = 2 * math.pi * 50.0
S3 = math.sqrt(3)


def e(eid: str, text: str) -> None:
    OUT.append(f"{eid}: {text}")


def pol(z: complex) -> str:
    m, a = to_polar(z)
    return f"{m:.4g} /_ {a:.2f} deg"


def section_a() -> None:
    i400 = 100e6 / (S3 * 400)
    i33 = 100e6 / (S3 * 33e3)
    i132 = 100e6 / (S3 * 132e3)
    e("E01", f"100 MW at pf 1: {i400 / 1e3:.1f} kA at 400 V, {i33:.1f} A at 33 kV, "
             f"{i132:.1f} A at 132 kV; same conductor: losses x {(132 / 0.4) ** 2:,.0f} "
             f"(400 V vs 132 kV), x {(132 / 33) ** 2:.0f} (33 vs 132 kV)")
    e("E02", f"zero crossings 3.0 ms apart: {360 * 50 * 3e-3:.1f} deg at 50 Hz, "
             f"{360 * 60 * 3e-3:.1f} deg at 60 Hz")
    lost = 60 * (50 - 49.8)
    e("E03", f"49.8 Hz: period {1000 / 49.8:.2f} ms; in one minute {60 * 49.8:.0f} "
             f"cycles instead of 3000 ({lost:.0f} lost); a mains clock lags "
             f"{lost / 50:.2f} s")
    r = 230 ** 2 / 2000
    i = 230 / r
    e("E04", f"2 kW heater at 230 V: R = {r:.2f} ohm, I = {i:.2f} A RMS, peak "
             f"{i * math.sqrt(2):.2f} A, p(t) peak {2 * 2000 / 1e3:.1f} kW")
    e("E05", f"same heater on 230 V DC: {230 ** 2 / r / 1e3:.2f} kW; on 325.3 V DC: "
             f"{325.3 ** 2 / r / 1e3:.2f} kW (peak taken for RMS: double)")
    z = complex(0.75, 0.66)
    i_f = polar(460.4, -18.19)
    e("E06", f"Z = 0.75 + j0.66 ohm = {pol(z)}; I = 460.4 /_ -18.19 deg; Z I = "
             f"{pol(z * i_f)} = {(z * i_f).real:.1f} + j{(z * i_f).imag:.1f} V")
    e("E07", f"230 /_ 0 / (8 + j6) = {pol(230 / complex(8, 6))}")
    s = polar(100, 0) + polar(50, -90)
    th = np.linspace(0, 2 * math.pi, 3600, endpoint=False)
    y = 100 * math.sqrt(2) * np.sin(th) + 50 * math.sqrt(2) * np.sin(th - math.pi / 2)
    e("E08", f"100 /_ 0 + 50 /_ -90 = {pol(s)}; sampled sum: peak {y.max():.1f} "
             f"= sqrt2 x {y.max() / math.sqrt(2):.1f}")
    i_pv = polar(87.48, 0.0)                     # 5 MW at pf 1, 33 kV
    i_wt = polar(92.08, -18.19)                  # 5 MW at pf 0.95 lagging
    tot = i_pv + i_wt
    e("E09", f"PV unit 87.48 /_ 0 + wind unit 92.08 /_ -18.19 = {pol(tot)} "
             f"(arithmetic sum {87.48 + 92.08:.2f} A)")
    for f in (50, 250):
        e("E10" if f == 50 else "E10b", f"10 mH at {f} Hz: X_L = {ac.reactance_l(f, 0.01):.2f} ohm")
    x = ac.reactance_l(50, 0.1)
    il = 230 / x
    e("E11", f"0.1 H on 230 V: X_L = {x:.2f} ohm, I = {il:.2f} A lagging 90 deg; "
             f"peak stored energy {0.5 * 0.1 * (il * math.sqrt(2)) ** 2:.2f} J; mean power 0")
    xc = ac.reactance_c(50, 100e-6)
    ic = 230 / xc
    e("E12", f"100 uF at 50 Hz: X_C = {xc:.2f} ohm; on 230 V: {ic:.2f} A leading, "
             f"Q = {230 * ic / 1e3:.2f} kvar supplied")
    c = 5e6 / (W * 33e3 ** 2)
    e("E13", f"5 Mvar bank at 33 kV (star): C = {c * 1e6:.2f} uF per phase, current "
             f"{5e6 / (S3 * 33e3):.1f} A")
    z = complex(8, 6)
    e("E14", f"8 + j6 ohm on 230 V: |Z| = {abs(z):.1f} ohm, I = {230 / abs(z):.1f} A, "
             f"pf {z.real / abs(z):.2f}, angle {math.degrees(cmath.phase(z)):.2f} deg")
    y = 1 / 10 + 1 / complex(0, -20)
    zp = 1 / y
    e("E15", f"10 ohm || -j20 ohm: Y = {y.real:.3f} + j{y.imag:.3f} S, Z = "
             f"{zp.real:.2f} {zp.imag:+.2f}j ohm = {pol(zp)}")
    zs, zl = complex(0.05, 0.10), complex(2.0, 1.0)
    vl = 230 * zl / (zs + zl)
    e("E16", f"230 V source, Z_s 0.05 + j0.10, load 2 + j1 ohm: V_load = {pol(vl)}, "
             f"drop {100 * (1 - abs(vl) / 230):.2f} %")
    f0 = ac.resonance_hz(0.1, 100e-6)
    i0 = 230 / 2.0
    xl0 = ac.reactance_l(f0, 0.1)
    e("E17", f"series resonance on 230 V, R 2 ohm: I = {i0:.0f} A; V_L = V_C = "
             f"{i0 * xl0:.0f} V = Q_f x 230 = {ac.q_series(2, 0.1, 100e-6) * 230:.0f} V")
    e("E18", f"L/R = 0.1/2 = {1000 * 0.1 / 2:.0f} ms; after 5 tau = {5 * 50:.0f} ms the "
             f"transient is below {100 * math.exp(-5):.1f} %")


def section_b() -> None:
    p, v = 100e3, 230.0
    i1 = p / v
    i3 = p / (3 * v)
    loss1, loss3 = 2 * i1 ** 2, 3 * i3 ** 2
    e("E19", f"100 kW at 230 V: one phase {i1:.1f} A (2 wires), three phases {i3:.1f} A "
             f"(3 wires); losses per ohm {loss1 / 1e3:.1f} vs {loss3 / 1e3:.1f} kW "
             f"(1/{loss1 / loss3:.0f}); copper for equal loss: {3 / 2 / (loss1 / loss3):.2f}")
    e("E20", f"1 + a + a^2 = {abs(1 + ac.balanced_set(1.0)[2] + ac.balanced_set(1.0)[1]):.1e}; "
             "swapping two phases turns abc into acb")
    e("E21", "balanced delta 30 ohm per branch = star 10 ohm per phase (Z_Y = Z_D / 3)")
    va = polar(230.9, 0)
    vb = polar(230.9, -120)
    e("E22", f"V_ab = V_a - V_b = {pol(va - vb)}; sqrt3 x 230.9 = {S3 * 230.9:.1f}")
    n = 33 / 0.69
    e("E23", f"unit transformer 33/0.69 kV: ratio {n:.2f}; phase voltages "
             f"{33e3 / S3:,.0f} and {690 / S3:.1f} V; 5 MW at pf 0.95: "
             f"{5e6 / (S3 * 33e3 * 0.95):.1f} and {5e6 / (S3 * 690 * 0.95):,.0f} A")
    for kv in (132, 33, 0.69, 0.4):
        zb = kv ** 2 / 100
        ib = 100e6 / (S3 * kv * 1e3)
        e(f"E24-{kv}", f"base 100 MVA, {kv} kV: Z_base = {zb:.4g} ohm, I_base = {ib:,.1f} A")
    e("E24t", f"export transformer 12 % on 120 MVA -> {12 * 100 / 120:.1f} % on 100 MVA")
    zf = complex(0.75, 0.66) / (33 ** 2 / 100)
    e("E24f", f"feeder 0.75 + j0.66 ohm at 33 kV -> {zf.real:.4f} + j{zf.imag:.4f} pu "
              "on 100 MVA")
    z_grid = 100 / 1000
    z_tx = 0.12 * 100 / 120
    e("E25", f"grid 1000 MVA -> z {z_grid:.3f} pu; + transformer {z_tx:.3f} pu = "
             f"{z_grid + z_tx:.3f} pu -> S_sc at 33 kV = {100 / (z_grid + z_tx):.0f} MVA")
    v = ac.balanced_set(230.0)
    i_n_bal = sum(x / 10 for x in v)
    i_n_open = v[0] / 10 + v[1] / 10
    e("E26", f"three 10 ohm loads: I_N = {abs(i_n_bal):.1e} A; phase c load off: "
             f"I_N = {abs(i_n_open):.1f} A (one phase current)")
    vab, vbc, vca = 400.0, 396.0, 404.0
    mean = (vab + vbc + vca) / 3
    nema = max(abs(x - mean) for x in (vab, vbc, vca)) / mean
    beta = (vab ** 4 + vbc ** 4 + vca ** 4) / (vab ** 2 + vbc ** 2 + vca ** 2) ** 2
    u2 = math.sqrt((1 - math.sqrt(3 - 6 * beta)) / (1 + math.sqrt(3 - 6 * beta)))
    # check with phasors: build a triangle with these sides
    a_ang = math.acos((vab ** 2 + vca ** 2 - vbc ** 2) / (2 * vab * vca))
    v_ab = complex(vab, 0)
    v_ca = polar(vca, 180 - math.degrees(a_ang))
    v_bc = -(v_ab + v_ca)
    _, v1, v2 = symmetrical_components(v_ab, v_bc, v_ca)
    e("E27", f"line voltages 400, 396, 404 V: max deviation / mean {100 * nema:.2f} %; "
             f"from magnitudes |V2|/|V1| = {100 * u2:.3f} %; by phasors "
             f"{100 * abs(v2) / abs(v1):.3f} %")
    e("E28", f"meter set to CT 300/5 on a 400/5 CT: shows {300 / 400:.2f} x true "
             f"({100 * (300 / 400 - 1):+.0f} %)")
    v = ac.balanced_set(230.0)
    ia, ib, ic = (x / complex(8, 6) for x in v)
    p = [(vx * ix.conjugate()).real for vx, ix in zip(v, (ia, ib, ic))]
    e("E29", f"three-wattmeter (4-wire) readings {p[0]:.0f}, {p[1]:.0f}, {p[2]:.0f} W; "
             f"sum {sum(p) / 1e3:.2f} kW")


def section_c() -> None:
    s1 = complex(100, 75)
    s2 = complex(50, 0)
    e("E30", f"100 kW pf 0.8 + 50 kW pf 1: S = {abs(s1 + s2):.1f} kVA (P {150:.0f}, "
             f"Q {75:.0f}); |S1| + |S2| = {abs(s1) + abs(s2):.1f} kVA")
    e("E31", "export 100 MW absorbing 20 Mvar: generator convention P +100, Q -20; "
             "load convention at the meter P -100, Q +20")
    q1 = 180 * math.tan(math.acos(0.8))
    q2 = 180 * math.tan(math.acos(0.95))
    e("E32", f"aux 180 kW pf 0.8 (Q {q1:.0f} kvar): to pf 1 Q_c {q1:.0f} kvar; "
             f"a {q1 + q2:.1f} kvar bank would give pf 0.95 leading")
    for name, s_kva, s_r in (("aux 180 kW pf 0.80", 225.0, 250),
                             ("aux 180 kW pf 0.95", 180 / 0.95, 250),
                             ("export 100 MW pf 0.95", 100 / 0.95, 120),
                             ("export 100 MW pf 0.90", 100 / 0.90, 120)):
        e("E33", f"{name}: {s_kva:.1f} of {s_r} -> loading {100 * s_kva / s_r:.0f} %")
    i_r = 5.5e6 / (S3 * 690)
    e("E34", f"5.5 MVA at 690 V: rated current {i_r:.0f} A; at 0.90 pu voltage the same "
             f"current gives {0.9 * 5.5:.2f} MVA")
    th = np.linspace(0, 2 * math.pi, 8192, endpoint=False)
    sq = np.where(np.sin(th) >= 0, 1.0, -1.0)
    amps = signals.harmonic_amplitudes(sq, 41) / math.sqrt(2)
    thd = math.sqrt(math.pi ** 2 / 8 - 1)
    e("E35", f"square wave: fundamental peak {amps[1] * math.sqrt(2):.4f} (4/pi = "
             f"{4 / math.pi:.4f}); THD exact {100 * thd:.2f} %, first 41 orders "
             f"{100 * signals.thd(amps):.2f} %")
    for h in (1, 3, 5, 7, 9, 11, 13):
        shift = (-120 * h) % 360
        seq = {0: "zero", 240: "positive", 120: "negative"}[shift]
        e("E36", f"order {h:2d}: phase b shifted {-120 * h:5d} deg = {shift:3d} deg -> {seq}")
    v5 = 0.05
    i_c = math.sqrt(1 + (5 * v5) ** 2)
    e("E37", f"5 % 5th-harmonic voltage on a capacitor: 5th current {5 * v5:.2f} pu; RMS "
             f"{i_c:.3f} pu")
    energy = 0.312 * 100 * 8760 / 1e3
    e("E38", f"export {energy:.1f} GWh/yr (CF 0.312, ch 5); 0.2 % = "
             f"{0.002 * energy * 1e3:.0f} MWh = {0.002 * energy * 1e3 * 50:,.0f} u at 50 u/MWh")
    e("E39", f"256 samples per cycle at 50 Hz: {256 * 50 / 1e3:.1f} kHz; Nyquist "
             f"{256 * 50 / 2e3:.1f} kHz = order {256 // 2}")
    e("E40", "dip to 166 V (72 %) of 230 V: depth 28 %; 6 cycles at 50 Hz = 0.12 s")


def section_more() -> None:
    # LV feeder of the auxiliary board (A-110): 2 x 240 mm2 Cu per phase, 80 m
    r_km, x_km, length, par = 0.0754, 0.080, 0.080, 2
    r, x = r_km * length / par, x_km * length / par
    i, pf = 252.7, 0.873
    sin = math.sqrt(1 - pf ** 2)
    dv_ph = i * (r * pf + x * sin)
    e("E41", f"aux feeder 2 x 240 mm2, 80 m: R {1000 * r:.2f} mohm, X {1000 * x:.2f} "
             f"mohm per phase; 252.7 A at pf 0.873: drop {dv_ph:.2f} V = "
             f"{100 * dv_ph / 230:.2f} % (three-phase, per phase)")
    e("E42", f"with the 2.48 % of the transformer: about {2.48 + 100 * dv_ph / 230:.1f} % "
             "at the board")
    r1 = 7.41 * 0.050                                   # 2.5 mm2, 50 m, A-110
    dv1 = 2 * 16 * r1
    e("E43", f"lighting circuit 16 A, 50 m of 2.5 mm2 (7.41 ohm/km): go and return "
             f"2 x 16 x {r1:.3f} = {dv1:.1f} V = {100 * dv1 / 230:.1f} %")
    dv3 = 16 * r1
    e("E44", f"same cable as a balanced three-phase circuit, 16 A per phase: "
             f"{dv3:.1f} V per phase = {100 * dv3 / 230:.1f} % (no return drop)")
    for s_sc in (1000, 500, 250):
        e("E45", f"S_sc {s_sc} MVA: dV/dQ ~ 1/S_sc = {100 / s_sc:.2f} % per Mvar; "
                 f"10 Mvar -> {1000 / s_sc:.1f} %")
    i_ds = 4400.0
    s_ds = S3 * 690 * i_ds / 1e6
    v_need = 5.5e6 / (S3 * i_ds)
    e("E46", f"data sheet: 5.5 MVA, 690 V, max current 4400 A -> sqrt3 V I = "
             f"{s_ds:.2f} MVA at 690 V; 5.5 MVA needs {v_need:.0f} V "
             f"({100 * v_need / 690:.1f} % of 690 V)")
    p_r, eff = 5.0, 0.985
    e("E47", f"5.0 MW AC at 98.5 % efficiency needs {p_r / eff:.3f} MW DC; losses "
             f"{1000 * (p_r / eff - p_r):.0f} kW to remove as heat")
    thd, i1 = 0.03, 4184.0
    e("E48", f"current THD 3 % at 4184 A fundamental: harmonics "
             f"{thd * i1:.0f} A RMS; total {i1 * math.sqrt(1 + thd ** 2):.0f} A")
    v = ac.balanced_set(230.0)
    loads = [complex(4.0, 1.5), complex(8.0, 3.0), complex(16.0, 0.0)]
    i3, _, _ = ac.unbalanced_wye(v, loads, 0j)
    s_ph = [vx * ix.conjugate() for vx, ix in zip(v, i3)]
    s_vec = abs(sum(s_ph))
    s_ari = sum(abs(x) for x in s_ph)
    p_tot = sum(x.real for x in s_ph)
    e("E49", f"unbalanced loads of section B: P {p_tot / 1e3:.2f} kW; vector S "
             f"{s_vec / 1e3:.2f} kVA (pf {p_tot / s_vec:.3f}); arithmetic S "
             f"{s_ari / 1e3:.2f} kVA (pf {p_tot / s_ari:.3f})")
    s_led, p_led = 1.436, 1.0
    d_led = math.sqrt(s_led ** 2 - p_led ** 2)
    e("E50", f"LED current, V sinusoidal: S {s_led:.3f}, P {p_led:.3f}, Q1 0, "
             f"distortion power D = sqrt(S^2 - P^2 - Q1^2) = {d_led:.3f} pu")


if __name__ == "__main__":
    section_a()
    section_b()
    section_c()
    section_more()
    emit("worked", OUT)
