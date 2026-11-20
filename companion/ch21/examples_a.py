"""Chapter 21, section A - cost and cash-flow foundations: the capital
cost breakdown, construction spending with interest during construction
and the sources and uses, operating and lifecycle costs, real and
nominal money (and the error of mixing them), a currency shock on the
hard-currency part of the capital cost, and cleaning and water
strategies judged on lifecycle cost.

Run from the project root:   python -m companion.ch21.examples_a
Writes companion/ch21/expected/a_*.txt and diagrams/data/ch21-*.csv.
Teaching values A-304 to A-310.
"""
from __future__ import annotations

import numpy as np

from companion.ch21 import model, sources as src
from companion.ch21.common import csv, emit
from plantp import finance as fn

T = src.TERMS


def capex() -> None:
    tot = src.capex_total()
    base = tot / (1 + src.CONTINGENCY)
    lines = ["capital cost of Plant P, S1 (teaching, A-304):",
             "  item                          k u      share %   k u per MW"]
    rows = []
    for k, v in src.CAPEX.items():
        mw = 60 if k.startswith("wind") else 50 if k.startswith("PV") else 20 if k.startswith("batt") else 110
        lines.append(f"  {k:28s} {v:9,.0f}   {v / tot * 100:7.1f}   {v / mw:10,.0f}")
        rows.append((k.split()[0], f"{v:.0f}"))
    lines += [f"  contingency 5 %              {base * src.CONTINGENCY:9,.0f}"
              f"   {base * src.CONTINGENCY / tot * 100:7.1f}",
              f"  total                        {tot:9,.0f}   100.0   {tot / 110:10,.0f}",
              f"  without the battery (S0)     {src.capex_total(False):9,.0f}",
              "  wind and PV are 73 % of the cost; contingency is a budget for",
              "  known unknowns, not for scope changes; real numbers come from",
              "  quotes and the EPC price (chapters 38-40)"]
    emit("a_capex", lines)
    csv("ch21-capex.csv", "k,v", [(i + 1, f"{v / 1000:.2f}") for i, v in
                                  enumerate(list(src.CAPEX.values()) + [base * src.CONTINGENCY])])


def sources_uses() -> None:
    r = model.run()
    lines = ["construction and sources and uses (base case, A-307..A-309):",
             f"  capital cost                 {r['capex']:9,.0f} k u",
             f"  interest during construction {r['idc']:9,.0f}",
             f"  upfront fee 1.5 % of debt    {r['fee']:9,.0f}",
             f"  DSRA (6 months of service)   {r['dsra']:9,.0f}",
             f"  uses                         {r['uses']:9,.0f}",
             f"  senior debt                  {r['debt']:9,.0f}   ({r['gearing'] * 100:.1f} %)",
             f"  equity                       {r['equity']:9,.0f}   ({(1 - r['gearing']) * 100:.1f} %)",
             f"  debt sized by: {r['binding']}",
             "  IDC and fees are paid with the same money as the plant: they",
             "  are uses, they are financed, and the lenders size the debt on",
             "  cash flows, not on the cost"]
    emit("a_sources", lines)
    csv("ch21-sources.csv", "x,capex,idc,fee,dsra,debt,equity",
        [(1, f"{r['capex'] / 1000:.2f}", f"{r['idc'] / 1000:.2f}", f"{r['fee'] / 1000:.2f}",
          f"{r['dsra'] / 1000:.2f}", "0", "0"),
         (2, "0", "0", "0", "0", f"{r['debt'] / 1000:.2f}", f"{r['equity'] / 1000:.2f}")])


def opex() -> None:
    tot = sum(src.OPEX.values())
    e1 = src.energy_series(1)[0]
    lines = ["operating cost of Plant P, year-1 money (A-305):",
             "  line                              k u a year   u per MWh"]
    for k, v in src.OPEX.items():
        lines.append(f"  {k:32s} {v:11,.0f}   {v / e1:9.2f}")
    lines += [f"  total                            {tot:11,.0f}   {tot / e1:9.2f}",
              "lifecycle costs (A-306), year-1 money:"]
    for y, (k, v) in sorted(src.REPLACE.items()):
        lines.append(f"  year {y:2d}  {k:32s} {v:7,.0f}")
    lines += [f"  year 25  {'decommissioning less salvage':32s} "
              f"{src.DECOM['cost'] - src.DECOM['salvage']:7,.0f}",
              "  every line escalates with inflation (2.5 %) in the nominal",
              "  model; replacements are paid from cash flow, before debt"]
    emit("a_opex", lines)


