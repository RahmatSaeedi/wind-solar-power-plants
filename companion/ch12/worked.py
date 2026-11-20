"""Chapter 12 - the small worked numbers quoted in the lessons (E01 ...).

Run from the project root:   python -m companion.ch12.worked
Writes companion/ch12/expected/worked.txt.
"""
from __future__ import annotations

import math

from companion.ch12.common import emit
from plantp import irradiance as ir, solar

OUT: list[str] = []


def e(eid: str, text: str) -> None:
    OUT.append(f"{eid}: {text}")


def main() -> None:
    e("E01", f"declination on 21 June (day 172): {float(solar.declination(172)):.2f} deg;"
             f" 21 December: {float(solar.declination(355)):.2f} deg")
    e("E02", f"equation of time on 11 February: {float(solar.equation_of_time(42)):+.1f} min;"
             f" 3 November {float(solar.equation_of_time(307)):+.1f} min")
    e("E03", f"G0n on 3 January {float(ir.g0n(3)):.0f} W/m2, on 4 July"
             f" {float(ir.g0n(185)):.0f} W/m2 (+-3.3 %)")
    e("E04", f"air mass at zenith 60 deg: {float(ir.air_mass(60.0)):.3f};"
             f" at 80 deg: {float(ir.air_mass(80.0)):.2f}")
    cz30 = math.cos(math.radians(30))
    e("E05", f"Haurwitz clear sky at zenith 30 deg:"
             f" {float(ir.clear_sky_haurwitz(cz30)):.0f} W/m2")
    kt = 800 / (float(ir.g0n(172)) * cz30)
    e("E06", f"k_t for GHI 800 W/m2 at zenith 30 deg on 21 June: {kt:.3f}")
    e("E07", f"Erbs k_d at k_t 0.5: {float(ir.erbs_diffuse_fraction(0.5)):.3f};"
             f" Orgill-Hollands {float(ir.orgill_hollands_diffuse_fraction(0.5)):.3f}")
    e("E08", f"DNI from GHI 800, DHI 150, zenith 30 deg: 650 / cos 30 ="
             f" {(800 - 150) / cz30:.0f} W/m2")
    c40 = 700 * math.cos(math.radians(40)) + 140
    e("E09", f"closure: 700 cos 40 + 140 = {c40:.0f} W/m2 against GHI 700:"
             f" ratio {c40 / 700:.3f}")
    e("E10", f"sky (1 + cos 25)/2 = {(1 + math.cos(math.radians(25))) / 2:.4f};"
             f" ground (1 - cos 25)/2 = {(1 - math.cos(math.radians(25))) / 2:.4f}")
    e("E11", f"ground-reflected on 25 deg, GHI 900, albedo 0.2: "
             f"{900 * 0.2 * (1 - math.cos(math.radians(25))) / 2:.1f} W/m2")
    e("E12", f"thermal offset -4 W/m2 for 4,660 daylight hours: {-4 * 4660 / 1e3:.1f} kWh/m2")
    e("E13", f"7.65 mV / 8.50 uV per W/m2 = {7.65e-3 / 8.50e-6:.0f} W/m2")
    e("E14", f"P90 = P50 (1 - 1.2816 u): 1,920 x (1 - 1.2816 x 0.028) ="
             f" {1920 * (1 - 1.2816 * 0.028):,.0f} kWh/m2")
    e("E15", f"long-term factor 1,910.5 / 1,937.8 = {1910.5 / 1937.8:.4f}")
    e("E16", f"a UTC record read as +04:00 is 4 h early; solar noon at 08:02")
    e("E17", f"sensor and modules both 2 % dirty: reported PR x"
             f" {(1 - 0.02) / (1 - 0.02):.3f}")
    e("E18", f"20 years, year-to-year sd 2.7 %: sd of the mean 2.7 / sqrt(20) ="
             f" {2.7 / math.sqrt(20):.2f} %")
    e("E19", f"day length at 34 deg N on 21 June:"
             f" {2 * math.degrees(math.acos(-math.tan(math.radians(34)) * math.tan(math.radians(23.45)))) / 15:.2f} h")
    e("E20", f"noon sun on 21 Dec at 34 deg N: 90 - 34 - 23.45 ="
             f" {90 - 34 - 23.45:.2f} deg")


if __name__ == "__main__":
    main()
    emit("worked", OUT)
