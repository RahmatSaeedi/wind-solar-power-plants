"""Chapter 32 - small worked examples (E-lines) and the numerical answers
of the exercises (P-lines), each computed here.

Run from the project root:   python -m companion.ch32.worked
Writes companion/ch32/expected/worked.txt and solutions.txt.
"""
from __future__ import annotations

import math

from companion.ch32.common import emit
from plantp import safety as sf


def stop(kmh: float, tr: float = 1.5, mu: float = 0.45) -> float:
    v = kmh / 3.6
    return v * tr + v * v / (2 * mu * 9.81)


def lex(tasks) -> float:
    return 10 * math.log10(sum(10 ** (lv / 10) * h for lv, h in tasks) / 8)


def worked() -> None:
    r, lo, hi = sf.incident_rate(2, 300_000)
    lines = [f"E01 risk score, likelihood 4, severity 3: {sf.risk_score(4, 3)}"
             f" ({sf.risk_band(12)})",
             f"E02 rate, 2 recordables in 300,000 h: {r:.2f} per 200,000 h"
             f" ({lo:.2f}-{hi:.2f})",
             f"E03 fall clearance, lanyard 2.0 m, deceleration 1.75 m:"
             f" {sf.fall_clearance(2.0, 1.75):.2f} m",
             f"E04 air changes, 40 m3 and 400 m3/h: {sf.air_changes(40, 400):.0f} per hour",
             f"E05 purge to 10 % at 10 changes an hour: {-math.log(0.1) / 10 * 60:.1f} min",
             f"E06 stopping distance at 40 km/h: {stop(40):.1f} m",
             f"E07 noise, 95 dB(A) for 2 h: {lex([(95, 2)]):.1f} dB(A) over 8 h",
             f"E08 autonomy, 100 m3 at 2,000 L/min: {sf.autonomy_minutes(100, 2000):.0f} min",
             f"E09 flux at 15 m from 20 MW, radiant 0.3:"
             f" {sf.heat_flux_point(20_000, 0.3, 15):.1f} kW/m2",
             f"E10 PFD, rate 0.05 a year, tested yearly: {0.05 * 1 / 2:.3f}"]
    emit("worked", lines)


def solutions() -> None:
    r, lo, hi = sf.incident_rate(3, 1_050_000)
    r0, lo0, hi0 = sf.incident_rate(0, 52_000)
    out = [f"P01 score L3 S5: {sf.risk_score(3, 5)} ({sf.risk_band(15)})",
           f"P02 score L2 S2: {sf.risk_score(2, 2)} ({sf.risk_band(4)})",
           f"P03 lost-time rate, 3 in 1,050,000 h: {r:.2f} ({lo:.2f}-{hi:.2f})",
           f"P04 zero in 52,000 h, upper 90 % bound: {hi0:.2f}",
           f"P05 near misses per recordable, 164 / 11: {164 / 11:.1f}",
           f"P06 clearance, lanyard 1.8, deceleration 1.75: {sf.fall_clearance(1.8, 1.75):.2f} m",
           f"P07 clearance, retracting 0.3 + 0.6: {sf.fall_clearance(0.3, 0.6):.2f} m",
           f"P08 air changes, 30 m3 at 300 m3/h: {sf.air_changes(30, 300):.0f}",
           f"P09 purge to 1 % at 10 changes an hour: {-math.log(0.01) / 10 * 60:.1f} min",
           f"P10 dilution, 2 m3/h kept at 1 %, mixing 3: {sf.dilution_flow(2, 0.01, 3):,.0f} m3/h",
           f"P11 stopping at 30 km/h: {stop(30):.1f} m",
           f"P12 stopping at 60 km/h: {stop(60):.1f} m",
           f"P13 noise of the day (98/1, 90/2, 80/4, 65/1): "
           f"{lex([(98, 1), (90, 2), (80, 4), (65, 1)]):.1f} dB(A)",
           f"P14 noise, 98 dB(A) for 1 h alone: {lex([(98, 1)]):.1f} dB(A)",
           f"P15 autonomy, 180 m3 at 3,000 L/min: {sf.autonomy_minutes(180, 3000):.0f} min",
           f"P16 autonomy, 180 m3 at 1,500 L/min: {sf.autonomy_minutes(180, 1500):.0f} min",
           f"P17 refill 180 m3 with 39 L/min: {180_000 / 39 / 60:.0f} h",
           f"P18 oil-pool heat release, 140 m2 x 0.039 x 46,000: {0.039 * 46_000 * 140 / 1000:.0f} MW",
           f"P19 flux at 20 m from 251 MW, radiant 0.3: {sf.heat_flux_point(251_160, 0.3, 20):.1f} kW/m2",
           f"P20 distance for 12.5 kW/m2 from 251 MW: {sf.distance_for_flux(251_160, 0.3, 12.5):.1f} m",
           f"P21 PFD one detector, 0.02/yr, 6 months: {0.02 * 0.5 / 2:.4f}",
           f"P22 PFD two detectors, same: {(0.02 * 0.5) ** 2 / 3:.6f}",
           f"P23 rescue time by night (2+1+35+12+15+10): {2 + 1 + 35 + 12 + 15 + 10} min",
           f"P24 ambulance, 10 + 35 km at 60 km/h + 10: {10 + 35 + 10} min",
           f"P25 camp water, 270 x 70 x 1.8: {270 * 70 * 1.8 / 1000:.1f} m3/day",
           f"P26 coverage, arrivals 50, 55, 62, 70 within 60: "
           f"{sf.coverage_fraction([50, 55, 62, 70], 60) * 100:.0f} %",
           f"P27 battery container at 50 %, 5,016 kWh: {5016 / 2 * 3.6:,.0f} MJ",
           f"P28 JHA sum of scores before / after: 91 / 39 ({(1 - 39 / 91) * 100:.0f} % lower)"]
    emit("solutions", out)


if __name__ == "__main__":
    worked()
    solutions()
