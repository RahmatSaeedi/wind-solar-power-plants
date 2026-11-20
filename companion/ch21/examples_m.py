"""Chapter 21, revenue, finance and stress additions: selling part of
the output to a factory behind the meter, a floating rate against a
swap, refinancing after construction, sizing on a ten-year P90, a
Monte Carlo of construction delay against the delay damages, and the
termination payment against the debt outstanding.

Run from the project root:   python -m companion.ch21.examples_m
Writes companion/ch21/expected/m_*.txt and diagrams/data/ch21-*.csv.
Teaching values A-304 to A-310; commercial concepts only.
"""
from __future__ import annotations

import numpy as np

from companion.ch21 import model, sources as src
from companion.ch21.common import csv, emit
from plantp import finance as fn

T = src.TERMS


def self_consumption() -> None:
    """A factory takes 20 GWh a year at 85 u/MWh (its avoided retail
    price less a discount) instead of 70 under the PPA; the factory's
    credit is weaker: lenders count it at 70 % (teaching, A-307)."""
    extra = 20 * (85 - 70)
    r0 = model.run()
    r1 = model.run(extra_revenue=extra)
    r2 = model.run(extra_revenue=extra, sizing_price=1.0 + 0.7 * extra / 20_453 - extra / 20_453)
    lines = ["selling 20 GWh a year to a factory at 85 u instead of 70 u:",
             f"  extra revenue {extra:,.0f} k u a year (year-1 money)",
             f"  equity IRR: PPA only {r0['equity_irr'] * 100:.2f} %,"
             f" with the factory {r1['equity_irr'] * 100:.2f} %",
             "  but the factory can close, move or stop paying: lenders who",
             f"  discount it lend {r2['debt']:,.0f} instead of {r1['debt']:,.0f} k u",
             "  self-consumption needs the connection rules, metering and a",
             "  buyer whose credit is checked like the main offtaker's"]
    emit("m_self", lines)


def hedge() -> None:
    """Floating rate = base rate path + 2 % margin vs a swap fixing the
    whole at 6.2 % (0.2 % cost); three base-rate paths (teaching)."""
    base = model.run()
    paths = {"rates fall": 0.025, "rates flat": 0.04, "rates rise": 0.065}
    lines = ["floating rate against a swap (debt fixed at the base amount):",
             "  path          floating all-in %   min DSCR float   min DSCR swap"]
    rs = model.run(debt=base["debt"], rate=0.062)
    for k, br in paths.items():
        rf = model.run(debt=base["debt"], rate=br + 0.02)
        lines.append(f"  {k:12s} {(br + 0.02) * 100:18.1f}   {rf['min_dscr']:14.2f}   {rs['min_dscr']:13.2f}")
    lines += [f"  equity IRR with the swap {rs['equity_irr'] * 100:.2f} % in every path",
              "  the swap gives up the gain of falling rates to remove the",
              "  loss of rising ones: lenders usually require most of the",
              "  debt hedged, because a rise breaks the cover"]
    emit("m_hedge", lines)


def refinance() -> None:
    """After two years of operation the risk is lower: the remaining
    debt is refinanced at 5 % with a new 15-year tenor sculpted at DSCR
    1.30; the extra debt (less a 1 % fee) goes to the owners."""
    r = model.run()
    k = 2                                       # after operating year 2
    cf = r["cfads"][k:k + 15]
    new_debt, i_n, p_n, b_n = fn.sculpted_debt(cf, src.TERMS["dscr_p50"], 0.05)
    old = r["balance"][k]
    release = new_debt - old - 0.01 * new_debt
    eq = r["cfads"] - r["ds"]                   # operating years 1..25
    eq[k:k + 15] = r["cfads"][k:k + 15] - (i_n + p_n)
    eq[k] += release + r["dsra"]                # old DSRA freed, new one
    eq[k] -= 0.5 * (i_n[0] + p_n[0])            # funded from the release
    eq[k + 14] += 0.5 * (i_n[0] + p_n[0])
    ph = T["construction"]
    eq_cash = np.concatenate([[-r["equity"] * ph[0], -r["equity"] * ph[1]], eq])
    lines = ["refinancing after two years (5 %, new 15 years, DSCR 1.30, fee 1 %):",
             f"  debt outstanding {old:,.0f} k u; new debt {new_debt:,.0f}",
             f"  released to owners {release:,.0f} k u at the start of year 3",
             f"  equity IRR {r['equity_irr'] * 100:.2f} % -> {fn.irr(eq_cash) * 100:.2f} %"
             " (with the new service to year 17)",
             "  refinancing is an upside the owner may take when the market",
             "  allows; the base case never assumes it, and lenders limit it"]
    emit("m_refinance", lines)


