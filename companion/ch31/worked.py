"""Chapter 31 - small worked examples (E-lines) and the numerical answers
of the exercises (P-lines), each computed here.

Run from the project root:   python -m companion.ch31.worked
Writes companion/ch31/expected/worked.txt and solutions.txt.
"""
from __future__ import annotations

import math

from companion.ch31.common import emit
from plantp import logistics as lg

CHART = [(12, 250.0), (16, 210.0), (20, 178.0), (24, 150.0), (28, 128.0)]


def worked() -> None:
    t, r = lg.axle_loads(100, 25, 30, 10, tractor_axles=3, tractor_share=0.1)
    lines = [f"E01 axles, 100 t on 10 axles, 10 % on tractor: {t:.0f} / {r:.0f} kN",
             f"E02 bridge, 1,500 kN over 10 m on a 20 m span, allowed 6,000 kN m: "
             f"{lg.bridge_moment_ratio(1500, 10, 20, 6000):.2f}",
             f"E03 convoy, 150 km at 50 and 10 km at 10 with 1 h stops: "
             f"{lg.convoy_time([(150, 50), (10, 10)], 1):.1f} h",
             f"E04 crane capacity at 18 m: {lg.chart_capacity(18, CHART):.0f} t",
             f"E05 wind on 100 m2 at 10 m/s, Cd 1.2: {lg.wind_on_load(10, 100) / 1e3:.1f} kN",
             f"E06 desiccant, 8 m3 for 6 months: {lg.desiccant_kg(8, 6):.1f} kg",
             f"E07 response, 40 km at 60 km/h, 10 + 20 min: {lg.response_time(40, 60, 10, 20):.0f} min"]
    emit("worked", lines)


def solutions() -> None:
    t, r = lg.axle_loads(160, 30, 42, 16, tractor_axles=4, tractor_share=0.05)
    out = [f"P01 nacelle trailer axle, 16 axles: {r:.0f} kN",
           f"P02 same on 12 axles: {lg.axle_loads(160, 30, 40, 12, 4, 0.05)[1]:.0f} kN",
           f"P03 bridge, 2,280 kN over 24 m on 32 m, allowed 9,000 kN m: "
           f"{lg.bridge_moment_ratio(2280, 24, 32, 9000):.2f}",
           f"P04 same on a 12 m span, allowed 4,200: {lg.bridge_moment_ratio(2280, 24, 12, 4200):.2f}",
           f"P05 point load 1,000 kN on 16 m, allowed 4,000: {lg.bridge_moment_ratio(1000, 0, 16, 4000):.2f}",
           f"P06 convoy 244 km (12/25, 180/50, 40/30, 6/10, 6/10) + 3 h: "
           f"{lg.convoy_time([(12, 25), (180, 50), (40, 30), (6, 10), (6, 10)], 3):.1f} h",
           f"P07 capacity at 22 m: {lg.chart_capacity(22, CHART):.0f} t",
           f"P08 use, 120 + 9 t at 20 m: {lg.lift_utilisation(120, 9, 20, CHART):.2f}",
           f"P09 use, 160 + 8 t at 17 m: {lg.lift_utilisation(160, 8, 17, CHART):.2f}",
           f"P10 wind on the rotor (555 m2) at 8 m/s: {lg.wind_on_load(8, 555) / 1e3:.1f} kN",
           f"P11 wind on a nacelle side (60 m2) at 10 m/s: {lg.wind_on_load(10, 60) / 1e3:.1f} kN",
           f"P12 desiccant, 12 m3 for 9 months: {lg.desiccant_kg(12, 9):.1f} kg",
           f"P13 laydown for 3 blades (74 x 4.2 m), factor 1.6: {lg.laydown_area([74 * 4.2] * 3):.0f} m2",
           f"P14 response, 70 km at 70 km/h, 15 + 30 min: {lg.response_time(70, 70, 15, 30):.0f} min",
           f"P15 drums for 185 km at 1 km a drum: {math.ceil(185 / 1.0)}",
           f"P16 truck loads of three drums: {math.ceil(186 / 3)}",
           f"P17 reels for 21.8 km of conductor at 2.5 km: {math.ceil(21.8 / 2.5)}",
           f"P18 loaded height, deck 0.30 + 4.50 m, clearance 4.85: margin {4.85 - 4.80:.2f} m",
           f"P19 standby, mean wait 5.6 h at 60 k u a day: {60 * 5.6 / 24:.1f} k u",
           f"P20 abnormal loads, 12 turbines x 9: {12 * 9}"]
    emit("solutions", out)


if __name__ == "__main__":
    worked()
    solutions()
