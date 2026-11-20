"""Chapter 54, lesson E: finance and fiscal sources of the fictional Country
Z - the source register by status, what goes into the base case, and the
chapter 21 model run with items that are not yet verified: a production
premium sized into the debt, a tax-depreciation rule, a currency that
weakens against the debt, dividends held in the country, and a
withholding tax grossed up on interest. Sensitivities, never advice.

Run from the project root:   python -m companion.ch54.examples_e
Writes companion/ch54/expected/e_*.txt and diagrams/data/ch54-fx.csv.
Fictional teaching values (A-550); model and terms of chapter 21.
"""
from __future__ import annotations

import numpy as np

from companion.ch21 import model
from companion.ch54 import sources as src
from companion.ch54.common import csv, emit
from plantp import finance as fn

PREMIUM = 5.0            # u/MWh, draft regulation (to-confirm)
TARIFF = 70.0            # u/MWh (ch 21)
FX_WEAKEN = 0.04         # local currency loses 4 % a year against the debt's
WHT = 0.10               # withholding tax on interest, grossed up


def base() -> dict:
    return model.run()


# ------------------------------------------------ E1. the register
def register() -> dict:
    by = {}
    for item, kind, st, who in src.FINANCE:
        by[st] = by.get(st, 0) + 1
    lines = [f"finance and fiscal sources of the project ({len(src.FINANCE)} items,"
             " fictional)"]
    for item, kind, st, who in src.FINANCE:
        lines.append(f"  {item:40s} {st}")
        lines.append(f"      source: {kind}; review: {who}")
    rule = {"verified": "base case", "project-dependent": "base case, flagged",
            "to-confirm": "sensitivity only"}
    lines += ["  rule for the model:"]
    lines += [f"    {k:18s} -> {v} ({by.get(k, 0)} items)" for k, v in rule.items()]
    emit("e_register", lines)
    return by


# ------------------------------------------------ E2. a premium sized into debt
def premium() -> dict:
    b = base()
    k = 1 + PREMIUM / TARIFF
    with_p = model.run(price_scale=k, sizing_price=k)
    fails = model.run(debt=with_p["debt"])
    lines = [f"production premium of {PREMIUM:.0f} u/MWh from a draft regulation",
             f"  {'case':38s} {'debt':>8s} {'min DSCR':>9s} {'equity IRR':>11s}",
             f"  {'base (no premium)':38s} {b['debt']:8,.0f} {b['min_dscr']:9.2f}"
             f" {b['equity_irr']:11.1%}",
             f"  {'premium in the base, debt sized on it':38s} {with_p['debt']:8,.0f}"
             f" {with_p['min_dscr']:9.2f} {with_p['equity_irr']:11.1%}",
             f"  {'same debt, premium never paid':38s} {fails['debt']:8,.0f}"
             f" {fails['min_dscr']:9.2f} {fails['equity_irr']:11.1%}",
             f"  sizing binds on: base {b['binding']}; with premium {with_p['binding']}",
             f"  an unverified premium buys {with_p['debt'] - b['debt']:,.0f} k u more debt;"
             " if it never",
             f"  comes the minimum DSCR is {fails['min_dscr']:.2f}: "
             + ("below" if fails['min_dscr'] < 1.20 else "above")
             + " the 1.20 sizing target,",
             "  " + ("above" if fails['min_dscr'] >= 1.10 else "below")
             + " the 1.10 lock-up. The equity IRR still rises (more",
             "  leverage): the risk has moved to the lenders, who will not",
             "  take it - an unverified premium belongs in a sensitivity"]
    emit("e_premium", lines)
    return dict(base=b, with_p=with_p, fails=fails)


# ------------------------------------------------ E3. tax depreciation unknown
def depreciation() -> dict:
    n = len(base()["year"])
    fast = np.zeros(n)
    fast[:5] = 0.2
    b = base()
    f = model.run(dep_shares=fast)
    lines = ["tax depreciation rule 'to-confirm': straight line 20 years (base)",
             "against five years (a rule some places allow - not known for Z)",
             f"  straight line 20 yr: equity IRR {b['equity_irr']:.2%}, min DSCR"
             f" {b['min_dscr']:.2f}",
             f"  accelerated 5 yr:    equity IRR {f['equity_irr']:.2%}, min DSCR"
             f" {f['min_dscr']:.2f}",
             f"  the rule moves the equity IRR by {(f['equity_irr'] - b['equity_irr']) * 100:+.2f}"
             " points, and the",
             f"  minimum DSCR to {f['min_dscr']:.2f}: tax deferred is tax paid later,"
             " inside",
             "  the debt's life - worth a tax advisor's written opinion",
             "  before the model is shown"]
    emit("e_dep", lines)
    return dict(base=b, fast=f)


