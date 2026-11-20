"""Chapter 25, section A - transformer theory and specification for
Plant P's 63 MVA units: volts per turn and turns, the equivalent circuit
from the test data, regulation, efficiency over the load range, the
phase shift of YNd11, the tap range, load sharing in parallel, inrush,
and the short-circuit current and force.

Run from the project root:   python -m companion.ch25.examples_a
Writes companion/ch25/expected/a_*.txt and diagrams/data/ch25-*.csv.
Teaching values A-326 to A-330.
"""
from __future__ import annotations

import math

from companion.ch25 import sources as src
from companion.ch25.common import csv, emit
from plantp import transformer as tr

M = src.MAIN


def faraday() -> None:
    lines = ["volts per turn and turns of the 63 MVA unit (teaching core):",
             "  B peak T   core m2   V/turn   HV turns (76.2 kV)   LV turns (33 kV)"]
    for b, a in ((1.6, 0.45), (1.7, 0.45), (1.7, 0.40)):
        vpt = tr.volts_per_turn(b, a)
        lines.append(f"  {b:7.1f}   {a:7.2f}   {vpt:6.1f}   {tr.turns(132e3 / math.sqrt(3), b, a):18.0f}"
                     f"   {tr.turns(33e3, b, a):16.0f}")
    i_lv = M["s_mva"] * 1e6 / (3 * 33e3)                 # delta winding current
    lines += [f"  LV delta winding current {i_lv:,.0f} A; at 3 A/mm2: {tr.conductor_mm2(i_lv, 3.0):,.0f} mm2",
              "  higher flux density means fewer turns and a smaller core",
              "  but more core loss and noise and less margin against",
              "  over-excitation: the maker's choice, checked in review"]
    emit("a_faraday", lines)


def circuit() -> None:
    e = tr.from_tests(M["s_mva"] * 1e3, M["hv_kv"], M["p0_kw"], M["i0_pct"],
                      M["pk_kw"], M["uk_pct"])
    lines = ["equivalent circuit from the tests (per unit on 63 MVA):",
             f"  series r {e['r']:.5f}, x {e['x']:.5f}, z {e['z']:.3f} (x/r {e['x'] / e['r']:.0f})",
             f"  shunt g {e['g']:.6f}, b {e['b']:.6f}",
             "  regulation and efficiency at full load:",
             "  pf      regulation %   efficiency %"]
    for pf in (1.0, 0.95, 0.9):
        lines.append(f"  {pf:4.2f}   {tr.regulation_pct(e['r'], e['x'], 1.0, pf):12.2f}"
                     f"   {tr.efficiency(1.0, 63000, pf, M['p0_kw'], M['pk_kw']) * 100:12.3f}")
    k_best = math.sqrt(M["p0_kw"] / M["pk_kw"])
    rows = [(f"{k:.2f}", f"{tr.efficiency(k, 63000, 1.0, M['p0_kw'], M['pk_kw']) * 100:.3f}")
            for k in [x / 20 for x in range(1, 25)]]
    csv("ch25-efficiency.csv", "load,eta", rows)
    lines += [f"  efficiency is highest where load loss = no-load loss: at"
              f" {k_best:.2f} of rating",
              "  the regulation is mostly the reactance: at pf 1 the",
              "  voltage falls little, at pf 0.9 lagging it falls ~6 %,",
              "  which the tap changer and the plant's reactive power absorb"]
    emit("a_circuit", lines)


def vector() -> None:
    lines = ["vector group YNd11 (clock notation, teaching):",
             "  HV star with an earthed neutral (YN), LV delta (d), and",
             "  the LV voltage at 11 o'clock against HV at 12: it leads",
             "  by 30 degrees",
             "  consequences on the one-line (ch 23):",
             "    - the 132 kV neutral can be earthed; the 33 kV side needs",
             "      earthing transformers (no neutral on a delta)",
             "    - two transformers in parallel need the same group;",
             "      a d1 unit beside a d11 would short a 60-degree shift",
             "    - protection and metering CTs see the 30-degree shift and",
             "      the relay compensates it (ch 26)"]
    emit("a_vector", lines)


def taps() -> None:
    lo, hi, step = M["taps"]
    n = int(round((hi - lo) / step)) + 1
    lines = [f"on-load tap changer {lo:+.0f} % to {hi:+.0f} % in {step} % steps: {n} positions",
             "  HV voltage seen at each end of the range for 33 kV on the LV:"]
    for t in (lo, 0.0, hi):
        lines.append(f"    tap {t:+6.2f} %: LV 33 kV at HV {132 * (1 + t / 100):6.1f} kV")
    lines += ["  the range covers the grid's voltage band at the POC and the",
              "  regulation across the transformer (above); the range and",
              "  steps are fixed with the grid study (ch 28) - an open item",
              "  of the specification until then"]
    emit("a_taps", lines)


def parallel() -> None:
    lines = ["two 63 MVA units in parallel (coupler closed), 100 MVA load:"]
    for z2 in (0.12, 0.13, 0.15):
        s = tr.share(100, [63, 63], [0.12, z2])
        lines.append(f"  z 12 % and {z2 * 100:4.1f} %: {s[0]:5.1f} and {s[1]:5.1f} MVA"
                     f"  ({s[0] / 63:.0%} and {s[1] / 63:.0%} of rating)")
    full = tr.share(126, [63, 63], [0.12, 0.15])
    lines += [f"  at 126 MVA (both ratings) with 12 % and 15 %: {full[0]:.1f} and"
              f" {full[1]:.1f} MVA",
              f"    - the first is at {full[0] / 63:.0%} before the pair is full",
              "  the lower impedance takes more load; equal ratio, vector",
              "  group and close impedances are conditions of parallel",
              "  operation (Plant P runs them split, ch 23)"]
    emit("a_parallel", lines)


def fault_inrush() -> None:
    i_hv = tr.sc_current_ka(63, 33, 0.12)
    lines = ["short circuit and inrush of the 63 MVA unit (infinite bus):",
             f"  fault on the 33 kV terminals: {i_hv:.1f} kA = {1 / 0.12:.1f} x rated",
             f"  force on the windings ~ I^2: {tr.force_ratio(0.12):.0f} x the rated-current force"
             " (x peak factor^2)",
             "  inrush on energising: a few times to over ten times rated",
             "  current for some cycles, decaying over seconds, rich in",
             "  the 2nd harmonic - the protection must not trip on it (ch 26)",
             "  the windings and clamping are designed and type-proved for",
             "  the short-circuit force; the specification states the",
             "  fault level the transformer must withstand (ch 23 faults)"]
    emit("a_fault", lines)


if __name__ == "__main__":
    faraday()
    circuit()
    vector()
    taps()
    parallel()
    fault_inrush()
