"""Chapter 27 - expansion round 7: the turbines' 3p power modulation
against the eye's flicker sensitivity, a capacitive VT's error at
harmonic orders, how Q(U) control narrows the voltage spread at the POC,
and an on-site check of a PQ instrument with a reference signal.

Run from the project root:   python -m companion.ch27.examples_u
Writes companion/ch27/expected/u_*.txt and diagrams/data/ch27-vspread.csv.
Teaching values (A-336 to A-340).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch27.common import csv, emit
from plantp import pq


def three_p() -> None:
    lines = ["the turbines' 3p power modulation (tower passage) at the POC (teaching)",
             "  rotor rpm   3p Hz   12 turbines, 2 % each, random phases: dP MW   dU %",
             ]
    for rpm in (8, 12, 14):
        f3p = 3 * rpm / 60
        dp = 5.0 * 0.02 * math.sqrt(12)
        du = 100 * pq.voltage_change(dp, 0.0, 1500.0, 8.0)
        lines.append(f"  {rpm:9d}   {f3p:5.2f}   {dp:44.2f}   {du:5.3f}")
    lines += ["  the eye is most sensitive to lamp flicker near 8.8 Hz and",
              "  much less below 1 Hz; three thousandths of a per cent at",
              "  0.4-0.7 Hz is far below anything a flickermeter would rank",
              "  (STD-129) - which is why the flicker coefficient (lesson",
              "  A) of modern turbines is small; synchronised turbines (all",
              "  in phase) would add linearly - the sqrt(12) assumes they",
              "  are not"]
    emit("u_3p", lines)


def cvt_response() -> None:
    h_r = 10.0
    lines = ["a capacitive VT's ratio error at harmonic orders (teaching resonance",
             "  near the 10th): |H(h)| = 1 / |1 - (h / h_r)^2|",
             "  order   gain   true 1.0 % reads as"]
    for h in (3, 5, 7, 11, 13, 17):
        g = 1 / abs(1 - (h / h_r) ** 2)
        lines.append(f"  {h:5d}   {g:4.2f}   {g:17.2f} %")
    lines += ["  near its own resonance the CVT reads several times too high,",
              "  far above it (beyond the 14th here) too low - depending on",
              "  where that resonance lies;",
              "  a value from a CVT is not a harmonic measurement unless the",
              "  transducer has been characterised at that order"]
    emit("u_cvt", lines)


def spread() -> None:
    rng = np.random.default_rng(283)
    n = 1008
    grid = np.clip(1.0 + np.cumsum(rng.normal(0, 0.002, n)), 0.90, 1.10)
    k = 0.33 / 0.05                                   # pu Mvar per pu volt, on 100 MVA (teaching)
    s_sc = 15.0                                       # pu on 100 MVA
    rows, results = [], {}
    for name, droop in (("no voltage control", 0.0), ("Q(U) 33 Mvar per 5 %", k)):
        v = 1 + (grid - 1) / (1 + droop / s_sc)       # quasi-steady sensitivity
        results[name] = v
    for a, b, c in zip(range(n), results["no voltage control"], results["Q(U) 33 Mvar per 5 %"]):
        if a % 4 == 0:
            rows.append((a, f"{b:.4f}", f"{c:.4f}"))
    csv("ch27-vspread.csv", "k,free,qu", rows)
    lines = ["voltage at the POC over a week with and without Q(U) control",
             "  (grid voltage wandering; SCR 15; teaching quasi-steady model)",
             "  case                        5th pct   95th pct   spread pu"]
    for name, v in results.items():
        lo, hi = np.percentile(v, [5, 95])
        lines.append(f"  {name:27s} {lo:7.3f}   {hi:8.3f}   {hi - lo:9.3f}")
    lines += ["  with SCR 15 the plant's reactive power moves the POC voltage",
              "  modestly: Q(U) narrows the spread by about a third; on a",
              "  weaker grid the same droop does more, and its gain must be",
              "  checked for stability there (lesson B, weak grid)"]
    emit("u_spread", lines)


def onsite_check() -> None:
    ref = {"U1 %": 100.0, "U5 %": 2.00, "U7 %": 1.00, "Pst": 1.00, "f Hz": 50.000}
    read = {"U1 %": 100.05, "U5 %": 2.04, "U7 %": 0.99, "Pst": 1.03, "f Hz": 50.002}
    tol = {"U1 %": 0.1, "U5 %": 0.05, "U7 %": 0.05, "Pst": 0.05, "f Hz": 0.01}
    lines = ["on-site check of a PQ instrument with a reference source (teaching)",
             "  quantity   reference   reading   tolerance   result"]
    for k in ref:
        ok = abs(read[k] - ref[k]) <= tol[k]
        lines.append(f"  {k:8s}   {ref[k]:9.3f}   {read[k]:7.3f}   +/- {tol[k]:5.3f}   {'pass' if ok else 'FAIL'}")
    lines += ["  the check proves the instrument on site, not the",
              "  transducers - those need their own data (lesson A); the",
              "  record joins the calibration certificate in the dossier"]
    emit("u_onsite", lines)


if __name__ == "__main__":
    three_p()
    cvt_response()
    spread()
    onsite_check()
