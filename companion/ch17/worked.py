"""Chapter 17 - small worked calculations quoted in the text (E01 ...) and
numerical answers to the end-of-chapter problems (P01 ...).

Run from the project root:   python -m companion.ch17.worked
Writes companion/ch17/expected/worked.txt and solutions.txt.
"""
from __future__ import annotations

import math

from companion.ch17.common import emit
from plantp import demand as dm

E: list[str] = []
P: list[str] = []


def e(i, t):
    E.append(f"{i}: {t}")


def p(i, t):
    P.append(f"{i}: {t}")


def worked() -> None:
    e("E01", f"30 MW for 8 h + 20 MW for 16 h: {30 * 8 + 20 * 16} MWh a day")
    e("E02", f"load factor, mean 28 MW, peak 52 MW: {28 / 52:.3f}")
    e("E03", f"coincidence, peaks 35 + 9 + 13 MW, peak of sum 52 MW: {52 / (35 + 9 + 13):.3f}")
    e("E04", f"growth 3 %/yr for 10 years: x {1.03 ** 10:.3f}")
    e("E05", f"battery 40 MWh, 90 % -> 10 %, eff 0.93, 0.2 MW: "
             f"{dm.critical_hours(0.2, 40, 20):.0f} h")
    e("E06", f"voltage rise, R 0.85 ohm, 100 MW, 132 kV: "
             f"{float(dm.voltage_rise(100, 0, 0.85, 2.8, 132)):.2f} %")
    e("E07", f"short-circuit ratio 1,500 MVA / 100 MW: {dm.short_circuit_ratio(1500, 100):.1f}")
    e("E08", f"line loss R 0.847 ohm at 100 MW, 132 kV: {0.847 * (100 / 132) ** 2:.3f} MW")
    emit("worked", E)


def solutions() -> None:
    p("P01", f"energy of 45 MW for 10 h and 25 MW for 14 h: {45 * 10 + 25 * 14} MWh")
    p("P02", f"load factor, 245,178 MWh, peak 51.83 MW: {245178 / (51.83 * 8760):.3f}")
    p("P03", f"mean of 245.2 GWh over a year: {245.2e3 / 8760:.2f} MW")
    p("P04", f"15-min peak 53.33 over hourly 51.83: +{100 * (53.33 / 51.83 - 1):.1f} %")
    p("P05", f"coincidence factor 51.83 / 56.92: {51.83 / 56.92:.3f}; diversity"
             f" {56.92 / 51.83:.3f}")
    p("P06", f"peak 51.83 MW at 3.5 %/yr after 10 years: {51.83 * 1.035 ** 10:.2f} MW")
    p("P07", f"years until 51.83 MW passes 63 MW at 2 %/yr: "
             f"{math.log(63 / 51.83) / math.log(1.02):.1f}")
    p("P08", f"battery hours, 200 kW, 40 MWh from 50 %: {dm.critical_hours(0.2, 40, 20, 0.5):.0f} h")
    p("P09", f"voltage rise, 100 MW and 32.9 Mvar, R 0.847, X 2.824: "
             f"{float(dm.voltage_rise(100, 32.9, 0.847, 2.824, 132)):.2f} %")
    p("P10", f"apparent power at 100 MW, pf 0.95: {100 / 0.95:.1f} MVA")
    p("P11", f"SCR, 1,500 MVA and 110 MW: {1500 / 110:.1f}")
    p("P12", f"line R, 0.12 ohm/km x 7.06 km: {0.12 * 7.06:.3f} ohm")
    p("P13", f"yearly line loss 754 MWh of 295.3 GWh: {100 * 754 / 295.3e3:.2f} %")
    p("P14", f"shallow cost 14.48 million u per MW of 110: {14.48e3 / 110:.0f} k u")
    p("P15", f"deep share 14.0 x 100/160: {14.0 * 100 / 160:.2f} million u")
    p("P16", f"aux transformer, 565 kW x 1.25 / 0.9: {565 * 1.25 / 0.9:.0f} kVA")
    p("P17", f"local use 179.1 of 295.3 GWh: {100 * 179.1 / 295.3:.1f} %")
    p("P18", f"open cells 7 of 66: {100 * 7 / 66:.1f} %")
    emit("solutions", P)


if __name__ == "__main__":
    worked()
    solutions()
