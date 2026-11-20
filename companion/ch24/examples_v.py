"""Chapter 24 - sixth round: the soil survey turned into a design thermal
resistivity, the cable screen in a cross-country double earth fault,
and the PV string cable chosen over the plant's life.

Run from the project root:   python -m companion.ch24.examples_v
Writes companion/ch24/expected/v_*.txt. Teaching values (A-321..A-325
extended).
"""
from __future__ import annotations

import math
import statistics

from companion.ch24 import sources as src
from companion.ch24.common import emit
from companion.ch24.examples_h import ampacity, t_soil
from plantp import cables as cb

PROBES = [0.82, 0.95, 1.10, 0.88, 1.35, 1.02, 0.91, 1.48, 1.20, 0.99, 1.62, 1.05,
          0.93, 1.28, 1.15, 0.87, 1.75, 1.08, 0.97, 1.31]      # K m/W, dry season


def soil_survey() -> None:
    ordered = sorted(PROBES)
    p90 = ordered[math.ceil(0.9 * len(ordered)) - 1]
    lines = ["soil thermal resistivity along the collector routes (20 probes,",
             "  dry season, teaching):",
             f"  mean {statistics.mean(PROBES):.2f}, median {statistics.median(PROBES):.2f},"
             f" 90th percentile {p90:.2f}, highest {max(PROBES):.2f} K m/W"]
    for name, rho in (("design on the mean", statistics.mean(PROBES)), ("design on the 90th", p90),
                      ("design on the worst", max(PROBES))):
        lines.append(f"  {name:22s} rho {rho:.2f}: 630 mm2 rating {ampacity(70, t_soil(rho, 0.8)):.0f} A")
    lines += ["  the mean hides the dry patches that set the hot spot (lesson",
              "  H's DTS profile); designing on a high percentile, or on the",
              "  worst with thermal backfill where the probes found it, is",
              "  the usual answer - the survey (season, depth, spacing) is",
              "  evidence the rating rests on (U-093)"]
    emit("v_soil", lines)


def cross_country() -> None:
    e_ll = 33e3
    z_loop = 4.0                                   # ohm, two cables and the earth path
    i = e_ll / z_loop
    lines = ["a cross-country fault: a second earth fault on another phase while",
             "  the first is still on (resistance-earthed 33 kV, teaching):",
             f"  line voltage {e_ll / 1e3:.0f} kV through a loop of about {z_loop:.0f} ohm"
             f" -> {i / 1e3:.1f} kA",
             "  screen Cu mm2   withstand 0.3 s kA   0.5 s kA   1 s kA"]
    for mm2 in (16, 25, 35):
        lines.append(f"  {mm2:13d}   {cb.withstand_ka(mm2, 0.3, src.K_CU):18.1f}"
                     f"   {cb.withstand_ka(mm2, 0.5, src.K_CU):8.1f}"
                     f"   {cb.withstand_ka(mm2, 1.0, src.K_CU):6.1f}")
    need = cb.adiabatic_mm2(i / 1e3, 0.5, src.K_CU)
    lines += ["  the 400 A resistor does not limit this fault: it flows phase",
              "  to phase through the earth and the screens; the feeder's",
              "  overcurrent relay sees it as a phase fault and clears it in",
              f"  about 0.3 s - 35 mm2 holds; a slower clearing (0.5 s) would",
              f"  need {need:.0f} mm2 - so the screen size and the relay setting",
              "  are checked together, and the first earth fault is cleared",
              "  before a second can join (ch 26)"]
    emit("v_crosscountry", lines)


def pv_cable() -> None:
    i, l_m, hours, price, rate, years = 13.0, 120.0, 1600.0, 70.0, 0.075, 25
    annuity = (1 - (1 + rate) ** -years) / rate
    strings = 420 * 10
    lines = ["PV string cable size over the plant's life (120 m loop, 13 A,",
             "  1,600 equivalent full-load hours, teaching costs):",
             "  mm2   loss W   MWh/yr (all strings)   PV of loss k u   extra copper k u"]
    base_cost = {4: 0.0, 6: 0.25, 10: 0.70}           # u per m extra over 4 mm2
    for mm2 in (4, 6, 10):
        r = 0.0222 / mm2 * 1.15                       # ohm/m Cu at 70 C
        w = i ** 2 * r * l_m
        mwh = w * hours * strings / 1e6
        pv = mwh * price * annuity / 1e3
        extra = base_cost[mm2] * l_m * strings / 1e3
        lines.append(f"  {mm2:3d}   {w:6.0f}   {mwh:20.0f}   {pv:14.0f}   {extra:16.0f}")
    lines += ["  6 mm2 saves more in losses than its copper costs over 4 mm2;",
              "  10 mm2 does not pay back at these prices - the economic size",
              "  is a number from the hours and the price, checked against",
              "  the drop (lesson E) and the connectors' size range"]
    emit("v_pvcable", lines)


if __name__ == "__main__":
    soil_survey()
    cross_country()
    pv_cable()
