"""Chapter 41, a sixth round: contact resistance in the series-resistance
budget, the curing buffer and the glass flow of the module line, the
tolerance stack along a table row, encapsulant shelf life on receipt,
a variables plan for glass transmittance, and lot-to-lot consistency of
the flash results.

Run from the project root:   python -m companion.ch41.examples_w
Writes companion/ch41/expected/w_*.txt and diagrams/data/ch41-*.csv.
Teaching values (A-443 to A-447); no process settings.
"""
from __future__ import annotations

import math
import random
from statistics import mean, pstdev

from companion.ch40.examples_v import variables_plan
from companion.ch41 import sources as src
from companion.ch41.common import csv, emit
from companion.ch41.examples_a import CELL


# ------------------------------------------- contact resistance
# [start: contact]
def contact_share(rho_c: float, s_cm: float = 0.13, w_f: float = 0.003):
    """Contact part of the series resistance (ohm cm2) when the current
    of a strip s wide enters a finger w_f wide: r_c ~ rho_c s / w_f
    (contact longer than the transfer length, a first estimate)."""
    return rho_c * s_cm / w_f
# [end: contact]


def contacts() -> dict[float, float]:
    out = {}
    lines = [f"contact resistance in the series-resistance budget "
             f"(total {CELL['rs']} ohm cm2)",
             "  rho_c mOhm cm2   contact part ohm cm2   share of the budget"]
    for rho in (1.0, 3.0, 10.0):
        r = contact_share(rho / 1000)
        out[rho] = r
        lines.append(f"  {rho:14.0f}   {r:20.3f}   {r / CELL['rs']:19.0%}")
    lines += ["  a well-fired contact takes under a tenth of the budget; a",
              "  poorly formed one takes most of it - the left wall of the",
              "  firing window (lesson B) is this term growing, and the",
              "  transfer-length test on sample cells measures it"]
    emit("w_contacts", lines)
    return out


# ------------------------------------------- curing buffer, glass flow
def flow(cure_h: float = 4.0, takt_s: float = 30.0,
         glass_kg: float = 20.7) -> dict[str, float]:
    buffer = cure_h * 3600 / takt_s
    per_h = 3600 / takt_s
    lines = [f"curing buffer and material flow at a {takt_s:.0f} s takt "
             "(teaching)",
             f"  sealant and potting need {cure_h:.0f} h before handling: "
             f"{buffer:,.0f} modules in the buffer",
             f"  glass in: {per_h:.0f} sheets an hour = {per_h * glass_kg / 1000:.1f}"
             " t an hour",
             f"  frames, boxes, pallets out: one finished pallet every "
             f"{31 * takt_s / 60:.1f} min",
             "  the buffer is floor space and work in progress, not idle",
             "  stock: shortening the cure moves the line's layout; the",
             "  glass flow sets the forklift and rack plan (ch 40, layout)"]
    emit("w_flow", lines)
    return dict(buffer=buffer, glass_t_h=per_h * glass_kg / 1000)


# ------------------------------------------- tolerance stack on a table
def stackup(n: int = 26, w_mm: float = 1134.0, tol_mm: float = 2.0,
            gap_mm: float = 20.0, gap_tol: float = 1.0) -> dict[str, float]:
    nominal = n * w_mm + (n - 1) * gap_mm
    worst = n * tol_mm + (n - 1) * gap_tol
    rss = math.sqrt(n * (tol_mm / 3) ** 2 + (n - 1) * (gap_tol / 3) ** 2) * 3
    lines = [f"{n} modules side by side on a table row (teaching tolerances)",
             f"  module width {w_mm:.0f} +- {tol_mm} mm; clamp gap {gap_mm:.0f} "
             f"+- {gap_tol} mm",
             f"  nominal length {nominal / 1000:.3f} m",
             f"  worst case +- {worst:.0f} mm; statistical (3 sigma) "
             f"+- {rss:.0f} mm",
             "  the end clamps need room for the statistical stack, not the",
             "  worst case - but a lot cut from one glass batch can all sit",
             "  near one tolerance edge, so the table keeps a margin and",
             "  installers set gaps with a gauge, not by eye"]
    emit("w_stackup", lines)
    return dict(worst=worst, rss=rss, nominal=nominal)


