"""Chapter 32, lesson K: more on managing risk and hazards - barriers
between a cause and a top event (a LOPA-style count), leading indicators,
lightning distance by flash-to-bang, respirable dust over a shift, the
lifting index of a PV module, and the hours the weather stops work at
height in the data-pack year.

Run from the project root:   python -m companion.ch32.examples_k
Writes companion/ch32/expected/k_*.txt and diagrams/data/ch32-barriers.csv.
Teaching values (A-371, A-372); the frequencies, barrier credits and
limits of a real analysis come from the project's study and local law.
"""
from __future__ import annotations

import math

from companion.ch32 import sources as src  # noqa: F401  (puts plantp on the path)
from companion.ch32.common import csv, emit
from plantp import datapack

# [start: barriers]
BARRIERS = [  # (barrier, PFD credit, independent?)
    ("cell monitoring and BMS limits", 0.1, True),
    ("rack fuse / contactor opens", 0.1, True),
    ("off-gas detection -> PCS stop", 0.1, True),
    ("explosion control (per product test)", 0.1, True),
    ("second BMS channel, same sensors", 0.1, False),
]
# [end: barriers]


def barriers() -> None:
    f0 = 0.02                          # initiating events a year per container (teaching)
    rows = []
    lines = ["barriers between a cell fault and a container explosion (teaching)",
             f"  initiating cell faults: {f0} a year per container",
             "  barrier                                  PFD    counted   frequency /yr"]
    f = f0
    for name, pfd, ind in BARRIERS:
        if ind:
            f *= pfd
        rows.append((name.split()[0], f))
        lines.append(f"  {name:38s}  {pfd:5.2f}   {'yes' if ind else 'no':7s}   {f:13.1e}")
    csv("ch32-barriers.csv", "barrier,freq", [(k + 1, f"{r[1]:.2e}") for k, r in enumerate(rows)])
    target = 1e-5
    lines += [f"  8 containers: {8 * f:.1e} a year against a teaching target {target:.0e}:",
              "  above it - the study asks for a further independent",
              "  barrier or a lower initiating rate (cell screening, ch 19);",
              "  the second BMS channel shares the first one's sensors, so",
              "  it is not an independent barrier and earns no credit;",
              "  one impaired barrier multiplies the frequency by ten -",
              "  which is why barrier health is tracked like any KPI"]
    emit("k_barriers", lines)


def leading() -> None:
    items = [("inspections done / planned", 46, 52, "88 %"),
             ("near misses reported per 100 workers a month", 9, 100, "9"),
             ("actions closed on time", 31, 40, "78 %"),
             ("permits audited, found correct", 18, 20, "90 %"),
             ("toolbox talks held / planned", 60, 60, "100 %"),
             ("impaired barriers today", 1, 12, "1 of 12")]
    lines = ["leading indicators for one month of construction (synthetic)",
             "  indicator                                        value"]
    for name, a, b, txt in items:
        lines.append(f"  {name:47s}  {txt}")
    lines += ["  lagging rates count harm after it happens; leading",
              "  indicators show whether the system works now - a fall in",
              "  near-miss reports is a warning (people stopped reporting),",
              "  not good news, until it is understood"]
    emit("k_leading", lines)


def lightning() -> None:
    lines = ["how far is the storm? flash-to-bang (sound 343 m/s)",
             "  seconds   distance km"]
    for s in (5, 10, 20, 30, 45):
        lines.append(f"  {s:7d}   {s * 0.343:11.1f}")
    lines += ["  under 30 s the storm is within about 10 km: work at height,",
              "  on the line and in open areas stops, and restarts 30",
              "  minutes after the last thunder; a lightning detector",
              "  with a warning radius replaces counting where fitted -",
              "  the site rule sets the distances (ch 26 for protection)"]
    emit("k_lightning", lines)


