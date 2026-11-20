"""Chapter 26 - numerical answers of the small examples (E..) and of the
end-of-chapter problems (P..), each computed here.

Run from the project root:   python -m companion.ch26.worked
Writes companion/ch26/expected/worked.txt and solutions.txt.
"""
from __future__ import annotations

import math

from companion.ch26.common import emit
from plantp import protection as pr

E = 33e3 / math.sqrt(3)


def worked() -> None:
    f = pr.fault_currents(E, 2.98j, 2.98j, 2.0j)
    g = pr.fault_currents(E, 2.98j, 2.98j, 2.0j, zf=47.6)
    lines = [f"E01 three-phase fault behind 2.98 ohm at 33 kV: {f['3ph'] / 1e3:.2f} kA",
             f"E02 earth fault through 47.6 ohm: {g['SLG']:.0f} A",
             f"E03 standard inverse, 4 kA, pickup 450 A, TMS 0.1: {pr.trip_time(4000, 450, 0.1):.2f} s",
             f"E04 grid of 7,000 m2, 2,400 m, 150 ohm m: {pr.grid_resistance(150, 7000, 2400):.3f} ohm",
             f"E05 GPR of 2,080 A on 0.857 ohm: {pr.gpr(2080, 0.857):,.0f} V",
             f"E06 strikes a year on a 175 m turbine, Ng 2: {pr.strikes_per_year(2, pr.collection_area(175)):.2f}"]
    emit("worked", lines)


