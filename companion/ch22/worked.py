"""Chapter 22 - numerical answers of the small examples (E..) and of the
end-of-chapter problems (P..), each computed here.

Run from the project root:   python -m companion.ch22.worked
Writes companion/ch22/expected/worked.txt and solutions.txt.
"""
from __future__ import annotations

import numpy as np

from companion.ch22.common import emit
from companion.ch22.examples_h import rollback
from plantp import appraisal as ap


def worked() -> None:
    lines = [f"E01 normalise 330, 295, 262 (higher better): "
             f"{np.round(ap.normalise([330, 295.14, 262]), 2).tolist()}",
             f"E02 weighted [1, 0.5] with weights 0.6, 0.4: {float(ap.weighted([[1, 0.5]], [0.6, 0.4])[0]):.2f}",
             f"E03 quality 0.4 on score 1.0: {float(ap.quality_adjusted(1.0, 0.4)):.2f}",
             f"E04 expected cost of (0.15, 8000) and (0.4, 2500): "
             f"{ap.risk_cost([(0.15, 8000), (0.4, 2500)]):,.0f}",
             f"E05 range of 156,450 at -20 % / +30 %: "
             f"{ap.estimate_range(156450, -0.2, 0.3)[0]:,.0f} to {ap.estimate_range(156450, -0.2, 0.3)[1]:,.0f}",
             f"E06 value of a 120 survey, p stop 0.5, saving 1,500: {0.5 * 1500 - 120:,.0f}"]
    emit("worked", lines)


def solutions() -> None:
    out = []
    out.append(f"P01 normalise costs 181, 156.45, 146.5 (lower better): "
               f"{np.round(ap.normalise([181, 156.45, 146.5], False), 2).tolist()}")
    s = np.array([[1.0, 0.0], [0.5, 0.8], [0.0, 1.0]])
    for i, w in enumerate(([0.5, 0.5], [0.7, 0.3], [0.3, 0.7]), 2):
        out.append(f"P{i:02d} weights {w}: totals {np.round(ap.weighted(s, w), 2).tolist()}")
    out.append(f"P05 dominated in [[1,1],[0.5,1],[0.6,0.4]]: {ap.dominated([[1, 1], [0.5, 1], [0.6, 0.4]])}")
    tasks = {"a": (5, []), "b": (3, []), "c": (4, ["a"]), "d": (6, ["b"]), "e": (2, ["c", "d"])}
    tot, crit, slack = ap.critical_path(tasks)
    out.append(f"P06 CPM: total {tot:.0f}, critical {crit}, slack a {slack['a']:.0f}")
    out.append(f"P07 risk register (0.2, 3000), (0.3, 4500): {ap.risk_cost([(0.2, 3000), (0.3, 4500)]):,.0f}")
    out.append(f"P08 survey 200, p 0.3, saving 2,000: value {0.3 * 2000 - 200:,.0f}")
    out.append(f"P09 quality 0.7 on 0.0 and 1.0: {float(ap.quality_adjusted(0.0, 0.7)):.2f},"
               f" {float(ap.quality_adjusted(1.0, 0.7)):.2f}")
    out.append(f"P10 development 6,500 as share of 156,450: {6500 / 156450 * 100:.1f} %")
    out.append(f"P11 restoration 38 x 60 + 6 x 400 + 900 x 1.2: {38 * 60 + 6 * 400 + 900 * 1.2:,.0f} k u")
    out.append(f"P12 energy loss of P-Central vs P-North: {(1 - 295.14 / 330) * 100:.1f} %")
    out.append(f"P13 P90 with u 9 %: {1 - 1.282 * 0.09:.3f}; with 5.1 %: {1 - 1.282 * 0.051:.3f}")
    out.append(f"P14 cost incl. grid P-North: {156000 + 25000:,} k u ({181000 / 156450 - 1:.1%} above P-Central)")
    out.append(f"P15 later COD of P-North vs P-Central: {(54 - 32) / 12:.2f} years")
    out.append(f"P16 mean of triangular (6, 9, 16): {(6 + 9 + 16) / 3:.2f} months;"
               f" PERT {(6 + 4 * 9 + 16) / 6:.2f}")
    out.append(f"P17 rollback [(2200, 0.75), (2500, 0.8)] to 7,740: "
               f"{rollback([(2200, 0.75), (2500, 0.8)], 7740):,.0f}")
    out.append(f"P18 same with value 5,000: {rollback([(2200, 0.75), (2500, 0.8)], 5000):,.0f}")
    out.append(f"P19 influx 270 outsiders, 2,000 people: {270 / 2000 * 100:.1f} %")
    out.append(f"P20 route 15 km OHL at 180 + 1 crossing at 60: {15 * 180 + 60:,.0f} k u")
    out.append(f"P21 NPV 5,000 discounted 24 months at 7.5 %: {5000 / 1.075 ** 2:,.0f}")
    out.append(f"P22 margin 0.19 over weight 0.25: fall needed {0.19 / 0.25:.2f}")
    out.append(f"P23 reservation 10 % of 4,000 + 52,000 + 2,500: {0.1 * 58500:,.0f} k u")
    out.append(f"P24 index 30 turbines x 0.07 + 0.6: {30 * 0.07 + 0.6:.1f} per year")
    out.append(f"P25 energy equivalent of 10,000 k u at 1.4 GWh per 1,000: {10 * 1.376:.1f} GWh")
    out.append(f"P26 contingency P80 158,443 over base 149,000: {(158443 / 149000 - 1) * 100:.1f} %")
    out.append(f"P27 P(all three gates) 0.8 x 0.7 x 0.75: {0.8 * 0.7 * 0.75:.2f}")
    out.append(f"P28 window days for 20 turbines at 3 each, 25 a month: {20 * 3 / 25:.1f} months")
    out.append(f"P29 partner share 49 % of 4,700 spend: {0.49 * 4700:,.0f} k u")
    out.append(f"P30 worker-months 450 peak x 18 months x 0.56: {450 * 18 * 0.56:,.0f}")
    emit("solutions", out)


if __name__ == "__main__":
    worked()
    solutions()
