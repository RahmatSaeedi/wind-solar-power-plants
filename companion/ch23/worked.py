"""Chapter 23 - numerical answers of the small examples (E..) and of the
end-of-chapter problems (P..), each computed here.

Run from the project root:   python -m companion.ch23.worked
Writes companion/ch23/expected/worked.txt and solutions.txt.
"""
from __future__ import annotations

import math

from companion.ch23.common import emit
from companion.ch23.lab_g import series
from plantp import auxpower as ax


def amps(mva, kv, pf=1.0):
    return mva * 1e6 / (math.sqrt(3) * kv * 1e3) / pf


def worked() -> None:
    lines = [f"E01 current of 5 MW at 0.69 kV: {amps(5, 0.69):,.0f} A",
             f"E02 current of 20 MW at 33 kV, pf 0.95: {amps(20, 33, 0.95):.0f} A",
             f"E03 fault current of 250 kVA, 0.4 kV, z 0.045: {ax.sc_current_ka(250, 0.4, 0.045):.2f} kA",
             f"E04 dip of a 120 kVA start on 150 kVA, x 0.15: {ax.start_dip(120, 150, 0.15):.1%}",
             f"E05 series of 1,500 and 5,910 MVA: {series(1500, 5910):,.0f} MVA",
             f"E06 resistor for 400 A at 33 kV: {33e3 / math.sqrt(3) / 400:.1f} ohm"]
    emit("worked", lines)


