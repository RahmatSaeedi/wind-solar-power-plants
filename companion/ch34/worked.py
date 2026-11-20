"""Chapter 34 - small worked examples (E-lines) and the numerical answers
of the exercises (P-lines), each computed here.

Run from the project root:   python -m companion.ch34.worked
Writes companion/ch34/expected/worked.txt and solutions.txt.
"""
from __future__ import annotations

import math

from companion.ch34.common import emit
from plantp import instrumentation as ic


def worked() -> None:
    lines = [f"E01 12 mA on a 0-150 kV range: {ic.ma_to_eng(12, 0, 150):.1f} kV",
             f"E02 33 kV on a 0-40 kV range: {ic.eng_to_ma(33, 0, 40):.2f} mA",
             f"E03 Pt100 at 50 deg C: {ic.pt100_r(50):.2f} ohm",
             f"E04 two leads of 1 ohm each on a Pt100: +{ic.lead_error_2wire(1.0):.1f} K",
             f"E05 clock at 50 ppm for 1 hour: {ic.clock_drift_s(50, 3600) * 1000:.0f} ms",
             f"E06 response 20 + 2 x 100 + 10 + 50 ms: {ic.response_budget(20, 100, 10, 50):.0f} ms",
             f"E07 one PLC MTBF 100,000 h, MTTR 10 h: A = {ic.availability(1e5, 10):.5f}"]
    emit("worked", lines)


def solutions() -> None:
    a = ic.availability(150_000, 8)
    out = [f"P01 4 mA, 20 mA and 8 mA on 0-150 kV: {ic.ma_to_eng(4, 0, 150):.0f},"
           f" {ic.ma_to_eng(20, 0, 150):.0f}, {ic.ma_to_eng(8, 0, 150):.1f} kV",
           f"P02 145.2 kV on 0-150 kV: {ic.eng_to_ma(145.2, 0, 150):.2f} mA",
           f"P03 longest loop, 24 V, 12 V, 250 ohm, 0.75 mm2:"
           f" {ic.loop_max_length(24, 12, 250, 0.75):,.0f} m",
           f"P04 same with 15 V needed at the transmitter:"
           f" {ic.loop_max_length(24, 15, 250, 0.75):,.0f} m",
           f"P05 one count of 16 bits over 21 mA: {ic.adc_step(21, 16) * 1000:.2f} uA",
           f"P06 combined u of 0.29, 0.13, 0.09 %: {ic.combine(0.29, 0.13, 0.09):.2f} %",
           f"P07 VT class 0.2 as rectangular u: {0.2 / math.sqrt(3):.3f} %",
           f"P08 Pt100 at 0 and 100 deg C: {ic.pt100_r(0):.2f}, {ic.pt100_r(100):.2f} ohm",
           f"P09 temperature of 119.40 ohm: {ic.pt100_t(119.40):.1f} deg C",
           f"P10 lead error, 2 x 1.17 ohm: +{ic.lead_error_2wire(1.17):.1f} K",
           f"P11 drift 20 ppm for a week: {ic.clock_drift_s(20, 7 * 86400):.1f} s",
           f"P12 interval, tol 0.5, drift 0.15/yr, as-left 0.05:"
           f" {ic.calibration_interval(0.5, 0.15, 0.05):.1f} yr",
           f"P13 response 20 + 2 x 50 + 10 + 30: {ic.response_budget(20, 50, 10, 30):.0f} ms",
           f"P14 panel 400 W on 5 m2: rise {ic.panel_rise_k(400, 5):.1f} K",
           f"P15 fan for 400 W and 5 K: {ic.fan_flow_m3h(400, 5):.0f} m3/h",
           f"P16 modules for 185 DI at 16 + 20 %: {ic.modules_needed(185, 0.2, 16)}",
           f"P17 autonomy 250 Ah, 44.7 A, 80 %: {ic.autonomy_h(250, 44.7):.1f} h",
           f"P18 PLC pair, independent: {(1 - ic.parallel(a)) * 8760 * 3600:.2f} s a year",
           f"P19 false watchdog timeouts, p 0.5 %, 3 beats: {0.005 ** 3 * 365 * 86400:.1f}"
           " a year",
           f"P20 quality of 2.5 mA: {ic.quality(2.5, 0.0)}; of 12 mA aged 15 s:"
           f" {ic.quality(12, 15)}"]
    out += more_solutions()
    emit("solutions", out)