def dust() -> None:
    tasks = [("grading in the wind", 3.0, 3.0), ("driving the site roads", 1.2, 2.0),
             ("cab with filter, closed", 0.3, 2.0), ("office", 0.05, 1.0)]
    twa = sum(c * h for _, c, h in tasks) / 8
    lines = ["respirable dust over an 8-hour shift (teaching concentrations)",
             "  task                         mg/m3   hours"]
    for name, c, h in tasks:
        lines.append(f"  {name:28s} {c:6.2f}   {h:5.1f}")
    lines += [f"  time-weighted average: {twa:.2f} mg/m3",
              "  three hours of grading supply most of the dose; water",
              "  sprays, closed cabs and working upwind come before masks;",
              "  the limit, and whether silica needs its own, come from",
              "  local law and an occupational hygienist's sampling"]
    emit("k_dust", lines)


def lifting_index() -> None:
    lc = 23.0                                        # kg, load constant of the revised equation
    module = 32.0                                    # kg, one 2.28 x 1.13 m module (teaching)

    def rwl(h_cm, v_cm, d_cm, a_deg, fm, cm):
        hm = min(1.0, 25 / h_cm)
        vm = 1 - 0.003 * abs(v_cm - 75)
        dm = min(1.0, 0.82 + 4.5 / d_cm)
        am = 1 - 0.0032 * a_deg
        return lc * hm * vm * dm * am * fm * cm

    cases = [("one person, module from pallet to table", 50, 40, 100, 30, 0.85, 0.90, 1),
             ("two persons, same lift", 50, 40, 100, 30, 0.85, 0.90, 2),
             ("two, held close, pallet at 75 cm, no twist", 25, 75, 25, 0, 0.85, 0.90, 2)]
    lines = ["lifting index of a PV module (revised lifting equation, teaching)",
             f"  module {module:.0f} kg; load constant {lc:.0f} kg",
             "  case                                       RWL kg   load kg   index"]
    for name, h, v, d, a, fm, cm, people in cases:
        r = rwl(h, v, d, a, fm, cm)
        load = module / people
        lines.append(f"  {name:42s} {r:6.1f}   {load:7.1f}   {load / r:5.2f}")
    lines += ["  one person carrying a module from a low pallet is far",
              "  above 1; two people halve it but stay above 1; holding",
              "  it close, raising the pallet and cutting the twist bring",
              "  it under 1 - the layout of the work, not the strength",
              "  of the worker, is the control (modules crack if bent)"]
    emit("k_lifting", lines)


def weather_stop() -> None:
    d = datapack.load_hourly()
    v = d["ws_100m_ms"].to_numpy()
    t = d["t_air_c"].to_numpy()
    h = d.index.hour.to_numpy()
    day = (h >= 6) & (h < 18)
    months = d.index.month.to_numpy()
    csv("ch32-weather.csv", "month,wind,heat",
        [(m, int(((v > 12) & day & (months == m)).sum()), int(((t >= 35) & day & (months == m)).sum()))
         for m in range(1, 13)])
    lines = ["daytime hours that stop work at height (data-pack year, 06-18 h)",
             f"  daytime hours in the year: {int(day.sum()):,}",
             "  rule (teaching)                                hours   share"]
    for name, mask in [("hub wind above 12 m/s (no climbing)", v > 12),
                       ("hub wind above 15 m/s (leave the nacelle)", v > 15),
                       ("air 35 C or more (heavy work moved)", t >= 35)]:
        n = int((mask & day).sum())
        lines.append(f"  {name:45s} {n:5d}   {n / day.sum() * 100:4.1f} %")
    lines += ["  wind stops climbing on about 7 % of working hours, heat",
              "  moves heavy work on about 5 %; the maker's limits for the",
              "  service lift, the hub and the roof hatch, and the site's",
              "  heat rule, set the real thresholds"]
    emit("k_weather", lines)


if __name__ == "__main__":
    barriers()
    leading()
    lightning()
    dust()
    lifting_index()
    weather_stop()
