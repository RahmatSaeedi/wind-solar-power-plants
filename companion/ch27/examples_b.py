"""Chapter 27, section B - the plant's causes and responses: summation of
the units' harmonic currents, the frequency scan of the 33 kV bus with
cables, a capacitor bank and a tuned filter, the filter's design, the
effect of power factor on current (worked example 1), a weak grid, and
the reactive capability at the POC.

Run from the project root:   python -m companion.ch27.examples_b
Writes companion/ch27/expected/b_*.txt and diagrams/data/ch27-*.csv.
Teaching values A-336 to A-340.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch27 import sources as src
from companion.ch27.common import csv, emit
from plantp import ac
from plantp import pq

N = src.NET


def summation() -> None:
    i_unit_33 = 5.5e6 / (math.sqrt(3) * 33e3)          # one unit's rated current at 33 kV
    lines = ["5th-harmonic current of the 26 units at the 33 kV side (teaching):",
             "  summation               exponent   5th A   % of plant current"]
    currents = [src.EMISSION[k][5] / 100 * i_unit_33 for k, n in src.UNITS.items() for _ in range(n)]
    i_plant = 26 * i_unit_33
    for name, a in (("all in phase", 1.0), ("partly random", 1.4), ("fully random", 2.0)):
        s = pq.summation(currents, a)
        lines.append(f"  {name:23s} {a:8.1f}   {s:5.1f}   {100 * s / i_plant:18.2f}")
    lines += ["  identical converters with the same control and the same",
              "  operating point emit low-order harmonics nearly in phase;",
              "  higher orders mix more randomly - the assessment report",
              "  (STD-130) uses summation exponents between these limits;",
              "  the in-phase sum is the safe first screening, the measured",
              "  plant emission replaces it"]
    emit("b_summation", lines)


def frequency_scan() -> None:
    h = np.arange(1.0, 25.0, 0.05)
    z_cab = pq.scan(h, N["s_sc_33"], N["xr_33"], N["q_cables"], N["kv_33"])
    z_cap = pq.scan(h, N["s_sc_33"], N["xr_33"], N["q_cables"] + 5.0, N["kv_33"])
    f = src.FILTER
    z_fil = pq.scan(h, N["s_sc_33"], N["xr_33"], N["q_cables"], N["kv_33"],
                    (f["q_mvar"], f["h_tune"], f["quality"]))
    csv("ch27-scan.csv", "h,cables,capacitor,filter",
        [(f"{a:.2f}", f"{b:.2f}", f"{c:.2f}", f"{d:.2f}") for a, b, c, d in zip(h, z_cab, z_cap, z_fil)])
    z1 = N["kv_33"] ** 2 / N["s_sc_33"]
    lines = ["frequency scan of the 33 kV bus (grid 365 MVA, X/R 10, cables 1.77 Mvar;",
             "  no load damping in this teaching model, so the peaks are sharp):",
             "  case                         resonances at h   at 5th ohm   at 7th ohm"]
    for name, z in (("cables only", z_cab), ("plus 5 Mvar capacitor bank", z_cap),
                    ("plus 5 Mvar filter at 4.7th", z_fil)):
        peaks = [h[k] for k in range(1, len(h) - 1) if z[k] > z[k - 1] and z[k] > z[k + 1] and z[k] > 30]
        at5 = z[np.argmin(np.abs(h - 5))]
        at7 = z[np.argmin(np.abs(h - 7))]
        txt = ", ".join(f"{x:.1f}" for x in peaks)
        lines.append(f"  {name:28s} {txt:>15s}   {at5:10.1f}   {at7:10.1f}")
    lines += [f"  the grid alone would show {z1:.2f} ohm x h; cable capacitance makes a",
              f"  parallel resonance near h = sqrt(365/1.77) = {ac.resonance_order(365, 1.77):.1f};",
              "  a plain capacitor bank for power factor pulls it down to the",
              "  7th, where the units emit: a 5th or 7th current there sees",
              "  many times the grid impedance - the classic trap; a filter",
              "  tuned below the 5th gives the same Mvar and a low impedance",
              "  at 5 and 7; it creates a new resonance below its tuning,",
              "  where the units emit little, and pushes the cable one up"]
    emit("b_scan", lines)


def filter_design() -> None:
    f = src.FILTER
    c, l_mh, xc, xl = pq.tuned_filter(f["q_mvar"], f["h_tune"], N["kv_33"])
    lines = [f"single-tuned filter: {f['q_mvar']} Mvar at 33 kV, tuned to h = {f['h_tune']}",
             f"  X_C = {xc:.1f} ohm, X_L = {xl:.2f} ohm per phase (star equivalent)",
             f"  C = {c:.2f} uF, L = {l_mh:.1f} mH per phase",
             "  capacitor tolerance   tuned to h"]
    for tol in (-f["cap_tol"], 0.0, f["cap_tol"]):
        lines.append(f"  {tol:+19.0%}   {f['h_tune'] / math.sqrt(1 + tol):10.2f}")
    v_c = 1 + 1 / (f["h_tune"] ** 2 - 1)
    lines += [f"  the capacitor sees {v_c:.3f} x the bus voltage at 50 Hz (the reactor's",
              "  rise), plus its harmonic duty: it is rated for both; tuned",
              "  a little below the 5th, the filter never sits exactly on a",
              "  harmonic even with tolerance and ageing (capacitance falls",
              "  with failed elements and the tuning rises toward the 5th)"]
    emit("b_filter", lines)


def pf_current() -> None:
    p, v = 100e6, 132e3
    r_line = 0.12 * 7.06
    lines = ["worked example 1: power factor and current at the POC (100 MW)",
             "  pf     current A   line loss kW   reactive Mvar   vs 437 A at pf 1"]
    for pf in (1.0, 0.95, 0.9, 0.85):
        i = ac.line_current_a(p, v, pf)
        loss = 3 * i * i * r_line / 1e3
        q = p / 1e6 * math.tan(math.acos(pf))
        lines.append(f"  {pf:4.2f}   {i:9.0f}   {loss:12.0f}   {q:13.1f}   {i / ac.line_current_a(p, v, 1.0) - 1:+15.1%}")
    lines += ["  the same active power at pf 0.9 needs 11 % more current",
              "  and 23 % more line loss; on a hot, still day the line's",
              "  rating (ch 24: 419 A at 45 C and 0.6 m/s) is already below",
              "  437 A - every Mvar the plant is asked to export or absorb",
              "  at full power deepens the curtailment; the reactive",
              "  requirement and the line rating are read together"]
    emit("b_pf", lines)


def weak_grid() -> None:
    lines = ["grid strength at the POC (short-circuit ratio SCR = S_sc / P_plant):",
             "  case                         S_sc MVA   SCR    dU per 10 Mvar %"]
    for name, s in (("normal (ch 17)", 1500.0), ("one grid line out", 600.0), ("weak corner", 300.0),
                    ("very weak", 200.0)):
        du = pq.voltage_change(0.0, 10.0, s, 8.0)
        lines.append(f"  {name:28s} {s:8.0f}   {s / 100:4.1f}   {100 * du:16.2f}")
    lines += ["  the weaker the grid, the more each Mvar moves the voltage:",
              "  controller gains tuned for SCR 15 can oscillate at SCR 3;",
              "  converters that follow the grid (a phase-locked loop) need",
              "  a voltage to lock on - at low SCR their own current moves",
              "  it, and interactions appear; the operator's weak-grid study",
              "  (ch 28) tests the plant's models at the weakest case"]
    emit("b_weak", lines)


def capability() -> None:
    s_units = 22 * 5.5                                   # PV and wind units, MVA
    rows = []
    lines = ["reactive capability at the POC (S0: 22 units of 5.5 MVA; teaching):",
             "  P MW   units Mvar   transformers+line Mvar   at POC Mvar   pf at POC"]
    for p in (10, 25, 50, 75, 100):
        q_u = ac.q_capability(s_units, p)
        s_t = p / 0.95 / 2
        loss = 2 * 0.12 * s_t ** 2 / 63 + 3 * (p / 0.95 * 1e6 / (math.sqrt(3) * 132e3)) ** 2 * 7.06 * 0.40 / 1e6
        q_poc = q_u - loss
        pf = p / math.hypot(p, q_poc)
        rows.append((p, f"{q_poc:.1f}"))
        lines.append(f"  {p:4d}   {q_u:10.1f}   {loss:22.1f}   {q_poc:11.1f}   {pf:9.3f}")
    csv("ch27-capability.csv", "p,q", rows)
    lines += ["  at full power the units give 68 Mvar but the transformers",
              "  and the line take 12: about 56 Mvar reaches the POC - more",
              "  than a 0.95 requirement (33 Mvar) asks; the requirement is",
              "  checked at the POC with the losses in between, and at the",
              "  edges of the voltage band (ch 28), not at the terminals"]
    emit("b_capability", lines)


if __name__ == "__main__":
    summation()
    frequency_scan()
    filter_design()
    pf_current()
    weak_grid()
    capability()
