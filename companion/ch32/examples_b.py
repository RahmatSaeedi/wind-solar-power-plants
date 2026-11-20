"""Chapter 32, lesson B: the hazards of a renewable plant in numbers - when
the PV array is energised, fall clearance below an anchor, purging a
confined space, heat and cold from the data-pack year, stopping distance
on site roads, daily noise exposure, and the off-gas ventilation concept
of a battery container.

Run from the project root:   python -m companion.ch32.examples_b
Writes companion/ch32/expected/b_*.txt and diagrams/data/ch32-heat.csv.
Teaching values (A-371). None of this is a work procedure: isolation,
entry, rescue and ventilation design follow the project's management
system, the product data and qualified specialists.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch32 import sources as src  # noqa: F401  (puts plantp on the path)
from companion.ch32.common import csv, emit
from plantp import datapack
from plantp import safety as sf


def _year():
    return datapack.load_hourly()


def pv_energised() -> None:
    d = _year()
    g = d["ghi_wm2"].to_numpy()
    lit = int((g > 50).sum())
    dawn = int(((g > 1) & (g <= 50)).sum())
    lines = ["when the PV array is energised (data-pack year, hourly GHI)",
             f"  hours with GHI above 50 W/m2: {lit:,} ({lit / 87.6:.0f} % of the year)",
             f"  hours with faint light (1-50 W/m2): {dawn:,}",
             "  a module makes voltage in faint light, and open-circuit",
             "  voltage is highest on cold, dim mornings; opening a combiner",
             "  or an inverter switch isolates what lies beyond it, never the",
             "  modules and string cables on the array side - which is why",
             "  DC work is planned with the array treated as energised and",
             "  done under the permit system (ch 6, 9, 10)"]
    emit("b_pv", lines)


def fall() -> None:
    lines = ["clear height needed below an anchor (teaching, maker data governs)",
             "  system                          lanyard  decel  total   anchor  ok?"]
    cases = [("energy-absorbing lanyard 1.8 m", 1.8, 1.75, 5.0),
             ("energy-absorbing lanyard 1.8 m", 1.8, 1.75, 7.0),
             ("short lanyard 1.0 m", 1.0, 1.2, 5.0),
             ("self-retracting device", 0.3, 0.6, 5.0)]
    for name, la, de, h in cases:
        need = sf.fall_clearance(la, de)
        lines.append(f"  {name:31s} {la:5.1f}  {de:5.2f}  {need:5.2f}   {h:4.1f}"
                     f"   {'yes' if need <= h else 'NO'}")
    lines += ["  on a transformer top or a short platform the usual lanyard",
              "  hits the ground before it stops the fall, and the short one",
              "  has only the 1 m margin in the sum: restraint (no free",
              "  fall at all) or a retracting device is chosen, and the",
              "  rescue of a suspended person is planned before work starts"]
    emit("b_fall", lines)


def purge() -> None:
    vol, flow = 30.0, 300.0
    ach = sf.air_changes(vol, flow)
    lines = ["purging a confined space by dilution (well mixed, teaching)",
             f"  space {vol:.0f} m3 (a hub or a cable vault), fan {flow:.0f} m3/h:"
             f" {ach:.0f} air changes an hour"]
    for frac in (0.5, 0.1, 0.01):
        t = -math.log(frac) * vol / flow * 60
        lines.append(f"  time to bring a contaminant to {frac * 100:4.0f} % of its start:"
                     f" {t:5.1f} min")
    lines += ["  real spaces mix badly: corners and low points keep gas long",
              "  after the formula says it has gone. The atmosphere is",
              "  measured before and during entry, never calculated; the",
              "  formula only says how long a fan needs before measuring"]
    emit("b_purge", lines)


def heat() -> None:
    d = _year()
    t = d["t_air_c"].to_numpy()
    hour = d.index.hour.to_numpy()                 # local standard time of the pack
    rows = []
    for h in range(24):
        sel = hour == h
        rows.append((h, int((t[sel] >= 35).sum()), int((t[sel] >= 40).sum())))
    csv("ch32-heat.csv", "hour,above35,above40", rows)
    hot = t >= 35
    early = hot & (hour >= 5) & (hour < 11)
    late = hot & (hour >= 11) & (hour < 18)
    lines = ["heat from the data-pack year (air temperature only)",
             f"  hottest hour {t.max():.1f} C; hours at or above 35 C: {int(hot.sum())},"
             f" above 40 C: {int((t >= 40).sum())}",
             f"  of the 35 C hours, {int(early.sum())} fall between 05 and 11 h and"
             f" {int(late.sum())} between 11 and 18 h",
             f"  a 05-11 h summer shift meets {early.sum() / hot.sum() * 100:.0f} % of them;"
             f" a day shift {late.sum() / hot.sum() * 100:.0f} %",
             "  heat stress depends on humidity, sun, wind and the work, not",
             "  on air temperature alone: the index used on site (for",
             "  example WBGT) needs a measured humidity and globe",
             "  temperature the data pack does not hold. The year shows",
             "  when to plan heavy work (early shifts in summer) and where",
             "  to put shade, water and rest; the limits come from the",
             "  site's heat-stress procedure and local law"]
    emit("b_heat", lines)


def cold() -> None:
    d = _year()
    t = d["t_air_c"].to_numpy() - 0.65             # ~100 m above ground
    v = d["ws_100m_ms"].to_numpy() * 3.6
    vv = np.maximum(v, 4.8)
    wct = 13.12 + 0.6215 * t - 11.37 * vv ** 0.16 + 0.3965 * t * vv ** 0.16
    wct = np.where(t <= 10, wct, t)
    lines = ["cold at nacelle height: wind-chill temperature (data-pack year)",
             f"  coldest wind chill {wct.min():.1f} C; hours below -10 C: {int((wct < -10).sum())},"
             f" below -20 C: {int((wct < -20).sum())}",
             "  the ground minimum was -8.6 C (ch 29); a technician on the",
             "  nacelle roof in a winter wind feels far colder - clothing,",
             "  time on the roof and a warm refuge are planned for it, and",
             "  turbines stopped for work make no heat in the nacelle"]
    emit("b_cold", lines)


def stopping() -> None:
    lines = ["stopping distance on a gravel site road (reaction 1.5 s, mu 0.45)",
             "  speed km/h   reaction m   braking m   total m"]
    for kmh in (20, 30, 40, 50, 60):
        v = kmh / 3.6
        r = v * 1.5
        b = v * v / (2 * 0.45 * 9.81)
        lines.append(f"  {kmh:9d}   {r:10.1f}   {b:9.1f}   {r + b:7.1f}")
    lines += ["  braking grows with the square of speed: 60 km/h needs nearly",
              "  three times the distance of 30 km/h. Site speed limits,",
              "  separated walkways at pads and laydown, and banksmen for",
              "  reversing are chosen from distances like these"]
    emit("b_stopping", lines)


def noise() -> None:
    tasks = [("angle grinder on a tower flange", 98, 1.0),
             ("diesel generator at 3 m", 90, 2.0),
             ("compactor operator (cab closed)", 80, 4.0),
             ("site office and drive", 65, 1.0)]
    e = sum(10 ** (lv / 10) * h for _, lv, h in tasks) / 8
    lex = 10 * math.log10(e)
    lines = ["daily noise exposure of one worker (teaching levels)",
             "  task                                 level dB(A)  hours"]
    for name, lv, h in tasks:
        lines.append(f"  {name:36s} {lv:11d}  {h:5.1f}")
    one = 10 * math.log10(10 ** 9.8 * 1.0 / 8)
    lines += [f"  8-hour equivalent: {lex:.1f} dB(A); the grinder hour alone"
              f" gives {one:.1f}",
              "  each 3 dB is a doubling of sound energy: one grinder hour",
              "  outweighs the whole rest of the day. The action values and",
              "  hearing protection rules come from local law; quieter tools",
              "  and shorter exposure come before ear defenders"]
    emit("b_noise", lines)


def offgas() -> None:
    vol = 60.0
    lines = ["off-gas dilution in a battery container: the concept (placeholders)",
             f"  free air volume {vol:.0f} m3; release and limit are PLACEHOLDERS",
             "  kept below 25 % of a 4 % limit, mixing factor 3",
             "  release m3/h    fresh air m3/h    air changes per hour"]
    for gen in (0.5, 2.0, 8.0):
        q = sf.dilution_flow(gen, 0.25 * 0.04, mixing=3.0)
        lines.append(f"  {gen:12.1f}    {q:14,.0f}    {sf.air_changes(vol, q):20.0f}")
    lines += ["  the steady formula shows why a small release is diluted by a",
              "  fan and a large one is not - a runaway releases gas far",
              "  faster than any fan, which is why explosion control is",
              "  designed from the product's large-scale test gas data, the",
              "  authority's requirements and a specialist's analysis (ch 19,",
              "  U-073); it is never sized from this lesson"]
    emit("b_offgas", lines)


def stored() -> None:
    e_cont = 40.13 / 8 * 1000                       # kWh per container (ch 19)
    oil = 22.0 * 0.87 * 46.0                        # GJ: m3 x t/m3 x GJ/t (ch 25)
    lines = ["energy that stays after the switch is open (teaching)",
             f"  battery container: {e_cont:,.0f} kWh; at 50 % charge"
             f" {e_cont / 2:,.0f} kWh = {e_cont / 2 * 3.6:,.0f} MJ",
             f"  main transformer oil: 22 m3 = {oil:,.0f} GJ of fire load",
             "  DC link capacitors of an inverter: charged for minutes",
             "  after stopping - the maker states the wait",
             "  tensioned springs, brakes and a rotor held by its lock",
             "  opening a breaker removes the grid, not the stored energy:",
             "  a damaged battery keeps its charge after a fire (stranded",
             "  energy) and may reignite days later; its removal is a",
             "  specialist job with the maker, never a site improvisation"]
    emit("b_stored", lines)


if __name__ == "__main__":
    stored()
    pv_energised()
    fall()
    purge()
    heat()
    cold()
    stopping()
    noise()
    offgas()
