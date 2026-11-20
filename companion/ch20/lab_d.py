"""Chapter 20, lab D - the chapter's worked example: an hourly dispatch
table for one day with changing renewables, an operator export cap and
the battery's SOC; then edge-case tests of the controller.

The day: the sunniest day with an 80 MW operator cap from 11:00 to
15:00 (examples_b caps). The battery plan comes from the day-ahead
forecast by dynamic programming (charge only from the plant, discharge
within the export room); the controller executes it with the actual
output and the cap it receives.

Run from the project root:   python -m companion.ch20.lab_d
Writes companion/ch20/expected/d_*.txt and diagrams/data/ch20-day.csv.
"""
from __future__ import annotations

import numpy as np

from companion.ch20 import examples_b as eb, sources as src
from companion.ch20.common import csv, emit
from plantp import control as ct

L = src.LIMITS


def the_day() -> int:
    cap = eb.caps().reshape(365, 24)
    pv = src.poc_actual().reshape(365, 24)
    capped = np.where((cap < 100).any(axis=1))[0]
    return int(capped[np.argmax(pv[capped, 11:15].sum(axis=1))])


# [start: plan]
def plan(day: int):
    """Day-ahead battery plan from the forecast and the known caps."""
    h = slice(day * 24, day * 24 + 24)
    fc = np.clip(src.poc_forecast(24)[h], 0, None)
    cap = eb.caps()[h]
    price = src.prices()[h]
    rev, e, p = ct.dp_schedule(price, np.minimum(fc, L["bess_mw"]),
                               np.clip(cap - fc, 0, None), L["bess_mw"],
                               L["e_min"], L["e_max"], L["e_min"], L["eta"],
                               step=1.0, wear=10.0)
    return fc, cap, price, p
# [end: plan]


def worked() -> None:
    d = the_day()
    fc, cap, price, plan_p = plan(d)
    act = np.clip(src.poc_actual()[d * 24:d * 24 + 24], 0, None)
    c = ct.Controller(export_cap=L["export_mw"], e=L["e_min"])
    lines = [f"hourly dispatch of day {d + 1} (sunniest day with an 80 MW cap, A-302):",
             "   h  fcst   act  cap  price  plan   chg   dis  export  curt   SOC"]
    rows = []
    tot = {"export": 0.0, "curt": 0.0, "value": 0.0}
    for k in range(24):
        r = c.step(k, act[k], plan_p[k], cap[k], True)
        tot["export"] += r["export"]
        tot["curt"] += r["curtailed"]
        tot["value"] += r["export"] * price[k]
        lines.append(f"  {k:2d} {fc[k]:5.1f} {act[k]:5.1f} {cap[k]:4.0f} {price[k]:6.1f}"
                     f" {plan_p[k]:+5.1f} {r['charge']:5.1f} {r['discharge']:5.1f}"
                     f" {r['export']:7.1f} {r['curtailed']:5.1f} {r['soc']:5.1f}")
        rows.append((k, f"{act[k]:.2f}", f"{r['export']:.2f}", f"{cap[k]:.0f}", f"{r['soc']:.2f}"))
    lines += [f"  day: export {tot['export']:.0f} MWh, curtailed {tot['curt']:.1f} MWh,"
              f" value {tot['value'] / 1000:.1f} k u",
              f"  controller alarms: {len(c.alarms)}"]
    lines += [f"    h{h:02d} {msg}" for h, msg in c.alarms[:4]]
    emit("d_worked", lines)
    csv("ch20-day.csv", "h,act,export,cap,soc", rows)


def tests() -> None:
    res = []
    c = ct.Controller(e=4.0)
    r = c.step(0, 60.0, -35.0, None, True)
    res.append(("infeasible request (-35 MW) clamped to 20 MW, alarm",
                r["charge"] == 20.0 and any("beyond" in a for _, a in c.alarms)))
    c = ct.Controller(e=4.0)
    r = c.step(0, 30.0, 15.0, None, True)
    res.append(("empty battery: no discharge, alarm",
                r["discharge"] == 0.0 and len(c.alarms) == 1))
    c = ct.Controller(e=36.0)
    r = c.step(0, 50.0, -10.0, None, True)
    res.append(("full battery: no charge", r["charge"] == 0.0))
    c = ct.Controller(e=20.0)
    r = c.step(0, 95.0, 20.0, 80.0, True)
    res.append(("operator cap 80 MW overrides the plan: export <= 80", r["export"] <= 80.0 + 1e-9))
    c = ct.Controller(e=30.0)
    r0 = c.step(0, 50.0, 10.0, None, False)
    r1 = c.step(1, 50.0, 10.0, None, False)
    r2 = c.step(2, 50.0, 10.0, None, True)
    res.append(("comms lost: plan kept 1 h, then battery idle; back on return",
                r0["discharge"] == 10.0 and r1["discharge"] == 0.0
                and r2["discharge"] == 10.0))
    c = ct.Controller(e=12.0, reserve_up=5.0)
    r = c.step(0, 40.0, 20.0, None, True)
    floor = 4.0 + 5.0 / c.eta
    res.append(("reserve keeps energy for 5 MW x 1 h: discharge stops at floor",
                abs(c.e - floor) < 1e-9 and r["discharge"] < 3.0))
    c = ct.Controller(e=30.0, reserve_up=5.0)
    r = c.step(0, 40.0, 20.0, None, True)
    res.append(("reserve keeps 5 MW of converter room: discharge <= 15 MW",
                r["discharge"] <= 15.0 + 1e-9))
    c = ct.Controller(e=10.0, export_cap=100.0)
    r = c.step(0, 110.0, 0.0, None, True)
    res.append(("curtailment recaptured when the plan is idle", r["charge"] > 0.0))
    lines = ["edge-case tests of the hourly controller:"]
    lines += [f"  {'PASS' if ok else 'FAIL'}  {name}" for name, ok in res]
    lines += ["  each test is a requirement written as code (section C); the",
              "  same cases run in the factory and site tests of the real",
              "  controller (chapters 44, 48 and 50)"]
    emit("d_tests", lines)


if __name__ == "__main__":
    worked()
    tests()
