"""Chapter 14 - numerical answers to the end-of-chapter problems (P01 ...).
Criteria-based problems are answered in the text.

Run from the project root:   python -m companion.ch14.solutions
Writes companion/ch14/expected/solutions.txt.
"""
from __future__ import annotations

import math

from companion.ch14.common import emit
from plantp import siting as st, wind as w

OUT: list[str] = []


def p(pid: str, text: str) -> None:
    OUT.append(f"{pid}: {text}")


def level_1() -> None:
    p("P01", f"slope, 9 m over 150 m: {100 * 9 / 150:.1f} %")
    p("P02", f"hub 120 m, rotor 160 m: tip 200 m, 1.1 x tip = {1.1 * 200:.0f} m")
    p("P03", f"trapezoid (0,0) (1200,0) (1000,800) (0,800):"
             f" {st.polygon_area([(0, 0), (1200, 0), (1000, 800), (0, 800)]) / 1e4:.0f} ha")
    p("P04", f"GCR, 2 x 2.278 m table, pitch 9.1 m: {2 * 2.278 / 9.1:.2f}")
    p("P05", f"Jensen deficit at 8 D, Ct 0.75, D 150 m:"
             f" {w.jensen_deficit(0.75, 1200.0, 150.0):.4f}")
    p("P06", f"added turbulence at 4 D, Ct 0.6:"
             f" {1 / (1.5 + 0.8 * 4 / math.sqrt(0.6)):.3f}")
    p("P07", f"106 dB(A) at 800 m: {float(w.sound_pressure_level(106, 800.0)):.1f} dB(A)")
    p("P08", f"38 + 35 + 33 dB(A): {w.sum_levels([38.0, 35.0, 33.0]):.1f} dB(A)")
    p("P09", f"tip shadow at a 15 deg sun: {175 / math.tan(math.radians(15)):.0f} m")
    p("P10", f"speed-up of a 25 m hill over 600 m: {100 * 2 * 25 / 600:.1f} %")
    p("P11", f"pad 50 x 35 m on 8 %: {35 * 0.08 * 50 ** 2 / 8:.0f} m3 each way")
    _, t = st.minimum_spanning_tree([(0, 0), (3, 0), (3, 4)])
    p("P12", f"tree of (0,0), (3,0), (3,4) km: {t:.0f} km")
    p("P13", f"climb 45 m at 8 %: {45 / 0.08:.0f} m of road at least")
    p("P14", f"25 m3 a day: {25 / 86.4:.2f} L/s")
    p("P15", f"30 MWp: glass 14.1 ha / 0.40 x 1.25 = {14.1 / 0.40 * 1.25:.0f} ha")
    p("P16", f"expected flicker = 112 h x 0.7 x 0.8 x 0.5 = {112 * 0.7 * 0.8 * 0.5:.0f} h")
    p("P17", "two rows: 3 D 11.62 %, 8 D 6.75 % wake loss; +10.0 GWh a year")
    p("P18", f"(2, 1) to (5, 5) km: {math.hypot(3, 4):.0f} km")
    p("P19", f"10 deg as a slope: {100 * math.tan(math.radians(10)):.1f} %")
    p("P20", "corridor at 5 % margin: 784 ha, 700 m wide at x = 10.5 km")


def level_2() -> None:
    p("P21", "buildable: turbines 4,304 ha, PV 4,828 ha of 6,300 ha")
    p("P22", "slope classes: 81.9 % under 2 %, 5.0 % above 10 %")
    p("P23", "50 m raster 15.3 % steepest, 200 m raster 13.2 %")
    p("P24", "spring spare water: -0.5 to -2.0 L/s in Jun-Sep")
    p("P25", "W1 236.9 GWh (wake 0.50 %), W2 193.1 GWh (5.85 %)")
    p("P26", "ridge without speed-up 204.7 GWh: the hill adds 16 %")
    p("P27", "effective TI at 15 m/s: 0.197 at 4 D, 0.169 at 6 D (curve 0.184)")
    p("P28", "PV: 28.2 ha glass, 70.5 ha rows, 88 ha with roads (1.47 ha/MWp)")
    p("P29", "collector tree W1 9.32, W2 8.91 km; strings 18.21, 12.63 km")
    p("P30", "roads W1 9.50 km (12.4 %), W2 9.90 km (6.4 %)")
    p("P31", "pads: W1 2,174 m3, W2 522 m3 each way")
    p("P32", "noise at camp B: W1 34.9, W2 45.4, W2b 37.7 dB(A)")
    p("P33", "flicker at camp B, worst case: W1 36, W2 112, W2b 0 h/yr")
    p("P34", "W1: 5 turbines within 1 km of the nest, nearest 78 m")
    p("P35", "W2b: 196.9 GWh, wake loss 4.01 %, strings 13.26 km")
    p("P36", "routes: straight 6.41 km (inf), least cost 7.06 km, south 8.72 km")
    p("P37", "corridor 1 % 187 ha, 3 % 527 ha, 5 % 784 ha, 10 % 1,397 ha")
    p("P38", "farmland weight 1: 6.41 km with 3.42 km of fields; 2 to 8: 7.06 km")
    p("P39", "exposure: rangeland 126.0 ha (2.59 %), herders 3.1 ha (0.40 %)")
    p("P40", "export route 25 m from all eight strips")


