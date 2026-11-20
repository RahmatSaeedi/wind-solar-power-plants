"""Chapter 34, lesson C: design and factory realisation in numbers - the
I/O count and its modules, the heat a control cabinet must lose, the
coverage of a control cause-and-effect matrix, configuration management
by fingerprint, defects found in the factory test and those still left,
and the effort of the factory test and the site loop checks.

Run from the project root:   python -m companion.ch34.examples_c
Writes companion/ch34/expected/c_*.txt and diagrams/data/ch34-defects.csv.
Teaching values (A-388); the design, the makers and the tests decide.
"""
from __future__ import annotations

import hashlib
import math

import numpy as np
from scipy.optimize import curve_fit

from companion.ch34 import sources as src
from companion.ch34.common import csv, emit
from plantp import instrumentation as ic


def io_totals() -> tuple[int, int, int]:
    ai = sum(n * a for _, n, a, _, _ in src.EQUIPMENT)
    di = sum(n * d for _, n, _, d, _ in src.EQUIPMENT)
    do = sum(n * o for _, n, _, _, o in src.EQUIPMENT)
    return ai, di, do


def io_count() -> None:
    ai, di, do = io_totals()
    per = {"AI": 8, "DI": 16, "DO": 16}
    lines = ["hard-wired I/O of the substation and plant controller (teaching)",
             "  kind   points   +20 % spare   channels/module   modules"]
    for kind, n in (("AI", ai), ("DI", di), ("DO", do)):
        m = ic.modules_needed(n, 0.2, per[kind])
        lines.append(f"  {kind:4s}   {n:6d}   {math.ceil(n * 1.2):11d}   {per[kind]:15d}"
                     f"   {m:7d}")
    lines += [f"  {ai + di + do} hard-wired points; turbines, inverters and battery",
              "  containers add thousands more by network (ch 35), which",
              "  is why the hard-wired list is kept for what must work",
              "  when the network does not: trips, interlocks, fire",
              "  signals, breaker positions"]
    emit("c_io", lines)


def panel_heat() -> None:
    ai, di, do = io_totals()
    mods = (ic.modules_needed(ai, 0.2, 8) + ic.modules_needed(di, 0.2, 16)
            + ic.modules_needed(do, 0.2, 16))
    parts = [("CPU pair", 2, 25.0), ("power supplies (losses)", 2, 22.0),
             ("I/O modules", mods, 3.0), ("interposing relays", 60, 0.5),
             ("network switches", 2, 15.0), ("transducers", 12, 2.5)]
    losses = sum(n * w for _, n, w in parts)
    area = 5.6                                   # m2 of free surface, 0.8 x 2.0 x 0.6 m
    rise = ic.panel_rise_k(losses, area)
    rating = 55.0
    lines = ["heat inside the plant-controller cabinet (teaching losses)",
             "  part                         count   W each   W"]
    for name, n, w in parts:
        lines.append(f"  {name:28s} {n:5d}   {w:6.1f}   {n * w:4.0f}")
    lines += [f"  total {losses:.0f} W; closed cabinet with {area} m2 of surface:"
              f" rise {rise:.0f} K"]
    for room, note in ((25.0, "room cooled"), (40.0, "HVAC lost, mild day"),
                       (47.0, "HVAC lost, summer day")):
        inside = room + rise
        lines.append(f"  room {room:.0f} deg C ({note}): inside {inside:.0f}"
                     f" - {'within' if inside <= rating else 'OVER'} the {rating:.0f} deg C rating")
    lines += [f"  a filtered fan for a 5 K rise needs {ic.fan_flow_m3h(losses, 5.0):.0f} m3/h",
              "  the cabinet is fine while the room is cooled and fails",
              "  on a summer day without it: the control-room HVAC is an",
              "  essential load (ch 23), and the cabinet temperature is",
              "  an alarm on the I/O list"]
    emit("c_panel", lines)


