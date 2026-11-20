"""Chapter 31, lab D (worked example): plan the delivery and lift of a
nacelle from the port to its tower - the steps with their weather and
access hold points, the expected wait for a weather window and what it
costs, emergency access and response time from a remote workface, and
what separates this planning exercise from an approved lift plan.

Run from the project root:   python -m companion.ch31.lab_d
Writes companion/ch31/expected/d_*.txt. Teaching values (A-365, A-367).
"""
from __future__ import annotations

import numpy as np

from companion.ch31.common import emit
from plantp import datapack
from plantp import logistics as lg

# [start: plan]
PLAN = [   # step, hold point (H) or check (C), who releases it
    ("route permit and escort booked", "H", "transport company / authority"),
    ("bridge assessments accepted (2)", "H", "bridge owner's engineer"),
    ("overpass and power line measured", "H", "route surveyor / line owner"),
    ("crane assembled and inspected", "H", "crane inspector"),
    ("crane pad and mats accepted", "H", "civil engineer (ch 29, ch 30)"),
    ("tower erected and bolted, ready", "C", "erection supervisor"),
    ("convoy at the site gate, receiving check", "C", "receiving inspector"),
    ("forecast: 6 h below 10 m/s at hub", "H", "lift supervisor"),
    ("lift plan approved, briefing held", "H", "appointed person (lifts)"),
    ("exclusion zone set, rescue team on site", "H", "site manager"),
    ("radio check crane-ground-nacelle", "C", "lift supervisor"),
    ("lift, set, first bolts to maker's value", "-", "erection crew"),
]
# [end: plan]


def plan() -> None:
    lines = ["nacelle route-to-install plan with hold points (teaching)"]
    for k, (step, t, who) in enumerate(PLAN, 1):
        lines.append(f"  {k:2d} [{t}] {step}")
        lines.append(f"         released by {who}")
    n_h = sum(t == "H" for _, t, _ in PLAN)
    lines += [f"  {n_h} hold points: any one of them stops the next step",
              "  until the named person releases it"]
    emit("d_plan", lines)


def waiting() -> None:
    v = datapack.load_hourly()["ws_100m_ms"].to_numpy()
    limit, need = 10.0, 6
    ok = v < limit
    waits = []
    for start in range(0, len(v) - 400, 24):          # a crew ready at 06:00 each day
        k, run = start + 6, 0
        while k < len(v):
            run = run + 1 if ok[k] else 0
            if run >= need:
                break
            k += 1
        waits.append(max(k - need + 1 - (start + 6), 0))
    w = np.array(waits)
    standby = 60.0                                     # k u a day, crane and crew (teaching)
    lines = ["waiting for the nacelle's weather window (6 h below 10 m/s at hub)",
             "  crew ready at 06:00 on each day of the data-pack year:",
             f"  no wait {100 * (w == 0).mean():.0f} % of days; mean wait {w.mean():.1f} h;"
             f" worst {w.max():.0f} h",
             f"  expected standby cost a lift at {standby:.0f} k u a day: {standby * w.mean() / 24:.1f} k u;"
             f" worst {standby * w.max() / 24:.0f} k u",
             "  the average is small, the worst case is not: the contract",
             "  says who pays for weather standby, and the plan says",
             "  which work the crane does while it waits"]
    emit("d_waiting", lines)


def emergency() -> None:
    cases = [("on-site first aider and rescue team", 0.0, 60.0, 5.0, 25.0),
             ("district ambulance", 35.0, 60.0, 15.0, 30.0),
             ("hospital (by road)", 70.0, 70.0, 15.0, 30.0)]
    lines = ["emergency response to a casualty in the nacelle (teaching times, min)",
             "  responder                            km   mobilise  drive  access  total"]
    for name, km, spd, mob, acc in cases:
        t = lg.response_time(km, spd, mob, acc)
        drive = km / spd * 60 if km else 0.0
        lines.append(f"  {name:35s} {km:4.0f}   {mob:8.0f}  {drive:5.0f}  {acc:6.0f}  {t:5.0f}")
    lines += ["  outside help needs well over an hour to reach a casualty",
              "  at height: rescue from the nacelle is the site team's job",
              "  (trained, equipped, on site during lifts), and the medical",
              "  transfer plan is agreed with the local services (ch 32);",
              "  mobile coverage is patchy on the plain - radios or a",
              "  satellite link are part of the lift's hold points"]
    emit("d_emergency", lines)


def approved_plan() -> None:
    parts = ["crane configuration and the crane maker's load chart for it",
             "load data: mass, centre of gravity, lifting points (component maker)",
             "rigging: slings, shackles, spreader - certificates and inspection",
             "ground: pad bearing and mats (calculation and test, ch 29 / ch 30)",
             "weather limits and how they are measured on site",
             "exclusion zone, communications, roles and stop rules",
             "method statement and risk assessment, rescue arrangements",
             "signatures: lift planner, appointed person, crane operator"]
    lines = ["what an approved lift plan contains (this lab is not one)"]
    lines += [f"  {k}. {p}" for k, p in enumerate(parts, 1)]
    lines += ["  this chapter plans and asks; the approved plan is written",
              "  and signed by competent people for the real crane, load",
              "  and day - teaching numbers never go into it"]
    emit("d_approved", lines)


if __name__ == "__main__":
    plan()
    waiting()
    emergency()
    approved_plan()
