"""Chapter 24 - numerical answers of the small examples (E..) and of the
end-of-chapter problems (P..), each computed here.

Run from the project root:   python -m companion.ch24.worked
Writes companion/ch24/expected/worked.txt and solutions.txt.
"""
from __future__ import annotations

import math

from companion.ch24.common import emit
from plantp import cables as cb


def worked() -> None:
    lines = [f"E01 R of 0.125 ohm/km Al at 90 C: {cb.r_at(0.125, 90, 0.00403):.4f} ohm/km",
             f"E02 rating 520 A x 0.97 x 0.88 x 0.93 x 0.85: {cb.rating(520, {'a': .97, 'b': .88, 'c': .93, 'd': .85})[0]:.0f} A",
             f"E03 drop 368 A, 1.1 km, r 0.16, x 0.116, pf 0.95, 33 kV: {cb.drop_pct(368, 1.1, 0.16, 0.116, 0.95, 33):.2f} %",
             f"E04 least Al section for 12.5 kA, 1 s: {cb.adiabatic_mm2(12.5, 1, 94):.0f} mm2",
             f"E05 peak of 12.5 kA at X/R 14: {cb.peak_ka(12.5, 14):.1f} kA",
             f"E06 sag of 11 N/m over 300 m at 19 kN: {cb.sag_m(11, 300, 19000):.2f} m"]
    emit("worked", lines)