def solutions() -> None:
    out = [f"P01 three-phase fault behind 4 ohm at 33 kV: {E / 4 / 1e3:.2f} kA",
           f"P02 line-to-line fault, Z1 = Z2 = 4j: {math.sqrt(3) * E / 8 / 1e3:.2f} kA",
           f"P03 earth fault, Z1 Z2 Z0 = 4j, solid: {3 * E / 12 / 1e3:.2f} kA",
           f"P04 earth fault through 63.5 ohm (300 A design): {3 * E / abs(12j + 190.5):.0f} A",
           f"P05 SI time at 10 x pickup, TMS 0.2: {pr.trip_time(10, 1, 0.2):.2f} s",
           f"P06 VI time at 10 x pickup, TMS 0.2: {pr.trip_time(10, 1, 0.2, 'very inverse'):.2f} s",
           f"P07 EI time at 10 x pickup, TMS 0.2: {pr.trip_time(10, 1, 0.2, 'extremely inverse'):.3f} s",
           f"P08 grading 0.25 s and 0.50 s with 0.3 s margin: {'ok' if pr.grading_ok(0.25, 0.50) else 'no'}",
           f"P09 knee needed, If 20 A sec, Rct 3, Rb 2, k 2: {2 * 20 * 5:.0f} V",
           f"P10 diff with I1 5, I2 -4.5: {'trip' if pr.diff_trips(5, -4.5) else 'restrain'}",
           f"P11 diff with I1 2, I2 0: {'trip' if pr.diff_trips(2, 0) else 'restrain'}",
           f"P12 zones of a 5 ohm line, next 6 ohm: {pr.distance_zones(5, 6)}",
           f"P13 grid 50 x 50 m, 1,000 m, 300 ohm m: {pr.grid_resistance(300, 2500, 1000):.2f} ohm",
           f"P14 GPR 3 kA x 1.2 ohm: {pr.gpr(3000, 1.2):,.0f} V",
           f"P15 limit ratio for clearing 0.5 s vs 0.2 s: {math.sqrt(0.5 / 0.2):.2f}",
           f"P16 collection area of a 120 m mast: {pr.collection_area(120) / 1e6:.3f} km2",
           f"P17 strikes a year, Ng 4, area 0.4 km2: {pr.strikes_per_year(4, 0.4e6):.1f}",
           f"P18 building 30 x 20 x 8 m area: {pr.collection_area(8, 30, 20):,.0f} m2",
           f"P19 arrester margin 550/350: {550 / 350:.2f}",
           f"P20 CT burden 5 A over 1.2 ohm: {25 * 1.2:.0f} VA; 1 A: {1.2:.1f} VA",
           f"P21 intertrip 20 + 20 + 10 + 50 ms: {20 + 20 + 10 + 50} ms",
           f"P22 two channels of 99.5 %: {1 - 0.005 ** 2:.4%}",
           f"P23 arc energy ratio 0.5 s to 0.1 s: {0.1 / 0.5:.1f}",
           f"P24 BF clearing 30 + 150 + 60 ms: {30 + 150 + 60} ms"]
    i0, i1, i2 = pr.sequence(pr.phasor(1000, 0), 0, 0)
    j0, j1, j2 = pr.sequence(pr.phasor(800, 0), pr.phasor(800, -110), pr.phasor(800, 120))
    lo, hi, ok = pr.pickup_window(250, 2400)
    rf = pr.foot_resistance(2500)
    out += [f"P25 sequence parts of Ia 1000, Ib = Ic = 0: |I0| = |I1| = |I2| = {abs(i0):.0f} A",
            f"P26 unbalanced set (800 A, 0/-110/120 deg): |I0| {abs(j0):.0f},"
            f" |I1| {abs(j1):.0f}, |I2| {abs(j2):.0f} A",
            f"P27 pickup window, load 250 A, min fault 2,400 A: {lo:.0f}-{hi:.0f} A"
            f" ({'feasible' if ok else 'none'})",
            f"P28 TMS for 0.6 s at 3 kA, pickup 600 A: {pr.tms_for(0.6, 3000, 600):.3f}",
            f"P29 hemisphere a = 1 m, 100 ohm m, 1 kA: GPR"
            f" {pr.hemisphere_v(100, 1000, 1) / 1e3:.1f} kV, at 2 m"
            f" {pr.hemisphere_v(100, 1000, 2) / 1e3:.1f} kV",
            f"P30 foot on 2,500 ohm m rock: {rf:,.0f} ohm; touch current for 300 V:"
            f" {pr.body_current(300, 1000, rf) * 1e3:.0f} mA",
            f"P31 rolling sphere 30 m, mast 15 m: {pr.rolling_sphere_r(15, 30):.1f} m at ground",
            f"P32 loop 20 m2 at 100 m, 20 kA/us: {pr.loop_voltage(20, 100, 2e10):,.0f} V",
            f"P33 arrester 280 kV, 20 m, 800 kV/us: {pr.at_equipment(280, 20, 800):.0f} kV at equipment",
            f"P34 fuses with 3 strings, Isc 11 A, reverse 20 A:"
            f" {'needed' if pr.fuse_needed(3, 11, 20) else 'not needed'}",
            f"P35 main 1 % and backup 1 %, beta 0.1: {0.9 * 1e-4 + 0.1 * 0.01:.1e}",
            f"P36 earth conductor for 20 kA, 1 s, k 143: {20e3 / 143:.0f} mm2",
            f"P37 rod 2.4 m x 16 mm in 80 ohm m:"
            f" {80 / (2 * math.pi * 2.4) * (math.log(4 * 2.4 / 0.016) - 1):.1f} ohm",
            f"P38 capacitive current, 5 uF per phase at 33 kV:"
            f" {3 * 2 * math.pi * 50 * 5e-6 * E:.0f} A",
            f"P39 ROCOF with 5 % mismatch, H 1 s: {0.05 * 50 / 2:.2f} Hz/s",
            f"P40 unit transformer 2.5 MVA at 33 kV, 6 %: In {2.5e6 / (math.sqrt(3) * 33e3):.1f} A,"
            f" LV fault {2.5e6 / (math.sqrt(3) * 33e3) / 0.06:.0f} A",
            f"P41 longest run, 0.5 ohm max, 0.01 ohm/m loop, 0.04 source: {(0.5 - 0.04) / 0.01:.0f} m",
            f"P42 CT error, 400/1, 400 A gives 0.995 A: {(400 * 0.995 - 400) / 400 * 100:.2f} %",
            f"P43 insulation of 300 strings at 10 MOhm: {10e3 / 300:.1f} kOhm",
            f"P44 strikes on 10 masts of 30 m, Ng 3: "
            f"{10 * pr.strikes_per_year(3, pr.collection_area(30)):.2f} a year"]
    emit("solutions", out)


