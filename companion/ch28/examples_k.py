"""Chapter 28 - expansion round 2: an earth fault at the POC with and
without the plant's earthed transformer stars, the peak fault current
against the switchgear's making rating, and the line's auto-reclose
against how fast the plant leaves an island.

Run from the project root:   python -m companion.ch28.examples_k
Writes companion/ch28/expected/k_*.txt. Teaching values (A-341, A-346).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch28 import sources as src
from companion.ch28.common import emit
from plantp import gridstudy as gs

K0_GRID, K0_LINE = 1.5, 3.0          # zero- to positive-sequence ratios (A-346)


# [start: earth]
def earth_fault(z1: complex, z0: complex, c: float = 1.1) -> complex:
    """Single-phase-to-earth fault current (pu) from sequence impedances
    at the fault: 3 c / (Z1 + Z2 + Z0), with Z2 = Z1."""
    return 3 * c / (2 * z1 + z0)


def par(a: complex, b: complex) -> complex:
    return a * b / (a + b)
# [end: earth]


def earth() -> None:
    zb = 132.0 ** 2 / src.S_BASE
    ib = src.S_BASE / (math.sqrt(3) * 132) * 1e3          # A
    z1g = gs.thevenin(src.GRID["max"]["s_sc"], src.GRID["max"]["xr"])
    z0g = K0_GRID * z1g
    z1l = complex(src.LINE["r"], src.LINE["x"]) * src.LINE["km"] / zb
    zt = complex(0.0063, 0.1905)                            # one main transformer
    z0_plant = K0_LINE * z1l + zt / 2                      # two YN stars in parallel
    cases = [("plant transformers' stars unearthed", z0g),
             ("both stars earthed (YNd11 as built)", par(z0g, z0_plant))]
    lines = ["single-phase fault at the POC (grid max; sequence ratios teaching, A-346)",
             "  case                                   I fault kA   in plant neutrals"]
    for name, z0 in cases:
        i_f = earth_fault(z1g, z0) * ib / 1e3
        share = abs(z0 / z0_plant) if "earthed" in name and "un" not in name else 0.0
        lines.append(f"  {name:38s} {abs(i_f):10.2f}   {abs(i_f) * share:14.2f} kA")
    lines += ["  the plant's earthed stars are a zero-sequence source even",
              "  when the plant produces nothing: they raise the earth-fault",
              "  current at the POC and carry part of it in their neutrals",
              "  for faults on the operator's network - the operator's",
              "  earth-fault relays and the plant's neutral and transformer",
              "  ratings are checked with them (data the operator needs)"]
    emit("k_earth", lines)


def peak() -> None:
    lines = ["peak (first-cycle) fault current against the making rating",
             "  bus     I_k kA   X/R    kappa   i_p kA   making rating kA"]
    for name, k, kv, rating in (("POC", 1, 132, 80.0), ("MV-A", 3, 33, 63.0)):
        br = src.branches("max")
        zbus = np.linalg.inv(gs.ybus(src.N, br)[1:, 1:])
        z = zbus[k - 1, k - 1]
        xr = z.imag / z.real
        kappa = 1.02 + 0.98 * math.exp(-3 / xr)
        sources = [(13 + j - 1, f.units * f.unit_mva * 1.1 / src.S_BASE)
                   for j, f in enumerate(src.FEEDERS) if f.kind != "bess"]
        ik = gs.fault_current(zbus, k - 1, 1.1, sources)["total"] * src.S_BASE / (math.sqrt(3) * kv)
        ip = kappa * math.sqrt(2) * ik
        lines.append(f"  {name:6s}  {ik:6.2f}   {xr:4.1f}   {kappa:5.2f}   {ip:6.1f}   {rating:16.1f}")
    lines += ["  kappa from the usual approximation 1.02 + 0.98 exp(-3 R/X);",
              "  a breaker must close onto the peak, not only break the rms",
              "  value - both are far inside the teaching ratings here"]
    emit("k_peak", lines)


def reclose() -> None:
    lines = ["auto-reclose of the 132 kV line against the plant's trip on loss of grid",
             "  (island frequency drifting 2 Hz/s, teaching)",
             "  dead time s   plant trips in s           margin s   at reclose"]
    for dead in (0.3, 0.5, 1.0):
        for trip, how in ((0.15, "intertrip"), (0.6, "passive relays")):
            margin = dead - trip
            angle = 360 * 0.5 * 2.0 * dead ** 2 % 360          # 0.5 a t^2 in cycles
            state = "off in time" if margin > 0.1 else f"{angle:.0f} deg out of phase"
            lines.append(f"  {dead:11.1f}   {trip:5.2f} {how:18s} {margin:+8.2f}   {state}")
    lines += ["  the plant must be off before the line closes again, with",
              "  margin; with passive relays a fast reclose (0.3-0.5 s)",
              "  catches it still connected and closes out of phase - the",
              "  intertrip (or a longer dead time agreed with the operator)",
              "  is the study's answer, coordinated with ch 26's protection"]
    emit("k_reclose", lines)


if __name__ == "__main__":
    earth()
    peak()
    reclose()
