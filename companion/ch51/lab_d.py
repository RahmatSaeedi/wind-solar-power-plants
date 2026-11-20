"""Chapter 51, lesson D (shift simulation, the chapter's worked example):
one operating day of Plant P - the day-ahead plan, an intraday forecast
that is 20 MW higher at midday, an export restriction from the grid
operator and a battery that starts the day near its upper SOC limit -
played twice through the chapter 20 controller: following the plan, and
acting on the update and the notice. Decisions, communications and
learning are logged.

Run from the project root:   python -m companion.ch51.lab_d
Writes companion/ch51/expected/d_*.txt and diagrams/data/ch51-shift.csv.
Teaching values (A-522 onwards); S1 (battery) scenario.
"""
from __future__ import annotations

import numpy as np

from companion.ch20 import sources as s20
from companion.ch51.common import csv, emit
from plantp import control, operations

DAY = 34                                  # 4 February of the data-pack year
CAP = dict(start=11, end=15, mw=80.0, notice=10)       # grid operator's restriction
UPDATE_H = 9                              # intraday forecast arrives
SOC0 = 30.0                               # MWh at 06:00 handover (e_max 36)
SERVICE = (18, 22, 5.0)                   # REQ-S01 window and MW (ch 20)


def day_series():
    sl = slice(DAY * 24, DAY * 24 + 24)
    act = s20.poc_actual()[sl]
    da = s20.poc_forecast(24)[sl]
    intra = s20.poc_forecast(3)[sl]
    return act, da, intra


def plan_battery(da):
    """Day-ahead battery plan: charge 4 MW in the four highest forecast
    hours, discharge 5 MW in the evening window (shifting, ch 19/20)."""
    req = np.zeros(24)
    top = np.argsort(da[8:17])[-4:] + 8
    req[top] = -4.0
    req[SERVICE[0]:SERVICE[1]] = 5.0
    return req


# [start: shift]
def run(act, req, cap_known_h, reserve=True):
    """Play the day hour by hour. cap_known_h: hour from which the
    controller is told the cap (the notice). Returns the hourly records."""
    lim = s20.LIMITS
    c = control.Controller(export_cap=lim["export_mw"], p_max=lim["bess_mw"],
                           e_min=lim["e_min"], e_max=lim["e_max"],
                           eta=lim["eta"], e=SOC0,
                           reserve_up=SERVICE[2] if reserve else 0.0)
    rows = []
    for h in range(24):
        cap = None
        if h >= cap_known_h:
            cap = CAP["mw"] if CAP["start"] <= h < CAP["end"] else 100.0
        r = c.step(h, float(act[h]), float(req[h]), cap, True)
        rows.append(r)
    return rows, c.alarms
# [end: shift]


def strategies():
    act, da, intra = day_series()
    plan = plan_battery(da)
    a_rows, a_al = run(act, plan, CAP["start"])           # follow the plan
    act_req = plan.copy()
    act_req[UPDATE_H:CAP["start"]] = 12.0                 # make room before the cap
    act_req[CAP["start"]:CAP["end"]] = 0.0                # controller recaptures the spill
    b_rows, b_al = run(act, act_req, CAP["notice"])
    sched_a = np.minimum(da, 100.0)
    sched_b = sched_a.copy()
    sched_b[CAP["start"]:] = np.minimum(intra[CAP["start"]:], 100.0)   # re-declared
    sched_b[CAP["start"]:CAP["end"]] = np.minimum(sched_b[CAP["start"]:CAP["end"]], CAP["mw"])
    return act, da, intra, plan, act_req, a_rows, a_al, b_rows, b_al, sched_a, sched_b


def timeline() -> dict:
    act, da, intra, plan, req, a, a_al, b, b_al, sa, sb = strategies()
    csv("ch51-shift.csv", "h,act,da,intra,cap,exp_a,exp_b,soc_a,soc_b",
        [(h, round(act[h], 1), round(da[h], 1), round(intra[h], 1),
          CAP["mw"] if CAP["start"] <= h < CAP["end"] else 100,
          round(a[h]["export"], 1), round(b[h]["export"], 1),
          round(a[h]["soc"], 1), round(b[h]["soc"], 1)) for h in range(24)])
    lines = [f"day {DAY} of the data-pack year, MW at the POC; cap {CAP['mw']:.0f} MW "
             f"{CAP['start']}:00-{CAP['end']}:00",
             "  hour  day-ahead  intraday  actual  export A  export B  SOC A  SOC B"]
    for h in range(6, 22):
        lines.append(f"  {h:4d}  {da[h]:9.0f}  {intra[h]:8.0f}  {act[h]:6.0f}  "
                     f"{a[h]['export']:8.1f}  {b[h]['export']:8.1f}  {a[h]['soc']:5.1f}  "
                     f"{b[h]['soc']:5.1f}")
    lines += ["  A follows the day-ahead plan; B acts on the 09:00 update and the",
              "  10:00 notice: discharges 09-11 to make room, then lets the",
              "  controller absorb only the spill above the cap"]
    emit("d_timeline", lines)
    return dict(act=act, a=a, b=b)


