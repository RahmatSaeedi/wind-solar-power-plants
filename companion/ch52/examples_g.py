"""Chapter 52, lesson G: water-dependent maintenance - four cleaning
methods side by side, the best interval between campaigns, residue from
the wash water, breakage and warranty, when to wash in the heat, runoff,
and the robots' own maintenance.

Run from the project root:   python -m companion.ch52.examples_g
Writes companion/ch52/expected/g_*.txt and diagrams/data/ch52-interval.csv.
Teaching values (A-535).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch52 import sources as src
from companion.ch52.common import csv, emit
from plantp import datapack

MODULES = 109_200
MWP = 60.0
SHORT = {"truck with brush, RO water": "truck + brush, RO",
         "truck, high pressure lance": "truck, HP lance",
         "waterless robot (dry brush)": "dry robot",
         "manual, low pressure, RO": "manual, low P, RO"}


def campaign_cost(method: str, labour_u_h: float = 40.0, truck_u: float = 1_000.0,
                  robot_u: float = 1_400.0) -> float:
    l_mod, rec, brk, crew_h_mw, run = src.CLEAN_METHODS[method]
    water = MODULES * l_mod / 1000 * src.SOILING["water_u_m3"]
    crew = crew_h_mw * MWP * labour_u_h
    kit = robot_u if "robot" in method else (truck_u if "truck" in method else 0.0)
    return water + crew + kit


# ------------------------------------------------ 1. four methods
def methods() -> dict:
    out = {}
    for k, (l_mod, rec, brk, crew, run) in src.CLEAN_METHODS.items():
        out[k] = dict(water=MODULES * l_mod / 1000, rec=rec, broken=brk * MODULES / 1e5,
                      crew=crew * MWP, runoff=MODULES * run / 1000, cost=campaign_cost(k))
    lines = ["one cleaning campaign of the whole PV field by method (teaching data)",
             "  method              water m3  recov %  broken  crew h  runoff m3   cost u"]
    lines += [f"  {SHORT[k]:18s} {v['water']:9.0f} {v['rec']:8.1f} {v['broken']:7.1f}"
              f" {v['crew']:7.0f} {v['runoff']:10.0f} {v['cost']:8,.0f}" for k, v in out.items()]
    lines += ["  the lance recovers most and breaks most (pressure above the",
              "  module maker's limit risks the warranty); the dry robot",
              "  uses no water and recovers least; manual work is gentle",
              "  and slow - the choice weighs all six columns, not one"]
    emit("g_methods", lines)
    return out


# ------------------------------------------------ 2. best interval between campaigns
def interval() -> dict:
    s = src.SOILING
    loss_rate = s["rate_pct_day"] / 100 * s["mwh_day"] * s["price"]     # u per day per day
    out = {}
    rows = []
    for k in src.CLEAN_METHODS:
        c = campaign_cost(k)
        t = math.sqrt(2 * c / loss_rate)
        out[k] = (c, t, c / t + loss_rate * t / 2)
    for t in range(5, 91, 5):
        c = campaign_cost("truck with brush, RO water")
        rows.append((t, round(c / t, 1), round(loss_rate * t / 2, 1)))
    csv("ch52-interval.csv", "days,clean,soil", rows)
    lines = [f"cleaning interval: soiling {s['rate_pct_day']} %/day of {s['mwh_day']:.0f} MWh/day "
             f"at {s['price']:.0f} u/MWh",
             "  cost per day = C/T + r E p T / 2 ; best T = sqrt(2 C / (r E p))",
             "  method                C u    best T days   u per day"]
    lines += [f"  {SHORT[k]:18s} {c:7,.0f} {t:11.0f} {d:11,.0f}" for k, (c, t, d) in out.items()]
    lines += ["  a cheap campaign is worth doing often; the formula assumes a",
              "  steady soiling rate and full recovery (the robot recovers",
              "  less, breakage is not priced) - a dust storm resets it, so",
              "  the trigger of ch 10 (measured soiling ratio) overrides the",
              "  calendar"]
    emit("g_interval", lines)
    return out


# ------------------------------------------------ 3. residue from the wash water
def residue(tds_ro: float = 60.0, tds_well: float = 1_800.0, limit_mg_m2: float = 50.0) -> dict:
    area = 2.6                                                        # m2 a module (teaching)
    film = 0.1                                                        # L left on a module to dry
    out = {}
    for name, tds in (("RO permeate", tds_ro), ("raw well water", tds_well)):
        out[name] = tds * film / area                                # mg/m2
    lines = [f"what the wash leaves behind: dissolved solids x water left to dry / area"]
    lines += [f"  {k:16s} {v:6.0f} mg/m2" + ("  over the teaching limit" if v > limit_mg_m2 else "")
              for k, v in out.items()]
    lines += ["  raw well water leaves a film of salts that soils faster than",
              "  the dust it removed - RO treatment (ch 29) is part of the",
              "  cleaning system, and its failure stops the campaign (ch 51)"]
    emit("g_residue", lines)
    return out


# ------------------------------------------------ 4. breakage and warranty
def breakage(campaigns: int = 8) -> dict:
    out = {k: brk * MODULES / 1e5 * campaigns for k, (_, _, brk, _, _) in src.CLEAN_METHODS.items()}
    lines = [f"modules broken or cracked a year at {campaigns} campaigns (teaching rates)"]
    lines += [f"  {SHORT[k]:18s} {v:6.1f}" for k, v in out.items()]
    lines += ["  the lance's count is the visible part: micro-cracks show",
              "  later in EL images (ch 41) and the maker may refuse the claim",
              "  if the wash broke its limits - the method is written into",
              "  the O&M contract with the maker's cleaning instructions"]
    emit("g_breakage", lines)
    return out


# ------------------------------------------------ 5. when to wash in the heat
def wash_hours(limit: float = 35.0) -> dict:
    h = datapack.load_hourly()
    t = h["t_air_c"].to_numpy(float)
    hr = np.arange(t.size) % 24
    night = (hr >= 20) | (hr < 6)
    day = (hr >= 8) & (hr < 18)
    hot_day = int(np.sum(day & (t >= limit)))
    lines = [f"washing crews and heat: day hours (08-18) at or above {limit:.0f} C: {hot_day}",
             f"  night hours (20-06) in the year: {int(night.sum()):,}, of them at or above "
             f"{limit:.0f} C: {int(np.sum(night & (t >= limit)))}",
             "  washing at night keeps the crew out of the heat (ch 32), the",
             "  glass away from a cold-water shock on a hot module, and the",
             "  energy lost while washing near zero - it needs lighting,",
             "  a night permit and a fatigue-aware roster (ch 51)"]
    emit("g_hours", lines)
    return dict(hot_day=hot_day, night=int(night.sum()),
                hot_night=int(np.sum(night & (t >= limit))))


# ------------------------------------------------ 6. runoff
def runoff(campaigns: int = 8) -> dict:
    out = {k: MODULES * run / 1000 * campaigns for k, (_, _, _, _, run) in src.CLEAN_METHODS.items()}
    lines = [f"runoff from the arrays a year at {campaigns} campaigns (m3)"]
    lines += [f"  {SHORT[k]:18s} {v:7.0f}" for k, v in out.items()]
    lines += ["  under the drip line the water cuts channels (ch 33 drip-line",
              "  erosion); the lance's runoff is the largest - the drainage",
              "  inspection after a campaign is a task in the plan (lesson B)"]
    emit("g_runoff", lines)
    return out


# ------------------------------------------------ 7. robots' own maintenance
def robots(n: int = 2_100, fail_yr: float = 0.4, mttr_d: float = 6.0) -> dict:
    down = n * fail_yr * mttr_d / 365
    cover = 1 - down / n
    lines = [f"{n:,} cleaning robots (one a row), {fail_yr} failures a robot-year, "
             f"{mttr_d:.0f} days to repair",
             f"  robots down on an average day {down:.1f}; rows cleaned on schedule "
             f"{cover:.1%}",
             "  a robot down in the dust season leaves its row soiling",
             "  while the others are clean: the row shows in the string",
             "  currents (lesson D) - robot spares are a cleaning-system",
             "  task in the CMMS like any other asset (lesson I)"]
    emit("g_robots", lines)
    return dict(down=down, cover=cover)


if __name__ == "__main__":
    methods()
    interval()
    residue()
    breakage()
    wash_hours()
    runoff()
    robots()
