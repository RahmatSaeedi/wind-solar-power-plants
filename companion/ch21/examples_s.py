"""Chapter 21, final lessons: the battery as its own profit centre, two
term sheets compared, a tax holiday shown only as a labelled
sensitivity, an EPC price-adjustment formula between bid and order,
and a new grid charge on generators under the change-in-law clause.

Run from the project root:   python -m companion.ch21.examples_s
Writes companion/ch21/expected/s_*.txt.
Teaching values A-304 to A-310; no incentive or law is assumed to exist.
"""
from __future__ import annotations

import numpy as np

from companion.ch21 import model, sources as src
from companion.ch21.common import emit
from plantp import finance as fn

T = src.TERMS


def battery_pnl() -> None:
    cap = src.capex_total() - src.capex_total(False)
    infl = fn.index(T["inflation"], 25)
    shift = src.SHIFT_VALUE * 70 / 50 * infl
    service = 7_300 * 9.0 / 1000 * infl
    recapture = 0.0                                   # inside shifting (ch 20)
    om = 160.0 * infl
    aug = np.zeros(25)
    aug[7] = aug[12] = 600.0 * infl[7]
    losses = 1_760 * 70 / 1000 * fn.index(0.02, 25)  # energy lost in the battery
    cf = shift + service - om - aug - losses
    npv = fn.pv(cf, T["wacc"]) - cap
    lines = ["the battery as its own profit centre (k u, PV at 7.5 %):",
             f"  capital {cap:,.0f}",
             f"  shifting under a time-of-day PPA      PV {fn.pv(shift, T['wacc']):9,.0f}",
             f"  reserve service at 9 u (sensitivity)  PV {fn.pv(service, T['wacc']):9,.0f}",
             f"  battery O&M                           PV {-fn.pv(om, T['wacc']):9,.0f}",
             f"  augmentation years 8 and 13           PV {-fn.pv(aug, T['wacc']):9,.0f}",
             f"  energy lost in round trips            PV {-fn.pv(losses, T['wacc']):9,.0f}",
             f"  NPV of the battery {npv:,.0f}",
             "  the battery repays about two fifths of its capital from these",
             "  streams: it needs a price spread, a service or a requirement",
             "  worth the rest - the same verdict as the option lesson"]
    emit("s_battery", lines)


def term_sheets() -> None:
    offers = {"A: 6.0 %, 15 yr, DSCR 1.20, fee 1.5 %": dict(rate=0.06, tenor=15, dscr=1.20, fee=0.015),
              "B: 6.5 %, 18 yr, DSCR 1.25, fee 2.0 %": dict(rate=0.065, tenor=18, dscr=1.25, fee=0.02)}
    lines = ["two term sheets for the same plant (sculpted on P90 1-yr):",
             "  offer                                   debt k u   equity IRR %   min DSCR"]
    keep = dict(T)
    for name, o in offers.items():
        T.update(rate=o["rate"], tenor=o["tenor"], dscr_p90=o["dscr"], fee=o["fee"])
        r = model.run(rate=o["rate"])
        lines.append(f"  {name:38s} {r['debt']:9,.0f}   {r['equity_irr'] * 100:12.2f}   {r['min_dscr']:8.2f}")
        T.update(keep)
    lines += ["  the dearer offer with the longer tenor lends more (up to the",
              "  75 % gearing cap) and pays the owners better despite its",
              "  rate and fee: compare offers in the model, never by their",
              "  headline rate"]
    emit("s_terms", lines)


def tax_holiday() -> None:
    base = model.run()
    lines = ["a five-year tax holiday as a LABELLED SENSITIVITY (no scheme",
             "is assumed to exist in any country; U-083):"]
    saved = base["tax"][:5].sum()
    eq = base["eq_cash"].copy()
    eq[2:7] += base["tax"][:5]
    lines += [f"  tax of years 1-5 in the base case {saved:,.0f} k u",
              f"  equity IRR {base['equity_irr'] * 100:.2f} % -> {fn.irr(eq) * 100:.2f} % if the holiday applied",
              "  small here because early taxes are small (depreciation and",
              "  interest shield them); never in the base case or the debt",
              "  sizing until the law, eligibility and approval are in hand"]
    emit("s_tax", lines)


def price_adjustment() -> None:
    """EPC price = base x (0.55 + 0.20 steel index + 0.25 FX index)
    between bid and order (teaching formula)."""
    base = src.capex_total() * 0.85
    lines = ["EPC price adjustment between bid and order:",
             "  price = base x (0.55 + 0.20 x steel + 0.25 x currency)",
             "  steel   currency   price k u   change %"]
    for st, fx in ((1.0, 1.0), (1.15, 1.0), (1.0, 1.10), (1.15, 1.10)):
        pr = base * (0.55 + 0.20 * st + 0.25 * fx)
        lines.append(f"  {st:5.2f}   {fx:8.2f}   {pr:9,.0f}   {(pr / base - 1) * 100:8.1f}")
    lines += ["  an adjustment formula shares index risk until the price is",
              "  fixed; its weights should match the contractor's real cost",
              "  mix, and it should end at a fixed date (financial close)"]
    emit("s_adjust", lines)


def grid_charge() -> None:
    base = model.run()
    lines = ["a new grid charge on generators (change in law), u per MWh:",
             "  charge   PPA passes it on   min DSCR   equity IRR %"]
    for c in (0.0, 2.0, 5.0):
        for passed in (False, True):
            if c == 0 and passed:
                continue
            cost = 0.0 if passed else c * 295.14 * 0.99
            r = model.run(debt=base["debt"], extra_revenue=-cost)
            lines.append(f"  {c:6.0f}   {'yes' if passed else 'no':>16s}   {r['min_dscr']:8.2f}"
                         f"   {r['equity_irr'] * 100:12.2f}")
    lines += ["  a change-in-law clause decides who carries a new charge; a",
              "  5 u charge the owner keeps costs over 2 points of return"]
    emit("s_charge", lines)


if __name__ == "__main__":
    battery_pnl()
    term_sheets()
    tax_holiday()
    price_adjustment()
    grid_charge()
