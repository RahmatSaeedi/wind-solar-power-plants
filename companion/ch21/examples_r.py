"""Chapter 21, last lessons: who pays for grid reinforcement, the value
of development spending as a decision tree, the merchant tail after the
PPA, a hard-currency loan against a local one, and full-service against
basic O&M.

Run from the project root:   python -m companion.ch21.examples_r
Writes companion/ch21/expected/r_*.txt.
Teaching values A-304 to A-310; commercial concepts only.
"""
from __future__ import annotations

import numpy as np

from companion.ch21 import model, sources as src
from companion.ch21.common import emit
from plantp import finance as fn

T = src.TERMS


def connection() -> None:
    lines = ["shallow or deep connection charges (reinforcement 10,000 k u):",
             "  regime                       capex k u   tariff for 10 % equity"]
    for name, extra in (("shallow (grid pays)", 0.0), ("deep (plant pays)", 10_000.0)):
        cs = 1 + extra / src.capex_total()
        t = fn.breakeven(lambda x: model.run(tariff=x, capex_scale=cs)["equity_irr"],
                         50.0, 100.0, T["cost_of_equity"])
        lines.append(f"  {name:28s} {src.capex_total() * cs:9,.0f}   {t:22.1f}")
    lines += ["  a deep charge (the plant pays for upstream reinforcement)",
              "  raises the tariff it needs by several units; who pays is set",
              "  by the connection rules and agreement (ch 17, 28, U-081)"]
    emit("r_connection", lines)


# [start: tree]
def development_tree() -> None:
    """Spend in three stages; each stage passes with a probability;
    the built project is worth its NPV (teaching numbers)."""
    stages = [("measurement and studies", 800.0, 0.70),
              ("permits and grid offer", 1_200.0, 0.60),
              ("PPA award and financing", 1_000.0, 0.65)]
    value = 5_159.0 + 3_000.0          # NPV at close + development spent
    ev = value
    for name, cost, p in reversed(stages):
        ev = p * ev - cost
    p_all = np.prod([p for *_, p in stages])
    lines = ["development as a decision tree (k u, no discounting):",
             "  stage                       cost    pass chance"]
    lines += [f"  {n:26s} {c:6,.0f}   {p:11.2f}" for n, c, p in stages]
    lines += [f"  chance of reaching financial close {p_all * 100:.0f} %",
              f"  expected value of starting development {ev:,.0f} k u",
              "  each stage is an option to stop: spending is cheap early",
              "  and grows as the chance of success rises; a developer",
              "  needs a portfolio, because most projects stop"]
    emit("r_tree", lines)
# [end: tree]


def merchant_tail() -> None:
    base = model.run()
    lines = ["the merchant tail (years 21-25) against its price:",
             "  merchant price u (real)   equity IRR %   NPV k u"]
    for m in (30.0, 45.0, 60.0):
        r = model.run(debt=base["debt"], merchant_scale=m / 45.0)
        lines.append(f"  {m:23.0f}   {r['equity_irr'] * 100:12.2f}   {r['npv']:7,.0f}")
    lines += ["  five far years move the equity return little: lenders give",
              "  them no value, owners some; a longer PPA or a floor turns",
              "  them from hope into revenue"]
    emit("r_merchant", lines)


def hard_currency() -> None:
    """A hard-currency loan at 4.5 % against a local one at 6 %; revenue
    in local money; the local currency loses 3 % a year against the
    hard one (teaching). Debt service in local money grows with it."""
    base = model.run()
    n = T["tenor"]
    i, p, b = fn.annuity_debt(base["debt"], 0.045, n)
    fx = (1.03) ** np.arange(1, n + 1)
    ds_local = (i + p) * fx
    dscr = base["cfads"][:n] / ds_local
    i2, p2, b2 = fn.annuity_debt(base["debt"], 0.06, n)
    dscr_l = base["cfads"][:n] / (i2 + p2)
    lines = ["a hard-currency loan (4.5 %) against a local one (6 %), annuity:",
             "  year   DSCR local loan   DSCR hard loan (local money -3 %/yr)"]
    for y in (1, 5, 10, 15):
        lines.append(f"  {y:4d}   {dscr_l[y - 1]:15.2f}   {dscr[y - 1]:34.2f}")
    lines += ["  the cheaper loan starts with better cover and ends below 1:",
              "  a currency that slides moves the debt service up every year;",
              "  only revenue in (or indexed to) the same currency matches it"]
    emit("r_currency", lines)


def om_choice() -> None:
    """Full-service O&M at 3,100 k u a year (parts and repairs included)
    against basic at 1,900 plus repairs: 2 major repairs a year expected
    at 350 each, with a 10 % chance of a 3,000 one (teaching)."""
    rng = np.random.default_rng(2151)
    n = 100_000
    repairs = rng.poisson(2.0, n) * 350.0 + (rng.random(n) < 0.10) * 3_000.0
    basic = 1_900.0 + repairs
    full = np.full(n, 3_100.0)
    lines = ["full-service or basic O&M (k u a year, 100,000 draws):",
             "  contract       mean    P90     P99",
             f"  full service {full.mean():6,.0f} {np.percentile(full, 90):6,.0f} {np.percentile(full, 99):7,.0f}",
             f"  basic        {basic.mean():6,.0f} {np.percentile(basic, 90):6,.0f} {np.percentile(basic, 99):7,.0f}",
             "  basic is cheaper on average and dearer in a bad year; the",
             "  full-service price buys a flat cost line that lenders value;",
             "  the choice also moves the availability guarantee (section B)"]
    emit("r_om", lines)


if __name__ == "__main__":
    connection()
    development_tree()
    merchant_tail()
    hard_currency()
    om_choice()