# ------------------------------------------- encapsulant shelf life
def shelf(seed: int = 4120) -> dict[str, int]:
    rng = random.Random(seed)
    rolls = []
    for k in range(40):
        made = rng.randrange(0, 240)                  # days before today
        temp = rng.choice([20, 22, 25, 28, 32])        # storage C
        rolls.append((f"R{k + 1:02d}", made, temp))
    life_25 = 180.0                                    # days at 25 C, teaching
    expired, close = [], []
    for rid, age, t in rolls:
        life = life_25 * 2 ** ((25 - t) / 10)
        left = life - age
        if left < 0:
            expired.append(rid)
        elif left < 30:
            close.append(rid)
    lines = ["encapsulant rolls on receipt and in store (teaching: 180 days",
             "  at 25 C, halving every 10 K warmer)",
             f"  40 rolls: {len(expired)} past their life, {len(close)} within 30 days",
             f"  past: {', '.join(expired[:8])}{' ...' if len(expired) > 8 else ''}",
             "  an encapsulant past its life may still laminate, but cures",
             "  differently (gel content, lesson C): rolls are used first in",
             "  first out by their remaining life, not by arrival, and the",
             "  store's temperature is logged as part of the material's record"]
    emit("w_shelf", lines)
    return dict(expired=len(expired), close=len(close))


# ------------------------------------------- glass transmittance plan
def glass_plan() -> dict[str, float]:
    n_var, k = variables_plan(0.01, 0.05)
    lines = ["incoming glass: solar transmittance against a lower limit",
             "  (AQL 1 %, LTPD 5 %; variables plan of ch 40)",
             f"  measure {n_var} sheets; accept if (mean - limit)/s >= {k:.2f}",
             "  an attribute pass/fail on the same risks needs 132 sheets;",
             "  transmittance is measured anyway, so the variables plan is",
             "  cheaper - but a lot whose readings are not normal (two",
             "  furnaces mixed) breaks its assumption: plot them first"]
    emit("w_glass", lines)
    return dict(n=n_var, k=k)


# ------------------------------------------- lot-to-lot consistency
def lots(seed: int = 4121) -> dict[str, int]:
    rng = random.Random(seed)
    means = []
    for lot in range(30):
        shift = -1.6 if lot >= 22 else 0.0           # a glass batch change
        means.append(round(552.4 + shift + rng.gauss(0, 0.35), 2))
    base = means[:15]
    cl, sd = mean(base), pstdev(base)
    lcl = cl - 3 * sd
    run = None
    for k in range(len(means) - 7):
        if all(m < cl for m in means[k:k + 8]):
            run = k + 8
            break
    first3 = next((k + 1 for k, m in enumerate(means) if m < lcl), None)
    csv("ch41-lots.csv", "lot,mean", [(k + 1, m) for k, m in enumerate(means)])
    lines = ["mean Pmax of 30 lots of 3,000 modules (chart from lots 1-15)",
             f"  centre {cl:.2f} W, lower limit {lcl:.2f} W",
             f"  first lot below the limit: {first3}; eight in a row below the "
             f"centre by lot {run}",
             "  a 1.6 W drop is inside every module's tolerance and every",
             "  lot's spread, yet the lot means show it within a few lots -",
             "  the factory asks what changed at lot 23 (a new glass batch)",
             "  before the buyer's laboratory finds it a year later"]
    emit("w_lots", lines)
    return dict(first=first3 or 0, run=run or 0)


if __name__ == "__main__":
    contacts()
    flow()
    stackup()
    shelf()
    glass_plan()
    lots()
