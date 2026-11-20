"""Chapter 18 - small worked calculations quoted in the text (E01 ...) and
numerical answers to the end-of-chapter problems (P01 ...).

Run from the project root:   python -m companion.ch18.worked
Writes companion/ch18/expected/worked.txt and solutions.txt.
"""
from __future__ import annotations

import math

from companion.ch18.common import emit
from plantp import architecture as ar
from plantp.yieldrisk import annuity

E: list[str] = []
P: list[str] = []


def e(i, t):
    E.append(f"{i}: {t}")


def p(i, t):
    P.append(f"{i}: {t}")


def worked() -> None:
    e("E01", f"AC chain 0.983 x 0.98 x 0.9 x 0.98: {0.983 * 0.98 * 0.9 * 0.98:.3f}")
    e("E02", f"DC chain 0.99 x 0.9 x 0.99 x 0.983: {0.99 * 0.9 * 0.99 * 0.983:.3f}")
    e("E03", f"current, 20 MW at 33 kV, pf 0.95: {float(ar.current_ka(20, 33, 0.95)):.3f} kA")
    e("E04", f"loss, 0.368 kA in 0.64 ohm: {3 * 0.368 ** 2 * 0.64:.3f} MW")
    e("E05", f"charging, 132 kV, 0.20 uF/km, 7.06 km: "
             f"{ar.charging_mvar(132, 0.20, 7.06):.2f} Mvar")
    e("E06", f"line outages 0.006/km x 7.06 km x 12 h x 33.7 MW: "
             f"{0.006 * 7.06 * 12 * 33.7:.0f} MWh/yr")
    e("E07", f"transformer 0.01/yr x 4,380 h x 33.76 MW: {0.01 * 4380 * 33.76:,.0f} MWh/yr")
    e("E08", f"annuity factor 6 %, 20 y: {annuity(0.06, 20):.2f}; yearly per k u with"
             f" 2 % opex: {1 / annuity(0.06, 20) + 0.02:.4f}")
    e("E09", f"dry-season demand 433 + 326 + 326 + 433: {433 + 326 + 326 + 433} m3")
    e("E10", f"modules 10 x 21 x 20 x 26: {10 * 21 * 20 * 26:,d}; at 1 L each:"
             f" {10 * 21 * 20 * 26 / 1000:.1f} m3")
    e("E11", f"2 MW headroom for about 8,000 producing hours: {2 * 8000 / 1000:.0f} GWh")
    e("E12", f"one 63 MVA transformer at pf 0.95: {63 * 0.95:.2f} MW")
    e("E13", f"string inverter failure, 12.37 MW / 200 x 24 h: {12.37 / 200 * 24:.2f} MWh")
    e("E14", f"central inverter failure, 12.37 MW / 10 x 72 h: {12.37 / 10 * 72:.1f} MWh")
    e("E15", f"AC round trip 0.98 x 0.9 x 0.98: {0.98 * 0.9 * 0.98:.3f}; x 227 MWh:"
             f" {227 * 0.98 * 0.9 * 0.98:.0f} MWh")
    e("E16", f"Q at the POC, 100 MW at pf 0.95: {100 * math.tan(math.acos(0.95)):.1f} Mvar")
    e("E17", f"transformer Q, 0.12 x 105.3^2 / 126: {0.12 * 105.3 ** 2 / 126:.1f} Mvar")
    e("E18", f"feeder of five blocks, 25 MW at 33 kV, pf 0.95: "
             f"{float(ar.current_ka(25, 33, 0.95)):.3f} kA")
    e("E19", f"line loss at 66 kV against 132 kV: x {(132 / 66) ** 2:.0f}")
    e("E20", f"RO feed for 1,529 m3 at 70 %: {1529 / 0.7:,.0f} m3; brine"
             f" {1529 / 0.7 - 1529:,.0f} m3")
    e("E21", f"break-even chance 400 / 1,622: {400 / 1622:.3f}")
    e("E22", f"island peak 200/0.9 + 30/0.85 x 6: {200 / 0.9 + 30 / 0.85 * 6:.0f} kVA")
    e("E23", f"spares mean, 40 x 0.125 x 8/52: {40 * 0.125 * 8 / 52:.2f}")
    e("E24", f"data a day, 1.068e9 samples x 16 bytes: {1.068e9 * 16 / 1e9:.0f} GB")
    emit("worked", E)


