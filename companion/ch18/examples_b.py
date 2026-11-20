"""Chapter 18, section B - architecture selection with model 15.1's plant
end: capacity ratios of Plant P, the wind/PV mix at a fixed export limit
with a teaching cost per delivered MWh, the export limit itself, energy
given up to hold reserve headroom, main-transformer redundancy, central
against string inverters, and a staged PV extension.

Run from the project root:   python -m companion.ch18.examples_b
Writes companion/ch18/expected/b_*.txt and diagrams/data/ch18-*.csv.
Teaching costs A-287 and reliability A-288; same hourly shapes scaled
(wakes and inverter loading do not change with size: a screening).
"""
from __future__ import annotations

from dataclasses import replace

import numpy as np

from companion.ch15 import sources as s15
from companion.ch18 import sources as src
from companion.ch18.common import csv, emit
from plantp import yieldmodel as ym
from plantp.yieldrisk import annuity

C, R = src.COST, src.REL
NO_OUT = np.zeros(8760, bool)


# [start: screen]
def screen(n_wtg: int = 12, pv_mw: float = 50.0, limit: float = 100.0):
    """Delivered and curtailed energy (MWh) and the teaching cost per
    delivered MWh for a plant of n turbines, pv_mw AC and an export
    limit; hourly shapes of model 15.1 scaled to the sizes."""
    r = s15.plant_year()
    cfg = replace(s15.ModelConfig(), export_mw=limit,
                  aux_wind_mw=n_wtg * 168.2 / 8760)
    w = r["w_av"] * n_wtg / 12
    pv = r["pv_av"] * pv_mw / 50.0
    poc, _ = ym.plant_end(w, pv, cfg, NO_OUT)
    delivered = np.minimum(poc, limit).clip(0, None).sum()
    curtailed = np.clip(poc - limit, 0, None).sum()
    capex = (C["wind_per_mw"] * 5.0 * n_wtg + C["pv_per_mw_ac"] * pv_mw
             + C["connection"]
             + C["connection_per_mw"] * max(limit - 100.0, 0.0))
    yearly = capex / annuity(C["rate"], C["years"]) + C["opex_share"] * capex
    return delivered, curtailed, 1000.0 * yearly / delivered, capex
# [end: screen]


def ratios() -> None:
    lines = ["capacity ratios of Plant P (S1 with the battery):",
             "  ratio                                   value",
             "  PV DC / PV AC (60.06 MWp / 50 MW)        1.20",
             "  wind / PV AC (60 / 50 MW)                1.20",
             "  wind + PV AC / export limit (110 / 100)  1.10",
             "  battery power / export limit (20 / 100)  0.20",
             "  battery energy / power (40 / 20)          2 h",
             "  transformers / export (2 x 63 MVA / 100)  1.26",
             "  each ratio is a choice with a price: >1 buys energy in",
             "  the other hours and pays in curtailment or clipping"]
    emit("b_ratios", lines)


def mix() -> None:
    lines = ["wind/PV mix at the 100 MW limit (teaching costs A-287):",
             "  turbines  PV MW  delivered GWh  curtailed %  cost u/MWh"]
    rows, best = [], None
    for n in (8, 10, 12, 14, 16):
        for pv in (25.0, 50.0, 75.0, 100.0):
            d, c, u, _ = screen(n, pv)
            lines.append(f"  {n:6d}  {pv:7.0f}  {d / 1e3:11.1f}   "
                         f"{100 * c / (d + c):9.2f}   {u:9.2f}")
            rows.append((n, int(pv), f"{d / 1e3:.2f}", f"{u:.3f}"))
            if best is None or u < best[2]:
                best = (n, pv, u)
    lines += [f"  lowest teaching cost: {best[0]} turbines and {best[1]:.0f} MW"
              f" PV, {best[2]:.2f} u/MWh",
              "  the lowest cost sits at the edge of the table: with these",
              "  teaching costs PV energy is cheaper, so the table shows a",
              "  direction, not an optimum; more PV puts the energy into",
              "  midday hours (price shape, chapter 21), needs land (chapter",
              "  14) and raises curtailment; the spread is under 13 %"]
    emit("b_mix", lines)
    csv("ch18-mix.csv", "n,pv,gwh,cost", rows)


def export_limit() -> None:
    lines = ["export limit for the Plant P sizes (12 turbines, 50 MW PV):",
             "  limit MW  delivered GWh  curtailed GWh  extra GWh per 10 MW"]
    prev, rows = None, []
    for lim in (70.0, 80.0, 90.0, 100.0, 110.0, 120.0):
        d, c, u, _ = screen(12, 50.0, lim)
        extra = "" if prev is None else f"{(d - prev) / 1e3:8.2f}"
        prev = d
        lines.append(f"  {lim:6.0f}   {d / 1e3:11.2f}   {c / 1e3:11.2f}       {extra}")
        rows.append((int(lim), f"{d / 1e3:.2f}", f"{c / 1e3:.2f}"))
    lines += ["  each step of 10 MW buys less: the last hours above a limit",
              "  are few; the limit is a grid decision (chapter 17) and a",
              "  price, not a free design variable"]
    emit("b_export", lines)
    csv("ch18-export.csv", "lim,gwh,curt", rows)


