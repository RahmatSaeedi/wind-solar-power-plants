"""Chapter 21, more foundations and measures: a tariff indexed below
inflation, the WACC built from its parts, a sinking fund for
decommissioning, a Monte Carlo of the cover and the equity return with
yearly and shared energy uncertainty, and the option to add the battery
later instead of now.

Run from the project root:   python -m companion.ch21.examples_h
Writes companion/ch21/expected/h_*.txt and diagrams/data/ch21-*.csv.
Teaching values A-304 to A-310; energy uncertainty from ch 16 (D-020).
"""
from __future__ import annotations

import numpy as np

from companion.ch21 import model, sources as src
from companion.ch21.common import csv, emit
from plantp import finance as fn

T = src.TERMS


def indexation() -> None:
    lines = ["real value of the tariff when it is indexed below inflation:",
             "  inflation %   tariff index %   real tariff year 10   year 20"]
    rows = []
    for infl in (0.025, 0.04, 0.06):
        real10 = T["tariff"] * (1.02 / (1 + infl)) ** 9
        real20 = T["tariff"] * (1.02 / (1 + infl)) ** 19
        lines.append(f"  {infl * 100:11.1f}   {2.0:14.1f}   {real10:19.1f}   {real20:7.1f}")
    for y in range(1, 21):
        rows.append((y, f"{T['tariff'] * (1.02 / 1.025) ** (y - 1):.2f}",
                     f"{T['tariff'] * (1.02 / 1.06) ** (y - 1):.2f}"))
    r = model.run()
    hi = dict(T)
    T["inflation"] = 0.06
    r6 = model.run(debt=r["debt"])
    T.update(hi)
    lines += [f"  model with 6 % inflation (debt fixed): min DSCR {r6['min_dscr']:.2f},"
              f" equity IRR {r6['equity_irr'] * 100:.1f} %",
              "  costs rise with inflation, the tariff with its index: when",
              "  inflation runs ahead of the index the margin shrinks year",
              "  by year - indexation is a price term worth negotiating"]
    emit("h_indexation", lines)
    csv("ch21-index.csv", "y,i25,i60", rows)


def wacc() -> None:
    r = model.run()
    g = r["gearing"]
    re, rd, t = T["cost_of_equity"], T["rate"], T["tax"]
    w = (1 - g) * re + g * rd * (1 - t)
    lines = ["the weighted average cost of capital from its parts:",
             f"  equity {1 - g:.2f} x {re * 100:.1f} % + debt {g:.2f} x {rd * 100:.1f} % x (1 - {t:.2f})",
             f"  = {w * 100:.2f} %; the model's 7.5 % adds a margin for project",
             "  risk above this textbook figure (A-310)",
             "  NPV of the project at several rates (k u):"]
    proj = np.concatenate([[-0.4 * r["capex"], -0.6 * r["capex"]],
                           r["ebitda"] - r["repl"] - r["dwc"] - r["decom"]])
    for k in (0.06, w, 0.075, 0.09):
        npv = float((proj / (1 + k) ** np.arange(-1, proj.size - 1)).sum())
        lines.append(f"    {k * 100:5.2f} %   {npv:9,.0f}")
    lines += ["  (pre-tax project cash flow; the post-tax NPV of section B is",
              "  lower) - a point of discount rate moves the NPV by tens of",
              "  millions: the rate is an assumption to state and defend"]
    emit("h_wacc", lines)


def decom_fund() -> None:
    cost = (src.DECOM["cost"] - src.DECOM["salvage"]) * fn.index(T["inflation"], 25)[-1]
    lines = ["sinking fund for decommissioning (paid in years 21-25, earns 3 %):",
             f"  net cost in year 25 money: {cost:,.0f} k u"]
    for years in (5, 10):
        a = cost * 0.03 / ((1.03) ** years - 1)
        lines.append(f"  {years:2d} yearly deposits of {a:,.0f} k u")
    lines += ["  authorities or landowners may require the fund or a bond",
              "  from the start; a fund that starts late costs more each",
              "  year but less in present value - and is at risk if the",
              "  plant stops early"]
    emit("h_decom", lines)


