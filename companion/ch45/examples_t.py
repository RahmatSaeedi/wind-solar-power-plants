"""Chapter 45, round t: the lot data file checked before it is used, lots
kept together or mixed in assembly, the weld meter's gauge study, how far
a hot cell can be from a temperature sensor, an audit of the cell maker
built from this chapter's findings, the energy of the first full charge
at site, how matching wears off with age, and the energy of formation.

Run from the project root:   python -m companion.ch45.examples_t
Writes companion/ch45/expected/t_*.txt.
Teaching values (A-474 to A-481).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch45 import sources as src
from companion.ch45.common import csv, emit
from plantp import procure as pr
from plantp import quality as qy

C, B = src.CELL, src.BUILD


# ------------------------------------------------ 1. the lot file
def lot_file() -> dict:
    """A lot file as delivered, with planted data faults (teaching)."""
    lot = src.lot()
    rows = [dict(id=i, cap=float(c), k=float(k)) for i, c, k in
            zip(lot["ids"], lot["cap"], lot["k"])]
    rows[1500]["id"] = rows[1499]["id"]                     # duplicate ID
    del rows[700]                                           # a cell missing
    rows[1200]["k"] = rows[1200]["k"] / 1000                # V/day, not mV/day
    rows[1800]["cap"] = 0.318                               # kAh typed for Ah
    ids = [r["id"] for r in rows]
    dup = sorted({x for x in ids if ids.count(x) > 1})
    expected = {f"C45-{i:05d}" for i in range(2000)}
    missing = sorted(expected - set(ids))
    units = [r["id"] for r in rows if 0 < r["k"] < 0.001]
    cap_bad = [r["id"] for r in rows if not 250 < r["cap"] < 400]
    neg = [r["id"] for r in rows if r["k"] < 0]
    lines = [f"lot file of L4506 as delivered: {len(rows)} rows for 2000 cells "
             "(planted faults)",
             f"  duplicate IDs: {', '.join(dup) or 'none'}",
             f"  IDs missing: {', '.join(missing) or 'none'}",
             f"  K values a thousand times too small (unit): {', '.join(units)}",
             f"  capacities outside 250-400 Ah: {', '.join(cap_bad)}",
             f"  negative K (sign or entry): {', '.join(neg)}",
             "  five checks, each a line of code, run before any analysis;",
             "  a file that fails goes back to the cell maker - grading data",
             "  with silent faults would flag good cells and pass bad ones"]
    emit("t_lotfile", lines)
    return dict(dup=dup, missing=missing, units=units, cap=cap_bad, neg=neg)


# ------------------------------------------------ 2. lots kept together
def lot_spread(lot_cells: int = 2000, seed: int = 4507) -> dict:
    modules = B["s_module"] * 0 + B["m_rack"] * B["r_container"] * B["containers"]
    n = B["s_module"]
    together = math.ceil(lot_cells / n)
    rng = np.random.default_rng(seed)
    cells = modules * n
    pick = rng.choice(cells, lot_cells, replace=False)
    mixed = len(set(int(p) // n for p in pick))
    lines = [f"lot of {lot_cells} cells in a battery of {modules} modules of {n} "
             "cells",
             f"  modules holding the lot if it is kept together: {together}",
             f"  modules holding the lot if lots are mixed at random: {mixed}",
             f"  a recall of the lot opens {together} modules in the first",
             f"  case and {mixed} in the second ({mixed / modules:.0%} of the "
             "battery);",
             "  mixing spreads a bad lot thinly - fewer weak cells in one",
             "  module - but makes every lot problem a battery-wide one; kept",
             "  together, with the lot written on the module, a recall stays",
             "  small"]
    emit("t_spread", lines)
    return dict(together=together, mixed=mixed)


# ------------------------------------------------ 3. weld meter gauge study
def weld_grr(seed: int = 4508, parts: int = 10, ops: int = 3, reps: int = 2,
             tol_uohm: float = 10.0) -> dict:
    rng = np.random.default_rng(seed)
    true = rng.normal(20.0, 1.8, parts)
    bias = rng.normal(0.0, 0.25, ops)
    data = [[[t + b + rng.normal(0.0, 0.35) for _ in range(reps)] for b in bias]
            for t in true]
    g = qy.grr_anova(data)
    grr_sd = math.sqrt(g["repeatability"] + g["reproducibility"])
    p2t = 6 * grr_sd / tol_uohm
    lines = [f"four-wire micro-ohm meter on weld resistance: {parts} welds x "
             f"{ops} operators x {reps}",
             f"  repeatability sd {math.sqrt(g['repeatability']):.2f} uohm, "
             f"reproducibility sd {math.sqrt(g['reproducibility']):.2f} uohm",
             f"  %GRR of the spread {g['grr_pct']:.0f} %, distinct categories "
             f"{g['ndc']}",
             f"  against the {tol_uohm:.0f} uohm between a good weld and the "
             f"limit: 6 sd = {p2t:.0%}",
             "  the meter tells good welds apart only roughly but separates",
             "  a cold weld (40 uohm above) without doubt: what a gauge must",
             "  do depends on the decision it serves (ch 40)"]
    emit("t_grr", lines)
    return dict(grr=g["grr_pct"], ndc=g["ndc"], p2t=p2t)


# ------------------------------------------------ 4. temperature sensor map
def sensor_map(n: int = 52, grad_k: float = 0.8) -> dict:
    """A hot spot k cells from the nearest sensor reads grad_k per cell
    lower (teaching gradient)."""
    lines = [f"temperature sensors along a module of {n} cells; a hot cell's "
             "excess",
             f"  fades {grad_k} K per cell of distance (teaching)",
             "  sensors   farthest cell from a sensor   unseen excess K"]
    out = {}
    for s in (4, 8, 13, 26):
        spacing = n / s
        far = math.ceil(spacing / 2)
        out[s] = far * grad_k
        lines.append(f"  {s:7d}   {far:27d}   {far * grad_k:15.1f}")
    lines += ["  a few sensors read the module, not each cell: the BMS limit",
              "  must sit below the cell limit by the unseen excess - the",
              "  sensor map is a design input to the temperature margins of",
              "  lesson B, and the map is checked at assembly"]
    emit("t_sensors", lines)
    return out


# ------------------------------------------------ 5. audit of the cell maker
def audit() -> dict:
    scores = {"coating control (Cpk)": 2.0, "dry room records": 4.0,
              "formation and rest records": 2.5, "grading data file": 3.0,
              "traceability": 4.5, "change control": 3.5, "hazard control": 4.0}
    weights = {"coating control (Cpk)": 2, "dry room records": 1,
               "formation and rest records": 2, "grading data file": 1,
               "traceability": 2, "change control": 1, "hazard control": 1}
    floors = {"formation and rest records": 3.0, "traceability": 3.0,
              "coating control (Cpk)": 2.5}
    s, fails = pr.audit_score(scores, weights, floors)
    lines = ["audit of the fictional cell maker, scored 0-5 from this chapter's "
             "findings",
             "  item                           score   weight   floor"]
    for k in scores:
        lines.append(f"  {k:30s} {scores[k]:5.1f}   {weights[k]:6d}   "
                     f"{floors.get(k, '-')!s:>5s}")
    lines += [f"  weighted score {s:.2f} of 5; below a floor:",
              f"    {', '.join(fails)}",
              "  a good average does not pass a maker who fails a floor: the",
              "  rest records and the coating line B are corrective actions",
              "  with dates before the next lot is accepted (ch 39)"]
    emit("t_audit", lines)
    return dict(score=s, fails=fails)


# ------------------------------------------------ 6. the first full charge at site
def first_charge(soc_ship: float = 0.30, p_import_mw: float = 10.0) -> dict:
    e = B["s_module"] * B["m_rack"] * B["r_container"] * B["containers"] * \
        C["q_ah"] * C["v_nom"] / 1e6
    to_full = e * (0.90 - soc_ship) / 0.93                  # charge losses
    hours = to_full / p_import_mw
    lines = [f"first full charge of the battery at site: {e:.2f} MWh nominal, "
             f"arriving at {soc_ship:.0%}",
             f"  to the top of the window (90 %): {to_full:.1f} MWh from the "
             "grid or the plant",
             f"  at {p_import_mw:.0f} MW: {hours:.1f} h - then a full discharge "
             "to calibrate SOC",
             "  and capacity of every rack against the BMS",
             "  the first charge is planned with the grid operator and the",
             "  PV output (ch 50): it is also the first test of the DC",
             "  window, the PCS limits and the HVAC at full heat"]
    emit("t_first", lines)
    return dict(mwh=to_full, hours=hours)


# ------------------------------------------------ 7. matching wears off
def matching_decay(sd0: float = 1.3, growth: float = 0.6, years=(0, 5, 10, 20),
                   n: int = 52) -> dict:
    """Cell capacity sd grows with sqrt(t) (teaching); the string loses the
    expected minimum of n cells, mean - sd sqrt(2 ln n)."""
    z = math.sqrt(2 * math.log(n))
    lines = [f"cell-to-cell capacity spread in a module of {n}: sd "
             f"{sd0} Ah at assembly, growing",
             f"  {growth} Ah x sqrt(years) (teaching); string loss = sd x "
             f"{z:.2f}",
             "  year   sorted: sd Ah  loss Ah   unsorted: sd Ah  loss Ah"]
    out = {}
    for y in years:
        add = growth * math.sqrt(y)
        sorted_sd = math.sqrt(0.05 ** 2 + add ** 2)          # matched at start
        unsorted_sd = math.sqrt(sd0 ** 2 + add ** 2)
        out[y] = (sorted_sd * z, unsorted_sd * z)
        lines.append(f"  {y:4d}   {sorted_sd:13.2f}  {sorted_sd * z:7.2f}   "
                     f"{unsorted_sd:15.2f}  {unsorted_sd * z:7.2f}")
    csv("ch45-decay.csv", "y,sorted,unsorted",
        [(y, round(math.sqrt(0.05 ** 2 + growth ** 2 * y) * z, 2),
          round(math.sqrt(sd0 ** 2 + growth ** 2 * y) * z, 2)) for y in range(21)])
    lines += ["  matching wins most at the start; the spread that grows in",
              "  service is shared by both - after twenty years the matched",
              "  module still keeps an advantage, but smaller; even ageing",
              "  (lesson A, temperature) protects it"]
    emit("t_decay", lines)
    return out


# ------------------------------------------------ 8. formation energy
def formation_energy(rate_day: float = 12000.0, cycles: float = 1.5,
                     recover: float = 0.80, price: float = 70.0) -> dict:
    e_cell = C["q_ah"] * C["v_nom"] / 1000                  # kWh
    day = rate_day * e_cell * cycles / 1000                  # MWh charged a day
    year = day * 365
    lines = [f"formation of {rate_day:,.0f} cells a day, about {cycles} cycles "
             "of charge each (teaching)",
             f"  energy charged into the cells: {day:.1f} MWh a day, "
             f"{year / 1000:.1f} GWh a year",
             f"  discharged into resistors: all of it lost; into a",
             f"  regenerative cycler that returns {recover:.0%}: "
             f"{year * recover / 1000:.1f} GWh a year back",
             f"  value at {price:.0f} u/MWh: {year * recover * price / 1e6:.2f} "
             "M u a year",
             "  a cell factory consumes energy on the scale of a small",
             "  plant; how it forms its cells shows in its footprint data",
             "  (ch 33, ch 39) - a buyer can ask"]
    emit("t_formation", lines)
    return dict(day=day, year=year)


if __name__ == "__main__":
    lot_file()
    lot_spread()
    weld_grr()
    sensor_map()
    audit()
    first_charge()
    matching_decay()
    formation_energy()
