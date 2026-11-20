"""Chapter 11 - numerical answers to the end-of-chapter problems (P01 ...).
Criteria-based problems are answered in the text.

Run from the project root:   python -m companion.ch11.solutions
Writes companion/ch11/expected/solutions.txt.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch11 import lab_d, rotor
from companion.ch11.common import emit
from plantp import physics, stats, wind as w

OUT: list[str] = []
A = rotor.AREA
OM = rotor.turbine().omega_max


def p(pid: str, text: str) -> None:
    OUT.append(f"{pid}: {text}")


def level_1() -> None:
    p("P01", f"0.5 x 1.056 x {A:,.0f} x 9^3 = {0.5 * 1.056 * A * 729 / 1e6:.2f} MW")
    p("P02", f"(1.1)^3 - 1 = {100 * (1.1 ** 3 - 1):.1f} % more")
    p("P03", f"4 MW / (pi 70^2) = {4e6 / (math.pi * 70 ** 2):.0f} W/m2")
    p("P04", f"a 0.25: Cp {4 * 0.25 * 0.75 ** 2:.4f}, Ct {4 * 0.25 * 0.75:.3f}")
    p("P05", f"9 rpm, 8 m/s: TSR = {9 * math.pi / 30 * 75 / 8:.2f}")
    p("P06", f"10 rpm: tip speed {10 * math.pi / 30 * 75:.1f} m/s")
    p("P07", f"11.5 rpm: 1P {11.5 / 60:.3f} Hz, 3P {3 * 11.5 / 60:.3f} Hz")
    p("P08", f"10 x (1.056/1.225)^(1/3) = {10 * (1.056 / 1.225) ** (1 / 3):.3f} m/s")
    p("P09", f"yaw 7 deg, cos^3: {100 * (1 - math.cos(math.radians(7)) ** 3):.2f} %"
             " loss")
    re = OM * 37.5 * 4.0 / 1.5e-5
    p("P10", f"0.5 R, chord 4 m: Re = {OM * 37.5:.1f} x 4 / 1.5e-5 = {re:.1e}")
    cl, cd = (float(x) for x in w.polar(8.0))
    p("P11", f"8 deg: Cl {cl:.3f}, Cd {cd:.5f}, L/D {cl / cd:.1f}")
    p("P12", f"5 MW / 0.94 / {OM:.3f} = {5e6 / 0.94 / OM / 1e6:.2f} MN m")
    p("P13", f"4.42 MN m / 35 = {4.42e3 / 35:.0f} kN m")
    p("P14", f"25 t x 9.81 x 23 m = {25e3 * 9.81 * 23 / 1e6:.2f} MN m")
    om10 = 10 * math.pi / 30
    p("P15", f"22 t x {om10:.3f}^2 x 22 m = {22e3 * om10 ** 2 * 22 / 1e3:.0f} kN")
    p("P16", f"0.5 x 1.225 x A x 49 x 0.852 = {0.5 * 1.225 * A * 49 * 0.852 / 1e3:.0f}"
             " kN")
    p("P17", f"0.5 x 32.0e6 x {om10:.3f}^2 = {0.5 * 32.0e6 * om10 ** 2 / 1e6:.1f} MJ")
    p("P18", f"90 deg at 6 deg/s: {90 / 6:.0f} s")
    p("P19", f"top mass +10 %: f x 1/sqrt(1.1) = {1 / math.sqrt(1.1):.3f} "
             f"({100 * (1 / math.sqrt(1.1) - 1):.1f} %)")
    p("P20", f"Weibull k 2, c 8: mean {8 * math.gamma(1.5):.2f} m/s")
    p("P21", f"BPFO 16/2 x 25 x (1 - 0.15) = {8 * 25 * 0.85:.0f} Hz")
    p("P22", f"Jensen Ct 0.8 at 6D: {w.jensen_deficit(0.8, 900, 150):.3f}")
    p("P23", f"lightning Ng 4: 4 x 0.866 x 12 = {4 * 9 * math.pi * 0.175 ** 2 * 12:.0f}"
             " a year")
    p("P24", f"ice throw 1.5 x (136 + 112) = {1.5 * 248:.0f} m")
    p("P25", f"paint for 12 towers: 12 x 1,795 = {12 * 1795:,} L")
    p("P26", f"150 GWh / (60 MW x 8760 h) = {150 / (60 * 8.76):.3f}")
    p("P27", f"full-load hours 188.16 GWh / 60 MW = {188.16e3 / 60:,.0f} h")
    p("P28", f"133 kW, 10 K: {133e3 / (870 * 1900 * 10) * 6e4:.0f} L/min")
    p("P29", f"DEL m 4: ((2^4 + 2^4 + 4^4) / 3)^(1/4) = "
             f"{((16 + 16 + 256) / 3) ** 0.25:.2f}")
    p("P30", f"Miner: 1e6 x 0.5^4 / 1e7 = {1e6 * 0.5 ** 4 / 1e7:.5f}")


def level_2() -> None:
    for a in (0.2, 0.4):
        p("P31" if a == 0.2 else "   ", f"a {a}: Cp {4 * a * (1 - a) ** 2:.4f}, "
              f"Ct {4 * a * (1 - a):.3f}")
    phi = math.degrees(math.atan(6.7 / 60))
    p("P32", f"phi = atan(6.7/60) = {phi:.2f} deg = alpha with zero twist")
    b = rotor.blade()
    p("P33", f"BEM Cp: lambda 7 {w.bem(b, 7.0).cp:.4f}, lambda 10 "
             f"{w.bem(b, 10.0).cp:.4f}")
    k = 0.5 * 1.225 * A * 75 ** 3 * w.bem(b, rotor.tsr_opt()).cp / rotor.tsr_opt() ** 3
    p("P34", f"k at 1.056: {k / 1e3:,.0f} x 1.056/1.225 = {k * 1.056 / 1.225 / 1e3:,.0f}"
             " kN m s2")
    o9 = w.operate(rotor.turbine(), 9.0, 1.056)
    p("P35", f"9 m/s at 1.056: {o9.power_w / 1e3:,.0f} kW (1.225: 3,595)")
    o10 = w.operate(rotor.turbine(), 10.0, 1.056)
    p("P36", f"10 m/s at 1.056: thrust {o10.thrust_n / 1e3:.0f} kN (1.225: 923)")
    p("P37", "rated wind 11.0 m/s at site, 10.5 at 1.225 (a_density)")
    p("P38", f"yaw 5 deg, cos^2: {0.76:.2f} % of 188.16 GWh = "
             f"{0.0076 * 188.16:.2f} GWh")
    top = 271e3
    f46 = w.tower_frequency(210e9, w.tube_inertia(4.6, 0.033),
                            math.pi * 4.6 * 0.033 * 7850, 100.0, top)
    p("P39", f"tube 4.6 m, 33 mm: f1 = {f46:.3f} Hz")
    p("P40", f"1P meets 0.215 Hz at {0.215 * 60:.1f} rpm (above 11.5)")
    p("P41", f"DEL ratio m 10 / m 4: 7.94 / 3.56 = {7.94 / 3.56:.2f}")
    cyc = w.rainflow([0, 3, 1, 4, 0])
    p("P42", "series 0 3 1 4 0: " + ", ".join(f"range {s:g} x {c:g}"
                                              for s, c in cyc))
    v = lab_d.hourly()[0]
    kk, cc = stats.weibull_fit_mle(v)
    p("P43", f"P(v > 13) = exp(-(13/{cc:.2f})^{kk:.2f}) = "
             f"{math.exp(-(13 / cc) ** kk):.4f}; data {(v > 13).mean():.4f}")
    p("P44", "7..13 m/s: 10.1 + 12.2 + 14.7 + 14.2 + 12.1 + 8.6 = "
             f"{10.1 + 12.2 + 14.7 + 14.2 + 12.1 + 8.6:.1f} %")
    p("P45", f"density correction per turbine: 18,233 - 16,769 = "
             f"{18233 - 16769:,} MWh")
    p("P46", f"layout C vs A: 188.16 - 179.98 = {188.16 - 179.98:.2f} GWh")
    p("P47", f"at 50 u/MWh: {8.18e3 * 50 / 1e3:.0f} k u a year")
    s = np.array([22.2e3, 22.0e3, 22.0e3]) * 22.0
    u = abs(np.sum(s * np.exp(1j * np.radians([0, 120, 240]))))
    p("P48", f"one blade 0.2 t heavier: U {u:,.0f} kg m, F {u * OM ** 2 / 1e3:.1f}"
             " kN")
    p("P49", f"tip 200 m: 2 x 9 pi 0.2^2 = {2 * 9 * math.pi * 0.04:.2f} a year")
    p("P50", f"icing screen 333 / 8760 = {100 * 333 / 8760:.1f} %")
    p("P51", f"section 1: pi x 4.3125 x 0.0465 x 25 x 7850 = "
             f"{math.pi * 4.3125 * 0.0465 * 25 * 7850 / 1e3:.0f} t")
    p("P52", f"section 1 welds: (10 - 1 + 2) x pi x 4.3125 = "
             f"{11 * math.pi * 4.3125:.0f} m")
    p("P53", f"23 teeth at 19.25 Hz: mesh {23 * 19.25:.2f} Hz")
    rho15 = float(physics.air_density(float(physics.standard_pressure(1500.0)),
                                      15 - 0.0065 * 1500))
    p("P55", f"standard atmosphere at 1500 m: {rho15:.3f} kg/m3")
    p("P56", f"10 x (0.98/1.225)^(1/3) = {10 * (0.98 / 1.225) ** (1 / 3):.3f} m/s")
    p("P57", f"steady 4,932 vs smoothed 4,451 kW at 10 m/s: "
             f"{100 * (4451 / 4932 - 1):.1f} %")
    p("P58", f"bin 12.5 m/s: 314 x 4,985 = {314 * 4985 / 1e3:,.0f} MWh")
    p("P59", f"full-load hours at 1.225: 18,233 / 5 = {18233 / 5:,.0f} h")
    p("P60", f"Jensen Ct 0.35 at 8D: {w.jensen_deficit(0.35, 1200, 150):.4f}")


def level_3() -> None:
    o = w.operate(rotor.turbine(), 12.0, 1.15)
    p("P61", f"12 m/s, 1.15 kg/m3: {o.power_w / 1e3:,.0f} kW, pitch {o.pitch:.1f}"
             f" deg, thrust {o.thrust_n / 1e3:.0f} kN")
    p("P62", f"density alone: 218.79 - 201.23 = {218.79 - 201.23:.2f} GWh")
    p("P63", f"wakes 201.23 - 188.16 = {201.23 - 188.16:.2f} GWh = "
             f"{(201.23 - 188.16) * 50e3 / 1e3:,.0f} k u a year")
    t2 = w.Turbine(rotor.blade(), tsr_opt=rotor.tsr_opt(),
                   omega_max=10.5 * math.pi / 30)
    o2 = w.operate(t2, 10.0)
    o1 = w.operate(rotor.turbine(), 10.0)
    p("P64", f"cap 10.5 rpm at 10 m/s: {o2.power_w / 1e3:,.0f} kW (11.5 rpm: "
             f"{o1.power_w / 1e3:,.0f}); TSR {o2.tsr:.2f}")
    p("P65", f"efficiency 0.92 vs 0.94: energy x {0.92 / 0.94:.4f} "
             f"({100 * (0.92 / 0.94 - 1):.1f} %, below rated)")
    f300 = w.tower_frequency(210e9, w.tube_inertia(4.4, 0.031),
                             math.pi * 4.4 * 0.031 * 7850, 100.0, 300e3)
    p("P66", f"top 300 t: f1 = {f300:.3f} Hz; 1P max 0.192 -> margin "
             f"{100 * (f300 / 0.1917 - 1):.0f} %")
    v, wd, rho = lab_d.hourly()
    t = lab_d.datapack.load_hourly()["t_air_c"].to_numpy(float)
    cold = (t <= 0) & (v >= 3)
    v_eq = w.density_equivalent_speed(v, rho)
    e_cold = lab_d.pack_power(v_eq[cold]).sum() / 1e3
    p("P68", f"20 % of the {int(cold.sum())} cold hours lost: "
             f"{0.2 * e_cold:,.0f} MWh per turbine, {12 * 0.2 * e_cold / 1e3:.2f}"
             " GWh")
    p("P69", f"CF 0.358 x 0.95 x 0.98 = {0.358 * 0.95 * 0.98:.3f}")
    p("P70", f"PV specific yield 1,854 kWh/kWp -> CF {1854 / 8760:.3f} (DC);"
             f" wind {188.16e3 / 60 / 8760:.3f}")
    shear = (120 / 100) ** 0.2
    e100 = (lab_d.pack_power(v_eq)).sum()
    e120 = (lab_d.pack_power(v_eq * shear)).sum()
    p("P71", f"hub 120 m, shear 0.2: speed x {shear:.4f}; energy "
             f"{100 * (e120 / e100 - 1):+.1f} % (no wake, same curve)")
    p("P72", f"oil sample every 6 months, 12 turbines: {12 * 2} samples a year")


def level_4() -> None:
    xy = lab_d.rotate(np.array([[x * 600.0, y * 1500.0] for y in (0, 1)
                                for x in range(6)]), 285.0)
    fr, wk, _, _ = lab_d.farm_energy(xy)
    p("P73", f"two rows, 4D x 10D: wake loss {100 * (1 - wk / fr):.2f} % "
             "(8D: 6.50 %)")
    vv = np.arange(0.0, 30.01, 0.5)
    _, _, sm0, _ = rotor.curve_arrays()
    p("P74", f"model curve, 1.225, smoothed: "
             f"{np.interp(lab_d.hourly()[0], vv, sm0).sum() / 1e3:,.0f} MWh "
             "per turbine (pack 18,233)")
    p("P75", "see text: criteria")


def deeper() -> None:
    """Problems on the deeper lessons (aerodynamics, control, subsystems,
    measurement and sound): P76 onwards."""
    from companion.ch11 import dynamics, lab_f
    p("P76", f"Glauert Cp_max at TSR 2: {w.glauert_cp_max(2.0):.4f}")
    ct = w.thrust_coefficient([0.5, 0.6])
    p("P77", f"a 0.5: momentum 1.000, Buhl {ct[0]:.3f}; a 0.6: momentum"
             f" 0.960, Buhl {ct[1]:.3f}")
    p("P78", f"shear 0.14, 9 m/s at 100 m: lowest tip 25 m "
             f"{9 * 0.25 ** 0.14:.2f} m/s, top tip {9 * 1.75 ** 0.14:.2f} m/s")
    p("P79", f"sun 24, ring 96: ratio {w.planetary_ratio(24, 96):.2f}, planet"
             f" {(96 - 24) // 2} teeth, (24 + 96)/3 = {(24 + 96) / 3:.0f} (ok)")
    p("P80", f"load +10 %, rollers: life x {1.1 ** (-10 / 3):.3f}"
             f" ({100 * (1.1 ** (-10 / 3) - 1):.1f} %)")
    p("P81", f"two 40 dB sources: {w.sum_levels([40, 40]):.1f} dB;"
             f" ten: {w.sum_levels([40] * 10):.1f} dB")
    p("P82", f"slant distance sqrt(600^2 + 100^2) = {math.hypot(600, 100):.1f} m")
    p("P83", f"9 x (1.10/1.056)^(1/3) = {9 * (1.10 / 1.056) ** (1 / 3):.3f} m/s")
    # level 2
    k, w1 = dynamics.k_law(), 9.74 * math.pi / 30
    eps = 1e-4
    ta = (dynamics.aero_torque(9.0, w1 + eps, 0)
          - dynamics.aero_torque(9.0, w1 - eps, 0)) / (2 * eps)
    tau2 = dynamics.J_TOTAL / 2 / (2 * k * w1 - ta)
    p("P84", f"J halved: tau = {tau2:.1f} s (full J: 3.8 s)")
    fc = 10 / 60 * w.planetary_ratio(21, 99)
    p("P85", f"stage 2 at 10 rpm: carrier {fc:.3f} Hz x 97 = {97 * fc:.1f} Hz")
    p("P86", f"cap: 20e6 / (225e6 x 0.9 x 1.5) = "
             f"{1e3 * 20e6 / (225e6 * 0.9 * 1.5):.1f} mm")
    p("P87", f"uniform 4 kN/m over 72.5 m: q L^2 / 2 = "
             f"{4e3 * 72.5 ** 2 / 2 / 1e6:.2f} MN m")
    e1 = 0.5 * dynamics.J_TOTAL * (7.58 * math.pi / 30) ** 2
    e2 = 0.5 * dynamics.J_TOTAL * (9.74 * math.pi / 30) ** 2
    p("P88", f"rotor energy {e1 / 1e6:.2f} MJ -> {e2 / 1e6:.2f} MJ"
             f" (+{(e2 - e1) / 1e6:.2f} MJ)")
    p("P89", f"G doubled, same gains: wn x sqrt(2) = {math.sqrt(2):.3f};"
             f" 0.6 -> {0.6 * math.sqrt(2):.2f} rad/s")
    p("P90", f"8.1 rpm x 60 x 7,735 h = {8.1 * 60 * 7735 / 1e6:.2f} million rev")
    p("P91", f"shear 0.3: REWS {w.rotor_equivalent_speed(10, 100, 75, 0.3):.3f}"
             " m/s for 10 m/s at hub")
    # level 3
    p("P92", f"night mode 1.81 % of 188.16 GWh = {0.0181 * 188.16:.2f} GWh")
    p("P93", f"own use, 12 turbines: {12 * 168.2 / 1e3:.2f} GWh; imported"
             f" {12 * 4.2:.0f} MWh")
    v, rho, pw, flag = lab_f.records()
    good = flag == 0
    v_n = v * (rho / lab_f.RHO_REF) ** (1 / 3)
    base = lab_f.aep(w.bin_power_curve(v_n[good], pw[good]), 7.0)
    high = lab_f.aep(w.bin_power_curve(1.02 * v_n[good], pw[good]), 7.0)
    p("P94", f"anemometer reads 2 % high: measured energy {high:,.0f} vs"
             f" {base:,.0f} MWh ({100 * (high / base - 1):+.1f} %)")
    life = w.bearing_life_mrev(9.0e6, 2.125e6)
    p("P95", f"C 9 MN: L10 = {life:.0f} million rev = {life / 3.77:.1f} years")
    p("P96", f"erosion on 6 of 12 turbines: {6.84 / 2:.2f} GWh a year")
    clear = 6 + 75 * (math.sin(math.radians(5)) + math.sin(math.radians(3))) \
        + 4 - 2.2
    p("P97", f"prebend 4 m: clearance {clear:.1f} m; less 18.1 m deflection:"
             f" {clear - 18.1:.1f} m (rule {0.3 * clear:.1f} m)")
    p("P98", "see text: criteria")
    m_op = 923e3 * 100.0
    s46 = m_op / (math.pi * 2.25 ** 2 * 0.046)
    s40 = m_op / (math.pi * 2.25 ** 2 * 0.040)
    p("P99", f"wall 40 mm: {s40 / 1e6:.0f} MPa (46 mm: {s46 / 1e6:.0f} MPa)")
    f100 = 4 * m_op / (100 * 4.30) - (271 + 340) * 1e3 * 9.81 / 100
    p("P100", f"100 bolts: 4 M / (n D) - W / n = {f100 / 1e3:.0f} kN")
    p("P101", f"joint opens, m = 4: damage x (1/0.12)^4 = {(1 / 0.12) ** 4:,.0f}")
    p("P102", f"yaw at 0.3 deg/s: 16,546 / 0.3 / 3600 = {16546 / 0.3 / 3600:.1f} h")
    p("P103", f"availability loss 12 x 326 MWh = {12 * 326 / 1e3:.2f} GWh ="
              f" {12 * 326 * 50 / 1e3:.0f} k u at 50 u/MWh")
    p("P104", f"gearbox stop halved: {168 - 36} h a year -> time availability"
              f" about {100 * (1 - 132 / 8760):.2f} %")
    p("P105", f"162 m rotor: 5e6 / (pi 81^2) = {5e6 / (math.pi * 81 ** 2):.0f}"
              " W/m2")
    extra = 12 * (18921 - 17168)
    p("P106", f"12 x (18,921 - 17,168) = {extra / 1e3:.1f} GWh ="
              f" {extra * 50 / 1e3:,.0f} k u a year before curtailment")


if __name__ == "__main__":
    level_1()
    level_2()
    level_3()
    level_4()
    deeper()
    emit("solutions", OUT)
