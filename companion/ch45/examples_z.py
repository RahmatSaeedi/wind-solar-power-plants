"""Chapter 45, round z: BMS versions across the racks, the wet module
behind a low rack insulation reading, contactor wear over twenty years,
how much data the BMS makes against what SCADA should carry, and how far
a six-month ageing test can be extrapolated.

Run from the project root:   python -m companion.ch45.examples_z
Writes companion/ch45/expected/z_*.txt.
Teaching values (A-477 to A-481).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch45 import sources as src
from companion.ch45.common import emit
from plantp import convmfg as cm

B = src.BUILD


# ------------------------------------------------ 1. BMS versions across racks
def versions() -> dict:
    racks = [f"C{c}-R{r:02d}" for c in range(1, B["containers"] + 1)
             for r in range(1, B["r_container"] + 1)]
    base = {"firmware": "3.8.2", "limits": "L-2026-07", "map": "M-12"}
    cfg = {r: dict(base) for r in racks}
    cfg["C2-R07"]["firmware"] = "3.8.1"
    cfg["C6-R11"]["limits"] = "L-2026-05"
    ref = cm.fingerprint(base)
    odd = {r: [k for k in base if c[k] != base[k]] for r, c in cfg.items()
           if cm.fingerprint(c) != ref}
    lines = [f"BMS configuration of the {len(racks)} racks read back at site "
             "acceptance;",
             f"  released {ref}"]
    for r, keys in odd.items():
        lines.append(f"  {r}: differs in {', '.join(keys)} = "
                     f"{', '.join(cfg[r][k] for k in keys)}")
    lines += [f"  {len(odd)} of {len(racks)} racks differ; one older firmware, one",
              "  older limit table (the one before the charging-temperature",
              "  fix of lesson B) - the fingerprint finds both in a second,",
              "  as for the inverters (ch 44)"]
    emit("z_versions", lines)
    return dict(odd=odd)


# ------------------------------------------------ 2. the wet module
def wet_module(n: int = 8, r_dry_mohm: float = 40.0, r_wet_mohm: float = 0.6) -> dict:
    rs = [r_dry_mohm] * n
    rs[5] = r_wet_mohm
    rack = 1 / sum(1 / r for r in rs)
    dry = r_dry_mohm / n
    halves = (1 / sum(1 / r for r in rs[:4]), 1 / sum(1 / r for r in rs[4:]))
    lines = [f"insulation of a rack of {n} modules in parallel to the frame",
             f"  (teaching: {r_dry_mohm:.0f} Mohm a dry module)",
             f"  all dry: {dry:.2f} Mohm; with module 6 wet ({r_wet_mohm} Mohm): "
             f"{rack:.2f} Mohm",
             f"  split the rack in halves: {halves[0]:.2f} and {halves[1]:.2f} Mohm"
             " - the wet one is in the second",
             "  one wet module sets the rack's reading; dividing the rack",
             "  (lesson C) and measuring the parts finds it in three steps",
             "  for eight modules - the search is part of the integrator's",
             "  procedure, done by qualified people"]
    emit("z_wet", lines)
    return dict(rack=rack, dry=dry, halves=halves)


# ------------------------------------------------ 3. contactor wear
def contactor(ops_day: float = 2.0, years: int = 20, mech: float = 50000.0,
              load_life: float = 3000.0, load_share: float = 0.002) -> dict:
    ops = ops_day * 365 * years
    load_ops = ops * load_share
    lines = [f"rack contactors: {ops_day:.0f} operations a day for {years} years "
             f"= {ops:,.0f}",
             f"  mechanical life (teaching) {mech:,.0f}: {ops / mech:.0%} used",
             f"  openings under load ({load_share:.1%} of them, faults and trips): "
             f"{load_ops:.0f} of {load_life:,.0f}",
             "  wear is in the rare openings under load, not the daily ones:",
             "  the BMS counts both, and a contactor that opened a fault",
             "  current gets an inspection - its count is in the rack record"]
    emit("z_contactor", lines)
    return dict(ops=ops, load=load_ops)


# ------------------------------------------------ 4. BMS data against SCADA
def data_rate(bytes_pt: int = 4, period_s: float = 1.0) -> dict:
    cells = B["s_module"] * B["m_rack"] * B["r_container"] * B["containers"]
    temps = cells // 4
    pts = cells + temps
    rate = pts * bytes_pt / period_s
    summary = B["m_rack"] * B["r_container"] * B["containers"] * 12 * bytes_pt
    lines = [f"BMS points: {cells:,} cell voltages and {temps:,} temperatures, "
             f"every {period_s:.0f} s",
             f"  raw data {rate / 1000:.0f} kB/s ({rate * 86400 / 1e9:.1f} GB a "
             "day) - kept in the container's own store",
             "  to SCADA: 12 summaries a module (min, max, mean, balancing"
             " duty, ...):",
             f"    {summary / 1000:.1f} kB/s",
             "  the plant network carries the summaries and the alarms; the",
             "  raw data stays local and is fetched for an investigation -",
             "  the split is part of the point list (ch 35)"]
    emit("z_data", lines)
    return dict(raw=rate, summary=summary)


# ------------------------------------------------ 5. extrapolating an ageing test
def extrapolate(months: int = 6, loss20: float = 0.20) -> dict:
    """Six months of synthetic capacity data from a sqrt(t) fade; a straight
    line and a sqrt(t) curve fitted and carried to 20 years."""
    rng = np.random.default_rng(4514)
    t = np.arange(1, months + 1) / 12                       # years
    k = loss20 / math.sqrt(20)                              # 20 % at 20 years
    loss = k * np.sqrt(t) + rng.normal(0, 0.0015, months)
    a_lin = float(np.sum(loss * t) / np.sum(t * t))
    a_sqrt = float(np.sum(loss * np.sqrt(t)) / np.sum(t))
    y = 20.0
    lines = [f"capacity loss of test cells over {months} months (synthetic, "
             "fade ~ sqrt(t));",
             "  two fits carried to 20 years",
             f"  straight line: {a_lin:.4f} a year -> loss at 20 years "
             f"{a_lin * y:.0%}",
             f"  sqrt(t) curve: {a_sqrt:.4f} a sqrt(year) -> loss at 20 years "
             f"{a_sqrt * math.sqrt(y):.0%}",
             f"  true model at 20 years: {k * math.sqrt(y):.0%}",
             "  both fit six months well; carried to twenty years the line",
             "  predicts more loss than the cell has - the shape, not the",
             "  fit, decides, and a short test shows the shape only with a",
             "  model of the mechanism: the maker's ageing model and its",
             "  evidence are what the warranty rests on (ch 19)"]
    emit("z_extrap", lines)
    return dict(lin=a_lin * y, sqrt=a_sqrt * math.sqrt(y), true=k * math.sqrt(y))


if __name__ == "__main__":
    versions()
    wet_module()
    contactor()
    data_rate()
    extrapolate()
