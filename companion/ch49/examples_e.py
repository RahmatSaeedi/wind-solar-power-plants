"""Chapter 49, lesson E (construction project controls): the six-week
look-ahead and its constraints, productivity by week, working hours lost
to wind and heat in the data-pack year, a recovery plan priced against
delay damages, and two subcontractors booked into one area.

Run from the project root:   python -m companion.ch49.examples_e
Writes companion/ch49/expected/e_*.txt and diagrams/data/ch49-*.csv.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch49 import sources as src
from companion.ch49.common import csv, emit
from plantp import construction as con
from plantp import datapack


def lookahead() -> dict:
    pk = {k: [f"{k}|{c}" for c in v[0]] for k, v in src.LOOKAHEAD.items()}
    start = {k: v[1] for k, v in src.LOOKAHEAD.items()}
    open_ = con.lookahead(pk, src.CLEARED, start, src.LOOK_TODAY)
    lines = [f"six-week look-ahead from day {src.LOOK_TODAY}: constraints not cleared "
             "by each start",
             "  package              start  open constraints"]
    for k, cons in open_.items():
        names = [c.split("|")[1] + ("" if src.CLEARED[c] is None
                                    else f" (day {src.CLEARED[c]})") for c in cons]
        lines.append(f"  {k:20s} {start[k]:5d}  {', '.join(names) or 'ready'}")
    ready = [k for k, c in open_.items() if not c]
    lines += [f"  ready to issue to the crews: {len(ready)} of {len(open_)}",
              "  piling waits two days for its posts; the road crossing and",
              "  T07 wait for things nobody has a date for - they leave the",
              "  look-ahead until they do, and the crews are planned on",
              "  work that is ready (ch 22 constraints)"]
    emit("e_lookahead", lines)
    return dict(open=open_, ready=ready)


def productivity() -> dict:
    rows = [(w, q, h, c, q / h) for w, q, h, c in src.WEEKS]
    csv("ch49-rate.csv", "week,rate,crews", [(w, round(r, 2), c) for w, _, _, c, r in rows])
    lines = [f"module mounting by week against the planned {src.PLAN_RATE} modules a crew-hour",
             "  week  modules  crew-h  crews  rate   factor"]
    lines += [f"  {w:4d}  {q:7d}  {h:6d}  {c:5d}  {r:4.2f}   {r / src.PLAN_RATE:5.2f}"
              for w, q, h, c, r in rows]
    three = np.mean([r for *_, c, r in rows if c == 3])
    four = np.mean([r for *_, c, r in rows if c == 4])
    low = [w for w, *_, r in rows if r / src.PLAN_RATE < 0.8]
    lines += [f"  mean rate with 3 crews {three:.2f}, with 4 crews {four:.2f}",
              f"  weeks below 80 % of plan: {', '.join(map(str, low))} - the daily",
              "  reports give the causes (teaching: week 34 a late module",
              "  delivery, week 37 wind stops); the fourth crew added",
              f"  {(four * 4) / (three * 3) - 1:.0%} output for 33 % more crews"]
    emit("e_productivity", lines)
    return dict(three=three, four=four, low=low)


def weather(wind_limit: float = 9.0, heat_limit: float = 38.0) -> dict:
    d = datapack.load_hourly()
    v10 = d["ws_60m_ms"].to_numpy() * (10 / 60) ** 0.14   # teaching shear to 10 m
    t = d["t_air_c"].to_numpy()
    hour = d.index.hour
    month = d.index.month
    work = (hour >= 6) & (hour < 18)
    rows = []
    for m in range(1, 13):
        sel = work & (month == m)
        n = int(sel.sum())
        w = int((sel & (v10 > wind_limit)).sum())
        h = int((sel & (t > heat_limit) & (v10 <= wind_limit)).sum())
        rows.append((m, n, w, h, (w + h) / n))
    csv("ch49-weather.csv", "month,wind,heat", [(m, w, h) for m, _, w, h, _ in rows])
    lines = [f"working hours 06-18 lost in the data-pack year: module handling above "
             f"{wind_limit:.0f} m/s",
             f"  at 10 m (scaled from 60 m), heat stop above {heat_limit:.0f} C "
             "(teaching limits)",
             "  month  hours  wind  heat  lost"]
    lines += [f"  {m:5d}  {n:5d}  {w:4d}  {h:4d}  {x:5.1%}" for m, n, w, h, x in rows]
    worst = max(rows, key=lambda r: r[4])
    lines += [f"  worst month {worst[0]}: {worst[4]:.0%} of the working hours; the year "
              f"{sum(r[2] + r[3] for r in rows) / sum(r[1] for r in rows):.1%}",
              "  the plan carries these hours month by month, not as one",
              "  annual allowance - the limits themselves come from the",
              "  module maker's handling instruction and the heat plan (ch 32)"]
    emit("e_weather", lines)
    return dict(rows=rows, worst=worst)


def recovery(total: int = 109_200, crews: int = 4, days_left: int = 70,
             ld_day: float = 25.0, crew_day: float = 1.8,
             ot_factor: float = 0.85) -> dict:
    four = [(q, h) for _, q, h, c in src.WEEKS if c == crews]
    rate = sum(q for q, _ in four) / sum(h for _, h in four)
    crew_h_day = sum(h for _, h in four) / len(four) / crews / 7
    left = total - sum(q for _, q, _, _ in src.WEEKS)
    need = left / (rate * crew_h_day * crews)
    late = max(0.0, need - days_left)
    options = {}
    for k in (1, 2):
        d = left / (rate * crew_h_day * (crews + k))
        options[f"{k} more crew(s)"] = (d, max(0.0, d - days_left) * ld_day
                                        + k * crew_day * d)
    d_ot = left / (rate * ot_factor * crew_h_day * 1.25 * crews)
    options["overtime +25 % hours"] = (d_ot, max(0.0, d_ot - days_left) * ld_day
                                       + 0.25 * crews * crew_day * 1.5 * d_ot)
    lines = [f"modules left {left:,}; {crews} crews at {rate:.2f} a crew-hour (weeks 35-38),",
             f"  {crew_h_day:.1f} crew-hours a day each; {days_left} days to the planned end",
             f"  as planned: {need:.0f} days against {days_left} left - {late:.0f} days late",
             f"  delay damages {ld_day} k u a day (teaching); a crew {crew_day} k u a day",
             "  option                  days  cost k u (damages + crews)"]
    lines.append(f"  {'do nothing':22s} {need:5.0f}  {late * ld_day:9.0f}")
    lines += [f"  {k:22s} {d:5.0f}  {c:9.0f}" for k, (d, c) in options.items()]
    best = min(options, key=lambda k: options[k][1])
    dear = max(options, key=lambda k: options[k][1])
    lines += [f"  cheapest: {best}; dearest: {dear} - its rate falls to",
              f"  {ot_factor:.0%} and tired crews are a safety risk; a crew is added",
              "  only with its supervisor, induction and tools (lesson A)"]
    emit("e_recovery", lines)
    return dict(need=need, late=late, options=options, best=best, left=left, rate=rate)


def clashes() -> list:
    plan = {   # (day, area): subcontractors booked
        (251, "PVF2-1 north"): ["piling (Sub P)"],
        (252, "PVF2-1 north"): ["piling (Sub P)", "trenching (Sub T)"],
        (252, "PVF2-2"): ["trenching (Sub T)"],
        (253, "PVF2-1 north"): ["piling (Sub P)", "trenching (Sub T)"],
        (254, "PVF2-1 south"): ["tables (Sub S)", "module delivery"],
        (255, "PVF2-1 south"): ["tables (Sub S)"],
    }
    bad = [(d, a, s) for (d, a), s in plan.items() if len(s) > 1]
    lines = ["coordination plan: areas booked by more than one party on a day"]
    lines += [f"  day {d} {a:14s} {' + '.join(s)}" for d, a, s in bad]
    lines += ["  a piling rig and an open trench in one area is a struck",
              "  cable or a rig at an edge; a delivery into a table crew's",
              "  area blocks both - the daily coordination meeting resolves",
              "  each before the day, and the permit to work names the area",
              "  (ch 32)"]
    emit("e_clash", lines)
    return bad


if __name__ == "__main__":
    lookahead()
    productivity()
    weather()
    recovery()
    clashes()