def reserve() -> None:
    """Hold R MW below the available power (upward reserve)."""
    r = s15.plant_year()
    poc = r["poc"]
    base = np.minimum(poc, 100.0).clip(0, None)
    lines = ["energy given up to hold upward reserve headroom (one year):",
             "  headroom MW  lost MWh  lost %   hours with free headroom"]
    for res in (2.0, 5.0, 10.0):
        held = np.minimum(np.clip(poc - res, 0, None), 100.0)
        lost = (base - held).sum()
        free = int((poc >= 100.0 + res).sum())
        lines.append(f"  {res:8.0f}     {lost:8,.0f}   {100 * lost / base.sum():5.2f}"
                     f"     {free:6,d}")
    lines += ["  in hours already curtailed by the limit the headroom costs",
              "  nothing; elsewhere it spills energy; a battery can hold the",
              "  same reserve without spilling, at the cost of its state of",
              "  charge (chapters 19 and 20); reserve is sold only where the",
              "  rules and the contract allow it"]
    emit("b_reserve", lines)


def redundancy() -> None:
    """One 125 MVA transformer against two of 63 MVA (each ~60 MW)."""
    r = s15.plant_year()
    p = np.minimum(r["poc"], 100.0).clip(0, None)
    one = R["trafo_fail"] * R["trafo_repair_h"] * p.mean()
    two = 2 * R["trafo_fail"] * R["trafo_repair_h"] * np.clip(p - 60.0, 0, None).mean()
    spare = R["trafo_fail"] * R["trafo_spare_h"] * p.mean()
    lines = ["main transformer redundancy (A-288, expected values):",
             f"  one 125 MVA unit, no spare:   {one:7,.0f} MWh/yr expected,"
             f" one event {R['trafo_repair_h'] * p.mean() / 1e3:5.1f} GWh",
             f"  one unit with a shared spare: {spare:7,.0f} MWh/yr expected,"
             f" one event {R['trafo_spare_h'] * p.mean() / 1e3:5.1f} GWh",
             f"  two 63 MVA units:             {two:7,.0f} MWh/yr expected,"
             f" one event {R['trafo_repair_h'] * np.clip(p - 60, 0, None).mean() / 1e3:5.1f} GWh",
             "  the expected values are small next to 295 GWh; the single",
             "  event is not: half a year without export is what lenders",
             "  and owners insure against, so redundancy is bought for the",
             "  tail, not for the mean (chapter 16)"]
    emit("b_redundancy", lines)


def inverters() -> None:
    """Ten 5 MW central inverters against 200 string inverters of 250 kW."""
    r = s15.plant_year()
    pv = r["pv_av"]
    rows = [("central 10 x 5 MW", 10, 5.0, R["central_fail"], R["central_mttr_h"]),
            ("string 200 x 250 kW", 200, 0.25, R["string_fail"], R["string_mttr_h"])]
    lines = ["PV inverter architecture (A-288, expected values):",
             "  option               units  failures/yr  lost MWh/yr  MWh/failure"]
    for name, n, size, lam, mttr in rows:
        per_unit = pv.mean() / n                  # MW lost while one unit is out
        lost = n * lam * mttr * per_unit
        lines.append(f"  {name:19s}  {n:5d}  {n * lam:9.1f}   {lost:9.0f}"
                     f"     {lost / (n * lam):7.1f}")
    lines += ["  string inverters fail more often in total but each failure",
              "  loses less and is swapped in hours; central units mean fewer",
              "  call-outs, each costlier in energy and skilled work; both are",
              "  small: the choice turns on cost, service model and the grid",
              "  functions the plant must provide (chapters 9, 25 and 51)"]
    emit("b_inverters", lines)


def expansion() -> None:
    """A later PV extension of 25 MW AC (30 MWp) at the same limit."""
    d0, c0, u0, k0 = screen(12, 50.0, 100.0)
    d1, c1, u1, k1 = screen(12, 75.0, 100.0)
    d2, c2, u2, k2 = screen(12, 75.0, 120.0)
    lines = ["staged PV extension of 25 MW AC (teaching):",
             f"  today: {d0 / 1e3:.1f} GWh, {u0:.2f} u/MWh",
             f"  + 25 MW PV at 100 MW: +{(d1 - d0) / 1e3:.1f} GWh, curtailed"
             f" {c1 / 1e3:.1f} GWh, {u1:.2f} u/MWh",
             f"  + 25 MW PV at 120 MW: +{(d2 - d0) / 1e3:.1f} GWh, curtailed"
             f" {c2 / 1e3:.1f} GWh, {u2:.2f} u/MWh",
             "  what the first stage must leave: land, a spare 33 kV bay,",
             "  transformer capacity or space for a third unit, a cable",
             "  route, and protection and control that can take more",
             "  blocks; cheap now, costly to retrofit with outages"]
    emit("b_expansion", lines)


if __name__ == "__main__":
    ratios()
    mix()
    export_limit()
    reserve()
    redundancy()
    inverters()
    expansion()
