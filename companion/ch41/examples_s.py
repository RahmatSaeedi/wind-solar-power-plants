"""Chapter 41, a second round: the module line's capacity against Plant
P's order, module power classes from cell variation with and without
binning, the flash test's temperature error, what a lower light-induced
loss is worth, series resistance from two I-V curves, and cracks that
grow after installation.

Run from the project root:   python -m companion.ch41.examples_s
Writes companion/ch41/expected/s_*.txt and diagrams/data/ch41-*.csv.
Teaching values (A-443 to A-449).
"""
from __future__ import annotations

import math
import random
from statistics import mean

import numpy as np

from companion.ch41 import sources as src
from companion.ch41.common import csv, emit
from companion.ch41.examples_a import sample
from plantp import pvcell as pc

REF = pc.fit(pc.PVM_550_DS)


# ------------------------------------------------ line capacity vs order
def capacity(oee: float = 0.85, yield_: float = 0.985,
             hours: float = 22.0) -> dict[str, float]:
    takts = [(s, t) for s, _, t, _ in src.LINE if t > 0]
    t_neck = max(t for _, t in takts)
    neck = " and ".join(s for s, t in takts if t == t_neck)
    per_day = hours * 3600 / t_neck * oee * yield_
    days = src.MODULES_PLANT / per_day
    lines = ["module line against Plant P's order (teaching)",
             f"  bottleneck: {neck} at {t_neck} s a module",
             f"  {hours:.0f} h a day x OEE {oee:.0%} x yield {yield_:.1%}: "
             f"{per_day:,.0f} modules a day",
             f"  {src.MODULES_PLANT:,} modules: {days:.0f} working days on one "
             "line",
             f"  ({days / 6:.1f} weeks of six days) - the order fills the line",
             "  for two months: the delivery plan of ch 31 and the slot",
             "  reserved at award (ch 39) follow from this one division"]
    emit("s_capacity", lines)
    return dict(per_day=per_day, days=days)


# ------------------------------------------- power classes from the cells
def classes(n_modules: int = 2000, seed: int = 4113) -> dict[str, dict]:
    rng = random.Random(seed)
    cells = [sample(rng) for _ in range(n_modules * 72)]
    edges = (545, 550, 555, 560)
    out = {}
    # cell mismatch inside a module from lab D: unsorted 0.34 %, binned ~0
    for name, sort, mism in (("cells as they come", False, 0.0034),
                             ("cells sorted into bins", True, 0.0)):
        pool = sorted(cells) if sort else list(cells)
        powers = []
        for m in range(n_modules):
            eta = mean(pool[m * 72:(m + 1) * 72])
            powers.append(eta * 330 * 0.1 * 72 * 0.992 * (1 - mism))
        share = {e: sum(1 for p in powers if e <= p < e + 5) / n_modules
                 for e in edges}
        share["below"] = sum(1 for p in powers if p < 545) / n_modules
        out[name] = share
    lines = [f"power classes of {n_modules:,} modules built from the varied "
             "cells of lesson A",
             "  cells                    below 545   545     550     555     560"]
    for name, s in out.items():
        lines.append(f"  {name:24s} {s['below']:8.1%}   {s[545]:5.1%}"
                     f"   {s[550]:5.1%}   {s[555]:5.1%}   {s[560]:5.1%}")
    lines += ["  sorting does not make better cells; it puts like with like:",
              "  strong cells make high-class modules instead of being",
              "  dragged by weak ones - binning is how a factory sells the",
              "  spread of its process as a ladder of power classes"]
    emit("s_classes", lines)
    return out


# ------------------------------------------- flash temperature error
def flash_temperature(gamma: float = -0.35) -> dict[float, float]:
    out = {}
    lines = ["flash test: module temperature read wrong by dT (gamma "
             f"{gamma} %/K)",
             "  error K   power error W at 550 W   share moved to the next class"]
    for dt in (0.5, 1.0, 2.0):
        e = abs(gamma) / 100 * dt * 550
        out[dt] = e
        lines.append(f"  {dt:7.1f}   {e:22.2f}   {min(e / 5, 1):29.0%}")
    lines += ["  a module that waited in a warm hall reads low unless its",
              f"  temperature is measured, not assumed; a 2 K error moves "
              f"{min(out[2.0] / 5, 1):.0%}",
              "  of modules (spread evenly in a 5 W class) across a boundary -",
              "  the hall's temperature and the module's soak time are",
              "  part of the flash procedure (IEC 60891 corrections)"]
    emit("s_flashtemp", lines)
    return out


