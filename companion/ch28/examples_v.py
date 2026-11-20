"""Chapter 28 - expansion round 11: the plant's reactive capability at
full output against a voltage-dependent requirement (a teaching U-Q/Pmax
profile), and the plant's own trip as a contingency for the grid.

Run from the project root:   python -m companion.ch28.examples_v
Writes companion/ch28/expected/v_*.txt and diagrams/data/ch28-uq.csv.
Teaching profile, placeholder for the operator's (U-102).
"""
from __future__ import annotations

import numpy as np

from companion.ch28 import sources as src
from companion.ch28.common import csv, emit
from plantp import gridstudy as gs

FULL = {"wind": 1.0, "pv": 0.84}


def required(u: float) -> tuple:
    """Teaching profile of Q/Pmax that must be available at POC voltage u:
    +0.33 up to 1.00 pu falling to 0 at 1.10; -0.33 from 1.00 pu,
    falling to 0 at 0.90."""
    give = 0.33 if u <= 1.0 else max(0.0, 0.33 * (1.10 - u) / 0.10)
    absorb = -0.33 if u >= 1.0 else min(0.0, -0.33 * (u - 0.90) / 0.10)
    return give, absorb


def uq_profile() -> None:
    lines = ["reactive capability at full output against a teaching U-Q/Pmax profile",
             "  (grid min; the requirement is read at the POC voltage the grid",
             "  sets with Q = 0, then the plant's limit is computed there)",
             "  source   U POC at Q=0   give Q/Pmax  need   absorb Q/Pmax  need   ok"]
    rows = []
    for e in (0.92, 0.95, 1.00, 1.05, 1.08):
        u0 = src.q_for_target(FULL, 0.0, grid="min", e=e)[1]["v"][1]
        hi = src.q_limits(FULL, 1, grid="min", e=e)
        lo = src.q_limits(FULL, -1, grid="min", e=e)
        qh, ql = hi["s_poc"].imag / 100, lo["s_poc"].imag / 100
        nh, nl = required(u0)
        ok = qh >= nh - 1e-9 and ql <= nl + 1e-9
        lines.append(f"  {e:6.2f}   {u0:12.3f}   {qh:11.2f}  {nh:4.2f}   {ql:13.2f}  {nl:5.2f}"
                     f"   {'yes' if ok else 'NO'}")
        rows.append((f"{u0:.3f}", f"{qh:.3f}", f"{u0:.3f}", f"{ql:.3f}"))
    csv("ch28-uq.csv", "uh,qh,ul,ql", rows)
    prof = [(f"{u:.3f}", f"{required(u)[0]:.3f}", f"{required(u)[1]:.3f}")
            for u in np.linspace(0.88, 1.12, 49)]
    csv("ch28-uqreq.csv", "u,give,absorb", prof)
    lines += ["  at every swept voltage the plant meets the teaching profile",
              "  in both directions at 25 C (lesson F shows the hot day);",
              "  the profile's shape, not one number, is the requirement -",
              "  the operator's own profile replaces this one (U-102)"]
    emit("v_uq", lines)


def plant_as_contingency() -> None:
    t = np.arange(0, 30, 0.01)
    lines = ["the plant's own trip at 100 MW as an event for the grid",
             "  system                         nadir Hz   RoCoF Hz/s",
             ]
    for name, s, h in (("large (20 GW, H 4)", 20000, 4.0), ("small (2 GW, H 3)", 2000, 3.0)):
        o = gs.freq_event(t, s, h, 100.0, gov=(0.05, 6.0, 0.2))
        lines.append(f"  {name:29s}  {o['nadir']:8.3f}   {o['rocof']:10.3f}")
    lines += ["  on the small system the plant is a large infeed: losing it",
              "  costs almost a hertz - the operator compares the",
              "  plant's size with the largest loss the system is planned",
              "  for, and may limit export or ask for a slower trip of",
              "  the units (ramped disconnection) where the code allows"]
    emit("v_contingency", lines)


if __name__ == "__main__":
    uq_profile()
    plant_as_contingency()
