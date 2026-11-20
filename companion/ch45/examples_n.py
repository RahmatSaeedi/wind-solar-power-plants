"""Chapter 45, round n: SOC error across the whole LFP curve (plot data),
charging on a winter morning against the heat the container needs, and
the age of cells at installation.

Run from the project root:   python -m companion.ch45.examples_n
Writes companion/ch45/expected/n_*.txt and diagrams/data/ch45-lfpsoc.csv.
Teaching values (A-474, A-477, A-480).
"""
from __future__ import annotations

import numpy as np

from companion.ch19 import sources as s19
from companion.ch45 import sources as src
from companion.ch45.common import csv, emit
from plantp import storage as st

C, B = src.CELL, src.BUILD


# ------------------------------------------------ 1. SOC error across the curve
def soc_curve(err_mv: float = 5.0) -> dict:
    socs = np.linspace(0.05, 0.97, 93)
    err = [err_mv / 1000 / float(st.ocv_slope(s)) for s in socs]
    csv("ch45-lfpsoc.csv", "soc,err",
        [(round(100 * s, 1), round(100 * min(e, 0.12), 2)) for s, e in zip(socs, err)])
    flat = [s for s, e in zip(socs, err) if e > 0.03]
    lines = [f"SOC error from a {err_mv:.0f} mV reading error across the LFP "
             "teaching curve",
             f"  error above 3 % between SOC {min(flat):.0%} and {max(flat):.0%}",
             f"  largest {max(err):.1%}, smallest {min(err):.2%}",
             "  only the ends of the curve let the voltage correct the SOC"]
    emit("n_lfpsoc", lines)
    return dict(lo=min(flat), hi=max(flat))


# ------------------------------------------------ 2. charging on a winter morning
def derate(t_cell: float) -> float:
    """Educational charge-current limit (C-rate) by cell temperature."""
    if t_cell < 2.0 or t_cell > 52.0:
        return 0.0
    if t_cell < 10.0:
        return 0.1
    if t_cell < 15.0:
        return 0.25
    return 0.5


def winter(t_air: float = -5.0, hours: float = 10.0) -> dict:
    th = s19.THERMAL
    lines = [f"a winter night at {t_air:.0f} C before a sunny morning; container UA "
             f"{th['ua_kw_k']} kW/K (ch 19)",
             "  cells kept at   charge C-rate allowed   heat to hold kW   "
             f"heat over {hours:.0f} h kWh"]
    out = {}
    for t_cell in (5.0, 12.0, 15.0, 20.0):
        q = th["ua_kw_k"] * (t_cell - t_air)
        out[t_cell] = (derate(t_cell), q, q * hours)
        lines.append(f"  {t_cell:12.0f}   {derate(t_cell):21.2f}   {q:15.1f}   "
                     f"{q * hours:15.0f}")
    h15 = out[15.0][2]
    lines += [f"  holding the cells at 15 C costs {h15:.0f} kWh a container a night",
              f"  ({h15 * B['containers'] / 1000:.1f} MWh for the plant) and "
              "lets the battery take the",
              "  morning's PV at full rate; at 5 C",
              "  it takes a fifth - the BMS limit by temperature and the",
              "  HVAC set point are designed together, and the limit table",
              "  is part of the configuration record (lesson B)"]
    emit("n_winter", lines)
    return out


# ------------------------------------------------ 3. the age of cells
def cell_age(seed: int = 4515, n: int = 39936, limit_months: float = 12.0) -> dict:
    """Months from formation to installation of the battery's cells
    (synthetic: lots made over six months, shipped, then stored)."""
    rng = np.random.default_rng(seed)
    made = rng.uniform(0, 6, n)                           # month of formation
    ship = 8.0
    cod_wait = rng.choice([1.0, 4.0, 9.0], n, p=[0.6, 0.3, 0.1])
    age = ship - made + 2.0 + cod_wait
    old = int((age > limit_months).sum())
    lines = [f"months from formation to installation of the {n:,} cells "
             "(synthetic)",
             f"  median {np.median(age):.1f}, oldest {age.max():.1f}; older than "
             f"{limit_months:.0f} months: {old:,} ({old / n:.1%})",
             "  cells past the maker's storage limit get a capacity and",
             "  voltage check before they go in, by the dates in their",
             "  record - a container that waited (lesson C) is checked",
             "  as a whole"]
    emit("n_age", lines)
    return dict(old=old, share=old / n)


if __name__ == "__main__":
    soc_curve()
    winter()
    cell_age()
