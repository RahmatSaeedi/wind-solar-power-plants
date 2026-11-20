"""Chapter 21, section C - contracts and risk allocation as numbers: what
a month of delay costs the owner against delay liquidated damages, a
performance shortfall against performance damages, one EPC wrap
against several contracts with interface risk, an extended warranty
against the expected repairs, and the risk-allocation matrix.

Commercial concepts only - not legal advice; every rate, cap and
probability is a teaching value (A-308).

Run from the project root:   python -m companion.ch21.examples_c
Writes companion/ch21/expected/c_*.txt.
"""
from __future__ import annotations

from companion.ch21 import model, sources as src
from companion.ch21.common import emit
from plantp import finance as fn

T = src.TERMS


def delay() -> None:
    r = model.run()
    month_rev = r["revenue"][0] / 12
    month_opex_fixed = sum(src.OPEX.values()) * 0.5 / 12
    month_int = r["debt"] * T["rate"] / 12
    cost = month_rev - 0 + month_int + month_opex_fixed
    epc = src.capex_total() * 0.85                    # EPC price share (teaching)
    ld_rate = 0.0005 * epc * 30                       # 0.05 % a day
    cap = 0.10 * epc
    lines = ["one month of delay to the commercial operation date:",
             f"  revenue lost                      {month_rev:8,.0f} k u",
             f"  interest on the drawn debt        {month_int:8,.0f}",
             f"  fixed costs that continue (half)  {month_opex_fixed:8,.0f}",
             f"  cost to the owner                 {cost:8,.0f} k u a month",
             f"  delay LD at 0.05 % a day of the EPC price: {ld_rate:,.0f} k u a month,",
             f"  capped at 10 % = {cap:,.0f} k u (about {cap / ld_rate:.0f} months)",
             f"  the LD covers {ld_rate / cost * 100:.0f} % of the owner's monthly loss; LD rates",
             "  are set near the real loss so the contractor carries the",
             "  delay it causes; beyond the cap the owner carries it -",
             "  lenders want LDs to cover at least the interest and fixed",
             "  costs of the delay period (teaching, A-308)"]
    emit("c_delay", lines)


def performance() -> None:
    lines = ["a 2 % shortfall of the wind farm's power curve (teaching):",
             "  lost energy a year GWh, value over 25 years (NPV 7.5 %)"]
    lost = 0.02 * 191.87                               # farm P50, chapter 13
    val = fn.pv(lost * T["tariff"] * fn.index(T["tariff_index"], 20), T["wacc"])
    ld = 0.02 * 78_000 * 1.0                           # 1 % of price per 1 % shortfall
    lines += [f"  lost {lost:.2f} GWh a year, worth {val:,.0f} k u over the PPA",
              f"  performance LD at 1 % of the turbine price per 1 % shortfall: {ld:,.0f} k u",
              f"  the LD pays {ld / val * 100:.0f} % of the loss; it is a remedy for a",
              "  measured shortfall in a defined test (power-curve test,",
              "  chapter 11), capped, and usually the owner's only remedy;",
              "  so the test method and the measurement uncertainty are",
              "  worth as much as the LD rate"]
    emit("c_performance", lines)


def wrap() -> None:
    """EPC wrap with a 6 % premium against a multi-contract route with a
    30 % chance of an interface failure costing 12 % (teaching)."""
    cost = src.capex_total() * 0.85
    lines = ["one EPC wrap or several contracts (expected cost, k u):",
             f"  EPC wrap: price {cost:,.0f} + premium 6 % = {cost * 1.06:,.0f}",
             f"  multi-contract: {cost:,.0f} + interface team 1.5 %",
             f"    + 30 % chance x 12 % = {cost * (1 + 0.015 + 0.3 * 0.12):,.0f}",
             f"  expected saving of the multi-contract route "
             f"{cost * 1.06 - cost * (1 + 0.015 + 0.3 * 0.12):,.0f} k u",
             f"  but its bad case (interface failure) costs "
             f"{cost * (1 + 0.015 + 0.12):,.0f}: {cost * (0.015 + 0.12 - 0.06):,.0f} more",
             "  than the wrap; lenders often prefer the wrap because it puts",
             "  the interface risk with one party that can carry it"]
    emit("c_wrap", lines)


def warranty() -> None:
    """Extend the inverter warranty from 5 to 10 years for 8 % of the
    inverter price, against an expected 3 % of units failing a year at
    35 % of the unit price each (teaching)."""
    inv = 50 * 60.0 + 4 * 5.5 * 60.0                  # PV + battery inverters, k u
    price = 0.08 * inv
    exp = sum(0.03 * 0.35 * inv / (1 + T["wacc"]) ** y for y in range(6, 11))
    lines = ["extended inverter warranty, years 6-10 (teaching):",
             f"  inverter fleet price {inv:,.0f} k u; extension price {price:,.0f}",
             f"  expected repair cost years 6-10, PV at 7.5 %: {exp:,.0f}",
             "  the extension costs more than the expected repairs: it buys",
             "  certainty, not value - worth it if the owner cannot carry a",
             "  bad year, or if lenders require it; read what it excludes"]
    emit("c_warranty", lines)


# [start: matrix]
RISKS = [  # (risk, owner of the risk, how it is passed on or kept)
    ("resource below P50", "owner/equity", "P90 debt sizing, DSRA"),
    ("construction delay", "EPC contractor", "delay LDs up to the cap"),
    ("cost overrun", "EPC (fixed price)", "contingency, standby equity"),
    ("equipment performance", "OEM", "performance LDs, tests"),
    ("availability", "O&M contractor", "availability LDs, capped"),
    ("curtailment by grid", "offtaker or owner", "deemed energy clause"),
    ("buyer does not pay", "owner/lenders", "payment security, DSRA"),
    ("change in law", "offtaker (if agreed)", "change-in-law clause"),
    ("force majeure", "shared", "insurance, relief periods"),
    ("interest rate", "owner", "rate hedge"),
    ("currency", "owner", "hedge, indexed tariff"),
    ("battery degradation", "OEM to warranty limit", "warranty, augmentation"),
]
# [end: matrix]


def matrix() -> None:
    lines = ["risk allocation matrix of Plant P (teaching; commercial, not legal):",
             "  risk                     carried by             instrument"]
    for r, who, how in RISKS:
        lines.append(f"  {r:24s} {who:22s} {how}")
    lines += ["  a risk belongs with the party that can best control it or",
              "  carry it; what is not passed on stays with the owner and,",
              "  through the cover ratios, with the lenders"]
    emit("c_matrix", lines)


if __name__ == "__main__":
    delay()
    performance()
    wrap()
    warranty()
    matrix()
