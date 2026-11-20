"""Chapter 35, fourth deeper round: what a sampling rate can show, a check
of the address plan, a check of the point list, staleness of points that
report only on change, the telemetry budget of the link to the grid
operator, historian disks, and the sample size for accepting network
points.

Run from the project root:   python -m companion.ch35.examples_q
Writes companion/ch35/expected/q_*.txt and diagrams/data/ch35-alias.csv.
Synthetic data and teaching values (A-393 to A-399).
"""
from __future__ import annotations

import ipaddress
import math

import numpy as np

from companion.ch35.common import csv, emit
from plantp import scada as sc


def aliasing() -> None:
    f_osc = 0.08                                   # Hz, a slow power oscillation
    t = np.arange(0, 600, 0.1)
    x = 2.0 * np.sin(2 * np.pi * f_osc * t)        # MW around the set point
    rows = []
    lines = ["a 0.08 Hz power oscillation of 2 MW seen at three sampling intervals",
             "  interval s   apparent frequency Hz   largest swing seen MW"]
    for dt in (1.0, 10.0):
        ts = np.arange(0, 600, dt)
        xs = 2.0 * np.sin(2 * np.pi * f_osc * ts)
        fs = 1 / dt
        alias = abs(f_osc - round(f_osc / fs) * fs)
        lines.append(f"  {dt:10.0f}   {alias:21.3f}   {np.ptp(xs):21.2f}")
        if dt == 10.0:
            rows = [(round(float(a), 1), round(float(b), 3)) for a, b in zip(ts, xs)]
    th = np.arange(0, 3600, 0.1)                   # an hour, six 10-minute averages
    avg = 2.0 * np.sin(2 * np.pi * f_osc * th).reshape(6, -1).mean(axis=1)
    lines.append(f"  {'10-min avg':>10s}   {'none':>21s}   {np.ptp(avg):21.2f}")
    csv("ch35-alias.csv", "t,x", rows)
    csv("ch35-alias-true.csv", "t,x", [(round(float(a), 1), round(float(b), 3))
                                       for a, b in zip(t[::10], x[::10])])
    lines += ["  at 1 s the oscillation is seen as it is; at 10 s it shows",
              "  up as a slow wave of the wrong frequency (aliasing); in a",
              "  10-minute average it is gone. The sampling of each point",
              "  is chosen from the fastest thing it must show - at least",
              "  two samples a period, better ten - and a phenomenon",
              "  faster than SCADA sampling belongs to a recorder (ch 27)"]
    emit("q_alias", lines)


PLAN = [  # device, address (synthetic extract with planted errors)
    ("IED-E1-1", "10.35.1.11"), ("IED-E1-2", "10.35.1.12"), ("IED-T1-1", "10.35.1.12"),
    ("WTG-T01", "10.35.2.21"), ("WTG-T02", "10.35.2.22"), ("PVI-B01-I1", "10.35.3.31"),
    ("BES-C01", "10.35.4.41"), ("BES-C02", "10.35.5.42"), ("HMI-1", "10.35.6.10")]
SUBNETS = {"IED": "10.35.1.0/26", "WTG": "10.35.2.0/26", "PVI": "10.35.3.0/26",
           "BES": "10.35.4.0/26", "HMI": "10.35.6.0/27"}


def address_plan() -> None:
    seen, issues = {}, []
    for dev, addr in PLAN:
        ip = ipaddress.ip_address(addr)
        net = ipaddress.ip_network(SUBNETS[dev.split("-")[0]])
        if ip not in net:
            issues.append(f"{dev}: {addr} outside its subnet {net}")
        if addr in seen:
            issues.append(f"{dev}: {addr} already used by {seen[addr]}")
        seen.setdefault(addr, dev)
    lines = ["the address plan checked by program (synthetic extract of 9)"]
    lines += [f"  {s}" for s in issues]
    lines += [f"  {len(issues)} findings in {len(PLAN)} rows",
              "  a duplicate address makes two devices answer by turns -",
              "  intermittent faults that look like a bad cable; an",
              "  address outside its subnet cannot be reached through the",
              "  zone rules at all. The plan is checked like the tag list",
              "  (lesson B), before any device is configured"]
    emit("q_ipplan", lines)


POINTS = [  # tag, unit, low, high, deadband, instrument uncertainty (same unit)
    ("PLP-E1-VT.Voltage", "kV", 0.0, 150.0, 0.5, 0.87),
    ("PLP-TRF-T1.OilTemp", "C", -20.0, 120.0, 0.5, 1.0),
    ("PLP-WTG-T01.ActivePower", "kW", -500.0, 5500.0, 10.0, 25.0),
    ("PLP-BES-C03.Soc", "%", 0.0, 100.0, 0.0, 2.0),
    ("PLP-MET-M1.Ghi", "W/m2", 0.0, 150.0, 5.0, 20.0)]
