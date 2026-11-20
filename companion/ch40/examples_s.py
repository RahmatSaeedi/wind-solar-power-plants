"""Chapter 40, further lessons on the production system and its economics:
overall equipment effectiveness of the FAT bay, work in progress and lead
time (Little's law), assigning tasks to stations under precedence, a
flow-shop schedule of the ten skids, a reorder point with safety stock,
the cost of poor quality, the calibration interval that keeps a tool in
tolerance, and a design FMEA beside the process FMEA.

Run from the project root:   python -m companion.ch40.examples_s
Writes companion/ch40/expected/s_*.txt and diagrams/data/ch40-*.csv.
Teaching values (A-435 to A-437); a fictional integrator.
"""
from __future__ import annotations

import math

from companion.ch40 import sources as src
from companion.ch40.common import csv, emit
from plantp import quality as qa


# ------------------------------------------------------ OEE of the FAT bay
# [start: oee]
def oee(planned_h: float, down_h: float, ideal_h_per_unit: float,
        units: int, good: int) -> dict[str, float]:
    """Availability x performance x quality of one workstation."""
    run = planned_h - down_h
    a = run / planned_h
    p = ideal_h_per_unit * units / run
    q = good / units
    return dict(availability=a, performance=p, quality=q, oee=a * p * q)
# [end: oee]


def fat_bay() -> dict[str, float]:
    r = oee(planned_h=160.0, down_h=22.0, ideal_h_per_unit=8.0, units=13,
            good=12)
    lines = ["overall equipment effectiveness of the FAT bay, four weeks",
             "  planned 160 h; down 22 h (test set fault, waiting for skids)",
             "  13 skid tests at an ideal 8 h; 12 passed first time",
             f"  availability {r['availability']:.0%}  performance "
             f"{r['performance']:.0%}  quality {r['quality']:.0%}",
             f"  OEE {r['oee']:.0%}",
             "  the three losses point to three owners: maintenance of the",
             "  test set, the flow of skids into the bay, and the line that",
             "  sends faults to be found here (the FAT yield of lesson A)"]
    emit("s_oee", lines)
    return r


# ------------------------------------------------------ WIP and lead time
def wip() -> dict[str, float]:
    throughput = 10 / 160.0                      # skids an hour (takt 16 h)
    cases = {"lean flow (WIP 6)": 6, "batches of 5 (WIP 15)": 15}
    lines = ["work in progress and lead time (Little's law, L = lambda W)",
             f"  throughput {throughput * 40:.1f} skids a week"]
    out = {}
    for name, w in cases.items():
        lead = w / throughput
        out[name] = lead
        lines.append(f"  {name:22s} lead time {lead:5.0f} h = "
                     f"{lead / 40:.1f} weeks")
    lines += ["  the same line, the same throughput: more skids waiting",
              "  between stations only stretches the time each one spends",
              "  in the factory - and the time before a defect made at OP40",
              "  is found at OP80"]
    emit("s_wip", lines)
    return out


# ------------------------------------------- line balancing with precedence
# [start: balance]
TASKS = {  # task: (hours, predecessors) - OP40 to OP70 split into tasks
    "busbar supports": (3.0, []),
    "LV busbars": (4.0, ["busbar supports"]),
    "torque joints": (3.0, ["LV busbars"]),
    "LV cables": (4.0, ["busbar supports"]),
    "MV termination": (6.0, []),
    "earth bonds": (4.0, []),
    "aux wiring": (8.0, []),
    "control cables": (4.0, ["aux wiring"]),
}
# [end: balance]


def assign(tasks, cycle: float) -> list[list[str]]:
    """Largest-candidate rule: fill each station with the longest task
    whose predecessors are done and which still fits."""
    done, stations = set(), []
    while len(done) < len(tasks):
        load, st = 0.0, []
        while True:
            ready = [t for t, (h, pre) in tasks.items() if t not in done
                     and all(p in done for p in pre) and load + h <= cycle]
            if not ready:
                break
            t = max(ready, key=lambda k: tasks[k][0])
            st.append(t)
            done.add(t)
            load += tasks[t][0]
        if not st:
            raise ValueError("a task is longer than the cycle")
        stations.append(st)
    return stations


