"""Chapter 21, closing lessons: the three financial statements of the
first years with a balance check, a spider chart of the equity return,
the tariff to bid for a target return, where the LCOE comes from, a
DSRA held as a letter of credit, curtailment compensation regimes,
life extension after year 25, and a combined Monte Carlo of delay,
cost and energy.

Run from the project root:   python -m companion.ch21.examples_q
Writes companion/ch21/expected/q_*.txt and diagrams/data/ch21-*.csv.
Teaching values A-304 to A-310; accounting simplified (no tax law).
"""
from __future__ import annotations

import numpy as np

from companion.ch21 import model, sources as src
from companion.ch21.common import csv, emit
from plantp import finance as fn

T = src.TERMS


# [start: statements]
def statements(r: dict, years: int = 3) -> list[dict]:
    """Income statement, cash and balance sheet of the first operating
    years (simplified: one fixed asset, receivables net of payables as
    working capital, DSRA cash, senior debt, paid-in equity and
    retained earnings). Distributions = CFADS - debt service."""
    asset = r["capex"] + r["idc"] + r["fee"]
    wc = np.cumsum(r["dwc"])
    retained, rows = 0.0, []
    for t in range(years):
        ebit = r["ebitda"][t] - r["repl"][t] - r["dep"][t]
        ni = ebit - r["interest"][t] - r["tax"][t]
        dist = r["cfads"][t] - r["ds"][t]
        retained += ni - dist
        assets = (asset - r["dep"][:t + 1].sum()) + wc[t] + r["dsra"]
        debt = r["balance"][t] - r["principal"][t]
        rows.append({"ebitda": r["ebitda"][t], "dep": r["dep"][t],
                     "ebit": ebit, "int": r["interest"][t],
                     "tax": r["tax"][t], "ni": ni,
                     "dist": dist, "assets": assets, "debt": debt,
                     "equity": r["equity"] + retained,
                     "gap": assets - debt - r["equity"] - retained})
    return rows
# [end: statements]


def three() -> None:
    r = model.run()
    lines = ["the first three years as statements (k u):",
             "  line                         year 1     year 2     year 3"]
    rows = statements(r)
    for key, name in (("ebitda", "EBITDA"), ("dep", "depreciation"), ("ebit", "EBIT"),
                      ("int", "interest"), ("tax", "tax"), ("ni", "net income"),
                      ("dist", "distributions"), ("assets", "total assets"),
                      ("debt", "debt at year end"), ("equity", "equity (paid + retained)"),
                      ("gap", "assets - debt - equity")):
        lines.append(f"  {name:26s}" + "".join(f" {row[key]:10,.0f}" for row in rows))
    lines += ["  the balance closes (gap 0) only if every cash line of the",
              "  model has its place in the statements: a balance check is",
              "  the strongest identity an auditor runs; distributions above",
              "  net income in the early years shrink the book equity - the",
              "  depreciation is cash the owners take back"]
    emit("q_statements", lines)


def spider() -> None:
    base = model.run()
    keys = [("energy", "energy_scale"), ("tariff", "price_scale"), ("capex", "capex_scale"),
            ("opex", "opex_scale")]
    rows = []
    lines = ["equity IRR % against the change of one input (debt fixed):",
             "  change %   energy   tariff   capex    opex"]
    for d in (-0.2, -0.1, 0.0, 0.1, 0.2):
        vals = []
        for _, key in keys:
            vals.append(model.run(debt=base["debt"], **{key: 1 + d})["equity_irr"] * 100)
        lines.append(f"  {d * 100:8.0f}" + "".join(f" {v:8.2f}" for v in vals))
        rows.append((f"{d * 100:.0f}",) + tuple(f"{v:.3f}" for v in vals))
    lines += ["  energy and tariff are one line; a 20 % fall in either takes",
              "  the equity below the debt rate; capex slopes the other way"]
    emit("q_spider", lines)
    csv("ch21-spider.csv", "d,energy,tariff,capex,opex", rows)


def bid_matrix() -> None:
    lines = ["tariff to bid (u/MWh, year 1) for a 10 % equity IRR (debt resized):",
             "  capex      energy 95 %   energy 100 %   energy 105 %"]
    for cs in (0.9, 1.0, 1.1):
        vals = []
        for es in (0.95, 1.0, 1.05):
            t = fn.breakeven(lambda x: model.run(tariff=x, capex_scale=cs,
                                                 energy_scale=es)["equity_irr"],
                             40.0, 110.0, T["cost_of_equity"])
            vals.append(t)
        lines.append(f"  {cs * 100:4.0f} %   " + "".join(f"{v:12.1f}  " for v in vals))
    lines += ["  a bidder who prices at P50 energy and the base capex bids",
              "  about 69.5; every 5 % of energy or 10 % of capex moves the",
              "  bid by several units - the bid is as good as its inputs"]
    emit("q_bid", lines)


