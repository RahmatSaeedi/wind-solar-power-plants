"""Chapter 10 - numerical answers to the end-of-chapter problems (P01 ...).
Criteria-based problems are answered in the text.

Run from the project root:   python -m companion.ch10.solutions
Writes companion/ch10/expected/solutions.txt.
"""
from __future__ import annotations

import math
import warnings

import numpy as np
from scipy.special import comb

from companion.ch10 import pvyear10
from companion.ch10.common import emit
from companion.ch10.examples_c import string_limits
from plantp import pvcell as pc

warnings.simplefilter("ignore", RuntimeWarning)
DS = pc.PVM_550_DS
H, C0, Q, KB = 6.62607015e-34, 2.99792458e8, 1.602176634e-19, 1.380649e-23
OUT: list[str] = []


def p(pid: str, text: str) -> None:
    OUT.append(f"{pid}: {text}")


def ev(nm: float) -> float:
    return H * C0 / (nm * 1e-9) / Q


def vt(t_c: float) -> float:
    return KB * (t_c + 273.15) / Q


def oc(n: int, c: int, q: float) -> float:
    return float(sum(comb(n, k) * q ** k * (1 - q) ** (n - k)
                     for k in range(c + 1)))


def level_1() -> None:
    p("P01", f"700 nm {ev(700):.3f} eV (absorbed); 1200 nm {ev(1200):.3f} eV"
             " (below 1.12 eV: passes)")
    p("P02", f"cut-off for 1.70 eV: {1239.84 / 1.70:.0f} nm")
    p("P03", f"V_t at 45 C: {1e3 * vt(45):.2f} mV")
    p("P04", f"V_oc per cell = 25 mV x ln(1e12 + 1) = "
             f"{0.025 * math.log(1e12 + 1):.3f} V")
    ff = 37.5 * 11.2 / (45.0 * 12.0)
    p("P05", f"FF {ff:.3f}; efficiency {37.5 * 11.2 / 2000:.3f}")
    p("P06", f"string 26 x 550 = {26 * 550 / 1e3:.2f} kW; 4200 strings "
             f"{4200 * 26 * 550 / 1e6:.2f} MWp")
    p("P07", f"a = 1.1 x 60 x {vt(25):.5f} = {1.1 * 60 * vt(25):.3f} V")
    p("P08", f"V_oc at -25 C {49.90 * (1 + 0.0027 * 50):.2f} V; at 70 C "
             f"{49.90 * (1 - 0.0027 * 45):.2f} V")
    p("P09", f"550 x 0.8 x (1 - 0.0035 x 25) = {550 * 0.8 * (1 - 0.0035 * 25):.1f} W")
    p("P10", f"NOCT rule: 30 + 25/800 x 900 = {30 + 25 / 800 * 900:.1f} C")
    p("P11", f"Faiman: 20 + 800/(25 + 6.84 x 3) = "
             f"{float(pc.faiman(20, 800, 3)):.1f} C")
    p("P12", f"IAM(70 deg) = {float(pc.iam_ashrae(math.cos(math.radians(70)))):.3f}")
    p("P13", f"900 + 0.8 x 100 = {900 + 0.8 * 100:.0f} W/m2")
    p("P14", f"thirds: 216 x (1/3)^2 x (1/3) / 72 = {216 / 9 / 3 / 72:.3f}")
    p("P15", f"P_a = 0.95^20 = {0.95 ** 20:.3f}")
    n = math.ceil(50e6 / 550)
    p("P16", f"{n:,} modules; {math.ceil(n / 31):,} pallets; "
             f"{math.ceil(n / 620)} containers")
    f20 = 0.98 - 0.0055 * 19
    p("P17", f"year 20 floor {f20:.4f} -> {550 * f20:.1f} W")
    p("P18", f"N_max = floor(1500 / 58.7) = {math.floor(1500 / 58.7)}")
    p("P19", f"N_min = ceil(880 / 35.3) = {math.ceil(880 / 35.3)}")
    p("P20", f"two strings: reverse {1 * DS.isc * 1.25:.1f} A < 25 A, no fuse")
    p("P21", f"pitch 4.556 / 0.35 = {4.556 / 0.35:.2f} m")
    f = 1 - 2.5 * math.sin(math.radians(10)) / math.sin(math.radians(35))
    p("P22", f"f(10 deg) = {f:.3f}")
    g02 = 1947 * 0.2 * (1 - math.cos(math.radians(25))) / 2
    p("P23", f"ground term with albedo 0.8: {4 * g02:.0f} kWh/m2 (0.2: "
             f"{g02:.0f}); daily x4")
    p("P24", f"6 mm2, 200 m at 70 C: {0.0172 * 1.1965 * 200 / 6:.3f} ohm")
    p("P25", f"mean loss 0.2 x 45 / 2 = {0.2 * 45 / 2:.1f} %")
    p("P26", f"T* / sqrt(2) = 27.3 / 1.414 = {27.3 / math.sqrt(2):.1f} d")
    p("P27", f"half plant, 1.5 L: {54600 * 1.5 / 1e3:.1f} m3")
    p("P28", f"PR = 111339 / (60.06 x 2150) = {111339 / (60.06 * 2150):.3f}")
    p("P29", f"specific yield {111339 / 60.06:.0f} kWh/kWp")
    s = 5e6 * 1.1 / (26 * 550)
    p("P30", f"{s:.1f} strings -> 384 = 16 x 24; DC/AC {384 * 26 * 550 / 5e6:.3f}")


