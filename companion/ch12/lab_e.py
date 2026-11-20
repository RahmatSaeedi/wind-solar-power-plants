"""Chapter 12, section E - resource-to-cleaning evidence: a dirty
irradiance sensor against dirty modules, the performance ratio each
combination reports, the soiling station's own sensors, and what the
cleaning decision of chapter 10 (D-014) needs from the resource data.

Run from the project root:   python -m companion.ch12.lab_e
Writes companion/ch12/expected/e_*.txt and diagrams/data/ch12-*.csv.
Soiling year of chapter 10 (A-195, seed 41); sensor cleaning A-247.
"""
from __future__ import annotations

import numpy as np

from companion.ch10 import lab_d as soil10
from companion.ch12 import sources
from companion.ch12.common import csv, emit

DAYS = 365


def sensor_loss(rate, rain, heavy, every: int | None):
    """Daily soiling loss of a sensor dome cleaned every `every` days
    (None: never), with the same deposition and rain as the modules."""
    loss = np.zeros(DAYS)
    x = 0.0
    for k in range(DAYS):
        x += rate[k]
        if heavy[k]:
            x = 0.0
        elif rain[k]:
            x *= 0.5
        if every and k % every == every - 1:
            x = 0.0                                   # cleaned at day's end
        loss[k] = x
    return loss


# [start: pr]
def reported_pr(true_pr, module_loss, sensor_loss_d):
    """PR as reported: energy / (measured irradiation x rated power). A
    dirty module lowers the energy; a dirty sensor lowers the measured
    irradiation, so it raises the reported PR."""
    return true_pr * (1 - module_loss) / (1 - sensor_loss_d)
# [end: pr]


def pr_bias() -> None:
    d, module, _, rain, heavy, rate = soil10.station_year()
    p = sources.pack()
    h_day = p["ghi"].reshape(DAYS, 24).sum(axis=1)       # daily weights
    pr0 = 0.862 / (1 - 0.0143)              # chapter 10 PR without soiling
    lines = ["what the performance ratio reports (A-247; modules never cleaned",
             "except by rain, chapter 10 soiling year):",
             "  sensor cleaning   mean sensor loss   reported PR   PR change"]
    rows = []
    for every, name in ((1, "daily"), (7, "weekly"), (30, "monthly"),
                        (None, "never")):
        s = sensor_loss(rate, rain, heavy, every)
        pr = reported_pr(pr0, module, s)
        w = float(np.sum(pr * h_day) / h_day.sum())
        rows.append((name, s, pr))
        lines.append(f"  {name:8s}          {100 * np.mean(s):5.2f} %           "
                     f"{w:.4f}        {100 * (w / (pr0 * (1 - np.average(module, weights=h_day))) - 1):+.2f} %")
    lines += [f"  true PR with dirty modules"
              f" {pr0 * (1 - np.average(module, weights=h_day)):.4f};"
              f" clean modules {pr0:.4f}",
              "  a sensor as dirty as the modules hides the module soiling:",
              "  the PR looks clean, the energy is lost and nobody cleans",
              "  daily sensor cleaning (or a heated, ventilated, cleaned pair)",
              "  keeps the reference honest; record every cleaning in the log"]
    emit("e_prbias", lines)
    csv("ch12-prbias.csv", "day,module,weekly,never",
        [(k + 1, f"{100 * module[k]:.3f}", f"{100 * rows[1][1][k]:.3f}",
          f"{100 * rows[3][1][k]:.3f}") for k in range(0, DAYS, 2)])


def station_sensors() -> None:
    """The soiling station's 'clean' reference cell must itself be clean:
    if it is cleaned weekly instead of daily, the soiling ratio is biased."""
    d, module, measured, rain, heavy, rate = soil10.station_year()
    ref = sensor_loss(rate, rain, heavy, 7)
    sr_true = 1 - module
    sr_meas = (1 - module) / (1 - ref)
    rates_true = soil10.estimate_rates(d, module, rain)
    rates_meas = soil10.estimate_rates(d, 1 - sr_meas, rain)
    mt = np.mean([r for _, r in rates_true])
    mm = np.mean([r for _, r in rates_meas])
    lines = ["soiling station: dirty cell / 'clean' cell (A-247):",
             f"  'clean' cell cleaned daily: mean soiling loss {100 * np.mean(1 - sr_true):.2f} %",
             f"  'clean' cell cleaned weekly: {100 * np.mean(1 - sr_meas):.2f} %"
             " (underestimated)",
             f"  soiling rate from rain-free spells: {100 * mt:.3f} %/day true,"
             f" {100 * mm:.3f} %/day biased",
             "  the optimal cleaning interval of chapter 10 scales with",
             f"  1 / sqrt(rate): biased by {100 * (np.sqrt(mt / mm) - 1):+.0f} %"
             " (cleaning too late)",
             "  the station's maintenance is part of the cleaning evidence"]
    emit("e_station", lines)


def requirements() -> None:
    """What the cleaning decision (D-014) needs from section C data."""
    lines = ["inputs of the module-cleaning decision and their source:",
             "  input                          source                 quality",
             "  daily soiling loss             soiling station        cells clean,",
             "                                                         calibrated",
             "  daily POA irradiation          station (cleaned       QC-flagged,",
             "                                 pyranometer)           gaps filled",
             "  rain events                    station rain gauge     time-aligned",
             "  energy and price               plant meter, PPA       chapter 21",
             "  cost per cleaning, water       O&M contract (ch 52)   quoted",
             "  without the first three, a cleaning trigger is a guess;",
             "  with them, D-014's trigger policy becomes a measured rule"]
    emit("e_inputs", lines)


if __name__ == "__main__":
    pr_bias()
    station_sensors()
    requirements()
