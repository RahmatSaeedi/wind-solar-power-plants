"""Chapter 39 - small worked examples (E-lines) and the numerical answers
of the exercises (P-lines), each computed here.

Run from the project root:   python -m companion.ch39.worked
Writes companion/ch39/expected/worked.txt and solutions.txt.
"""
from __future__ import annotations

from companion.ch39.common import emit
from plantp import procure as pr
from plantp import transformer as tr


def worked() -> None:
    lines = [f"E01 compliance, 16 of 18 comply: {16 / 18 * 100:.0f} %",
             f"E02 evaluated price 1,000 + 20 + 300 + 4 x 10 + 1,000 x 0.5 x 0.1:"
             f" {pr.evaluated_price(1000, 20, 300, 4, 10, 0.5, 0.1):,.0f} k u",
             f"E03 delay damages, 30 weeks at 0.5 %, cap 10 %, price 1,000:"
             f" {pr.ld_amount(30, 0.005, 1000, 0.10)[0]:.0f} k u",
             f"E04 equal share of 98 % for 4 parts: "
             f"{pr.allocate_availability(0.98, 4) * 100:.2f} %",
             f"E05 annuity factor, 7.5 %, 25 years: {pr.annuity(0.075, 25):.2f}",
             f"E06 audit score 4, 2 with weights 1, 1: "
             f"{pr.audit_score({'a': 4, 'b': 2}, {'a': 1, 'b': 1}, {})[0]:.1f}"]
    emit("worked", lines)


def solutions() -> None:
    a, b = tr.ab_factors(70, 25, 0.075, 0.20)
    out = [f"P01 A factor at 70 u/MWh, 25 y, 7.5 %: {a:.2f} k u/kW",
           f"P02 B factor with loss load factor 0.20: {b:.2f} k u/kW",
           f"P03 losses of one U-B unit (5.2, 52 kW): {tr.loss_cost(5.2, 52, a, b):.1f} k u",
           f"P04 ten U-C units (4.5, 45 kW): {10 * tr.loss_cost(4.5, 45, a, b):.0f} k u",
           f"P05 U-B late 4 weeks at 0.5 % of 1,010: {4 * 0.005 * 1010:.1f} k u",
           f"P06 currency allowance, U-C 90 % foreign at 8 %: {1080 * 0.9 * 0.08:.1f} k u",
           f"P07 evaluated price of U-A: {1160 + 6 + 840.7 + 0 + 1160 * 0.7 * 0.08:,.0f} k u",
           f"P08 margin U-C over U-A: {2093 - 2072} k u",
           f"P09 delay damages, 20 weeks, cap 10 % of 1,160: "
           f"{pr.ld_amount(20, 0.005, 1160, 0.10)[0]:.0f} k u",
           f"P10 PV energy a week at 70 u/MWh: {107_426 * 70 / 52 / 1000:.0f} k u",
           f"P11 chain on time, 0.99 x 0.95 x 0.97 x 0.96 x 0.98: "
           f"{0.99 * 0.95 * 0.97 * 0.96 * 0.98 * 100:.0f} %",
           f"P12 equal share of 97 % over 4 parts: "
           f"{pr.allocate_availability(0.97, 4) * 100:.2f} %",
           f"P13 inverter availability, MTBF 2,000 h, 24 + 8 h: "
           f"{2000 / 2032 * 100:.2f} %",
           f"P14 same with 72 + 24 h: {2000 / 2096 * 100:.2f} %",
           f"P15 U-B data schedule, 8 of 14: {8 / 14 * 100:.0f} %",
           f"P16 U-A audit, weighted: "
           f"{(4*2 + 4*3 + 4*3 + 3*2 + 3*2 + 4*2 + 4*2 + 4*1) / 17:.2f}",
           f"P17 interfaces among 5 packages: {5 * 4 // 2}",
           f"P18 expected repairs a year, 10 units at 1 %: {10 * 0.01:.1f}",
           f"P19 U-B compliance, 14 of 18: {14 / 18 * 100:.0f} %",
           f"P20 labour risk score 2 + 2 + 2 + 1: {2 + 2 + 2 + 1} (high at 5 or more)"]
    emit("solutions", out)


if __name__ == "__main__":
    worked()
    solutions()