def real_nominal() -> None:
    n = 20
    cash_real = np.full(n, 10_000.0)                 # constant in year-1 money
    infl, real = T["inflation"], 0.05
    nom_rate = fn.real_to_nominal_rate(real, infl)
    cash_nom = cash_real * fn.index(infl, n)
    a = fn.pv(cash_real, real)
    b = fn.pv(cash_nom, nom_rate)
    c = fn.pv(cash_real, nom_rate)
    d = fn.pv(cash_nom, real)
    lines = ["the same 20 years of 10,000 k u (year-1 money), inflation 2.5 %:",
             f"  real flows at the real rate 5 %:            {a:9,.0f}",
             f"  nominal flows at the nominal rate {nom_rate * 100:.3f} %:  {b:9,.0f}",
             f"  WRONG real flows at the nominal rate:       {c:9,.0f}"
             f"  ({(c / a - 1) * 100:+.1f} %)",
             f"  WRONG nominal flows at the real rate:       {d:9,.0f}"
             f"  ({(d / a - 1) * 100:+.1f} %)",
             f"  real with real and nominal with nominal agree once both are in",
             f"  the same money ({a:,.0f} / 1.025 = {a / 1.025:,.0f}: the real value",
             "  is in year-1 money, the nominal one in today's money);",
             "  mixing them moves the value by about 20 %: every model states",
             "  its convention, its base year and its currency"]
    emit("a_realnominal", lines)


def fx() -> None:
    base = model.run()
    lines = ["a 10 % fall of the local currency before financial close:",
             "  70 % of the capital cost is priced in a hard currency (A-310)",
             "  case                    capex k u   debt k u   equity k u   equity IRR %"]
    for name, k in (("base", 0.0), ("currency -10 %", 0.7 * 0.10 / 0.90)):
        r = model.run(fx_capex=k)
        lines.append(f"  {name:22s} {r['capex']:10,.0f}   {r['debt']:8,.0f}   {r['equity']:10,.0f}"
                     f"   {r['equity_irr'] * 100:12.2f}")
    lines += ["  the debt is sized on the cash flows, which did not change:",
              "  the whole increase lands on the equity; hedging the",
              "  currency until the price is fixed, or a tariff indexed to",
              "  the hard currency, moves this risk elsewhere (section E)"]
    emit("a_fx", lines)


def cleaning() -> None:
    """Cleaning strategies over 25 years on lifecycle cost: chapter 15's
    recovered energy and running cost, plus a robot's capital and
    upkeep, water price and a water shortage that stops truck cleaning
    for 60 days a year (teaching, A-305)."""
    t = T["tariff"]
    n = 25
    years = np.arange(1, n + 1)
    infl = fn.index(T["inflation"], n)
    tar = t * fn.index(T["tariff_index"], n)
    pol = {                  # recovered MWh/yr, running k u/yr, water m3/yr, capital k u
        "truck every 30 d": (7_514, 197, 1_310, 0.0),
        "truck at 4 % loss": (8_992, 229, 1_529, 0.0),
        "robot every 12 d": (9_255, 98, 0, 2_600.0),
    }
    lines = ["cleaning strategies on 25-year lifecycle cost (NPV at 7.5 %):",
             "  policy               capital   energy value   running+water   NPV k u",
             "  (water 3 u/m3; robot capital 2,600 k u and 4 % upkeep; A-305)"]
    rows = []
    for name, (mwh, run, water, cap) in pol.items():
        value = mwh * tar / 1000
        cost = (run + water * 3.0 / 1000 + cap * 0.04) * infl
        npv = fn.pv(value - cost, T["wacc"]) - cap
        lines.append(f"  {name:20s} {cap:7,.0f}   {fn.pv(value, T['wacc']):12,.0f}"
                     f"   {fn.pv(cost, T['wacc']):13,.0f}   {npv:7,.0f}")
        rows.append((name.split()[0], f"{npv:.0f}"))
    # water shortage: trucks stop 60 days a year, losing about 1/6 of the recovery
    mwh, run, water, cap = pol["truck at 4 % loss"]
    short = (mwh * (1 - 60 / 365) * tar / 1000) - (run + water * 3.0 / 1000) * infl
    lines += [f"  truck at 4 % with a 60-day water shortage each year: NPV "
              f"{fn.pv(short, T['wacc']):,.0f}",
              "  the robot recovers the most energy and is immune to water",
              "  shortage, but its capital must be paid back: on lifecycle",
              "  cost the trigger truck wins here, even with a yearly water",
              "  shortage; judged on energy alone the robot would win; a",
              "  lower robot price, a higher tariff or a longer shortage turns",
              "  the answer (D-014 revisited)"]
    emit("a_cleaning", lines)


if __name__ == "__main__":
    capex()
    sources_uses()
    opex()
    real_nominal()
    fx()
    cleaning()
