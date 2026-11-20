"""Chapter 48, round u: spare sensors for a calibration rotation, cable
segregation in shared trays, patch-panel chains from switch to device,
what a biased pyranometer does to the PR, hours a cabinet spends above a
device's rating, and how long a configuration drift stays unseen.

Run from the project root:   python -m companion.ch48.examples_u
Writes companion/ch48/expected/u_*.txt and diagrams/data/ch48-*.csv.
Teaching values (A-498 to A-505); defensive administration only.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch48.common import csv, emit


# ------------------------------------------------ 1. spares for the rotation
def rotation(sensors: int = 8, interval_y: float = 3.0, away_weeks: float = 8.0) -> dict:
    away_share = away_weeks / 52 / interval_y
    spares = math.ceil(sensors * away_share) + 1
    rows = []
    for k in range(sensors):
        start = k * interval_y * 52 / sensors
        rows.append((k + 1, round(start, 1), round(start + away_weeks, 1)))
    csv("ch48-rotation.csv", "sensor,out,back", rows)
    lines = [f"{sensors} irradiance sensors on a {interval_y:.0f}-year calibration "
             f"interval, {away_weeks:.0f} weeks away each time",
             f"  share of the time one sensor is away: {away_share:.1%}; "
             f"expected away at once: {sensors * away_share:.2f}",
             f"  spares: ceil({sensors} x {away_share:.3f}) + 1 = {spares} (one for a failure)",
             "  staggered, one sensor leaves every "
             f"{interval_y * 52 / sensors:.1f} weeks and a spare takes its place",
             "  - the stations never stop measuring, and each swap is a line",
             "  in the instrument's record (lesson A interval)"]
    emit("u_rotation", lines)
    return dict(spares=spares, share=away_share)


# ------------------------------------------------ 2. segregation in trays
TRAYS = {   # tray: list of (cable, class)
    "TR-1": [("P-01", "power 400 V"), ("C-101", "analogue"), ("P-02", "power 400 V")],
    "TR-2": [("C-102", "analogue"), ("C-103", "RS-485"), ("F-11", "fibre")],
    "TR-3": [("P-05", "power 33 kV aux"), ("F-12", "fibre")],
    "TR-4": [("C-104", "Ethernet copper"), ("C-105", "analogue"), ("C-106", "Pt100")],
}
ALLOWED = {"power 400 V": {"power 400 V", "fibre"},
           "power 33 kV aux": {"power 33 kV aux", "fibre"},
           "analogue": {"analogue", "Pt100", "RS-485", "Ethernet copper", "fibre"},
           "Pt100": {"analogue", "Pt100", "RS-485", "Ethernet copper", "fibre"},
           "RS-485": {"analogue", "Pt100", "RS-485", "Ethernet copper", "fibre"},
           "Ethernet copper": {"analogue", "Pt100", "RS-485", "Ethernet copper", "fibre"},
           "fibre": {"analogue", "Pt100", "RS-485", "Ethernet copper", "fibre",
                     "power 33 kV aux", "power 400 V"}}


def segregation() -> list:
    bad = []
    for t, cables in TRAYS.items():
        classes = [c for _, c in cables]
        for a in classes:
            for b in classes:
                if b not in ALLOWED[a] and (t, a, b) not in bad and (t, b, a) not in bad:
                    bad.append((t, a, b))
    lines = ["cable classes sharing a tray against the project's segregation rule",
             "  (teaching: power apart from signals; fibre may run with anything)"]
    lines += [f"  {t}: {a} with {b}" for t, a, b in bad]
    lines += ["  TR-1 lays an analogue loop between two 400 V feeders: the",
              "  loop picks up their field and the reading wanders with the",
              "  load; the tray schedule is checked like any other schedule,",
              "  before cables are pulled (ch 24 trays, ch 34 cables)"]
    emit("u_segregation", lines)
    return bad


# ------------------------------------------------ 3. patch-panel chains
CHAIN = {   # switch port -> patch panel port -> outlet -> device
    ("SW-CTRL", 1): ("PP-A", 1), ("SW-CTRL", 2): ("PP-A", 2), ("SW-CTRL", 3): ("PP-A", 4),
    ("SW-CTRL", 4): ("PP-A", 3),
}
PP = {("PP-A", 1): "HMI-1", ("PP-A", 2): "HMI-2", ("PP-A", 3): "ENG-WS",
      ("PP-A", 4): "PRINTER"}
DESIGN = {("SW-CTRL", 1): "HMI-1", ("SW-CTRL", 2): "HMI-2", ("SW-CTRL", 3): "ENG-WS",
          ("SW-CTRL", 4): "PRINTER"}


def chains() -> list:
    bad = []
    lines = ["switch port -> patch panel -> device, followed for each port"]
    for k, want in DESIGN.items():
        pp = CHAIN[k]
        got = PP[pp]
        ok = got == want
        if not ok:
            bad.append((k, want, got))
        lines.append(f"  {k[0]}:{k[1]} -> {pp[0]}:{pp[1]} -> {got:8s} "
                     f"{'ok' if ok else 'design says ' + want}")
    lines += ["  two patch cords crossed at the panel: the engineering",
              "  workstation sits on the printer's port, with the printer's",
              "  access rules - each link of the chain was labelled right;",
              "  only following the whole chain finds it"]
    emit("u_chains", lines)
    return bad


# ------------------------------------------------ 4. pyranometer bias and PR
def pr_bias(pr_true: float = 0.82, biases=(-0.02, -0.01, 0.0, 0.01, 0.02),
            guarantee: float = 0.81) -> dict:
    lines = [f"a biased plane-of-array sensor and the PR test (true PR {pr_true:.2f}, "
             f"guarantee {guarantee:.2f})",
             "  sensor bias   reported PR   guarantee"]
    out = {}
    for b in biases:
        pr = pr_true / (1 + b)
        out[b] = pr
        lines.append(f"  {b:+11.0%}   {pr:11.3f}   {'met' if pr >= guarantee else 'MISSED'}")
    lines += ["  the PR divides by the measured irradiance: a sensor reading",
              f"  2 % high takes {100 * (pr_true - out[0.02]):.1f} points off the PR and "
              "fails a plant that",
              "  meets its guarantee - a guarantee test is",
              "  only as good as its sensor's certificate, which is why the",
              "  test protocol names the sensors and their calibrations (ch 37)"]
    emit("u_prbias", lines)
    return out


# ------------------------------------------------ 5. cabinet hours above rating
def cabinet_hours(seed: int = 4802, rating: float = 55.0, margin: float = 5.0) -> dict:
    rng = np.random.default_rng(seed)
    hours = np.arange(24 * 92)                          # June-August
    day = hours % 24
    amb = 33 + 8 * np.sin((day - 9) / 24 * 2 * np.pi) + rng.normal(0, 2, hours.size)
    sun = np.clip(np.sin((day - 6) / 12 * np.pi), 0, None) * 14   # gain, K
    inside = amb + 2 + sun * 0.85
    over = int((inside > rating - margin).sum())
    over_hard = int((inside > rating).sum())
    lines = ["PV block cabinet over a summer (synthetic hourly temperatures):",
             f"  hours inside above {rating - margin:.0f} C (rating {rating:.0f} C less "
             f"{margin:.0f} K): {over}",
             f"  hours above the rating itself: {over_hard}",
             f"  peak inside {inside.max():.0f} C at mid-afternoon (lesson A's summer "
             "day: 58 C)",
             f"  about {over / 92:.1f} hours of an average summer day near or over",
             "  its rating: a sun shield (up to 12 K of solar gain) or a",
             "  device rated higher - lesson A's single number hid how many",
             "  hours it lasts"]
    emit("u_hours", lines)
    return dict(over=over, hard=over_hard, peak=float(inside.max()))


# ------------------------------------------------ 6. how long a drift stays unseen
def detection(changes_per_year: int = 6, intervals=(1, 7, 30, 90)) -> dict:
    lines = ["configuration compared with its last backup every N days: how long",
             "  does an unrecorded change stay unseen on average?",
             "  every N days   mean days unseen   change-days a year"]
    out = {}
    for n in intervals:
        mean = n / 2
        out[n] = mean
        lines.append(f"  {n:12d}   {mean:16.1f}   {changes_per_year * mean:18.0f}")
    lines += ["  a daily comparison finds a change within a day; a quarterly",
              "  audit leaves it in place for six weeks on average - the",
              "  comparison of lesson C is cheap enough to run every day"]
    emit("u_detection", lines)
    return out


if __name__ == "__main__":
    rotation()
    segregation()
    chains()
    pr_bias()
    cabinet_hours()
    detection()
