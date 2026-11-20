"""Chapter 27 - expansion round 11: how the 33 kV resonance moves as
converters (each with its own filter capacitor) come online, and the
harmonic voltage on the plant's own 400 V auxiliary board from its
HVAC drives.

Run from the project root:   python -m companion.ch27.examples_z
Writes companion/ch27/expected/z_*.txt and diagrams/data/ch27-units.csv.
Teaching values (A-336, A-337).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch27 import sources as src
from companion.ch27.common import csv, emit
from plantp import pq

Q_UNIT = 0.15            # Mvar of filter capacitance per converter (teaching)


def resonance_units() -> None:
    n = src.NET
    total = sum(src.UNITS.values())
    rows, lines = [], ["the 33 kV resonance against converters online (cables 1.77 Mvar,",
                       f"  {Q_UNIT} Mvar of filter capacitance per converter; grid 365 MVA, X/R 10)",
                       "  online   C Mvar   resonance h   amplification at 11th   at 13th"]
    h = np.array([11.0, 13.0])
    for k in range(total + 1):
        q = n["q_cables"] + k * Q_UNIT
        hr = math.sqrt(n["s_sc_33"] / q)
        z = pq.scan(h, n["s_sc_33"], n["xr_33"], q, n["kv_33"])
        zg = pq.scan(h, n["s_sc_33"], n["xr_33"], 1e-9, n["kv_33"])
        amp = z / zg
        rows.append((k, f"{hr:.2f}", f"{amp[0]:.2f}", f"{amp[1]:.2f}"))
        if k in (0, 3, 8, 16, 26):
            lines.append(f"  {k:6d}   {q:6.2f}   {hr:11.2f}   {amp[0]:21.1f}   {amp[1]:7.1f}")
    csv("ch27-units.csv", "n,hr,a11,a13", rows)
    lines += ["  the resonance falls from the 14th (nothing online) to the",
              "  8th (all 26 online); with about 3 units online it sits on",
              "  the 13th and with about 8 on the 11th - low-output hours",
              "  with few units running are the risky ones, so the scan is",
              "  run for every unit count, not only 'all online'"]
    emit("z_units", lines)


def aux_board() -> None:
    s_sst, uk = 250.0, 0.04
    spectra = {"6-pulse, no choke": {5: 0.70, 7: 0.50, 11: 0.12, 13: 0.08},
               "6-pulse, DC choke": {5: 0.35, 7: 0.20, 11: 0.08, 13: 0.06},
               "active front end": {5: 0.03, 7: 0.02, 11: 0.01, 13: 0.01}}
    lines = ["voltage THD on the 400 V auxiliary board fed by the 250 kVA station",
             "  transformer (uk 4 %) from the HVAC drives (current % of fundamental)",
             "  drive type            drives kW   voltage THD %"]
    for name, sp in spectra.items():
        for kw in (60.0, 160.0):
            i1 = kw / s_sst
            vh = {h: i1 * c * h * uk for h, c in sp.items()}
            thd = 100 * math.sqrt(sum(v * v for v in vh.values()))
            lines.append(f"  {name:20s}  {kw:9.0f}   {thd:13.1f}")
    lines += ["  the plant's own drives distort its own control supply: a",
              "  PQ question inside the fence, separate from the POC; the",
              "  drive type is chosen with the board's short-circuit level",
              "  (ch 23), and the battery HVAC of S1 makes it larger"]
    emit("z_aux", lines)


if __name__ == "__main__":
    resonance_units()
    aux_board()
