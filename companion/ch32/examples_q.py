"""Chapter 32, lesson Q: more on people and emergencies - how far a
defibrillator may be from a collapse, how far a site radio reaches, the
time to descend from a nacelle, pedestrian risk against vehicle speed,
and the hours the wind carries site dust toward the village.

Run from the project root:   python -m companion.ch32.examples_q
Writes companion/ch32/expected/q_*.txt and diagrams/data/ch32-aed.csv.
Teaching values (A-374, A-375); medical, radio and road-safety planning
belong to their specialists and local rules.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch32 import sources as src  # noqa: F401  (puts plantp on the path)
from companion.ch32.common import csv, emit
from plantp import datapack


def aed() -> None:
    rows = []
    lines = ["a defibrillator's distance and the time to the first shock (teaching)",
             "  survival of a cardiac arrest falls about 10 % a minute without",
             "  a shock (a common rule of thumb; the medical provider decides)",
             "  AED walk m (each way)   minutes to shock   survival relative to 1 min"]
    for d in (50, 150, 300, 800, 2000):
        t = 1.0 + 2 * d / 80 / 1.0 + 1.0                  # notice + fetch at 80 m/min + set up
        s = max(0.0, 1 - 0.1 * (t - 1))
        rows.append((d, round(t, 1), round(s, 2)))
        lines.append(f"  {d:21d}   {t:16.1f}   {s:26.2f}")
    csv("ch32-aed.csv", "d,t,s", rows)
    lines += ["  an AED in the welfare cabin is minutes away from a PV",
              "  block: AEDs go in every site vehicle and at each work",
              "  front, with trained first aiders (lesson G), so the",
              "  first shock comes before the ambulance (lab H)"]
    emit("q_aed", lines)


def radio_range() -> None:
    lines = ["line-of-sight radio range: d = 3.57 (sqrt h1 + sqrt h2) km",
             "  antenna 1 m   antenna 2 m   range km"]
    for h1, h2 in [(1.5, 1.5), (1.5, 10.0), (1.5, 30.0), (100.0, 1.5)]:
        lines.append(f"  {h1:11.1f}   {h2:11.1f}   {3.57 * (math.sqrt(h1) + math.sqrt(h2)):8.1f}")
    lines += ["  two hand-held radios see about 9 km over flat ground, but a",
              "  ridge or the hollow at T07-T08 blocks them: a repeater on",
              "  a mast or on the substation's tower extends the reach,",
              "  and a nacelle at 100 m sees across the whole site - the",
              "  survey of lab H checks each pad, not the formula"]
    emit("q_radio", lines)


def descent() -> None:
    h = 100.0
    lines = ["evacuating a nacelle with a descent device (teaching)",
             "  people   set-up min   descent m/s   total min"]
    for n in (1, 2, 3):
        t = 3.0 + n * (h / 0.9 / 60 + 1.0)
        lines.append(f"  {n:6d}   {3.0:10.1f}   {0.9:11.1f}   {t:9.1f}")
    lines += ["  self-evacuation of a two-person crew takes under ten",
              "  minutes - far quicker than any outside help (lab H), if",
              "  the device is in the nacelle, inspected, and both people",
              "  have practised with it; the maker's device and the site's",
              "  rescue plan decide"]
    emit("q_descent", lines)


def pedestrian() -> None:
    lines = ["pedestrian fatality risk against impact speed (teaching curve)",
             "  P = 1 / (1 + exp(-(v - 50) / 7)), v in km/h (illustrative)",
             "  speed km/h   risk"]
    for v in (20, 30, 40, 50, 60, 70):
        p = 1 / (1 + math.exp(-(v - 50) / 7))
        lines.append(f"  {v:10d}   {p * 100:3.0f} %")
    lines += ["  the risk climbs steeply between 30 and 60 km/h: a village",
              "  speed limit of 30 for site traffic and a marshal at the",
              "  school crossing (lesson G) do more than any sign; the",
              "  real curve and limits come from road-safety authorities"]
    emit("q_pedestrian", lines)


def dust_toward_village() -> None:
    d = datapack.load_hourly()
    wd = d["wd_100m_deg"].to_numpy()
    ws = d["ws_100m_ms"].to_numpy()
    h = d.index.hour.to_numpy()
    work = (h >= 6) & (h < 18)
    toward = ((wd >= 135) & (wd <= 225))              # village north of the PV block (ch 14)
    windy = ws > 8.0
    n = int((work & toward & windy).sum())
    lines = ["working hours when strong wind blows site dust toward the village",
             "  village 3 km north of the PV block (ch 14): wind from 135-225 deg",
             f"  working hours (06-18 h): {int(work.sum()):,}",
             f"  wind from that sector: {int((work & toward).sum()):,}",
             f"  ... and above 8 m/s at 100 m: {n} ({n / work.sum() * 100:.1f} %)",
             "  the prevailing wind blows away from the village; in the few",
             "  hours it does not, grading and haul near the village stop",
             "  or get extra water - a wind-direction rule set with the",
             "  community and the dust plan (ch 29) costs about 1 % of",
             "  working time and removes a cause of lesson G's complaints"]
    emit("q_dust", lines)


if __name__ == "__main__":
    aed()
    radio_range()
    descent()
    pedestrian()
    dust_toward_village()