def balance() -> dict[str, float]:
    total = sum(h for h, _ in TASKS.values())
    lines = [f"tasks of OP40-OP70: {total:.0f} h a skid; minimum stations at"
             " a 16 h takt:", f"  ceil({total:.0f}/16) = "
             f"{math.ceil(total / 16)}"]
    out = {}
    for cycle in (16.0, 12.0):
        st = assign(TASKS, cycle)
        eff = total / (len(st) * cycle)
        out[cycle] = len(st)
        lines.append(f"  cycle {cycle:.0f} h: {len(st)} stations, "
                     f"efficiency {eff:.0%}")
        for k, s in enumerate(st, 1):
            load = sum(TASKS[t][0] for t in s)
            lines.append(f"    {k}  {load:4.1f} h  {', '.join(s)}")
    lines += ["  precedence keeps the torque after the busbars are fitted;",
              "  a faster cycle needs more stations and loses efficiency -",
              "  the rule is a heuristic, a check by hand is still needed"]
    emit("s_balance", lines)
    return out


# ---------------------------------------------------- flow-shop schedule
def flow_shop(times: list[float], n: int) -> tuple[float, list]:
    """Each unit passes the stations in order; a station takes the next
    unit when it is free and the unit has left the previous station."""
    m = len(times)
    finish = [[0.0] * m for _ in range(n)]
    bars = []
    for j in range(n):
        for k in range(m):
            start = max(finish[j - 1][k] if j else 0.0,
                        finish[j][k - 1] if k else 0.0)
            finish[j][k] = start + times[k]
            bars.append((j + 1, k + 1, round(start, 2), times[k]))
    return finish[-1][-1], bars


def schedule() -> dict[str, float]:
    from companion.ch40.examples_a import station_times
    times = list(station_times(True).values())
    span, bars = flow_shop(times, len(src.SERIALS))
    first = sum(times)
    neck = max(times)
    csv("ch40-gantt.csv", "skid,station,start,dur", bars)
    lines = ["flow-shop schedule of the ten skids (frames bought)",
             "  stations: " + ", ".join(f"S{k + 1} {t:.1f} h"
                                        for k, t in enumerate(times)),
             f"  first skid through: {first:.1f} h; then one every "
             f"{neck:.2f} h",
             f"  ten skids: {span:.1f} h = {span / 40:.1f} weeks of 40 h",
             f"  check: {first:.1f} + 9 x {neck:.2f} = {first + 9 * neck:.1f} h",
             "  takt is met in steady state, yet ten skids need more than",
             "  four weeks: the first skid takes 66 h to come through.",
             "  The window needs a start a week earlier or a second shift",
             "  in the first week - takt alone hides the time to fill"]
    emit("s_gantt", lines)
    return dict(span=span, first=first, neck=neck)


# ------------------------------------------- reorder point, safety stock
def reorder() -> dict[str, float]:
    d_mean, d_sd = 60.0, 18.0          # lugs a day used (two lines, A-435)
    lead = 10.0                         # days to restock
    z = 1.645                           # 95 % cycle service
    ss = z * d_sd * math.sqrt(lead)
    rop = d_mean * lead + ss
    lines = ["crimp lugs: reorder point with safety stock",
             f"  use {d_mean:.0f} a day (sd {d_sd:.0f}); restock {lead:.0f} days",
             f"  safety stock = 1.645 x {d_sd:.0f} x sqrt({lead:.0f}) = {ss:.0f}",
             f"  reorder point = {d_mean:.0f} x {lead:.0f} + {ss:.0f} = {rop:.0f}",
             "  the safety stock covers the variation of use in the lead",
             "  time, not a late supplier; a supplier change (lesson C)",
             "  also resets it - the new lot is held until released"]
    emit("s_reorder", lines)
    return dict(ss=ss, rop=rop)