def level_3() -> None:
    p("P41", f"W1 against W2b: +{236.9 - 196.9:.1f} GWh a year,"
             f" {(236.9 - 196.9) * 50 / 1e3:.1f} M u a year at 50 u/MWh")
    p("P42", f"W2b against W2: +{196.9 - 193.1:.1f} GWh,"
             f" {(196.9 - 193.1) * 50:,.0f} k u a year")
    p("P43", f"extra strings W2b against W2: {13.26 - 12.63:.2f} km")
    p("P44", f"least-cost against south route: {8.72 - 7.06:.2f} km shorter")
    p("P45", f"construction water by truck, 20 m3 a load: {12204 / 20:.0f} loads")
    p("P46", "PV block used 74 % (88 of 119 ha)")
    p("P47", f"tip height above sea level on the crest: {1262 + 175} m at most")
    p("P48", f"rows 8 D instead of 4 D: +{191.78 - 184.67:.2f} GWh a year")


def level_4() -> None:
    """Problems on the deeper sections (A2, B2, B3, C2, F2)."""
    p("P49", f"one degree of longitude at 34 N: {111.32 * math.cos(math.radians(34)):.1f} km")
    p("P50", f"area computed in degrees at 34 N: +{100 * (1 / math.cos(math.radians(34)) - 1):.0f} %")
    b = math.radians(25)
    ta = 4.556 * math.sin(b) / (11.4 - 4.556 * math.cos(b))
    d = 4.556 * (math.sin(b) + math.cos(b) * ta) / (ta - 0.04)
    p("P51", f"pitch on a 4 % slope to the north: {d:.2f} m (GCR {4.556 / d:.3f})")
    p("P52", "grading the PV block to a plane: 283,086 m3 each way, 0.48 m mean")
    p("P53", "temporary land of W2b: 8.1 ha; crane walk 7.20 km")
    r = 575.0
    p("P54", f"one turbine at {r:.0f} m: {float(w.sound_pressure_level(106, r)):.1f} dB(A)")
    p("P55", "W2b, target 36 dB(A) at the camp: 5 turbines in mode, 0.44 % energy")
    p("P56", "strings along the roads 21.34 km against 13.26 km straight (+61 %)")
    p("P57", "stagger 1,200 m: 196.88 GWh, 37.7 dB(A); 1,500 m inside the buffer")
    p("P58", "turn -20 deg: -2.3 GWh; +20 deg: +0.4 GWh")
    p("P59", "herders' straight routes cross W2b roads 1 and 2 times")
    p("P60", f"night mode for 5 of 12 turbines in 7 months: 1.81 x 5/12 x 7/12 ="
             f" {1.81 * 5 / 12 * 7 / 12:.2f} %")
    p("P61", f"cross-prediction, 2 km and 30 m higher: 0.5 + 0.5 x 2 + 1.0 x 3 ="
             f" {0.5 + 0.5 * 2 + 1.0 * 3:.1f} %")
    p("P62", "cross-prediction mean: W1 7.64 %, W2b 1.35 %")
    p("P63", f"ice-throw radius, D 160 m, hub 120 m: 1.5 x 280 = {1.5 * 280:.0f} m")
    p("P64", "W2b ice zones 476 ha; 7.1 km of site roads inside; no dwelling")
    p("P65", "visible from the west of the ridge: W1 12, W2b 6 turbines")
    p("P66", "ruggedness index: 0 % here, 17.8 % on terrain three times steeper")
    p("P67", "DC feeders: east edge 579 m mean, middle row 215 m, 5 x 2 grid 119 m")
    p("P68", "substation: chosen 27.20, best (7.00, 2.75) 25.07 weighted km (-7.8 %)")
    p("P69", "PV between the rows: 504 ha, 288 outside ice zones, 154 outside grazing")


if __name__ == "__main__":
    level_1()
    level_2()
    level_3()
    level_4()
    emit("solutions", OUT)