def level_2() -> None:
    m = pvyear10.ref_sdm()
    one = 1 - math.exp(-64 * 0.012)
    two = 1 - math.exp(-2 * 64 * 0.012)
    p("P31", f"120 um at 1000 nm: {100 * one:.1f} % (one pass), {100 * two:.1f} %"
             " (two)")
    p("P32", f"25.7 mV x ln 10 = {25.7 * math.log(10):.1f} mV per cell")
    share = 1.12 * 12 * 60 / 1700
    vf = 0.75 / 1.12
    p("P33", f"share {100 * share:.1f} %, x {vf:.3f} x 0.75 -> "
             f"{100 * share * vf * 0.75:.1f} %")
    p("P34", "W(e) = 1 (1 x e^1 = e)")
    v = 49.8                                                   # fixed point
    i, hist = 0.2, []
    for _ in range(12):
        i = i + (m.i_l - m.i_0 * (math.exp((v + i * m.r_s) / m.a) - 1)
                 - (v + i * m.r_s) / m.r_sh - i)
        hist.append(i)
    slope = m.i_0 * m.r_s / m.a * math.exp((v + float(m.i(v)) * m.r_s) / m.a) \
        + m.r_s / m.r_sh
    p("P35", f"49.8 V: |1 + df/di| = {slope:.2f} > 1; iterates {hist[0]:.2f},"
             f" {hist[1]:.2f}, {hist[2]:.2f}..; true {float(m.i(v)):.3f} A")
    m2 = pc.SDM(m.i_l, m.i_0, m.a, 2 * m.r_s, m.r_sh)
    v2, i2, p2 = m2.mpp()
    p("P36", f"R_s doubled: P_mp {p2:.1f} W, FF {p2 / (m2.voc * m2.isc):.3f}"
             f" (was 0.789)")
    m3 = pc.SDM(m.i_l, m.i_0, m.a, m.r_s, m.r_sh / 2)
    lo = pc.at_conditions(m3, 200, 25, DS.alpha_isc).mpp()[2]
    p("P37", f"R_sh halved: 200 W/m2 relative efficiency "
             f"{lo / (0.2 * m3.mpp()[2]):.3f} (was 0.975)")
    a1 = pc.at_conditions(m, 800, 25, DS.alpha_isc).mpp()[2]
    a2 = pc.at_conditions(m, 800, 65, DS.alpha_isc).mpp()[2]
    p("P38", f"800 W/m2: {a1:.1f} W at 25 C, {a2:.1f} W at 65 C -> "
             f"{100 * (a2 / a1 - 1) / 40:.3f} %/K")
    p("P39", f"27 modules at -20 C: "
             f"{27 * pc.at_conditions(m, 1000, -20, DS.alpha_isc).voc:.0f} V")
    p("P40", f"553 / 1.005 = {553 / 1.005:.1f} W")
    noct = 30 + 25 / 800 * 1000
    fai = float(pc.faiman(30, 1000, 5))
    p("P41", f"NOCT {noct:.1f} C, Faiman {fai:.1f} C: {noct - fai:.1f} K ->"
             f" about {0.319 * (noct - fai):.1f} % power")
    p("P42", f"8 V x 12 A = 96 W on 0.0179 m2 = {96 / 0.0179 / 1e3:.1f} kW/m2")
    p("P43", f"23 x 0.55 + 0.6 = {23 * 0.55 + 0.6:.2f} V")
    p("P44", f"n 125, c 3 at 1.5 %: P_a = {oc(125, 3, 0.015):.3f}")
    p("P45", f"10 samples, 1 %: {1 - 0.99 ** 10:.3f}; n for 50 %: "
             f"{math.ceil(math.log(0.5) / math.log(0.99))}")
    y1 = 551 * 0.98 * 0.995
    p("P46", f"551 x 0.98 x 0.995 = {y1:.1f} W vs floor 539.0 W")
    p("P47", f"498 x 1.025 = {498 * 1.025:.1f} W < 511.8 W: shortfall proven")
    p("P48", f"mean of 1 - 0.005 t, t = 1..25: "
             f"{np.mean(1 - 0.005 * np.arange(1, 26)):.3f}")
    r = string_limits(26, -15.0, 72.0)
    p("P49", f"floor 1000 V: N_min = ceil(1000 / {r['v_mp_hot'] / 26:.2f}) = "
             f"{math.ceil(1000 / (r['v_mp_hot'] / 26))}; N_max 27: no N fits")
    p("P50", f"(N - 1) x 13.98 x 1.25 <= 25 -> N <= "
             f"{1 + math.floor(25 / (13.98 * 1.25))}")
    p("P51", f"21 x 13.98 x 1.25 = {21 * 13.98 * 1.25:.0f} A")
    a_lim = math.degrees(math.atan(math.sin(math.radians(25)) /
                                   (2 - math.cos(math.radians(25)))))
    p("P52", f"GCR 0.5: no shade above {a_lim:.1f} deg")
    p("P53", f"tower 100 m, sun 45 deg: {100 / math.tan(math.radians(45)):.0f} m")
    p("P54", f"square law: 0.80 x (4/3)^2 = {0.80 * (4 / 3) ** 2:.2f} %")
    p("P55", f"parallel: 0.96 x cos 25 x sin 25 = "
             f"{0.96 * math.cos(math.radians(25)) * math.sin(math.radians(25)):.3f}"
             " kN/m2")
    p("P56", f"1.2 % x 0.66 = {1.2 * 0.66:.2f} % of DC energy")
    p("P57", f"300 Mohm / 5460 = {300e6 / 5460 / 1e3:.1f} kohm")
    p("P58", f"1.2 -> 1.3: AC {100 * (119.85 / 112.94 - 1):.1f} % more; "
             f"clipped at 1.3 {3.293:.3f} GWh")
    t = math.sqrt(2 * 13104 / (50 * 112.9e3 / 365 * 0.003 * 0.85))
    p("P59", f"manual dry T* = {t:.1f} d")
    d = np.arange(10)
    y = np.array([0.1, 0.4, 0.7, 0.9, 1.3, 1.5, 1.8, 2.1, 2.4, 2.8])
    p("P60", f"least-squares slope {np.polyfit(d, y, 1)[0]:.3f} %/day")


