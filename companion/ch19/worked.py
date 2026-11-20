"""Chapter 19 - small worked calculations quoted in the text (E01 ...) and
numerical answers to the end-of-chapter problems (P01 ...).

Run from the project root:   python -m companion.ch19.worked
Writes companion/ch19/expected/worked.txt and solutions.txt.
"""
from __future__ import annotations

import math

from companion.ch19.common import emit
from plantp import storage as st

E: list[str] = []
P: list[str] = []


def e(i, t):
    E.append(f"{i}: {t}")


def p(i, t):
    P.append(f"{i}: {t}")


def worked() -> None:
    e("E01", f"cell energy 314 Ah x 3.2 V: {314 * 3.2 / 1000:.4f} kWh")
    e("E02", f"module 52 x 3.2 V: {52 * 3.2:.1f} V; rack 416 x 3.6 V: {416 * 3.6:,.1f} V")
    e("E03", f"C-rate 20 MW / 40 MWh: {20 / 40:.2f} C; current {0.5 * 314:.0f} A")
    e("E04", f"heat per cell at 154 A in 0.4 mohm: {154 ** 2 * 0.0004:.2f} W")
    e("E05", f"leak 60 mA for 7 days in 314 Ah: {0.06 * 24 * 7 / 314 * 100:.2f} % SOC")
    e("E06", f"offset 0.5 A for 24 h in 314 Ah: {0.5 * 24 / 314 * 100:.2f} % SOC")
    e("E07", f"Arrhenius, 0.5 eV, 25 to 35 C: x {math.exp(0.5 / 8.617e-5 * (1 / 298.15 - 1 / 308.15)):.2f}")
    e("E08", f"usable at the POC, 40 x 0.8 x sqrt(0.86): {40 * 0.8 * math.sqrt(0.86):.1f} MWh")
    e("E09", f"nominal for 25 MWh at health 0.70: {25 / (0.8 * math.sqrt(0.86) * 0.7):.1f} MWh")
    e("E10", f"cycles to end of life at 80 % depth: {4000 * 0.8 ** -1.3:,.0f}")
    e("E11", f"rack short circuit 1,352 V / 0.108 ohm: {1352 / 0.108 / 1000:.1f} kA")
    e("E12", f"cells for 40 MWh of 18 Wh cells: {40e6 / 18:,.0f}")
    e("E13", f"weakest-cell loss 308.0 of 314 Ah: {100 * (1 - 308.0 / 314):.1f} %")
    e("E14", f"cells 39,936 x 5.5 kg: {39936 * 5.5 / 1000:.0f} t")
    emit("worked", E)


