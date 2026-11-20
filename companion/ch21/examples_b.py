"""Chapter 21, section B - economic measures and uncertainty: NPV and
IRR of the project and of the equity (and a cash flow with two IRRs),
levelised cost and what it hides, tariff structures and the variability
of revenue they leave to the owner, curtailment risk, availability
guarantees, and a tornado of what moves the equity return and the cover.

Run from the project root:   python -m companion.ch21.examples_b
Writes companion/ch21/expected/b_*.txt and diagrams/data/ch21-*.csv.
Teaching values A-304 to A-310; inter-annual energy spread from ch 16.
"""
from __future__ import annotations

import numpy as np

from companion.ch21 import model, sources as src
from companion.ch21.common import csv, emit
from plantp import finance as fn

T = src.TERMS


def measures() -> None:
    r = model.run()
    lines = ["economic and financial measures of the base case (nominal):",
             f"  project IRR after tax, unlevered   {r['project_irr'] * 100:6.2f} %",
             f"  NPV at the 7.5 % WACC              {r['npv']:8,.0f} k u",
             f"  equity IRR                         {r['equity_irr'] * 100:6.2f} %"
             f"  (cost of equity {T['cost_of_equity'] * 100:.0f} %)",
             f"  debt {r['debt']:,.0f} k u at {T['rate'] * 100:.1f} %, gearing {r['gearing'] * 100:.0f} %",
             "  the project earns more than the debt costs, so leverage",
             "  lifts the equity return above the project return; the NPV",
             "  asks whether value is created, the equity IRR whether the",
             "  owners are paid for their risk - two questions"]
    cash = [-100, 230, -132]
    r1 = fn.irr(cash, -0.5, 0.15)
    r2 = fn.irr(cash, 0.15, 1.0)
    lines += ["a cash flow with two sign changes (-100, +230, -132):",
              f"  IRR {r1 * 100:.1f} % and IRR {r2 * 100:.1f} % both make NPV zero:",
              "  a decommissioning cost or a late replacement can do this;",
              "  report NPV at a stated rate, not only IRR"]
    emit("b_measures", lines)
    proj = np.concatenate([[-0.4 * r["capex"], -0.6 * r["capex"]],
                           r["ebitda"] - r["repl"] - r["dwc"] - r["decom"]])
    csv("ch21-npv.csv", "rate,npv",
        [(f"{k:.3f}", f"{float((proj / (1 + k) ** np.arange(-1, proj.size - 1)).sum()) / 1000:.2f}")
         for k in np.arange(0.0, 0.1501, 0.0075)])


def lcoe() -> None:
    lines = ["levelised cost of energy, real, at a 5 % real rate:",
             "  case                         LCOE u/MWh"]
    n = 25
    for name, batt in (("S0 (no battery)", False), ("S1 (battery)", True)):
        r = model.run(battery=batt)
        infl = fn.index(T["inflation"], n)
        costs = (r["opex"] + r["repl"] + r["decom"]) / infl
        v = fn.lcoe(src.capex_total(batt), costs, r["energy"], 0.05)
        lines.append(f"  {name:28s} {v:10.1f}")
    lines += ["  the battery raises the cost of each MWh and adds no MWh;",
              "  LCOE cannot see that it moves energy to dearer hours, holds",
              "  reserve or recaptures curtailment; LCOE also hides when",
              "  the energy comes, curtailment of delivered energy, and the",
              "  financing: use it to compare like with like, never to judge",
              "  a battery or a service (section E)"]
    emit("b_lcoe", lines)


def tariffs() -> None:
    """Revenue variability left to the owner under three structures,
    from 20 synthetic years with the chapter 16 one-year spread (5.1 %)."""
    rng = np.random.default_rng(2101)
    e = 295.14 * (1 + 0.051 * rng.standard_normal(2000))
    price_m = 50 * (1 + 0.20 * rng.standard_normal(2000) - 0.4 * (e / 295.14 - 1))
    cases = {"pay-as-produced 70 u": e * 70,
             "fixed volume 280 GWh at 66 u": np.full(2000, 280 * 66.0) + (e - 280) * 40,
             "merchant (price falls when windy)": e * price_m}
    lines = ["revenue of a year under three structures (k u, 2,000 draws):",
             "  structure                          mean     P10     spread %"]
    for k, v in cases.items():
        lines.append(f"  {k:33s} {v.mean():7,.0f} {np.percentile(v, 10):7,.0f}"
                     f"   {v.std() / v.mean() * 100:8.1f}")
    lines += ["  (fixed volume: shortfall bought and surplus sold at 40 u)",
              "  pay-as-produced leaves the resource risk with the owner;",
              "  a fixed volume moves it to the owner's balancing, and a",
              "  merchant revenue adds price risk; lenders size debt on the",
              "  P90 of the revenue the structure leaves (section F)"]
    emit("b_tariffs", lines)


