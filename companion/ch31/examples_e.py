"""Chapter 31, lesson E: export-system logistics - cable drums for the
33 kV collectors, conductor reels and stringing sections for the 132 kV
line, stringing weather, the substation's delivery sequence, and the
work packages with the people who approve them.

Run from the project root:   python -m companion.ch31.examples_e
Writes companion/ch31/expected/e_*.txt. Teaching values (A-366, A-367).
"""
from __future__ import annotations

import math

from companion.ch31.common import emit
from plantp import datapack
from plantp import logistics as lg


def drums() -> None:
    route_km = 60.0                     # collector trenches (ch 29 spoil lesson)
    cable_km = 3 * route_km * 1.03      # single cores in trefoil, 3 % allowance
    per_drum, kg_m, drum_t = 1.0, 4.2, 1.3
    n = math.ceil(cable_km / per_drum)
    mass = n * (per_drum * 1000 * kg_m / 1000 + drum_t)
    trucks = math.ceil(n / 3)
    lines = ["33 kV collector cable on drums (teaching: 1 km of single core a drum)",
             f"  cable {cable_km:.0f} km -> {n} drums of {per_drum * kg_m + drum_t:.1f} t,"
             f" {mass:,.0f} t in all; {trucks} truck loads of three",
             f"  laydown for the drums: {lg.laydown_area([3.0 * 2.6] * n):,.0f} m2",
             "  drums travel on their sides only if the maker allows it,",
             "  are rolled in the arrow's direction, and are stored on",
             "  firm ground with chocks; each drum's number ties to its",
             "  test report and to the section it is laid in (ch 24)"]
    emit("e_drums", lines)


def reels() -> None:
    line_km, phases = 7.06, 3
    cond_km = line_km * phases * 1.03
    reel_km, kg_m = 2.5, 1.1
    n = math.ceil(cond_km / reel_km) + math.ceil(line_km * 1.03 / reel_km)
    sections = 5
    lines = ["132 kV conductor and stringing (teaching; route of ch 29)",
             f"  conductor {cond_km:.1f} km + earth wire: {n} reels of about"
             f" {reel_km * kg_m:.1f} t",
             f"  stringing sections between angle and terminal towers: {sections}",
             f"  puller and tensioner sites: {2 * sections} (one at each section end)",
             "  each site needs a level pad, access for a low-loader and",
             "  anchors; the site track crossing needs a guard structure",
             "  so a dropped conductor never reaches the track"]
    emit("e_reels", lines)


def stringing_weather() -> None:
    v = datapack.load_hourly()["ws_60m_ms"].to_numpy() * (20 / 60) ** 0.14
    lim, hrs = 10.0, 8
    lines = ["stringing weather (wind at 20 m from the data pack; teaching limit",
             f"  {lim:.0f} m/s for {hrs} h)",
             f"  {lg.weather_windows(v, lim, hrs)} windows of {hrs} h a year at any hour"
             " (daylight work keeps about half)",
             "  stringing is rarely stopped by wind on this plain; heat",
             "  is the limit in summer (work hours, crew welfare, ch 32)",
             "  and the conductor's sag is set to the temperature on the",
             "  day with the line designer's sag tables (ch 24)"]
    emit("e_stringing", lines)


def substation() -> None:
    steps = [("civil works, plinths and bunds accepted (ch 29)", "H"),
             ("earthing grid installed and tested (ch 26)", "H"),
             ("main transformer delivered, impact recorder read", "H"),
             ("transformer jacked and skidded onto the plinth", "W"),
             ("bushings, radiators, conservator fitted", "W"),
             ("oil filled under vacuum, samples taken", "H"),
             ("switchgear and gantries erected", "W"),
             ("cable terminations by qualified jointers", "H"),
             ("handover to testing and commissioning (ch 50)", "H")]
    lines = ["substation delivery and installation sequence (teaching)"]
    for k, (s, t) in enumerate(steps, 1):
        lines.append(f"  {k}. [{t}] {s}")
    lines += ["  the transformer arrives without oil (72 t, ch 25) and is",
              "  skidded rather than lifted when a crane cannot reach;",
              "  each step is a work package with its own approval"]
    emit("e_substation", lines)


def packages() -> None:
    rows = [("cable laying and jointing", "cable maker's procedure", "qualified jointer, QC"),
            ("road and track crossings", "authority's permit", "road authority"),
            ("line stringing", "line designer's method", "line owner / operator"),
            ("transformer installation", "maker's instruction", "maker's supervisor"),
            ("work near energised parts", "permit-to-work system", "authorised person (ch 32)")]
    lines = ["export-system work packages and who approves them"]
    for wp, basis, who in rows:
        lines.append(f"  {wp}")
        lines.append(f"      basis: {basis}; approved by {who}")
    lines += ["  the logistics plan sequences them; it does not replace",
              "  any of their approvals"]
    emit("e_packages", lines)


if __name__ == "__main__":
    drums()
    reels()
    stringing_weather()
    substation()
    packages()
