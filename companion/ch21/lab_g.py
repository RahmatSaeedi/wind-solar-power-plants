"""Chapter 21, lab G - bankability, diligence and stress: the base case
under one-at-a-time downsides with the debt fixed at financial close,
a combined downside, break-even values, and the conditions-precedent
register the lenders work through before the first drawdown.

Run from the project root:   python -m companion.ch21.lab_g
Writes companion/ch21/expected/g_*.txt and diagrams/data/ch21-*.csv.
Teaching values A-304 to A-310; illustrative covenant levels only.
"""
from __future__ import annotations

import numpy as np

from companion.ch21 import model, sources as src
from companion.ch21.common import csv, emit
from plantp import finance as fn

T = src.TERMS


# [start: stress]
def stresses(debt: float) -> list[tuple[str, dict]]:
    """One-at-a-time downsides; the debt is the one signed at close."""
    return [
        ("base", {}),
        ("delay 1 year", {"delay_years": 1}),
        ("capex +10 %", {"capex_scale": 1.10}),
        ("energy P90 1-yr every year", {"energy_scale": src.P90_1Y}),
        ("energy P99 1-yr every year", {"energy_scale": 260.0 / 295.14}),
        ("tariff -10 %", {"price_scale": 0.90}),
        ("buyer pays 6 months late", {"default_months": 6.0}),
        ("currency -10 % on capex", {"fx_capex": 0.0778}),
        ("rate +2 points (unhedged)", {"rate": T["rate"] + 0.02}),
        ("replacements x 2", {"repl_scale": 2.0}),
        ("water shortage (PV -1 %)",
         {"energy_scale": 1 - 0.01 * 108.36 / 295.14}),
        ("curtailment +4 %", {"curtail_extra": 0.04}),
    ]
# [end: stress]


def run_stresses() -> None:
    base = model.run()
    lines = ["stress cases with the debt fixed at close (k u, nominal):",
             "  case                        min DSCR  min LLCR  lock-up  equity IRR %"]
    rows = []
    for name, kw in stresses(base["debt"]):
        r = model.run(debt=base["debt"], **kw)
        lock = int((r["dscr"] < T["lockup"]).sum())
        flag = " *" if r["min_dscr"] < T["default"] else ""
        lines.append(f"  {name:27s} {r['min_dscr']:8.2f}{flag:2s} {r['min_llcr']:7.2f}  {lock:7d}"
                     f"  {r['equity_irr'] * 100:12.2f}")
        rows.append((len(rows) + 1, f"{r['min_dscr']:.3f}"))
    lines += ["  (* below the illustrative default level 1.05; lock-up = years",
              "  below 1.10)",
              "  a P90 resource in every year keeps the cover above lock-up;",
              "  a P99 resource every year, a 10 % lower tariff or an",
              "  unhedged rate rise push it into lock-up; a buyer six months",
              "  late drops the year's cover below 0.5 - the six-month DSRA is",
              "  what pays the lenders that year; capex, currency and delay",
              "  hit the owners first because they are paid with equity"]
    emit("g_stress", lines)
    csv("ch21-stress.csv", "case,dscr", rows)


def combined() -> None:
    base = model.run()
    r = model.run(debt=base["debt"], energy_scale=src.P90_1Y, price_scale=0.95,
                  opex_scale=1.10, delay_years=1, capex_scale=1.05)
    lines = ["a combined downside (P90 every year, tariff -5 %, opex +10 %,",
             "delay 1 year, capex +5 %):",
             f"  min DSCR {r['min_dscr']:.2f}, lock-up years {int((r['dscr'] < T['lockup']).sum())},"
             f" min LLCR {r['min_llcr']:.2f}, equity IRR {r['equity_irr'] * 100:.2f} %",
             "  no single stress breaks the base case, but a plausible",
             "  combination keeps the owners locked up for years: lenders",
             "  ask for the combined case, the standby equity and the",
             "  reserves that carry it (conditions precedent)"]
    emit("g_combined", lines)


def breakevens() -> None:
    base = model.run()
    d = base["debt"]
    e_be = fn.breakeven(lambda k: model.run(debt=d, energy_scale=k)["min_dscr"], 0.6, 1.0, 1.0)
    p_be = fn.breakeven(lambda k: model.run(debt=d, price_scale=k)["min_dscr"], 0.6, 1.0, 1.0)
    c_be = fn.breakeven(lambda k: model.run(debt=d, capex_scale=k)["equity_irr"], 1.0, 1.6, T["rate"])
    t_be = fn.breakeven(lambda t: model.run(tariff=t)["equity_irr"], 50.0, 90.0, T["cost_of_equity"])
    lines = ["break-even values (one input moved, others at base):",
             f"  energy for min DSCR 1.00 (debt fixed):  {e_be * 100:.1f} % of P50"
             f" = {e_be * 295.14:.0f} GWh",
             f"  tariff for min DSCR 1.00 (debt fixed):  {p_be * 100:.1f} % of 70 u"
             f" = {p_be * 70:.1f} u/MWh",
             f"  capex at which equity earns only the debt rate: +{(c_be - 1) * 100:.0f} %",
             f"  tariff at which equity earns its 10 % cost (debt resized): {t_be:.1f} u/MWh",
             "  a lender asks how far the project is from 1.00; an owner",
             "  asks how far it is from its cost of equity; both answers",
             "  are distances, not single values"]
    emit("g_breakeven", lines)


# [start: cp]
CP = [  # (evidence the lenders want, source in this book, status)
    ("long-term resource and P50/P90 yield report", "ch 12-16", "draft"),
    ("independent engineer's review of the yield", "ch 16, 59", "open"),
    ("grid connection agreement and studies", "ch 17, 27-28", "open"),
    ("permits and environmental consents", "ch 14, 33, 55-57", "open"),
    ("EPC contract: price, schedule, LDs, security", "ch 38-40", "open"),
    ("equipment warranties and type certificates", "ch 9-11, 19, 41-46",
     "draft"),
    ("O&M contract with availability guarantee", "ch 51-52", "open"),
    ("PPA signed, payment security in place", "ch 21 E", "open"),
    ("insurance programme (construction, operation)", "ch 38, 51", "open"),
    ("financial model audit (this lab)", "ch 21 D, F", "draft"),
    ("hedging of rate and currency at close", "ch 21 F", "open"),
    ("equity committed, standby equity letter", "ch 21 F", "open"),
]
# [end: cp]


def cp_register() -> None:
    lines = ["conditions precedent to first drawdown (teaching register):",
             "  evidence                                       source             status"]
    for k, s, st in CP:
        lines.append(f"  {k:46s} {s:18s} {st}")
    n_open = sum(1 for *_, st in CP if st == "open")
    lines += [f"  {n_open} of {len(CP)} open: the project is not yet bankable whatever its",
              "  IRR - bankability is evidence, not a ratio"]
    emit("g_cp", lines)


if __name__ == "__main__":
    run_stresses()
    combined()
    breakevens()
    cp_register()