def solutions() -> None:
    out = [f"P01 current of 100 MW at 132 kV: {amps(100, 132):.0f} A",
           f"P02 current of 0.5 MVA at 0.4 kV: {amps(0.5, 0.4):.0f} A",
           f"P03 phase voltage of 33 kV: {33 / math.sqrt(3):.2f} kV",
           f"P04 loss ratio 0.69 kV vs 33 kV, same power: {(33 / 0.69) ** 2:,.0f}",
           f"P05 section with 13 units of 5 MW at pf 0.95: {13 * 5 / 0.95:.1f} MVA",
           f"P06 feeder of 4 x 5 MW, pf 0.95 at 33 kV: {amps(20, 33, 0.95):.0f} A"
           f" ({amps(20, 33, 0.95) / 410:.0%} of 410 A)"]
    p, q, s = ax.demand([ax.Load("a", 30, 0.85, duty={"n": 0.7}),
                         ax.Load("b", 25, 0.95, duty={"n": 1.0})], "n")
    out.append(f"P07 demand of 30 kW x 0.7 (pf 0.85) + 25 kW (pf 0.95): {p:.1f} kW,"
               f" {s:.1f} kVA")
    out.append(f"P08 standard size for 167 kVA + 20 %: {ax.next_size(167, 0.2)} kVA")
    out.append(f"P09 standard size for 167 kVA + 50 %: {ax.next_size(167, 0.5)} kVA")
    out.append(f"P10 fault current of 500 kVA, 0.4 kV, z 0.06: {ax.sc_current_ka(500, 0.4, 0.06):.1f} kA")
    out.append(f"P11 dip of 200 kVA start on 250 kVA, z 0.045: {ax.start_dip(200, 250, 0.045):.1%}")
    out.append(f"P12 dip of 200 kVA start on 150 kVA generator, x 0.15: {ax.start_dip(200, 150, 0.15):.1%}")
    raw, ah = ax.battery_ah([(30, 120), (120, 1)])
    out.append(f"P13 DC duty 30 A x 2 h + 120 A x 1 min: raw {raw:.1f} Ah, sized {ah:.1f} Ah")
    out.append(f"P14 charger for 30 A standing, 150 Ah in 8 h: {ax.charger_a(30, 150, 8):.1f} A")
    kva, kwh = ax.ups(15, 0.9, 30)
    out.append(f"P15 UPS for 15 kW, pf 0.9, 30 min: {kva:.1f} kVA, {kwh:.2f} kWh")
    q, e = ax.hvac_kw(10, 0.3, 40, 24, 2)
    out.append(f"P16 room 10 kW, UA 0.3 kW/K, 40/24 C, sun 2 kW: {q:.1f} kW cooling,"
               f" {e:.2f} kW in")
    out.append(f"P17 series of 1,500, 5,910 and 525 MVA: {series(1500, 5910, 525):,.0f} MVA"
               f" = {series(1500, 5910, 525) / (math.sqrt(3) * 33):.2f} kA at 33 kV")
    out.append(f"P18 line impedance 7.06 km of 0.12 + j0.40: {7.06 * math.hypot(0.12, 0.40):.3f} ohm;"
               f" {132 ** 2 / (7.06 * math.hypot(0.12, 0.40)):,.0f} MVA")
    out.append(f"P19 line loss at 80 MW: {80 ** 2 * 0.847 / 132 ** 2:.3f} MW")
    out.append(f"P20 transformer 63 MVA z 0.12 as fault MVA: {63 / 0.12:.0f}")
    out.append(f"P21 resistor for 300 A at 33 kV: {33e3 / math.sqrt(3) / 300:.1f} ohm")
    out.append(f"P22 lighting 3,000 m2 x 2 + 250 m2 x 10 W/m2: {(3000 * 2 + 250 * 10) / 1e3:.1f} kW")
    qd = 400 * 0.040 / 3600
    out.append(f"P23 sump for 400 m2 at 40 mm/h: {qd * 1000:.2f} L/s;"
               f" {1000 * 9.81 * qd * 8 / 0.5 / 1e3:.2f} kW at 8 m head")
    i = 22e3 / (math.sqrt(3) * 400 * 0.85)
    dv = math.sqrt(3) * i * (1.15 * 0.85 + 0.08 * math.sin(math.acos(0.85))) * 0.12
    out.append(f"P24 22 kW at 0.85 over 120 m of 16 mm2: {i:.1f} A, drop {dv:.1f} V ({dv / 400:.1%})")
    out.append(f"P25 lead-acid life at 28 C (10 y at 20 C): {10 * 2 ** (-0.8):.1f} y")
    out.append(f"P26 fuel for 60 kW for 6 h at 0.27 L/kWh: {60 * 6 * 0.27:.0f} L")
    out.append(f"P27 UPS energy for 30 kW for 45 s: {30 * 45 / 3600:.2f} kWh")
    out.append(f"P28 inverter contribution 1.2 x 130 MW at 33 kV: {1.2 * amps(130, 33) / 1e3:.2f} kA")
    out.append(f"P29 earthing resistor energy 7.6 MW for 1 s: {7.6:.1f} MJ")
    out.append(f"P30 per-phase power check: 3 x 19.05 kV x 350 A = {3 * 19.053 * 350 / 1e3:.2f} MW")
    # answers of the per-unit, states, checks and trade-off lessons
    zb = lambda kv: kv ** 2 / 100.0
    a = complex(-0.5, math.sqrt(3) / 2)
    out += [f"P31 base impedance 132 kV / 100 MVA: {zb(132):.2f} ohm; 0.69 kV: {zb(0.69):.5f} ohm",
            f"P32 2.5 MVA, 6 % on 100 MVA: {0.06 * 100 / 2.5:.2f} pu; 63 MVA, 12 %: {0.12 * 100 / 63:.4f} pu",
            f"P33 0.5 pu to a 33 kV bus: {100 / 0.5:.0f} MVA, {100 / 0.5 / (math.sqrt(3) * 33):.2f} kA",
            f"P34 64 MVA at 0.69 kV: {64 / (math.sqrt(3) * 0.69):.1f} kA",
            f"P35 unit transformer 5 %: {100 / (0.3209 + 0.05 * 100 / 5.6):.1f} MVA,"
            f" {100 / (0.3209 + 0.05 * 100 / 5.6) / (math.sqrt(3) * 0.69):.1f} kA",
            f"P36 both transformers: {100 / (100 / 1500 + 0.0169 + 0.1905 / 2):.0f} MVA",
            f"P37 line 20 km x 0.4 ohm on 100 MVA: {8 / zb(132):.4f} pu",
            f"P38 chain of three links 0.99: {0.99 ** 3:.4f}; two paths 0.98, 0.995:"
            f" {1 - 0.02 * 0.005:.4f}",
            f"P39 10 kW at 230 V: {10e3 / 230:.1f} A; neutral of 60/50/40 A:"
            f" {abs(60 + 50 * a * a + 40 * a):.1f} A",
            f"P40 line losses 100 MW / 140 MW on 0.85 ohm:"
            f" {3 * (100e6 / (math.sqrt(3) * 132e3)) ** 2 * 0.847 / 1e6:.3f} /"
            f" {3 * (140e6 / (math.sqrt(3) * 132e3)) ** 2 * 0.847 / 1e6:.3f} MW",
            f"P41 start 60 kVA on 100 kVA, x'd 0.15: {ax.start_dip(60, 100, 0.15):.1%}",
            f"P42 K of a 20 % 5th harmonic: {(1 + 0.04 * 25) / 1.04:.2f};"
            f" 250 kVA at K 4: {250 * math.sqrt(1.1 / 1.4):.0f} kVA",
            f"P43 two sources of 6 h and 10 h a year: {6 * 10 / 8760:.4f} h",
            f"P44 maintenance + 40 kW at 0.9: {math.hypot(148.1 + 40, 68.0 + 40 * math.tan(math.acos(0.9))):.0f} kVA",
            f"P45 500 MVA, X/R 5, 100 MW: {0.2 / math.sqrt(26) * 100:.1f} %",
            f"P46 NER 300 A at 33 kV for 5 s: {300 ** 2 * (33e3 / math.sqrt(3) / 300) * 5 / 1e6:.1f} MJ"]
    emit("solutions", out)


if __name__ == "__main__":
    worked()
    solutions()
