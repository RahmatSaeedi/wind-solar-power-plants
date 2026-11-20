"""Chapter 37 - three integrated Plant P examples: two results by hand,
the monitoring package in numbers, and the basis D-041.

Run from the project root:   python -m companion.ch37.integrated
Writes companion/ch37/expected/int_*.txt.
"""
from __future__ import annotations

from companion.ch37.common import emit
from plantp import performance as pf


def by_hand() -> None:
    pr = (10_039 / 60.06) / 206.2
    lines = ["two monitoring results checked by hand",
             f"  April PR: (10,039 MWh / 60.06 MWp) / 206.2 kWh/m2 = {pr:.3f};"
             f" code {pf.performance_ratio(10_039_000, 60_060, 206.2):.3f}",
             f"  fan MTBF: (38,600 h of the 4 failed + 8 x 17,520 h) / 4 = "
             f"{pf.mtbf_censored([3200, 7900, 12400, 15100], [17520] * 8):,.0f} h",
             "  a hand check of PR catches the commonest slip: MWh against",
             "  kWh/kWp, a factor of a thousand in one place only"]
    emit("int_hand", lines)


def package() -> None:
    lines = ["the monitoring package of Plant P in numbers (synthetic year)",
             "  plant energy at MV 300,212 MWh, 99.57 % of model 15.1",
             "  four problems found: April soiling (314 MWh), June outage",
             "    (339 MWh), August curtailment (163 MWh), October sensor",
             "  PR 0.832 on the reference sensor; corrected to 25 C the",
             "    months agree within 0.02 except April and June",
             "  fleet availability 98.41 % true; 98.36 % raw and 98.48 %",
             "    cleaned from a log with planted defects",
             "  day-ahead forecast skill 0.42 on held-out data; a drift",
             "    found 8 days after a plant change",
             "  service step passes its placeholder specification"]
    emit("int_package", lines)


def basis() -> None:
    lines = ["D-041 performance monitoring basis of Plant P (teaching)",
             "  1 indicators: PR on a reference sensor and at 25 C, specific",
             "    yield, time- and production-based availability with the",
             "    contract's exclusions, curtailment kept apart",
             "  2 baseline: model 15.1 hourly; daily residual with a CUSUM;",
             "    thresholds set from the cost of a miss and of a visit",
             "  3 data: validation before any indicator; flagged hours",
             "    marked, not deleted; completeness reported",
             "  4 events: one taxonomy, written entry/exit and priority",
             "    rules, planned overruns counted as forced",
             "  5 reliability: coded hierarchy, exposure-based rates with",
             "    intervals, censored estimates, Weibull for wear-out,",
             "    growth slope for the young fleet",
             "  6 forecasts: scored by horizon on held-out data, against",
             "    persistence; drift watched after every plant change",
             "  7 services: scored against a written specification; trace,",
             "    specification and result kept as settlement evidence",
             "  open: contractual availability definitions and the grid",
             "    operator's service specification (U-118)"]
    emit("int_basis", lines)


if __name__ == "__main__":
    by_hand()
    package()
    basis()
