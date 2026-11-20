"""Chapter 16 - small worked calculations quoted in the text (E01 ...) and
numerical answers to the end-of-chapter problems (P01 ...).

Run from the project root:   python -m companion.ch16.worked
Writes companion/ch16/expected/worked.txt and solutions.txt.
"""
from __future__ import annotations

import math

from companion.ch16.common import emit
from plantp import yieldrisk as yr

E: list[str] = []
P: list[str] = []


def e(i, t):
    E.append(f"{i}: {t}")


def p(i, t):
    P.append(f"{i}: {t}")


def worked() -> None:
    e("E01", f"z for P90, P95, P99: {yr.z_exceed(0.9):.4f}, {yr.z_exceed(0.95):.4f},"
             f" {yr.z_exceed(0.99):.4f}")
    e("E02", f"P90 of 300 GWh at 5 %: {yr.p_value(300, 0.05):.2f} GWh")
    e("E03", f"independent 3 % and 4 %: {yr.combine([3, 4]):.1f} %; fully correlated 7 %")
    e("E04", f"r 0.5: sqrt(9 + 16 + 2 x 0.5 x 12) = {yr.combine([3, 4], [[1, .5], [.5, 1]]):.2f} %")
    e("E05", f"speed 2.6 % x sensitivity 1.82 = {2.6 * 1.82:.2f} % of energy")
    e("E06", f"long-term 3 %, year-to-year 4 %: one year {yr.n_year(.03, .04, 1) * 100:.1f} %,"
             f" ten years {yr.n_year(.03, .04, 10) * 100:.2f} %")
    e("E07", f"shares of 3 and 4: {yr.shares([3, 4])[0]:.2f} and {yr.shares([3, 4])[1]:.2f}")
    e("E08", f"MC noise of a P90 with 10,000 draws, sigma 15 GWh: about"
             f" {1.71 * 15 / math.sqrt(10000):.2f} GWh")
    e("E09", f"annuity factor 6 %, 15 years: {yr.annuity(0.06, 15):.4f}")
    e("E10", f"CFADS 9,796 k u at ratio 1.20: debt {9796 / 1.2 * yr.annuity(0.06, 15):,.0f} k u")
    e("E11", f"lognormal P90 at 10 %: {yr.p_value_lognormal(100, 0.10):.2f} against normal"
             f" {yr.p_value(100, 0.10):.2f}")
    e("E12", f"uniform half-width for sigma 5 %: {5 * math.sqrt(3):.2f} %")
    emit("worked", E)