SIGNAL_UNITS = {"Voltage": "kV", "OilTemp": "C", "ActivePower": "MW", "Soc": "%", "Ghi": "W/m2"}


def point_list() -> None:
    issues = []
    for tag, unit, lo, hi, db, u in POINTS:
        sig = tag.split(".")[1]
        if SIGNAL_UNITS[sig] != unit:
            issues.append(f"{tag}: unit {unit}, the signal is in {SIGNAL_UNITS[sig]}")
        if db == 0:
            issues.append(f"{tag}: deadband 0 - every sample sent")
        if sig == "Ghi" and hi < 1400:
            issues.append(f"{tag}: range 0-{hi:.0f} cannot hold a clear-sky value")
    lines = ["the point list checked by program (synthetic extract of 5)"]
    lines += [f"  {s}" for s in issues]
    lines += [f"  {len(issues)} findings in {len(POINTS)} rows",
              "  each check is one line of code and runs on every revision",
              "  of the list: units against the signal, a deadband near",
              "  the instrument's uncertainty, a range that holds the",
              "  largest real value - the kW/MW error of lab D is caught",
              "  here, before the gateway is configured"]
    emit("q_points", lines)


def rbe_staleness(seed: int = 361) -> None:
    rng = np.random.default_rng(seed)
    n_pts = 1000
    # hours between changes of a quiet point (state, setting, slow temperature)
    gaps_min = rng.exponential(40, n_pts)
    lines = ["staleness of points that send only on change (synthetic, 1,000 points)",
             "  integrity scan every 15 min; stale limit   points flagged stale"]
    for limit in (10, 20, 60):
        age = np.minimum(gaps_min, 15.0)          # the integrity scan refreshes them
        flagged = int(np.sum(age > limit))
        lines.append(f"  {limit:3d} min{'':35s}{flagged:6d}")
    lines += ["  with report-by-exception a quiet value is old but true;",
              "  the integrity scan refreshes it, so the stale limit is",
              "  set above the scan period - a limit below it flags",
              "  hundreds of healthy points (lab D used 10 s because its",
              "  synthetic points were sent every second)"]
    emit("q_rbe", lines)


def wan_budget() -> None:
    points, per_s, bytes_pt = 60, 1 / 4, 25       # every 4 s, with overhead
    link = 64e3
    steady = points * per_s * bytes_pt * 8
    gi = 300 * bytes_pt * 8                       # all 300 listed objects once an hour
    lines = ["telemetry to the grid operator on a 64 kbit/s link (placeholder list)",
             f"  60 points every 4 s, 25 bytes each: {steady / 1e3:.1f} kbit/s,"
             f" {steady / link * 100:.1f} % of the link",
             f"  general interrogation of 300 objects: {gi / 1e3:.0f} kbit, {gi / link:.1f} s"
             " on the link",
             "  the grid operator's list, rates and link are theirs to set",
             "  (U-115); the budget shows the list fits with room for",
             "  the interrogation after a restart and for set points"]
    emit("q_wan", lines)


def disks() -> None:
    need_tb = 12.2
    mirror, headroom = 2, 0.30
    raw = need_tb * mirror / (1 - headroom)
    lines = ["historian disks for the plant's life (teaching)",
             f"  data over 25 years: {need_tb} TB (lesson C)",
             f"  mirrored, with {headroom * 100:.0f} % free space kept: {raw:.1f} TB raw",
             "  plus an off-site copy of the aggregates, refreshed weekly",
             "  disks fail and age faster than the plant: the plan buys",
             "  for five years at a time and migrates the archive - a",
             "  migration is tested by reading old data back"]
    emit("q_disks", lines)


def acceptance_sample() -> None:
    lines = ["how many network points to test, accepting on zero faults (95 %)",
             "  fault rate to detect   sample size"]
    for p in (0.01, 0.005, 0.001):
        n = math.ceil(math.log(0.05) / math.log(1 - p))
        lines.append(f"  {p * 100:18.1f} %   {n:11,d}")
    lines += ["  a sample of about 300 shows, with 95 % confidence, that",
              "  fewer than 1 % of the 22,000 network points are wrong if",
              "  it finds none; lesson C's 2,200 detects 0.14 %. Every",
              "  hard-wired point and every point used by control,",
              "  protection or the grid operator is tested in full"]
    emit("q_sample", lines)


if __name__ == "__main__":
    aliasing()
    address_plan()
    point_list()
    rbe_staleness()
    wan_budget()
    disks()
    acceptance_sample()