# --------------------------------------------- cost of poor quality
COPQ = {  # k u for the ten skids (A-435, A-440)
    "prevention": {"FMEA and control plan": 6.0, "training": 4.0,
                   "probe fixture, torque analyser": 5.0},
    "appraisal": {"FAT and inspection": 16.0, "calibration": 3.0,
                  "owner's witness support": 2.0},
    "internal failure": {"rework (1.41 h x 10 x 0.06)": 0.85,
                         "re-tests after FAT faults": 2.4, "scrap": 1.5},
    "external failure": {"S-06 event": 63.4, "site checks S-05, S-07": 8.0},
}


def copq() -> dict[str, float]:
    tot = {k: sum(v.values()) for k, v in COPQ.items()}
    allc = sum(tot.values())
    lines = ["cost of quality of the ten skids (k u)"]
    for k, v in tot.items():
        lines.append(f"  {k:17s} {v:6.1f}  ({v / allc:4.0%})")
    lines += [f"  total {allc:.1f} k u; external failure alone is "
              f"{tot['external failure'] / allc:.0%}",
              "  one escaped defect cost more than all prevention and",
              "  appraisal together; the 8 k u of the corrective actions",
              "  (lesson D) would have been prevention money"]
    emit("s_copq", lines)
    return tot


# ------------------------------------------ calibration interval of a tool
def interval() -> dict[str, float]:
    mtbo = 400.0                       # days mean time to out-of-tolerance
    lines = ["calibration interval of a torque wrench (exponential drift,",
             f"mean time to out of tolerance {mtbo:.0f} days)",
             "  target in-tolerance at the end   interval, days"]
    out = {}
    for r in (0.95, 0.90, 0.80):
        t = -mtbo * math.log(r)
        out[r] = t
        lines.append(f"  {r:32.0%}   {t:12.0f}")
    lines += ["  the interval keeps most tools in tolerance on average; it",
              "  cannot catch a dropped tool - that is what the shift check",
              "  is for: a drop is a sudden failure, not a slow drift"]
    emit("s_interval", lines)
    return out


# --------------------------------------------- design FMEA beside PFMEA
DFMEA = [  # design FMEA rows of the skid (A-437)
    dict(item="LV busbar section", mode="overheats at full load",
         cause="cross-section by rule of thumb", s=8, o=2, d=3,
         control="heat-rise calculation, type test"),
    dict(item="skid frame", mode="fatigue crack at lift points",
         cause="lift lugs not designed", s=9, o=2, d=4,
         control="lift analysis, first-article check"),
    dict(item="enclosure vents", mode="condensation inside",
         cause="no heater in the design", s=6, o=4, d=5,
         control="humidity study, heaters specified"),
    dict(item="cable entries", mode="water ingress",
         cause="gland type not specified", s=7, o=3, d=4,
         control="IP rating test of one skid"),
]


def dfmea() -> list[dict]:
    rows = qa.fmea_rank(DFMEA)
    lines = ["design FMEA of the skid: failure caused by the design",
             "  item               mode                          S O D"]
    for r in rows:
        lines += [f"  {r['item']:18s} {r['mode']:29s} {r['s']} {r['o']} "
                  f"{r['d']}", f"      control: {r['control']}"]
    lines += ["  the design FMEA asks what the drawing allows to go wrong;",
              "  the process FMEA (lesson B) asks what the factory may do",
              "  wrong while following the drawing - both feed the ITP"]
    emit("s_dfmea", lines)
    return rows


if __name__ == "__main__":
    fat_bay()
    wip()
    balance()
    schedule()
    reorder()
    copq()
    interval()
    dfmea()