def solutions() -> None:
    p("P01", f"P90 of 200 GWh at 6 %: {yr.p_value(200, 0.06):.2f} GWh")
    p("P02", f"P99 of 200 GWh at 6 %: {yr.p_value(200, 0.06, 0.99):.2f} GWh")
    p("P03", f"P75 of 200 GWh at 6 %: {yr.p_value(200, 0.06, 0.75):.2f} GWh")
    p("P04", f"RSS of 2, 3 and 6 %: {yr.combine([2, 3, 6]):.1f} %")
    p("P05", f"sum of 2, 3 and 6 % fully correlated: {2 + 3 + 6} %")
    p("P06", f"r 0.3 for 5 and 5 %: {yr.combine([5, 5], [[1, .3], [.3, 1]]):.2f} %")
    p("P07", f"r -0.3 for 5 and 5 %: {yr.combine([5, 5], [[1, -.3], [-.3, 1]]):.2f} %")
    p("P08", f"speed 3 % x 1.82: {3 * 1.82:.2f} % of energy")
    p("P09", f"n-year, long-term 4 %, year 5 %, 4 years: {100 * yr.n_year(.04, .05, 4):.2f} %")
    p("P10", f"the same for 25 years: {100 * yr.n_year(.04, .05, 25):.2f} %")
    p("P11", f"shares of 1, 2 and 2: {', '.join(f'{x:.2f}' for x in yr.shares([1, 2, 2]))}")
    p("P12", f"P90 wind 175 and PV 102 summed: {175 + 102} GWh (not the hybrid P90)")
    p("P13", f"annuity 8 %, 12 years: {yr.annuity(0.08, 12):.4f}")
    p("P14", f"debt for 8,000 k u at 1.25, 6 %, 15 y: {8000 / 1.25 * yr.annuity(0.06, 15):,.0f} k u")
    p("P15", f"CFADS of 280 GWh at 50 u/MWh less 4,000 k u: {280 * 50 - 4000:,.0f} k u")
    p("P16", "below the P90 twice or more in 10 years:"
             f" {1 - 0.9 ** 10 - 10 * 0.1 * 0.9 ** 9:.3f}")
    p("P17", f"probability of at least one year below the P90 in 15: {1 - 0.9 ** 15:.3f}")
    p("P18", f"MC noise, sigma 15, 1,000 draws: about {1.71 * 15 / math.sqrt(1000):.2f} GWh")
    p("P19", f"draws for 0.1 GWh: about {(1.71 * 15 / 0.1) ** 2:,.0f}")
    p("P20", f"uniform sigma for half-width 2 %: {2 / math.sqrt(3):.2f} %")
    p("P21", f"triangular sigma for half-width 3 %: {3 / math.sqrt(6):.2f} %")
    p("P22", f"P90 / P50 at 5.1 %: {1 - 1.2816 * 0.051:.4f}")
    p("P23", f"wind 2.26 % and 3.44 %: {yr.combine([2.26, 3.44]):.2f} %")
    p("P24", f"debt per GWh of P90 at 50 u/MWh, ratio 1.20: {50 / 1.2 * yr.annuity(0.06, 15):.0f} k u")
    p("P25", f"expected shortfall cost 0.71 GWh x 100 u/MWh: {0.71 * 100:.0f} k u a year")
    from companion.ch16.examples_f import u_mcp
    p("P26", f"MCP, 12 months at r 0.80: {100 * u_mcp(12, 0.80):.2f} %; 24 months at r 0.90:"
             f" {100 * u_mcp(24, 0.90):.2f} %")
    p("P27", f"trend -0.05 %/yr over 17.5 years: speed {-0.05 * 17.5:.2f} %, energy"
             f" {-0.05 * 17.5 * 1.82:.2f} %")
    p("P28", f"degradation rate sd 0.2 %/yr, year 20: {0.002 * 20 * 108.36 / 0.995:.2f} GWh")
    p("P29", f"no major failure among 12 turbines at 4 %: {0.96 ** 12:.3f}")
    p("P30", f"long-term part after 3 years: {(1 / 11.76 ** 2 + 3 / 9.31 ** 2) ** -0.5:.2f} GWh")
    p("P31", f"W1 P99 one year: 333.5 - 2.3263 x 35.8 = {333.5 - 2.3263 * 35.8:.1f} GWh")
    p("P32", f"debt W1 with a ridge mast over W2b: {93418 / 79287:.3f}")
    p("P33", f"major-failure downtime: {12 * 0.04 * 60:.1f} turbine-days ="
             f" {100 * 12 * 0.04 * 60 / (12 * 365):.2f} % of time")
    p("P34", f"P90 one year with sigma 12 GWh and P50 295: {295 - 1.2816 * 12:.1f} GWh")
    p("P35", f"debt per GWh of P90 at ratio 1.25: {50 / 1.25 * yr.annuity(0.06, 15):.0f} k u")
    d = 10.817                                       # GWh discharged, ch 15 n_shifting
    loss = d * (1 / 0.86 - 1)
    s_loss = d * 0.02 / 0.86 ** 2
    p("P36", f"S1 round-trip loss {loss:.2f} GWh; efficiency 86 +/- 2 %: sigma"
             f" {s_loss:.2f} GWh")
    p("P37", f"S1 value 375 k u, spread +/- 20 %: +/- {0.2 * 375:.0f} k u"
             f" ({0.2 * 375 / 14417 * 100:.2f} % of 14,417 k u)")
    emit("solutions", P)


if __name__ == "__main__":
    worked()
    solutions()
