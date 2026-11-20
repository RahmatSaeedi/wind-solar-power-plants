"""Chapter 41, a fifth round: series and shunt resistance read from the
slopes of an I-V curve, an EL image as numbers, cost per watt and what a
design change is worth, the operating temperature of two module builds
weighted by the data-pack sun, and pallets in a container.

Run from the project root:   python -m companion.ch41.examples_v
Writes companion/ch41/expected/v_*.txt and diagrams/data/ch41-*.csv.
Teaching values (A-444 to A-449); the EL image is synthetic.
"""
from __future__ import annotations

import math
import random

import numpy as np

from companion.ch41.common import csv, emit
from plantp import datapack
from plantp import pvcell as pc

REF = pc.fit(pc.PVM_550_DS)


# ------------------------------------------- resistances from the slopes
# [start: slopes]
def slopes(sdm, n_pts: int = 300, noise: float = 0.001, seed: int = 4118):
    """Measured-like I-V points; shunt from the slope near I_sc, series
    resistance from the slope near V_oc minus the diode's own part."""
    rng = random.Random(seed)
    v = np.linspace(0, sdm.voc, n_pts)
    i = np.array([float(sdm.i(x)) * (1 + rng.gauss(0, noise)) for x in v])
    near_isc = v < 0.2 * sdm.voc
    k_sc = np.polyfit(v[near_isc], i[near_isc], 1)[0]
    near_voc = i < 0.08 * i[0]
    k_oc = np.polyfit(i[near_voc], v[near_voc], 1)[0]
    rsh = -1 / k_sc
    rs = -k_oc - sdm.a / i[0]
    return rs, rsh
# [end: slopes]


def resistances() -> dict[str, tuple[float, float]]:
    cases = {"good module": REF,
             "shunted cells": pc.SDM(REF.i_l, REF.i_0, REF.a, REF.r_s, 15.0),
             "weak joints": pc.SDM(REF.i_l, REF.i_0, REF.a, 0.35, REF.r_sh)}
    out = {}
    vv = np.linspace(0, REF.voc, 60)
    csv("ch41-ivslopes.csv", "v,good,shunt,joints",
        [(round(float(x), 2),
          *(round(max(float(m.i(x)), 0.0), 3) for m in cases.values()))
         for x in vv])
    lines = ["Rs and Rsh read from the slopes of a flash curve (0.1 % noise)",
             "  module            Rs true   Rs read   Rsh true   Rsh read"]
    for name, m in cases.items():
        rs, rsh = slopes(m)
        out[name] = (rs, rsh)
        lines.append(f"  {name:16s} {m.r_s:8.3f}  {rs:8.3f}  {m.r_sh:9.0f}"
                     f"  {rsh:9.0f}")
    lines += ["  a low shunt (edge isolation, cracks through the junction)",
              "  tilts the flat part of the curve; a high series resistance",
              "  (cold solder, thin ribbon) leans the steep part - the",
              "  slopes point at the process step, which is why the flash",
              "  file keeps the whole curve, not only Pmax; Rsh read from",
              "  a noisy flat part is rough, Rs needs the diode's own part",
              "  (n Ns kT/q over Isc) taken away, and a strong shunt",
              f"  biases it high ({out['shunted cells'][0]:.3f} against "
              f"{REF.r_s:.3f}) - read the two together"]
    emit("v_slopes", lines)
    return out


# ------------------------------------------- an EL image as numbers
def el_image(seed: int = 4119, px: int = 6) -> dict[str, float]:
    rng = random.Random(seed)
    cols, rows = 6, 24
    img = np.ones((rows * px, cols * px))
    for r in range(rows * px):
        for c in range(cols * px):
            img[r, c] = 1.0 + rng.gauss(0, 0.06)
    cracked = {(5, 2): 0.35, (17, 4): 0.12, (9, 0): 0.03}   # cell: share dark
    for (r0, c0), share in cracked.items():
        n_dark = int(round(share * px * px))
        cells = [(r, c) for r in range(px) for c in range(px)]
        cells.sort(key=lambda rc: rc[0] + rc[1], reverse=True)   # a corner
        for r, c in cells[:n_dark]:
            img[r0 * px + r, c0 * px + c] = 0.15 + rng.gauss(0, 0.03)
    found = {}
    for r0 in range(rows):
        for c0 in range(cols):
            blk = img[r0 * px:(r0 + 1) * px, c0 * px:(c0 + 1) * px]
            share = float((blk < 0.5).mean())
            if share > 0:
                found[(r0, c0)] = share
    worst = max(found.values()) if found else 0.0
    grade = "C" if worst > 0.10 else "B" if worst > 0.02 else "A"
    rows_csv = [(c, r, round(float(img[r, c]), 3))
                for r in range(rows * px) for c in range(cols * px)]
    csv("ch41-el.csv", "x,y,z", rows_csv)
    lines = [f"EL image of one module: {rows} x {cols} half cells, {px} x {px} "
             "pixels each (synthetic)",
             "  pixel darker than half the module's mean = inactive",
             "  half cell (row, col)   inactive share"]
    for (r, c), s in sorted(found.items()):
        lines.append(f"  ({r:2d}, {c})              {s:12.0%}")
    lines += [f"  worst cell {worst:.0%}: grade {grade} (teaching rule: C above "
              "10 %, B above 2 %)",
              "  the grade is a rule on numbers, so two graders agree when",
              "  they apply it (lesson C, kappa); the image is kept with the",
              "  serial as the module's baseline for later claims"]
    emit("v_el", lines)
    return dict(worst=worst, cells=len(found))


