"""Chapter 29, lesson G: water resources and the site balance - what the
wells can give (Cooper-Jacob drawdown, seasons), what construction and
operation need month by month, and the balance with a tank whose fire
reserve is held, in a normal and a drought year.

Run from the project root:   python -m companion.ch29.examples_g
Writes companion/ch29/expected/g_*.txt and diagrams/data/ch29-water.csv.
Teaching values (A-351, A-352); rights and permits are project-specific
(U-104).
"""
from __future__ import annotations

import numpy as np

from companion.ch29 import sources as src
from companion.ch29.common import csv, emit
from plantp import architecture as ar
from plantp import civil as cv

DAYS = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
SUMMER = np.array([0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0], bool)
RO_RECOVERY = 0.6          # treated / raw water for washing (spot-free), teaching


def wells() -> None:
    lines = ["what the wells give (Cooper-Jacob drawdown after 30 days of pumping)",
             "  well   rate L/s   drawdown at 0.3 m   at 300 m   m3/month   summer m3/month"]
    for name, w in src.WELLS.items():
        q = w["safe_l_s"] / 1000
        s_well = cv.cooper_jacob(q, w["t_m2_s"], w["s"], 0.3, 30 * 86400)
        s_300 = cv.cooper_jacob(q, w["t_m2_s"], w["s"], 300.0, 30 * 86400)
        month = q * 86400 * 30
        lines.append(f"  {name:5s}  {w['safe_l_s']:8.2f}   {s_well:17.1f}   {s_300:8.2f}"
                     f"   {month:8.0f}   {month * w['summer_factor']:15.0f}")
    lines += ["  the two wells 300 m apart draw each other down a little;",
              "  the summer yield falls when the water table does - a",
              "  pumping test of at least several days, and the water",
              "  right that allows the abstraction, replace these numbers"]
    emit("g_wells", lines)


def demand() -> dict:
    d = src.DEMAND
    clean_treated = np.array(d["washes"]) * src.WASH_M3
    clean_raw = clean_treated / RO_RECOVERY
    staff = d["staff"] * d["staff_l_day"] * DAYS / 1000
    return {"cleaning (raw for RO)": clean_raw, "staff": staff}


def construction() -> None:
    d = src.DEMAND
    concrete = d["construction_concrete_m3"] * (d["water_per_m3_concrete"] + d["curing_per_m3"])
    dust = d["dust_l_m2_day"] * d["road_area_m2"] * d["dust_days"] / 1000
    people = d["worker_months"] * 30 * d["worker_l_day"] / 1000
    total = concrete + dust + people
    supply = sum(w["safe_l_s"] for w in src.WELLS.values()) / 1000 * 86400 * 30 * d["construction_months"]
    lines = ["construction water over 18 months (teaching quantities)",
             f"  concrete batching and curing      {concrete:9,.0f} m3",
             f"  dust suppression on site roads    {dust:9,.0f} m3",
             f"  workers (4,534 worker-months)     {people:9,.0f} m3",
             f"  total                             {total:9,.0f} m3",
             f"  both wells at their safe yield    {supply:9,.0f} m3 over the same months",
             f"  shortfall                         {total - supply:9,.0f} m3",
             "  dust suppression is by far the largest use: treated",
             "  wastewater, binders on the busiest roads or speed limits",
             "  cut it - and the construction contract states the source,",
             "  not 'by the contractor'"]
    emit("g_construction", lines)


def balance() -> None:
    use = demand()
    w1 = src.WELLS["W-1"]
    base = w1["safe_l_s"] / 1000 * 86400 * DAYS
    supply = np.where(SUMMER, base * w1["summer_factor"], base) * 0.5     # pumped half the day
    drought = np.where(SUMMER, supply * 0.6, supply * 0.9)
    reserve = 180.0                                                     # lesson F (placeholder)
    s_n, u_n = ar.water_balance(supply, use, 2500.0, reserve)
    s_d, u_d = ar.water_balance(drought, use, 2500.0, reserve)
    total_use = sum(v.sum() for v in use.values())
    csv("ch29-water.csv", "m,use,supply,drought,stock,stockd",
        [(k + 1, f"{sum(v[k] for v in use.values()):.0f}", f"{supply[k]:.0f}", f"{drought[k]:.0f}",
          f"{s_n[k]:.0f}", f"{s_d[k]:.0f}") for k in range(12)])
    lines = ["operating water balance with W-1 (pumped 12 h a day) and the 2,500 m3 tank",
             f"  demand a year: {total_use:,.0f} m3 (staff, and washing water treated",
             f"  by RO at {100 * RO_RECOVERY:.0f} % recovery)",
             f"  supply a year: normal {supply.sum():,.0f} m3, drought {drought.sum():,.0f} m3",
             f"  held fire reserve (lesson F, placeholder): {reserve:.0f} m3, never drawn",
             f"  unmet demand: normal {u_n.sum():.0f} m3, drought {u_d.sum():.0f} m3",
             f"  lowest usable stock: normal {s_n.min():,.0f} m3 (month {s_n.argmin() + 1}),"
             f" drought {s_d.min():,.0f} m3",
             "  over the year W-1 gives more than operation needs, but the",
             "  dry summer months need more than it gives: the tank",
             f"  carries them (down to {s_d.min():,.0f} m3 in the drought) - which is",
             "  why the balance is monthly, and why construction, at",
             f"  {84_550 / total_use:.0f} times the yearly operating demand, needs another source"]
    emit("g_balance", lines)


if __name__ == "__main__":
    wells()
    construction()
    balance()