def compare() -> dict:
    act, da, intra, plan, req, a, a_al, b, b_al, sa, sb = strategies()
    out = {}
    for name, rows, al, sched in (("A follow the plan", a, a_al, sa),
                                  ("B act on update", b, b_al, sb)):
        exp = np.array([r["export"] for r in rows])
        curt = sum(r["curtailed"] for r in rows)
        imb = control.imbalance(sched, exp, s20.IMBALANCE["short"], s20.IMBALANCE["long"])
        soc18 = rows[SERVICE[0] - 1]["soc"]
        e_floor = s20.LIMITS["e_min"] + SERVICE[2] / s20.LIMITS["eta"]
        held = soc18 >= e_floor
        out[name] = dict(curt=curt, imb=imb, soc18=soc18, held=held, alarms=len(al),
                         energy=float(exp.sum()))
    lines = ["the two shifts compared (same weather, same plant, same limits)",
             "  strategy           exported  curtailed  imbalance  SOC 17:00  alarms",
             "                          MWh        MWh          u        MWh"]
    for k, v in out.items():
        lines.append(f"  {k:17s}  {v['energy']:8.0f}  {v['curt']:9.1f}  {v['imb']:9,.0f}  "
                     f"{v['soc18']:9.1f}  {v['alarms']:6d}")
    a_, b_ = out["A follow the plan"], out["B act on update"]
    lines += [f"  acting on the update saved {a_['curt'] - b_['curt']:.1f} MWh of curtailment "
              f"and {a_['imb'] - b_['imb']:,.0f} u",
              "  of imbalance, and the evening service energy was still held:",
              f"  {'yes' if b_['held'] else 'NO'}; the plan was not wrong when written - it was",
              "  overtaken by the update at 09:00 and the notice at 10:00"]
    emit("d_compare", lines)
    return out


LOG = [   # the shift log of strategy B: hour, event, decision, told, by
    dict(hour=6, event="handover: SOC 30 MWh (near 36), DA plan, no open permits",
         decision="accept plan; watch SOC", told="-", by="shift lead"),
    dict(hour=9, event="intraday forecast +20 MW at 11-14",
         decision="discharge 12 MW 09-11 to make room", told="trading desk", by="operator"),
    dict(hour=10, event="grid operator: export cap 80 MW 11:00-15:00",
         decision="acknowledge; set the cap; re-declare", told="trading desk",
         by="shift lead"),
    dict(hour=11, event="cap active; battery absorbing up to 20 MW",
         decision="hold", told="", by="operator"),
    dict(hour=15, event="cap lifted", decision="return to plan", told="grid operator",
         by="operator"),
    dict(hour=18, event="service window opens; SOC checked above the floor",
         decision="service available", told="grid operator", by="operator"),
]
REQUIRED = ["event", "decision", "told", "by"]


def shift_log() -> dict:
    chk = operations.check_log(LOG, REQUIRED, hours=range(6, 19))
    lines = ["shift log of strategy B (hour, event, decision, who was told, by whom)"]
    for e in LOG:
        lines.append(f"  {e['hour']:02d}:00 {e['event']}")
        lines.append(f"        -> {e['decision']}; told: {e['told'] or 'MISSING'}; by {e['by']}")
    lines += [f"  entries missing a field: {', '.join(f'{h}:00 {f}' for h, f in chk['missing'])}",
              "  the 11:00 entry does not say who was told the battery was",
              "  absorbing the spill: the controller did it, but the trading",
              "  desk's imbalance estimate needed it - a log is written for",
              "  the next reader, not for the writer"]
    emit("d_log", lines)
    return chk


def learning() -> list:
    act, da, intra, *_ = strategies()
    bias = float(np.mean(da[9:15] - act[9:15]))
    items = [(f"the day-ahead forecast was {-bias:.0f} MW low at 09-15: feed back",
              "to the forecast provider with the version and the weather (ch 37)"),
             (f"the battery began the day at {SOC0:.0f} of 36 MWh: the overnight plan",
              "leaves room when a sunny, windy day is forecast"),
             ("the restriction came with one hour's notice: ask the grid operator",
              "whether planned restrictions can be notified day-ahead (ch 28)"),
             ("the log missed one 'told' entry: add it to the shift-lead check", "")]
    lines = ["post-event learning, recorded the next morning"]
    for k, (a, b) in enumerate(items, 1):
        lines.append(f"  {k}. {a}")
        if b:
            lines.append(f"     {b}")
    emit("d_learning", lines)
    return items


if __name__ == "__main__":
    timeline()
    compare()
    shift_log()
    learning()
