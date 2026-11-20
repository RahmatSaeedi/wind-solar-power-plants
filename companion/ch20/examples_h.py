"""Chapter 20, operation lessons: where the controller's alarms come from
(by type and by hour), the energy the plan leaves in the battery at
midnight, and how long the island could carry the critical loads from
any hour of the year (with and without an island reserve).

Run from the project root:   python -m companion.ch20.examples_h
Writes companion/ch20/expected/h_*.txt and diagrams/data/ch20-*.csv.
Teaching values A-299 to A-303.
"""
from __future__ import annotations

from collections import Counter

import numpy as np

from companion.ch15 import sources as s15
from companion.ch20 import examples_b as eb, lab_e, sources as src
from companion.ch20.common import csv, emit
from plantp import control as ct

L = src.LIMITS


def alarms() -> None:
    lines = ["controller alarms by type in a year (REQ-S01, no calls):",
             "  type                       controller only   plan knows service"]
    res = {m: lab_e.run_year(m)["alarm_list"] for m in ("controller", "plan")}
    kinds = sorted({msg.split(" (")[0].split(" +")[0] if not msg.startswith("request")
                    else "request beyond rating"
                    for m in res for _, msg in res[m]})
    for k in kinds:
        n = {m: sum(1 for _, msg in res[m] if msg.startswith(k.split(" beyond")[0]))
             for m in res}
        lines.append(f"  {k:26s} {n['controller']:15d}   {n['plan']:18d}")
    hours = {m: Counter(t % 24 for t, _ in res[m]) for m in res}
    peak = max(range(24), key=lambda h: hours["controller"][h])
    lines += [f"  busiest hour (controller only): {peak:02d}:00 with "
              f"{hours['controller'][peak]} alarms",
              "  two thirds of the first case are 'discharge limited' in the",
              "  window hours (the plan asks for energy the reserve keeps); the",
              "  rest are 'charge limited' around midday, when recapture has",
              "  already filled the battery; the alarm count measures how far",
              "  the plan and the controller disagree"]
    emit("h_alarms", lines)
    csv("ch20-alarms.csv", "h,ctrl,plan",
        [(h, hours["controller"][h], hours["plan"][h]) for h in range(24)])


# [start: year_soc]
def year_soc(e_end: float):
    """A year of day-ahead plans that end each day at e_end; returns
    export value and the stored energy at the start of every hour."""
    act = np.clip(src.poc_actual(), 0, None)
    fc = np.clip(src.poc_forecast(24), 0, None)
    cap, price = eb.caps(), src.prices()
    c = ct.Controller(e=L["e_min"])
    soc = np.zeros(8760)
    val = 0.0
    for d in range(365):
        h = slice(d * 24, d * 24 + 24)
        _, _, plan = ct.dp_schedule(price[h], np.minimum(fc[h], L["bess_mw"]),
                                    np.clip(cap[h] - fc[h], 0, None),
                                    L["bess_mw"], L["e_min"], L["e_max"],
                                    round(c.e), L["eta"], wear=10.0,
                                    e_end=e_end)
        for k in range(24):
            t = d * 24 + k
            soc[t] = c.e
            r = c.step(t, act[t], plan[k], cap[t], True)
            val += r["export"] * price[t]
    return val, soc
# [end: year_soc]


def end_target() -> None:
    lines = ["energy the plan leaves at midnight (terminal value):",
             "  e_end MWh   export value k u   vs e_end 4   mean SOC at 18 h MWh"]
    base = None
    for e_end in (4.0, 10.0, 20.0):
        val, soc = year_soc(e_end)
        base = val if base is None else base
        lines.append(f"  {e_end:9.0f}   {val / 1000:16,.1f}   {(val - base) / 1000:+10.1f}"
                     f"   {soc[18::24].mean():21.1f}")
    lines += ["  energy kept overnight is energy not sold in the evening; with",
              "  prices known a day ahead and a plant that refills the battery",
              "  most days, ending low is best; a higher end target buys",
              "  readiness (island reserve, morning services) at a known cost"]
    emit("h_endtarget", lines)


def autonomy(soc, floor: float, load: float = 1.57, horizon: int = 24):
    """Hours the island carries a critical load from each start hour:
    battery from soc down to e_min, PV of the plant on top (A-303)."""
    pv = np.clip(s15.plant_year()["pv_av"], 0, None)
    eta = L["eta"]
    hours = np.zeros(8760, int)
    for t0 in range(0, 8760 - horizon):
        e = max(soc[t0], floor)
        n = 0
        for t in range(t0, t0 + horizon):
            net = load - pv[t]
            e = min(L["e_max"], e - net / eta) if net > 0 else min(L["e_max"], e - net * eta)
            if e < L["e_min"]:
                break
            n += 1
        hours[t0] = n
    return hours[: 8760 - horizon]


def island() -> None:
    _, soc = year_soc(4.0)
    lines = ["hours the island carries 1.57 MW of critical load (priority",
             "1 + 2) from each hour of the year, battery + PV (A-303):",
             "  island floor MWh   P10 h   P50 h   share of starts >= 24 h"]
    rows = []
    for floor in (0.0, 10.0, 20.0):
        h = autonomy(soc, floor)
        lines.append(f"  {floor:16.0f}   {np.percentile(h, 10):5.0f}   {np.percentile(h, 50):5.0f}"
                     f"   {(h >= 24).mean() * 100:22.0f} %")
        rows.append((int(floor), f"{np.percentile(h, 10):.0f}", f"{(h >= 24).mean() * 100:.0f}"))
    lines += ["  without a floor the island fails at once from an empty",
              "  night-time battery in a tenth of the hours; a 20 MWh floor",
              "  gives a day of autonomy from 93 % of starts, at a cost of",
              "  the order of the 88 k u a year of h_endtarget; whether that",
              "  is worth it is the owner's decision (U-080)"]
    emit("h_island", lines)
    csv("ch20-island.csv", "floor,p10,share", rows)


if __name__ == "__main__":
    alarms()
    end_target()
    island()