def solutions() -> None:
    p("P01", f"PV via AC battery at 0.97/0.97/0.92 cells: {0.983 * 0.97 * 0.92 * 0.97:.3f}")
    p("P02", f"DC gain on 1,000 MWh shifted, 86.7 % vs 85.0 %: {1000 * (0.867 - 0.850):.0f} MWh")
    p("P03", f"current at 66 kV, 20 MW, pf 0.95: {float(ar.current_ka(20, 66, 0.95)):.3f} kA")
    p("P04", f"loss ratio 33 to 66 kV, same R: {(66 / 33) ** 2:.0f}")
    p("P05", f"drop, R 0.64, X 0.47 ohm, 20 MW, pf 0.95, 33 kV: "
             f"{float(ar.drop_pct(20, 33, 0.64, 0.47, 0.95)):.2f} %")
    p("P06", f"charging of an overhead line, 0.009 uF/km: "
             f"{ar.charging_mvar(132, 0.009, 7.06):.2f} Mvar")
    p("P07", f"cable 240 h repair, 0.002/km, 7.06 km, 33.7 MW: "
             f"{0.002 * 7.06 * 240 * 33.7:.0f} MWh/yr")
    p("P08", f"double circuit loss: half of 754: {754 / 2:.0f} MWh")
    p("P09", f"yearly cost of 1,620 k u at 0.1072: {1620 * 0.1072:.1f} k u")
    p("P10", f"value of 394 MWh at 50 u/MWh: {394 * 50 / 1000:.1f} k u")
    p("P11", f"wind + PV AC / export: (60 + 50) / 100 = {110 / 100:.2f}")
    p("P12", f"transformer capacity, 2 x 63 MVA x 0.95 / 110 MW: {2 * 63 * 0.95 / 110:.2f}")
    p("P13", f"N-1 export with one 63 MVA unit at pf 0.95: {63 * 0.95:.1f} MW")
    p("P14", f"battery energy / power 40 / 20: {40 / 20:.0f} h")
    p("P15", f"mean POC power 295.86 GWh / 8760: {295.86e3 / 8760:.2f} MW")
    p("P16", f"half-year transformer event at 33.76 MW: {33.76 * 4380 / 1000:.1f} GWh")
    p("P17", f"value of that event at 50 u/MWh: {33.76 * 4380 * 50 / 1e6:.2f} million u")
    p("P18", f"tank for 1,518 m3 in steps of 100 m3: {math.ceil(1518 / 100) * 100} m3")
    p("P19", f"tank with a 900 m3 reserve: {1600 + 900} m3")
    p("P20", f"staff water 25 x 120 L x 31 d: {25 * 120 * 31 / 1000:.0f} m3")
    p("P21", f"cleaning 3 x 109.2 m3: {3 * 109.2:.1f} m3")
    p("P22", f"well 1,500 m3/month as L/s: {1500e3 / (30 * 86400):.2f} L/s")
    p("P23", f"dust 10,800 m3 at 40 m3 a working day: {10800 / 40:.0f} days;"
             f" 40 m3 a day as L/s: {40e3 / 86400:.2f}")
    p("P24", f"N-squared pairs of 9 systems: {9 * 8 // 2}")
    p("P25", f"interface share 18 of 36: {100 * 18 / 36:.0f} %")
    p("P26", f"failures, 200 x 0.1 against 10 x 0.5: {200 * 0.1:.0f} and {10 * 0.5:.0f}")
    p("P27", f"tie cable 3.0 km at 95 k u/km: {3.0 * 95:.0f} k u")
    p("P28", f"two strings at 33 kV, 40 MW, pf 0.95: "
             f"{float(ar.current_ka(40, 33, 0.95)):.3f} kA")
    p("P29", f"derate 2 %/K at 45 C: {100 * (1 - 0.02 * 5):.0f} % of rating")
    p("P30", f"weighted score 25x4 + 20x5 + 15x5 + 10x(4+4+5+4): "
             f"{25 * 4 + 20 * 5 + 15 * 5 + 10 * (4 + 4 + 5 + 4)}")
    p("P31", f"curtailment at 100 MW of 295.86 GWh at POC: {100 * 0.23 / 295.86:.2f} %")
    p("P32", f"extra GWh per MW from 90 to 100 MW: {1.80 / 10:.2f}")
    p("P33", f"collector cost 13.26 km at 165 k u/km: {13.26 * 165:,.0f} k u")
    p("P34", f"busbar fault, half of 33.76 MW for 48 h: {0.5 * 33.76 * 48:.0f} MWh")
    emit("solutions", P)


if __name__ == "__main__":
    worked()
    solutions()
