"""Chapter 45, round y: what the records save in an incident, a capacity
calibration cycle against its energy, the battery's mass at the end of
life, a CUSUM on a rack's insulation trend, the sample needed to qualify
a second cell factory, and a dry-room excursion contained by the record.

Run from the project root:   python -m companion.ch45.examples_y
Writes companion/ch45/expected/y_*.txt.
Teaching values (A-475 to A-481).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch45 import sources as src
from companion.ch45.common import emit
from plantp import performance as pf

C, B = src.CELL, src.BUILD


# ------------------------------------------------ 1. what the records save
def records_value(h_module: float = 6.0, crew: int = 2, p_rack_mw: float = 0.21,
                  hours_trace: float = 3.0) -> dict:
    modules_c = B["m_rack"] * B["r_container"]
    with_rec = 1
    no_rec = modules_c
    h_with = hours_trace + with_rec * h_module
    h_without = no_rec * h_module / crew
    lines = ["a leaker found in container C5: hours to the cell (teaching)",
             f"  with the record: trace {hours_trace:.0f} h, open {with_rec} "
             f"module ({h_module:.0f} h): {h_with:.0f} h, one rack out",
             f"  without it: open all {no_rec} modules of the container, {crew} "
             f"crews: {h_without:.0f} h",
             f"  energy not shifted meanwhile: rack {p_rack_mw * h_with:.1f} MWh "
             f"against container {p_rack_mw * 12 * h_without:.0f} MWh",
             "  the record turns a search into a lookup; opening 96 healthy",
             "  modules also risks damaging them - the record is safety too"]
    emit("y_records", lines)
    return dict(h_with=h_with, h_without=h_without)


# ------------------------------------------------ 2. a calibration cycle
def calibration(rt: float = 0.86, price: float = 70.0, per_year=(1, 4, 12)) -> dict:
    e = B["s_module"] * B["m_rack"] * B["r_container"] * B["containers"] * \
        C["q_ah"] * C["v_nom"] / 1e6
    usable = 0.8 * e
    loss = usable * (1 - rt)
    lines = [f"a full capacity cycle of the battery ({usable:.1f} MWh in the "
             "window)",
             "  to recalibrate SOC and health",
             f"  energy lost a cycle at round trip {rt:.0%}: {loss:.1f} MWh "
             f"({loss * price / 1000:.2f} k u)",
             "  cycles a year   MWh lost   k u"]
    out = {}
    for n in per_year:
        out[n] = loss * n
        lines.append(f"  {n:13d}   {loss * n:8.1f}   {loss * n * price / 1000:4.1f}")
    lines += ["  a calibration cycle costs little; scheduling it where it",
              "  replaces a normal cycle costs less still - what it buys is a",
              "  health figure the warranty and the plant model can trust",
              "  (ch 19, ch 37)"]
    emit("y_calib", lines)
    return dict(loss=loss)


# ------------------------------------------------ 3. mass at the end
def end_mass(truck_t: float = 24.0, soc_end: float = 0.10) -> dict:
    cells = B["s_module"] * B["m_rack"] * B["r_container"] * B["containers"]
    m_cells = cells * C["mass_kg"] / 1000
    m_modules = m_cells * 1.18
    trucks = math.ceil(m_modules / truck_t)
    e_left = cells * C["q_ah"] * C["v_nom"] / 1e6 * soc_end
    lines = [f"the battery at the end: {cells:,} cells = {m_cells:.0f} t, as "
             f"modules {m_modules:.0f} t",
             f"  {trucks} trucks of {truck_t:.0f} t to the recycler (modules "
             "out of the containers)",
             f"  energy still in them at {soc_end:.0%} SOC: {e_left:.1f} MWh",
             "  discharging before removal lowers that energy, and the",
             "  removal order, isolation by division and transport class",
             "  come from the integrator's procedure and the rules (ch 53)"]
    emit("y_endmass", lines)
    return dict(m=m_modules, trucks=trucks, e_left=e_left)


# ------------------------------------------------ 4. insulation trend
def insulation_trend(seed: int = 4513, days: int = 120, start: int = 70) -> dict:
    """Daily insulation resistance of a rack (log scale, teaching); moisture
    enters from day `start` and lowers it slowly."""
    rng = np.random.default_rng(seed)
    base = np.log10(500.0)                                # kohm
    x = base + rng.normal(0, 0.05, days)
    x[start:] -= 0.004 * np.arange(days - start)
    resid = (x - base) / 0.05
    alarm_fixed = next((d for d in range(days) if 10 ** x[d] < 300), None)
    hit = pf.cusum(list(resid), k=0.5, h=5.0)
    lines = [f"daily insulation resistance of one rack, {days} days "
             "(synthetic);",
             f"  moisture from day {start + 1}",
             f"  fixed alarm below 300 kohm: day {alarm_fixed + 1}",
             f"  CUSUM on the log reading (k 0.5, h 5): day {hit + 1}",
             "  a slow fall stays above a fixed alarm for weeks; a CUSUM",
             "  sees the trend while the value is still healthy - time to",
             "  find a door seal or a cooling leak before the insulation",
             "  alarm trips the rack (ch 37)"]
    emit("y_trend", lines)
    return dict(fixed=alarm_fixed, cusum=hit)


# ------------------------------------------------ 5. a second cell factory
def requalify(sd: float = 1.3, shift: float = 0.5, alpha_z: float = 1.96,
              power_z: float = 0.84) -> dict:
    n = math.ceil(2 * (alpha_z + power_z) ** 2 * sd ** 2 / shift ** 2)
    lines = [f"the cell maker adds a second factory: does it make the same cell?",
             f"  capacity sd {sd} Ah; to see a mean shift of {shift} Ah",
             "  with 95 % confidence and 80 % power:",
             f"  n = 2 (z_a + z_b)^2 sd^2 / shift^2 = {n} cells from each factory",
             "  capacity is the easy part; the K-value, resistance and the",
             "  lot data file get the same comparison, and the second",
             "  factory's audit (lesson B) comes first - a new factory is a",
             "  change to the product, with its own release (ch 40)"]
    emit("y_requal", lines)
    return dict(n=n)


# ------------------------------------------------ 6. a dry-room excursion
def excursion(rate_day: float = 12000.0, hours: float = 3.0) -> dict:
    """Cells that passed the open assembly steps during an excursion above
    the dew-point limit (teaching: steady flow through the line)."""
    per_h = rate_day / 24
    held = per_h * hours
    lines = [f"dew-point record above the limit for {hours:.0f} h (teaching);",
             f"  {per_h:.0f} cells an hour pass assembly",
             f"  cells whose open steps fell in the excursion: {held:,.0f}",
             "  the record of time and place for each cell turns this into",
             "  a list: those cells are held and tested; without it, the",
             "  whole day's production - "
             f"{rate_day:,.0f} cells - would be in doubt"]
    emit("y_excursion", lines)
    return dict(held=held)


if __name__ == "__main__":
    records_value()
    calibration()
    end_mass()
    insulation_trend()
    requalify()
    excursion()