def solutions2() -> None:
    """Checks of the short answers added with the expansion lessons."""
    from companion.ch26.examples_n import fop_reading  # noqa: F401
    from companion.ch26.examples_p import asymmetry_spill
    from companion.ch26.examples_r import thermal_trip
    from companion.ch26.examples_t import acceptance_band
    from companion.ch26.examples_u import inrush_cycle, second_ratio
    six = 6 * 5.26e6 / (math.sqrt(3) * 33e3) * 1.3
    lo, hi = acceptance_band(1.5, 5.0, 0.030, 1.0)
    out = [f"P45 spill at 5 pu, tap +5 %, mismatch 2 %: {5 * 0.07:.2f} pu",
           f"P46 REF reach at 10 %, 400 A limit, 1,102 A rated: x >= {0.10 * 1102 / 400:.2f}",
           f"P47 six turbines at 1.3 x: {six:.0f} A, {pr.trip_time(six, 480, 0.10):.2f} s",
           f"P48 phase drift 0.2 Hz over 2 s: {360 * 0.2 * 2:.0f} deg",
           f"P49 advance angle, slip 0.3 Hz, 60 ms: {360 * 0.3 * 0.06:.1f} deg",
           f"P50 Wenner a = 10 m, 2.0 ohm: {2 * math.pi * 10 * 2.0:.0f} ohm m",
           f"P51 potential probe for a 300 m current lead: {0.618 * 300:.0f} m",
           f"P52 arc boundary at 0.5 s, x = 1.5: {0.455 * (4 / 1.2) ** (1 / 1.5):.2f} m",
           f"P53 incomer at 9.8 kA: {pr.trip_time(9800, 1600, 0.11):.2f} s",
           f"P54 asymmetry 3 ms at 437 A: {asymmetry_spill(437, 3.0):.0f} A",
           f"P55 charging of 12 km cable: {33.8 * 12 / 7:.1f} A",
           f"P56 unavailability, 0.03 a year, 4 y: {0.03 * 4 / 2:.0%}",
           f"P57 interval for 1 % with 90 % supervision: {2 * 0.01 / (0.02 * 0.1):.0f} y",
           f"P58 dependability 48/50, security 48/49: {48 / 50:.0%}, {48 / 49:.1%}",
           f"P59 thermal replica at 600 A from cold: {thermal_trip(600, 400, 45):.1f} min",
           f"P60 400 mm2 Al at 12.5 kA: {(94 * 400 / 12500) ** 2:.1f} s",
           f"P61 stability voltage with 3 ohm leads: {25e3 / 2000 * (5 + 6):.1f} V",
           f"P62 SPD lead for 4 kV at 10 kA/us: {(4 - 1.5) / 10:.2f} m",
           f"P63 locator at 3.0 km: {1.1 + 1.9 * 1.2:.2f} km",
           f"P64 acceptance band at 1.5 s: {lo:.2f} - {hi:.2f} s",
           f"P65 reversed CT trips above (slope 0.25): {0.2 / 1.75:.3f} pu",
           f"P66 3,000 terminations at 0.5 per 1,000: {1.5:.1f}, none {math.exp(-1.5):.0%}",
           f"P67 2nd harmonic of a 240 deg inrush pulse: {second_ratio(inrush_cycle(240)):.0%}",
           f"P68 screen of 3.6 kA for 1 s at 800 A: {(3600 / 800) ** 2:.0f} s",
           f"P69 loop voltages at 300 m: "
           + ", ".join(f"{pr.loop_voltage(a, 300, 2e10) / 1e3:.2f}" for a in (118.6, 29.6, 3.0))
           + " kV",
           f"P70 BF timer for a 35 ms slowest pole: {35 + 20 + 60} ms",
           f"P71 plant share at 1.5 x, grid 3.0 kA: "
           f"{1.5 * 105.26e6 / (math.sqrt(3) * 132e3) / 1e3:.2f} kA,"
           f" {1.5 * 105.26e6 / (math.sqrt(3) * 132e3) / 3000:.0%}",
           f"P72 four services, 150 kA stroke: {150 * 0.5 / 4:.2f} kA each",
           f"P73 unit window with a 30 ms LV breaker: "
           f"{0.03 + 0.3:.3f} to {pr.trip_time(1400, 480, 0.10) - 0.3:.3f} s",
           f"P74 longest 6 mm2 run on the diesel (866 A): "
           f"{(230 / 320 - 230 / 866) / 0.0074:.0f} m",
           f"P75 smallest fuse for 1.6 MVA at 33 kV: "
           f"{12 * 1.6e6 / (math.sqrt(3) * 33e3) / 8:.0f} A"]
    emit("solutions2", out)


if __name__ == "__main__":
    worked()
    solutions()
    solutions2()