def more_solutions() -> list[str]:
    """Answers of the exercises on the deeper lessons (P21-P40)."""
    from scipy import stats

    from companion.ch34.examples_r import crossover, margin_deg
    i10 = 10e6 / (math.sqrt(3) * 132e3)
    wc_deg = math.degrees(crossover())
    t_h = 0.5 * 470e-6 * (325 ** 2 - 200 ** 2) / (240 / 0.9) * 1000
    i80 = 80e6 / (math.sqrt(3) * 132e3)
    lam = math.exp(0.7 / 8.617e-5 * (1 / 307.15 - 1 / 318.15))
    a2 = ic.availability(100_000, 10)
    return [
        f"P21 0.5 % of a 0-200 L/min span at 40 L/min: {0.5 * 200 / 40:.1f} % of reading",
        f"P22 10 MW at 132 kV on 600/1 A: {i10:.1f} A, {i10 / 600 * 100:.1f} % of rated",
        f"P23 1 A, 2 x 200 m of 2.5 mm2 Cu + 1 VA: {0.0175 * 400 / 2.5 + 1:.1f} VA",
        f"P24 Pt100 at 0 C, 2 mA, 0.5 K/mW: {0.002 ** 2 * 100 * 1000 * 0.5:.2f} K",
        f"P25 110 V, 36.7 kohm input, 30 kohm leak: {110 / (30e3 + 36.7e3) * 1e3:.2f}"
        " mA (undefined)",
        f"P26 230 V on a core, 1 km at 100 nF/km: "
        f"{2 * math.pi * 50 * 100e-9 * 1.0 * 230 * 1e3:.1f} mA",
        f"P27 false deviation alarms at k = 4, 1 s samples: "
        f"{2 * (1 - stats.norm.cdf(4)) * 3600:.2f} a hour",
        f"P28 pocket tau 60 s, oil warming 2 K/min: lag {60 * 2 / 60:.1f} K",
        f"P29 phase margin with 0.5 s of loop delay: {margin_deg(0.5):.1f} deg",
        f"P30 loop delay for a 60 deg margin: {(margin_deg(0) - 60) / wc_deg:.2f} s",
        f"P31 30 ms pulse, 50 ms scan: missed {(1 - 30 / 50) * 100:.0f} %",
        f"P32 proportional kick, kp 1.5, error 10 MW: {1.5 * 10:.0f} MW",
        f"P33 hold-up, 470 uF, 325 -> 200 V, 240 W at 90 %: {t_h:.1f} ms",
        f"P34 5 mHz error, 5 % droop, 100 MW: {(0.005 / 50) / 0.05 * 100:.2f} MW",
        f"P35 0.3 % voltage error, 5 % slope, 33 Mvar: {0.003 / 0.05 * 33:.2f} Mvar",
        f"P36 line loss at 80 MW, 7.06 km of 0.12 ohm/km: "
        f"{3 * i80 ** 2 * 0.12 * 7.06 / 1e6:.2f} MW",
        f"P37 capacitor 5,000 h at 105 C, at 65 C: {5000 * 2 ** 4 / 8760:.1f} years",
        f"P38 failure-rate factor 34 -> 45 C, 0.7 eV: {lam:.2f}",
        f"P39 MTBF 100,000 h, MTTR 10 h: {(1 - a2) * 525_600:.1f} min down a year",
        f"P40 sequence timeouts 10 + 30 + 5 + 40 + 5 + 90: {10 + 30 + 5 + 40 + 5 + 90} s"]


if __name__ == "__main__":
    worked()
    solutions()
