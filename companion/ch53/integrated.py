"""Chapter 53 - the three integrated Plant P examples: by hand, the lifecycle
review at year 18, and the lifecycle basis (decision D-057).

Run from the project root:   python -m companion.ch53.integrated
Writes companion/ch53/expected/int_*.txt.
"""
from __future__ import annotations

import math

from companion.ch53 import sources as src
from companion.ch53.common import emit
from plantp import lifecycle as lc


def by_hand() -> dict:
    g = src.GEARBOX
    t, k, c = g["hours"], g["k"], g["c"]
    med = c * ((t / c) ** k + math.log(2)) ** (1 / k) - t
    pv = lc.option_pv(0, 100.0, 0, 0, 7, src.RATE)
    fund = lc.sinking_fund(4_635.0, 7, 0.04)
    lines = ["three numbers by hand",
             f"  gearbox median remaining life: c((t/c)^k + ln 2)^(1/k) - t",
             f"    = {c:,.0f} x (({t:,.0f}/{c:,.0f})^{k} + 0.693)^(1/{k}) - {t:,.0f} = {med:,.0f} h",
             f"  100 k u a year for 7 years at {src.RATE:.1%}: present value {pv:,.0f} k u",
             f"  sinking fund for 4,635 k u in 7 years at 4 %: {fund:,.0f} k u a year"]
    emit("int_hand", lines)
    return dict(med=med, pv=pv, fund=fund)


REVIEW = [   # item, in place at year 18
    ("degradation and availability trends with intervals", True),
    ("lost energy by cause with an owner for each", True),
    ("remaining-life estimates for the major components", True),
    ("repair / replace decision record with assumptions", True),
    ("grid-requirement gap list for a repowering", False),
    ("decommissioning provision funded to the current estimate", False),
    ("waste routes and receivers named", False),
    ("closure commitments with evidence", False),
    ("workforce transition plan", False),
    ("records retention schedule and migration plan", False),
    ("footprint comparison on one boundary", True),
    ("lessons carried into the next specification", True)]


def review() -> dict:
    ok = sum(1 for _, d in REVIEW if d)
    lines = ["lifecycle review at year 18: what is in place"]
    lines += [f"  [{'x' if d else ' '}] {k}" for k, d in REVIEW]
    lines += [f"  {ok} of {len(REVIEW)} in place: the analysis is done, the closure",
              "  preparation is not - seven years is short for permits,",
              "  funds, routes and people"]
    emit("int_review", lines)
    return dict(ok=ok, total=len(REVIEW))


def basis() -> None:
    lines = ["D-056 -> D-057 lifecycle basis (teaching, Plant P at year 18)",
             "  1. performance: PV degrades 0.37 %/yr (model 0.5 %); wind",
             "     availability falls 0.30 points/yr since year 10 (wear-out)",
             "  2. gearboxes: monitor and repair at failure to year 25 (lesson D);",
             "     replacement only with a longer life or a resale value",
             "  3. inverters and SCADA/PPC: replace or upgrade before support",
             "     ends (year 21) - obsolescence, not condition, decides",
             "  4. repowering of the wind farm studied as a new grid application",
             "     (+55 GWh/yr inside the export limit; three requirement gaps)",
             "  5. decommissioning provision funded now (587 k u a year to",
             "     year 25); waste routes and receivers named; custody checked",
             "  6. closure commitments with owners and dates; workforce",
             "     transition plan; disclosure from 36 months before the end",
             "  7. records: retention schedule, migration of the CMMS and SCADA",
             "     history, access removal verified by scan",
             "  8. footprint compared on one boundary; avoided emissions",
             "     reported apart, with the displaced source stated",
             "  open: U-134 (permit and land-return conditions for repowering",
             "  and closure, local recycling routes, retention obligations)"]
    emit("int_basis", lines)


if __name__ == "__main__":
    by_hand()
    review()
    basis()