# ------------------------------------------------ E4. currency against the debt
def fx_case(b: dict, weaken: float) -> dict:
    """Revenue converted at a rate weakening by `weaken` a year; the debt
    service stays as fixed at close; lost revenue after 25 % tax."""
    n = len(b["year"])
    path = (1 - weaken) ** np.arange(n)
    lost = b["revenue"] * (1 - path) * (1 - 0.25)
    cfads = b["cfads"] - lost
    nd = len(b["dscr"])
    dscr = cfads[:nd] / b["ds"][:nd]
    eq = b["eq_cash"].copy()
    eq[2:] -= lost
    below = np.flatnonzero(dscr < 1.10)
    short = np.flatnonzero(dscr < 1.00)
    return dict(dscr=dscr, min=float(dscr.min()), irr=fn.irr(eq),
                below=len(below), first=int(below[0]) + 1 if len(below) else None,
                short=int(short[0]) + 1 if len(short) else None)


def currency() -> dict:
    b = base()
    nd = len(b["dscr"])
    cases = {w: fx_case(b, w) for w in (0.02, FX_WEAKEN)}
    csv("ch54-fx.csv", "year,base,fx2,fx4",
        [(i + 1, round(float(b["dscr"][i]), 3), round(float(cases[0.02]["dscr"][i]), 3),
          round(float(cases[FX_WEAKEN]["dscr"][i]), 3)) for i in range(nd)])
    lines = ["tariff paid in local currency, debt in another; the local currency",
             "weakens each year and the tariff is not indexed to it (revenue",
             "converted at the year's rate, debt service as fixed at close,",
             "lost revenue after 25 % tax; costs left alone - teaching case)",
             f"  {'case':14s} {'min DSCR':>9s} {'years < 1.10':>13s} {'first':>6s}"
             f" {'equity IRR':>11s}",
             f"  {'base':14s} {b['min_dscr']:9.2f} {0:13d} {'-':>6s}"
             f" {b['equity_irr']:11.1%}"]
    for w, c in cases.items():
        irr = "none" if np.isnan(c["irr"]) else format(c["irr"], ".1%")
        lines.append(f"  {'weakens ' + format(w, '.0%'):14s} {c['min']:9.2f} {c['below']:13d}"
                     f" {str(c['first'] or '-'):>6s} {irr:>11s}")
    c2 = cases[0.02]
    lines += [f"  even 2 % a year leaves cash short of debt service from year"
              f" {c2['short']}:",
              "  a currency clause is a debt question, not a footnote"]
    lines += ["  what to verify: the PPA's currency and indexation clause, the",
             "  convertibility rule and who carries the risk - sources, not",
             "  a forecast of the rate"]
    emit("e_fx", lines)
    return dict(base=b, cases=cases)


# ------------------------------------------------ E5. dividends held in the country
def repatriation(hold: int = 2) -> dict:
    b = base()
    eq = b["eq_cash"].copy()
    held = eq.copy()
    # distributions of operating years 1-3 (index 2-4) leave two years late
    for i in (2, 3, 4):
        held[i + hold] += held[i]
        held[i] = 0.0
    irr0, irr1 = fn.irr(eq), fn.irr(held)
    lines = [f"dividends of operating years 1-3 held {hold} years by a transfer rule",
             f"  equity IRR {irr0:.2%} -> {irr1:.2%} ({(irr1 - irr0) * 100:+.2f} points),"
             " no money lost",
             "  only time - the rule, its exceptions and any fee are a",
             "  question for local counsel and the central bank's text"]
    emit("e_repat", lines)
    return dict(irr0=irr0, irr1=irr1)


# ------------------------------------------------ E6. withholding tax grossed up
def withholding() -> dict:
    b = base()
    rate = 0.06 / (1 - WHT)
    w = model.run(rate=rate, debt=b["debt"])
    lines = [f"withholding tax of {WHT:.0%} on interest, grossed up for a foreign lender:",
             f"  interest {0.06:.2%} -> {rate:.2%} for the same net return to the lender",
             f"  min DSCR {b['min_dscr']:.2f} -> {w['min_dscr']:.2f};"
             f" equity IRR {b['equity_irr']:.1%} -> {w['equity_irr']:.1%}",
             "  whether the tax applies, at what rate and whether a treaty",
             "  reduces it are 'to-confirm' items for the tax advisor"]
    emit("e_wht", lines)
    return dict(base=b, w=w, rate=rate)


# ------------------------------------------------ E7. the advisors' review log
def advisors() -> dict:
    open_ = {}
    for item, kind, st, who in src.FINANCE:
        if st != "verified":
            for w in who.split(" + "):
                open_.setdefault(w, []).append(item)
    lines = ["open items by the qualified reviewer who must close them"]
    for w, items in sorted(open_.items(), key=lambda kv: -len(kv[1])):
        lines.append(f"  {w:22s} {len(items)}")
        lines += [f"      {i}" for i in items]
    lines += ["  the model owner does not close these items; each closes with",
              "  a dated written opinion filed against its register line"]
    emit("e_advisors", lines)
    return open_


if __name__ == "__main__":
    register()
    premium()
    depreciation()
    currency()
    repatriation()
    withholding()
    advisors()