def level_3() -> None:
    m = pvyear10.ref_sdm()
    w = pc.at_conditions(m, 700, 10, DS.alpha_isc)
    v, i, pw = w.mpp()
    p("P61", f"700 W/m2, cell 10 C: {pw:.1f} W at {v:.2f} V; string "
             f"{26 * v:.0f} V")
    c12 = pc.at_conditions(m, 1200, -15, DS.alpha_isc).voc
    c10 = pc.at_conditions(m, 1000, -15, DS.alpha_isc).voc
    p("P62", f"-15 C: V_oc {26 * c10:.0f} V at 1000, {26 * c12:.0f} V at 1200"
             " W/m2")
    p("P63", f"20 deg vs 25 deg: 2071 / 2086 - 1 = {100 * (2071 / 2086 - 1):.2f} %")
    p("P64", f"pitch 9.11 vs 11.39 m: land {100 * (1 - 9.11 / 11.39):.0f} % less;"
             " loss 0.23 % vs 0.07 %")
    p("P65", "GCR 0.6: portrait 1.13 %, landscape 0.38 % (c_rows)")
    p("P66", f"1.273 x 0.96 x 0.99 - 1 = {100 * (1.273 * 0.96 * 0.99 - 1):.1f} %")
    e = (0.0099 - 0.0066) * 0.66 * 115.62e3
    p("P67", f"6 mm2 saves (0.99 - 0.66) % x 0.66 x 115.6 GWh = {e:.0f} MWh"
             f" = {e * 50 / 1e3:.1f} k u/yr")
    p("P68", f"630 V: 0.052 % x 115.7 GWh = {0.00052 * 115.7e3:.0f} MWh/yr")
    p("P69", "aged 3 %: 159 h below 933 V (E32)")
    p("P70", f"extra 10,920 modules give {(119.85 - 112.94) * 1e6 / 10920:.0f}"
             f" kWh each; base {112.94e6 / 109200:.0f} kWh")
    p("P71", f"truck 30 d minus trigger: {340745 - 310025:,} u/yr")
    af10 = (1 - 1.07 ** -10) / 0.07
    p("P72", f"10-year break-even: 145,242 x {af10:.3f} = "
             f"{145242 * af10 / 1e6:.2f} million u")
    p("P73", "water a year: every 14 d 2,839 m3; trigger 1,529 m3")
    p("P74", f"548 - 9 = 539 < 550 < 548 + 9 = 557: neither proven")
    p("P75", f"(1 - 0.9952) x 60,060 kWp = {(1 - 0.9952) * 60060:.0f} kWp")
    p("P76", f"31 of a container with 5 % cracked: detect "
             f"{1 - 0.95 ** 31:.2f}")
    p("P77", f"113,400 x 0.0002 = {113400 * 2e-4:.0f} a year")
    p("P78", f"eight snowfalls, scale 1.94 x 8 / 5 = {1.94 * 8 / 5:.1f} %")
    p("P79", f"floating, 1100 V: about -550 V to +550 V; module step "
             f"{1100 / 26:.0f} V")
    n50 = math.ceil(50e6 / 550)
    p("P80", f"{n50:,} modules x 28 kg = {n50 * 28 / 1e3:,.0f} t; glass "
             f"{0.7 * n50 * 28 / 1e3:,.0f} t; Al {0.1 * n50 * 28 / 1e3:,.0f} t")
    ib = 17.09 * 1.076
    p("P81", f"17.09 x 1.076 = {ib:.2f} A (< 25 A fuse); x 20 = "
             f"{20 * ib:.0f} A > 350 A")
    p("P82", f"LID 1.5 % on 111.3 GWh: {0.015 * 111339:.0f} MWh/yr = "
             f"{0.015 * 111339 * 50 / 1e3:.1f} k u/yr")