# ------------------------------------------- cost per watt
COST = [  # item, u per W (teaching shares, A-449)
    ("silicon and wafer", 0.034), ("cell processing (incl. silver)", 0.026),
    ("glass", 0.012), ("frame", 0.010), ("encapsulant and backsheet", 0.010),
    ("junction box and cables", 0.006), ("ribbon, sealant, labels", 0.004),
    ("module labour and overhead", 0.012)]


def cost() -> dict[str, float]:
    total = sum(c for _, c in COST)
    out = {"total": total}
    lines = ["module cost per watt (teaching shares, not a market price)",
             "  item                              u/W     share"]
    for name, c in COST:
        lines.append(f"  {name:32s} {c:6.3f}   {c / total:5.0%}")
    frame30 = 0.010 * 0.30 / total
    ctm1 = 0.01
    out.update(frame30=frame30, ctm1=ctm1)
    lines += [f"  total {total:.3f} u/W",
              f"  frame 30 % dearer: +{frame30:.1%} on the module",
              f"  CTM 1 % higher: every cost per watt falls {ctm1:.0%} - worth",
              f"  {ctm1 * total * 1000:.2f} u per kW, as much as making the "
              f"frame {ctm1 * total / 0.010:.0%} cheaper",
              "  design for manufacture is also design for watts: a gain in",
              "  CTM spreads over every line of the bill"]
    emit("v_cost", lines)
    return out


# ------------------------------------------- operating temperature
def temperature(noct_a: float = 44.0, noct_b: float = 46.0,
                gamma: float = -0.35) -> dict[str, float]:
    h = datapack.load_hourly()
    g = h["ghi_wm2"].to_numpy()
    dt = (noct_b - noct_a) / 800.0 * g
    loss = float((g * dt).sum() / g.sum()) * abs(gamma) / 100
    lines = [f"two builds: NOCT {noct_a:.0f} C (glass-backsheet) and "
             f"{noct_b:.0f} C (glass-glass), teaching",
             "  cell temperature difference = (NOCT_b - NOCT_a)/800 x G,",
             "  weighted by the data-pack GHI of every hour",
             f"  energy-weighted difference {float((g * dt).sum() / g.sum()):.2f} K;"
             f" energy {loss:.2%} lower",
             f"  on 110 GWh of PV a year: {110 * loss:.2f} GWh",
             "  a hotter build is not a worse one if it lasts longer or",
             "  carries a bifacial gain - the comparison is made in energy",
             "  over the life, with each build's own data"]
    emit("v_temp", lines)
    return dict(loss=loss)


# ------------------------------------------- pallets in a container
def pallets(per_pallet: int = 31, mod_kg: float = 28.1, pack_kg: float = 1.0,
            pallet_kg: float = 25.0, floor_slots: int = 10, high: int = 2,
            payload_kg: float = 26500.0) -> dict[str, float]:
    n_pal = floor_slots * high
    mass = n_pal * (per_pallet * (mod_kg + pack_kg) + pallet_kg)
    per_ctn = n_pal * per_pallet
    lines = ["pallets in a 40-ft container (teaching dimensions)",
             f"  {per_pallet} modules a pallet on edge; {floor_slots} floor "
             f"slots, stacked {high} high",
             f"  {n_pal} pallets = {per_ctn} modules; mass {mass / 1000:.1f} t of "
             f"{payload_kg / 1000:.1f} t payload",
             f"  volume, not weight, fills the box ({mass / payload_kg:.0%} of "
             "the payload)",
             f"  {math.ceil(math.ceil(109200 / per_pallet) / n_pal)} containers "
             "for the plant (as ch 10)",
             "  the bottom pallet carries the top one through every bump:",
             "  the transport test qualifies this package as packed, so a",
             "  change of pallet or stacking is a change of the package"]
    emit("v_pallets", lines)
    return dict(per_ctn=per_ctn, mass=mass)


if __name__ == "__main__":
    resistances()
    el_image()
    cost()
    temperature()
    pallets()
