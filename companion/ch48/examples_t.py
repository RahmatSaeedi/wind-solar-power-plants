"""Chapter 48, round t: an anemometer calibration carried to the energy
estimate, main and check meters compared, loops crossing between earthing
systems, a fibre bend found by two wavelengths, a switch's PoE budget,
configuration items a hardening review reads, devices' time sources,
alarm tests end to end, point names, and the physical and logical views
checked against each other.

Run from the project root:   python -m companion.ch48.examples_t
Writes companion/ch48/expected/t_*.txt and diagrams/data/ch48-*.csv.
Teaching values (A-498 to A-505); defensive administration only.
"""
from __future__ import annotations

import re

import numpy as np

from companion.ch48.common import csv, emit
from plantp import cablemfg as km


# ------------------------------------------------ 1. anemometer calibration
def anemometer(slope: float = 1.012, offset: float = 0.08, v_mean: float = 7.4,
               sens: float = 1.82) -> dict:
    """The tunnel says the cup reads true = slope x reading + offset; a mast
    that used the default transfer function under-reads by this much."""
    true = slope * v_mean + offset
    bias = true / v_mean - 1
    lines = [f"cup anemometer: tunnel calibration true = {slope} x reading + {offset} "
             "m/s,",
             "  against the maker's default (true = reading)",
             f"  at the mast's mean {v_mean} m/s the default under-reads by "
             f"{bias:.1%}",
             f"  with ch 16's energy sensitivity of {sens}, the farm's energy is",
             f"  underestimated by about {bias * sens:.1%} - a calibration that",
             f"  moves the P50 by {bias * sens:.0%} is worth its certificate; the",
             "  individual calibration, not the type's default, goes into ch 13"]
    emit("t_anemometer", lines)
    return dict(bias=bias, energy=bias * sens)


# ------------------------------------------------ 2. main and check meter
def check_meter(seed: int = 4801, days: int = 60, drift_from: int = 30,
                drift: float = 0.012, limit: float = 0.3) -> dict:
    rng = np.random.default_rng(seed)
    diff = [rng.normal(0.02, 0.03) + (drift * (d - drift_from) if d >= drift_from else 0)
            for d in range(days)]
    csv("ch48-meters.csv", "day,diff", [(d, round(x, 3)) for d, x in enumerate(diff)])
    b0, _ = km.trend(list(range(drift_from)), diff[:drift_from])
    b1, se1 = km.trend(list(range(drift_from, days)), diff[drift_from:])
    first = next((d for d, x in enumerate(diff) if abs(x) > limit), None)
    seen = None
    for k in range(drift_from + 5, days + 1):
        b, se = km.trend(list(range(drift_from, k)), diff[drift_from:k])
        if b > 2 * se:
            seen = k - 1
            break
    lines = ["main against check meter at the POC: daily difference in %",
             f"  ({days} days, synthetic)",
             f"  days 0-{drift_from - 1}: slope {b0:+.4f} % a day (no trend)",
             f"  days {drift_from}-{days - 1}: slope {b1:+.4f} +/- {2 * se1:.4f} % a day",
             f"  the trend is significant by day {seen}; the difference first",
             f"  passes {limit} % on day {first}",
             "  the trend shows a meter drifting weeks before the limit is",
             "  crossed; which meter drifts is found by the site test of",
             "  both - the check meter exists to make this comparison"]
    emit("t_meters", lines)
    return dict(b1=b1, first=first, seen=seen)


# ------------------------------------------------ 3. loops between earthing systems
LOOPS_X = [   # loop, from (earthing system), to, isolator
    ("L-101", "met mast", "MET-1", False), ("L-102", "MET-1", "SUB-RTU", True),
    ("L-103", "WTG-T05 tower", "WTG-T05 base", False),
    ("L-104", "PV-B07", "SUB-RTU", False), ("L-105", "BESS-C3", "SUB-RTU", True),
]
SAME = {frozenset(("met mast", "MET-1")), frozenset(("WTG-T05 tower", "WTG-T05 base"))}


