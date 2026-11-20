"""Chapter 28 - small worked examples (E-lines) and the numerical answers
of the exercises (P-lines), each computed here.

Run from the project root:   python -m companion.ch28.worked
Writes companion/ch28/expected/worked.txt and solutions.txt.
"""
from __future__ import annotations

import math

from companion.ch28.common import emit
from plantp import gridstudy as gs


def worked() -> None:
    z9 = gs.thevenin(900, 6)
    d = gs.ndz(0.85, 1.10, 49.0, 51.0, 1.0)
    lines = [f"E01 Thevenin of 900 MVA, X/R 6 on 100 MVA: z = {z9.real:.4f} + j{z9.imag:.4f} pu",
             f"E02 POC rise for 100 MW at Q = 0, 1,500 MVA X/R 8: "
             f"{100 * gs.thevenin(1500, 8).real:.2f} %",
             f"E03 POC fault current, 1,500 MVA, c 1.1: {1.1 * 1500 / (math.sqrt(3) * 132):.2f} kA",
             f"E04 blind zone dP/P for 0.85-1.10 pu: {d['dp'][0]:+.3f} to {d['dp'][1]:+.3f}",
             f"E05 WSCR of 100 MW at 1,500 and 80 MW at 1,500 MVA: "
             f"{gs.wscr([1500, 1500], [100, 80]):.2f}",
             f"E06 extra current after a 20 deg jump, x 0.15: "
             f"{gs.phase_jump_current(20, 0.15):.2f} pu",
             f"E07 surge on closing at 10 deg through 0.2 pu: {gs.sync_power(1, 1, 0.2, 10):.2f} pu",
             f"E08 POC voltage change for 10 Mvar at 900 MVA: {100 * 10 / 900:.2f} %"]
    emit("worked", lines)


def solutions() -> None:
    z = gs.thevenin(1200, 10)
    r9 = gs.thevenin(900, 6).real
    d1 = gs.ndz(0.90, 1.10, 49.0, 51.0, 1.0)
    d2 = gs.ndz(0.85, 1.10, 49.5, 50.5, 2.0)
    out = [f"P01 1,200 MVA, X/R 10 on 100 MVA: |z| {abs(z):.4f}, R {z.real:.5f}, X {z.imag:.4f} pu",
           f"P02 fault current at 132 kV, 1,200 MVA: {1200 / (math.sqrt(3) * 132):.2f} kA;"
           f" with c 1.1 {1.1 * 1200 / (math.sqrt(3) * 132):.2f}",
           f"P03 SCR of a 120 MW plant on 900 MVA: {900 / 120:.1f}",
           f"P04 rise for 60 MW at Q = 0 on 900 MVA, X/R 6: {100 * 0.6 * r9:.2f} %",
           f"P05 Q that cancels it: -P/(X/R) = {-60 / 6:.0f} Mvar",
           f"P06 ESCR, 900 MVA with 20 Mvar of shunt, 100 MW: {gs.escr(900, 20, 100):.1f}",
           f"P07 WSCR, 100 MW at 1,500 and 100 MW at 1,000 MVA: "
           f"{gs.wscr([1500, 1000], [100, 100]):.2f}",
           f"P08 blind zone dP/P for 0.90-1.10 pu: {d1['dp'][0]:+.3f} to {d1['dp'][1]:+.3f}",
           f"P09 blind zone dQ/P for 49.5-50.5 Hz, quality factor 2: "
           f"{d2['dq'][0]:+.4f} to {d2['dq'][1]:+.4f}",
           f"P10 extra current after a 15 deg jump, x 0.2: "
           f"{gs.phase_jump_current(15, 0.2):.3f} pu",
           f"P11 surge on closing at 8 deg through 0.25 pu: {gs.sync_power(1, 1, 0.25, 8):.3f} pu",
           f"P12 slip 0.15 Hz, +/-10 deg window: {20 / (360 * 0.15):.2f} s",
           f"P13 initial RoCoF, 300 MW lost of 5,000 MW, H 5: {-300 / 5000 * 50 / (2 * 5):.2f} Hz/s",
           f"P14 settled deviation, 20 % on 5 % droop, D 1: "
           f"{-300 / (0.2 * 5000 / (0.05 * 50) + 5000 / 50):.2f} Hz",
           f"P15 apparent R, 2 ohm fault, infeed ratio 10: {2 * (1 + 10):.0f} ohm + line R",
           f"P16 line current, 80 MW at 132 kV, unity pf: {80e6 / (math.sqrt(3) * 132e3):.0f} A",
           f"P17 load losses at 80 % against 100 %: {0.8 ** 2:.2f}",
           f"P18 no-load losses of 199 kW for a year: {0.199 * 8760 / 1e3:.2f} GWh",
           f"P19 two transformers, 0.01 failures/yr, 720 h: {100 * 2 * 0.01 * 720 / 8760:.2f} %",
           f"P20 810 MWh at 70 u/MWh: {810 * 70 / 1e3:.0f} k u",
           f"P21 latency with a 0.5 s scan (rest as c_restore): {0.5 + 0.2 + 0.3 + 0.5:.1f} s",
           f"P22 30 MW change at 10 MW/min: {30 / 10:.0f} min",
           f"P23 reconnection loss at 50 MW, 60 s, 10 %/min: "
           f"{50 * 60 / 3600 + 0.5 * 50 * 5 / 60:.1f} MWh",
           f"P24 loop gain ki/S_sc, 1,500 on 300 and on 1,500 MVA: {1500 / 300:.0f} and"
           f" {1500 / 1500:.0f} 1/s",
           f"P25 reactive current, k 2 at 0.6 pu: {2 * (1 - 0.6):.1f} pu",
           f"P26 dip 0.5 with k 2 and x 0.1: {(0.5 + 0.1 * 2) / (1 + 0.1 * 2):.3f} pu"]
    emit("solutions", out)


