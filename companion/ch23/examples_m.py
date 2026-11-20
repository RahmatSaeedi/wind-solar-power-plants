"""Chapter 23 - more lessons: line and phase voltages of each level, the
earth of the 33 kV system behind delta windings, the structure of a
reference designation, lighting and drainage loads from first
principles, an LV feeder's voltage drop, the DC battery's replacement
interval with temperature, and the two connection alternatives.

Run from the project root:   python -m companion.ch23.examples_m
Writes companion/ch23/expected/m_*.txt. Teaching values A-316 to A-320.
"""
from __future__ import annotations

import math

from companion.ch18 import sources as s18
from companion.ch23 import sources as src
from companion.ch23.common import emit


def phases() -> None:
    lines = ["line and phase voltages of Plant P's levels (star equivalent):",
             "  level              line kV    phase kV   drawn as"]
    for name, kv in [("LV board", 0.4), ("PV inverter", 0.6), ("turbine, battery", 0.69),
                     ("collector", 33.0), ("export", 132.0)]:
        lines.append(f"  {name:18s} {kv:8.2f}  {kv / math.sqrt(3):9.3f}   one line")
    lines += ["  a balanced three-phase circuit is drawn as one line: the",
              "  other two phases are the same shifted by 120 degrees, so",
              "  P = sqrt 3 U I cos phi holds for the line the drawing shows;",
              "  the earthing, the neutral and anything unbalanced are drawn",
              "  explicitly"]
    emit("m_phases", lines)


# [start: earthing]
def earthing(limit_a: float = 400.0) -> None:
    u_ph = 33e3 / math.sqrt(3)
    r = u_ph / limit_a
    p = u_ph * limit_a / 1e3
    lines = ["the earth of the 33 kV system (main transformers YNd11):",
             "  the 33 kV windings are delta: they give the collector system",
             "  no neutral and no earth-fault current - an unearthed system",
             "  an earthing transformer per bus section with a resistor",
             "  that limits the earth-fault current to"
             f" {limit_a:.0f} A (teaching):",
             f"    R = U_phase / I = {u_ph:,.0f} / {limit_a:.0f}"
             f" = {r:.1f} ohm",
             f"    the resistor takes {p / 1e3:.1f} MW while a fault lasts",
             "  (seconds: it is rated by time, not continuously); the",
             "  one-line shows both earthing transformers, and the",
             "  protection of ch 26 uses the limited current to find the",
             "  faulted feeder"]
    emit("m_earthing", lines)
# [end: earthing]


def designation() -> None:
    tags = [("=WS1-W2", "function WS1 (wind string 1), product W2 (cable 2)"),
            ("=PVF1-1-T1", "function PVF1-1 (PV block 1 of feeder 1), product T1"),
            ("=T2-Q1", "function T2 (main transformer 2), product Q1 (breaker)"),
            ("=E1-Q9 +SS1.Y2", "export bay E1, product Q9, place SS1 yard bay 2")]
    lines = ["reference designations (aspects of IEC 81346, ch 18):",
             "  '=' says what a thing does, '-' what product it is, '+'",
             "  where it is; the same tag on the one-line, the layout, the",
             "  cable schedule, the label on site and the maintenance system"]
    lines += [f"  {t:16s} {m}" for t, m in tags]
    lines += ["  letter codes of products (Q switching, T transforming, W",
              "  guiding power) come from the standard's classes; a project",
              "  rule-book fixes the rest before the first drawing"]
    emit("m_designation", lines)


def lighting_drainage() -> None:
    yard, bld = 5_000.0, 400.0                      # m2
    light = (yard * 2.0 + bld * 10.0) / 1e3         # kW at 2 and 10 W/m2
    area, storm = 600.0, 0.030                      # m2 catchment, m/h
    q = area * storm / 3600                         # m3/s
    p = 1000 * 9.81 * q * 10.0 / 0.5 / 1e3          # kW at 10 m head
    lines = ["lighting and drainage loads from first principles (teaching):",
             f"  lighting: yard {yard:,.0f} m2 x 2 W/m2 + buildings {bld:.0f} m2 x 10 W/m2"
             f" = {light:.1f} kW",
             f"  drainage: {area:.0f} m2 of trenches and pits x {storm * 1000:.0f} mm/h"
             f" = {q * 1000:.1f} L/s",
             f"    pump power at 10 m head, efficiency 0.5: {p:.2f} kW per sump",
             f"    four sumps, duty and standby pumps: {4 * 2 * math.ceil(p):.0f} kW installed",
             "  the register's 15 kW of lighting and 8 kW of sump pumps",
             "  agree; the storm intensity and the head come from the civil",
             "  design (ch 29), the light levels from the lighting design"]
    emit("m_lighting", lines)


def lv_drop() -> None:
    kw, pf, u, length = 30.0, 0.85, 400.0, 80.0
    i = kw * 1e3 / (math.sqrt(3) * u * pf)
    lines = ["voltage drop of an LV feeder (control room HVAC, teaching):",
             f"  {kw:.0f} kW at pf {pf}: I = {i:.0f} A over {length:.0f} m",
             "  section   r ohm/km  drop V   drop %"]
    for mm2, r in ((10, 1.83), (16, 1.15), (25, 0.727)):
        dv = math.sqrt(3) * i * (r * pf + 0.08 * math.sin(math.acos(pf))) * length / 1e3
        lines.append(f"  {mm2:4d} mm2  {r:8.3f}  {dv:6.1f}   {dv / u:6.1%}")
    lines += ["  with a 2.5 % running limit for this motor feeder (teaching,",
              "  leaving room for the starting dip) 10 mm2 fails and 16 mm2",
              "  passes; its current rating after derating and the fault",
              "  withstand are checked as well (ch 24)"]
    emit("m_lvdrop", lines)


def battery_life() -> None:
    lines = ["DC battery replacement interval against room temperature",
             "(rule of thumb from makers' data for lead-acid: life halves",
             "for every 10 C above 20 C; design life 10 years):",
             "  room C   expected life years"]
    for t in (20, 25, 30, 35):
        lines.append(f"  {t:6d}   {10 * 2 ** (-(t - 20) / 10):10.1f}")
    lines += ["  a cooled battery room pays for itself in fewer replacements;",
              "  the replacement strategy (whole string, planned date, test",
              "  results that trigger it) is part of the DC design, and the",
              "  maker's data for the chosen chemistry replaces this rule"]
    emit("m_battery", lines)


def alternatives() -> None:
    line = s18.EXPORT["overhead line, single circuit"]
    cost = line["cost_per_km"] * 7.06
    loss = 755.0 * 70 / 1e3                          # k u a year (lab G, ch 21)
    om = 0.01 * cost
    lines = ["two connection alternatives for the 132 kV line (teaching):",
             "  A: POC at the plant's line bay - the utility builds, owns",
             "     and maintains the line; the plant pays a connection charge",
             "  B: POC at the utility's bay - the plant builds and owns it",
             f"  the line: {cost:,.0f} k u to build; losses {loss:.1f} k u a year;",
             f"  upkeep about {om:.0f} k u a year",
             "  in B the plant also carries the line's outages, repairs,",
             "  access rights and permits; in A it pays for them through",
             "  the charge - which is cheaper is a number in the grid offer",
             "  (U-065, U-068), and the one-line is redrawn for either"]
    emit("m_alternatives", lines)


if __name__ == "__main__":
    phases()
    earthing()
    designation()
    lighting_drainage()
    lv_drop()
    battery_life()
    alternatives()