# [start: mc]
def monte_carlo(n: int = 400, seed: int = 2121):
    """Equity IRR and minimum DSCR with energy drawn each year (one-year
    spread 5.1 %, of which 3.6 % shared over the life and the rest
    yearly; ch 16) and the debt fixed at the base case."""
    rng = np.random.default_rng(seed)
    base = model.run()
    u_shared, u_year = 0.036, np.sqrt(0.051 ** 2 - 0.036 ** 2)
    irr, mind, lock = [], [], []
    for _ in range(n):
        f = 1 + u_shared * rng.standard_normal()
        scale = f * (1 + u_year * rng.standard_normal(T["years"]))
        r = model.run(debt=base["debt"], energy_scale=1.0,
                      extra_revenue=0.0, energy_path=scale)
        irr.append(r["equity_irr"])
        mind.append(r["min_dscr"])
        lock.append(int((r["dscr"] < T["lockup"]).sum()))
    return np.array(irr), np.array(mind), np.array(lock)
# [end: mc]


def mc() -> None:
    irr, mind, lock = monte_carlo()
    lines = ["Monte Carlo of the base case, 400 draws, debt fixed:",
             "  quantity           P10      P50      P90",
             f"  equity IRR %   {np.percentile(irr, 10) * 100:7.2f}  {np.percentile(irr, 50) * 100:7.2f}"
             f"  {np.percentile(irr, 90) * 100:7.2f}",
             f"  min DSCR       {np.percentile(mind, 10):7.2f}  {np.percentile(mind, 50):7.2f}"
             f"  {np.percentile(mind, 90):7.2f}",
             f"  draws with at least one lock-up year: {(lock > 0).mean() * 100:.0f} %",
             f"  draws with a DSCR below 1.00: {(mind < 1.0).mean() * 100:.1f} %",
             "  one bad year alone rarely locks up; a low long-term resource",
             "  (the shared part) plus a bad year does: lenders size on P90,",
             "  owners should read the whole distribution"]
    emit("h_mc", lines)
    hist, edges = np.histogram(mind, bins=np.arange(0.80, 1.61, 0.04))
    csv("ch21-mc.csv", "x,n", [(f"{(a + b) / 2:.2f}", int(h)) for a, b, h in
                              zip(edges[:-1], edges[1:], hist)])


def battery_option() -> None:
    """Build the battery now, or keep the option to add it in year 5 if
    a time-of-day tariff arrives (probability p), at 15 % lower cost but
    with 10 % extra for building into a running plant (teaching)."""
    s0 = model.run(battery=False)
    now = model.run(extra_revenue=src.SHIFT_VALUE * 70 / 50)
    bess_cap = (src.capex_total() - src.capex_total(False))
    tod = src.SHIFT_VALUE * 70 / 50
    infl = fn.index(T["inflation"], 25)
    later_cost = bess_cap * 0.85 * 1.10
    gain = fn.pv(tod * infl[5:] - 160 * infl[5:], T["wacc"]) / (1 + T["wacc"]) ** 5
    lines = ["the battery now or as an option in year 5 (NPV at 7.5 %, k u):",
             f"  build now under a time-of-day PPA: equity IRR {now['equity_irr'] * 100:.2f} %"
             f" (S0 {s0['equity_irr'] * 100:.2f} %)",
             f"  adding it in year 5 costs {later_cost:,.0f} k u then,"
             f" PV {later_cost / (1 + T['wacc']) ** 5:,.0f}",
             f"  PV of its shifting value from year 6: {gain:,.0f}",
             "  chance of a time-of-day tariff   value of waiting k u"]
    for p in (0.25, 0.5, 0.75, 1.0):
        v = p * max(0.0, gain - later_cost / (1 + T["wacc"]) ** 5)
        lines.append(f"  {p * 100:31.0f} %   {v:18,.0f}")
    lines += ["  at these teaching prices the late battery costs more than",
              "  its shifting value, so the option is worth nothing - and",
              "  building now lowers the equity return even with a time-of-day",
              "  tariff: the battery pays only with a wider price spread, a",
              "  service contract, or a requirement (island, grid operator);",
              "  keeping space and a bay ready (chapter 18) keeps the option"]
    emit("h_option", lines)


if __name__ == "__main__":
    indexation()
    wacc()
    decom_fund()
    mc()
    battery_option()
