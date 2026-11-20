"""Chapter 37, lesson B (from data to diagnosis): validation checks on the
operating data, the daily residual against the model and a CUSUM that
finds a drift, the threshold between misses and false alarms, alarm
quality, root cause with evidence, and the limits of predictive
maintenance.

Run from the project root:   python -m companion.ch37.examples_b
Writes companion/ch37/expected/b_*.txt and diagrams/data/ch37-*.csv.
Synthetic data and teaching values (A-409 to A-411).
"""
from __future__ import annotations

import numpy as np

from companion.ch37 import sources as src
from companion.ch37.common import csv, emit
from plantp import performance as pf


def validation(seed: int = 373) -> None:
    y = src.operating_year()
    rng = np.random.default_rng(seed)
    ws = 3.0 + y["w_exp"] / 12 * 2.0 + np.abs(rng.normal(0, 0.3, 8760))   # proxy m/s
    ws[3001:3012] = ws[3000]                              # planted: 12 identical hours
    g = y["poa_sensor"].copy()
    night = y["poa_true"] < 1
    g[night] += 4.0                                       # planted: offset at night
    gap = np.zeros(8760, bool)
    gap[5000:5030] = True                                 # planted: 30 h missing
    # hours that belong to a run of 6 or more identical values
    same = np.r_[False, np.abs(np.diff(ws)) < 1e-9]
    flag_run = np.zeros(8760, bool)
    i = 0
    while i < 8760:
        if same[i]:
            j = i
            while j < 8760 and same[j]:
                j += 1
            if j - i + 1 >= 6:
                flag_run[i - 1:j] = True
            i = j
        else:
            i += 1
    checks = [("missing values", int(gap.sum())),
              ("wind speed stuck for 6 h or more", int(flag_run.sum())),
              ("irradiance above 2 W/m2 at night", int(np.sum(night & (g > 2)))),
              ("irradiance above 1,400 W/m2", int(np.sum(g > 1400)))]
    lines = ["validation checks on a year of hourly data (planted faults)",
             "  check                                  hours flagged"]
    for c, n in checks:
        lines.append(f"  {c:38s} {n:6d}")
    lines += [f"  night readings above 2 W/m2 in {np.sum(night & (g > 2)) / night.sum() * 100:.0f} %"
              " of night hours: not noise",
              "    but a constant offset of the pyranometer - serviced, and",
              "    the offset removed from the record with a flag",
              "  every check runs before any indicator: a stuck anemometer",
              "  makes a turbine look like it ignores the wind. Flagged",
              "  hours are marked, not deleted, and the indicator says how",
              "  many hours it rests on (ch 35, completeness)"]
    emit("b_validation", lines)


def daily_residual():
    y = src.operating_year()
    days = np.arange(365)
    r = np.empty(365)
    for d in days:
        s = y["day"] == d
        ex = y["pv_exp"][s].sum()
        r[d] = y["pv_act"][s].sum() / ex - 1 if ex > 1 else 0.0
    return r


def residual_cusum() -> None:
    r = daily_residual()
    csv("ch37-residual.csv", "d,r", [(d, round(v, 4)) for d, v in enumerate(r)])
    apr0, jun0 = 90, 160
    k, h = 0.01, 0.05
    d_min = int(np.argmin(r))
    a = pf.cusum(r[apr0:], k, h)
    j = pf.cusum(r[150:], k, h)
    lines = ["daily PV residual (actual / model - 1) and a CUSUM on it",
             f"  noise of the residual on ordinary days: {np.std(r[:90]):.3f}",
             f"  CUSUM (k {k}, h {h}) from 1 April: alarm on day {apr0 + a} (April {a + 1})",
             f"  from 31 May: alarm on day {150 + j}; the outage began on day {jun0}",
             "  a CUSUM adds up small shortfalls until they are too many",
             f"  to be noise: the step is found on its first day, the slow",
             f"  soiling drift after {a + 1} days - weeks before the monthly",
             "  report shows it",
             f"  the deepest day of all, day {d_min} ({r[d_min] * 100:.1f} %), is in August:",
             "    the export-limit signal explains it, so it is booked as",
             "    curtailment, not as a plant fault"]
    emit("b_cusum", lines)


