"""Chapter 31, lesson B: lift planning governance - capacity read from
the crane's chart and utilisation, lift classification and who approves,
the crawler tracks on the crane pad, wind on the suspended load, and
weather windows from the data-pack year.

Run from the project root:   python -m companion.ch31.examples_b
Writes companion/ch31/expected/b_*.txt and diagrams/data/ch31-*.csv.
Teaching values (A-365); an approved lift plan uses the crane's own
charts, the maker's instructions and the lift engineer's review.
"""
from __future__ import annotations

import numpy as np

from companion.ch31 import sources as src
from companion.ch31.common import csv, emit
from plantp import datapack
from plantp import logistics as lg

LIFTS = [   # lift, load t, rigging t, radius m, tandem, near live parts
    ("tower section 1", 124.0, 6.0, 14.0, True, False),
    ("tower section 4", 50.0, 4.0, 18.0, False, False),
    ("nacelle", 160.0, 8.0, 16.0, False, False),
    ("rotor (hub + blades)", 111.0, 9.0, 20.0, True, False),
    ("main transformer onto plinth", 72.0, 6.0, 12.0, False, True)]


def utilisation() -> None:
    lines = ["lifts against the teaching load chart (capacity at 112 m hook height)",
             "  lift                          load+rig t   radius m   capacity t   use"]
    rows = []
    for name, m, rig, r, *_ in LIFTS:
        cap = lg.chart_capacity(r, src.CRANE_CHART)
        u = lg.lift_utilisation(m, rig, r, src.CRANE_CHART)
        rows.append((name, u))
        lines.append(f"  {name:29s} {m + rig:10.0f}   {r:8.0f}   {cap:10.0f}   {u:4.2f}")
    csv("ch31-chart.csv", "r,c", src.CRANE_CHART)
    lines += ["  the nacelle uses four fifths of the crane at 16 m: a",
              "  metre more radius takes capacity away fast - the radius",
              "  is fixed by the crane's position on the pad, which is",
              "  why the pad and the crane's set-up are surveyed"]
    emit("b_chart", lines)


def classify() -> None:
    lines = ["lift classification (teaching rules: critical if use > 0.8, tandem,",
             "  or near live parts; complex if use > 0.6; otherwise routine)",
             "  lift                          use    class      approved by"]
    for name, m, rig, r, tandem, live in LIFTS:
        u = lg.lift_utilisation(m, rig, r, src.CRANE_CHART)
        cls = "critical" if (u > 0.8 or tandem or live) else "complex" if u > 0.6 else "routine"
        who = {"critical": "lift engineer + site manager",
               "complex": "appointed person (lifts)", "routine": "crane supervisor"}[cls]
        lines.append(f"  {name:29s} {u:4.2f}   {cls:9s}  {who}")
    lines += ["  the class decides who writes and who signs the lift plan;",
              "  a tandem lift or a lift near live equipment is critical",
              "  whatever its utilisation - the rules are the project's",
              "  lifting procedure, not this table"]
    emit("b_classify", lines)


def tracks() -> None:
    crane, counter, load = 600.0, 250.0, 168.0
    area = 2 * 1.5 * 12.0
    avg = (crane + counter + load) * 9.81 / area
    peak = 2.0 * avg
    lines = ["the crawler crane on its pad (teaching masses; two tracks 1.5 x 12 m)",
             f"  crane {crane:.0f} t, counterweight {counter:.0f} t, nacelle with rigging"
             f" {load:.0f} t",
             f"  average track pressure {avg:.0f} kPa; under the loaded track edge"
             f" about {peak:.0f} kPa",
             "  timber or steel mats spread the edge pressure; the pad",
             "  (ch 29) was checked for one outrigger load - the crawler",
             "  case is checked again with the crane maker's ground-",
             "  bearing data and the pad's tested bearing (ch 30, ch 29)"]
    emit("b_tracks", lines)


def wind_load() -> None:
    items = [("nacelle (side)", 14.0 * 4.3), ("rotor in its plane", 3 * 74 * 2.5),
             ("tower section", 25.0 * 4.5)]
    lines = ["wind force on the suspended load (Cd 1.2; teaching areas)",
             "  load                     area m2    6 m/s    8 m/s    10 m/s   12 m/s  (kN)"]
    for name, a in items:
        f = [lg.wind_on_load(v, a) / 1e3 for v in (6, 8, 10, 12)]
        lines.append(f"  {name:24s} {a:7.0f}   " + "   ".join(f"{x:6.1f}" for x in f))
    lines += ["  the rotor is a sail: at 8 m/s it is pushed about twice as",
              "  hard as a tower section in a 12 m/s wind -",
              "  hence the low wind limits for rotor and blade lifts and",
              "  the tag lines that keep the load from turning"]
    emit("b_wind", lines)


def longest_wait(v, limit: float, hours: int) -> int:
    """Longest stretch (h) in which no run of `hours` calm hours ends."""
    run, last, worst = 0, 0, 0
    for k, x in enumerate(v):
        run = run + 1 if x < limit else 0
        if run >= hours:
            worst = max(worst, k - last)
            last = k
    return max(worst, len(v) - 1 - last)


def windows() -> None:
    v = datapack.load_hourly()["ws_100m_ms"].to_numpy()
    months = np.repeat(np.arange(12), [744, 672, 744, 720, 744, 720, 744, 744, 720, 744, 720, 744])
    lines = ["weather windows in the data-pack year (hub-height wind; teaching limits)",
             "  lift                  limit  hours  windows/yr  worst month  longest wait h"]
    rows = []
    for name, (lim, hrs) in src.WIND_LIMITS.items():
        per_m = [lg.weather_windows(v[months == k], lim, hrs) for k in range(12)]
        total = lg.weather_windows(v, lim, hrs)
        worst = int(np.argmin(per_m)) + 1
        rows.append((name.split()[0], *per_m))
        lines.append(f"  {name:21s} {lim:5.0f}  {hrs:5d}  {total:10d}  {worst:5d} ({min(per_m):3d})"
                     f"  {longest_wait(v, lim, hrs):14d}")
    csv("ch31-windows.csv", "m,tower,nacelle,rotor,blade",
        [(k + 1, *(r[k + 1] for r in rows)) for k in range(12)])
    lines += ["  even the worst month has dozens of windows; what costs",
              "  money is the wait - the rotor lift can stand idle for",
              "  nine days (214 h) when a windy spell sets in: erection is planned",
              "  around the season, and a waiting crane costs every day",
              "  it stands (lab D)"]
    emit("b_windows", lines)


if __name__ == "__main__":
    utilisation()
    classify()
    tracks()
    wind_load()
    windows()
