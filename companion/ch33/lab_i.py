"""Chapter 33, lab I (worked example 5): a bounded lifecycle greenhouse-gas
footprint of Plant P for two cases (S0 without and S1 with the battery),
with the functional unit, boundary, data and factor provenance stated,
the uncertainty sampled, end-of-life credits shown apart, and avoided
emissions kept separate from the project inventory.

Run from the project root:   python -m companion.ch33.lab_i
Writes companion/ch33/expected/i_*.txt and diagrams/data/ch33-lca.csv.
Teaching factors (A-383); a real study follows ISO 14040/14044 and
ISO 14067 (STD-141 to STD-143) with supplier data where it exists.
"""
from __future__ import annotations

import numpy as np

from companion.ch33 import sources as src
from companion.ch33.common import csv, emit
from plantp import envsocial as es


def _cases():
    s0 = dict(src.LCA)
    s1 = dict(src.LCA, **src.BESS_LCA)
    return {"S0": s0, "S1": s1}


def _operation_t() -> float:
    o = src.OPERATION
    grid = o["own_use_mwh"] * 0.3 * o["grid_factor"] * src.LIFE_YEARS      # t, 30 % imported
    diesel = o["diesel_m3_year"] * 2.7 * src.LIFE_YEARS                     # t
    return grid + diesel


def scope() -> None:
    lines = ["goal and scope of the footprint (stated before any number)",
             "  functional unit: 1 kWh delivered at the point of connection",
             "  reporting period: 25 years of operation, P50 energy (ch 15)",
             "  boundary: materials and manufacture, transport, construction,",
             "    operation (grid imports for own use, backup diesel; no grid",
             "    charging of the battery - S1 charges from the plant only),",
             "    replacements, end of life (credits shown separately)",
             "  factors: teaching values with a stated spread (A-383); the",
             "    real study uses supplier EPDs where verified (lesson K)",
             "  excluded: land-use change, staff travel, office overheads",
             "  every comparison below holds only inside this scope"]
    emit("i_scope", lines)


def inventory() -> None:
    rows = []
    lines = ["inventory of case S0 (t CO2e, teaching factors)",
             "  item                                    amount        factor     t CO2e"]
    s0 = src.LCA
    total = 0.0
    for name, (a, f, _c) in s0.items():
        t = a * f / 1000
        total += t
        rows.append((len(rows) + 1, round(t)))
        lines.append(f"  {name:38s} {a:10,.0f}   {f:9,.0f}   {t:8,.0f}")
    repl = total * src.OPERATION["replacements_share"]
    op = _operation_t()
    eol = total * src.OPERATION["eol_credit_share"]
    csv("ch33-lca.csv", "item,t", rows)
    lines += [f"  manufacture and construction             {total:28,.0f}",
              f"  replacements (8 %)                       {repl:28,.0f}",
              f"  operation over 25 years                  {op:28,.0f}",
              f"  end-of-life credit (shown apart)         {eol:28,.0f}",
              "  modules and turbines dominate; operation is small because",
              "  the plant powers itself most of the time"]
    emit("i_inventory", lines)


def compare() -> None:
    lines = ["two cases per kWh with uncertainty (Monte Carlo of the factors)",
             "  case   energy GWh/yr   g CO2e/kWh   P5 - P95        with EoL credit"]
    for case, items in _cases().items():
        mc = es.inventory_mc(items)                      # kg
        mc = mc * (1 + src.OPERATION["replacements_share"]) + _operation_t() * 1000
        kwh = src.ENERGY_GWH[case] * 1e6 * src.LIFE_YEARS
        g = mc * 1000 / kwh
        p5, p50, p95 = np.percentile(g, [5, 50, 95])
        base = es.inventory_total({k: (a, f) for k, (a, f, _c) in items.items()})
        eol = base * src.OPERATION["eol_credit_share"] * 1000 / kwh
        lines.append(f"  {case:4s}   {src.ENERGY_GWH[case]:13.1f}   {p50:10.1f}   {p5:5.1f} - {p95:5.1f}"
                     f"        {p50 + eol:6.1f}")
    lines += ["  the battery adds about a gram per kWh and its spread",
              "  overlaps the S0 range: the cases differ by less than the",
              "  factors' uncertainty, so the study reports both with",
              "  their ranges and does not rank them on the medians"]
    emit("i_compare", lines)


def avoided() -> None:
    e = src.ENERGY_GWH["S0"] * 1000                       # MWh a year
    lines = ["avoided emissions: a claim kept apart from the inventory",
             "  counterfactual: the same energy from the regional grid mix",
             "  grid factor t/MWh   avoided t CO2e/yr   project t/yr (life avg)"]
    life_t = (es.inventory_total({k: (a, f) for k, (a, f, _c) in src.LCA.items()}) / 1000
              * (1 + src.OPERATION["replacements_share"]) + _operation_t()) / src.LIFE_YEARS
    for gf in (0.3, 0.5, 0.7):
        lines.append(f"  {gf:17.1f}   {e * gf:17,.0f}   {life_t:24,.0f}")
    lines += ["  the avoided number depends on a counterfactual that is",
              "  an assumption (which plants the energy displaces, now and",
              "  in 20 years); it is not a property of the plant, not",
              "  guaranteed, and not transferable to another grid - it is",
              "  reported with its counterfactual, never added to or",
              "  subtracted from the project's own inventory"]
    emit("i_avoided", lines)


if __name__ == "__main__":
    scope()
    inventory()
    compare()
    avoided()
