"""Chapter 21 - the project cash-flow and debt model of Plant P: annual
periods, two construction years before COD, 25 operating years, nominal
money (year-1 prices escalated by inflation), sculpted debt sized by
cover ratios and gearing, DSRA, tax with losses carried forward,
working capital, decommissioning, and the checks an auditor would run.

    from companion.ch21 import model
    r = model.run()                       # base case (S1, P50)
    r = model.run(energy_scale=0.935)     # a downside

Every input comes from companion/ch21/sources.py (teaching values).
"""
from __future__ import annotations

import numpy as np

from companion.ch21 import sources as src
from plantp import finance as fn

T = src.TERMS


# [start: revenue]
def operating_lines(c: dict) -> dict:
    """Energy, price, revenue and costs by operating year (nominal)."""
    n = T["years"]
    yrs = np.arange(1, n + 1)
    infl = fn.index(T["inflation"], n)                  # year 1 = 1.0
    e = src.energy_series(n, c["energy_scale"]) * (1 - T["curtail_uncomp"])
    if c.get("energy_path") is not None:      # yearly factors (Monte Carlo)
        e = e * np.asarray(c["energy_path"])
    e = e - c["curtail_extra"] * e
    ppa = yrs <= T["ppa_years"]
    price = np.where(ppa, c["tariff"] * fn.index(T["tariff_index"], n),
                     T["merchant_real"] * infl * c["merchant_scale"])
    revenue = e * price * c["price_scale"]              # GWh x u/MWh = k u
    revenue = revenue + c["extra_revenue"] * infl
    opex = (sum(src.OPEX.values()) - (0 if c["battery"] else 160.0)) * infl
    opex = opex * c["opex_scale"]
    repl = np.zeros(n)
    for y, (_, cost) in src.REPLACE.items():
        if c["battery"] or "battery" not in _:
            repl[y - 1] += cost * infl[y - 1] * c["repl_scale"]
    decom = np.zeros(n)
    decom[-1] = (src.DECOM["cost"] - src.DECOM["salvage"]) * infl[-1]
    return {"year": yrs, "energy": e, "price": price, "revenue": revenue,
            "opex": opex, "repl": repl, "decom": decom}
# [end: revenue]


DEFAULT = {"energy_scale": 1.0, "tariff": T["tariff"], "price_scale": 1.0,
           "merchant_scale": 1.0, "curtail_extra": 0.0, "extra_revenue": 0.0,
           "opex_scale": 1.0, "repl_scale": 1.0, "capex_scale": 1.0,
           "battery": True, "delay_years": 0, "rate": T["rate"],
           "debt": None, "fx_capex": 0.0, "default_months": 0.0,
           "sizing_price": 1.0, "energy_path": None, "dep_shares": None,
           "sizing_energy": 1.0}     # another site's P50 (ch 22)