def solutions() -> None:
    out = [f"P01 R of 0.0778 ohm/km Al at 65 C: {cb.r_at(0.0778, 65, 0.00403):.4f}",
           f"P02 R of 1.15 ohm/km Cu at 70 C: {cb.r_at(1.15, 70):.3f}",
           f"P03 rating 410 A x 0.675: {410 * 0.675:.0f} A",
           f"P04 factor product 0.9 x 0.85 x 0.95: {0.9 * 0.85 * 0.95:.3f}",
           f"P05 current of 15 MW at 33 kV, pf 0.95: {15e6 / 0.95 / (math.sqrt(3) * 33e3):.0f} A",
           f"P06 drop of 276 A over 1.1 km of 240 mm2 (r 0.16, x 0.116): "
           f"{cb.drop_pct(276, 1.1, 0.16, 0.116, 0.95, 33):.2f} %",
           f"P07 loss of 368 A in 1.1 km at 0.16 ohm/km: {cb.loss_kw(368, 0.16, 1.1):.1f} kW",
           f"P08 annual loss of 200 A constant in 2 km at 0.1: {cb.annual_loss_mwh([200] * 8760, 0.1, 2):.1f} MWh",
           f"P09 least Cu section for 7.9 kA, 0.1 s: {cb.adiabatic_mm2(7.9, 0.1, 143):.1f} mm2",
           f"P10 withstand of 630 mm2 Al for 1 s: {cb.withstand_ka(630, 1, 94):.1f} kA",
           f"P11 withstand of 35 mm2 Cu for 0.5 s: {cb.withstand_ka(35, 0.5, 143):.2f} kA",
           f"P12 peak of 25 kA at X/R 10: {cb.peak_ka(25, 10):.1f} kA",
           f"P13 20 kA for 2 s against 25 kA 1 s: {'ok' if cb.short_time_ok(20, 2, 25, 1) else 'no'}",
           f"P14 charging of 10 km of 33 kV at 0.25 uF/km: {cb.charging_a(33, 0.25, 10):.1f} A",
           f"P15 sheath volts, 437 A, 400 m, s 140, d 105: {cb.sheath_v(437, 140, 105, 400):.1f} V",
           f"P16 conductor temp, 400 A, 0.1 ohm/km, 25 C, 2.0 K m/W: "
           f"{cb.conductor_temp(400, 1e-4, 25, 2.0):.0f} C",
           f"P17 sag, 11 N/m, 350 m, 19 kN: {cb.sag_m(11, 350, 19000):.2f} m",
           f"P18 capstan: 5 kN around 90 deg, mu 0.35: {5 * math.exp(0.35 * math.pi / 2):.2f} kN",
           f"P19 least bend radius of a 92 mm cable at 15 D: {15 * 92 / 1e3:.2f} m",
           f"P20 busbar force, 63 kA, 0.25 m: {2e-7 * 63000 ** 2 / 0.25 / 1e3:.2f} kN/m",
           f"P21 joints, 1.1 km sections on 0.5 km drums, 4 sections: {4 * (math.ceil(1.1 / 0.5) - 1)}",
           f"P22 coil voltage: 96.2 V less 5 A x 2 x 0.2 km x 8.78 ohm/km: "
           f"{96.2 - 5 * 2 * 0.2 * 8.784:.1f} V",
           f"P23 LV drop 68 A over 350 m of 95 mm2 Cu (0.193 at 20 C): "
           f"{cb.drop_pct(68, 0.35, cb.r_at(0.193, 70), 0.08, 0.85, 0.4):.2f} %",
           f"P24 PV of 100 MWh a year at 70 u for 25 y at 7.5 %: "
           f"{100 * 70 / 1e3 * (1 - 1.075 ** -25) / 0.075:.1f} k u"]
    # answers of the lessons added after the first draft (H to V)
    from companion.ch24.examples_h import ampacity, t_soil
    from companion.ch24.examples_m import ohl_amps
    xs2 = 8 * math.pi * 50 / 4e-5 * 1e-7
    out += [f"P25 soil 2.0 K m/W, 1.0 m, 75 mm: T4 = {t_soil(2.0, 1.0):.2f} K m/W",
            f"P26 ys for R' 4e-5 ohm/m: {xs2 ** 2 / (192 + 0.8 * xs2 ** 2):.3f}",
            f"P27 630 mm2 at 30 C ground: factor {math.sqrt(60 / 70):.3f}",
            f"P28 630 mm2 with 1.30 K m/W soil: {ampacity(70, t_soil(1.30, 0.8)):.0f} A",
            f"P29 DC time constant at X/R 20: {20 / (2 * math.pi * 50) * 1e3:.1f} ms",
            f"P30 arc 16 kA, 0.5 s, 500 V per phase: {3 * 500 * 16e3 * 0.5 / 1e6:.1f} MJ",
            f"P31 SF6 1 % of 54 kg at GWP 24,000: {54 * 0.01 * 24000 / 1e3:.1f} t CO2e a year",
            f"P32 Cpk mean 8.2, s 0.1, 7.6-8.8 mm: {min(8.8 - 8.2, 8.2 - 7.6) / 0.3:.2f}",
            f"P33 duct with 0.60 K m/W extra: {ampacity(70, t_soil(1.0, 0.8) + 0.60):.0f} A",
            f"P34 generator 200 kVA, xd 2.0: rated {200e3 / (math.sqrt(3) * 400):.0f} A,"
            f" steady {200e3 / (math.sqrt(3) * 400) / 2:.0f} A",
            f"P35 wind 25 m/s on 24.5 mm: {0.5 * 1.225 * 625 * 0.0245:.1f} N/m",
            f"P36 line rating at 45 C, 0.6 m/s: {ohl_amps(45, 0.6):.0f} A",
            f"P37 back-flash, 15 ohm footing: {30 * 15 + 15 * 30:.0f} kV",
            f"P38 overload class 20 at 5 x: {20 * (7.2 / 5) ** 2:.1f} s",
            f"P39 trefoil force, 60 kA, 0.15 m: {0.17 * 60 ** 2 / 0.15 / 1e3:.1f} kN/m",
            f"P40 relative life at 86 C: {2 ** ((90 - 86) / 8):.2f}",
            f"P41 inverter 3 MVA at 800 V: {3e6 / (math.sqrt(3) * 800):,.0f} A",
            f"P42 air for 10 kW, 10 K rise: {10e3 / (1.2 * 1005 * 10) * 3600:,.0f} m3/h",
            f"P43 pressure at 40 C from 1.40 bar at 20 C: {1.40 * 313.15 / 293.15:.2f} bar",
            f"P44 charging current, 1.5 uF per phase, 33 kV: {cb.charging_a(33, 1.5, 1):.1f} A",
            f"P45 earth bar 31.5 kA, 1 s, Cu: {cb.adiabatic_mm2(31.5, 1, 143):.0f} mm2",
            f"P46 screen 25 mm2 Cu for 0.3 s: {cb.withstand_ka(25, 0.3, 143):.1f} kA",
            f"P47 heater for 8 K, 18 m2 at 3.5 W/(m2 K): {18 * 3.5 * 8:.0f} W",
            f"P48 clamp force, M12 at 50 N m, K 0.2: {50 / (0.2 * 0.012) / 1e3:.1f} kN",
            f"P49 20 K rise at 60 % load, at full load: {20 / 0.6 ** 2:.0f} K",
            f"P50 markers, 10 km, 20 bends, 4 crossings: {10000 // 50 + 20 + 8}",
            f"P51 surface field, r 2.0 cm, D 400 cm, 145 kV:"
            f" {145 / math.sqrt(3) * math.sqrt(2) / (2.0 * math.log(200)):.1f} kV/cm",
            f"P52 echo 10 us at velocity factor 0.6: {0.6 * 299.79 * 10 / 2:.0f} m"]
    emit("solutions", out)


if __name__ == "__main__":
    worked()
    solutions()
