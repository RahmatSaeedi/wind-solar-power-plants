"""Chapter 14 - small worked calculations quoted in the text (E01 ...).

Run from the project root:   python -m companion.ch14.worked
Writes companion/ch14/expected/worked.txt.
"""
from __future__ import annotations

import math

from companion.ch14.common import emit
from plantp import siting as st, wind as w

OUT: list[str] = []


def e(eid: str, text: str) -> None:
    OUT.append(f"{eid}: {text}")


def main() -> None:
    e("E01", f"slope, 6 m rise over 120 m: {100 * 6 / 120:.1f} %")
    e("E02", f"tip height 100 + 75 = 175 m; 1.1 x tip = {1.1 * 175:.1f} m")
    e("E03", f"PV block 1,400 x 850 m:"
             f" {st.polygon_area([(0, 0), (1400, 0), (1400, 850), (0, 850)]) / 1e4:.0f} ha")
    e("E04", f"GCR of a 2 x 2.278 m table at 11.4 m pitch: {2 * 2.278 / 11.4:.2f}")
    e("E05", f"Jensen deficit at 5 D, Ct 0.8, k 0.05:"
             f" {w.jensen_deficit(0.8, 750.0, 150.0, 0.05):.4f}")
    e("E06", f"added turbulence at 6 D, Ct 0.36: 1 / (1.5 + 0.8 x 6 / 0.6) ="
             f" {1 / (1.5 + 0.8 * 6 / math.sqrt(0.36)):.3f}")
    e("E07", f"one turbine, 106 dB(A), 500 m: {float(w.sound_pressure_level(106, 500.0)):.1f}"
             " dB(A)")
    e("E08", f"two sources of 40 dB(A): {w.sum_levels([40.0, 40.0]):.1f} dB(A)")
    e("E09", f"tip shadow at a 20 deg sun: 175 / tan 20 = {175 / math.tan(math.radians(20)):.0f} m")
    e("E10", f"teaching speed-up of a 40 m hill over 800 m: 2 x 40 / 800 = {100 * 2 * 40 / 800:.1f} %")
    e("E11", f"pad 45 x 30 m on a 5 % slope: cut = fill = 30 x 0.05 x 45^2 / 8 ="
             f" {30 * 0.05 * 45 ** 2 / 8:.0f} m3")
    _, t = st.minimum_spanning_tree([(0, 0), (1000, 0), (0, 1000), (1000, 1000)])
    e("E12", f"tree joining the corners of a 1 km square: {t / 1e3:.1f} km")
    e("E13", f"climb 60 m at a 10 % grade: at least {60 / 0.10:.0f} m of road")
    e("E14", f"40 m3 a day of dust water: {40 / 86.4:.2f} L/s")
    e("E15", f"straight distance (6.5, 3.5) to (12.7, 3.0) km:"
             f" {math.hypot(12.7 - 6.5, 3.0 - 3.5):.2f} km")
    e("E16", f"12 pads of 1,730 m2 and 9.9 km of 8 m road:"
             f" {(12 * 1730 + 9900 * 8) / 1e4:.1f} ha")
    emit("worked", OUT)


if __name__ == "__main__":
    main()
