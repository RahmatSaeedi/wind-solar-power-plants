"""Chapter 21 - numerical answers of the small examples (E..) and of the
end-of-chapter problems (P..), each computed here.

Run from the project root:   python -m companion.ch21.worked
Writes companion/ch21/expected/worked.txt and solutions.txt.
"""
from __future__ import annotations

import numpy as np

from companion.ch21 import model, sources as src
from companion.ch21.common import emit
from plantp import finance as fn


def worked() -> None:
    lines = [f"E01 PV of 110 in one year at 10 %: {fn.pv([110], 0.10):.1f}",
             f"E02 nominal rate for 4 % real and 2.5 % inflation: "
             f"{fn.real_to_nominal_rate(0.04, 0.025) * 100:.2f} %",
             f"E03 IRR of -100, +60, +60: {fn.irr([-100, 60, 60]) * 100:.2f} %",
             f"E04 annuity payment 100 at 10 % over 2 yr: "
             f"{100 * 0.10 / (1 - 1.1 ** -2):.2f}",
             f"E05 sculpted debt for CFADS 22, 22 at DSCR 1.10, 10 %: "
             f"{fn.sculpted_debt([22, 22], 1.10, 0.10)[0]:.2f}",
             f"E06 DSCR of CFADS 13,837 on service 11,514: {13837 / 11514:.3f}",
             f"E07 IDC on 100 spent evenly over 2 yr at 10 %: "
             f"{fn.construction(100, [1, 1], 0.10)[1].sum():.1f}",
             f"E08 tax 25 % on 10, 10, 50 with depreciation 30, 0, 0: "
             f"{[float(x) for x in fn.tax_schedule([10, 10, 50], [30, 0, 0], [0, 0, 0], 0.25)]}",
             f"E09 LCOE capex 100, 10 MWh a year for 2 yr at 0 %: "
             f"{fn.lcoe(100, [0, 0], [10, 10], 0.0):.1f}",
             f"E10 LC fee 1.5 % a year on 5,301: {0.015 * 5301:.0f} k u"]
    emit("worked", lines)