# ------------------------------------------- what a lower LID is worth
def lid_value(pv_gwh: float = 110.0, price: float = 70.0,
              years: int = 25, rate: float = 0.075) -> dict[str, float]:
    annuity = (1 - (1 + rate) ** -years) / rate
    out = {}
    lines = [f"light-induced loss: PV energy {pv_gwh:.0f} GWh a year (model "
             "15.1), 70 u/MWh",
             "  first-hours loss   energy lost GWh/yr   value k u/yr   "
             f"PV {years} y @ {rate:.1%}"]
    for lid in (0.003, 0.01, 0.02):
        e = pv_gwh * lid
        v = e * price
        out[lid] = v * annuity
        lines.append(f"  {lid:16.1%}   {e:18.2f}   {v:12.0f}   "
                     f"{v * annuity:9,.0f} k u")
    d = out[0.02] - out[0.003]
    lines += [f"  2 % against 0.3 % is worth about {d:,.0f} k u over the life:",
              "  the maker's light-soaking data (and the dopant choice behind",
              "  it, lesson B) is a priced item in the bid evaluation, not a",
              "  footnote (ch 39, evaluated price)"]
    emit("s_lid", lines)
    return out


# ------------------------------------------- series resistance, two curves
def rs_two_curves(g2: float = 600.0) -> dict[str, float]:
    a = pc.at_conditions(REF, 1000.0, 25.0, pc.PVM_550_DS.alpha_isc)
    b = pc.at_conditions(REF, g2, 25.0, pc.PVM_550_DS.alpha_isc)
    d_i = a.isc - b.isc
    est = []
    for frac in (0.6, 0.7, 0.8):
        i_b = frac * b.isc
        v_b = float(b.v(i_b))
        v_a = float(a.v(i_b + d_i))
        est.append((v_b - v_a) / d_i)
    rs = mean(est)
    lines = [f"series resistance from two curves (1000 and {g2:.0f} W/m2, "
             "25 C, ch 10 model)",
             f"  shift the low curve up by dI = {d_i:.2f} A; the voltage gap",
             "  between matching points is Rs x dI",
             "  points at 60 / 70 / 80 % of Isc: " +
             ", ".join(f"{x:.3f}" for x in est) + " ohm",
             f"  estimate {rs:.3f} ohm; fitted model value {REF.r_s:.3f} ohm "
             f"({rs / REF.r_s - 1:+.0%}):",
             "  the method assumes the curves differ only by the shift -",
             "  the diode and shunt terms also move with irradiance;",
             "  the two-curve method needs no model: a rising Rs between",
             "  the factory flash and a field curve points at joints and",
             "  ribbons (cold solder, corrosion), not at the cells"]
    emit("s_rs", lines)
    return dict(rs=rs, fit=float(REF.r_s))


# ------------------------------------------- cracks that grow later
LOSS_BY_INACTIVE = [(0, 0.0), (5, 0.3), (10, 2.6), (20, 10.6), (30, 20.1)]


def _loss(inactive: float) -> float:
    xs, ys = zip(*LOSS_BY_INACTIVE)
    return float(np.interp(inactive, xs, ys)) / 100


def crack_growth(share: float = 0.005, seed: int = 4114) -> dict[str, float]:
    rng = random.Random(seed)
    n = src.MODULES_PLANT
    cracked = int(n * share)
    before = [rng.uniform(0, 4) for _ in range(cracked)]
    after = [min(30.0, x + rng.expovariate(1 / 6.0)) for x in before]
    p_mod = 550.0
    loss0 = sum(_loss(x) for x in before) * p_mod / 1000
    loss1 = sum(_loss(x) for x in after) * p_mod / 1000
    lines = [f"{share:.1%} of {n:,} modules with a crack at installation "
             f"({cracked} modules)",
             "  inactive area grows with thermal and wind cycles (teaching:",
             "  +6 % on average over some years, ch 10 loss curve)",
             f"  loss at installation {loss0:.1f} kW; after growth "
             f"{loss1:.1f} kW",
             f"  of {n * p_mod / 1e6:.1f} MWp: {loss1 / (n * p_mod / 1000):.3%}"
             " of the array",
             "  small for the plant, larger for each owner of a cracked",
             "  module: the cracked ones also run hotter (hot spots, ch 10)",
             "  - which is why EL at receipt and after installation sets",
             "  the baseline for warranty claims later"]
    emit("s_cracks", lines)
    return dict(before=loss0, after=loss1)


if __name__ == "__main__":
    capacity()
    classes()
    flash_temperature()
    lid_value()
    rs_two_curves()
    crack_growth()