def isolation() -> list:
    bad = [l for l, a, b, iso in LOOPS_X if frozenset((a, b)) not in SAME and not iso]
    lines = ["4-20 mA loops that cross from one earthing system to another"]
    for l, a, b, iso in LOOPS_X:
        cross = frozenset((a, b)) not in SAME
        lines.append(f"  {l}  {a:14s} -> {b:13s}  crosses: {'yes' if cross else 'no '}  "
                     f"isolator: {'yes' if iso else 'no'}")
    lines += [f"  crossing without an isolator: {', '.join(bad)}",
              "  in an earth fault the two earths can differ by hundreds of",
              "  volts for a moment: the loop carries it into the RTU's input",
              "  card - an isolator at the boundary, recorded in the loop",
              "  schedule (ch 26 earth potential rise, ch 34 earthing)"]
    emit("t_isolation", lines)
    return bad


# ------------------------------------------------ 4. a bend found by two wavelengths
EVENTS = [   # event, km, loss dB at 1310 nm, at 1550 nm
    ("connector", 0.00, 0.45, 0.42), ("splice", 0.18, 0.06, 0.05),
    ("splice", 0.41, 0.08, 0.07), ("event", 0.52, 0.12, 0.94),
    ("connector", 0.71, 0.48, 0.45),
]


def bend() -> dict:
    lines = ["link T05-T06 event table at two wavelengths (teaching)",
             "  event       km     1310 nm dB   1550 nm dB   reading"]
    found = []
    for e, k, a, b in EVENTS:
        r = "bend" if b > 2 * a and b > 0.3 else "-"
        if r == "bend":
            found.append(k)
        lines.append(f"  {e:10s} {k:4.2f}   {a:10.2f}   {b:10.2f}   {r}")
    lines += [f"  a bend at {found[0]:.2f} km: a splice loses about the same at both",
              "  wavelengths, a tight bend loses far more at 1550 nm - the",
              "  1.5 dB excess of lesson B is a cable squeezed in a tray, not",
              "  a dirty connector; cleaning would not have fixed it"]
    emit("t_bend", lines)
    return dict(km=found)


# ------------------------------------------------ 5. PoE budget
def poe(budget_w: float = 60.0) -> dict:
    loads = {"camera 1": 12.9, "camera 2": 12.9, "camera 3 (PTZ)": 25.5,
             "access point": 13.0, "camera 4": 12.9}
    tot = sum(loads.values())
    lines = [f"power over Ethernet on switch SW-FENCE: budget {budget_w:.0f} W",
             "  " + ", ".join(f"{k} {v} W" for k, v in list(loads.items())[:3]),
             "  " + ", ".join(f"{k} {v} W" for k, v in list(loads.items())[3:]),
             f"  total {tot:.1f} W: {'over' if tot > budget_w else 'inside'} the "
             f"budget by {abs(tot - budget_w):.1f} W",
             "  over budget, the switch refuses power to the last device to",
             "  start - after a power cut, a different camera each time; the",
             "  budget is summed from the devices' class, not their typical",
             "  draw, and checked when a device is added"]
    emit("t_poe", lines)
    return dict(tot=tot, over=tot > budget_w)


# ------------------------------------------------ 6. configuration hardening items
CONFIGS = {   # device: items read from its saved configuration file
    "SW-T05": dict(snmp_community="private-x91", telnet=False, unused_ports_shut=True,
                   ntp=["CLK-1", "CLK-2"]),
    "SW-T09": dict(snmp_community="public", telnet=False, unused_ports_shut=True,
                   ntp=["CLK-1", "CLK-2"]),
    "GW-PV1": dict(snmp_community="gw-7c2", telnet=True, unused_ports_shut=True,
                   ntp=["pool.example.net"]),
    "SW-SUB": dict(snmp_community="sub-55a", telnet=False, unused_ports_shut=False,
                   ntp=["CLK-1"]),
}


def hardening() -> list:
    out = []
    for d, c in CONFIGS.items():
        if c["snmp_community"] in ("public", "private"):
            out.append((d, "default SNMP community"))
        if c["telnet"]:
            out.append((d, "telnet enabled"))
        if not c["unused_ports_shut"]:
            out.append((d, "unused ports not shut"))
    lines = ["saved configurations read against the hardening checklist of ch 36"]
    lines += [f"  {d}: {x}" for d, x in out]
    lines += [f"  {len(out)} findings, all read from files the integrator handed",
              "  over - no probing of the network; each closes with a",
              "  changed configuration, a new backup and its fingerprint",
              "  (lesson C, ch 36 hardening)"]
    emit("t_hardening", lines)
    return out