def curtailment() -> None:
    lines = ["uncompensated curtailment beyond the 1 % of the base case:",
             "  extra %   min DSCR   equity IRR %"]
    for x in (0.0, 0.02, 0.04, 0.06):
        r = model.run(curtail_extra=x)
        lines.append(f"  {x * 100:7.0f}   {r['min_dscr']:8.2f}   {r['equity_irr'] * 100:12.2f}")
    lines += ["  each 2 % of unpaid curtailment costs about half a point of",
              "  equity return and 0.03 of cover; whether curtailment is paid",
              "  (deemed energy) or not is a contract term that lenders read",
              "  first (section E)"]
    emit("b_curtail", lines)


def availability() -> None:
    """O&M availability guarantee 97 %: shortfall paid as liquidated
    damages at the tariff, capped at 20 % of the O&M fee (teaching)."""
    fee = 1_800.0 + 500.0
    lines = ["availability guarantee of the O&M contract (97 %, LD at tariff,",
             "cap 20 % of the O&M fee; teaching, A-308):",
             "  availability %   lost GWh   lost k u   LD paid k u   owner keeps loss k u"]
    for a in (0.97, 0.96, 0.95, 0.93):
        lost = max(0.0, 0.97 - a) / 0.97 * 295.14
        loss = lost * 70
        ld = min(loss, 0.2 * fee)
        lines.append(f"  {a * 100:14.0f}   {lost:8.1f}   {loss:8,.0f}   {ld:11,.0f}   {loss - ld:20,.0f}")
    a_cap = 0.97 - 0.2 * fee / 70 / 295.14 * 0.97
    lines += [f"  the cap limits what the contractor pays: below about {a_cap * 100:.1f} %",
              "  the owner carries the rest; a guarantee is worth what the",
              "  cap and the contractor's balance sheet make it"]
    emit("b_availability", lines)


def tornado() -> None:
    base = model.run()
    cases = [("energy", "energy_scale", 0.9, 1.1), ("tariff", "price_scale", 0.9, 1.1),
             ("capex", "capex_scale", 1.1, 0.9), ("opex", "opex_scale", 1.1, 0.9),
             ("debt rate", "rate", T["rate"] + 0.01, T["rate"] - 0.01),
             ("replacements", "repl_scale", 1.5, 0.5)]
    lines = ["what moves the equity IRR and the minimum DSCR (debt fixed):",
             f"  base: equity IRR {base['equity_irr'] * 100:.2f} %, min DSCR {base['min_dscr']:.2f}",
             "  input (bad / good)        equity IRR %         min DSCR"]
    rows = []
    for name, key, bad, good in cases:
        rb = model.run(debt=base["debt"], **{key: bad})
        rg = model.run(debt=base["debt"], **{key: good})
        lines.append(f"  {name:24s} {rb['equity_irr'] * 100:6.2f} / {rg['equity_irr'] * 100:6.2f}"
                     f"   {rb['min_dscr']:5.2f} / {rg['min_dscr']:5.2f}")
        rows.append((len(rows) + 1, f"{(rb['equity_irr'] - base['equity_irr']) * 100:.2f}",
                     f"{(rg['equity_irr'] - base['equity_irr']) * 100:.2f}"))
    lines += ["  (+-10 % on energy, tariff, capex and opex; +-1 point on the",
              "  rate; +-50 % on replacements)",
              "  energy and tariff dominate both measures; capex moves the",
              "  equity return but hardly the cover once the debt is fixed",
              "  (it even rises a little through depreciation and tax); the",
              "  debt rate moves the cover through the debt service"]
    emit("b_tornado", lines)
    csv("ch21-tornado.csv", "k,bad,good", rows)


if __name__ == "__main__":
    measures()
    lcoe()
    tariffs()
    curtailment()
    availability()
    tornado()
