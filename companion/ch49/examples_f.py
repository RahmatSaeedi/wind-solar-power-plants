"""Chapter 49, lessons F-J: auxiliary systems installed and preserved,
fire-system construction records (submittals, penetrations, detector
positions, impairments), construction water by month and its meters, the
132 kV corridor and the WS1 cable sections, and the social plan's records
(grievances, local hiring, village traffic, a chance find).

Run from the project root:   python -m companion.ch49.examples_f
Writes companion/ch49/expected/f_*.txt to j_*.txt and diagrams/data/ch49-water.csv.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch29 import sources as s29
from companion.ch49 import sources as src
from companion.ch49.common import csv, emit
from plantp import construction as con


# ------------------------------------------------ F. auxiliary systems
def aux() -> dict:
    steps = ["installed", "labelled", "connected", "inspected", "preserved"]
    gaps = {}
    for item, (rec, *flags) in src.AUX.items():
        miss = [s for s, f in zip(steps, flags) if f is False]
        if miss:
            gaps[item] = miss
    batt = src.AUX["station battery 110 V"][0]
    stored = src.AUX_DAY - batt
    lines = [f"station-service equipment on day {src.AUX_DAY}: steps not done"]
    lines += [f"  {k:22s} {', '.join(v)}" for k, v in gaps.items()]
    lines += [f"  the station battery has waited {stored} days since receipt; the",
              f"  maker allows {src.BATTERY_STORE_MAX} before a refresh charge "
              "(teaching): it is now",
              "  a record to raise with the maker, not a battery to install",
              "  as delivered; the DC board has no labels yet and the fire",
              "  pump set is connected but not inspected"]
    emit("f_aux", lines)
    return dict(gaps=gaps, stored=stored)


# ------------------------------------------------ G. fire-system QA
def fire() -> dict:
    sub = [k for k, (_, cert, ok) in src.SUBMIT.items() if not ok or cert is None]
    pen_bad = {p: [n for n, f in zip(("inspected", "photo", "label"), v) if not f]
               for p, v in src.PEN.items() if not all(v)}
    det_bad = []
    for d, (app, inst) in src.DETECT.items():
        if inst is None:
            det_bad.append((d, "not installed"))
        elif con.distance(app, inst) > src.DETECT_TOL:
            det_bad.append((d, f"{con.distance(app, inst):.1f} m from the approved spot"))
    lines = ["fire-system construction records (the approved design rules)",
             "  submittals not approved or without a certificate:",
             f"    {', '.join(sub)}",
             f"  penetrations with gaps: {len(pen_bad)} of {len(src.PEN)}"]
    lines += [f"    {p}: {', '.join(v)}" for p, v in pen_bad.items()]
    lines += [f"  detectors: {d} {why}" for d, why in det_bad]
    lines += ["  fire stopping is being installed from a system whose",
              "  submittal is not approved: every penetration sealed with it",
              "  waits on that approval; a detector moved 1.4 m to clear a",
              "  duct goes back to the designer, not the installer"]
    emit("g_fire", lines)
    return dict(sub=sub, pen=pen_bad, det=det_bad)


def impairments() -> list:
    open_ = [(s, a, m) for s, a, b, m in src.IMPAIR if b is None]
    lines = [f"fire-system impairments on day {src.AUX_DAY}"]
    for s, a, b, m in src.IMPAIR:
        days = (b if b is not None else src.AUX_DAY) - a
        lines.append(f"  {s:22s} day {a}-{b if b is not None else 'open':>4}  "
                     f"{days:3d} d  {m or 'NO MEASURE'}")
    lines += [f"  {len(open_)} open; hydrant H-04 has been out 21 days with no",
              "  compensating measure - each impairment has an owner, a",
              "  measure, a notice to the responders and an end (ch 32)"]
    emit("g_impair", lines)
    return open_


# ------------------------------------------------ H. construction water
def water() -> dict:
    d = s29.DEMAND
    months = np.arange(1, 19)
    curve = np.sin(np.pi * (months - 0.5) / 18) ** 1.5
    workers = 450 * curve / curve.max()
    people = workers * d["worker_l_day"] * 30 / 1000
    concrete = np.zeros(18)
    concrete[3:12] = d["construction_concrete_m3"] / 9 * (d["water_per_m3_concrete"]
                                                         + d["curing_per_m3"])
    dust_m = d["dust_l_m2_day"] * d["road_area_m2"] / 1000 * d["dust_days"] / 18
    dust = np.full(18, dust_m)
    total = people + concrete + dust
    wells_m = src.WATER_WELLS_M3 / 18
    csv("ch49-water.csv", "month,people,concrete,dust",
        [(m, round(a), round(b), round(c)) for m, a, b, c in zip(months, people, concrete,
                                                                   dust)])
    lines = ["construction water by month (ch 29 demand, ch 22 workforce curve), m3",
             "  month  people  concrete  dust   total  trucked beyond the wells"]
    for m in (1, 5, 9, 13, 18):
        k = m - 1
        lines.append(f"  {m:5d}  {people[k]:6.0f}  {concrete[k]:8.0f}  {dust[k]:5.0f}  "
                     f"{total[k]:6.0f}  {max(0.0, total[k] - wells_m):8.0f}")
    lines += [f"  total {total.sum():,.0f} m3 (ch 29: 87,460); wells {src.WATER_WELLS_M3:,.0f};"
              f" dust {dust.sum() / total.sum():.0%} of it",
              "  dust suppression is the largest use: water on roads is the",
              "  first saving (binder, speed limits, sealed sections), and it",
              "  is metered apart from the plant's permanent water (ch 18)"]
    emit("h_water", lines)
    return dict(total=float(total.sum()), dust_share=float(dust.sum() / total.sum()))


def meters() -> list:
    rows = [(m, t, w, (t - w) / t) for m, (t, w) in src.TICKETS.items()]
    bad = [r for r in rows if abs(r[3]) > 0.03]
    lines = ["trucked water: delivery tickets against the meter at the tank, m3",
             "  month  tickets  meter  difference"]
    lines += [f"  {m:5d}  {t:7d}  {w:5d}  {x:+9.1%}" for m, t, w, x in rows]
    lines += [f"  month {bad[0][0]}: {bad[0][1] - bad[0][2]} m3 paid for and not received"
              if bad else "  all within 3 %",
              "  - a short delivery or water drawn on the way; the meter is",
              "  read each day and the tickets checked against it weekly"]
    emit("h_meters", lines)
    return bad


# ------------------------------------------------ I. collector and export
def corridor() -> dict:
    blocked = [t for t, (_, acc, _) in src.TOWERS.items() if not acc]
    owners = sorted({src.TOWERS[t][0] for t in blocked})
    done = sum(1 for _, _, f in src.TOWERS.values() if f)
    joints = {s: (L, max(0, math.ceil(L / drum) - 1), bays)
              for s, (L, drum, bays) in src.SECTIONS.items()}
    short = [s for s, (L, need, bays) in joints.items() if need > bays]
    lines = [f"132 kV line: {done} of {len(src.TOWERS)} foundations done; no access "
             f"agreement for {', '.join(blocked)}",
             f"  (landowner {', '.join(owners)}) - the line crew's sequence skips them",
             "  and the agreement is the item on the critical path",
             "  crossings and who approves them:"]
    lines += [f"    {x}: {k} - {who}; {how}" for x, k, who, how in src.CROSS]
    lines += ["  WS1 cable sections against 1,500 m drums:",
              "    section  length m  joints needed  joint bays"]
    lines += [f"    {s:7s}  {L:8d}  {n:13d}  {b:10d}" for s, (L, n, b) in joints.items()]
    lines += [f"  {', '.join(short)} needs one more joint bay than the route drawing",
              "  shows: it is added before the trench, not found at the drum's end"]
    emit("i_corridor", lines)
    return dict(blocked=blocked, short=short)


# ------------------------------------------------ J. social plan
def grievances() -> dict:
    late_ack = [g for g, r, _, a, _ in src.GRIEV if a - r > src.GRIEV_ACK_DAYS]
    open_ = [(g, c, src.AUX_DAY - r) for g, r, c, _, cl in src.GRIEV if cl is None]
    over = [g for g, c, age in open_ if age > src.GRIEV_CLOSE_DAYS]
    wages = [g for g, _, c, _, _ in src.GRIEV if c.startswith("wages")]
    lines = [f"grievance log on day {src.AUX_DAY} (acknowledge in {src.GRIEV_ACK_DAYS} days, "
             f"close in {src.GRIEV_CLOSE_DAYS})",
             f"  acknowledged late: {', '.join(late_ack)}"]
    lines += [f"  open: {g} ({c}) for {age} days" for g, c, age in open_]
    lines += [f"  past the closing time: {', '.join(over)}",
              f"  the two oldest open ones are one subcontractor's wages ({', '.join(wages)}):",
              "  a pattern, not two cases - it goes to the EPC contractor's",
              "  management under the approved labour plan, and the",
              "  workers are told what happens next (ch 33 workflow)"]
    emit("j_griev", lines)
    return dict(late_ack=late_ack, open=open_, over=over)


def hiring() -> dict:
    rows = [(m, w, l, l / w) for m, (w, l) in src.HIRE.items()]
    below = [m for m, *_, s in rows if s < src.HIRE_TARGET]
    lines = [f"local hiring against the approved {src.HIRE_TARGET:.0%} commitment",
             "  month  workers  local  share"]
    lines += [f"  {m:5d}  {w:7d}  {l:5d}  {s:5.0%}" for m, w, l, s in rows]
    lines += [f"  below the commitment from month {below[0]}: the share fell as the",
              "  workforce grew with specialist crews from outside; the",
              "  report says so, with the trades local people can be",
              "  trained for - the plan is reported as it is, not as hoped"]
    emit("j_hire", lines)
    return dict(below=below, last=rows[-1][3])


def traffic() -> dict:
    quiet = {h: src.TRAFFIC[h] for h in src.QUIET_HOURS}
    lines = ["heavy vehicles through the village by hour (mean of a week)",
             "  " + "  ".join(f"{h:02d}" for h in src.TRAFFIC),
             "  " + "  ".join(f"{v:2d}" for v in src.TRAFFIC.values()),
             f"  school hours {', '.join(f'{h:02d}:00' for h in src.QUIET_HOURS)} "
             "should have none (approved traffic plan):",
             f"  {sum(quiet.values())} vehicles a day in them",
             "  the plan is enforced at the gate: deliveries are booked",
             "  outside the quiet hours and drivers briefed; a count like",
             "  this one is the evidence the plan works (ch 32, ch 33)"]
    emit("j_traffic", lines)
    return quiet


def chance_find() -> dict:
    f = src.FIND
    stop_min = 15
    notify_h = 24 + 11 - 9 - 40 / 60
    lines = [f"chance find on day {f['day']}: found {f['found']}, work stopped {f['stop']},",
             f"  authority notified {f['notified']}",
             f"  stop within {stop_min} minutes, a {f['radius_m']} m exclusion: as the procedure",
             f"  notification after {notify_h:.1f} h against {f['procedure_hours']} h: late",
             "  the procedure worked on the ground and failed on the phone:",
             "  the contact list had the authority's office line only - the",
             "  fix is in the procedure, and the find stays fenced until",
             "  the authority releases it (ch 33 chance finds)"]
    emit("j_find", lines)
    return dict(notify_h=notify_h)


if __name__ == "__main__":
    aux()
    fire()
    impairments()
    water()
    meters()
    corridor()
    grievances()
    hiring()
    traffic()
    chance_find()
