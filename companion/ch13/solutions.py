"""Chapter 13 - numerical answers to the end-of-chapter problems (P01 ...).
Criteria-based problems are answered in the text.

Run from the project root:   python -m companion.ch13.solutions
Writes companion/ch13/expected/solutions.txt.
"""
from __future__ import annotations

import math

from companion.ch13.common import emit
from plantp import stats, windres as wr

OUT: list[str] = []


def p(pid: str, text: str) -> None:
    OUT.append(f"{pid}: {text}")


def level_1() -> None:
    p("P01", f"7.0 m/s at 100 m, shear 0.14, at 150 m:"
             f" {float(wr.power_law(7.0, 100, 150, 0.14)):.3f} m/s")
    p("P02", f"log law z0 0.1 m, 7.0 m/s at 100 m, at 60 m:"
             f" {float(wr.log_law(7.0, 100, 60, 0.1)):.3f} m/s")
    p("P03", f"shear from 6.0 at 60 m and 6.6 at 100 m:"
             f" {math.log(6.6 / 6.0) / math.log(100 / 60):.4f}")
    p("P04", f"TI with sigma 0.9 at 6 m/s: {0.9 / 6:.3f}; at 15 m/s with 1.5:"
             f" {1.5 / 15:.3f}")
    p("P05", f"density at 880 hPa and 5 C: {88000 / (287.05 * 278.15):.4f} kg/m3")
    p("P06", f"veer 12 deg between 60 and 100 m: {12 / 40:.2f} deg per m")
    p("P07", f"recovery with 2,628 flagged of 52,560: {100 * (1 - 2628 / 52560):.1f} %")
    p("P08", f"u* for z0 0.05 m, 8 m/s at 100 m: 0.4 x 8 / ln(2000) ="
             f" {0.4 * 8 / math.log(2000):.3f} m/s")
    p("P09", f"cosine error at 10 deg inclination:"
             f" {100 * (math.cos(math.radians(10)) - 1):+.2f} %")
    p("P10", f"return level, Gumbel 25.0 and 1.2, 50 years:"
             f" {stats.return_level(25.0, 1.2, 50):.1f} m/s")
    p("P11", f"50-year wind in 20 years: {stats.prob_exceed_in_life(50, 20):.3f}")
    p("P12", f"ratio method: 7.0 x 6.8 / 6.5 = {7.0 * 6.8 / 6.5:.3f} m/s")
    p("P13", f"least-squares slope r x sy/sx: 0.9 x 1.1 = {0.9 * 1.1:.2f}")
    p("P14", f"speed +2 %, sensitivity 1.6: energy +{1.6 * 2:.1f} %")
    p("P15", f"24 monthly means, sd 14.7 %: {14.7 / math.sqrt(24):.1f} %")
    p("P16", f"energy uncertainty from 2.58 % speed and 1.6: {1.6 * 2.58:.1f} %")
    p("P17", f"hub 150 m from 100 m, shear 0.233: speed x {1.5 ** 0.233:.4f}")
    p("P18", f"shear uncertainty 0.03 at 150 m: speed x {1.5 ** 0.03:.4f}")


def level_2() -> None:
    p("P19", "night shear 0.32, day 0.12, all hours 0.233 (A-250)")
    p("P20", "fitted 'roughness': night 3.4 m, morning/evening 0.84-0.86 m,"
             " day 0.02 m")
    p("P21", "veer: night +10 deg, day +2 deg between 60 and 100 m")
    p("P22", "TI mean 0.238 at 4.5 m/s, 0.113 at 12.5 m/s; 90 % quantile 0.131 at 15")
    p("P23", "density: January 1.103, July 1.009, mean 1.056 kg/m3")
    p("P24", "lidar at 100 m: slope 1.0051, r^2 0.9966; recovery 92.0 %")
    p("P25", "150 m: lidar 7.828, mast extrapolated 7.775 m/s (-0.7 %)")
    p("P26", "redundancy: wear from week 26 found in week 31")
    p("P27", "recovery: 100 m 98.6 %, 80 m 36.9 %, 60 m 98.9 %")
    p("P28", "icing found 147 of 288 records, no false alarm")
    p("P29", "80/100 ratio dips to 0.872 and 0.902 in 300-360 deg")
    p("P30", "shear 80/100 logged 0.3856 against true 0.2358")
    p("P31", "120 m energy with 80/100 shear: +4.13 %")
    p("P32", "sensitivity of energy to speed 1.60 % per %")
    p("P33", "energy uncertainty 4.1 %; 150 m extrapolation adds 2.0 %")
    p("P34", "extrapolation 120 m: one shear 19,410 vs row by row 19,392 MWh")
    p("P35", "sectors 240-330 deg: 70.7 % of the energy")
    p("P36", "Weibull ten-minute k 2.10, c 8.01; hourly k 2.11, c 8.01")
    p("P37", "MCP: linear 7.239, variance ratio 7.248, sector 7.248 m/s")
    p("P38", "MCP energy: linear 18,569, variance ratio 18,640 MWh per turbine")
    p("P39", "site year 7.066 m/s; long term 7.248 m/s (+2.6 %)")
    p("P40", "Gumbel location 26.72, scale 0.99; 50-year 30.6 m/s")