def level_4() -> None:
    m = pvyear10.ref_sdm()
    v25 = pc.at_conditions(m, 1000, -25, DS.alpha_isc).voc
    v75 = pc.at_conditions(m, 1000, 75, DS.alpha_isc).mpp()[0]
    p("P83", f"N_max = floor(1500 / {v25:.2f}) = {math.floor(1500 / v25)};"
             f" N_min = ceil(900 / {v75:.2f}) = {math.ceil(900 / v75)}")
    s = 6.25e6 * 1.25 / (26 * 550)
    p("P84", f"6.25 MW x 1.25: {s:.1f} strings -> 546 = 21 x 26; DC/AC "
             f"{546 * 14300 / 6.25e6:.3f}")
    st = pvyear10.strings()
    pw, tc = st["p_string"], st["t_cell"]
    tw = (pw * tc).sum() / pw.sum()
    p("P85", f"energy-weighted cell {tw:.1f} C: -0.29 vs -0.35 %/K gives"
             f" about {0.06 * (tw - 25):.1f} %")
    p("P86", f"portrait loss 0.5 % between GCR 0.5 (0.23) and 0.6 (1.13): "
             f"GCR {0.5 + 0.1 * (0.5 - 0.23) / (1.13 - 0.23):.2f}")
    p("P87", f"200 Mohm wet, inverter 30 kohm: at most "
             f"{200e6 / 30e3:,.0f} modules per inverter")
    flt = 1 - 0.0055 * 14 - 0.02
    p("P88", f"year 15 floor {flt:.4f} x 550 = {550 * flt:.1f} W")
    p("P89", "see text: decision rule, sample size, stabilisation, translation")
    pt = 380 * 1000 / 700 / (1 - 0.0035 * 15)
    p("P90", f"380 W at 700 W/m2, 40 C: 380 x 1000/700 / (1 - 0.0035 x 15) ="
             f" {pt:.1f} W")
    dv = 0.10 * 112.9e3 / 365 * 50
    p("P91", f"storm +10 %: {dv:,.0f} u/day; truck pays back in "
             f"{16380 / dv:.1f} days")


if __name__ == "__main__":
    level_1()
    level_2()
    level_3()
    level_4()
    emit("solutions", OUT)
