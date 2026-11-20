"""Chapter 21, section E - revenue pathways and bankability: the same
plant under a pay-as-produced PPA, a time-of-day PPA, a bilateral fixed
price on part of the output and a merchant sale; a reserve service and
a carbon credit shown only as labelled sensitivities; and payment
security against a buyer that pays late.

No market, service product or carbon scheme is assumed to exist in any
country: each line is a 'what if' with teaching numbers (A-307, A-310).

Run from the project root:   python -m companion.ch21.examples_e
Writes companion/ch21/expected/e_*.txt.
"""
from __future__ import annotations

import numpy as np

from companion.ch21 import model, sources as src
from companion.ch21.common import emit
from plantp import finance as fn

T = src.TERMS


def pathways() -> None:
    shift = src.SHIFT_VALUE * T["tariff"] / 50.0        # ch 20 value at this tariff
    cases = [
        ("PPA pay-as-produced, S1", dict()),
        ("PPA pay-as-produced, S0", dict(battery=False)),
        ("time-of-day PPA, S1 shifts", dict(extra_revenue=shift)),
        ("merchant S1, 50 u, lent on 80 %", dict(price_scale=50 / 70, sizing_price=0.8 * 50 / 70,
                                                    extra_revenue=src.SHIFT_VALUE)),
    ]
    lines = ["the same plant under four revenue pathways (teaching):",
             "  pathway                        debt k u  gearing %  min DSCR  eq. IRR %"]
    for name, kw in cases:
        r = model.run(**kw)
        lines.append(f"  {name:30s} {r['debt']:8,.0f}  {r['gearing'] * 100:9.1f}  {r['min_dscr']:8.2f}"
                     f"  {r['equity_irr'] * 100:9.2f}")
    lines += ["  under a flat PPA the battery only costs (S0 earns more); a",
              "  time-of-day tariff pays for the shifting of chapter 20 and",
              "  narrows the gap; a merchant sale earns less and the lenders",
              "  lend less on a price they discount - the equity then needs",
              "  a higher price or a hedge to reach its return"]
    emit("e_pathways", lines)


def services() -> None:
    held = 5 * 4 * 365                                    # MW-h a year, REQ-S01
    base = model.run()
    lines = ["a reserve service (REQ-S01) as a SENSITIVITY, not committed revenue:",
             "  price u per MW-h   revenue k u   less lost shifting   equity IRR %"]
    for p in (6.0, 9.0, 12.0):
        rev = held * p / 1000
        net = rev                                         # flat PPA: no shifting lost
        r = model.run(extra_revenue=net)
        lines.append(f"  {p:16.0f}   {rev:11,.1f}   {net:18,.1f}   {r['equity_irr'] * 100:12.2f}")
    lines += [f"  base equity IRR {base['equity_irr'] * 100:.2f} %",
              "  under a flat PPA the reserve displaces no shifting value, so",
              "  the whole fee is new money; under a time-of-day PPA it would",
              "  cost about 58 k u a year of shifting (chapter 20); a service",
              "  enters the lenders' case only with a signed contract,",
              "  qualification passed and penalties priced (U-077)"]
    emit("e_services", lines)


def carbon() -> None:
    e1 = 295.14
    lines = ["carbon credits as a LABELLED SENSITIVITY (scheme, eligibility and",
             "baseline NOT verified; grid factor 0.6 t/MWh is a teaching value):",
             "  price u/t   tonnes a year   revenue k u   equity IRR %"]
    for p in (0.0, 5.0, 15.0):
        rev = e1 * 1000 * 0.6 * p / 1000
        r = model.run(extra_revenue=rev)
        lines.append(f"  {p:9.0f}   {e1 * 1000 * 0.6:13,.0f}   {rev:11,.0f}   {r['equity_irr'] * 100:12.2f}")
    lines += ["  shown to say how much a verified scheme would matter; never",
              "  in the base case, never in the debt sizing, until the",
              "  methodology, eligibility, registration and the buyer of the",
              "  credits are confirmed in writing"]
    emit("e_carbon", lines)


def payment() -> None:
    r = model.run()
    ds = r["ds"][2]
    month = r["revenue"][2] / 12
    lc = 3 * month
    lines = ["payment security against a buyer that pays late (year 3):",
             f"  monthly revenue {month:,.0f} k u; debt service of the year {ds:,.0f}",
             f"  letter of credit for 3 months of revenue: {lc:,.0f} k u,",
             f"  fee 1.5 % a year = {0.015 * lc:,.0f} k u",
             f"  DSRA {r['dsra']:,.0f} k u = {r['dsra'] / ds * 12:.1f} months of service",
             "  months late   unpaid revenue   service due   from LC   from DSRA   short"]
    for m in (2, 4, 6, 9, 12):
        unpaid = m * month
        due = m / 12 * ds
        from_lc = min(due, lc)
        from_dsra = min(r["dsra"], due - from_lc)
        lines.append(f"  {m:11d}   {unpaid:14,.0f}   {due:11,.0f}   {from_lc:7,.0f}   {from_dsra:9,.0f}"
                     f"   {due - from_lc - from_dsra:5,.0f}")
    lines += ["  (the debt service falling due while the buyer does not pay is",
              "  paid first from the LC, then from the DSRA)",
              "  the LC carries a short delay at a small cost, the DSRA a",
              "  longer one; beyond both, the lenders' remedies start: buyer",
              "  credit and payment security are diligence items (section G)"]
    emit("e_payment", lines)


if __name__ == "__main__":
    pathways()
    services()
    carbon()
    payment()
