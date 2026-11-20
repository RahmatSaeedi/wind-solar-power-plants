"""Chapter 30 - small worked examples (E-lines) and the numerical answers
of the exercises (P-lines), each computed here.

Run from the project root:   python -m companion.ch30.worked
Writes companion/ch30/expected/worked.txt and solutions.txt.
"""
from __future__ import annotations

import math

from companion.ch30.common import emit
from plantp import structures as st


def worked() -> None:
    lines = [
        f"E01 wind at 100 m from 10 m/s at 10 m, alpha 0.14: {st.wind_profile(10, 10, 100):.2f} m/s",
        f"E02 pressure of a 40 m/s gust in air 1.09 kg/m3: {st.dynamic_pressure(40, 1.09):.0f} Pa",
        f"E03 vortex lock-in, f 0.5 Hz, D 3 m: {st.vortex_speed(0.5, 3.0):.1f} m/s",
        f"E04 elastic buckling, t 30 mm, r 2 m, knock-down 0.4: "
        f"{st.shell_buckling(210e9, 0.03, 2.0, 0.4) / 1e6:.0f} MPa",
        f"E05 Rankine with fy 355 and 1,000 MPa: {st.rankine(355, 1000):.0f} MPa",
        f"E06 S-N life at 50 MPa, detail 71: {st.sn_life(50, 71):.2e} cycles",
        f"E07 effective area, r 12 m, e 4 m: {st.effective_area_circle(12, 4):.1f} m2",
        f"E08 rocking stiffness, G 80 MPa, r 12 m, nu 0.3: "
        f"{st.rotational_stiffness(80e6, 12, 0.3) / 1e9:.0f} GN m/rad",
        f"E09 Broms, d 0.15, L 2.0, gamma 18, Kp 3, e 1.2: {st.broms_lateral_sand(0.15, 2.0, 18, 3, 1.2):.1f} kN",
        f"E10 zinc 85 um at 3 um/yr: {st.zinc_life(85, 3):.0f} years",
    ]
    emit("worked", lines)


def solutions() -> None:
    out = [
        f"P01 wind at 120 m from 8 m/s at 10 m, alpha 0.2: {st.wind_profile(8, 10, 120, 0.2):.2f} m/s",
        f"P02 peak gust, 20 m/s mean, TI 0.12, g 3.5: {st.peak_speed(20, 0.12):.1f} m/s",
        f"P03 drag, q 1,000 Pa, Cd 0.6, 3 m x 10 m: {st.drag_force(1000, 0.6, 30) / 1e3:.1f} kN",
        f"P04 vortex lock-in, f 0.45 Hz, D 3.0 m, St 0.2: {st.vortex_speed(0.45, 3.0):.2f} m/s",
        f"P05 elastic buckling, t 40 mm, r 2.06 m, knock-down 0.4: "
        f"{st.shell_buckling(210e9, 0.04, 2.06, 0.4) / 1e6:.0f} MPa",
        f"P06 Rankine with fy 355 and that: {st.rankine(355, st.shell_buckling(210e9, 0.04, 2.06, 0.4) / 1e6):.0f} MPa",
        f"P07 S-N life at 40 MPa, detail 71: {st.sn_life(40, 71):.2e} cycles",
        f"P08 S-N life at 100 MPa, detail 71: {st.sn_life(100, 71):.2e} cycles",
        f"P09 damage of 1e7 cycles at 45 MPa, detail 71: {1e7 / st.sn_life(45, 71):.2f}",
        f"P10 effective area, r 10 m, e 3 m: {st.effective_area_circle(10, 3):.1f} m2",
        f"P11 pressure, V 40 MN, M 120 MN m, r 12 m: "
        f"{st.foundation_pressure(40e3, 120e3, 12)[2]:.0f} kPa",
        f"P12 rocking stiffness, G 25 MPa, r 12 m, nu 0.35: "
        f"{st.rotational_stiffness(25e6, 12, 0.35) / 1e9:.0f} GN m/rad",
        f"P13 f1 with f_fixed 0.215 Hz, K 177 GN m/rad, m 353 t, h 100 m: "
        f"{st.frequency_with_foundation(0.215, 177e9, 353e3, 100):.4f} Hz",
        f"P14 pile uplift, perimeter 0.55 m, 2 m, 25 kPa: {st.pile_uplift(0.55, 2.0, 25):.1f} kN",
        f"P15 Broms, d 0.15, L 1.6, gamma 18, Kp 3, e 1.2: {st.broms_lateral_sand(0.15, 1.6, 18, 3, 1.2):.1f} kN",
        f"P16 zinc 85 um at 8 um/yr: {st.zinc_life(85, 8):.1f} years",
        f"P17 expansion of a 29.5 m rail over 74 K: {1000 * st.thermal_expansion(12e-6, 29.5, 74):.0f} mm",
        f"P18 base shear, 95 t, Sa 0.625 g: {st.base_shear(95e3, 0.625) / 1e3:.0f} kN",
        f"P19 slip resistance, 4 bolts, mu 0.3, 80 kN, 1 surface: {st.bolt_slip(4, 0.3, 80e3) / 1e3:.0f} kN",
        f"P20 rebar, M 2.4 MN m/m, d 1.6 m, fyd 435 MPa: {st.rebar_area(2.4e6, 1.6, 435e6) * 1e6:,.0f} mm2/m",
        f"P21 transverse pull, 35 kN at 60 deg: {2 * 35 * math.sin(math.radians(30)):.1f} kN a wire",
        f"P22 force between bars, ip 30 kA, a 0.5 m: {2e-7 * 30e3 ** 2 / 0.5:.0f} N/m",
        f"P23 worst anchor bolt, M 185 MN m, 160 bolts, D 4.3 m, V 6 MN: "
        f"{(4 * 185e6 / (160 * 4.3) - 6e6 / 160) / 1e3:.0f} kN",
        f"P24 carbonation to 50 mm with k 5 mm/sqrt(yr): {(50 / 5) ** 2:.0f} years",
        f"P25 verticality, 1.2 mm/m at 100 m: {1.2 * 100:.0f} mm",
    ]
    emit("solutions", out)


if __name__ == "__main__":
    worked()
    solutions()
