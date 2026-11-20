"""Chapter 12 - numerical answers to the end-of-chapter problems (P01 ...).
Criteria-based problems are answered in the text.

Run from the project root:   python -m companion.ch12.solutions
Writes companion/ch12/expected/solutions.txt.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch12 import lab_d, sources
from companion.ch12.common import emit
from plantp import irradiance as ir, solar

OUT: list[str] = []


def p(pid: str, text: str) -> None:
    OUT.append(f"{pid}: {text}")


def level_1() -> None:
    p("P01", f"declination 21 Jun {float(solar.declination(172)):.2f} deg,"
             f" 21 Dec {float(solar.declination(355)):.2f} deg")
    eot = float(solar.equation_of_time(42))
    noon = 12 - eot / 60
    p("P02", f"11 Feb: E_t {eot:+.1f} min -> solar noon"
             f" {int(noon)}:{round((noon % 1) * 60):02d}")
    p("P03", f"G0n day 3 {float(ir.g0n(3)):.0f}, day 185 {float(ir.g0n(185)):.0f} W/m2")
    phi, d = math.radians(34), math.radians(float(solar.declination(172)))
    ws = math.acos(-math.tan(phi) * math.tan(d))
    h0 = 24 / math.pi * float(ir.g0n(172)) * (math.cos(phi) * math.cos(d) * math.sin(ws)
                                             + ws * math.sin(phi) * math.sin(d)) / 1e3
    p("P04", f"H0 on 21 June at 34 N: {h0:.2f} kWh/m2 a day")
    kt = 600 / (float(ir.g0n(80)) * math.cos(math.radians(50)))
    p("P05", f"k_t = 600 / (G0n(80) cos 50) = {kt:.3f}")
    p("P06", f"air mass at zenith 48.2 deg: {float(ir.air_mass(48.2)):.3f}")
    cs = [float(ir.clear_sky_haurwitz(math.cos(math.radians(z)))) for z in (0, 45, 70)]
    p("P07", f"Haurwitz at 0, 45, 70 deg: {cs[0]:.0f}, {cs[1]:.0f}, {cs[2]:.0f} W/m2")
    p("P08", f"DNI = (700 - 200) / cos 35 = {(700 - 200) / math.cos(math.radians(35)):.0f} W/m2")
    p("P09", f"DHI = 650 - 600 cos 40 = {650 - 600 * math.cos(math.radians(40)):.0f} W/m2")
    e = [float(ir.erbs_diffuse_fraction(x)) for x in (0.2, 0.5, 0.85)]
    o = [float(ir.orgill_hollands_diffuse_fraction(x)) for x in (0.2, 0.5, 0.85)]
    p("P10", f"Erbs k_d at 0.2, 0.5, 0.85: {e[0]:.3f}, {e[1]:.3f}, {e[2]:.3f}")
    p("P11", f"Orgill-Hollands: {o[0]:.3f}, {o[1]:.3f}, {o[2]:.3f}")
    b, s, g = ir.poa_isotropic(800.0, 700.0, 150.0, 0.95, 25.0)
    p("P12", f"isotropic POA: beam {float(b):.0f} + sky {float(s):.0f} + ground"
             f" {float(g):.1f} = {float(b + s + g):.0f} W/m2")
    sky = 150 * (0.5 * 1.2 + 0.5 * (1 + math.cos(math.radians(25))) / 2)
    p("P13", f"Hay-Davies sky, A_i 0.5, R_b 1.2: {sky:.1f} W/m2"
             f" (isotropic {150 * (1 + math.cos(math.radians(25))) / 2:.1f})")
    d_dec = math.radians(float(solar.declination(355)))
    p("P14", f"day length at 34 N: equinox 12.00 h; 21 Dec"
             f" {2 * math.degrees(math.acos(-math.tan(phi) * math.tan(d_dec))) / 15:.2f} h")
    p("P15", f"noon elevation 21 June at 34 N: 90 - 34 + 23.45 = {90 - 34 + 23.45:.2f} deg")
    p("P16", f"offset -4 W/m2 on a 150 W/m2 day: {-4 / 150 * 100:.1f} %")
    p("P17", f"6.12 mV / 8.50 uV per W/m2 = {6.12e-3 / 8.50e-6:.0f} W/m2")
    p("P18", f"sensor 3 %, modules 1 % dirty: PR x {(1 - 0.01) / (1 - 0.03):.4f}")
    lim = ir.qc_limits(0.5, 1361.0)
    p("P19", f"GHI physically possible at mu 0.5: {float(lim['ghi_phys']):.1f} W/m2")
    p("P20", f"GHI extremely rare at mu 0.5: {float(lim['ghi_rare']):.1f} W/m2")
    p("P21", f"sqrt(2^2 + 1^2 + 1.5^2 + 0.6^2) = {ir.combine_uncertainty(2, 1, 1.5, 0.6):.2f} %")
    p("P22", f"P90 with u 4 %: {100 * (1 - 1.2816 * 0.04):.2f} % of P50"
             f" ({-1.2816 * 4:.2f} %)")
    p("P23", f"ten years, sd 2.7 %: {2.7 / math.sqrt(10):.2f} %")
    p("P24", f"2,050 x 1,980 / 2,010 = {ir.long_term_ratio([2050], [2010], [1980]):,.1f}"
             " kWh/m2")
    p("P25", "UTC labels read as +04:00: everything 4 h early; noon at 08:02")
    p("P26", f"20 channels x 4 bytes x 1 Hz: {20 * 4 * 3600 * 24 * 365 / 1e6:,.0f} MB a year")


def level_2() -> None:
    p("P27", "cosine error curve: annual GHI -0.65 %; sun below 20 deg -2.9 %")
    p("P28", "offset -4 W/m2 x 4,660 h = -18.6 kWh/m2 (-0.96 %)")
    p("P29", "PR 0.862 with the pyranometer, 0.889 with the reference cell")
    pk = sources.pack()
    pr = sources.provider()
    up = pk["cz"] > 0.087
    p("P30", f"provider GHI: MBE {ir.mbe(pr['ghi'][up], pk['ghi'][up]):+.1f} W/m2,"
             f" RMSE {ir.rmse(pr['ghi'][up], pk['ghi'][up]):.0f} W/m2")
    p("P31", f"provider DNI: MBE {ir.mbe(pr['dni'][up], pk['dni'][up]):+.1f} W/m2,"
             f" RMSE {ir.rmse(pr['dni'][up], pk['dni'][up]):.0f} W/m2")
    lt = sources.long_term()
    p("P32", f"long-term GHI 1,947.2 x {lt['annual'].mean() / lt['annual'][-1]:.4f} ="
             f" {1947.178 * lt['annual'].mean() / lt['annual'][-1]:,.1f} kWh/m2")
    p("P33", "monthly regression: 1,918.9 kWh/m2")
    p("P34", "GHI P50 1,920; P90 long-term 1,852; P90 one year 1,825 kWh/m2")
    p("P35", "POA P50 2,120; P90 long-term 2,030; P90 one year 2,005 kWh/m2")
    p("P36", "40 deg tilt: Hay-Davies 2,113 vs isotropic 2,058 kWh/m2 (+2.70 %)")
    p("P37", "Hay-Davies optimum near 30 deg (2,151 kWh/m2); 25 deg 2,150")
    p("P38", "far horizon: 218 h behind it, beam loss 1.7 kWh/m2 (0.08 %)")
    p("P39", "two-hour gaps filled in k_t: bias -12.1 W/m2, RMSE 32.0 W/m2")
    p("P40", "drift 0.06 %/week: trend -3.5 %/yr = 4.9 standard errors")
    p("P41", "one sample per 10 min: daily sum -1.2 %, RMS of 10-min values 97 W/m2")
    p("P42", "1 % less irradiance -> 0.83 % less energy (Plant P model)")
    p("P43", "share of GHI before noon: 0.500 correct, 0.379 one hour late")
    p("P44", "K_T June 0.732, December 0.468")
    p("P45", "year GHI / clear sky = 1,947 / 2,231 = 0.873")
    p("P46", "Orgill vs Erbs: DNI -1.7 %, POA -0.1 %")
    p("P47", f"23 June 12:00: k_t = 1030 / (1316.6 x 0.975) = {1030 / (1316.6 * 0.975):.3f}")


def level_3() -> None:
    p("P48", "energy: ground 111,402 MWh, provider 110,765 MWh (-0.6 %)")
    p("P49", "long-term energy 110,082 MWh (-1.2 %)")
    p("P50", "faulty year: as logged -4.3 %, after the six steps -0.3 %")
    p("P51", "sensor cleaning: weekly +0.63 %, monthly +2.86 %, never +11.12 % PR")
    p("P52", "station cell cleaned weekly: rate 0.150 vs 0.156 %/day, interval +2 %")
    d = 111_402 - 110_082
    p("P53", f"long-term correction: {d:,} MWh a year = {d * 50 / 1e3:.0f} k u at 50 u/MWh")
    p("P54", f"uncorrected -1.5 % drift: energy {-0.83 * 1.5:.2f} %")
    p("P55", f"12 h missing of 744: recovery {100 * (1 - 12 / 744):.1f} %")
    p("P56", f"sensitivity -1.1 % over 2 years, linear: at 1 year {-1.1 / 2:.2f} %")
    p("P57", f"daily cleaning 10 min: {365 * 10 / 60:.0f} h a year")
    e = lab_d.pv_energy_mwh(sources.pack()["ghi"] * 1.02, sources.pack()["dni"] * 1.02,
                            sources.pack()["dhi"] * 1.02)
    p("P58", f"provider 2 % high everywhere: energy {e:,.0f} MWh"
             f" ({100 * (e / 111_402 - 1):+.2f} %)")


def more() -> None:
    """Problems on the orientation, albedo, spectrum, SCADA and typical-year
    lessons (P59 onwards)."""
    pk = sources.pack()
    from companion.ch10 import pvyear10
    poa = pvyear10.poa()["poa"]
    p("P59", "tracker over fixed 25 deg: year +25.7 %, June +51 %, December -7.6 %")
    g = 0.70 * pk["ghi"].sum() * (0.02 + 0.5 * 0.25) / poa.sum()
    p("P60", f"bifacial gain at albedo 0.25: 0.70 x (0.02 + 0.125) x GHI/POA ="
             f" {100 * g:.2f} %")
    p("P61", "albedo 0.20 -> 0.30: gain 7.61 -> 10.78 % (+3.2 points)")
    p("P62", "share of GHI below air mass 2: 55.9 + 23.1 = 79.0 %")
    p("P63", "13:00 local (+04:00) = 09:00Z; 08:00Z = 12:00 local")
    p("P64", "hourly r: aligned 1.000, four hours off 0.324")
    p("P65", "typical year 1,911.9 vs mean 1,910.5; low year 1,814.8 (-5.0 %)")
    phi, d = math.radians(34), math.radians(float(solar.declination(355)))
    ws = math.acos(-math.tan(phi) * math.tan(d))
    h0 = 24 / math.pi * float(ir.g0n(355)) * (math.cos(phi) * math.cos(d) * math.sin(ws)
                                             + ws * math.sin(phi) * math.sin(d)) / 1e3
    p("P66", f"H0 on 21 December at 34 N: {h0:.2f} kWh/m2 a day")
    p("P67", f"sensor 1 %, modules 3 % dirty: PR x {(1 - 0.03) / (1 - 0.01):.4f}"
             f" ({100 * ((1 - 0.03) / (1 - 0.01) - 1):+.1f} %)")
    g0h = np.sum(pk["g0n"] * np.clip(pk["cz"], 0, None))
    p("P68", f"annual K_T = {pk['ghi'].sum() / 1e3:,.0f} / {g0h / 1e3:,.0f} ="
             f" {pk['ghi'].sum() / g0h:.3f}")
    d21 = math.radians(float(solar.declination(172)))
    ws21 = math.degrees(math.acos(-math.tan(phi) * math.tan(d21)))
    p("P69", f"21 June: sunset hour angle {ws21:.1f} deg; sunrise solar time"
             f" {12 - ws21 / 15:.2f} h")
    p("P70", "Hay-Davies over isotropic at 25 deg: +2.03 %")
    n = math.ceil((2 * 1.5 / 2.0) ** 2)
    p("P71", f"weekly sd 1.5 %, find a 2 % step at 2 sigma: average n >= {n} weeks")
    p("P72", "tilt 25 -> 30 deg (Hay-Davies): 2,150 -> 2,151 kWh/m2")
    p("P73", f"one-year P90 by scaling: 1,920 x (1 - 1.2816 x 0.038) ="
             f" {1920 * (1 - 1.2816 * 0.038):,.0f} kWh/m2")


def further() -> None:
    """Problems on the commissioning, uncertainty, aerosol, complementarity,
    spatial and ramp lessons (P74 onwards)."""
    p("P74", f"systematic sqrt(1.2^2 + 0.5^2 + 0.3^2) ="
             f" {math.sqrt(1.2 ** 2 + 0.5 ** 2 + 0.3 ** 2):.2f} %")
    p("P75", f"random 1.2 % over 182 independent days: {1.2 / math.sqrt(182):.3f} %")
    p("P76", f"sd of the sum (17.8, 21.4 MW, r -0.111):"
             f" {math.sqrt(17.8 ** 2 + 21.4 ** 2 - 2 * 0.111 * 17.8 * 21.4):.1f} MW;"
             f" r = 0: {math.sqrt(17.8 ** 2 + 21.4 ** 2):.1f} MW")
    p("P77", "dusty day: GHI -16.3 %, DNI -30 %, POA -15.7 %")
    p("P78", f"frozen clouds at 10 m/s, sensors 2.4 km apart: delay {2400 / 10:.0f} s")
    p("P79", f"largest one-minute step 215 W/m2 x 0.05 MW per W/m2 ="
             f" {215 * 0.05:.1f} MW")
    p("P80", "side by side: S3 at 1.033 of the median; 3.6 % put in")
    p("P81", "hourly r of solar and wind -0.111, monthly -0.410")


if __name__ == "__main__":
    level_1()
    level_2()
    level_3()
    more()
    further()
    emit("solutions", OUT)
