"""Chapter 29, lab H (worked water-stewardship case): compare no
cleaning, wet truck washing on a 4 % trigger, manual dry brushing and dry
robots against soiling loss, energy gained, cost, water, brine, worker
exposure and diesel; test the truck policy in two dry years; size the
water infrastructure; and write the monitoring plan and uncertainty
register.

Run from the project root:   python -m companion.ch29.lab_h
Writes companion/ch29/expected/h_*.txt and diagrams/data/ch29-cleaning.csv.
Soiling and cost results of chapter 10 (A-196, A-197, A-209); water of
lesson G; exposure and diesel rates are teaching values (A-352).
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np

from companion.ch10 import lab_d as l10
from companion.ch29 import examples_g as g
from companion.ch29 import sources as src
from companion.ch29.common import csv, emit

AREA_PER_DAY = 25_000.0          # m2 a truck crew washes in a day (teaching)
MODULES_PER_PERSON_DAY = 1_500   # manual dry brushing (teaching)
ROBOT_H_A_YEAR = 1.0             # maintenance person-hours per robot (teaching)
TRUCK_KM_A_DAY, DIESEL_L_KM = 40.0, 0.4
RO_M3_H = 3.0                    # RO unit, treated m3 an hour (teaching)
POLICIES = ("no cleaning", "truck at 4 % loss", "manual dry every 10 d", "robot every 12 d")
SHORT = {"no cleaning": "none", "truck at 4 % loss": "truck, wet",
         "manual dry every 10 d": "manual, dry", "robot every 12 d": "robot, dry"}


def ch10_policies() -> dict:
    """Loss %, lost and cleaning u, total u/yr and water m3/yr of the ch 10 policies."""
    text = (Path(l10.__file__).parent / "expected" / "d_policies.txt").read_text(encoding="utf-8")
    out = {}
    num = r"\s+([\d.]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)"
    for name in POLICIES:
        m = re.search(re.escape(name) + num, text)
        f = [float(x.replace(",", "")) for x in m.groups()]
        out[name] = dict(loss=f[0], lost=f[1], clean=f[2], total=f[3], water=f[4])
    out["robot every 12 d"]["total"] = l10.robot_annual(400.0)      # with capital and upkeep
    return out


def criteria() -> dict:
    pol = ch10_policies()
    rows = {}
    for name, p in pol.items():
        gain = (pol["no cleaning"]["lost"] - p["lost"]) / l10.PRICE
        raw = p["water"] / g.RO_RECOVERY
        washes = round(p["water"] / src.WASH_M3)
        truck_days = washes * src.DEMAND["module_area_m2"] / AREA_PER_DAY
        if name.startswith("truck"):
            hours = truck_days * 2 * 8
        elif name.startswith("manual"):
            passes = p["clean"] / (l10.METHODS["manual dry"]["cost"] * l10.N_MODULES)
            hours = passes * l10.N_MODULES / MODULES_PER_PERSON_DAY * 8
        elif name.startswith("robot"):
            hours = l10.N_MODULES / 52 * ROBOT_H_A_YEAR
        else:
            hours = 0.0
        rows[name] = dict(p, gain=gain, raw=raw, brine=raw - p["water"], truck_days=truck_days,
                          hours=hours, diesel=truck_days * TRUCK_KM_A_DAY * DIESEL_L_KM / 1000)
    return rows


def strategies() -> None:
    rows = criteria()
    summer = src.WELLS["W-1"]["safe_l_s"] / 1000 * 86400 * 31 * 0.5 * src.WELLS["W-1"]["summer_factor"]
    lines = ["cleaning strategies against water and the other criteria (worked case)",
             "  strategy       loss %   energy gained MWh   cost k u/yr   raw water m3"]
    for name, r in rows.items():
        lines.append(f"  {SHORT[name]:13s}  {r['loss']:6.2f}   {r['gain']:17,.0f}   {r['total'] / 1e3:11,.0f}"
                     f"   {r['raw']:12,.0f}")
    lines += ["",
              "  strategy       brine m3   truck-days   person-h among arrays   diesel m3"]
    for name, r in rows.items():
        lines.append(f"  {SHORT[name]:13s}  {r['brine']:8,.0f}   {r['truck_days']:10.0f}"
                     f"   {r['hours']:21,.0f}   {r['diesel']:9.1f}")
    csv("ch29-cleaning.csv", "name,loss,cost,raw",
        [(SHORT[n].split(",")[0], f"{r['loss']:.2f}", f"{r['total'] / 1e3:.0f}", f"{r['raw']:.0f}")
         for n, r in rows.items()])
    lines += [f"  (raw water at {100 * g.RO_RECOVERY:.0f} % RO recovery; a wash is"
              f" {src.WASH_M3:.0f} m3 treated;",
              f"  a two-wash month needs {2 * src.WASH_M3 / g.RO_RECOVERY:.0f} m3 raw against"
              f" {summer:.0f} m3 from W-1 in summer)",
              "  manual brushing gains the most energy but costs the most",
              "  of the three and puts people among the live arrays for",
              "  thousands of hours; the truck needs the scarce summer",
              "  water and makes brine; the robots are cheapest, use no",
              "  water and need the fewest hours - but only if the module",
              "  maker accepts them in the warranty (ch 10, D-014)"]
    emit("h_strategies", lines)


def drought() -> None:
    pol = ch10_policies()
    use = g.demand()
    w1 = src.WELLS["W-1"]
    base = w1["safe_l_s"] / 1000 * 86400 * g.DAYS * 0.5
    per = src.WASH_M3 / g.RO_RECOVERY                   # raw m3 for one wash
    tank = 2500.0 - 180.0
    cases = {"drought (lesson G)": np.where(g.SUMMER, base * w1["summer_factor"] * 0.6, base * 0.9),
             "severe: 30 % in summer, permit 150 m3/month":
                 np.minimum(np.where(g.SUMMER, base * 0.3, base * 0.8), 150.0)}
    n_want = sum(src.DEMAND["washes"])
    lines = ["the truck policy in the SECOND of two dry years (tank kept above 20 %",
             "  of its usable volume; a wash is skipped rather than empty the tank)",
             "  case                                         washes done   loss %"]
    for name, supply in cases.items():
        stock, done = tank, 0
        for year in (1, 2):
            for m in range(12):
                stock = min(stock + supply[m] - use["staff"][m], tank)
                for _ in range(src.DEMAND["washes"][m]):
                    if stock - per >= 0.2 * tank:
                        stock -= per
                        done += year == 2
        frac = 1 - done / n_want
        t, n = pol["truck at 4 % loss"]["loss"], pol["no cleaning"]["loss"]
        lines.append(f"  {name:44s} {done:4d} of {n_want}   {t + frac * (n - t):6.2f}")
    lines += ["  (loss linear between the truck and no-cleaning policies)",
              "  an ordinary drought is carried by the tank; a second severe",
              "  year with a capped permit skips washes and the soiling loss",
              "  climbs - a strategy that needs water must say what happens",
              "  when the water is not there; the dry methods have no such case"]
    emit("h_drought", lines)


def infrastructure() -> None:
    brine = criteria()["truck at 4 % loss"]["brine"]
    lines = ["water infrastructure for the truck policy (teaching sizing)",
             "  item                 size              why"]
    rows = [("RO unit", f"{RO_M3_H:.0f} m3/h treated",
             f"one wash ({src.WASH_M3:.0f} m3) in {src.WASH_M3 / RO_M3_H / 24:.1f} days"),
            ("treated water tank", "120 m3", "one full wash ready"),
            ("raw water tank", "2,500 m3", "fire reserve + summer deficit"),
            ("brine pond (lined)", "evaporation", f"about {brine:,.0f} m3 brine a year"),
            ("meters", "8 points", "the monitoring plan")]
    for item, size, why in rows:
        lines.append(f"  {item:19s}  {size:16s}  {why}")
    lines += ["  with robots the RO unit and the brine pond disappear; the",
              "  tank stays for staff, the fire reserve and construction"]
    emit("h_infra", lines)


def plan() -> None:
    meters = ["W-1 and W-2 abstraction (permit reporting)", "tank level with a low alarm above the"
              " fire reserve", "RO feed and permeate (recovery)", "brine to the pond",
              "truck filling point", "staff and building use", "construction draw-off (temporary)",
              "rain gauge at the soiling station"]
    risks = [("well yield in a drought", "pumping test, 2-year records", "plant"),
             ("soiling rate", "two soiling stations (D-014)", "O&M"),
             ("water right volume", "permit (U-104)", "developer"),
             ("RO recovery and brine", "supplier test, pond records", "O&M"),
             ("fire reserve volume", "fire strategy (U-105)", "fire eng.")]
    lines = ["water management plan: metering and the uncertainty register"]
    lines += [f"  meter {k}: {m}" for k, m in enumerate(meters, 1)]
    lines += ["  uncertainty                     closed by                        owner"]
    for r, c, o in risks:
        lines.append(f"  {r:30s}  {c:31s}  {o}")
    lines += ["  the plan is reviewed after the first dry season with the",
              "  metered data; the choice of cleaning method is revisited",
              "  if water or soiling differ from the assumptions"]
    emit("h_plan", lines)


if __name__ == "__main__":
    strategies()
    drought()
    infrastructure()
    plan()
