"""Chapter 24, section E - auxiliary LV and DC distribution: each
station-service feeder of chapter 23 gets a copper cable by current,
voltage drop and short-circuit withstand; the DC trip-coil circuit is
checked for the voltage that reaches the coil at the end of discharge;
critical circuits are segregated.

Run from the project root:   python -m companion.ch24.examples_e
Writes companion/ch24/expected/e_*.txt. Teaching values A-321 to A-325.
"""
from __future__ import annotations

import math

from companion.ch23 import sources as s23
from companion.ch24 import sources as src
from companion.ch24.common import emit
from plantp import cables as cb

LENGTH_M = {   # route lengths from the LV board (teaching)
    "DC chargers 110 V": 15, "UPS: SCADA, PPC, telecom": 20,
    "control room HVAC": 80, "switchgear room ventilation": 60,
    "on-load tap changer motors": 120, "transformer cooling fans": 120,
    "substation lighting and security": 150, "drainage and sump pumps": 200,
    "water pumping and treatment": 350, "cleaning robots charging": 400,
    "workshop and stores": 90, "maintenance socket outlets": 100,
    "staff facilities": 250,
}


# [start: lvselect]
def lv_cable(i: float, length_m: float, pf: float, ik_ka: float,
             t_s: float = 0.1, drop_max: float = 3.0):
    """Smallest Cu section that carries i, keeps the drop under drop_max
    % at 0.4 kV and withstands ik for t (adiabatic, k = 143)."""
    for mm2, (r20, i0) in src.LV_CABLES.items():
        r = cb.r_at(r20, 70)                      # PVC/XLPE in service
        d = cb.drop_pct(i, length_m / 1e3, r, 0.08, pf, 0.4)
        ok_sc = cb.withstand_ka(mm2, t_s, src.K_CU) >= ik_ka
        if i0 * 0.8 >= i and d <= drop_max and ok_sc:
            return mm2, d
    raise ValueError("no section in the table")
# [end: lvselect]


def lv_schedule() -> None:
    lines = ["LV cable schedule from the ch 23 load register (Cu, 0.4 kV):",
             "  feeder                            I A    m   mm2  drop %"]
    tot = 0.0
    for ld in s23.AUX:
        i = ld.kw * 1e3 / (math.sqrt(3) * 400 * ld.pf)
        mm2, d = lv_cable(i, LENGTH_M[ld.tag], ld.pf, 7.9)
        tot += LENGTH_M[ld.tag]
        lines.append(f"  {ld.tag[:32]:32s} {i:5.0f}  {LENGTH_M[ld.tag]:4d}  {mm2:4d}  {d:6.2f}")
    s_min = cb.adiabatic_mm2(7.9, 0.1, src.K_CU)
    lines += [f"  {tot:,.0f} m of feeders; the long ones (water, robots, staff)",
              "  are sized by the drop; all the others by the fault: 7.9 kA",
              f"  for 0.1 s needs {s_min:.1f} mm2, so 25 mm2 even for a 5 A motor;",
              "  a current-limiting breaker lets through far less I2t and",
              "  allows smaller cables - its let-through curve, from the",
              "  maker, decides; the factor 0.8 stands in for grouping"]
    emit("e_schedule", lines)


def trip_coil() -> None:
    v_end = 55 * 1.75                                # end of discharge
    i_coil = 5.0                                     # A, while it trips
    lines = ["the DC trip circuit: voltage at the coil at the end of discharge",
             f"  battery {v_end:.1f} V; coil draws {i_coil:.0f} A; loop length = 2 x route",
             "  route m  section mm2  drop V   at coil V   % of 110 V"]
    for length, mm2 in ((80, 2.5), (200, 2.5), (200, 4.0), (300, 6.0)):
        r = 1.83 * 10 / mm2 * 1.2                     # ohm/km at 70 C, Cu
        dv = i_coil * r * 2 * length / 1e3
        lines.append(f"  {length:7d}  {mm2:11.1f}  {dv:6.2f}   {v_end - dv:9.1f}"
                     f"   {(v_end - dv) / 110:9.0%}")
    lines += ["  a trip coil that must work from 70 % of rated voltage still",
              "  works at 200 m on 2.5 mm2, but the margin shrinks with the",
              "  route: DC circuits are sized for the worst battery state,",
              "  not the float voltage"]
    emit("e_trip", lines)


def segregation() -> None:
    groups = [("protection and trip circuits (DC)", "own trays, screened, two routes for duplicated systems"),
              ("UPS and SCADA supplies", "separate from power cables; fire-rated where the route needs"),
              ("emergency supplies (generator, ATS)", "own route from the generator to the essential half"),
              ("LV power", "trays by voltage class, spacing for heat"),
              ("33 kV cables", "own trench or duct bank, warning tape, marker posts")]
    lines = ["segregation of critical circuits (concepts, teaching):"]
    for g, how in groups:
        lines.append(f"  {g}:")
        lines.append(f"    {how}")
    lines += ["  segregation keeps one fault or one fire from taking out a",
              "  circuit and its backup together; the fire design (ch 31)",
              "  sets where fire-rated routes are required"]
    emit("e_segregation", lines)


if __name__ == "__main__":
    lv_schedule()
    trip_coil()
    segregation()