# ------------------------------------------------ 7. time sources configured
def ntp() -> list:
    out = []
    for d, c in CONFIGS.items():
        srcs = c["ntp"]
        if any(not s.startswith("CLK-") for s in srcs):
            out.append((d, f"time from outside the plant: {', '.join(srcs)}"))
        elif len(srcs) < 2:
            out.append((d, "one time source only"))
    lines = ["time sources in each device's configuration (two plant clocks each)"]
    lines += [f"  {d}: {x}" for d, x in out]
    lines += ["  GW-PV1 asks an outside server the plant cannot reach - it",
              "  falls back to its own clock, the 15 ms of lesson C; SW-SUB",
              "  has no second source; both are configuration lines, found",
              "  in the files before the clocks drift (ch 35, ch 36)"]
    emit("t_ntp", lines)
    return out


# ------------------------------------------------ 8. alarm tests
ALARMS = {"critical": (42, 40), "high": (118, 109), "medium": (260, 201), "low": (190, 96)}


def alarm_tests() -> dict:
    lines = ["alarms raised and cleared end to end at the SAT, by priority",
             "  priority   alarms   tested   coverage"]
    for p, (n, t) in ALARMS.items():
        lines.append(f"  {p:8s}   {n:6d}   {t:6d}   {t / n:8.0%}")
    crit_left = ALARMS["critical"][0] - ALARMS["critical"][1]
    lines += [f"  {crit_left} critical alarms never seen at the console: those are",
              "  tested before handover whatever else waits; low-priority",
              "  alarms are sampled - testing is ordered by what an alarm",
              "  that fails to sound would cost (ch 35 alarms)"]
    emit("t_alarms", lines)
    return dict(crit_left=crit_left)


# ------------------------------------------------ 9. point names
NAME = re.compile(r"^[A-Z0-9]+(\.[A-Z0-9]+)+$")
NAMES = ["POC.P", "POC.Q", "MET1.GHI", "T05.P", "t05.ws", "PVF1 P", "BESS.SOC",
         "SUB.TX1.T", "BESS..T", "MET1.TAMB"]


def names() -> list:
    bad = [n for n in NAMES if not NAME.match(n)]
    lines = ["point names against the project's pattern (teaching: upper-case",
             "  parts joined by dots, no spaces)"]
    lines += [f"  bad: {n!r}" for n in bad]
    lines += ["  a lower-case copy of a name is a second point to a program",
              "  that compares text; a space breaks the historian's query",
              "  language; an empty part hides a missing level - names are",
              "  checked with the rest of the tag database (lab D)"]
    emit("t_names", lines)
    return bad


# ------------------------------------------------ 10. physical against logical
PHYS = {"T05-PLC": "SW-T05", "T05-CMS": "SW-T05", "T05-MET": "SW-T05",
        "T05-CCTV": "SW-T05", "RTU-1": "SUB-CORE", "GW-PV1": "SUB-CORE",
        "HMI-3": "SW-CTRL"}
LOGIC = {"T05-PLC": 20, "T05-CMS": 30, "T05-MET": 20, "T05-CCTV": 40, "RTU-1": 20,
         "GW-PV1": 20, "HIST-2": 20}


def views() -> dict:
    only_p = sorted(set(PHYS) - set(LOGIC))
    only_l = sorted(set(LOGIC) - set(PHYS))
    lines = ["the physical view against the logical view: is every device in both?",
             f"  in the physical view only: {', '.join(only_p)}",
             f"  in the logical view only:  {', '.join(only_l)}",
             "  HMI-3 is cabled but in no VLAN of the design - a screen that",
             "  works because the port is in a default VLAN; HIST-2 is in the",
             "  design but nowhere on a switch - a historian that was never",
             "  installed; two views that agree are the as-built record"]
    emit("t_views", lines)
    return dict(only_p=only_p, only_l=only_l)


if __name__ == "__main__":
    anemometer()
    check_meter()
    isolation()
    bend()
    poe()
    hardening()
    ntp()
    alarm_tests()
    names()
    views()
