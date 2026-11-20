"""Chapter 37, lesson A (metrics and baselines): the indicators of the
operating year, time-based against production-based availability,
exclusions, reporting windows, PR corrected for temperature, the loss
waterfall and capacity factors.

Run from the project root:   python -m companion.ch37.examples_a
Writes companion/ch37/expected/a_*.txt and diagrams/data/ch37-*.csv.
Synthetic operating year (A-409, A-410); model 15.1 as the baseline.
"""
from __future__ import annotations

import numpy as np

from companion.ch37 import sources as src
from companion.ch37.common import csv, emit
from plantp import performance as pf


def indicators() -> None:
    y = src.operating_year()
    e_pv, e_w = y["pv_act"].sum(), y["w_act"].sum()
    h = y["poa_true"].sum() / 1000
    pr = pf.performance_ratio(e_pv * 1000, src.P_DC_KWP, h)
    lines = ["the indicators of the synthetic operating year",
             f"  PV energy {e_pv:,.0f} MWh; specific yield {e_pv * 1000 / src.P_DC_KWP:,.0f} kWh/kWp",
             f"  PV performance ratio (reference sensor) {pr:.3f}",
             f"  PV capacity factor on 50 MW AC {e_pv / (50 * 8760) * 100:.1f} %",
             f"  wind energy {e_w:,.0f} MWh; capacity factor on 60 MW {e_w / (60 * 8760) * 100:.1f} %",
             f"  plant energy at MV {e_pv + e_w:,.0f} MWh; curtailed {y['curtailed'].sum():,.0f} MWh",
             "  each indicator answers a different question: yield and PR",
             "  how well the PV turns sunlight into energy, capacity",
             "  factor how much of its rating the plant uses, curtailed",
             "  energy what the grid did not take"]
    emit("a_indicators", lines)


def time_vs_energy(seed: int = 372) -> None:
    y = src.operating_year()
    w = y["w_exp"] / 12                                # one turbine, MW
    mar = np.where(y["month"] == 2)[0]
    roll = np.convolve(w[mar], np.ones(48), "valid")
    calm, windy = int(np.argmin(roll)), int(np.argmax(roll))
    month_e = w[mar].sum()
    lines = ["one turbine down for 48 h in March: calm hours or windy hours",
             f"  March: {len(mar)} h, turbine energy {month_e:,.1f} MWh",
             "  outage in        time availability   production availability"]
    rows = []
    for name, start in (("calmest 48 h", calm), ("windiest 48 h", windy)):
        lost = w[mar][start:start + 48].sum()
        ta = pf.time_availability(len(mar) - 48, len(mar))
        ea = pf.energy_availability(month_e - lost, lost)
        rows.append((name, ta, ea))
        lines.append(f"  {name:15s} {ta * 100:17.2f} %   {ea * 100:21.2f} %")
    lines += ["  the same 48 hours cost almost nothing in a calm spell and a",
              "  lot in a windy one: time-based availability cannot tell",
              "  them apart, production-based availability can - which is",
              "  why contracts and reports name the one they use",
              "  (STD-165 describes both as information categories)"]
    emit("a_time_energy", lines)


def exclusions() -> None:
    period = 8760.0
    down = {"turbine faults": 120.0, "scheduled service": 60.0,
            "grid outage (operator's)": 12.0, "curtailment orders": 40.0}
    up = period - sum(down.values())
    excl = down["grid outage (operator's)"] + down["curtailment orders"]
    lines = ["time-based availability of one turbine with and without exclusions",
             "  hours lost: turbine faults 120, scheduled service 60,",
             "    grid outage (operator's) 12, curtailment orders 40",
             f"  nothing excluded: {pf.time_availability(up, period) * 100:.2f} %",
             f"  grid outages and curtailment excluded: "
             f"{pf.time_availability(up, period, excl) * 100:.2f} %",
             f"  scheduled service also excluded: "
             f"{pf.time_availability(up, period, excl + down['scheduled service']) * 100:.2f} %",
             "  three numbers for one turbine and one year: an availability",
             "  figure means nothing without its list of exclusions, and",
             "  that list is the contract's, not the analyst's"]
    emit("a_exclusions", lines)


def windows() -> None:
    hours = np.ones(8760)
    hours[24 * 200:24 * 200 + 50] = 0                  # one 50-hour outage in July
    month = src.operating_year()["month"]
    jul = month == 6
    a_jul = hours[jul].mean()
    a_year = hours.mean()
    lines = ["the same outage in two reporting windows",
             "  one turbine, a single 50-hour outage in July",
             f"  July availability: {a_jul * 100:.1f} %",
             f"  year availability: {a_year * 100:.2f} %",
             "  a month with one long outage looks bad, the year looks",
             "  fine; a report states its window, and comparisons use the",
             "  same window - a rolling 12 months for trends, the month",
             "  for follow-up"]
    emit("a_windows", lines)


def pr_temperature() -> None:
    y = src.operating_year()
    g = y["poa_true"]
    t_cell = y["t_air"] + 0.03 * g                      # simple estimate (teaching)
    lines = ["monthly PR and PR corrected to 25 C (reference sensor, teaching)",
             "  month   PR      cell C (weighted)   PR at 25 C"]
    rows = []
    for m in range(12):
        sel = y["month"] == m
        h = g[sel].sum() / 1000
        pr = pf.performance_ratio(y["pv_act"][sel].sum() * 1000, src.P_DC_KWP, h)
        tc = np.sum(t_cell[sel] * g[sel]) / np.sum(g[sel])
        prc = pf.pr_temperature(pr, tc)
        rows.append((m + 1, round(pr, 4), round(prc, 4)))
        lines.append(f"  {src.MONTHS[m]:5s}   {pr:5.3f}   {tc:17.1f}   {prc:10.3f}")
    csv("ch37-pr.csv", "m,pr,prc", rows)
    lines += ["  summer PR is lower partly because hot cells make less;",
              "  corrected to 25 C the months move closer together, and",
              "  what still sticks out - April's soiling, June's outage -",
              "  is what the plant did, not what the weather did"]
    emit("a_pr", lines)


def waterfall() -> None:
    y = src.operating_year()
    pv_model = y["pv_exp"].sum() + y["w_exp"].sum()
    soil = np.sum(y["pv_exp"] * y["soil"])
    outage = np.sum(np.where(y["outage"], y["pv_exp"] * 0.1, 0))
    cur = y["curtailed"].sum()
    actual = y["pv_act"].sum() + y["w_act"].sum()
    other = pv_model - soil - outage - cur - actual
    steps = [("model 15.1 (PV + wind at MV)", pv_model), ("soiling (April)", -soil),
             ("inverter outage (June)", -outage), ("curtailment", -cur),
             ("other and noise", -other), ("actual", actual)]
    lines = ["loss waterfall of the operating year (MWh, synthetic)"]
    for name, v in steps:
        lines.append(f"  {name:30s} {v:10,.0f}")
    lines += [f"  actual is {actual / pv_model * 100:.2f} % of the model; each loss has a",
              "  cause, an owner and a fix: cleaning (ch 10), the inverter",
              "  maker's response time, the grid operator's limits"]
    csv("ch37-waterfall.csv", "i,v", [(i, round(v, 1)) for i, (_, v) in enumerate(steps)])
    emit("a_waterfall", lines)


if __name__ == "__main__":
    indicators()
    time_vs_energy()
    exclusions()
    windows()
    pr_temperature()
    waterfall()