def thresholds() -> None:
    r = daily_residual()
    bad = np.zeros(365, bool)
    bad[90:120] = True                                  # April soiling
    bad[160:169] = True                                 # June outage
    lines = ["a daily alarm when the residual falls below a threshold",
             "  threshold   days of problems found   false alarms in a year"]
    for th in (-0.02, -0.04, -0.06, -0.08):
        hit = r < th
        lines.append(f"  {th:9.2f}   {int(np.sum(hit & bad)):12d} of {int(bad.sum())}"
                     f"   {int(np.sum(hit & ~bad)):22d}")
    lines += ["  a tight threshold catches more of the problem days and",
              "  calls on healthy days; a loose one stays quiet and misses",
              "  the early soiling. The threshold is chosen for what a",
              "  false alarm costs (a site visit) against a miss (lost",
              "  energy), and the CUSUM is used where both matter"]
    emit("b_thresholds", lines)


def alarm_quality() -> None:
    rows = [("alarms in the month", 3_420), ("acted on by the operator", 410),
            ("standing for more than 24 h", 37), ("from the top 10 alarm tags", 2_050)]
    lines = ["alarm quality of a month (synthetic counts)",
             "  measure                            count"]
    for a, n in rows:
        lines.append(f"  {a:34s} {n:6,d}")
    lines += [f"  acted on: {410 / 3420 * 100:.0f} %; top ten tags: {2050 / 3420 * 100:.0f} % of all alarms",
              "  most alarms come from a few bad actors; fixing ten tags",
              "  removes six alarms in ten, and the ones left are the ones",
              "  an operator acts on (ch 35, alarm philosophy)"]
    emit("b_alarms", lines)


def root_cause() -> None:
    rows = [("what", "B07 at zero for 9 days", "block data"),
            ("when", "first zero 06:10, day 160", "event log, UTC"),
            ("immediate cause", "trip on DC insulation fault", "inverter log"),
            ("why not reset", "spare monitor not in stock", "CMMS, store"),
            ("root cause", "spares list older than a design change", "spares register"),
            ("fix", "spare added, list tied to notices", "work order")]
    lines = ["root cause of the June outage (synthetic record)",
             "  step              finding                                 evidence"]
    for a, b, c in rows:
        lines.append(f"  {a:17s} {b:39s} {c}")
    lines += ["  the root cause is the one that, fixed, stops it happening",
              "  again - here a spares list, not the inverter; every step",
              "  cites its evidence, kept with the event (lesson B)"]
    emit("b_rca", lines)


def evidence() -> None:
    rows = [("raw SCADA and historian data", "untouched copy, hash recorded"),
            ("event and alarm logs", "with their time base"),
            ("settings and configurations", "as found, before any change"),
            ("photographs and failed parts", "labelled, stored"),
            ("operator and maker statements", "dated, signed"),
            ("analysis scripts and their outputs", "with the data's hash")]
    lines = ["evidence kept with an event (teaching)",
             "  item                                   kept as"]
    for a, b in rows:
        lines.append(f"  {a:38s} {b}")
    lines += ["  evidence is collected before the fix changes it, and an",
              "  analysis can be repeated from it by someone else - the",
              "  basis of a warranty claim, an insurance claim or a",
              "  dispute with the grid operator"]
    emit("b_evidence", lines)


def pdm_limits() -> None:
    failures, detect, lead_ok = 4, 0.6, 0.8         # a year, teaching
    false_alarms, visit_cost = 6, 3_000
    saved_each, failure_cost = 0.7, 250_000         # share of a failure cost saved
    caught = failures * detect * lead_ok
    value = caught * saved_each * failure_cost
    cost = false_alarms * visit_cost
    lines = ["what a gearbox temperature model can and cannot do (teaching)",
             f"  failures a year {failures}; found early {detect * 100:.0f} %, with time to act"
             f" {lead_ok * 100:.0f} %",
             f"  failures caught in time: {caught:.1f}; value {value:,.0f} u",
             f"  false alarms {false_alarms}, a site visit each: {cost:,.0f} u",
             "  a useful tool - and a partial one: half the failures still",
             "  come as surprises, some faults give no warning in this",
             "  signal, and a model trained on one maker's gearbox does",
             "  not transfer to another. It supports inspection; it does",
             "  not replace it"]
    emit("b_pdm", lines)


if __name__ == "__main__":
    validation()
    residual_cusum()
    thresholds()
    alarm_quality()
    root_cause()
    evidence()
    pdm_limits()
