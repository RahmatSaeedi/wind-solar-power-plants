"""Chapter 51, lesson B (normal and abnormal operation): energy lost in the
first operating year by cause, the battery's hours at its SOC limits, a
SCADA link lost for three hours, alarms per shift, and the restoration of
export after a blackout.

Run from the project root:   python -m companion.ch51.examples_b
Writes companion/ch51/expected/b_*.txt and diagrams/data/ch51-lost.csv.
"""
from __future__ import annotations

import numpy as np

from companion.ch20 import sources as s20
from companion.ch37 import sources as s37
from companion.ch51.common import csv, emit
from plantp import control, operations


def lost_by_cause() -> dict:
    y = s37.operating_year()
    avail = y["pv_exp"] + y["w_exp"]
    exported = y["pv_act"] + y["w_act"]
    cause = {}
    for h in range(8760):
        if y["limit"][h] < 100:
            cause[h] = "grid restriction"
        elif y["outage"][h]:
            cause[h] = "PV block outage"
        elif y["soil"][h] > 0:
            cause[h] = "soiling"
    lost = operations.lost_energy(avail, exported, cause)
    tot = sum(lost.values())
    named = {k: v for k, v in lost.items() if k != "unexplained"}
    csv("ch51-lost.csv", "k,cause,mwh", [(i + 1, k.replace(" ", "_"), round(v))
                                       for i, (k, v) in enumerate(sorted(lost.items(),
                                                                         key=lambda x: -x[1]))])
    lines = ["energy available but not exported in the first year, by recorded cause",
             "  cause                 MWh"]
    lines += [f"  {k:20s} {v:7,.0f}" for k, v in sorted(lost.items(), key=lambda x: -x[1])]
    lines += [f"  total {tot:,.0f} MWh; with a recorded cause {sum(named.values()):,.0f}",
              "  'unexplained' is mostly the ordinary scatter of an hour around",
              "  its expectation (both ways - only the shortfalls are summed",
              "  here); a cause is recorded when the operator knows one, and",
              "  the monthly review (ch 37) works on the named ones"]
    emit("b_lost", lines)
    return dict(lost=lost, total=tot)


def soc_limits(seed: int = 51) -> dict:
    act = s20.poc_actual()
    lim = s20.LIMITS
    c = control.Controller(export_cap=lim["export_mw"], p_max=lim["bess_mw"],
                           e_min=lim["e_min"], e_max=lim["e_max"], eta=lim["eta"],
                           reserve_up=5.0, e=20.0)
    at_max = at_floor = 0
    floor = lim["e_min"] + 5.0 / lim["eta"]
    for h in range(8760):
        hod = h % 24
        req = -6.0 if 10 <= hod < 15 else (6.0 if 18 <= hod < 22 else 0.0)
        r = c.step(h, float(act[h]), req, None, True)
        at_max += r["soc"] >= lim["e_max"] - 0.1
        at_floor += r["soc"] <= floor + 0.1
    lines = ["the battery over the year with a fixed daily shift (6 MW in at",
             "  10-15, out at 18-22), reserve 5 MW for an hour kept (ch 20)",
             f"  hours at the upper limit (36 MWh): {at_max}",
             f"  hours at the service floor ({floor:.1f} MWh): {at_floor}",
             f"  controller alarms: {len(c.alarms)}",
             "  a battery near its limits is the normal state of a plan that",
             "  does not look at the forecast: the shift of lesson D adjusts",
             "  the plan when the day is not ordinary"]
    emit("b_soc", lines)
    return dict(at_max=at_max, at_floor=at_floor, alarms=len(c.alarms))


def comms_loss(lost_h: int = 3, start: int = 14) -> dict:
    act = s20.poc_actual()[34 * 24:35 * 24]
    lim = s20.LIMITS
    c = control.Controller(e=20.0, reserve_up=5.0)
    rows = []
    for h in range(24):
        ok = not (start <= h < start + lost_h)
        req = 6.0 if 18 <= h < 22 else 0.0
        rows.append(c.step(h, float(act[h]), req, None, ok))
    fall = [a for a in c.alarms if "comms" in a[1]]
    lines = [f"SCADA link to the controller lost for {lost_h} h from {start}:00 (day 34)",
             f"  timeout {lim['comms_timeout_h']} h, then the battery goes to its fallback (idle)",
             f"  hours on fallback: {len(fall)} ({', '.join(f'{h}:00' for h, _ in fall)})",
             "  the export cap in force is held; no new instruction reaches",
             "  the plant: the operator rings the grid operator, logs the",
             "  time, and the OT team (ch 36) owns the link - the service",
             "  is suspended while the controller cannot be reached (lesson J)"]
    emit("b_comms", lines)
    return dict(fallback=len(fall))


def alarms(seed: int = 52, target: float = 6.0) -> dict:
    rng = np.random.default_rng(seed)
    per_h = rng.poisson(3.0, 24 * 30).astype(float)
    flood_days = [3, 17]
    for d in flood_days:
        per_h[d * 24 + 13: d * 24 + 16] += rng.poisson(40, 3)
    over = int((per_h > target).sum())
    top = int(per_h.max())
    lines = [f"alarms per hour in the control room over a month (teaching target "
             f"{target:.0f})",
             f"  mean {per_h.mean():.1f}, hours over the target {over}, worst hour {top}",
             f"  the floods were two afternoons ({', '.join(f'day {d + 1}' for d in flood_days)}):"
             " a feeder trip",
             "  raised the alarms of every converter on it at once - the",
             "  alarm philosophy of ch 35 groups them under the feeder; the",
             "  operator handles the cause, not the list"]
    emit("b_alarms", lines)
    return dict(over=over, top=top)


def restoration() -> dict:
    steps = [("grid back at the POC", 0), ("auxiliaries restarted (ch 50 restart)", 23),
             ("33 kV bus energised, protection checked", 15),
             ("wind feeders WS1-3 one by one", 20), ("PV feeders PVF1-3", 15),
             ("battery feeder and controller back", 10),
             ("export released in steps to the cap", 30)]
    acc, rows = 0, []
    for s, m in steps:
        acc += m
        rows.append((s, acc))
    lines = ["restoration of export after a blackout (minutes from grid back)"]
    lines += [f"  {s:42s} {t:4d}" for s, t in rows]
    lines += [f"  {acc} minutes to full export; each step under its own",
              "  authority (ch 50 energisation order) and the grid operator's",
              "  instruction for the export steps - the procedure OP-05 is",
              "  the one past its review (lesson C)"]
    emit("b_restore", lines)
    return dict(total=acc)


if __name__ == "__main__":
    lost_by_cause()
    soc_limits()
    comms_loss()
    alarms()
    restoration()
