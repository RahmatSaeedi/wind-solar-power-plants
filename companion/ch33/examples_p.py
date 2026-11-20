"""Chapter 33, lesson P (safeguards and footprint, more): change control
after a turbine is micro-sited, a dust complaint traced with the hourly
wind of the data pack, who came to the consultation meetings, the land
and livelihood risk register, allocation of recycled steel, the grid
factor over the years and grid charging of the battery, the factory grid
behind a module's footprint, and the replacements over the plant's life.

Run from the project root:   python -m companion.ch33.examples_p
Writes companion/ch33/expected/p_*.txt and diagrams/data/ch33-alloc.csv,
ch33-complaint.csv. Teaching values (A-380 to A-383).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch33 import sources as src
from companion.ch33.common import csv, emit
from companion.ch14 import examples_c as c14
from plantp import datapack
from plantp import envsocial as es

CAMP = src.DWELLINGS["herders' camp B (seasonal)"]


def _camp_noise(t: np.ndarray) -> float:
    d = np.hypot(t[:, 0] - CAMP[0], t[:, 1] - CAMP[1])
    return es.db_sum([es.noise_at(106.0, r) for r in d])


def _collisions(t: np.ndarray) -> float:
    b = src.BIRDS
    d = np.hypot(t[:, 0] - src.NEST[0], t[:, 1] - src.NEST[1])
    return sum(es.collision_estimate(b["passages_at_nest"] * math.exp(-r / b["decay_m"]),
                                     b["p_collision"], b["avoidance"]) for r in d)


def change_control() -> None:
    t0 = src.TURBINES.copy()
    d = np.hypot(t0[:, 0] - CAMP[0], t0[:, 1] - CAMP[1])
    k = int(np.argmin(d))
    t1 = t0.copy()
    t1[k] += 150.0 * (np.array(CAMP) - t0[k]) / d[k]          # 150 m toward the camp
    zc = float(c14.z_at([CAMP])[0])
    rows = [("night noise at camp, dB(A)", _camp_noise(t0), _camp_noise(t1), 1.0),
            ("flicker at camp, h/yr", c14.flicker_hours(t0, CAMP, zc)[0],
             c14.flicker_hours(t1, CAMP, zc)[0], 0.0),
            ("raptor collisions a year", _collisions(t0), _collisions(t1), 0.10)]
    lines = [f"change control: T{k + 1:02d} micro-sited 150 m toward the camp (teaching)",
             "  topic                          before    after   re-assess?"]
    for name, a, b, thr in rows:
        if "collisions" in name:
            redo = abs(b - a) / a > thr
        else:
            redo = (b - a) > thr if thr > 0 else b > a
        lines.append(f"  {name:28s} {a:8.1f} {b:8.1f}   {'YES' if redo else 'no'}")
    lines += [f"  T{k + 1:02d} now stands {d[k] - 150:.0f} m from the camp",
              "  a 'small' move by the civil contractor is a change to the",
              "  assessed layout: each topic has a trigger (here 1 dB, any",
              "  flicker, 10 % of collisions) written in the register, and",
              "  a change that trips one goes back to the specialist and,",
              "  if the permit says so, to the authority - before the",
              "  foundation is poured, not after (ch 32, management of change)"]
    emit("p_change", lines)


def complaint() -> None:
    d = datapack.load_hourly()
    wd = d["wd_100m_deg"].to_numpy()
    ws = d["ws_100m_ms"].to_numpy()
    hr = d.index.hour.to_numpy()
    fx, fy = src.DWELLINGS["farmhouse A"]
    bx = np.mean([p[0] for p in src.PV_BLOCK])
    by = np.mean([p[1] for p in src.PV_BLOCK])
    toward = math.degrees(math.atan2(bx - fx, by - fy)) % 360     # wind FROM the works
    diff = np.abs((wd - toward + 180) % 360 - 180)
    work = (hr >= 7) & (hr < 17)
    hit = work & (diff <= 22.5) & (ws >= 8.0)
    days = d.index.normalize()
    per_day = {}
    for day, h in zip(days[hit], np.ones(hit.sum())):
        per_day[day] = per_day.get(day, 0) + h
    spring = [k for k in per_day if k.month == 4]
    case1 = max(spring, key=lambda k: per_day[k])
    windy = [k for k in sorted(set(days[(ws >= 10) & work])) if k.month == 4 and k not in per_day]
    case2 = windy[0]
    rows = []
    for k, day in enumerate((case1, case2), 1):
        m = (days == day) & work
        rows.append((k, int(per_day.get(day, 0)), float(np.mean(wd[m]))))
    csv("ch33-complaint.csv", "case,hours,mean_dir", rows)
    n_days = len(per_day)
    lines = ["two dust complaints from farmhouse A traced with the hourly wind",
             f"  the PV works lie at {toward:.0f} deg from the farm; dust reaches it",
             "  when the wind blows from 22.5 deg either side of that at",
             "  >= 8 m/s (100 m height) in working hours",
             "  complaint   date         hours toward farm   mean direction deg"]
    for (k, h, mdir), day in zip(rows, (case1, case2)):
        lines.append(f"  {k:9d}   {day.date()}   {h:17d}   {mdir:18.0f}")
    lines += [f"  over the year such hours fall on {n_days} working days",
              "  complaint 1 is supported by the wind: the works were",
              "  upwind for hours - the response accepts it, waters the",
              "  block's west edge on forecast days and tells the family",
              "  what changed; complaint 2 is not supported by the wind",
              "  (it blew from elsewhere), so the response shows the",
              "  record, checks the other sources (the road, the track)",
              "  and still closes the case with the family - evidence,",
              "  not opinion, either way (lesson H)"]
    emit("p_complaint", lines)


def consultation() -> None:
    rows = [  # meeting, men, women, herders among them
        ("village scoping meeting", 64, 6, 2),
        ("draft ESIA meeting", 52, 9, 1),
        ("women-only meeting", 0, 38, 4),
        ("camp visit (herders)", 11, 9, 20),
        ("farm owners and strips", 12, 2, 0)]
    pop_women, pop_herders = 0.50, 0.08
    men = sum(r[1] for r in rows)
    women = sum(r[2] for r in rows)
    herd = sum(r[3] for r in rows)
    mixed_w = sum(r[2] for r in rows[:2]) / sum(r[1] + r[2] for r in rows[:2])
    lines = ["who came to the consultation meetings (synthetic records)",
             "  meeting                        men   women   herders"]
    for name, m, w, h in rows:
        lines.append(f"  {name:28s} {m:5d}   {w:5d}   {h:7d}")
    lines += [f"  women {women / (men + women) * 100:.0f} % of all attendance"
              f" ({mixed_w * 100:.0f} % at the two mixed village meetings),",
              f"    against about {pop_women * 100:.0f} % of the affected people",
              f"  herders {herd / (men + women) * 100:.0f} % of attendance against"
              f" {pop_herders * 100:.0f} % of the people - but",
              f"    {rows[3][3] / herd * 100:.0f} % of them came only when the meeting went to the camp",
              "  the mixed meetings alone would have heard almost no women",
              "  and few herders: the records show who was heard, and the",
              "  separate meetings are what made the consultation",
              "  representative - the attendance table is part of the file"]
    emit("p_consult", lines)


def land_register() -> None:
    rows = [  # risk, likelihood, impact, owner, control
        ("herders' route cut by the fence", 4, 4, "E&S manager", "gap and crossing"),
        ("customary grazing lost (3.1 ha)", 5, 2, "E&S manager", "agreement + plan"),
        ("strip owner not found for easement", 3, 3, "land agent", "notice, escrow"),
        ("informal user left off the list", 3, 4, "community liaison", "walk-over census"),
        ("dust on farm 1 crops", 3, 3, "construction lead", "watering, buffer"),
        ("water point not maintained", 2, 4, "E&S manager", "handover, budget")]
    lines = ["land and livelihood risk register (teaching scores 1-5)",
             "  risk                                 L  I  score  owner"]
    for r, lk, im, ow, ct in sorted(rows, key=lambda x: -x[1] * x[2]):
        lines.append(f"  {r:36s} {lk:2d} {im:2d}  {lk * im:5d}  {ow}")
        lines.append(f"      control: {ct}")
    lines += ["  the informal user and the absent owner are the risks a",
              "  title search misses; the census walks the land with the",
              "  village before any list is published (lesson B)"]
    emit("p_landrisk", lines)


def allocation() -> None:
    steel_t = 12 * 372.0                     # towers (ch 30)
    primary, scrap = 2_300.0, 600.0          # kg CO2e/t, teaching
    content, eol_rate = 0.30, 0.90
    cutoff = primary * (1 - content) + scrap * content
    avoided = primary - (primary - scrap) * eol_rate
    fifty = (cutoff + avoided) / 2
    rows = [("cut-off (recycled content)", cutoff), ("50:50", fifty),
            ("end-of-life (avoided burden)", avoided)]
    lines = ["allocation of recycled steel for the towers (teaching factors)",
             f"  primary {primary:.0f} kg/t, scrap route {scrap:.0f} kg/t;"
             f" content {content * 100:.0f} %, recycled at end {eol_rate * 100:.0f} %",
             "  method                            kg CO2e/t   towers t CO2e"]
    out = []
    for k, (name, f) in enumerate(rows, 1):
        out.append((k, round(f * steel_t / 1000)))
        lines.append(f"  {name:32s} {f:10.0f}   {f * steel_t / 1000:13,.0f}")
    csv("ch33-alloc.csv", "k,t", out)
    lines += [f"  the same towers carry {cutoff / avoided:.1f} times more carbon under",
              "  one rule than under another; neither is wrong - the study",
              "  states its rule, applies it to every item, keeps the",
              "  end-of-life credit apart (lab I) and shows the other rule",
              "  as a sensitivity"]
    emit("p_alloc", lines)


def grid_over_time() -> None:
    imp = src.OPERATION["own_use_mwh"] * 0.3                    # MWh a year imported
    years = np.arange(src.LIFE_YEARS)
    gf = 0.5 - (0.5 - 0.2) * years / (src.LIFE_YEARS - 1)       # declining grid (teaching)
    const = imp * 0.5 * src.LIFE_YEARS
    falling = float((imp * gf).sum())
    kwh = src.ENERGY_GWH["S1"] * 1e6 * src.LIFE_YEARS
    grid_charge = 40.0 * 300 * 0.30 * 0.5 * src.LIFE_YEARS     # MWh x cycles x share x t/MWh
    lines = ["the grid behind the plant's imports, and grid charging (teaching)",
             f"  own-use imports {imp:,.0f} MWh a year",
             f"    grid factor constant 0.5:         {const:8,.0f} t over 25 years",
             f"    falling 0.5 -> 0.2 over 25 years: {falling:8,.0f} t"
             f"  ({(const - falling) * 1e6 / kwh:.2f} g/kWh less)",
             "  S1 if 30 % of its charging came from the grid (NOT the base",
             f"    scenario): {grid_charge:,.0f} t = {grid_charge * 1e6 / kwh:.1f} g/kWh more",
             "  the grid's future matters little for a plant that powers",
             "  itself; grid charging would matter a lot, which is why it",
             "  is counted only where a scenario permits it and is stated",
             "  in the scope (lab I)"]
    emit("p_grid", lines)


def provenance() -> None:
    other, elec = 150.0, 500.0           # kg/kWp not from electricity; kWh/kWp at the factory
    lines = ["a module's footprint and the grid of its factory (teaching)",
             "  factory grid t/MWh   kg CO2e/kWp   60 MWp t CO2e"]
    for g in (0.3, 0.6, 0.8):
        f = other + elec * g
        lines.append(f"  {g:18.1f}   {f:11.0f}   {f * 60_000 / 1000:13,.0f}")
    lines += ["  the generic 450 kg/kWp of lab I matches a factory on a",
              "  grid of about 0.6; the same module from a factory on a",
              "  clean grid is a third lower - a factor's year and place",
              "  must match the product bought, or the study measures a",
              "  different module (lesson K)"]
    emit("p_provenance", lines)


def replacements() -> None:
    lca = src.LCA
    rows = [("inverters (half the item), year 13",
             lca["inverters and transformers (kW)"][0] * 0.5 * 45 / 1000),
            ("turbine major parts (10 %)", 0.10 * 60 * 300_000 / 1000),
            ("modules broken or failed (1 %)", 0.01 * 60_000 * 450 / 1000),
            ("cables and transformers", 0.0)]
    base = sum(a * f for a, f, _ in lca.values()) / 1000
    total = sum(t for _, t in rows)
    lines = ["replacements over 25 years, item by item (teaching)",
             "  item                               t CO2e"]
    for name, t in rows:
        lines.append(f"  {name:34s} {t:6,.0f}")
    lines += [f"  total {total:,.0f} t = {total / base * 100:.1f} % of manufacture and"
              " construction",
              "  lab I assumed 8 %: the item-by-item list is lower, so the",
              "  8 % is cautious - the study states which it used and why,",
              "  and S1 adds its battery augmentation separately (ch 19)"]
    emit("p_replace", lines)


if __name__ == "__main__":
    change_control()
    complaint()
    consultation()
    land_register()
    allocation()
    grid_over_time()
    provenance()
    replacements()
