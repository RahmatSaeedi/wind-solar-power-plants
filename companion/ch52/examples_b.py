"""Chapter 52, lesson B: subsystem maintenance - the PV string sample,
gearbox vibration and its P-F interval, inspections needed inside it,
gearbox oil, inverter heat-sink rise, transformer gas trends, breaker
contact wear, battery capacity spread, sensor drift, fibre margin, and
the preventive workload by subsystem.

Run from the project root:   python -m companion.ch52.examples_b
Writes companion/ch52/expected/b_*.txt and diagrams/data/ch52-vib.csv.
Teaching values (A-531).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch52 import sources as src
from companion.ch52.common import csv, emit
from plantp import ram


# ------------------------------------------------ 1. PV string sample
def pv_sample(strings: int = 4_200, share: float = 0.05, bad: int = 12) -> dict:
    n = round(strings * share)
    p_miss = math.comb(strings - bad, n) / math.comb(strings, n)
    lines = [f"annual I-V sample: {n} of {strings:,} strings ({share:.0%}); {bad} strings "
             "degraded",
             f"  chance the sample finds at least one: {1 - p_miss:.0%}; expected found "
             f"{bad * share:.1f}",
             "  a 5 % sample measures the fleet (a shift in mean power), it",
             "  does not find rare faults - those come from the combiner",
             "  currents every day (lesson D) and the thermography flight"]
    emit("b_pvsample", lines)
    return dict(n=n, p_find=1 - p_miss)


# ------------------------------------------------ 2. gearbox vibration trend
def vibration(alert: float = 4.5, alarm: float = 7.1, seed: int = 52) -> dict:
    rng = np.random.default_rng(seed)
    weeks = np.arange(40)
    v = 2.0 + rng.normal(0, 0.15, weeks.size)
    onset = 22
    v[onset:] += 0.35 * (np.exp(0.18 * (weeks[onset:] - onset)) - 1)
    csv("ch52-vib.csv", "week,mms", [(int(w), round(float(x), 2)) for w, x in zip(weeks, v)])
    w_alert = int(weeks[np.argmax(v >= alert)]) if np.any(v >= alert) else None
    w_alarm = int(weeks[np.argmax(v >= alarm)]) if np.any(v >= alarm) else None
    lines = ["T07 gearbox high-speed bearing: vibration velocity, weekly (mm/s RMS),",
             f"  teaching alert {alert} and alarm {alarm}",
             f"  growth starts about week {onset}; alert crossed week {w_alert}, alarm "
             f"week {w_alarm}",
             f"  alert to alarm: {w_alarm - w_alert} weeks - the time to order the bearing,",
             "  book the crane and pick a low-wind window (ch 31); a",
             "  monthly hand reading could miss those weeks altogether"]
    emit("b_vibration", lines)
    return dict(onset=onset, alert=w_alert, alarm=w_alarm)


# ------------------------------------------------ 3. inspections inside the P-F interval
def pf(pf_weeks: float = 8.0, target: float = 0.95) -> dict:
    out = {}
    for name, p in (("hand-held reading", 0.6), ("route with data collector", 0.8),
                    ("online CMS", 0.95)):
        n = ram.inspections_needed(p, target)
        out[name] = (p, n, pf_weeks / n)
    lines = [f"P-F interval {pf_weeks:.0f} weeks; inspections needed to catch the fault with "
             f"{target:.0%}",
             "  method                      p(detect)   n   interval (weeks)"]
    lines += [f"  {k:28s} {p:8.2f} {n:4d} {iv:10.1f}" for k, (p, n, iv) in out.items()]
    lines += ["  the weaker the single check, the more often it must be done:",
              "  a hand reading every two weeks or a route every four weeks;",
              "  online monitoring reads continuously - its value is the",
              "  weeks it adds to plan the repair"]
    emit("b_pf", lines)
    return out


# ------------------------------------------------ 4. gearbox oil
def oil() -> dict:
    samples = {"T03": [8, 9, 11, 10], "T05": [12, 14, 13, 15], "T07": [9, 12, 21, 38],
               "T11": [7, 8, 8, 9]}                     # iron ppm, every 3 months
    rate = {k: (v[-1] - v[-2]) / 3 for k, v in samples.items()}
    worst = max(rate, key=rate.get)
    lines = ["gearbox oil: iron (ppm) in four quarterly samples, four turbines shown"]
    lines += [f"  {k}: " + " ".join(f"{x:3d}" for x in v) + f"   last rise {rate[k]:+.1f} ppm/month"
              for k, v in samples.items()]
    lines += [f"  {worst} rises fastest - the same bearing the vibration trend",
              "  found: two independent signals on one fault make the case",
              "  for the repair; a level alone (T05 is higher than T03) says",
              "  less than the rate"]
    emit("b_oil", lines)
    return dict(worst=worst, rate=rate[worst])


# ------------------------------------------------ 5. inverter heat-sink rise
def heatsink() -> dict:
    months = np.arange(1, 13)
    rise = np.array([18.0, 18.2, 18.6, 19.5, 20.6, 22.0, 23.1, 18.3, 18.6, 19.0, 19.4, 19.9])
    clean = int(np.argmax(np.diff(rise) < -2)) + 2
    slope = float(np.polyfit(months[:clean - 1], rise[:clean - 1], 1)[0])
    lines = ["PV inverter PVF2-3: heat-sink rise over coolant at 90 % power (K), monthly",
             "  " + " ".join(f"{x:4.1f}" for x in rise),
             f"  rising {slope:.2f} K a month in the dust season; filters changed in month "
             f"{clean}",
             "  a rise of 5 K takes the stack 5 K nearer its derating; the",
             "  trend times the filter change better than a calendar (ch 44",
             "  thermal stack-up, ch 51 filters)"]
    emit("b_heatsink", lines)
    return dict(slope=slope, clean=clean)


# ------------------------------------------------ 6. transformer gases
def dga() -> dict:
    h2 = [12, 14, 15, 41]
    c2h2 = [0.0, 0.0, 0.1, 0.9]                         # ppm, quarterly, T2
    lines = ["main transformer T2 dissolved gases, quarterly (ppm)",
             "  H2   " + " ".join(f"{x:5d}" for x in h2),
             "  C2H2 " + " ".join(f"{x:5.1f}" for x in c2h2),
             f"  H2 x{h2[-1] / h2[-2]:.1f} in one quarter and acetylene appearing: the",
             "  interpretation (ch 43, IEC 60599) is a specialist's; the",
             "  maintenance step is to shorten the sampling to monthly and",
             "  to compare with the load and the tap-changer operations"]
    emit("b_dga", lines)
    return dict(h2_ratio=h2[-1] / h2[-2])


# ------------------------------------------------ 7. breaker contact wear
def wear(budget_ka2: float = 10_000.0) -> dict:
    ops = {"WS1": [(0.6, 40), (8.2, 1)], "WS2": [(0.6, 35), (11.5, 2)],
           "PVF1": [(0.4, 20)], "BESS-A": [(0.3, 220)]}    # (kA, operations)
    used = {k: sum(i * i * n for i, n in v) / budget_ka2 for k, v in ops.items()}
    lines = ["33 kV breakers: contact wear as sum of I^2 per operation against",
             f"  a teaching budget of {budget_ka2:,.0f} kA^2"]
    lines += [f"  {k:7s} " + ", ".join(f"{n} x {i} kA" for i, n in v) + f"  -> {used[k]:.1%}"
              for k, v in ops.items()]
    lines += ["  two fault clearances on WS2 used more than all the load",
              "  switching of the battery feeder: wear follows faults, so the",
              "  service is triggered by the counter, not the calendar (ch 25)"]
    emit("b_wear", lines)
    return used


# ------------------------------------------------ 8. battery capacity spread
def bess_soh() -> dict:
    soh = [97.8, 97.5, 97.9, 97.6, 97.4, 97.7, 95.1, 97.6]      # % after one year
    m = float(np.median(soh))
    low = [k + 1 for k, x in enumerate(soh) if x < m - 1.5]
    lines = ["battery containers: capacity test after the first year (% of rated)",
             "  " + " ".join(f"{x:5.1f}" for x in soh),
             f"  median {m:.1f} %; below median - 1.5 points: container(s) "
             f"{', '.join(map(str, low))}",
             "  container 7 is the one that waited 410 h for its cooling part",
             "  (ch 51): heat ages cells, and the capacity test is where it",
             "  shows - the warranty claim needs this record (ch 19)"]
    emit("b_soh", lines)
    return dict(median=m, low=low)


# ------------------------------------------------ 9. sensor drift
def sensor() -> dict:
    ratio = [1.000, 0.998, 0.995, 0.989, 0.984, 0.979, 1.001, 0.999]   # pyranometer/ref cell
    worst = min(ratio)
    lines = ["POA pyranometer against the cleaned reference cell, weekly ratio",
             "  " + " ".join(f"{x:.3f}" for x in ratio),
             f"  down {1 - worst:.1%} before cleaning in week 7: a dirty sensor reads low",
             "  and makes the PR look high - the cleaning interval of the",
             "  sensors is set by this ratio, and the cleaning is logged so",
             "  the PR can be corrected (ch 37, ch 48)"]
    emit("b_sensor", lines)
    return dict(drop=1 - worst)


# ------------------------------------------------ 10. fibre margin
def fibre(budget_db: float = 10.0) -> dict:
    loss = {"east ring": [6.8, 6.9, 7.4], "west ring": [8.9, 9.1, 9.6], "PV ring": [5.2, 5.2, 5.3]}
    lines = [f"fibre rings: measured loss at the yearly check (dB), budget {budget_db} dB"]
    for k, v in loss.items():
        lines.append(f"  {k:9s} " + " ".join(f"{x:4.1f}" for x in v)
                     + f"   margin {budget_db - v[-1]:.1f} dB")
    lines += ["  the west ring (ch 35) has 0.4 dB left after a splice repair:",
              "  one more repair and it fails - the cleaning of connectors",
              "  and a spare fibre pair are planned before then"]
    emit("b_fibre", lines)
    return {k: budget_db - v[-1] for k, v in loss.items()}


# ------------------------------------------------ 11. preventive workload by subsystem
def pm_by_subsystem() -> dict:
    out = {}
    for sub, task, months, h, units, outage in src.PM_TASKS:
        y = units * h * 12 / months
        a, b = out.get(sub, (0.0, 0.0))
        out[sub] = (a + y, b + (y if outage else 0.0))
    tot = sum(a for a, _ in out.values())
    lines = ["preventive hours a year by subsystem (and those needing an outage)"]
    lines += [f"  {k:12s} {a:7,.0f} h   outage {b:7,.0f} h" for k, (a, b) in
              sorted(out.items(), key=lambda kv: -kv[1][0])]
    lines += [f"  total {tot:,.0f} h; the outage hours are the ones planned into",
              "  low-resource months (lesson F) and agreed in the outage",
              "  request (ch 51)"]
    emit("b_pmtable", lines)
    return out


if __name__ == "__main__":
    pv_sample()
    vibration()
    pf()
    oil()
    heatsink()
    dga()
    wear()
    bess_soh()
    sensor()
    fibre()
    pm_by_subsystem()
