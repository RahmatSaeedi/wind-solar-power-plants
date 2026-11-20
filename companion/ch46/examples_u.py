"""Chapter 46, round u: the joints an as-laid length forces, bending space
in the cable compartment, the time a relay added at the FAT puts into the
trip path, the retest set after FAT fixes, which temperature corrects a
drum reading, and the voltage profile of string WS1 (plot data).

Run from the project root:   python -m companion.ch46.examples_u
Writes companion/ch46/expected/u_*.txt and diagrams/data/ch46-profile.csv.
Teaching values (A-483 to A-488); no test procedure, no live work.
"""
from __future__ import annotations

import math

from companion.ch24 import sources as s24
from companion.ch46 import sources as src
from companion.ch46.common import csv, emit
from plantp import cablemfg as km
from plantp import cables as cb


# ------------------------------------------------ 1. joints forced by as-laid
def joints() -> dict:
    planned = {"W001": 850, "W002": 970, "W003": 1090, "W004": 1210}
    laid = {"W001": 862, "W002": 1105, "W003": 1094, "W004": 1222}
    drum = {"W001": 1000, "W002": 1000, "W003": 1500, "W004": 1500}
    lines = ["string WS1: does each cable still fit its planned drum (plus 10 m",
             "  for the ends)?",
             "  cable   planned m   as laid m   drum m   drums   joints"]
    out = {}
    for c in planned:
        n = math.ceil((laid[c] + 10) / drum[c])
        out[c] = n - 1
        lines.append(f"  {c}    {planned[c]:9d}   {laid[c]:9d}   {drum[c]:6d}   "
                     f"{n:5d}   {n - 1:6d}")
    lines += ["  W003 and W004 were planned on 1,500 m drums and still fit;",
              "  W002 was planned on the 1,000 m drum D401 and",
              "  the wadi detour of 135 m now needs a joint or a longer drum",
              "  - a joint is a weak point for 30 years, so the cable is",
              "  re-ordered on a 1,500 m drum if the date allows (ch 24)"]
    emit("u_joints", lines)
    return out


# ------------------------------------------------ 2. bending space
OD = {240: 92.0, 400: 106.0, 630: 120.0}       # mm, three-core, teaching
DEPTH = 1300.0                                  # mm, cable compartment, teaching


def bending(factor: float = 12.0) -> dict:
    lines = [f"bending space in the cable compartment (teaching: radius >= "
             f"{factor:.0f} x OD;", f"  {DEPTH:.0f} mm from the floor plate to "
             "the connector)",
             "  size mm2   OD mm   radius mm   fits"]
    out = {}
    for a, d in OD.items():
        r = factor * d
        ok = r <= DEPTH
        out[a] = (r, ok)
        lines.append(f"  {a:8d}   {d:5.0f}   {r:9.0f}   {'yes' if ok else 'NO'}")
    lines += ["  the 630 mm2 cable of WS1-WS3 needs 1,440 mm and the",
              "  compartment gives 1,300: the cable would be forced into a",
              "  tighter bend than its maker allows, straining the",
              "  termination; a deeper cable trench under the panel or a",
              "  cable cellar is a civil interface (ch 29), found from the",
              "  cable data and the panel drawing, not on the day of pulling"]
    emit("u_bending", lines)
    return out


# ------------------------------------------------ 3. trip-path time
def trip_time(relay_ms: float = 30.0, k5_ms: float = 12.0, cb_ms: float = 32.6,
              margin_s: float = 0.31, need_s: float = 0.30) -> dict:
    before = relay_ms + cb_ms
    after = before + k5_ms
    left = margin_s - k5_ms / 1000
    lines = ["trip path of WS1 before and after the interposing relay K5 (FAT",
             "  change C-04), milliseconds (teaching)",
             f"  relay output {relay_ms:.0f} + breaker opening {cb_ms:.1f} = "
             f"{before:.1f} ms",
             f"  with K5 in the path: + {k5_ms:.0f} ms = {after:.1f} ms",
             f"  a grading margin as tight as ch 26's tightest ({margin_s:.2f} s) "
             f"would keep {left:.3f} s,",
             f"  below the {need_s:.2f} s the coordination study assumed",
             "  a relay added at the FAT changes the clearing time of every",
             "  trip through it: the change goes back to the protection",
             "  engineer, the margins are re-checked with the new time, and",
             "  the opening time used is the measured one (lesson B)"]
    emit("u_trip", lines)
    return dict(before=before, after=after, left=left)


