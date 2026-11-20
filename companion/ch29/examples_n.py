"""Chapter 29, lesson N (more on construction quality and environment):
the laboratory compaction curve and the field moisture window, plate
load tests, fresh concrete temperature in summer, the heat of a large
foundation pour, dust against water and speed, spoil and topsoil, and
the inspection and test plan of a turbine foundation.

Run from the project root:   python -m companion.ch29.examples_n
Writes companion/ch29/expected/n_*.txt and diagrams/data/ch29-proctor.csv.
Teaching values (A-354); the specification and the specialists decide.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch29 import sources as src
from companion.ch29.common import csv, emit
from plantp import materials as mt


def proctor() -> None:
    w = np.array([6.0, 8.0, 10.0, 12.0, 14.0])                 # moisture %
    rho = np.array([1.86, 1.95, 1.99, 1.96, 1.88])             # dry density t/m3
    a, b, c = np.polyfit(w, rho, 2)
    w_opt = -b / (2 * a)
    rho_max = c - b * b / (4 * a)
    target = 0.95 * rho_max
    disc = math.sqrt(b * b - 4 * a * (c - target))
    w_lo, w_hi = sorted(((-b - disc) / (2 * a), (-b + disc) / (2 * a)))
    ws = np.linspace(5, 15, 41)
    csv("ch29-proctor.csv", "w,rho", [(f"{x:.2f}", f"{np.polyval([a, b, c], x):.4f}") for x in ws])
    csv("ch29-proctor-pts.csv", "w,rho", list(zip(w, rho)))
    lines = ["laboratory compaction test of the pad fill (five points, synthetic)",
             "  moisture %   " + "  ".join(f"{x:5.1f}" for x in w),
             "  dry t/m3     " + "  ".join(f"{x:5.2f}" for x in rho),
             f"  parabola fit: maximum dry density {rho_max:.3f} t/m3 at {w_opt:.1f} % moisture",
             f"  95 % of the maximum ({target:.3f} t/m3) is reachable only between"
             f" {w_lo:.1f} and {w_hi:.1f} %",
             "  outside that window no number of roller passes gives 95 %;",
             "  in a desert summer the fill dries in hours - water is",
             "  added and mixed just before rolling, and the field test",
             "  records moisture as well as density"]
    emit("n_proctor", lines)


def plate() -> None:
    r = 0.15                                                    # 300 mm plate
    tests = [("road km 0.5", (0.0, 0.5), 2.10, 0.95), ("pad T03", (0.0, 0.5), 1.40, 0.62),
             ("pad T07", (0.0, 0.5), 3.90, 1.30)]
    lines = ["plate load tests (300 mm plate; E = 1.5 r d_sigma / d_s; teaching",
             "  criteria from the specification: Ev2 >= 45 MPa, Ev2/Ev1 <= 2.5)",
             "  place          s1 mm   s2 mm   Ev1 MPa   Ev2 MPa   ratio   result"]
    for name, (s0, s1), d1, d2 in tests:
        dsig = 0.25                                             # MPa between 0.1 and 0.35 MPa
        ev1 = 1.5 * r * dsig / (d1 / 1000)
        ev2 = 1.5 * r * dsig / (d2 / 1000)
        ok = ev2 >= 45 and ev2 / ev1 <= 2.5
        del s0, s1
        lines.append(f"  {name:13s}  {d1:5.2f}   {d2:5.2f}   {ev1:7.1f}   {ev2:7.1f}   {ev2 / ev1:5.2f}"
                     f"   {'pass' if ok else 'FAIL'}")
    lines += ["  a high Ev2/Ev1 ratio means the first loading compacted the",
              "  layer further - it was loose; T07 fails on stiffness and",
              "  on the ratio, matching its compaction lot (lesson C)"]
    emit("n_plate", lines)


def hot_concrete() -> None:
    mix = dict(agg=1900.0, cem=380.0, water=165.0, agg_water=40.0)   # kg per m3
    cases = [("summer day, as delivered", 40.0, 45.0, 32.0, 0.0),
             ("chilled mixing water (5 C)", 40.0, 45.0, 5.0, 0.0),
             ("half the water as ice", 40.0, 45.0, 5.0, 0.5),
             ("night pour, shaded stockpiles", 28.0, 35.0, 5.0, 0.0)]
    lines = ["fresh concrete temperature from its ingredients (heat balance with",
             "  solids at 0.22 of water's specific heat; ice melting = 80 K of water)",
             "  case                             aggregate  cement  water  ice   fresh C"]
    for name, ta, tc, tw, ice in cases:
        wi = ice * mix["water"]
        ww = mix["water"] - wi
        num = (0.22 * (ta * mix["agg"] + tc * mix["cem"]) + tw * ww + ta * mix["agg_water"]
               - 80 * wi)
        den = 0.22 * (mix["agg"] + mix["cem"]) + ww + wi + mix["agg_water"]
        lines.append(f"  {name:32s} {ta:9.0f}  {tc:6.0f}  {tw:5.0f}  {100 * ice:3.0f}%"
                     f"  {num / den:7.1f}")
    lines += ["  (teaching specification limit: 32 C at placing)",
              "  the aggregate carries most of the heat: chilled water",
              "  alone is not enough on a summer day; ice or a night pour",
              "  with shaded, sprayed stockpiles brings the mix within the",
              "  limit - and the ice is part of the water balance (lesson G)"]
    emit("n_hotconcrete", lines)


def mass_pour() -> None:
    h_cem = 330.0                                              # kJ/kg, ch 4 (A-066)
    lines = ["heat of hydration in a 620 m3 foundation pour (ch 4 values, A-066;",
             "  the concrete specialist sets the mix and the limits)",
             "  binder                              kg/m3   heat kJ/kg   adiabatic rise K"]
    rows = [("cement only", 380, h_cem), ("30 % fly ash", 380, 0.7 * h_cem + 0.3 * 130),
            ("50 % slag", 380, 0.5 * h_cem + 0.5 * 200)]
    for name, b, h in rows:
        lines.append(f"  {name:34s} {b:6d}   {h:10.0f}   {mt.adiabatic_rise(b, h):15.1f}")
    rise = mt.adiabatic_rise(380, h_cem)
    lines += [f"  placed at 30 C, the core of a thick pour nears 30 + {0.85 * rise:.0f}"
              f" = {30 + 0.85 * rise:.0f} C",
              "  (85 % of the adiabatic rise, cement only)",
              "  while the surface cools at night: a core-to-surface",
              "  difference above about 20 K (a common teaching limit)",
              "  cracks the surface; a low-heat binder, a cool mix,",
              "  insulation and thermocouples in the pour control it"]
    emit("n_masspour", lines)


def dust() -> None:
    base = 75_600.0                                            # m3 (lesson G)
    lines = ["dust control on the site roads: water against speed and binders",
             "  (teaching: emission in proportion to speed; watering at 1.5 L/m2",
             "   a day removes 75 %, half that rate 50 %, a binder 80 %)",
             "  option                                   emission %   water m3"]
    opts = [("no control, 50 km/h", 100.0, 0.0),
            ("watering, 50 km/h (lesson G)", 25.0, base),
            ("speed 30 km/h, watering", 0.6 * 25.0, base),
            ("speed 30 km/h, half the watering", 0.6 * 100 * (1 - 0.5), base / 2),
            ("binder on main track (40 % of traffic)", 0.6 * (60 * 0.25) + 0.4 * (60 * 0.20),
             base * 0.6)]
    for name, e, wtr in opts:
        lines.append(f"  {name:42s} {e:9.0f}   {wtr:8,.0f}")
    lines += ["    + speed 30 km/h elsewhere",
              "  a lower speed is the cheapest control: half the watering",
              "  at 30 km/h gives about the dust of full watering at 50",
              "  and saves nearly 38,000 m3; a binder on the busiest",
              "  stretch with the lower speed gives the least dust of all",
              "  on 40 % less water - and less wear (lesson M)"]
    emit("n_dust", lines)


def spoil() -> None:
    exc = 12 * math.pi * 11.5 ** 2 * (src.FOUNDATION_DEPTH + 0.2)
    back = 12 * (math.pi * 11.5 ** 2 - math.pi * 10 ** 2) * src.FOUNDATION_DEPTH + 12 * 900
    trench = 60_000 * 0.6 * 1.2
    topsoil_area = 28_000 * 8 + 12 * 1600 + 12_000 + 30_000
    top = topsoil_area * 0.15
    heap = top / 2.0
    rows = [("turbine excavations (23 m wide, 3.7 m deep)", exc),
            ("backfill over and around the foundations", back),
            ("cable trenches (60 km x 0.6 x 1.2 m), mostly back", trench),
            ("surplus from the turbine excavations", exc - back),
            (f"topsoil stripped 0.15 m from {topsoil_area / 1e4:.0f} ha", top)]
    lines = ["spoil and topsoil (teaching quantities)"]
    lines += [f"  {name:50s} {v:9,.0f} m3" for name, v in rows]
    lines += [f"  topsoil stockpiled at most 2 m high: about {heap / 1e4:.1f} ha of heaps",
             "  topsoil is kept apart, low and covered or seeded so its",
             "  seeds and soil life survive for reinstatement; surplus",
             "  spoil goes into the road embankments (lesson M) before a",
             "  tip is opened"]
    emit("n_spoil", lines)


def itp() -> None:
    steps = [("excavation to level, ground inspected", "H", "geotechnical engineer"),
             ("blinding level and setting out", "W", "surveyor"),
             ("anchor cage level and plumb", "H", "turbine maker"),
             ("reinforcement and cover before pour", "H", "structural engineer"),
             ("embedded earthing and ducts", "W", "electrical"),
             ("pour: slump, temperature, cubes", "W", "laboratory"),
             ("curing and thermocouple record", "R", "contractor"),
             ("28-day strength", "R", "laboratory"),
             ("grout under the tower flange", "H", "turbine maker"),
             ("backfill compaction", "W", "laboratory")]
    lines = ["inspection and test plan of one turbine foundation (H hold, W",
             "  witness, R record review)"]
    for k, (s, t, who) in enumerate(steps, 1):
        lines.append(f"  {k:2d} [{t}] {s:40s} {who}")
    n_h = sum(t == "H" for _, t, _ in steps)
    lines += [f"  {n_h} hold points: work stops until the named party signs;",
              "  twelve foundations make 48 signatures that must be",
              "  planned into the programme, or the crane waits for them"]
    emit("n_itp", lines)


if __name__ == "__main__":
    proctor()
    plate()
    hot_concrete()
    mass_pour()
    dust()
    spoil()
    itp()
