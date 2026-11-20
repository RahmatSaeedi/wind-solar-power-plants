"""Chapter 6 — every number used in the chapter's worked examples.

Run from the project root:   python -m companion.ch06.examples
Writes companion/ch06/expected/examples.txt. Each block is labelled with the
example it belongs to (E01, E02, ...), so a reader can find and re-run it.
"""
from __future__ import annotations

import math
import sys
import textwrap
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plantp import datapack, dc, screening as sc  # noqa: E402

HERE = Path(__file__).resolve().parent
E = dc.ELEMENTARY_CHARGE
N_CU = 8.49e28            # free electrons per m3 in copper (textbook value)
RHO_MASS = {"copper": 8.96, "aluminium": 2.70}   # g/cm3


def main() -> None:
    m = dc.PVM_550
    L: list[str] = []
    out = L.append

    # ---- A: foundations ------------------------------------------------------------
    q = m.i_mp * 3600
    out(f"E01 charge in 1 h at {m.i_mp} A: Q = {q:,.0f} C; electrons = Q/e = {q / E:.3e}")
    v_drift = m.i_mp / (N_CU * E * 4e-6)
    out(f"E02 drift speed, {m.i_mp} A in 4 mm2 copper: v = I/(n e A) = {v_drift:.3e} m/s = {v_drift * 1000:.3f} mm/s; "
        f"time to cross 1 m = {1 / v_drift / 3600:.2f} h")
    v_string = 26 * m.v_mp
    out(f"E03 energy to move {q:,.0f} C through {v_string:.1f} V: W = QV = {q * v_string / 1e6:.2f} MJ = "
        f"{q * v_string / 3.6e6:.2f} kWh (= one hour of a {v_string * m.i_mp / 1000:.2f} kW string)")
    r100 = dc.conductor_resistance(100, 4, "copper", 20)
    out(f"E05 100 m of 4 mm2 copper at 20 C: R = {r100:.3f} ohm; same in aluminium: "
        f"{dc.conductor_resistance(100, 4, 'aluminium', 20):.3f} ohm")
    area_ratio = dc.RESISTIVITY_20C["aluminium"] / dc.RESISTIVITY_20C["copper"]
    mass_ratio = area_ratio * RHO_MASS["aluminium"] / RHO_MASS["copper"]
    out(f"E06 equal resistance: A_Al/A_Cu = {area_ratio:.3f}; mass_Al/mass_Cu = {area_ratio:.3f} x "
        f"{RHO_MASS['aluminium']}/{RHO_MASS['copper']} = {mass_ratio:.3f}")
    out(f"E08 string power at STC: {v_string:.1f} V x {m.i_mp} A = {v_string * m.i_mp / 1000:.2f} kW")
    out(f"E09 3 A in 4 ohm: P = {dc.power_i2r(3, 4):.0f} W; at 6 A: {dc.power_i2r(6, 4):.0f} W")
    out(f"E11 parallel 4, 6, 12 ohm = {dc.parallel(4, 6, 12):.3f} ohm; series = {dc.series(4, 6, 12):.0f} ohm; "
        f"divider 12 V over 4 + 8 ohm -> {dc.divider_voltage(12, 4, 8):.2f} V across 8 ohm")
    out(f"E12 combiner busbar: 24 x {m.i_mp} A = {24 * m.i_mp:.2f} A")
    sol = dc.solve_dc(4, [(1, 2, 2.0), (2, 3, 3.0), (2, 0, 4.0)], [(1, 0, 10.0), (3, 0, 5.0)])
    vx = sol.node_voltages[2]
    i1, i3, i2 = (10 - vx) / 2, (5 - vx) / 3, vx / 4
    out(f"E13 node voltage V_x = 80/13 = {vx:.4f} V; I1 = {i1:.4f} A, I3 = {i3:.4f} A, I2 = {i2:.4f} A; "
        f"KCL I1 + I3 - I2 = {i1 + i3 - i2:.1e}")
    v_th, r_th = dc.thevenin(3, [(1, 2, 4.0), (2, 0, 4.0)], [(1, 0, 12.0)], terminal_a=2)
    out(f"E14 Thevenin: V_th = {v_th:.3f} V, R_th = {r_th:.4f} ohm; with 4 ohm load: I = {v_th / (r_th + 4):.3f} A, "
        f"V = {4 * v_th / (r_th + 4):.3f} V")
    full = dc.solve_dc(3, [(1, 2, 4.0), (2, 0, 4.0), (2, 0, 4.0)], [(1, 0, 12.0)])
    out(f"E14 check on the full circuit with the 4 ohm load: V = {full.node_voltages[2]:.3f} V")
    for rl in (2.0, 18.0):
        i = v_th / (r_th + rl)
        out(f"E15 R_L = {rl:.0f} ohm: I = {i:.3f} A, P_load = {i * i * rl:.3f} W, efficiency = {rl / (r_th + rl):.2f}")

    # ---- B: practical calculations ----------------------------------------------------
    r_s = (12.6 - 11.9) / 50
    out(f"E16 battery: R_s = (12.6 - 11.9)/50 = {r_s * 1000:.0f} mOhm; terminal voltage at 200 A = {12.6 - r_s * 200:.2f} V")
    for rl in (80.0, 40.0):
        v_op, i_op = dc.pv_resistive_operating_point(m, 26, rl)
        out(f"E17 string into {rl:.0f} ohm: V = {v_op:.1f} V, I = {i_op:.2f} A, P = {v_op * i_op / 1000:.2f} kW")
    vgrid = np.linspace(0, dc.string_voc(m, 26, 25), 4001)
    pgrid = vgrid * dc.pv_iv_curve(m, 26, vgrid)
    out(f"E17 model maximum power: {pgrid.max() / 1000:.2f} kW at {vgrid[pgrid.argmax()]:.0f} V "
        f"(datasheet 26 x 550 W = {26 * 0.55:.2f} kW); best resistor = {vgrid[pgrid.argmax()] ** 2 / pgrid.max():.1f} ohm")

    # E18-E20: the Plant P feeder (numbers also in feeder_report.txt)
    i_f = 24 * m.i_mp
    fr = dc.feeder(i_f, 180, 240, "aluminium", 50, source_voltage_v=v_string)
    out(f"E18 feeder: loop R = {fr.loop_resistance_ohm:.5f} ohm; drop = {fr.drop_v:.2f} V ({100 * fr.drop_fraction:.2f} %); "
        f"loss = {fr.loss_w:.0f} W")
    need = dc.area_for_drop(i_f, 180, 0.01 * v_string, "aluminium", 50)
    out(f"E19 1 % drop needs {need:.1f} mm2 Al -> {dc.next_standard_area(need)} mm2; copper needs "
        f"{dc.area_for_drop(i_f, 180, 0.01 * v_string, 'copper', 50):.1f} mm2 -> "
        f"{dc.next_standard_area(dc.area_for_drop(i_f, 180, 0.01 * v_string, 'copper', 50))} mm2")

    # E20: annual energy lost in the feeder, current proportional to irradiance (screening model)
    hourly = datapack.load_hourly()
    g = hourly["ghi_wm2"].to_numpy()
    p_dc_kw = 24 * 26 * 0.550 * g / 1000 * sc.PR_DC                 # kW at the combiner
    current = np.minimum(p_dc_kw * 1000 / v_string, 1.25 * i_f)     # A, assuming V stays near V_mp
    for area in (240, 400):
        r_loop = dc.feeder(1.0, 180, area, "aluminium", 50).loop_resistance_ohm
        e_loss = float((r_loop * current ** 2).sum()) / 1000            # kWh
        e_thru = float(p_dc_kw.sum())                                  # kWh
        out(f"E20 {area} mm2 Al: energy through feeder {e_thru:,.0f} kWh/yr, lost {e_loss:,.0f} kWh/yr "
            f"= {100 * e_loss / e_thru:.2f} % (peak-hour loss fraction {100 * r_loop * i_f / v_string:.2f} %)")
    out(f"E20 data: {datapack.cite('S0', '1.0.0')}; assumptions: I proportional to GHI, PR_dc = {sc.PR_DC}, "
        "conductor at 50 C all year (conservative)")

    # E21-E22: heating of a 4 mm2 copper string cable in free air
    r20 = dc.conductor_resistance(1.0, 4.0, "copper", 20.0)
    h, d = 10.0, 0.006
    r_th = 1.0 / (h * math.pi * d)
    out(f"E21 4 mm2 Cu: R20 = {r20 * 1000:.2f} mOhm/m; R_th = 1/(h pi d) = 1/({h} x pi x {d}) = {r_th:.2f} K m/W")
    for i, ta in ((14.0, 30.0), (40.0, 30.0), (60.0, 50.0)):
        t_exact = dc.conductor_temperature_closed_form(i, r20, dc.TEMP_COEFF["copper"], ta, r_th)
        t_cold = ta + i * i * dc.conductor_resistance(1.0, 4.0, "copper", ta) * r_th
        out(f"E21 I = {i:.0f} A, T_a = {ta:.0f} C: one-step estimate {t_cold:.1f} C, exact {t_exact:.1f} C")
    out(f"E22 runaway current of the linear model: I_c = 1/sqrt(R20 alpha R_th) = "
        f"{dc.runaway_current(r20, dc.TEMP_COEFF['copper'], r_th):.1f} A")

    # E23-E25: measurement
    out(f"E23 voltmeter loading: 10 MOhm -> {dc.voltmeter_reading(12, 1e6, 1e6, 10e6):.3f} V; "
        f"1 MOhm -> {dc.voltmeter_reading(12, 1e6, 1e6, 1e6):.3f} V; true 6.000 V")
    reading = v_string - fr.drop_v
    acc = 0.005 * reading + 2 * 1.0
    out(f"E24 meter +-(0.5 % + 2 digits), 1 V resolution, reading {reading:.0f} V: +-{acc:.1f} V; "
        f"difference of two such readings: +-{2 * acc:.1f} V vs a drop of {fr.drop_v:.1f} V")
    out(f"E25 ammeter burden: 1.5 V into 1 ohm: ideal {1.5:.2f} A; with 0.1 ohm meter {1.5 / 1.1:.3f} A")

    # E26-E27: faults
    out(f"E26 backfeed into one faulted string from the other 23: 23 x {m.i_sc} = {23 * m.i_sc:.1f} A "
        f"vs module maximum series fuse 25 A")
    out(f"E26 two strings in parallel: backfeed = 1 x {m.i_sc} = {m.i_sc:.2f} A (below 25 A)")
    out("E26 three strings: backfeed = 2 x {0} = {1:.2f} A (above 25 A)".format(m.i_sc, 2 * m.i_sc))

    # E28-E29: operating envelope
    for t in (-20, -10):
        out(f"E28 V_oc per module at {t} C = {m.v_oc} x (1 + {m.beta_voc_pct_per_c / 100} x ({t} - 25)) = "
            f"{dc.string_voc(m, 1, t):.4f} V; max modules for 1500 V = {dc.max_modules_in_series(m, 1500, t)}")
    v_mp_hot = 26 * m.v_mp * (1 + m.beta_voc_pct_per_c / 100 * (70 - 25))
    out(f"E29 V_mp of 26 modules at 70 C (V_oc coefficient used as an approximation) = {v_mp_hot:.1f} V")

    # E30-E32: protection, connectors, plant counts
    out(f"E30 fuse lower bound with an assumed factor 1.5: 1.5 x {m.i_sc} = {1.5 * m.i_sc:.2f} A -> 25 A fuse "
        f"(<= module maximum series fuse 25 A)")
    for rc in (0.0005, 0.020):
        out(f"E31 connector contact {rc * 1000:.1f} mOhm at {m.i_mp} A: {dc.power_i2r(m.i_mp, rc):.3f} W")
    n_str = math.ceil(60e6 / (26 * 550))
    n_cb = math.ceil(n_str / 24)
    out(f"E32 strings = ceil(60 MWp / (26 x 550 W)) = {n_str}; modules = {n_str * 26:,}; "
        f"DC capacity = {n_str * 26 * 550 / 1e6:.3f} MWp; combiner boxes = ceil({n_str}/24) = {n_cb}")
    pairs = n_str * (26 + 1)
    out(f"E31 connector pairs in the array (26 + 1 per string) ~ {pairs:,}; 0.1 % degraded = {pairs * 0.001:.0f}")
    total_loss_kw = n_cb * fr.loss_w / 1000
    out(f"E32 if every combiner feeder were like E18: {n_cb} x {fr.loss_w / 1000:.2f} kW = {total_loss_kw:.0f} kW at STC")

    def wrapped(lines):
        out_lines = []
        for line in lines:
            out_lines += textwrap.wrap(line, 78, subsequent_indent="    ") or [""]
        return "\n".join(out_lines) + "\n"

    (HERE / "expected").mkdir(exist_ok=True)
    text = wrapped(L)
    (HERE / "expected" / "examples.txt").write_text(text, encoding="utf-8", newline="\n")
    # the two blocks the chapter quotes inline get their own files
    (HERE / "expected" / "ex_annual_loss.txt").write_text(
        wrapped([s for s in L if s.startswith("E20")]), encoding="utf-8", newline="\n")
    (HERE / "expected" / "ex_heating.txt").write_text(
        wrapped([s for s in L if s.startswith(("E21", "E22"))]), encoding="utf-8", newline="\n")
    print(text)


if __name__ == "__main__":
    main()
