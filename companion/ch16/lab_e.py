"""Chapter 16, lab E - from the yield distribution to financing cases:
cash flow available for debt service by case, a level-annuity debt sized
on cover ratios, debt against the uncertainty, the value of measuring
better, downside cases that are not P-values, a delivery guarantee at
the P90, and a two-plant portfolio.

Teaching values only (A-281): price 50 u/MWh, operating cost 4,000 k u
a year, interest 6 %, 15 years, cover ratios P50 1.30, P90 (one year)
1.20, P99 (one year) 1.05. They are not market terms; lenders set their
own cases and ratios.

Run from the project root:   python -m companion.ch16.lab_e
Writes companion/ch16/expected/e_*.txt and diagrams/data/ch16-*.csv.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch16 import lab_d, sources as src
from companion.ch16.common import csv, emit
from plantp import yieldrisk as yr

PRICE, OPEX, RATE, YEARS = 50.0, 4000.0, 0.06, 15
DSCR = {"P50": 1.30, "P90 1y": 1.20, "P99 1y": 1.05}


def energies(sig1: float) -> dict:
    p50 = src.base()["net"]
    return {"P50": p50, "P90 1y": p50 - 1.2816 * sig1, "P99 1y": p50 - 2.3263 * sig1}


def cfads(e_gwh: float, price=PRICE, opex=OPEX) -> float:
    return e_gwh * price - opex                      # k u a year (GWh x u/MWh = k u)


def sig_one_year(it=None) -> float:
    return lab_d.total(it or lab_d.items()) * src.sigmas()["ratio"]


def cases() -> None:
    e = energies(sig_one_year())
    cf = {k: cfads(v) for k, v in e.items()}
    debt, bind = yr.debt_size(cf, DSCR, RATE, YEARS)
    lines = ["financing cases (teaching terms A-281; k u = thousand units):",
             "  case      energy GWh   CFADS k u   ratio   debt it allows k u"]
    rows = []
    for k in e:
        d_k = cf[k] / DSCR[k] * yr.annuity(RATE, YEARS)
        rows.append((k, f"{cf[k]:.0f}", f"{cf[k] / DSCR[k]:.0f}"))
        lines.append(f"  {k:8s}   {e[k]:8.2f}    {cf[k]:8,.0f}    {DSCR[k]:4.2f}     {d_k:10,.0f}")
    ds = debt / yr.annuity(RATE, YEARS)
    lines += [f"  debt {debt:,.0f} k u, set by the {bind} case; yearly service {ds:,.0f} k u",
              f"  cover ratio of the P50 case at that debt: {cf['P50'] / ds:.2f}",
              f"  the binding case decides the debt: here {bind}; the others",
              "  have room to spare"]
    emit("e_cases", lines)
    csv("ch16-cases.csv", "k,cf,ds", [(i, c, d) for i, (_, c, d) in enumerate(rows)])


def against_sigma() -> None:
    lines = ["debt against the one-year sigma of the net energy:",
             "  sigma %   debt k u   binding case"]
    rows = []
    p50 = src.base()["net"]
    for u in (0.03, 0.04, 0.05, 0.06, 0.07, 0.08):
        e = energies(u * p50)
        d, bind = yr.debt_size({k: cfads(v) for k, v in e.items()}, DSCR, RATE, YEARS)
        rows.append((f"{100 * u:.0f}", f"{d / 1000:.2f}"))
        lines.append(f"  {100 * u:5.0f}     {d:8,.0f}   {bind}")
    lines += ["  up to about 4.5 % the P50 case binds and uncertainty costs no",
              "  debt; beyond it every point costs about 1,500 k u, and at 8 %",
              "  the P99 case takes over: the owner pays for uncertainty with",
              "  equity once a downside case binds"]
    emit("e_sigma", lines)
    csv("ch16-debt.csv", "u,debt", rows)


def value() -> None:
    p50 = src.base()["net"]
    sig = sig_one_year()
    d0, b0 = yr.debt_size({k: cfads(v) for k, v in energies(sig).items()}, DSCR, RATE, YEARS)
    gain_gwh = 1.59                                   # d_measure, all three
    sig1 = (p50 - (p50 - 1.2816 * sig + gain_gwh)) / 1.2816
    d1, _ = yr.debt_size({k: cfads(v) for k, v in energies(sig1).items()}, DSCR, RATE, YEARS)
    per = (d1 - d0) / gain_gwh
    lines = ["value of measuring better (lab D: +1.59 GWh of one-year P90):",
             f"  sigma {sig:.2f} -> {sig1:.2f} GWh; debt {d0:,.0f} -> {d1:,.0f} k u"
             f" ({d1 - d0:+,.0f} k u)",
             f"  about {per:,.0f} k u of debt per GWh of P90 while the {b0} case binds",
             f"  (= {PRICE:.0f} k u per GWh / {DSCR[b0]:.2f} x annuity factor"
             f" {yr.annuity(RATE, YEARS):.3f})",
             "  set against the cost of a second mast year, a lidar campaign",
             "  and a cleaning routine, and against the delay to financing"]
    emit("e_value", lines)


def downside() -> None:
    sig = sig_one_year()
    e = energies(sig)
    d, _ = yr.debt_size({k: cfads(v) for k, v in e.items()}, DSCR, RATE, YEARS)
    ds = d / yr.annuity(RATE, YEARS)
    lines = ["downside cases that are not P-values (debt fixed as sized):",
             "  case                                        CFADS k u   cover"]
    cs = [("P50 energy", cfads(e["P50"])),
          ("P90 one-year energy", cfads(e["P90 1y"])),
          ("P50 energy, price -10 %", cfads(e["P50"], PRICE * 0.9)),
          ("P50 energy, operating cost +15 %", cfads(e["P50"], opex=OPEX * 1.15)),
          ("P50, 2 % availability below guarantee", cfads(e["P50"] * 0.98)),
          ("P90 1y, price -10 %, cost +15 %", cfads(e["P90 1y"], PRICE * 0.9, OPEX * 1.15))]
    for name, c in cs:
        lines.append(f"  {name:42s} {c:9,.0f}    {c / ds:4.2f}")
    lines += ["  price, cost and contract risks sit beside the energy cases;",
              "  stacking them is a lender's choice, not a P-value"]
    emit("e_downside", lines)


def guarantee() -> None:
    """A delivery guarantee at the one-year P90 with shortfall charged at
    100 u/MWh (A-268): expected yearly cost."""
    p50 = src.base()["net"]
    sig = sig_one_year()
    g = p50 - 1.2816 * sig
    rng = np.random.default_rng(167)
    x = p50 + sig * rng.standard_normal(1_000_000)
    short = np.clip(g - x, 0, None)
    lines = [f"a delivery guarantee at the one-year P90 ({g:.1f} GWh), shortfall at 100 u/MWh:",
             f"  years short: {100 * (short > 0).mean():.1f} %; mean shortfall in those years"
             f" {short[short > 0].mean():.2f} GWh",
             f"  expected cost {short.mean() * 100:,.0f} k u a year; worst 1 % of years"
             f" {np.quantile(short, 0.99) * 100:,.0f} k u",
             "  a P90 is not a promise: one year in ten falls short, and the",
             "  contract decides who pays"]
    emit("e_guarantee", lines)


def portfolio() -> None:
    """Two plants like Plant P whose year-to-year terms correlate (r) and
    whose long-term parts are independent (different masts, A-281)."""
    s = src.sigmas()
    r_ = s["ratio"]
    lt, iav = s["lt"] * r_, s["iav"] * r_
    p50 = src.base()["net"]
    lines = ["two plants like Plant P in one portfolio (one year):",
             "  r of years   portfolio sigma %   P90 of the sum / 2 x single P90"]
    single = p50 - 1.2816 * math.hypot(lt, iav)
    for r in (0.0, 0.5, 0.9):
        sg = math.sqrt(2 * lt ** 2 + 2 * iav ** 2 * (1 + r))
        p90 = 2 * p50 - 1.2816 * sg
        lines.append(f"  {r:9.1f}      {100 * sg / (2 * p50):6.2f} %          {p90 / (2 * single):.4f}")
    lines += ["  plants far apart vary less together: the portfolio P90 is more",
              "  than the sum of single P90s; nearby plants share their weather"]
    emit("e_portfolio", lines)


# [start: yearsbelow]
def years_below() -> None:
    """How many of 15 loan years fall below the one-year P90? Years are
    independent only if the long-term mean is known; with the shared
    long-term error drawn once per project, bad years come together."""
    s = src.sigmas()
    r = s["ratio"]
    lt, iav = s["lt"] * r, s["iav"] * r
    p50 = src.base()["net"]
    p90 = p50 - 1.2816 * math.hypot(lt, iav)
    rng = np.random.default_rng(172)
    n = 200_000
    e_ind = p50 + math.hypot(lt, iav) * rng.standard_normal((n, 15))
    shared = lt * rng.standard_normal((n, 1))          # one per project
    e_sh = p50 + shared + iav * rng.standard_normal((n, 15))
    k_ind = (e_ind < p90).sum(axis=1)
    k_sh = (e_sh < p90).sum(axis=1)
# [end: yearsbelow]
    lines = ["years below the one-year P90 in a 15-year loan (200,000 projects):",
             "  years below   independent years   shared long-term error"]
    rows = []
    for k in (0, 1, 2, 3, 4, 5):
        a, b = float((k_ind == k).mean()), float((k_sh == k).mean())
        rows.append((k, f"{100 * a:.1f}", f"{100 * b:.1f}"))
        lines.append(f"  {k:6d}          {100 * a:6.1f} %             {100 * b:6.1f} %")
    a6, b6 = float((k_ind >= 6).mean()), float((k_sh >= 6).mean())
    lines += [f"  6 or more       {100 * a6:6.1f} %             {100 * b6:6.1f} %",
              f"  mean            {k_ind.mean():6.2f}               {k_sh.mean():6.2f}",
              "  the mean is the same, the tail is not: if the long-term mean is",
              "  lower than estimated, many years fall short together; that is",
              "  the lender's real exposure, and why the long-term part matters"]
    emit("e_yearsbelow", lines)
    rows.append((6, f"{100 * a6:.1f}", f"{100 * b6:.1f}"))
    csv("ch16-yearsbelow.csv", "k,ind,sh", rows)


def two_way() -> None:
    """Debt for prices 40-60 u/MWh against the P90 cover ratio 1.15-1.35
    (other terms as A-281)."""
    sig = sig_one_year()
    e = energies(sig)
    ratios = (1.15, 1.20, 1.25, 1.30, 1.35)
    lines = ["debt (million u) by price and P90 cover ratio (one-year sigma"
             f" {sig:.1f} GWh):",
             "  price u/MWh   " + "   ".join(f"{r:.2f}" for r in ratios)]
    for price in (40, 45, 50, 55, 60):
        row = []
        for rt in ratios:
            dscr = dict(DSCR, **{"P90 1y": rt})
            cf = {k: cfads(v, price) for k, v in e.items()}
            d, _ = yr.debt_size(cf, dscr, RATE, YEARS)
            row.append(f"{d / 1000:5.1f}")
        lines.append(f"  {price:8d}      " + "  ".join(row))
    lines += ["  price moves the debt more than the cover ratio does within",
              "  these ranges: the energy statement is one input of several"]
    emit("e_twoway", lines)


if __name__ == "__main__":
    two_way()
    years_below()
    cases()
    against_sigma()
    value()
    downside()
    guarantee()
    portfolio()
