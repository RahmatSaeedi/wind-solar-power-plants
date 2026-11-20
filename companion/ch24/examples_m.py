"""Chapter 24 - more circuit engineering: the loop-impedance check of every
LV feeder of the chapter 23 register, the well pump's starting dip at the
motor's own terminals, the battery cable, three ways to cable the wind
strings priced with their losses, an overhead conductor's thermal rating
from its heat balance, insulator creepage, and a cable crossing a road in
a duct.

Run from the project root:   python -m companion.ch24.examples_m
Writes companion/ch24/expected/m_*.txt. Teaching values (A-321..A-325
extended).
"""
from __future__ import annotations

import math

from companion.ch24 import sources as src
from companion.ch24.common import csv, emit
from companion.ch24.examples_h import R90, ampacity, t_soil
from plantp import cables as cb

LV_RUNS = [  # feeder, breaker A (ch 23), route m and mm2 (lesson E schedule)
    ("DC chargers 110 V", 25, 15, 25), ("UPS: SCADA, PPC, telecom", 50, 20, 25),
    ("control room HVAC", 80, 80, 25), ("switchgear room ventilation", 50, 60, 25),
    ("on-load tap changer motors", 16, 120, 25), ("transformer cooling fans", 40, 120, 25),
    ("substation lighting and security", 32, 150, 25),
    ("drainage and sump pumps", 20, 200, 25), ("water pumping and treatment", 100, 350, 95),
    ("cleaning robots charging", 125, 400, 185), ("workshop and stores", 80, 90, 25),
    ("maintenance socket outlets", 63, 100, 25), ("staff facilities", 50, 250, 35)]


def loop() -> None:
    z_src = 0.03
    lines = ["loop-impedance check of the LV feeders (type C breakers, 10 x In):",
             "  feeder                            In A    m  mm2   Zs ohm   max ohm  ok"]
    bad, fails = 0, []
    for name, i_n, m, mm2 in LV_RUNS:
        r = src.LV_CABLES[mm2][0] * 1.2 * 1e-3       # ohm/m at 70 C, approx.
        zs = z_src + 2 * m * r
        zmax = 230 / (10 * i_n)
        ok = zs <= zmax
        bad += not ok
        if not ok:
            fails.append(name.split(' ')[0])
        lines.append(f"  {name:33s} {i_n:4d}  {m:3d}  {mm2:3d}   {zs:6.3f}   {zmax:7.3f}"
                     f"  {'y' if ok else 'n'}")
    d_fail = [n.split(" ")[0] for n, i_n, m, mm2 in LV_RUNS
              if z_src + 2 * m * src.LV_CABLES[mm2][0] * 1.2e-3 > 230 / (20 * i_n)]
    lines += [f"  {bad} feeder(s) fail: {', '.join(fails) if fails else 'none'}",
              f"  with type D breakers (20 x In) {len(d_fail)} would fail:",
              f"    {', '.join(d_fail)}",
              "  a failing feeder does not trip fast enough on a fault at its",
              "  far end: a larger cable is then needed for the disconnection,",
              "  not for the current; an RCD or a smaller breaker is often",
              "  the cheaper answer (the wiring rules decide the time; the",
              "  values here are teaching)"]
    emit("m_loop", lines)


def motor_start() -> None:
    s_start, pf_start = 200.0, 0.3             # kVA, power factor while starting
    z_t = 0.045 * 0.4 ** 2 / 0.25              # ohm, the 250 kVA transformer at 0.4 kV
    lines = ["well pump start (200 kVA direct on line) at the motor's terminals:",
             "  cable mm2   400 m loop ohm   dip at board %   dip at motor %"]
    for mm2 in (70, 95, 185):
        r = cb_lv_r(mm2) * 400
        x = 0.08e-3 * 400
        i = s_start * 1e3 / (math.sqrt(3) * 400)
        dv_t = i * z_t * math.sqrt(3) / 400
        dv_c = math.sqrt(3) * i * (r * pf_start + x * math.sin(math.acos(pf_start))) / 400
        lines.append(f"  {mm2:9d}   {r:14.3f}   {dv_t * 100:14.1f}   {(dv_t + dv_c) * 100:14.1f}")
    lines += ["  the transformer's share is small; the long cable adds most",
              "  of the dip the motor feels - a motor that starts on 80 %",
              "  voltage takes longer and heats more (the maker's limit",
              "  applies); a soft starter or a larger cable are the two",
              "  answers, and the cable is also needed for the running drop"]
    emit("m_motor", lines)


def cb_lv_r(mm2: int) -> float:
    return src.LV_CABLES[mm2][0] * 1.2 * 1e-3


def battery_cable() -> None:
    ik, t_fuse = 3.1, 0.02
    need = cb.adiabatic_mm2(ik, t_fuse, src.K_CU)
    lines = ["the 110 V battery's cables to its fuse board (teaching):",
             f"  battery fault current {ik} kA; the battery fuse clears in about"
             f" {t_fuse * 1e3:.0f} ms",
             f"  adiabatic need: {need:.1f} mm2 - the fault sets almost nothing",
             "  the discharge sets the size: 150 A for the trip burst and the",
             "  first minute, voltage drop below 1 % over 10 m:"]
    for mm2 in (35, 50, 70):
        drop = 150 * 2 * 10 * src.LV_CABLES[mm2][0] * 1.2e-3 / 110 * 100
        lines.append(f"    {mm2:3d} mm2: drop {drop:.2f} %")
    lines += ["  the cable from the battery to its first fuse is the one",
              "  unprotected piece of the DC system: short, double-insulated,",
              "  on its own route - a fault there is fed by the whole battery"]
    emit("m_battery", lines)