def solutions2() -> None:
    """Numerical answers of the exercises added with the later lessons."""
    out = [f"P27 kappa for X/R 10: {1.02 + 0.98 * math.exp(-0.3):.3f}",
           f"P28 peak current, 7.79 kA and kappa 1.69: {1.69 * math.sqrt(2) * 7.79:.1f} kA",
           f"P29 angle after 0.3 s of 2 Hz/s drift: {360 * 0.5 * 2 * 0.3 ** 2:.0f} deg",
           f"P30 three 33 kV circuits, 100 MW, 0.06 ohm/km, 12 km: "
           f"{3 * (100e6 / (math.sqrt(3) * 33e3)) ** 2 * 0.06 * 12 / 3 / 1e6:.2f} MW",
           f"P31 dP at 50.4 Hz, 5 % droop, 100 MW, 0.2 Hz deadband: {-0.2 / 2.5 * 100:.0f} MW",
           f"P32 loss-equivalent length, three turbines 1 km apart: {(9 + 4 + 1) / 9:.2f} km",
           f"P33 battery Q left, 8 MW dispatch + 4 MW reserve on 20 MVA: "
           f"{math.sqrt(400 - 144):.0f} Mvar",
           f"P34 V2 with k2 3 and x 0.08 (0.30 from the grid): {0.30 / (1 + 3 * 0.08):.3f} pu",
           f"P35 reactive current, k 2.5 at 0.63 pu: {2.5 * (1 - 0.63):.2f} pu",
           f"P36 WSCR with a fourth plant: "
           f"{gs.wscr([1500, 1500, 1095, 1500], [100, 80, 60, 50]):.1f}",
           f"P37 Q(U) 4 %, source 1.05 on 900 MVA: U "
           f"{(1.05 + 46 / (0.04 * 900)) / (1 + 46 / (0.04 * 900)):.3f}",
           f"P38 fault level after 10 years at 3 %: {1500 * 1.03 ** 10:.0f} MVA",
           f"P39 annuity factor, 7.5 % and 25 years: {(1 - 1.075 ** -25) / 0.075:.2f}",
           f"P40 daily volume of 532 values/s at 8 bytes: {532 * 86400 * 8 / 1e9:.2f} GB",
           f"P41 initial RoCoF, 100 MW lost of 5,000 MW, H 4: {-100 / 5000 * 50 / 8:.3f} Hz/s",
           f"P42 teaching need for giving at 1.08 pu: {0.33 * (1.10 - 1.08) / 0.10:.3f} Q/Pmax"]
    emit("solutions2", out)


if __name__ == "__main__":
    worked()
    solutions()
    solutions2()
