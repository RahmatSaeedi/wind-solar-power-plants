"""Chapter 25 - more transformer physics for the reviewer: inrush against
residual flux and switching instant, over-excitation (V/Hz), the extra
winding loss from converter harmonics, the impulse voltage along a
winding, short-circuit pressure on a winding, impedance from the winding
geometry, and eddy loss in the conductor strands.

Run from the project root:   python -m companion.ch25.examples_h
Writes companion/ch25/expected/h_*.txt. Teaching physics (A-326
extended); the maker's design tools and tests decide the real values.
"""
from __future__ import annotations

import math

from companion.ch25 import sources as src
from companion.ch25.common import emit

M = src.MAIN
MU0 = 4e-7 * math.pi
I_HV = M["s_mva"] * 1e6 / (math.sqrt(3) * M["hv_kv"] * 1e3)


def inrush() -> None:
    bn, bs, x_air = 1.7, 2.03, 0.30
    lines = ["inrush on energising from the 132 kV side (teaching estimate):",
             "  i_peak = sqrt2 In / x_air x (2 Bn + Br - Bs) / Bn",
             f"  In {I_HV:.0f} A, Bn {bn} T, Bs {bs} T, air-core reactance {x_air} pu",
             "  residual flux    switched at voltage zero    peak A    x rated rms"]
    for br_frac in (0.0, 0.4, 0.8):
        br = br_frac * bn
        k = max(2 * bn + br - bs, 0) / bn
        ipk = math.sqrt(2) * I_HV / x_air * k
        lines.append(f"  {br_frac:5.1f} x Bn       worst case                  {ipk:6.0f}"
                     f"    {ipk / I_HV:10.1f}")
    lines += ["  switched at the voltage peak the flux starts symmetric and",
              "  there is almost no inrush; at the zero with residual flux",
              "  of the same sign the core saturates for many cycles - the",
              "  current decays over seconds and is rich in the 2nd",
              "  harmonic (the differential's blocking, ch 26); a second",
              "  transformer already in service can draw a 'sympathetic'",
              "  inrush; controlled switching at the right instant is an",
              "  option the utility may ask for"]
    emit("h_inrush", lines)


def overexcitation() -> None:
    lines = ["over-excitation: flux follows V/f (teaching core, 1.7 T rated):",
             "  V/f pu   flux T   core loss x   magnetising current x"]
    for k in (1.00, 1.05, 1.10, 1.15, 1.20):
        b = 1.7 * k
        lines.append(f"  {k:6.2f}   {b:6.2f}   {k ** 2:11.2f}   {math.exp(8 * (b - 1.7)):21.1f}")
    lines += ["  above about 1.1 the core runs into saturation: the loss and",
              "  the magnetising current grow fast, flux leaks into the tank",
              "  and the clamps and heats them - high voltage at the plant",
              "  end of a long line, or low frequency in an island, does it;",
              "  a V/Hz protection (24) with a time curve from the maker",
              "  guards it, and the plant's voltage control keeps away from it"]
    emit("h_overexc", lines)


def harmonics() -> None:
    p_ec = 0.08
    spectra = {"modern converters": {5: 0.03, 7: 0.02, 11: 0.012, 13: 0.008},
               "a poor or resonant case": {5: 0.08, 7: 0.05, 11: 0.03, 13: 0.02}}
    lines = ["extra winding loss from converter harmonics (teaching):",
             "  F_HL = sum (Ih/I1)^2 h^2 / sum (Ih/I1)^2; eddy share of load",
             f"  loss {p_ec:.0%}",
             "  spectrum                    F_HL    load loss up   kW at 250 kW"]
    for name, sp in spectra.items():
        s2 = 1 + sum(v * v for v in sp.values())
        s2h = 1 + sum(v * v * h * h for h, v in sp.items())
        fhl = s2h / s2
        up = p_ec * (fhl - 1)
        lines.append(f"  {name:26s} {fhl:5.3f}   {up:12.1%}   {up * M['pk_kw']:12.1f}")
    lines += ["  today's converters add little; a resonance that amplifies",
              "  one harmonic (ch 27) can add several per cent - the",
              "  transformer specification states the expected spectrum so",
              "  the maker can design the windings and stray-loss shields"]
    emit("h_harmonics", lines)


