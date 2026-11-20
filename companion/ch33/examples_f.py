"""Chapter 33, lesson F: water stewardship - who withdraws how much from
the aquifer, whether the aquifer can sustain it, how far the site wells
draw down the village well, a drought plan with triggers, cleaning and
waste water, and the indicators that show the plan works.

Run from the project root:   python -m companion.ch33.examples_f
Writes companion/ch33/expected/f_*.txt and diagrams/data/ch33-water.csv.
Teaching values (A-384); recharge, rights and permits come from the
hydrogeological study and the water authority (U-114).
"""
from __future__ import annotations

import math

from companion.ch33 import sources as src  # noqa: F401  (puts plantp on the path)
from companion.ch33.common import csv, emit
from companion.ch29 import sources as s29
from plantp import civil as cv

YEAR = 365 * 86400


def withdrawals() -> None:
    uses = [("village households (50 x 100 L/day)", 50 * 0.1 * 365),
            ("livestock (600 animals x 40 L/day)", 600 * 0.04 * 365),
            ("farms 1 and 2 (irrigation, teaching)", 9_000.0),
            ("plant operation (ch 29)", 2_986.0),
            ("construction, per year of 18 months (ch 29)", 87_460.0 / 1.5)]
    recharge = 20e6 * 0.120 * 0.03                      # 20 km2, 120 mm rain, 3 % recharge
    total_op = sum(v for n, v in uses if not n.startswith("construction"))
    total_con = total_op + uses[-1][1]
    csv("ch33-water.csv", "use,m3", [(k + 1, round(v)) for k, (_, v) in enumerate(uses)])
    lines = ["who takes water from the aquifer (m3 a year, teaching)"]
    for n, v in uses:
        lines.append(f"  {n:46s} {v:9,.0f}")
    lines += [f"  estimated recharge (20 km2, 120 mm, 3 %): {recharge:9,.0f}",
              f"  total in operation {total_op:,.0f} ({total_op / recharge * 100:.0f} % of recharge);"
              f" in construction {total_con:,.0f} ({total_con / recharge * 100:.0f} %)",
              "  in operation the plant is a small user beside the village",
              "  and its animals; in construction the dust water alone",
              "  would take most of the recharge - which is why it is",
              "  trucked in or replaced (ch 29), never pumped locally"]
    emit("f_withdrawals", lines)


def drawdown() -> None:
    w = s29.WELLS["W-1"]
    q = w["safe_l_s"] / 1000
    lines = ["drawdown at the village well from site well W-1 (Cooper-Jacob)",
             f"  pumping {w['safe_l_s']} L/s; T {w['t_m2_s']:.1e} m2/s; S {w['s']:.0e}",
             "  distance m   after 1 year m   after 10 years m"]
    for r in (500, 1500, 3000):
        d1 = cv.cooper_jacob(q, w["t_m2_s"], w["s"], r, YEAR)
        d10 = cv.cooper_jacob(q, w["t_m2_s"], w["s"], r, 10 * YEAR)
        lines.append(f"  {r:10d}   {max(d1, 0):14.2f}   {max(d10, 0):16.2f}")
    lines += ["  the village well about 3 km away sees a few tenths of a",
              "  metre that grow slowly over the years - small next to",
              "  the seasonal swing, but measurable: a monitoring well",
              "  between the two and an agreed trigger (lesson C) turn",
              "  the estimate into evidence"]
    emit("f_drawdown", lines)


def drought_plan() -> None:
    rows = [("level falls 0.5 m below the seasonal normal", "watch",
             "weekly levels, cut non-essential use"),
            ("level falls 1.0 m or spring flow halves", "restrict",
             "washing paused or trucked, no dust water from wells"),
            ("village well cannot meet demand", "emergency",
             "site pumping stops, water shared with the village")]
    lines = ["drought plan for the site wells (teaching triggers)",
             "  trigger                                        stage"]
    for t, st, a in rows:
        lines += [f"  {t:46s} {st}", f"      action: {a}"]
    saved = 2_986 - 20 * 0.060 * 365                 # all but the staff's water
    lines += [f"  pausing washing saves about {saved:,.0f} m3 a year at the cost",
              "  of soiling losses (ch 10): the plant gives way first,",
              "  because the village has no other source - triggers and",
              "  actions are agreed with the water authority and the",
              "  village before the first dry year"]
    emit("f_drought", lines)


def wastewater() -> None:
    lines = ["cleaning runoff and wastewater (teaching)",
             f"  one wash: {s29.WASH_M3:.0f} m3 of treated water on 280,000 m2 of modules",
             f"  = {s29.WASH_M3 / 280_000 * 1000:.2f} L/m2 - it soaks in under the tables;",
             "  no detergent is used, so the runoff is clean water",
             "  RO reject (40 % of feed, saline): about 1,000 m3 a year to",
             "  a lined evaporation pond, not to the ground",
             "  staff 20 x 60 L/day = 1.2 m3/day to a septic system",
             "  construction camp (if on site, ch 32): about 30 m3/day",
             "  to a package treatment plant with a discharge permit",
             "  each stream has a route, a test and a record"]
    emit("f_wastewater", lines)


def performance() -> None:
    energy_mwh = 295_100.0
    water = 2_986.0 + 1_000.0
    lines = ["water indicators of the operating plant (teaching)",
             f"  water intensity: {water / energy_mwh * 1000:.1f} L per MWh",
             f"  share of washing water reused: 0 % (target 30 % by year 3)",
             f"  village well level change: within the agreed trigger",
             "  the plant's intensity is tiny beside thermal plants, but",
             "  the relevant comparison is local: what its water means",
             "  to the village wells in the driest month"]
    emit("f_performance", lines)


if __name__ == "__main__":
    withdrawals()
    drawdown()
    drought_plan()
    wastewater()
    performance()