def cause_effect() -> None:
    causes = {
        "POC voltage measurement bad": ["hold Q set point", "alarm"],
        "operator set point stale > 10 s": ["hold last set point", "alarm"],
        "operator link lost > 1 h": ["fallback schedule (ch 20)", "alarm"],
        "110 V DC undervoltage": ["alarm", "shed non-essential loads"],
        "UPS on battery": ["alarm"],
        "BESS container fire (from fire panel)": ["PCS stop", "alarm", "HVAC off"],
        "cabinet over-temperature": []}
    tests = {"hold Q set point": "T-07", "alarm": "T-01", "hold last set point": "T-12",
             "fallback schedule (ch 20)": "T-13", "shed non-essential loads": "T-21",
             "PCS stop": "T-30", "HVAC off": "T-31"}
    lines = ["control cause-and-effect matrix: coverage check (teaching)",
             "  cause                                    effects   tests"]
    gaps = []
    for c, effs in causes.items():
        t = [tests.get(e, "?") for e in effs]
        if not effs:
            gaps.append(c)
        lines.append(f"  {c:40s} {len(effs):7d}   {', '.join(t) if t else '-'}")
    lines += [f"  causes without an effect: {gaps}",
              "  each cause needs at least one effect and each effect a",
              "  test that proves it; the fire rows are copied from the",
              "  fire panel's own matrix (ch 32, lab C), never redrawn",
              "  by the control designer, so the two cannot disagree"]
    emit("c_ce", lines)


def config() -> None:
    tested = "PPC v2.3.1\nQ_DEADBAND=0.005\nV_DROOP=0.04\nRAMP=10\nHOLD_S=3600\n"
    site = "PPC v2.3.1\nQ_DEADBAND=0.005\nV_DROOP=0.05\nRAMP=10\nHOLD_S=3600\n"
    h1 = hashlib.sha256(tested.encode()).hexdigest()[:12]
    h2 = hashlib.sha256(site.encode()).hexdigest()[:12]
    diff = [(a, b) for a, b in zip(tested.splitlines(), site.splitlines()) if a != b]
    lines = ["configuration management: is the site running what was tested?",
             f"  fingerprint of the FAT configuration:  {h1}",
             f"  fingerprint read back from the site:   {h2}",
             f"  match: {'yes' if h1 == h2 else 'NO'}"]
    for a, b in diff:
        lines.append(f"  tested {a}  ->  on site {b}")
    lines += ["  a droop changed on site without a change record makes",
              "  every FAT result for voltage control invalid: the change",
              "  goes through management of change (ch 32), is re-tested",
              "  and gets a new fingerprint; the fingerprint is on the",
              "  commissioning record (ch 26 did the same for settings)"]
    emit("c_config", lines)


def defects() -> None:
    days = np.arange(1, 9)
    found = np.array([14, 10, 8, 5, 4, 3, 2, 1], float)        # synthetic FAT log
    cum = np.cumsum(found)

    def model(t, n, b):
        return n * (1 - np.exp(-b * t))

    (n, b), _ = curve_fit(model, days, cum, p0=(50.0, 0.3))
    left = n - cum[-1]
    csv("ch34-defects.csv", "day,cum,model", [(int(d), int(c), round(float(model(d, n, b)), 1))
                                             for d, c in zip(days, cum)])
    lines = ["defects found per day of the factory test, and those still left",
             "  day: " + "  ".join(f"{int(x):2d}" for x in days),
             "  new: " + "  ".join(f"{int(x):2d}" for x in found),
             f"  fitted N(1 - exp(-b t)): N = {n:.1f}, b = {b:.2f} per day",
             f"  found {cum[-1]:.0f}; expected still hidden about {left:.0f}",
             "  the falling rate says testing works; the fit says a few",
             "  defects remain - the FAT closes with a punch list and the",
             "  site tests (lesson D) look for exactly those, not with a",
             "  claim of zero defects"]
    emit("c_defects", lines)


def effort() -> None:
    ai, di, do = io_totals()
    fat_h = (ai * 3 + di * 1 + do * 2) / 60 + 40          # min per point + 40 h functions
    loops = ai + di + do
    crew_day = 40                                          # points a two-person crew checks a day
    lines = ["effort of the factory test and of the site loop checks (teaching)",
             f"  FAT: {ai} AI x 3 min + {di} DI x 1 min + {do} DO x 2 min",
             f"    + 40 h of functional tests = {fat_h:.0f} h",
             f"  site loop checks: {loops} points at {crew_day} a crew-day ="
             f" {math.ceil(loops / crew_day)} crew-days",
             "  loop checks run on de-energised equipment with a signal",
             "  injected at the field end (a calibrator in place of the",
             "  transmitter, a jumper in place of a contact): no work on",
             "  live parts; each point gets an as-found and as-left value",
             "  and the signature of the checker (ch 49)"]
    emit("c_effort", lines)


if __name__ == "__main__":
    io_count()
    panel_heat()
    cause_effect()
    config()
    defects()
    effort()