def solutions() -> None:
    out = []
    for i, (r, n) in enumerate([(0.05, 20), (0.075, 25), (0.10, 15)], 1):
        out.append(f"P{i:02d} annuity factor {r * 100:.1f} %, {n} yr: "
                   f"{(1 - (1 + r) ** -n) / r:.3f}")
    for i, (re, inf) in enumerate([(0.05, 0.02), (0.03, 0.04)], 4):
        out.append(f"P{i:02d} nominal from real {re * 100:.0f} % and inflation {inf * 100:.0f} %: "
                   f"{fn.real_to_nominal_rate(re, inf) * 100:.2f} %")
    out.append(f"P06 IRR of -1000, 150 x 10: {fn.irr([-1000] + [150] * 10) * 100:.2f} %")
    out.append(f"P07 NPV of -1000, 150 x 10 at 8 %: {fn.pv([150] * 10, 0.08) - 1000:.1f}")
    i, p, b = fn.annuity_debt(1000, 0.06, 10)
    out.append(f"P08 annuity 1,000 at 6 %, 10 yr: payment {i[0] + p[0]:.1f},"
               f" interest yr 1 {i[0]:.1f}")
    d, *_ = fn.sculpted_debt([150] * 10, 1.25, 0.06)
    out.append(f"P09 sculpted debt CFADS 150 x 10, DSCR 1.25, 6 %: {d:.1f}")
    d2, *_ = fn.sculpted_debt([150] * 10, 1.40, 0.06)
    out.append(f"P10 same at DSCR 1.40: {d2:.1f} ({(d2 / d - 1) * 100:.1f} %)")
    d3, *_ = fn.sculpted_debt([150] * 8, 1.25, 0.06)
    out.append(f"P11 same at 1.25 over 8 yr: {d3:.1f}")
    _, i4, p4, b4 = fn.sculpted_debt([30, 30, 30], 1.25, 0.08)
    out.append(f"P12 LLCR at start, CFADS 30 x 3, DSCR 1.25, 8 %: "
               f"{fn.llcr([30, 30, 30], b4, 0.08, 3)[0]:.3f}")
    out.append(f"P13 tax 25 % on 40, 40 with depreciation 60 then 0: "
               f"{[float(x) for x in fn.tax_schedule([40, 40], [60, 0], [0, 0], 0.25)]}")
    spend, idc = fn.construction(1000, [0.4, 0.6], 0.06 * 0.7)
    out.append(f"P14 IDC on 1,000 phased 40/60, 70 % debt at 6 %: {idc.sum():.1f}")
    out.append(f"P15 WC 45 days of 20,453 less 30 days of 4,270: "
               f"{(20453 * 45 - 4270 * 30) / 365:,.0f} k u")
    out.append(f"P16 DSRA 6 months of 11,514: {11514 / 2:,.0f} k u")
    out.append(f"P17 delay LD 0.05 %/day on 132,982 for 30 days: {0.0005 * 132982 * 30:,.0f}")
    out.append(f"P18 availability LD cap 20 % of 2,300 = 460 k u at 70 u: "
               f"{460 / 70:.2f} GWh")
    out.append(f"P19 carbon 177,084 t at 5 u/t: {177084 * 5 / 1000:,.0f} k u (sensitivity)")
    out.append(f"P20 REQ-S01 at 9 u per MW-h: {7300 * 9 / 1000:.1f} k u (sensitivity)")
    out.append(f"P21 merchant 50 u vs PPA 70 u: revenue ratio {50 / 70:.3f}")
    out.append(f"P22 FX -10 % on 70 % of 156,450: capex +{156450 * 0.7 * 0.1 / 0.9:,.0f}")
    out.append(f"P23 real flows 10,000 x 20 at 5 %: {fn.pv([10000] * 20, 0.05):,.0f}")
    out.append(f"P24 break-even tariff at DSCR 1.00: 0.859 x 70 = {0.859 * 70:.1f} u/MWh")
    out.append(f"P25 energy for DSCR 1.00: 0.859 x 295.14 = {0.859 * 295.14:.0f} GWh")
    out.append(f"P26 multiple IRR: -100, 230, -132 -> 10 % and 20 %;"
               f" check NPV at 10 %: {abs(-100 + 230 / 1.1 - 132 / 1.21):.4f}")
    out.append(f"P27 LCOE by hand: (156,450 x 0.0710 + 4,270) / 288.854 = "
               f"{(156450 * 0.0710 + 4270) / 288.854:.1f} u/MWh")
    out.append(f"P28 simple payback 156,450 / (20,453 - 4,270): "
               f"{156450 / (295.14 * 0.99 * 70 - 4270):.1f} yr")
    out.append(f"P29 cost of a month of delay: 1,704 + 605 + 178 = {1704 + 605 + 178:,} k u")
    out.append(f"P30 wrap premium 6 % vs expected multi 5.1 %: {0.06 - 0.051:.3f} of price")
    out.append(f"P31 real tariff yr 10, index 3 %, inflation 5 %: "
               f"{70 * (1.03 / 1.05) ** 9:.1f} u/MWh")
    out.append(f"P32 WACC at 50 % gearing (10 %, 6 %, tax 25 %): "
               f"{(0.5 * 0.10 + 0.5 * 0.06 * 0.75) * 100:.2f} %")
    out.append(f"P33 sinking fund 4,522 over 8 yr at 3 %: "
               f"{4522 * 0.03 / (1.03 ** 8 - 1):,.0f} k u a year")
    out.append(f"P34 shared and yearly 3.6 % each -> one-year spread "
               f"{np.sqrt(2) * 3.6:.1f} %")
    out.append(f"P35 option: PV value 4,808 vs PV cost 8,890 -> worth "
               f"{max(0, 4808 - 8890)} at any probability")
    out.append(f"P36 insurance: premium 1.3 x expected insured loss 554 = {1.3 * 554:,.0f} k u")
    from math import erfc, sqrt
    out.append(f"P37 P(pay) true 3 %, tolerance 1 %, u 2 %: "
               f"{0.5 * erfc((1.0 - 3.0) / (2.0 * sqrt(2))):.2f}")
    out.append(f"P38 self-consumption 30 GWh at +12 u: {30 * 12:,} k u a year")
    out.append(f"P39 swap cost 0.2 % on 121,025 in year 1: {0.002 * 121025:,.0f} k u")
    out.append(f"P40 refinancing release: 132,813 - 112,078 - 1 % = "
               f"{132813 - 112078 - 1328:,.0f} k u")
    out.append(f"P41 delay LD cap in months: 13,298 / 1,995 = {13298 / 1995:.1f}")
    out.append(f"P42 termination yr 5: 101,243 + 0.5 x 49,163 x 0.84 = "
               f"{101243 + 0.5 * 49163 * 0.84:,.0f} k u")
    out.append(f"P43 WC 60 days of 20,453 less 30 of 4,270: "
               f"{(20453 * 60 - 4270 * 30) / 365:,.0f} k u")
    out.append(f"P44 equity-first IDC: 0.06 x (6,708 + 13,417 + 46,935) = "
               f"{0.06 * (6708 + 13417 + 46935):,.0f} k u")
    out.append(f"P45 overrun 10 % of 149,000: 7,450 + 4,916 + left "
               f"{14900 - 7450 - 4916:,} k u")
    out.append(f"P46 stacking: 469 + 29 x 1.332 = {469 + 29 * 389 / 292:.0f} k u")
    out.append(f"P47 spare: expected loss 0.02 x 292.2 GWh x 6 % x 0.5 yr x 70 = "
               f"{0.02 * 292.2 * 0.06 * 0.5 * 70:.1f} k u")
    out.append(f"P48 half-plant outage 6 months: 292.2 x 6 % x 0.5 x 70 = "
               f"{292.2 * 0.06 * 0.5 * 70:.0f} k u")
    out.append(f"P49 discount factor yr 19 at 7.5 %: {1.075 ** -19:.3f}")
    out.append(f"P50 PV of 1,000 a year for 15 yr at 6 %: "
               f"{fn.pv([1000] * 15, 0.06):,.0f}")
    emit("solutions", out)


if __name__ == "__main__":
    worked()
    solutions()