def strings_npv() -> None:
    i_sec = [368.0, 276.0, 184.0, 92.0]          # A in the four sections of a wind string
    km, mu, hours, price, rate, years = 1.1, 0.30, 8760, 70.0, 0.075, 25
    annuity = (1 - (1 + rate) ** -years) / rate
    options = {"uniform 630": [630] * 4, "graded 630/240/240/240": [630, 240, 240, 240],
               "uniform 400": [400] * 4}
    lines = ["three ways to cable a wind string (four 1.1 km sections, teaching):",
             "  option                    current  capex k u  loss MWh/yr  PV loss k u"]
    for name, secs in options.items():
        ok = all(cb.rating(src.MV_CABLES[s]["i0"], src.FACTORS)[0] >= i for s, i in zip(secs, i_sec))
        capex = sum(src.MV_CABLES[s]["cost"] * km for s in secs)
        loss_kw = sum(3 * i ** 2 * cb.r_at(src.MV_CABLES[s]["r20"], 90) * km / 1e3
                      for s, i in zip(secs, i_sec))
        mwh = loss_kw * mu * hours / 1e3
        pv = mwh * price * annuity / 1e3
        lines.append(f"  {name:25s} {'ok' if ok else 'FAILS':7s}  {capex:9.0f}  {mwh:11.1f}"
                     f"  {pv:11.0f}")
    lines += ["  (per string; loss load factor 0.30, 70 u/MWh, 7.5 %, 25 years)",
              "  uniform 400 fails the first section; uniform 630 loses less",
              "  but costs more than its losses are worth; the graded string",
              "  is the cheapest that works - the decision of ch 24, lesson F,",
              "  now with its losses priced"]
    emit("m_strings", lines)


def ohl_amps(t_air: float, v: float, t_c: float = 75.0) -> float:
    """Rating (A) of the teaching 132 kV conductor from its heat balance."""
    d, eps, alpha = 0.0245, 0.5, 0.5
    r_ac = 0.10e-3 * (1 + 0.00403 * (t_c - 20))
    p_rad = math.pi * d * eps * 5.67e-8 * ((t_c + 273) ** 4 - (t_air + 273) ** 4)
    h = 3.9 + 8.8 * v ** 0.6 if v > 0 else 3.0
    p_conv = math.pi * d * h * (t_c - t_air)
    p_sun = alpha * d * 1000.0
    return math.sqrt(max(p_conv + p_rad - p_sun, 0) / r_ac)


def ohl_rating() -> None:
    lines = ["thermal rating of the 132 kV conductor from its heat balance:",
             "  I^2 R + solar = convection + radiation (teaching forms)",
             "  air C   wind m/s   rating A"]
    for t_air, v in ((25, 0.6), (35, 0.6), (45, 0.6), (35, 0.0), (35, 2.0)):
        lines.append(f"  {t_air:5d}   {v:8.1f}   {ohl_amps(t_air, v):8.0f}")
    v45 = next(v / 100 for v in range(1, 301) if ohl_amps(45, v / 100) >= 437)
    v35 = next(v / 100 for v in range(1, 301) if ohl_amps(35, v / 100) >= 437)
    lines += ["  wind cools a line far more than anything else: the same",
              "  conductor carries much less on a still, hot, sunny day -",
              "  ratings are given for stated weather: the 650 A of the line",
              "  data needs a cooler or windier day than 35 C and 0.6 m/s",
              f"  the plant's 437 A needs wind of at least {v35:.2f} m/s at 35 C and",
              f"  {v45:.2f} m/s at 45 C: on a hot, still, sunny noon the line is",
              "  the limit - a larger conductor, a higher design temperature,",
              "  or export held down in those hours; the line's design basis",
              "  (ch 28) and the weather data decide which"]
    emit("m_ohl", lines)
    csv("ch24-ohl.csv", "v,t25,t35,t45",
        [(f"{v:.2f}", *(f"{ohl_amps(t, v):.0f}" for t in (25, 35, 45)))
         for v in [i / 10 for i in range(1, 31)]])


def creepage() -> None:
    um = 145.0
    lines = ["insulator creepage for the 132 kV line (teaching factors, mm/kV):",
             "  site pollution     mm per kV   creepage mm   discs of 290 mm"]
    for name, k in (("light", 16.0), ("medium", 20.0), ("heavy", 25.0), ("very heavy", 31.0)):
        c = k * um
        lines.append(f"  {name:16s} {k:11.0f}   {c:11.0f}   {math.ceil(c / 290):15d}")
    lines += ["  dust and salt on the insulator make a conducting film when",
              "  damp; the creepage path must be long enough for the site -",
              "  a desert site near a road or a coast needs the long strings;",
              "  the factor comes from a site pollution assessment and the",
              "  applicable insulator standard, not from this table"]
    emit("m_creepage", lines)


def duct() -> None:
    t4 = t_soil(1.0, 0.8)
    extra = (0.15, 0.35, 0.60)
    lines = ["a road crossing in a duct: the air gap and duct add resistance",
             "  (630 mm2; extra thermal resistance, teaching values):",
             "  extra K m/W   rating A   factor"]
    ref = ampacity(70.0, t4)
    for e in extra:
        i = ampacity(70.0, t4 + e)
        lines.append(f"  {e:11.2f}   {i:8.0f}   {i / ref:6.3f}")
    lines += ["  a few tens of metres in a duct can set the rating of the",
              "  whole feeder (the hot spot of lesson H); filling the duct",
              "  with a thermal grout or a larger duct spacing restores most",
              "  of it - an item in the crossing's design and its records"]
    emit("m_duct", lines)


if __name__ == "__main__":
    loop()
    motor_start()
    battery_cable()
    strings_npv()
    ohl_rating()
    creepage()
    duct()
