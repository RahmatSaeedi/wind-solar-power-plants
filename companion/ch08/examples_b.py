"""Chapter 8, section B - machine construction: laminations and eddy losses,
winding factors, insulation (thermal life and converter voltage stress),
magnets and temperature, bearings, cooling.

Run from the project root:   python -m companion.ch08.examples_b
Writes companion/ch08/expected/b_*.txt and diagrams/data/ch08-*.csv.
Teaching values A-065, A-111, A-116, A-118, A-120 (fictional).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch08.common import csv, emit
from plantp import machines as m


def laminations() -> None:
    sigma, rho, b = 2.0e6, 7650.0, 1.5                         # A-118

    def eddy_w_kg(t_m, f):
        return math.pi ** 2 * sigma * t_m ** 2 * f ** 2 * b ** 2 / (6 * rho)

    lines = ["classical eddy-current loss p = pi^2 sigma t^2 f^2 B^2 / (6 rho),",
             f"  B {b} T, sigma 2 MS/m (A-118):"]
    for t_mm in (0.35, 0.50, 1.00):
        for f in (50.0, 57.75):
            lines.append(f"  sheet {t_mm:.2f} mm at {f:5.2f} Hz: "
                         f"{eddy_w_kg(t_mm / 1000, f):6.2f} W/kg")
    solid = eddy_w_kg(0.02, 50.0)
    lines += [f"  a solid 20 mm plate (formula far outside its range): "
              f"{solid:,.0f} W/kg",
              "loss grows with thickness squared: cores are stacks of thin,",
              "  insulated sheets. This is only the classical eddy part:",
              "  hysteresis (about proportional to f) and excess losses make",
              "  the measured total several times larger; data sheets give",
              "  the total in W/kg at stated B and f"]
    emit("b_laminations", lines)


def winding_factors() -> None:
    q, slot_deg = 3, 20.0                       # 3 slots per pole per phase
    lines = [f"distributed winding, q = {q} slots per pole and phase,",
             f"  {slot_deg:.0f} electrical deg per slot; k_w for orders "
             "1, 5, 7, 11, 13:"]
    rows = []
    for y in (1.0, 5 / 6, 7 / 9):
        parts = []
        for h in (1, 5, 7, 11, 13):
            kd = (math.sin(h * q * math.radians(slot_deg) / 2)
                  / (q * math.sin(h * math.radians(slot_deg) / 2)))
            kp = math.sin(h * y * math.pi / 2)
            parts.append(f"{abs(kd * kp):.3f}")
            rows.append((f"{y:.3f}", h, f"{abs(kd * kp):.4f}"))
        lines.append(f"  pitch {y:.3f}: " + ", ".join(parts))
    lines += ["  a 5/6 pitch gives up 3.4 % of the fundamental and cuts the",
              "  5th and 7th harmonics of the EMF to about a quarter"]
    emit("b_winding", lines)


def insulation() -> None:
    ea = 1.0e5                                                 # A-065
    lines = ["Arrhenius life relative to 130 C (Ea 100 kJ/mol, A-065):"]
    for t in (110, 120, 130, 140, 150):
        lines.append(f"  hot spot {t} C: life x {m.life_factor(t, 130, ea):5.2f}")
    v_dc = 1100.0
    lines += ["converter-fed winding (A-118): DC link 1100 V, fast switching",
              "  a reflected wave on a long cable can reach about",
              f"  {2 * v_dc:.0f} V peak line to line at the terminals, against",
              f"  {690 * math.sqrt(2):.0f} V peak of a 690 V sine: about "
              f"{2 * v_dc / (690 * math.sqrt(2)):.1f} times",
              "  so converter-fed insulation is designed and tested for "
              "repetitive",
              "  impulses (partial discharge), not only for the sine"]
    emit("b_insulation", lines)


def magnets() -> None:
    br20, alpha = 1.20, -0.0012                                # A-118
    lines = [f"NdFeB magnet: remanence {br20} T at 20 C, coefficient "
             f"{100 * alpha:.2f} %/K (A-118):"]
    for t in (20, 60, 100, 140):
        br = br20 * (1 + alpha * (t - 20))
        lines.append(f"  {t:3d} C: Br {br:.3f} T; EMF and torque per ampere "
                     f"x {br / br20:.3f}")
    lines += ["  hot magnets give less flux; too hot plus a strong opposing "
              "field",
              "  (a fault current) can demagnetise them for good: rotor "
              "cooling",
              "  and converter current limits protect the magnets"]
    emit("b_magnets", lines)


def bearings() -> None:
    b = m.bearing_freqs(1155, 14, 0.040, 0.220)                # A-116
    lines = ["generator bearing (A-116): 14 balls, 40 mm, pitch 220 mm, "
             "1155 rpm",
             f"  shaft {b['fr']:.2f} Hz; outer race {b['bpfo']:.1f} Hz, inner "
             f"race {b['bpfi']:.1f} Hz",
             f"  ball spin {b['bsf']:.1f} Hz, cage {b['ftf']:.2f} Hz"]
    for c_over_p in (8, 12, 16):
        l10_h = c_over_p ** 3 * 1e6 / (1155 * 60)
        lines.append(f"  life (C/P)^3 x 10^6 rev, C/P {c_over_p:2d}: "
                     f"{l10_h:9,.0f} h")
    lines += ["  20 years is about 175,000 h: bearings are chosen with margin "
              "and",
              "  monitored; lubrication, contamination and shaft currents "
              "decide",
              "  the real life more often than the formula (section D)"]
    emit("b_bearings", lines)


def cooling() -> None:
    p_loss = 158.7e3                                           # a_losses
    air = p_loss / (1.2 * 1005 * 20)
    water = p_loss / (4180 * 8)
    lines = [f"removing {p_loss / 1e3:.1f} kW of generator losses (A-120):",
             f"  air, 20 K rise: {air:.2f} m3/s ({air * 3600:,.0f} m3/h)",
             f"  water-glycol taken as water, 8 K rise: {water:.2f} kg/s "
             f"({water * 60:.0f} kg/min)",
             "  water carries the heat in a far smaller volume; the nacelle "
             "air",
             "  must still take it out through a heat exchanger"]
    emit("b_cooling", lines)
    rows = [(f"{t}", f"{m.life_factor(t, 130, 1e5):.4f}")
            for t in range(100, 161, 2)]
    csv("ch08-life.csv", "t,life", rows)


if __name__ == "__main__":
    laminations()
    winding_factors()
    insulation()
    magnets()
    bearings()
    cooling()