# [start: cashflow]
def run(**over) -> dict:
    """The whole model; keyword arguments override DEFAULT."""
    c = dict(DEFAULT, **over)
    op = operating_lines(c)
    n, rate, nd = T["years"], c["rate"], T["tenor"]
    capex = (src.capex_total(c["battery"]) * c["capex_scale"]
             * (1 + c["fx_capex"]))
    ebitda = op["revenue"] - op["opex"]
    # working capital: receivables less payables; its change uses cash
    wc = (op["revenue"] * T["receivable_days"]
          - op["opex"] * T["payable_days"]) / 365
    dwc = np.diff(np.concatenate([[0.0], wc]))
    dwc[-1] -= wc[-1]                         # released at the end
    # a buyer that pays some months of year 3 late (paid in year 4)
    late = op["revenue"][2] * c["default_months"] / 12
    dwc[2] += late
    dwc[3] -= late
    # debt: sized at financial close on the lenders' P50 and P90 cases
    # (CFADS proxy: EBITDA - replacements, less 7 % for tax and WC)
    cf_size = {}
    for case, k in (("P50", 1.0), ("P90 1-yr", src.P90_1Y)):
        o = operating_lines(dict(c, energy_scale=k * c["sizing_energy"],
                                 price_scale=c["sizing_price"],
                                 curtail_extra=0.0, opex_scale=1.0))
        cf = o["revenue"] - o["opex"] - o["repl"]
        cf_size[case] = cf[:nd] * 0.93
    cost_est = capex * 1.06
    targets = {"P50": T["dscr_p50"], "P90 1-yr": T["dscr_p90"]}
    debt, why = fn.size_debt(cf_size, targets, T["rate"], nd, cost_est,
                             T["max_gearing"])
    if c["debt"] is not None:                 # debt fixed at close
        debt = c["debt"]
    # construction: spend, IDC and fee on the debt share
    spend, idc = fn.construction(capex, T["construction"],
                                 rate * debt / cost_est)
    fee = T["fee"] * debt
    # service: sculpted on the sizing case that binds, scaled to debt
    shape = cf_size["P90 1-yr"] if "P90" in why else cf_size["P50"]
    _, i_s, p_s, b_s = fn.sculpted_debt(shape, 1.0, T["rate"])
    k = debt / b_s[0]
    bal = b_s * k
    principal = np.zeros(n)
    principal[:nd] = p_s * k
    interest = np.zeros(n)
    interest[:nd] = bal * rate                # actual rate applies
    ds = interest + principal
    dsra = T["dsra_months"] / 12 * ds[0]      # funded at COD
    uses = capex + idc.sum() + fee + dsra
    equity = uses - debt                      # sources = uses
    # delay: COD later, interest and fixed costs continue
    delay_cost = c["delay_years"] * (sum(src.OPEX.values()) * 0.5
                                     + debt * rate)
    equity += delay_cost
    # tax: capex + IDC + fee depreciated straight line
    dep = fn.straight_line(capex + idc.sum() + fee, T["dep_years"], n)
    if c.get("dep_shares") is not None:       # another depreciation profile
        dep = (capex + idc.sum() + fee) * np.asarray(c["dep_shares"])
    base = ebitda - op["repl"]
    tax = fn.tax_schedule(base, dep, interest, T["tax"])
    tax_u = fn.tax_schedule(base, dep, np.zeros(n), T["tax"])
    cfads = base - tax - dwc - op["decom"]
    dscr = fn.dscr(cfads[:nd], ds[:nd])
    llcr = fn.llcr(cfads, bal, T["rate"], nd)
    # equity pays in during construction and receives what is left;
    # the DSRA comes back with the last debt payment
    eq = cfads - ds
    eq[nd - 1] += dsra
    ph = T["construction"]
    eq_cash = np.concatenate([[-equity * ph[0], -equity * ph[1]], eq])
    # project (unlevered) cash flow: tax as if there were no debt
    proj = np.concatenate([-spend, base - dwc - op["decom"] - tax_u])
    npv = fn.pv(proj[2:], T["wacc"]) - fn.pv(spend, T["wacc"], start=-1)
    return dict(op, capex=capex, idc=idc.sum(), fee=fee, dsra=dsra,
                debt=debt, delay_cost=delay_cost, binding=why,
                equity=equity, uses=uses, ebitda=ebitda, dwc=dwc,
                dep=dep, tax=tax, cfads=cfads, interest=interest,
                principal=principal, ds=ds, dscr=dscr, llcr=llcr,
                balance=bal, eq_cash=eq_cash, gearing=debt / uses,
                equity_irr=fn.irr(eq_cash), project_irr=fn.irr(proj),
                npv=npv, min_dscr=float(np.nanmin(dscr)),
                avg_dscr=float(np.nanmean(dscr)),
                min_llcr=float(np.nanmin(llcr)))
# [end: cashflow]


def checks(r: dict) -> list[tuple[str, bool]]:
    """The audit checks: sources = uses, debt repaid to zero, CFADS
    identity, independent DSCR, no negative cash before distributions."""
    n = T["tenor"]
    rows = list(zip(r["revenue"][:n], r["opex"][:n] + r["repl"][:n] + r["decom"][:n],
                    r["tax"][:n], r["dwc"][:n], r["interest"][:n], r["principal"][:n]))
    ind = np.array(fn.check_dscr(rows))
    uses = r["capex"] + r["idc"] + r["fee"] + r["dsra"]
    eq_in = r["equity"] - r["delay_cost"]
    return [("sources = uses", abs(r["debt"] + eq_in - uses) < 1e-6),
            ("debt repaid within tenor", abs(r["principal"].sum() - r["debt"]) < 1e-6),
            ("CFADS = EBITDA - repl - tax - dWC - decom",
             np.allclose(r["cfads"], r["ebitda"] - r["repl"] - r["tax"] - r["dwc"] - r["decom"])),
            ("independent DSCR equals model DSCR", np.allclose(ind, r["dscr"])),
            ("CFADS covers debt service every year", bool((r["cfads"][:n] >= r["ds"][:n]).all()))]
