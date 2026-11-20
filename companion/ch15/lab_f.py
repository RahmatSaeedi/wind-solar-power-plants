"""Chapter 15, section F - soiling and cleaning lab: the chapter 10 station
year and cleaning policies run inside the energy model, so each day's loss
is weighted by that day's PV energy; recovered energy against the
no-cleaning baseline, water, cost, cleaning quality, and the uncertainty
of the soiling rate (does the best policy change?).

Run from the project root:   python -m companion.ch15.lab_f
Writes companion/ch15/expected/f_*.txt and diagrams/data/ch15-*.csv.
Chapter 10 teaching values A-195 .. A-197, D-014; price 50 u/MWh.
"""
from __future__ import annotations

import numpy as np

from companion.ch10 import lab_d as l10
from companion.ch15 import sources as src
from companion.ch15.common import csv, emit

POLICIES = [("no cleaning", None, 0), ("truck every 30 d", "truck wet", 30),
            ("truck every 14 d", "truck wet", 14), ("manual dry every 10 d", "manual dry", 10),
            ("robot every 12 d", "robot dry", 12), ("truck at 4 % loss", "truck wet", -0.04)]


# [start: policy]
def simulate(meth, every, rate, rain, heavy, removal=None):
    """Daily soiling loss and the number of cleanings of one policy:
    accumulation `rate` a day, heavy rain cleans, light rain halves, a
    cleaning removes `removal` of the dirt (fixed interval `every` days, or
    a trigger on the loss when `every` is negative)."""
    x, n, out = 0.0, 0, np.zeros(len(rate))
    rem = None if meth is None else (removal or l10.METHODS[meth]["removal"])
    for k in range(len(rate)):
        x += rate[k]
        if heavy[k]:
            x = 0.0
        elif rain[k]:
            x *= 0.5
        due = (every < 0 and x > -every) or (every > 0 and k % every == every - 1)
        if meth and due:
            x *= 1 - rem
            n += 1
        out[k] = x
    return out, n
# [end: policy]


def daily_pv():
    r = src.plant_year()
    return r["pv_clip"].reshape(365, 24).sum(axis=1)              # MWh a day


def run(scale: float = 1.0, removal=None):
    _, _, _, rain, heavy, rate = l10.station_year()
    e = daily_pv()
    out = []
    for name, meth, every in POLICIES:
        loss, n = simulate(meth, every, rate * scale, rain, heavy,
                           removal if meth == "truck wet" else None)
        lost = float((loss * e).sum())
        cost = n * (l10.METHODS[meth]["cost"] * l10.N_MODULES if meth else 0)
        water = n * (l10.METHODS[meth]["water"] * l10.N_MODULES / 1e3 if meth else 0)
        out.append((name, lost, n, cost, water, float(loss.mean())))
    return out


def policies() -> None:
    res = run()
    base = res[0][1]
    lines = ["cleaning policies inside the energy model (daily loss x that day's",
             "  PV energy; price 50 u/MWh; chapter 10 station year and costs):",
             "  policy                 loss %  recovered MWh  cost k u  net k u  water m3"]
    rows = []
    e_tot = daily_pv().sum()
    for name, lost, n, cost, water, mean in res:
        rec = base - lost
        net = rec * 50 - cost
        lines.append(f"  {name:21s}  {100 * lost / e_tot:5.2f}   {rec:9,.0f}     {cost / 1e3:6.0f}"
                     f"   {net / 1e3:6.0f}   {water:6,.0f}")
        rows.append((name.split()[0] + " " + name.split()[-1], f"{100 * lost / e_tot:.2f}", f"{net / 1e3:.0f}"))
    csv("ch15-cleaning.csv", "policy,loss,net", rows)
    lines += ["  net = recovered energy x price - cleaning cost, against no",
              "  cleaning (no cleaning loses "
              f"{100 * base / e_tot:.1f} % of the PV energy); a 14-day truck",
              "  recovers more than a 30-day one but its extra cleanings cost",
              "  more than they recover; the trigger and the robot clean when it",
              "  pays; the robot's figure leaves out its capital and upkeep",
              "  (chapter 10 break-even), so D-014 keeps the truck trigger"]
    emit("f_policies", lines)


def weighting() -> None:
    _, _, _, rain, heavy, rate = l10.station_year()
    e = daily_pv()
    loss, _ = simulate("truck wet", -0.04, rate, rain, heavy)
    lines = ["the same trigger policy, plain average against energy-weighted:",
             f"  mean daily loss {100 * loss.mean():.2f} % (chapter 10's figure);"
             f" energy-weighted {100 * (loss * e).sum() / e.sum():.2f} %",
             "  the dry season is both dusty and sunny: weighting by energy",
             "  raises the loss; an hourly model takes the weighted value"]
    emit("f_weighting", lines)


def uncertainty() -> None:
    lines = ["the soiling rate is uncertain (x 0.5, x 1, x 1.5) and the truck",
             "  may clean worse (removal 0.80 instead of 0.95): net u a year",
             "  policy                 rate x0.5   x1.0     x1.5    x1.0, truck 0.80"]
    table = {}
    for sc in (0.5, 1.0, 1.5):
        for name, lost, n, cost, water, mean in run(sc):
            table.setdefault(name, []).append((lost, cost))
    poor = {name: (lost, cost) for name, lost, n, cost, water, mean in run(1.0, 0.80)}
    best = {}
    for k, sc in enumerate((0.5, 1.0, 1.5)):
        base = table["no cleaning"][k][0]
        best[sc] = max(table, key=lambda nm: (base - table[nm][k][0]) * 50 - table[nm][k][1])
    for name in table:
        vals = []
        for k in range(3):
            base = table["no cleaning"][k][0]
            lost, cost = table[name][k]
            vals.append((base - lost) * 50 - cost)
        b1 = table["no cleaning"][1][0]
        vp = (b1 - poor[name][0]) * 50 - poor[name][1]
        lines.append(f"  {name:21s} {vals[0]:9,.0f} {vals[1]:9,.0f} {vals[2]:9,.0f}   {vp:9,.0f}")
    same = len(set(best.values())) == 1
    lines += [f"  best at every rate: {best[1.0]} (before its capital)" if same else
              f"  best: x0.5 {best[0.5]}; x1.0 {best[1.0]}; x1.5 {best[1.5]}",
              "  the top two (robot, trigger) hold over the range: robust; with half",
              "  the rate no fixed calendar pays at all, which is why the",
              "  station data (and the trigger) come before the contract"]
    emit("f_uncertainty", lines)


if __name__ == "__main__":
    policies()
    weighting()
    uncertainty()
