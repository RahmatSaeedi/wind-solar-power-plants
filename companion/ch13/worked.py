"""Chapter 13 - the small worked numbers quoted in the lessons (E01 ...).

Run from the project root:   python -m companion.ch13.worked
Writes companion/ch13/expected/worked.txt.
"""
from __future__ import annotations

import math

from companion.ch13.common import emit
from plantp import stats, windres as wr

OUT: list[str] = []


def e(eid: str, text: str) -> None:
    OUT.append(f"{eid}: {text}")


def main() -> None:
    e("E01", f"power law 7.0 m/s at 100 m, shear 0.2, to 150 m:"
             f" {float(wr.power_law(7.0, 100, 150, 0.2)):.3f} m/s")
    e("E02", f"log law z0 0.05 m, 7.0 m/s at 100 m, to 150 m:"
             f" {float(wr.log_law(7.0, 100, 150, 0.05)):.3f} m/s")
    e("E03", f"shear, 6.30 at 60 m, 7.10 at 100 m: ln(7.10/6.30)/ln(100/60) ="
             f" {math.log(7.10 / 6.30) / math.log(100 / 60):.3f}")
    e("E04", f"TI of 10.0 m/s with sigma 1.3 m/s: {1.3 / 10:.3f}")
    e("E05", f"veer 10 deg over 40 m: {10 / 40:.2f} deg per m")
    e("E06", f"cup cosine error at 5 deg inclination: {100 * (math.cos(math.radians(5)) - 1):+.2f} %")
    e("E07", f"recovery: 52,560 records, 1,500 flagged:"
             f" {100 * (1 - 1500 / 52560):.1f} %")
    e("E08", f"speed +1 % with energy sensitivity 1.6: energy +{1.6:.1f} %")
    e("E09", f"Gumbel 50-year level, location 26.7, scale 0.99:"
             f" {stats.return_level(26.7, 0.99, 50):.1f} m/s")
    e("E10", f"chance of the 50-year wind in 25 years:"
             f" 1 - (1 - 1/50)^25 = {stats.prob_exceed_in_life(50, 25):.3f}")
    e("E11", f"long-term ratio: 7.066 x 6.662 / 6.494 = {7.066 * 6.662 / 6.494:.3f} m/s")
    e("E12", f"variance ratio slope: sd_site / sd_ref = 3.40 / 3.10 = {3.40 / 3.10:.4f}")
    e("E13", f"least-squares slope = r x variance-ratio slope = 0.951 x 1.0968 ="
             f" {0.951 * 1.0968:.4f}")
    e("E14", f"density at 875 hPa and 20 C: {87500 / (287.05 * 293.15):.4f} kg/m3")
    e("E15", f"mean standard error of 12 monthly means with sd 14.7 %:"
             f" {14.7 / math.sqrt(12):.1f} %")
    e("E16", f"combined: sqrt(1^2 + 1^2 + 2^2 + 0.8^2) = {math.sqrt(1 + 1 + 4 + 0.64):.2f} %")


if __name__ == "__main__":
    main()
    emit("worked", OUT)
