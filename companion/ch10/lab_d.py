"""Chapter 10, section D - soiling and cleaning: a synthetic soiling-station
year with rain, the soiling rate estimated from it, the optimal cleaning
interval, and the year simulated under several cleaning policies.

Run from the project root:   python -m companion.ch10.lab_d
Writes companion/ch10/expected/d_*.txt and diagrams/data/ch10-*.csv.
Teaching values A-195 .. A-197 (fictional, seed 41).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch10.common import csv, emit

DAYS = 365
E_DAY = 112.9e3 / DAYS            # MWh/day of AC energy (DC/AC 1.2, c_dcac)
PRICE = 50.0                      # u/MWh (chapter 5)
N_MODULES = 4200 * 26


def station_year(seed: int = 41):
    """Daily soiling loss at a soiling station (reference cell cleaned
    daily, A-195): dry-season accumulation 0.30 %/day, wet season 0.10
    %/day; rain of more than 5 mm cleans fully, smaller rain halves the
    loss; measurement noise 0.3 %."""
    rng = np.random.default_rng(seed)
    d = np.arange(DAYS)
    dry = (d >= 120) & (d < 300)
    rate = np.where(dry, 0.0030, 0.0010)
    p_rain = np.where(dry, 0.01, 0.12)
    rain = rng.random(DAYS) < p_rain
    heavy = rain & (rng.random(DAYS) < 0.6)
    loss = np.zeros(DAYS)
    x = 0.0
    for k in range(DAYS):
        x += rate[k]
        if heavy[k]:
            x = 0.0
        elif rain[k]:
            x *= 0.5
        loss[k] = x
    measured = loss + rng.normal(0, 0.003, DAYS)
    return d, loss, measured, rain, heavy, rate


# [start: rate]
def estimate_rates(d, measured, rain):
    """Soiling rate as the slope of the measured loss in each rain-free
    spell of at least ten days (least squares per spell)."""
    rates, spell = [], []
    for k in range(len(d)):
        if rain[k]:
            if len(spell) >= 10:
                rates.append((spell[0], np.polyfit(d[spell], measured[spell], 1)[0]))
            spell = []
        else:
            spell.append(k)
    if len(spell) >= 10:
        rates.append((spell[0], np.polyfit(d[spell], measured[spell], 1)[0]))
    return rates
# [end: rate]


def soil_data() -> None:
    d, loss, meas, rain, heavy, rate = station_year()
    est = estimate_rates(d, meas, rain)
    dry = [r for s, r in est if 120 <= s < 300]
    wet = [r for s, r in est if not 120 <= s < 300]
    lines = ["soiling station, synthetic year (seed 41, A-195):",
             f"  rain days {int(rain.sum())} (heavy {int(heavy.sum())}); mean "
             f"soiling loss without cleaning {100 * loss.mean():.2f} %",
             f"  worst day {100 * loss.max():.1f} % (day {int(np.argmax(loss))})",
             f"  rain-free spells of 10+ days: {len(est)}",
             f"  estimated rate, dry season {100 * np.mean(dry):.3f} %/day "
             "(true 0.300)",
             f"  estimated rate, wet season {100 * np.mean(wet):.3f} %/day "
             "(true 0.100)" if wet else "  no wet-season spell long enough",
             "  the station measures the soiling of its own glass and place:",
             "  dust varies across a large plant, so two or more stations"]
    emit("d_soildata", lines)
    csv("ch10-soiling.csv", "d,loss,meas",
        [(int(a), f"{100 * b:.3f}", f"{100 * c:.3f}")
         for a, b, c in zip(d, loss, meas)])


METHODS = {                                     # A-196, teaching values
    "manual wet": dict(cost=0.35, water=1.5, removal=0.98),
    "truck wet": dict(cost=0.15, water=1.0, removal=0.95),
    "manual dry": dict(cost=0.12, water=0.0, removal=0.85),
    "robot dry": dict(cost=0.03, water=0.0, removal=0.90),
}


def optimum() -> None:
    r = 0.0030
    lines = ["optimal cleaning interval in the dry season,",
             "  T* = sqrt(2 C / (p E r eta)), eta = share of dirt removed",
             f"  daily energy {E_DAY:.0f} MWh, price {PRICE:.0f} u/MWh, rate "
             "0.30 %/day (A-196):",
             "  method       cost/cleaning u   T* days   cost per day u   water m3"]
    for name, m in METHODS.items():
        c = m["cost"] * N_MODULES
        t = math.sqrt(2 * c / (PRICE * E_DAY * r * m["removal"]))
        per_day = c / t + PRICE * E_DAY * r * m["removal"] * t / 2
        lines.append(f"  {name:11s}  {c:15,.0f}   {t:7.1f}   {per_day:14,.0f}"
                     f"   {m['water'] * N_MODULES / 1e3:8.0f}")
    lines += ["  cleaning cost per day and lost energy per day are equal at T*;",
              "  the robot's low cost per pass halves the best interval; its",
              "  capital, maintenance and warranty acceptance decide (A-196)"]
    emit("d_optimum", lines)
    rows = []
    c = METHODS["truck wet"]["cost"] * N_MODULES
    k = PRICE * E_DAY * r * METHODS["truck wet"]["removal"] / 2
    for t in range(2, 61, 2):
        rows.append((t, f"{c / t:.0f}", f"{k * t:.0f}"))
    csv("ch10-cleaning.csv", "t,clean,lost", rows)


def policies() -> None:
    d, loss_free, _, rain, heavy, rate = station_year()
    cases = [("no cleaning", None, 0), ("truck every 30 d", "truck wet", 30),
             ("truck every 14 d", "truck wet", 14),
             ("manual dry every 10 d", "manual dry", 10),
             ("robot every 2 d", "robot dry", 2),
             ("robot every 12 d", "robot dry", 12),
             ("truck at 4 % loss", "truck wet", -0.04)]
    lines = ["the soiling year under seven cleaning policies (A-197):",
             "  policy                 loss %   lost u    cleaning u   total u"
             "   water m3"]
    for name, meth, every in cases:
        x, lost, n_cl = 0.0, 0.0, 0
        for k in range(DAYS):
            x += rate[k]
            if heavy[k]:
                x = 0.0
            elif rain[k]:
                x *= 0.5
            due = (every < 0 and x > -every) or                 (every > 0 and k % every == every - 1)
            if meth and due:
                x *= 1 - METHODS[meth]["removal"]
                n_cl += 1
            lost += x
        loss_pct = 100 * lost / DAYS
        e_lost = lost * E_DAY
        cost = n_cl * (METHODS[meth]["cost"] * N_MODULES if meth else 0)
        water = n_cl * (METHODS[meth]["water"] * N_MODULES / 1e3 if meth else 0)
        lines.append(f"  {name:21s}  {loss_pct:5.2f}  {e_lost * PRICE:8,.0f}  "
                     f"{cost:10,.0f}  {e_lost * PRICE + cost:8,.0f}  {water:8,.0f}")
    lines += ["  rain cleans for free in the wet season, so a fixed calendar",
              "  wastes cleanings there; a trigger on measured soiling cleans",
              "  only when it pays and needs the station data of d_soildata"]
    emit("d_policies", lines)


def decision() -> None:
    saving = 310_025 - 164_783                  # truck trigger - robot 12 d
    af = (1 - 1.07 ** -15) / 0.07               # 15-year robot life, 7 %
    capex = saving * af
    rows_tables = 4200 * 26 / 52                # 52 modules per table row
    emit("d_decision", [
        "robot or truck? (yearly totals of d_policies, A-197):",
        f"  robot every 12 d saves {saving:,.0f} u/yr against the truck",
        "  on a 4 % trigger, before the robots' own capital and upkeep",
        f"  break-even capital over 15 years at 7 %: {capex / 1e6:.2f} million u",
        f"    = {capex / N_MODULES:.1f} u per module, or {capex / rows_tables:,.0f}"
        f" u per robot for {rows_tables:.0f} table rows of 52 modules",
        "  if robots cost less (with upkeep) and the module maker accepts",
        "  them in the warranty, robots win; else the truck on a trigger",
        "  water saved by robots: about 1,500 m3 a year (d_policies)"])


def robot_annual(capex_per_robot: float, upkeep: float = 0.03) -> float:
    """Robot policy cost a year: d_policies total plus annualised capital
    (15 years, 7 %) and upkeep as a share of capital (A-209)."""
    capex = capex_per_robot * N_MODULES / 52
    crf = 0.07 / (1 - 1.07 ** -15)
    return 164_783 + capex * (crf + upkeep)


def matrix(capex_per_robot: float = 400.0, w_water: float = 0.20,
           name: str = "d_matrix") -> None:
    """Weighted decision matrix for the cleaning basis (A-209: weights and
    the non-cost scores are teaching judgements, 1 = worst, 5 = best)."""
    cost = {"no cleaning": 478_247, "truck every 30 d": 340_745,
            "truck at 4 % trigger": 310_025,
            "robot every 12 d": robot_annual(capex_per_robot)}
    other = {                     # water, warranty, safety, robustness
        "no cleaning": (5, 5, 5, 1),
        "truck every 30 d": (2, 4, 2, 4),
        "truck at 4 % trigger": (2, 4, 3, 4),
        "robot every 12 d": (5, 3, 4, 2)}
    w_rest = (1 - 0.35 - w_water) / 3
    w = (0.35, w_water, w_rest, w_rest, w_rest)
    lo, hi = min(cost.values()), max(cost.values())
    lines = [f"cleaning decision matrix (A-209), robot capital "
             f"{capex_per_robot:.0f} u each, water weight {w_water:.2f}:",
             "  option                 cost u/yr  cost  water warr. safety"
             " robust  score"]
    ranked = []
    for k, c in cost.items():
        sc = 1 + 4 * (hi - c) / (hi - lo)
        row = (sc,) + other[k]
        total = sum(a * b for a, b in zip(w, row))
        ranked.append((total, k))
        lines.append(f"  {k:21s}  {c:9,.0f}  {sc:4.1f}  {row[1]:5d}  {row[2]:4d}"
                     f"  {row[3]:5d}  {row[4]:5d}  {total:5.2f}")
    best = max(ranked)
    lines.append(f"  highest score: {best[1]} ({best[0]:.2f})")
    emit(name, lines)


if __name__ == "__main__":
    matrix()
    matrix(capex_per_robot=700.0, name="d_matrix_hi")
    matrix(w_water=0.05, name="d_matrix_lw")
    soil_data()
    optimum()
    policies()
    decision()
