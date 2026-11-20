"""Chapter 47, round v: production of the PV structures (posts driven,
tables assembled), the galvanizing kettle and the tower fabricator's
lines as bottlenecks, and the days a foundation waits at its hold points.

Run from the project root:   python -m companion.ch47.examples_v
Writes companion/ch47/expected/v_*.txt.
Teaching values (A-490 to A-497).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch30 import sources as s30
from companion.ch47 import sources as src
from companion.ch47.common import emit


# ------------------------------------------------ 1. PV posts and tables
def pv_rates(tables: int = 2100, posts_per_table: int = 12,
             posts_per_rig_day: int = 220, tables_per_crew_day: int = 9,
             window_days: int = 60) -> dict:
    posts = tables * posts_per_table
    rig_days = posts / posts_per_rig_day
    crew_days = tables / tables_per_crew_day
    rigs = math.ceil(rig_days / window_days)
    crews = math.ceil(crew_days / window_days)
    lines = [f"PV structures of {tables:,} tables in a {window_days}-day window "
             "(teaching rates)",
             f"  posts: {posts:,} at {posts_per_rig_day} a rig-day = "
             f"{rig_days:.0f} rig-days -> {rigs} rigs",
             f"  tables: at {tables_per_crew_day} a crew-day = {crew_days:.0f} "
             f"crew-days -> {crews} crews",
             "  every rig drives posts from the survey marks of lesson C:",
             f"  a wrong mark repeats in a whole row - with {rigs} rigs, a day's",
             "  wrong mark is about "
             f"{posts_per_rig_day} posts; the first row of each day is",
             "  surveyed before the rig moves on"]
    emit("v_pvrates", lines)
    return dict(posts=posts, rigs=rigs, crews=crews)


# ------------------------------------------------ 2. galvanizing kettle
def kettle(steel_t: float = 3211.0, t_per_day: float = 45.0,
           other_share: float = 0.35, window_days: int = 120) -> dict:
    ours = t_per_day * (1 - other_share)
    days = steel_t / ours
    lines = [f"galvanizing the PV steel: one kettle of {t_per_day:.0f} t a day, "
             f"{other_share:.0%} booked by others",
             f"  {steel_t:,.0f} t at {ours:.1f} t a day for Plant P: {days:.0f} working "
             "days",
             f"  against a {window_days}-day supply window: "
             f"{'fits' if days <= window_days else 'does not fit'}",
             "  the kettle, not the rolling mill, sets the PV steel's date;",
             "  a lot re-galvanized (lesson B, Z-02) takes its slot again - a",
             "  rejected lot costs kettle days as well as zinc"]
    emit("v_kettle", lines)
    return dict(days=days)


# ------------------------------------------------ 3. tower fabricator's lines
def tower_lines(days_per_section: float = 4.0, lines_n: int = 2,
                erect_every: float = 3.0) -> dict:
    sections = src.TURBINES * 4
    days = sections * days_per_section / lines_n
    per_tower = 4 * days_per_section / lines_n
    # tower k is ready at k * per_tower - lead; the crane needs it at (k - 1) * erect
    lead = max(k * per_tower - (k - 1) * erect_every
               for k in range(1, src.TURBINES + 1))
    at_t05 = min(src.TURBINES, int((4 * erect_every + lead) // per_tower))
    lines = [f"tower fabrication: {sections} sections, {days_per_section:.0f} days a "
             f"section on {lines_n} lines",
             f"  {days:.0f} working days, a tower every {per_tower:.0f} days; the "
             f"crane takes one every {erect_every:.0f}",
             f"  so fabrication starts at least {lead:.0f} days before the first "
             "erection",
             f"  with that lead, about {at_t05} towers are made by the day the crane",
             "  reaches T05: another tower can be erected while T05's holds",
             "  close - re-sequencing removes round u's idle days, if that",
             "  tower's foundation and grout are ready too (ch 49)"]
    emit("v_lines", lines)
    return dict(days=days, lead=lead, at_t05=at_t05)


# ------------------------------------------------ 4. waiting at hold points
def hold_waits(seed: int = 4704, visits_per_week: int = 2, holds: int = 6,
               n: int = 12, notice_days: float = 2.0) -> dict:
    rng = np.random.default_rng(seed)
    gap = 7 / visits_per_week
    ready = rng.uniform(0, gap, (n, holds))           # time since last visit
    wait_random = gap - ready                         # until the next visit
    total = float(wait_random.sum())
    with_notice = float(np.clip(wait_random - notice_days, 0, None).sum())
    lines = [f"days a foundation waits at its {holds} hold points for the engineer",
             f"  engineer on site {visits_per_week} times a week; {n} foundations "
             "(synthetic)",
             f"  waiting when the work is simply ready: {total:.0f} days in all, "
             f"{total / n:.1f} a foundation",
             f"  with {notice_days:.0f} days' notice of each hold: {with_notice:.0f} "
             "days in all",
             "  a hold point costs time only when nobody planned it: the",
             "  look-ahead schedule names each hold and books the engineer",
             "  (ch 49) - the hold itself is not the delay, the surprise is"]
    emit("v_holds", lines)
    return dict(total=total, notice=with_notice)


if __name__ == "__main__":
    pv_rates()
    kettle()
    tower_lines()
    hold_waits()
