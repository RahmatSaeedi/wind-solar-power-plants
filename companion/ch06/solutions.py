"""Chapter 6 — numerical answers of the end-of-chapter problems.

Run from the project root:   python -m companion.ch06.solutions
Writes companion/ch06/expected/solutions.txt. Problem numbers match the book.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plantp import datapack, dc, screening as sc  # noqa: E402

HERE = Path(__file__).resolve().parent


def main() -> None:
    m = dc.PVM_550
    L: list[str] = []
    out = L.append
    v_mp26 = 26 * m.v_mp

    out(f"P03 energy: 14.30 kW x 6 h = {14.30 * 6:.1f} kWh")
    out(f"P09 48 V into 12 ohm: I = {dc.ohm_current(48, 12):.1f} A, P = {dc.power_v2r(48, 12):.0f} W")
    rp = dc.parallel(10, 15, 30)
    i_tot = 24 / (rp + 5)
    v_par = i_tot * rp
    out(f"P10 10||15||30 = {rp:.2f} ohm; total = {rp + 5:.2f} ohm; I = {i_tot:.2f} A; "
        f"branch currents {v_par / 10:.2f}, {v_par / 15:.2f}, {v_par / 30:.2f} A (V across = {v_par:.2f} V)")
    out(f"P11 250 m of 6 mm2 Cu: R20 = {dc.conductor_resistance(250, 6, 'copper', 20):.4f} ohm, "
        f"R70 = {dc.conductor_resistance(250, 6, 'copper', 70):.4f} ohm")
    sol = dc.solve_dc(3, [(1, 2, 3.0), (2, 0, 6.0)], [(1, 0, 12.0)], [(0, 2, 2.0)])
    out(f"P12 node voltage = {sol.node_voltages[2]:.4f} V; current in the 3 ohm resistor = "
        f"{(12 - sol.node_voltages[2]) / 3:.4f} A")
    v_th, r_th = dc.thevenin(3, [(1, 2, 6.0), (2, 0, 3.0)], [(1, 0, 24.0)], terminal_a=2)
    out(f"P13 V_th = {v_th:.3f} V, R_th = {r_th:.4f} ohm; P_max = V_th^2/(4 R_th) = {v_th ** 2 / (4 * r_th):.3f} W")
    i8 = v_th / (r_th + 8)
    out(f"P13 with 8 ohm: I = {i8:.3f} A, P = {i8 ** 2 * 8:.3f} W, efficiency = {8 / (r_th + 8):.2f}")
    rs = (51.2 - 49.6) / 80
    out(f"P14 R_s = {rs * 1000:.1f} mOhm; V(150 A) = {51.2 - rs * 150:.2f} V; internal loss = {rs * 150 ** 2:.0f} W")
    f15 = dc.feeder(20, 15, 4, "copper", 30, source_voltage_v=12)
    out(f"P15 loop R = {f15.loop_resistance_ohm:.4f} ohm; drop = {f15.drop_v:.3f} V = "
        f"{100 * f15.drop_fraction:.1f} %; loss = {f15.loss_w:.1f} W")
    a16 = dc.area_for_drop(20, 15, 0.03 * 12, "copper", 30)
    f16 = dc.feeder(20, 15, dc.next_standard_area(a16), "copper", 30, source_voltage_v=12)
    out(f"P16 area for 3 % = {a16:.2f} mm2 -> {dc.next_standard_area(a16)} mm2 "
        f"(drop {100 * f16.drop_fraction:.2f} %)")
    r20_6 = dc.conductor_resistance(1, 6, "copper", 20)
    out(f"P17 6 mm2 Cu: R20 = {r20_6 * 1000:.3f} mOhm/m; I_c = {dc.runaway_current(r20_6, 0.00393, 4.5):.1f} A")
    out(f"P18 V_oc 27 modules at -15 C = {dc.string_voc(m, 27, -15):.1f} V; "
        f"max modules for 1500 V at -15 C = {dc.max_modules_in_series(m, 1500, -15)}")
    out(f"P19 4 strings: backfeed = 3 x {m.i_sc} = {3 * m.i_sc:.2f} A vs 25 A")
    out(f"P20 +-(0.2 % x 1076.0 + 1 x 0.1) = +-{0.002 * 1076.0 + 0.1:.2f} V")

    out(f"P21 see feeder_report: Cu 185 mm2 -> 1.08 %, Cu 240 mm2 -> 0.83 %; Al 300 -> 1.09 %, Al 400 -> 0.82 %")
    saving = 4215 - 2529
    out(f"P22 saving per feeder = {saving} kWh/yr; x 175 = {saving * 175 / 1000:.0f} MWh/yr; "
        f"over 25 years = {saving * 175 * 25 / 1e6:.2f} GWh")
    v_hot = 26 * m.v_mp * (1 + m.beta_voc_pct_per_c / 100 * (70 - 25))
    out(f"P23 V_mp(70 C) ~ {v_hot:.0f} V vs assumed MPPT minimum 850 V: margin {v_hot - 850:.0f} V")
    v40, i40 = dc.pv_resistive_operating_point(m, 26, 40)
    out(f"P24 40 ohm: {v40:.0f} V, {i40:.2f} A, {v40 * i40 / 1000:.2f} kW; best resistor 82.6 ohm (examples E17)")
    out(f"P25 113 degraded connectors x 3.44 W = {113 * dc.power_i2r(m.i_mp, 0.020):.0f} W at STC")
    r_loop = dc.feeder(1, 180, 240, "aluminium", 50).loop_resistance_ohm
    out(f"P26 loop resistance to expect = {r_loop * 1000:.2f} mOhm at 50 C; at 20 C = "
        f"{dc.feeder(1, 180, 240, 'aluminium', 20).loop_resistance_ohm * 1000:.2f} mOhm; "
        f"at 10 A test current the drop is {10 * dc.feeder(1, 180, 240, 'aluminium', 20).loop_resistance_ohm * 1000:.0f} mV")
    day = datapack.load_hourly("day_summer")
    g12 = float(day["ghi_wm2"].iloc[12])
    p12 = 24 * 26 * 0.550 * g12 / 1000 * sc.PR_DC
    out(f"P40 23 June 12:00, GHI = {g12} W/m2: P_dc = 343.2 kWp x {g12 / 1000:.4f} x {sc.PR_DC} = {p12:.1f} kW; "
        f"I = {p12 * 1000 / v_mp26:.1f} A")

    i29 = 16 * m.i_mp
    a29 = dc.area_for_drop(i29, 120, 0.01 * v_mp26, "aluminium", 50)
    f29 = dc.feeder(i29, 120, dc.next_standard_area(a29), "aluminium", 50, source_voltage_v=v_mp26)
    out(f"P29 16 strings: I = {i29:.2f} A; area for 1 % = {a29:.1f} mm2 -> {dc.next_standard_area(a29)} mm2; "
        f"drop {f29.drop_v:.2f} V ({100 * f29.drop_fraction:.2f} %), loss {f29.loss_w:.0f} W")
    v_cold = dc.string_voc(m, 1, -25)
    n31 = dc.max_modules_in_series(m, 1500, -25)
    v_hot75 = n31 * m.v_mp * (1 + m.beta_voc_pct_per_c / 100 * (75 - 25))
    out(f"P31 V_oc/module at -25 C = {v_cold:.3f} V -> {n31} modules ({n31 * v_cold:.1f} V); "
        f"V_mp at 75 C ~ {v_hot75:.1f} V vs 850 V")

    n36 = dc.max_modules_in_series(m, 1000, -10)
    v36 = n36 * m.v_mp
    i36 = 24 * 26 * 550 / v36           # same combiner power, larger current
    f36 = dc.feeder(i36, 180, 240, "aluminium", 50, source_voltage_v=v36)
    out(f"P36 1000 V system: {n36} modules/string, V_mp = {v36:.1f} V; same 343.2 kW -> I = {i36:.1f} A; "
        f"loss {f36.loss_w:.0f} W = {100 * f36.loss_w / (i36 * v36):.2f} % (was 1.37 %); "
        f"strings for 60 MWp = {math.ceil(60e6 / (n36 * 550))}")
    out(f"P39 one string of 24 missing: {100 / 24:.2f} % less power; 2 % is about half a string")

    # ---- problems 41-62 (expanded edition) --------------------------------------------
    r100 = dc.cylinder_insulation_resistance(1e13, 1.13e-3, 2.9e-3, 100.0)
    r250 = dc.cylinder_insulation_resistance(1e13, 1.13e-3, 2.9e-3, 250.0)
    thick = math.log(4.67 / 1.13) / math.log(2.9 / 1.13)
    out(f"P45 R_ins 250 m = {r250 / 1e9:.2f} GOhm (100 m: {r100 / 1e9:.2f}); "
        f"r2 2.9 -> 4.67 mm multiplies R_ins by {thick:.3f}")
    r75 = dc.pt100_resistance(75)
    out(f"P46 PT100 at 75 C: R = {r75:.3f} ohm, bridge output = "
        f"{1000 * dc.bridge_output(5, 100, 100, 100, r75):.2f} mV; 0.5 ohm of lead = "
        f"{0.5 / (100 * 0.00385):.2f} C error")
    a = [[9.0, -6.0], [-6.0, 12.0]]
    ia, ib = __import__("numpy").linalg.solve(a, [12.0, 0.0])
    out(f"P47 mesh: 9 Ia - 6 Ib = 12, -6 Ia + 12 Ib = 0 -> Ia = {ia:.3f} A, Ib = {ib:.3f} A; "
        f"load 4 ohm: {4 * ib:.2f} V")
    out(f"P48 4.7 mF at 800 V: E = {dc.capacitor_energy(4.7e-3, 800):.0f} J; tau = "
        f"{100e3 * 4.7e-3:.0f} s; to 50 V: {dc.rc_time_to_discharge(800, 50, 100e3, 4.7e-3):.0f} s "
        f"= {dc.rc_time_to_discharge(800, 50, 100e3, 4.7e-3) / 60:.1f} min")
    out(f"P49 200 uH at 400 A: E = {dc.inductor_energy(200e-6, 400):.0f} J")
    k_cu = dc.adiabatic_k("copper", 90, 250)
    a50 = 20_000 * math.sqrt(0.5) / k_cu
    out(f"P50 95 mm2 Cu, 12 kA: t = {dc.adiabatic_withstand_time(12_000, 95, k_cu):.2f} s; "
        f"20 kA for 0.5 s needs {a50:.1f} mm2 -> {dc.next_standard_area(a50)} mm2")
    f51 = dc.feeder(6, 160, 2.5, "copper", 30)
    out(f"P51 160 m, 2.5 mm2, 6 A: drop {f51.drop_v:.2f} V; coil sees {95 - f51.drop_v:.2f} V "
        f"(needs 80 V)")
    a_star = dc.kelvin_optimum_area(4215 * 240, 0.05, 5.4, 0.08)
    out(f"P52 A* = {a_star:.0f} mm2; price x2 -> {a_star * math.sqrt(2):.0f}; "
        f"cable cost x2 -> {a_star / math.sqrt(2):.0f} mm2")
    out(f"P53 T_cell = 38 + 25/800 x 950 = {float(dc.cell_temperature_noct(38, 950)):.1f} C")
    g1, g2 = 1 / 0.050, 1 / 0.075
    out(f"P54 shares: {250 * g1 / (g1 + g2):.0f} A and {250 * g2 / (g1 + g2):.0f} A")
    out("P55 6 mm2 strings + 240 mm2 feeder: 0.29 + 0.74 = 1.03 %; "
        "6 mm2 + 400 mm2: 0.29 + 0.45 = 0.74 % (from ex_dcbudget)")
    out(f"P57 2 m2 loop, 100 m: dB/dt = {2e-7 * 3e10 / 100:.0f} T/s -> v = {2 * 2e-7 * 3e10 / 100:.0f} V")
    _, v05 = dc.rc_discharge_euler(9, 10e3, 1e-3, 30, 0.05)
    exact = float(dc.rc_discharge(9, 10e3, 1e-3, 30))
    out(f"P58 Euler dt = 0.05 s: error {v05[-1] - exact:+.5f} V (dt = 0.1 s: -0.00672 V)")
    r_max = 300 / (0.010 * math.log(1100 / 50))
    out(f"P59 bleeder for 50 V within 300 s: R <= {r_max:.0f} ohm; continuous loss at 1100 V = "
        f"{1100 ** 2 / r_max:.1f} W (50 kOhm: {1100 ** 2 / 50e3:.1f} W)")
    rho30 = dc.resistivity_at("copper", 30)
    a60 = 2 * rho30 * 250 * 15 / (93.5 - 77) * 1e6
    out(f"P60 3 coils = 15 A, allowed drop 16.5 V: A >= {a60:.2f} mm2 -> {dc.next_standard_area(a60)} mm2")
    saving = (103.9 - 69.3) * 4196 / 1000
    out(f"P62 6 mm2 instead of 4 mm2 saves {103.9 - 69.3:.1f} kWh per string per year; "
        f"x 4196 = {saving:.0f} MWh/yr")

    text = "\n".join(L) + "\n"
    import textwrap
    wrapped = []
    for line in L:
        wrapped += textwrap.wrap(line, 78, subsequent_indent="    ") or [""]
    text = "\n".join(wrapped) + "\n"
    (HERE / "expected").mkdir(exist_ok=True)
    (HERE / "expected" / "solutions.txt").write_text(text, encoding="utf-8", newline="\n")
    print(text)


if __name__ == "__main__":
    main()