def impulse() -> None:
    discs, bil = 80, 650.0
    lines = ["initial impulse voltage along a disc winding (neutral earthed):",
             "  u(x) / U = sinh(a (1 - x)) / sinh(a); first disc gets about a / N",
             f"  {discs} discs, {bil:.0f} kV impulse",
             "  alpha   first disc kV   x uniform   winding type"]
    for a, kind in ((10.0, "plain disc"), (5.0, "partly interleaved"), (2.5, "interleaved")):
        first = bil * (1 - math.sinh(a * (1 - 1 / discs)) / math.sinh(a))
        lines.append(f"  {a:5.1f}   {first:13.0f}   {first / (bil / discs):9.1f}   {kind}")
    lines += ["  a steep impulse first divides by capacitance, not by turns:",
              "  the line-end discs carry many times their share; interleaving",
              "  the turns raises the series capacitance and lowers alpha -",
              "  why the line end of an HV winding is built differently, and",
              "  why the impulse test (lesson C) is a type and routine",
              "  evidence the reviewer reads, not a site trial"]
    emit("h_impulse", lines)


def forces() -> None:
    n, i_ph, h, r_mean, build = 194, 636.0, 1.5, 0.55, 0.06
    lines = ["short-circuit pressure on the 33 kV winding (teaching geometry):",
             "  B = mu0 N i / h; pressure p = B^2 / (2 mu0); hoop stress p r / t",
             "  uk %   peak pu   peak kA   B T    p MPa   hoop MPa (60 % Cu)"]
    for uk in (12.0, 10.0, 8.0):
        ik_pu = 100 / uk
        ip_pu = 1.9 * math.sqrt(2) * ik_pu
        ip = ip_pu * i_ph
        b = MU0 * n * ip / h
        p = b * b / (2 * MU0) / 1e6
        hoop = p * r_mean / (build * 0.6)
        lines.append(f"  {uk:4.0f}   {ip_pu:7.1f}   {ip / 1e3:7.1f}   {b:4.2f}   {p:5.2f}   {hoop:17.1f}")
    lines += ["  the force grows with the square of the fault current: a",
              "  lower impedance (less voltage drop, smaller losses) costs",
              "  winding strength - the impedance of lesson A is chosen with",
              "  the forces in view; the inner winding is pressed inward and",
              "  must not buckle - the short-circuit withstand is proved by",
              "  the maker's test or calculation evidence"]
    emit("h_forces", lines)


def impedance() -> None:
    n, i_ph, v_t, d_m, h, a1, a2 = 194, 636.0, 169.8, 1.10, 1.50, 0.06, 0.09
    lines = ["impedance from the winding geometry (teaching formula):",
             "  ux = 2 pi f mu0 pi Dm N I / (h Vt) x (a12 + (a1 + a2) / 3)",
             f"  N {n}, I {i_ph:.0f} A, Vt {v_t} V, Dm {d_m} m, h {h} m,"
             f" a1 {a1} m, a2 {a2} m",
             "  gap a12 m   height h m   ux %"]
    for a12, hh in ((0.130, 1.50), (0.153, 1.50), (0.130, 1.35)):
        ux = 2 * math.pi * 50 * MU0 * math.pi * d_m * n * i_ph / (hh * v_t) * (a12 + (a1 + a2) / 3)
        lines.append(f"  {a12:9.3f}   {hh:10.2f}   {ux * 100:4.1f}")
    lines += ["  the leakage flux lives in the gap and the windings: a wider",
              "  gap or a shorter winding raises the impedance - the 13.4 %",
              "  of the test dossier (lesson D) is about 23 mm more gap or a",
              "  winding about 11 % shorter than designed; the maker's",
              "  calculation predicts it within a few per cent, and the",
              "  contract tolerance closes the rest"]
    emit("h_impedance", lines)


def eddy() -> None:
    share_25 = 0.10
    lines = ["eddy loss in the winding strands grows with thickness squared:",
             "  strand mm   eddy share of load loss   load loss kW   value k u (B 0.88)"]
    base = M["pk_kw"] / (1 + share_25)
    for t in (2.5, 1.8, 1.2):
        share = share_25 * (t / 2.5) ** 2
        pk = base * (1 + share)
        lines.append(f"  {t:9.1f}   {share:23.1%}   {pk:12.1f}   {(M['pk_kw'] - pk) * 0.88:18.1f}")
    lines += ["  thin strands, transposed along the winding (continuously",
              "  transposed cable), cut the eddy loss and the hot spots it",
              "  makes; the saving is priced with the B factor of lesson A -",
              "  the reason loss evaluation reaches into the winding design"]
    emit("h_eddy", lines)


if __name__ == "__main__":
    inrush()
    overexcitation()
    harmonics()
    impulse()
    forces()
    impedance()
    eddy()