# ------------------------------------------------ 4. retest set
AFFECTS = {   # FAT change -> functions whose tests must be repeated
    "C-01 trip coils rewired": ["trip coil 1", "trip coil 2",
                                "trip-circuit supervision"],
    "C-02 X1:3/X1:4 rewired": ["CT circuit L2", "CT circuit L3", "51N stability"],
    "C-03 link X4:3-X4:4 removed": ["Q8 position indication",
                                    "Q2 position indication", "interlock Q2/Q8"],
    "C-04 K5 added": ["intertrip send", "trip coil 1", "trip coil 2",
                      "trip time"],
    "C-05 CT of PVF3 replaced": ["CT ratio PVF3", "CT polarity PVF3", "51 PVF3"],
}


def retest() -> dict:
    tests = sorted({t for v in AFFECTS.values() for t in v})
    twice = sorted({t for t in tests if sum(t in v for v in AFFECTS.values()) > 1})
    lines = [f"{len(AFFECTS)} FAT changes and the tests they reopen"]
    for c, v in AFFECTS.items():
        lines.append(f"  {c}: {', '.join(v)}")
    lines += [f"  {len(tests)} tests to repeat; reopened by two changes: "
              f"{', '.join(twice)}",
              "  a fix makes the earlier result void for everything it",
              "  touched: the retest set comes from the change, not from",
              "  the tester's memory, and the repeated results replace the",
              "  old ones in the FAT record"]
    emit("u_retest", lines)
    return dict(n=len(tests), twice=twice)


# ------------------------------------------------ 5. which temperature?
def drum_temp() -> dict:
    d, l, r, t_air = src.DRUMS[0]
    lines = [f"drum {d}: {r} ohm read with the air at {t_air:.0f} C;",
             "  the conductor inside may differ",
             "  conductor C   ohm/km at 20 C   verdict"]
    out = {}
    for t in (t_air, 22.0, 20.0, 18.0):
        r20 = km.r_to_20(r, t) / (l / 1000)
        ok = r20 <= src.R20_MAX
        out[t] = (r20, ok)
        lines.append(f"  {t:11.0f}   {r20:14.4f}   {'ok' if ok else 'REJECT'}")
    lines += ["  a drum brought from the cold yard in the morning and read at",
              "  noon has a core cooler than the air: the same reading passes",
              f"  at {t_air:.0f} C and fails at 22 C - the drum rests indoors long enough",
              "  for the core to reach the room, and the record says so"]
    emit("u_drumtemp", lines)
    return out


# ------------------------------------------------ 6. voltage profile (plot data)
def profile(p_mw: float = 5.0, kv: float = 33.0, pf: float = 0.95,
            theta: float = 70.0) -> list:
    segs = [(630, 850), (400, 970), (240, 1090), (240, 1210)]
    i_t = p_mw * 1e6 / (math.sqrt(3) * kv * 1e3 * pf)
    x, drop, rows = 0.0, 0.0, [(0.0, 0.0)]
    for k, (a, l) in enumerate(segs):
        c = s24.MV_CABLES[a]
        r = cb.r_at(c["r20"], theta, 0.00403)
        drop += cb.drop_pct((4 - k) * i_t, l / 1000, r, c["x"], pf, kv)
        x += l
        rows.append((round(x / 1000, 3), round(drop, 4)))
    csv("ch46-profile.csv", "km,drop", rows)
    return rows


if __name__ == "__main__":
    joints()
    bending()
    trip_time()
    retest()
    drum_temp()
    profile()
