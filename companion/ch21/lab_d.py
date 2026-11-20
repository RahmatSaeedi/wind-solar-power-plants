"""Chapter 21, lab D - the model lab: the assumption register the model
reads, the cash flow of selected years, alternatives under different
yield, financing and replacement assumptions (the chapter's worked
example 1), and why the cheapest plant, the highest IRR or one P90
figure does not decide.

Run from the project root:   python -m companion.ch21.lab_d
Writes companion/ch21/expected/d_*.txt and diagrams/data/ch21-*.csv.
"""
from __future__ import annotations

import numpy as np

from companion.ch21 import model, sources as src
from companion.ch21.common import csv, emit

T = src.TERMS


def register() -> None:
    lines = ["assumption register read by the model (all teaching):",
             "  id     what                                       value",
             f"  A-304  capital cost S1 / S0, k u                  {src.capex_total():,.0f} / {src.capex_total(False):,.0f}",
             f"  A-305  operating cost year 1, k u                 {sum(src.OPEX.values()):,.0f}",
             "  A-306  replacements years 8, 12, 13, 15; decommissioning year 25",
             f"  A-307  PPA {T['tariff']:.0f} u/MWh +{T['tariff_index'] * 100:.0f} %/yr for {T['ppa_years']} yr,"
             f" then {T['merchant_real']:.0f} u real",
             f"  A-308  debt {T['rate'] * 100:.0f} %, {T['tenor']} yr, fee {T['fee'] * 100:.1f} %,"
             f" DSCR {T['dscr_p50']:.2f} P50 / {T['dscr_p90']:.2f} P90, gearing <= {T['max_gearing'] * 100:.0f} %",
             f"  A-309  inflation {T['inflation'] * 100:.1f} %, tax {T['tax'] * 100:.0f} % (straight line"
             f" {T['dep_years']} yr), WC {T['receivable_days']}/{T['payable_days']} days",
             f"  A-310  WACC {T['wacc'] * 100:.1f} %, cost of equity {T['cost_of_equity'] * 100:.0f} %,"
             " 70 % of capex in hard currency",
             "  D-019  energy: model 15.1, 295.14 GWh in year 1, PV -0.5 %/yr",
             "  D-020  P90 1-yr 276 GWh; one-year sigma 5.1 %"]
    emit("d_register", lines)


def years() -> None:
    r = model.run()
    sel = [1, 2, 5, 8, 10, 12, 15, 16, 20, 21, 25]
    lines = ["the model by year (k u, nominal; base case S1, P50):",
             "  yr  GWh   u/MWh  revenue   costs    tax   CFADS  service  to equity"]
    rows = []
    for y in sel:
        k = y - 1
        costs = r["opex"][k] + r["repl"][k] + r["decom"][k]
        eq = r["eq_cash"][k + 2]
        lines.append(f"  {y:2d} {r['energy'][k]:5.1f} {r['price'][k]:6.1f} {r['revenue'][k]:8,.0f}"
                     f" {costs:7,.0f} {r['tax'][k]:6,.0f} {r['cfads'][k]:7,.0f}"
                     f" {r['ds'][k]:8,.0f} {eq:10,.0f}")
    for k in range(T["years"]):
        rows.append((k + 1, f"{r['revenue'][k]:.0f}", f"{r['opex'][k] + r['repl'][k] + r['decom'][k]:.0f}",
                     f"{r['tax'][k]:.0f}", f"{r['ds'][k]:.0f}", f"{r['eq_cash'][k + 2]:.0f}"))
    lines += ["  year 15 holds the last debt payment and the DSRA release;",
              "  year 21 the PPA ends and the merchant price is lower; year 25",
              "  pays the decommissioning and returns the working capital"]
    emit("d_years", lines)
    csv("ch21-years.csv", "y,rev,costs,tax,ds,eq", rows)


# [start: alternatives]
TOD = src.SHIFT_VALUE * 70 / 50          # shifting value at the PPA tariff
ALTERNATIVES = [
    ("A  S1, flat PPA (base)", dict()),
    ("B  S0, flat PPA", dict(battery=False)),
    ("C  S1, time-of-day PPA", dict(extra_revenue=TOD)),
    ("D  C, oversize not augment", dict(extra_revenue=TOD,
                                        capex_scale=1 + 2125 / 156450,
                                        repl_scale=3300 / 4500)),
    ("E  C, debt 18 years", dict(extra_revenue=TOD)),
    ("F  C, thin cover, 85 % debt", dict(extra_revenue=TOD)),
]
# [end: alternatives]


def alternatives() -> None:
    lines = ["worked example 1: alternatives (k u; debt sized on each case):",
             "  case                           capex     debt  eq.IRR%  minDSCR  P90DSCR"]
    rows = []
    for name, kw in ALTERNATIVES:
        keep = dict(T)                                 # restore after each case
        if name.startswith("E"):
            T["tenor"] = 18
        if name.startswith("F"):                       # aggressive sizing
            T.update(dscr_p50=1.10, dscr_p90=1.00, max_gearing=0.85)
        r = model.run(**kw)
        p90 = model.run(debt=r["debt"], energy_scale=src.P90_1Y, **kw)
        T.update(keep)
        cap = "G" if r["binding"] == "gearing" else "D"
        lines.append(f"  {name:28s} {r['capex']:8,.0f} {r['debt']:7,.0f}{cap}  {r['equity_irr'] * 100:7.2f}"
                     f"  {r['min_dscr']:7.2f}  {p90['min_dscr']:7.2f}")
        rows.append((name[0], f"{r['equity_irr'] * 100:.2f}", f"{p90['min_dscr']:.3f}"))
    lines += ["  (P90 DSCR: the same debt with a P90 resource in every year;",
              "  debt set by G the gearing cap or D the cover target)",
              "  B has the lowest cost and a high IRR but no flexibility; C",
              "  pays for the battery only if the tariff values the hour; D",
              "  trades capital for fewer replacements and gains nothing",
              "  here; E spreads the same debt over 18 years: higher cover",
              "  and a higher equity IRR, if lenders offer the tenor; F takes",
              "  more debt on a thin cover: its equity IRR rises from 11.35 to",
              "  12.60 % while its P90 cover falls to 1.01, deep in lock-up -",
              "  a higher IRR bought with risk is not a better project"]
    emit("d_alternatives", lines)
    csv("ch21-alternatives.csv", "k,irr,p90", rows)


if __name__ == "__main__":
    register()
    years()
    alternatives()
