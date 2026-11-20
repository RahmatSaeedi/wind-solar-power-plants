"""Chapter 43, a tenth round: the earthed 132 kV neutral as a source of
zero-sequence current, end insulation set by the creep along barriers,
remanence left by the DC tests and the inrush it adds, the auxiliary load
a main transformer brings to ch 23, and the test bay's days for the ten
PV unit transformers.

Run from the project root:   python -m companion.ch43.examples_m
Writes companion/ch43/expected/m_*.txt.
Teaching values (A-462, A-464).
"""
from __future__ import annotations

import math

from companion.ch43 import sources as src
from companion.ch43.common import emit

M = src.MAIN_B


# ------------------------------------------------ the YN neutral in an earth fault
def neutral(s_grid_mva: float = 1500.0, z0_grid_ratio: float = 1.2,
            z0_t_ratio: float = 0.9) -> dict[str, float]:
    u = M["hv_kv"]
    e = u * 1e3 / math.sqrt(3)
    z1g = u ** 2 / s_grid_mva
    z0g = z0_grid_ratio * z1g
    z1t = 0.126 * u ** 2 / M["s_mva"]                  # measured impedance
    z0t = z0_t_ratio * z1t
    z0 = z0g * z0t / (z0g + z0t)
    i_with = 3 * e / (2 * z1g + z0) / 1e3
    i_without = 3 * e / (2 * z1g + z0g) / 1e3
    i_n = i_with * z0g / (z0g + z0t)
    lines = [f"single-phase fault on the 132 kV terminals (grid {s_grid_mva:.0f} MVA;"
             " teaching:",
             f"  Z0 = {z0_grid_ratio} Z1 for the grid, {z0_t_ratio} Z1 for the "
             "YNd transformer)",
             f"  ohm: grid Z1 {z1g:.1f}, Z0 {z0g:.1f}; transformer Z1 {z1t:.1f}, "
             f"Z0 {z0t:.1f}",
             f"  fault current with the neutral earthed {i_with:.2f} kA; with it "
             f"open {i_without:.2f} kA",
             f"  current in the transformer neutral {i_n:.2f} kA",
             "  the earthed star with a delta behind it is a source of",
             "  zero-sequence current even with the plant off: the 132 kV",
             "  earth-fault level and the neutral's conductor, CT and",
             "  bushing are sized with it (ch 26)"]
    emit("m_neutral", lines)
    return dict(i_with=i_with, i_without=i_without, i_n=i_n)


# ------------------------------------------------ end insulation and creep
def creep(u_kv: float = 100.0, e_bulk: float = 4.0, e_tang: float = 1.0):
    gap_bulk = u_kv / e_bulk
    path = u_kv / e_tang
    lines = [f"winding end to yoke at a teaching {u_kv:.0f} kV: through oil and board "
             "the gap",
             f"  holds about {e_bulk} kV/mm ({gap_bulk:.0f} mm); along a board "
             f"surface only {e_tang} kV/mm",
             f"  a creep path of {path:.0f} mm is needed - more than the straight gap",
             "  angle rings and caps lengthen the surface path without",
             "  lengthening the window much: the 0.35 m of end insulation",
             "  in the design (lesson A) is shaped by creep as much as by",
             "  the gap",
             "  (field values are teaching; the maker's design sets them)"]
    emit("m_creep", lines)
    return dict(gap=gap_bulk, path=path)


# ------------------------------------------------ remanence after DC tests
def remanence(bn: float = 1.7, bs: float = 2.03, x_air: float = 0.3) -> dict:
    i_n = 275.6
    out = {}
    lines = ["remanent flux left by the DC resistance tests, and the inrush",
             "  peak it adds on energising (ch 25 estimate)",
             "  core state                       residual   inrush peak A   x rated"]
    for name, br in (("after the DC tests", 0.8), ("demagnetised", 0.1)):
        pk = math.sqrt(2) * i_n / x_air * max(0.0, 2 * bn + br * bn - bs) / bn
        out[name] = pk
        lines.append(f"  {name:32s} {br:8.1f} Bn   {pk:13.0f}   "
                     f"{pk / i_n:7.1f}")
    lines += ["  the DC current of the resistance test magnetises the core and",
              "  leaves it there; demagnetising after the DC tests (at the",
              "  factory and again at site) is a record on the checklist -",
              "  the inrush and the differential's blocking (ch 26) thank it"]
    emit("m_remanence", lines)
    return out


# ------------------------------------------------ auxiliary load
AUX = [("fans (8 x 1.1 kW)", 8.8, "ONAF hours"),
       ("tap-changer motor", 1.1, "a few seconds an operation"),
       ("cabinet heaters", 0.5, "all year"),
       ("online gas monitor", 0.2, "all year"),
       ("cooling control and sensors", 0.1, "all year")]


def aux(fan_h: float = 532.0) -> dict[str, float]:
    peak = sum(v for _, v, _ in AUX)
    cont = sum(v for n, v, w in AUX if w == "all year")
    mwh = (cont * 8760 + 8.8 * fan_h) / 1000
    lines = ["auxiliary load of one main transformer (teaching)",
             "  item                           kW    when"]
    for n, v, w in AUX:
        lines.append(f"  {n:30s} {v:4.1f}    {w}")
    lines += [f"  peak {peak:.1f} kW; continuous {cont:.1f} kW; about {mwh:.1f} MWh a year",
              "  small, but it is an essential load: fans lost above the ONAN",
              "  rating mean a load limit - the transformer's auxiliaries",
              "  belong on the essential board of ch 23"]
    emit("m_aux", lines)
    return dict(peak=peak, cont=cont, mwh=mwh)


# ------------------------------------------------ PV unit test bay days
def pv_bay(units: int = 10, routine_h: float = 6.0, type_days: float = 2.0,
           special_days: float = 0.5, hours_day: float = 16.0) -> dict[str, float]:
    routine_days = units * routine_h / hours_day
    total = routine_days + type_days + special_days
    lines = [f"test bay for the ten PV unit transformers (teaching)",
             f"  routine tests {routine_h:.0f} h a unit x {units}: {routine_days:.2f} days",
             f"  type tests on the first unit: {type_days:.1f} days; sound on one: "
             f"{special_days:.1f} day",
             f"  {total:.1f} bay days; the buyer witnesses the first unit fully and",
             "  samples the rest (ch 39, witness sampling) - a design fault",
             "  shows on unit 1, a workmanship fault may sit on any unit,",
             "  which is why routine tests run on all ten"]
    emit("m_pvbay", lines)
    return dict(days=total, routine=routine_days)


if __name__ == "__main__":
    neutral()
    creep()
    remanence()
    aux()
    pv_bay()