def p90_10y() -> None:
    lines = ["sizing on a one-year or a ten-year P90 (DSCR 1.20, sculpted):",
             "  case             P90 / P50   debt k u   gearing %"]
    for name, k in (("one-year P90", 276.0 / 295.14), ("ten-year P90", 280.0 / 295.14)):
        keep = src.P90_1Y
        src.P90_1Y = k
        r = model.run()
        src.P90_1Y = keep
        lines.append(f"  {name:16s} {k:9.3f}   {r['debt']:8,.0f}   {r['gearing'] * 100:9.1f}")
    lines += ["  the ten-year P90 is higher because yearly variation averages",
              "  out (ch 16); which one is used, and at which cover, is the",
              "  lenders' choice - the one-year P90 protects a single bad",
              "  year, the ten-year one the loan as a whole"]
    emit("m_p90", lines)


def delay_mc() -> None:
    """Construction delay in months: 60 % none, else lognormal median 3;
    delay costs 2,487 k u a month (section C); LDs pay 1,995 a month up
    to a 6.7-month cap; owners carry the rest (teaching)."""
    rng = np.random.default_rng(2131)
    n = 100_000
    late = rng.random(n) > 0.6
    months = np.where(late, np.exp(np.log(3) + 0.8 * rng.standard_normal(n)), 0.0)
    cost = months * 2_487
    ld = np.minimum(months, 13_298 / 1_995) * 1_995
    kept = cost - ld
    lines = ["construction delay as a distribution (100,000 draws):",
             f"  chance of any delay 40 %; P50 of a delay when late {np.median(months[late]):.1f} months",
             "  quantity            mean k u    P90 k u    P99 k u",
             f"  delay cost       {cost.mean():10,.0f} {np.percentile(cost, 90):10,.0f} {np.percentile(cost, 99):10,.0f}",
             f"  LDs received     {ld.mean():10,.0f} {np.percentile(ld, 90):10,.0f} {np.percentile(ld, 99):10,.0f}",
             f"  kept by owners   {kept.mean():10,.0f} {np.percentile(kept, 90):10,.0f} {np.percentile(kept, 99):10,.0f}",
             "  the LDs cover most of an ordinary delay; the tail beyond",
             "  the cap is the owners' - sized by the standby equity or a",
             "  delay-in-start-up insurance (lenders' condition precedent)"]
    emit("m_delay", lines)
    hist, edges = np.histogram(months[late], bins=np.arange(0, 16, 1))
    csv("ch21-delay.csv", "m,n", [(f"{a + 0.5:.1f}", int(h)) for a, h in zip(edges[:-1], hist)])


def termination() -> None:
    """Buyer default terminates the PPA; the termination payment is the
    debt outstanding plus 50 % of the equity's book value (teaching)."""
    r = model.run()
    lines = ["termination payment on buyer default: debt + 50 % of equity",
             "  year   debt outstanding   payment   equity loses (book)"]
    eq_book = r["equity"]
    for y in (1, 5, 10, 15):
        debt = r["balance"][y - 1]
        book = eq_book * (1 - (y - 1) / 25)
        pay = debt + 0.5 * book
        lines.append(f"  {y:4d}   {debt:16,.0f}   {pay:7,.0f}   {0.5 * book:19,.0f}")
    lines += ["  lenders need the payment to cover the debt at any time; the",
              "  owners accept a loss on equity - and the payment is worth",
              "  only what the buyer (or its guarantor) can actually pay"]
    emit("m_termination", lines)


if __name__ == "__main__":
    self_consumption()
    hedge()
    refinance()
    p90_10y()
    delay_mc()
    termination()
