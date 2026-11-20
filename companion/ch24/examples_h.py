"""Chapter 24 - where the installation factors come from: a thermal circuit
of a buried 33 kV cable (internal resistance fitted to the reference
rating, soil resistance from depth and soil, mutual heating of a second
circuit by its image), the cyclic rating of a PV feeder, skin effect,
dielectric losses at 33 and 132 kV, an emergency overload, and a fibre
temperature profile along a feeder.

Run from the project root:   python -m companion.ch24.examples_h
Writes companion/ch24/expected/h_*.txt and diagrams/data/ch24-dts.csv.
Teaching physics (A-321, A-322 extended): real ratings come from the
maker's data and the applicable current-rating method.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch24 import sources as src
from companion.ch24.common import csv, emit

C630 = src.MV_CABLES[630]
D = 0.075                       # m, overall diameter of the 3-core cable
R90 = C630["r20"] * 1e-3 * (1 + 0.00403 * 70) * 1.02     # ohm/m, Al, skin
DT_REF = 90.0 - 20.0


# [start: thermal]
def t_soil(rho: float, depth: float, d: float = D) -> float:
    """Thermal resistance (K m/W) of the soil around a buried cable:
    rho / (2 pi) ln(4 L / D)."""
    return rho / (2 * math.pi) * math.log(4 * depth / d)


def t_mutual(rho: float, depth: float, spacing: float) -> float:
    """Extra resistance seen by one cable from a neighbour carrying the
    same loss: rho / (2 pi) ln(d' / d), d' the distance to its image."""
    d_img = math.hypot(2 * depth, spacing)
    return rho / (2 * math.pi) * math.log(d_img / spacing)


T_INT = DT_REF / (3 * C630["i0"] ** 2 * R90) - t_soil(1.0, 0.8)


def ampacity(dt: float, t_ext: float) -> float:
    """Current (A) that heats the conductor by dt with the cable's
    internal and the given external thermal resistance."""
    return math.sqrt(dt / (3 * R90 * (T_INT + t_ext)))
# [end: thermal]


def factors() -> None:
    ref = ampacity(DT_REF, t_soil(1.0, 0.8))
    rows = [("depth 1.0 m", ampacity(DT_REF, t_soil(1.0, 1.0)), 0.97),
            ("soil 1.5 K m/W", ampacity(DT_REF, t_soil(1.5, 0.8)), 0.88),
            ("ground 30 C", ampacity(60.0, t_soil(1.0, 0.8)), 0.93),
            ("two circuits 0.4 m", ampacity(DT_REF, t_soil(1.0, 0.8) + t_mutual(1.0, 0.8, 0.4)),
             0.85)]
    lines = ["installation factors from a thermal circuit (630 mm2, teaching):",
             f"  R at 90 C {R90 * 1e3:.4f} ohm/km; fitted internal resistance {T_INT:.3f} K m/W",
             f"  soil at reference (1.0 K m/W, 0.8 m): {t_soil(1.0, 0.8):.3f} K m/W;"
             f" rating {ref:.0f} A",
             "  condition              physics factor   table factor"]
    for name, i, tab in rows:
        lines.append(f"  {name:22s} {i / ref:14.3f}   {tab:12.2f}")
    allc = ampacity(60.0, t_soil(1.5, 1.0) + t_mutual(1.5, 1.0, 0.4))
    lines += [f"  all four together: {allc:.0f} A, factor {allc / ref:.3f}"
              f" (table product {0.97 * 0.88 * 0.93 * 0.85:.3f})",
              "  depth, soil and ground temperature follow from the physics;",
              "  the simple image model gives less mutual heating than the",
              "  table, which also allows for the soil drying out next to a",
              "  warm cable - the reason tables are kept conservative"]
    emit("h_factors", lines)


def cyclic() -> None:
    mu = 0.25                    # daily loss factor of a PV feeder (mean I^2 / peak I^2)
    t4 = t_soil(1.0, 0.8)
    cont = ampacity(DT_REF, t4)
    naive = ampacity(DT_REF, mu * t4)
    near = 0.5
    two = ampacity(DT_REF, near * t4 + (1 - near) * mu * t4)
    lines = ["cyclic rating of a PV feeder (daily loss factor 0.25, teaching):",
             f"  continuous rating                         {cont:5.0f} A",
             f"  soil sees only the daily mean (too simple) {naive:5.0f} A"
             f"  x{naive / cont:.2f}",
             f"  near soil follows the day, far soil the mean {two:5.0f} A"
             f"  x{two / cont:.2f}",
             "  the soil's long time constant lets a cable that carries",
             "  current only by day run hotter at noon; but a run of sunny",
             "  days warms the far soil too - the cyclic factor is a study",
             "  result with the soil's heat capacity, never taken from the",
             "  first line, and the ch 25 loading of the transformer uses",
             "  the same idea"]
    emit("h_cyclic", lines)


def skin() -> None:
    lines = ["skin effect: AC over DC resistance of large conductors",
             "  ys = xs^4 / (192 + 0.8 xs^4),  xs^2 = 8 pi f / R' x 1e-7 x ks",
             "  conductor                         R' ohm/m   ks    ys"]
    for name, r, ks in (("630 mm2 Al, compacted", 6.0e-5, 1.0),
                        ("1000 mm2 Cu, compacted", 2.3e-5, 1.0),
                        ("1000 mm2 Cu, segmental", 2.3e-5, 0.435)):
        xs2 = 8 * math.pi * 50 / r * 1e-7 * ks
        ys = xs2 ** 2 / (192 + 0.8 * xs2 ** 2)
        lines.append(f"  {name:32s} {r:9.1e}   {ks:4.2f}  {ys:5.3f}")
    lines += ["  the current crowds to the surface of a thick conductor: a",
              "  1000 mm2 copper conductor carries 14 % more resistance at",
              "  50 Hz; dividing it into insulated segments brings this down",
              "  - one reason export cables have segmental conductors"]
    emit("h_skin", lines)


def dielectric() -> None:
    lines = ["dielectric losses: W = omega C U0^2 tan(delta), three phases",
             "  cable              U0 kV   C uF/km  tan d   W W/m   conductor W/m"]
    for name, u0, c, i, r, td in (("33 kV, 630 mm2", 19.05, 0.30, 445.0, R90, 0.004),
                                  ("132 kV, 1000 mm2 Cu", 76.2, 0.20, 437.0, 2.6e-5,
                                   0.001)):
        wd = 3 * 2 * math.pi * 50 * c * 1e-9 * (u0 * 1e3) ** 2 * td
        wc = 3 * i ** 2 * r
        lines.append(f"  {name:18s} {u0:6.2f}   {c:7.2f}  {td:.3f}  {wd:6.2f}   {wc:12.1f}")
    lines += ["  tan d: 0.004 an upper teaching value for MV, 0.001 for HV",
              "  XLPE; the loss grows with U0^2 and is there day and night,",
              "  with or without load: at 33 kV about one per cent of the",
              "  conductor's, at 132 kV some per cent; the IEC 60287 method",
              "  counts it for XLPE from U0 of about 127 kV; it still adds",
              "  to the plant's night-time import (ch 23)"]
    emit("h_dielectric", lines)


def overload() -> None:
    tau = 1.5                   # h, conductor and insulation (teaching)
    i_norm = 0.85               # pu of rating before the event
    lines = ["emergency overload of a cable (first-order heating, tau 1.5 h):",
             "  start at 0.85 pu, then        final C   hours to 90 C"]
    th0 = 20 + DT_REF * i_norm ** 2
    for k in (1.1, 1.2, 1.3, 1.5):
        thf = 20 + DT_REF * k ** 2
        t = math.inf if thf <= 90 else -tau * math.log(1 - (90 - th0) / (thf - th0))
        lines.append(f"  {k:4.1f} pu                     {thf:8.1f}   "
                     f"{'stays below' if t == math.inf else f'{t:6.2f}'}")
    lines += [f"  (start temperature {th0:.1f} C) - a ring or a parallel",
              "  feeder that switches load onto a cable for an hour can",
              "  use this margin; at 1.3 pu the limit comes in about half",
              "  an hour, at 1.5 pu in under 20 minutes; the protection (ch 26) and",
              "  the switching rules must keep inside it"]
    emit("h_overload", lines)


def dts() -> None:
    x = np.linspace(0, 4400, 441)
    temp = 52 + 3 * np.sin(x / 600)
    temp += 14 * np.exp(-((x - 1650) / 25) ** 2)       # road crossing in a duct
    temp += 8 * ((x > 3000) & (x < 3350))              # dry sandy stretch
    i = int(np.argmax(temp))
    csv("ch24-dts.csv", "m,c", [(f"{a:.0f}", f"{b:.2f}") for a, b in zip(x, temp)])
    lines = ["fibre temperature profile along WS1 at full output (synthetic):",
             f"  hottest point {temp[i]:.1f} C at {x[i]:.0f} m (road crossing in a duct)",
             f"  dry stretch 3,000-3,350 m: {temp[(x > 3000) & (x < 3350)].max():.1f} C",
             f"  elsewhere about {np.median(temp):.0f} C",
             "  distributed temperature sensing in the fibre beside the",
             "  cable finds the few metres that set the rating: the",
             "  crossing, not the kilometres of open trench; the duct can",
             "  be filled with bentonite, the dry stretch backfilled - or",
             "  the rating of the whole feeder stays set by a few tens of",
             "  metres of it"]
    emit("h_dts", lines)


if __name__ == "__main__":
    factors()
    cyclic()
    skin()
    dielectric()
    overload()
    dts()