def level_3() -> None:
    p("P41", "farm long term 191.87 GWh vs 2023 186.69 GWh (+2.8 %)")
    p("P42", "P90 long term 181.8 GWh; one year 174.8 GWh")
    p("P43", f"value of +2.8 % on 186.69 GWh at 50 u/MWh:"
             f" {186.69 * 0.028 * 50:,.0f} k u a year")
    p("P44", f"faulty 80/100 shear, 12 turbines at 120 m: overstated by"
             f" {12 * (20217 - 19415) / 1e3:.2f} GWh a year")
    p("P45", f"one-year P90 spread: sqrt(4.1^2 + 5.6^2) = {math.sqrt(4.1 ** 2 + 5.6 ** 2):.1f} %")
    p("P46", f"MCP with r 0.951: least squares keeps r^2 = {0.951 ** 2:.3f} of the"
             " site variance")
    p("P47", f"mast 2 % slow from a wrong factor: energy {-1.6 * 2:.1f} %")
    p("P48", f"veer 10 deg over 40 m across 150 m rotor: {10 * 150 / 40:.0f} deg")


def level_4() -> None:
    """Problems on the deeper lessons (sections A2 .. D2)."""
    g = 9.81
    p("P49", f"dtheta/dz, 12.0 C at 10 m, 11.0 C at 92 m:"
             f" {-1 / 82 + 0.0098:+.4f} K/m (unstable)")
    ri = g / 280 * 0.02 / 0.025 ** 2
    p("P50", f"bulk Ri with 0.02 K/m, 280 K, 0.025 1/s: {ri:.2f}")
    p("P51", f"gust factor 1 + 2.5 x 0.16 = {1 + 2.5 * 0.16:.2f};"
             f" gust at 12 m/s {12 * (1 + 2.5 * 0.16):.1f} m/s")
    p("P52", "340 and 20 deg: vector mean 0 deg, arithmetic mean 180 deg")
    v_c, v_g = 0.0490 * 150 + 0.21, 0.0500 * 150 + 0.20
    p("P53", f"150 Hz: certificate {v_c:.2f}, generic {v_g:.2f} m/s"
             f" ({100 * (v_g / v_c - 1):+.2f} %)")
    p("P54", f"880 hPa, 120 m higher, 285 K:"
             f" {880 * math.exp(-g * 120 / (287.05 * 285)):.1f} hPa")
    c, s_ = math.cos(math.radians(30)), math.sin(math.radians(30))
    p("P55", f"lidar error, dw 0.2 m/s, beams 30 deg: {0.2 * c / (2 * s_):.3f} m/s")
    p("P56", f"scan circle at 150 m, 28 deg:"
             f" {2 * 150 * math.tan(math.radians(28)):.1f} m")
    p("P57", f"80 m to 140 m, u(shear) 0.04: {100 * math.log(140 / 80) * 0.04:.2f} %")
    p("P58", f"representative TI 0.12 + 1.28 x 0.03 = {0.12 + 1.28 * 0.03:.3f}")
    p("P59", f"five years, 4.1 and 5.6 %: {math.sqrt(4.1 ** 2 + 5.6 ** 2 / 5):.2f} %")
    p("P60", f"panel for 80 Wh a day, 3.5 sun-hours, 0.6: {80 / (3.5 * 0.6):.0f} W")
    p("P61", "Ri: night +1.24, morning +0.12, evening +0.13, midday -2.46")
    p("P62", "REWS: day 7.951, year 7.957, night 7.992, veer 7.888, jet 7.712")
    p("P63", "gust factor 1.20 / 1.32 / 1.50 at TI 0.08 / 0.13 / 0.20; g 2.5")
    p("P64", "wake loss: true 6.50 %, offset 6.22 %, turned layout 6.95 %")
    p("P65", "lidar losing nights: kept records -1.15 %, hourly-weighted -0.08 %")
    p("P66", "Weibull fits: -0.35 % (moments), -0.39 % (MLE), -0.36 % (LSQ)")
    p("P67", "reference step: ratio 1.006 -> 1.036 (t 6.8); long-term factor"
             " -1.5 %")
    p("P68", f"second year, +1.48 GWh P90 a year for 10 years at 50 u/MWh:"
             f" {1.48 * 50 * 10:,.0f} k u")
    p("P69", f"hub 120 m against 100 m: +{205.52 - 191.87:.2f} GWh a year,"
             f" {(205.52 - 191.87) * 50:,.0f} k u a year")
    p("P70", "representative TI at 15 m/s: 0.132 from 607 records")
    p("P71", f"POT 50-year, u 25, sigma 1.2, 3 storms a year:"
             f" {25 + 1.2 * math.log(3 * 50):.1f} m/s")
    p("P72", "50-year: maxima 32.7 (29.3-35.3), POT 30.9 (29.6-32.3), true 30.6")
    p("P73", f"50-year gust from 30.9 m/s, g 2.5, TI 0.10: {30.9 * 1.25:.1f} m/s")
    p("P74", "matrix MCP: 7.257 m/s, 18,935 MWh (+1.6 % against variance"
             " ratio)")
    p("P75", "night share 43.6/46.4/47.7 %; curtailed 0.17/0.25/0.32 GWh")
    p("P76", "80 m filling: hourly shear +0.09 %, 0.068 m/s; line +0.28 %,"
             " 0.168 m/s")


if __name__ == "__main__":
    level_1()
    level_2()
    level_3()
    level_4()
    emit("solutions", OUT)