def lcoe_parts() -> None:
    rows = []
    lines = ["where the LCOE comes from (real, 5 %, u/MWh):",
             "  case   capital   O&M   replacements+decom   total"]
    for name, batt in (("S0", False), ("S1", True)):
        r = model.run(battery=batt)
        infl = fn.index(T["inflation"], 25)
        e = fn.pv(r["energy"], 0.05)
        cap = src.capex_total(batt) / e
        om = fn.pv(r["opex"] / infl, 0.05) / e
        rp = fn.pv((r["repl"] + r["decom"]) / infl, 0.05) / e
        lines.append(f"  {name:4s}   {cap:7.1f}   {om:4.1f}   {rp:18.1f}   {cap + om + rp:5.1f}")
        rows.append((1 if name == "S0" else 2, f"{cap:.2f}", f"{om:.2f}", f"{rp:.2f}"))
    lines += ["  capital is about 70 % of the cost of energy: the",
              "  plant is bought, not run - which is why the cost of money",
              "  (the discount rate) moves the LCOE as much as the opex"]
    emit("q_lcoe", lines)
    csv("ch21-lcoe.csv", "x,cap,om,rep", rows)


def dsra_lc() -> None:
    r = model.run()
    fee = 0.02 * r["dsra"]
    eq = r["eq_cash"].copy()
    eq[1] += r["dsra"] * (1 - r["gearing"])        # equity no longer funds it
    eq[2:2 + T["tenor"]] -= fee
    eq[1 + T["tenor"]] -= r["dsra"] * (1 - r["gearing"])
    lines = ["DSRA held as a letter of credit instead of cash:",
             f"  cash DSRA {r['dsra']:,.0f} k u; LC fee 2 % a year = {fee:,.0f} k u",
             f"  equity IRR {r['equity_irr'] * 100:.2f} % -> about {fn.irr(eq) * 100:.2f} %",
             "  the owners keep their money at work and pay a fee; the",
             "  lenders accept an LC from a bank they rate - a credit",
             "  question, not a modelling one"]
    emit("q_dsra_lc", lines)


def curtail_regimes() -> None:
    base = model.run()
    extra = 0.04
    lost = extra * 295.14 * T["tariff"]
    lines = ["4 % grid curtailment under three compensation regimes:",
             "  regime                               revenue lost k u/yr   equity IRR %"]
    for name, unpaid in (("no compensation", extra), ("deemed energy, all", 0.0),
                         ("deemed above 1 % only", 0.01)):
        r = model.run(debt=base["debt"], curtail_extra=unpaid)
        lines.append(f"  {name:36s} {unpaid / extra * lost:19,.0f}   {r['equity_irr'] * 100:12.2f}")
    lines += ["  a threshold (the first hours unpaid) is a common compromise;",
              "  the regime is a PPA or connection-agreement term (U-081)"]
    emit("q_curtail", lines)


def extension() -> None:
    """Five more years after year 25: refurbishment 8 % of capex in year
    25, energy at 0.97 of year 25, merchant price, opex +20 %."""
    r = model.run()
    infl = fn.index(T["inflation"], 30)
    e = r["energy"][-1] * 0.97
    price = T["merchant_real"] * infl[25:30]
    opex = sum(src.OPEX.values()) * 1.2 * infl[25:30]
    cf = e * price - opex
    refurb = 0.08 * r["capex"] * infl[24]
    npv = fn.pv(cf, T["wacc"]) / (1 + T["wacc"]) ** 25 - refurb / (1 + T["wacc"]) ** 25
    lines = ["life extension to 30 years (k u, PV at 7.5 % to today):",
             f"  refurbishment in year 25 {refurb:,.0f}; cash flow years 26-30"
             f" {cf.mean():,.0f} a year",
             f"  NPV of the extension today {npv:,.0f}",
             "  far-off cash flows are worth little today and the merchant",
             "  price is uncertain: an extension is an option for later,",
             "  decided on the plant's condition (ch 53), not a base case"]
    emit("q_extension", lines)


def project_mc() -> None:
    rng = np.random.default_rng(2141)
    base = model.run()
    irr = []
    for _ in range(300):
        delay = 1 if rng.random() < 0.15 else 0
        cap = 1 + max(0.0, 0.05 * rng.standard_normal())
        f = 1 + 0.036 * rng.standard_normal()
        path = f * (1 + 0.036 * rng.standard_normal(T["years"]))
        r = model.run(debt=base["debt"], delay_years=delay, capex_scale=cap,
                      energy_path=path)
        irr.append(r["equity_irr"])
    irr = np.array(irr) * 100
    lines = ["equity IRR with delay (15 % chance of a year), capex overrun",
             "(half-normal 5 %) and energy uncertainty, 300 draws:",
             f"  P10 {np.percentile(irr, 10):.2f} %, P50 {np.percentile(irr, 50):.2f} %,"
             f" P90 {np.percentile(irr, 90):.2f} %; base {base['equity_irr'] * 100:.2f} %",
             f"  draws below the 6 % debt rate: {(irr < 6).mean() * 100:.0f} %",
             "  the median falls below the base: delay and overrun only go",
             "  one way, so the base case is not the expected case"]
    emit("q_project_mc", lines)


if __name__ == "__main__":
    three()
    spider()
    bid_matrix()
    lcoe_parts()
    dsra_lc()
    curtail_regimes()
    extension()
    project_mc()