def solutions() -> None:
    p("P01", f"energy of a 280 Ah, 3.2 V cell: {280 * 3.2 / 1000:.3f} kWh")
    p("P02", f"NMC 100 Ah x 3.7 V: {100 * 3.7 / 1000:.3f} kWh")
    p("P03", f"module of 16 cells, 3.2 V: {16 * 3.2:.1f} V")
    p("P04", f"rack of 400 cells at 3.65 V: {400 * 3.65:,.0f} V")
    p("P05", f"cells in series for 1,500 V at 3.6 V: {math.floor(1500 / 3.6)}")
    p("P06", f"C-rate of 30 MW on 60 MWh: {30 / 60:.2f} C")
    p("P07", f"hours inside 10-90 % at 0.5 C: {0.8 / 0.5:.1f} h")
    p("P08", f"I^2R of 314 A in 0.25 mohm: {314 ** 2 * 0.00025:.1f} W")
    p("P09", f"one-way efficiency of 86 % round trip: {math.sqrt(0.86):.3f}")
    p("P10", f"usable of 40 MWh in 5-95 %: {40 * 0.9:.0f} MWh")
    p("P11", f"SOC error of 2 mV at 1 mV/%: {2 / 1:.0f} %")
    p("P12", f"SOC error of 2 mV at 7.5 mV/%: {2 / 7.5:.2f} %")
    p("P13", f"offset 0.05 A for 30 days in 314 Ah: {0.05 * 720 / 314 * 100:.1f} %")
    p("P14", f"calendar fade 0.02 sqrt(9): {0.02 * 3:.2f}")
    p("P15", f"cycles to end of life at 50 % depth: {4000 * 0.5 ** -1.3:,.0f}")
    p("P16", f"loss per year, 365 cycles at 100 % depth: {0.2 * 365 / 4000 * 100:.2f} %")
    p("P17", f"health after 12 years at 2 %/yr: {100 - 2 * 12:.0f} %")
    p("P18", f"year when 2 %/yr reaches 84.2 %: {(1 - 0.842) / 0.02:.1f}")
    p("P19", f"nominal for 20 MWh at the POC, health 0.8: {20 / (0.8 * math.sqrt(0.86) * 0.8):.1f} MWh")
    p("P20", f"DC power for 20 MW at 0.927: {20 / math.sqrt(0.86):.1f} MW")
    p("P21", f"charge needed for 25 MWh at 86 %: {25 / 0.86:.1f} MWh")
    p("P22", f"heat of 4,992 cells at 9.5 W: {4992 * 9.5 / 1000:.1f} kW")
    p("P23", f"end-of-life heat at x 1.8: {47 * 1.8:.0f} kW")
    p("P24", f"envelope gain 1.5 kW/K x (40 - 25) K: {1.5 * 15:.1f} kW")
    p("P25", f"container DC bus, 12 racks x 12.5 kA: {12 * 12.5:.0f} kA")
    p("P26", f"accept a 1 % lot with n 50, c 0: {0.99 ** 50:.3f}")
    p("P27", f"chance one cell is in a sample of 125 of 2,000: {125 / 2000 * 100:.2f} %")
    p("P28", f"OCV drop for 60 mA, 7 days, at 30 % SOC: {st.ocv_drift_mv(60, 314, 7, 0.30):.2f} mV")
    p("P29", f"expected cells, p 0.5, chain of 26 each side: {1 + 2 * sum(0.5 ** k for k in range(1, 27)):.2f}")
    p("P30", f"minutes to the module edge at 20 min a cell: {20 * 26:,d}")
    p("P31", f"throughput of 365 cycles of 32 MWh: {365 * 32:,d} MWh")
    p("P32", f"trucks for 220 t at 20 t: {220 / 20:.0f}")
    p("P33", f"present cost of 1,000 k u in year 8 at 6 %: {1000 / 1.06 ** 8:.0f} k u")
    p("P34", f"price after 8 years at -4 %/yr: {250 * 0.96 ** 8:.1f} k u/MWh")
    p("P35", f"charge power at 0.2 C, 3.3 V, 39,936 cells: {0.2 * 314 * 3.3 * 39936 / 1e6:.1f} MW")
    p("P36", f"cost per MWh at 6 h: Li-ion {(150 + 250 * 6) / 6:.0f}, flow {(600 + 120 * 6) / 6:.0f} k u")
    p("P37", f"cross-over (600 - 150) / (250 - 120): {(600 - 150) / (250 - 120):.2f} h")
    p("P38", f"pre-charge resistor for 10 A at 1,331 V: {1331 / 10:.1f} ohm")
    p("P39", f"time constant 66.5 ohm x 20 mF: {66.5 * 0.020:.2f} s")
    p("P40", f"energy of 20 mF at 1,000 V: {0.5 * 0.020 * 1000 ** 2 / 1000:.1f} kJ")
    p("P41", f"leakage at 50 kohm, 1,498 V: {1498 / 50e3 * 1000:.1f} mA")
    p("P42", f"auxiliary share 567 / 10,817: {100 * 567 / 10817:.1f} %")
    p("P43", f"standby week 8.97 of 32.1 MWh: {100 * 8.97 / 32.1:.1f} %")
    p("P44", f"limit 1.5 mV in sd of the leaky cells (3.45, 0.5): {(3.45 - 1.5) / 0.5:.1f}")
    p("P45", f"pulse resistance rise 0.25 to 0.293 mohm: {100 * (0.293 / 0.25 - 1):.0f} %")
    p("P46", f"warranty floor in year 6 at 2.5 %/yr: {40.13 * (1 - 0.025 * 6):.2f} MWh")
    p("P47", f"Faraday for M 96.5 g/mol: {96485 / 3.6 / 96.5:.0f} mAh/g")
    p("P48", f"LFP for 280 Ah at 170 mAh/g: {280e3 / 170 / 1000:.2f} kg")
    p("P49", f"busbar current at 0.25 C: {0.25 * 5.02e6 / 1352:,.0f} A")
    p("P50", f"capacity error, SOC errors 0.5 % each over 60 %: "
             f"{100 * math.hypot(0.005, 0.005) / 0.6:.2f} %")
    p("P51", f"battery area with s 4 m: {(4 * 12.2 + 3 * 4) * (2 * 2.5 + 4):.0f} m2")
    p("P52", f"discharge time of 29.8 MWh at 15 MW: {29.8 / 15:.2f} h")
    p("P53", f"energy on a truck at 20 % SOC: {5.02 * 0.2:.2f} MWh")
    p("P54", f"usable of 40.13 MWh in 15-85 %: {40.13 * 0.7:.1f} MWh")
    p("P55", f"cycles, DC / nominal: {10817 / math.sqrt(0.86) / 40.13:.0f}")
    p("P56", f"rise with 2 of 3 units of 60 kW: {(118 - 120) / 6:.1f} K/h (falls)")
    p("P57", f"balancing 2 % of 314 Ah at 150 mA, 2 h a day: {0.02 * 314 / 0.15 / 2:.0f} days")
    p("P58", f"spares mean, 768 x 0.003 x 16/52: {768 * 0.003 * 16 / 52:.2f}")
    p("P59", f"usable at the POC at 73.6 % health: {40.13 * 0.8 * math.sqrt(0.86) * 0.736:.1f} MWh")
    p("P60", f"energy lost a year to a 2 % SOC margin: "
             f"{40.13 * 0.04 * math.sqrt(0.86) * 365:,.0f} MWh")
    p("P61", f"reserve 3 MWh, shifting lost: {3 * math.sqrt(0.86) * 365:,.0f} MWh a year")
    p("P62", f"reversible heat at 0.10 mV/K, 157 A, 298 K: {157 * 298.15 * 0.10e-3:.2f} W")
    p("P63", f"rise at 0.8 K/W and 9.9 W: {0.8 * 9.9:.1f} K")
    p("P64", f"Arrhenius 25 to 30 C, 0.5 eV: x {math.exp(0.5 / 8.617e-5 * (1 / 298.15 - 1 / 303.15)):.2f}")
    p("P65", f"yearly cost of 13,032 k u at 8 %, 15 y, 2 % opex: "
             f"{13032 * (0.08 / (1 - 1.08 ** -15) + 0.02):,.0f} k u")
    p("P66", f"two detectors, rate 0.1, test 6 months: {100 * (0.1 * 0.5) ** 2 / 3:.3f} %")
    p("P67", f"local isolation 1 + 0.5 + 0.05: {1 + 0.5 + 0.05:.2f} s")
    p("P68", f"wear cost 20 u on 10,357 MWh: {20 * 10357 / 1000:,.1f} k u")
    p("P69", f"losses of 100 MWh through, half each way: "
             f"{50 * (1 / math.sqrt(0.86) - 1) + 50 * (1 - math.sqrt(0.86)):.1f} MWh")
    p("P70", f"calendar fade 9 months at 25 C, 50 %: {100 * 0.02 * math.sqrt(0.75):.2f} %")
    emit("solutions", P)


if __name__ == "__main__":
    worked()
    solutions()
