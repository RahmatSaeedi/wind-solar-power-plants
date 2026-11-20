"""Chapter 19, lab D - dispatch and verification: a year of the S1
battery with its state of charge (charging from curtailment and from
midday output, discharging in the evening within the export limit),
the SOC distribution, rainflow cycles and the fade they cause, a
20-year projection against the data pack's linear 2 %/yr, the warranty
check, and edge-case tests of the controller.

Run from the project root:   python -m companion.ch19.lab_d
Writes companion/ch19/expected/d_*.txt and diagrams/data/ch19-*.csv.
Data pack S1, model 15.1, teaching fade and warranty (A-292, A-293).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch15 import sources as s15
from companion.ch19 import sources as src
from companion.ch19.common import csv, emit
from plantp import storage as st
from plantp.wind import rainflow

S1, F = src.S1, src.FADE
E_NOM = S1["energy_mwh"]
LO, HI = S1["soc_lo"] * E_NOM, S1["soc_hi"] * E_NOM
ETA = math.sqrt(S1["rt_ac"])


# [start: dispatch]
def dispatch(net, poc, outage, p_max=20.0, limit=100.0, soc0=None):
    """Hourly rule: store curtailed power at any hour; from 10:00 to
    15:00 also charge from the plant's output; from 18:00 to 22:00
    discharge within the export limit. No grid charging. Returns SOC
    (MWh, end of hour), charge and discharge (MW, AC)."""
    n = len(net)
    hour = np.arange(n) % 24
    soc = np.zeros(n)
    ch, dis = np.zeros(n), np.zeros(n)
    e = LO if soc0 is None else soc0
    for k in range(n):
        if not outage[k]:
            cut = max(poc[k] - limit, 0.0)
            c = min(cut, p_max, (HI - e) / ETA)
            if 10 <= hour[k] < 15:
                c += min(max(net[k], 0.0), p_max - c, (HI - e) / ETA - c)
            d = 0.0
            if 18 <= hour[k] < 22 and c == 0.0:
                d = min(p_max, (e - LO) * ETA, max(limit - net[k], 0.0))
            e += c * ETA - d / ETA
            ch[k], dis[k] = c, d
        soc[k] = e
    return soc, ch, dis
# [end: dispatch]


def turning(x):
    """Drop repeated values so that rainflow sees the turning points of
    a series with flat stretches (a full or empty battery)."""
    x = np.asarray(x, float)
    return x[np.r_[True, np.abs(np.diff(x)) > 1e-9]]


def year() -> dict:
    r = s15.plant_year()
    soc, ch, dis = dispatch(r["net"], r["poc"], r["outage"])
    return {"soc": soc, "ch": ch, "dis": dis, "r": r}


def results() -> None:
    y = year()
    soc, ch, dis = y["soc"], y["ch"], y["dis"]
    thr = dis.sum()
    efc = thr / ETA / (HI - LO)                   # usable cycles, DC side
    cyc = rainflow(turning(soc / E_NOM))
    deep = sum(c for d, c in cyc if d >= 0.5)
    lines = ["a year of the S1 battery (rule of chapter 15, data pack S1):",
             f"  charged {ch.sum():,.0f} MWh, discharged {thr:,.0f} MWh AC"
             f" ({100 * thr / ch.sum():.0f} %)",
             f"  equivalent full cycles of the usable window: {efc:.0f}",
             f"  rainflow cycles: {sum(c for _, c in cyc):.0f}, of which {deep:.0f}"
             " deeper than 50 %",
             f"  mean SOC {100 * soc.mean() / E_NOM:.0f} %; hours at the bottom"
             f" {int((soc <= LO + 1e-6).sum()):,}, at the top {int((soc >= HI - 1e-6).sum()):,}",
             "  SOC band      hours"]
    hist, edges = np.histogram(100 * soc / E_NOM, bins=[10, 20, 30, 40, 50, 60, 70, 80, 90.01])
    for k, h in enumerate(hist):
        lines.append(f"  {edges[k]:3.0f}-{min(edges[k + 1], 90):3.0f} %   {h:6,d}")
    emit("d_year", lines)
    csv("ch19-soc.csv", "band,hours", [(int(edges[k]) + 5, h) for k, h in enumerate(hist)])


def fade_projection() -> None:
    y = year()
    soc = y["soc"] / E_NOM
    cyc = rainflow(turning(soc))
    cyc_year = st.cycle_fade(cyc, F["n100"], F["k"], F["loss_at_life"])
    lines = ["fade of the S1 battery under this duty (A-292, cells at 25 C):",
             f"  cycling: {100 * cyc_year:.2f} % a year; calendar at mean SOC"
             f" {100 * soc.mean():.0f} %: k sqrt(t)",
             "  year   calendar   cycling   total   health   data pack"]
    rows = []
    eol = None
    for yr in range(0, 21):
        cal = float(st.calendar_fade(yr, 25.0, soc.mean(), F["k25"], F["ea_ev"]))
        tot = cal + cyc_year * yr
        if eol is None and 1 - tot < 0.80:
            eol = yr
        rows.append((yr, f"{100 * (1 - tot):.2f}", f"{100 * (1 - 0.02 * yr):.2f}"))
        if yr in (1, 5, 10, 15, 20):
            lines.append(f"  {yr:4d}   {100 * cal:7.1f} %  {100 * cyc_year * yr:6.1f} %"
                         f"  {100 * tot:5.1f} %  {100 * (1 - tot):5.1f} %   {100 * (1 - 0.02 * yr):5.1f} %")
    when = f"in year {eol}" if eol is not None else "after year 20"
    lines += [f"  health falls below 80 % {when} with this model; the data",
              "  pack's linear 2 %/yr is close to it; the warranty curve,",
              "  measured capacity tests and the actual duty replace both",
              "  (chapter 51)"]
    emit("d_fade", lines)
    csv("ch19-health.csv", "y,model,pack", rows)


def warranty() -> None:
    y = year()
    thr_dc = y["dis"].sum() / ETA
    efc = thr_dc / (HI - LO)
    rows = st.warranty_check(thr_dc, efc, y["soc"].mean() / E_NOM, 32.6, src.WARRANTY)
    lines = ["warranty check of the year (teaching limits A-293):",
             "  item                          value      limit    ok"]
    for name, v, lim, ok in rows:
        lines.append(f"  {name:28s} {v:9,.2f}  {lim:9,.2f}   {'yes' if ok else 'NO'}")
    lines += ["  temperature from the container model at end of life with a",
              "  100 kW HVAC (b_heat); a warranty is a contract: its limits",
              "  become controller settings and monthly reports"]
    emit("d_warranty", lines)


def edge_cases() -> None:
    """Invariants of the controller on the year and on made-up hours."""
    y = year()
    r = y["r"]
    soc, ch, dis = y["soc"], y["ch"], y["dis"]
    tests = [
        ("SOC stays inside 10-90 %", bool((soc >= LO - 1e-9).all() and (soc <= HI + 1e-9).all())),
        ("never charges and discharges in one hour", bool(((ch > 0) & (dis > 0)).sum() == 0)),
        ("no grid charging (charge <= plant output)", bool((ch <= np.clip(r["poc"], 0, None) + 1e-9).all())),
        ("export with the battery <= 100 MW", bool((r["net"] - ch + dis <= 100.0 + 1e-9).all())),
        ("idle in grid-outage hours", bool(((ch + dis)[r["outage"]] == 0).all())),
    ]
    e0 = LO + 0.0
    s2, c2, d2 = dispatch(np.array([50.0] * 24), np.array([50.0] * 24),
                          np.zeros(24, bool), soc0=e0)
    tests.append(("empty at 18:00 after a day of charging? no: charged",
                  bool(s2[17] > LO)))
    s3, c3, d3 = dispatch(np.zeros(24), np.zeros(24), np.zeros(24, bool), soc0=LO)
    tests.append(("empty battery, no plant output: no discharge", bool(d3.sum() == 0)))
    s4, c4, d4 = dispatch(np.full(24, 99.0), np.full(24, 99.0), np.zeros(24, bool), soc0=HI)
    tests.append(("full battery, plant at 99 MW: discharge <= 1 MW",
                  bool(d4.max() <= 1.0 + 1e-9)))
    bal = ch.sum() * ETA - dis.sum() / ETA - (soc[-1] - LO)
    tests.append(("energy balance closes (MWh)", abs(bal) < 1e-6))
    lines = ["edge-case tests of the controller:"]
    lines += [f"  {'PASS' if ok else 'FAIL'}  {name}" for name, ok in tests]
    lines += ["  each test is a requirement written as code; the same tests",
              "  run again on the real controller's logs in commissioning"]
    emit("d_tests", lines)


if __name__ == "__main__":
    results()
    fade_projection()
    warranty()
    edge_cases()
