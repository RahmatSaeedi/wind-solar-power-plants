"""Chapter 6 (expanded edition) — numbers for the additional worked examples.

Run from the project root:   python -m companion.ch06.examples2
Writes one small text file per example group to companion/ch06/expected/
(each line at most 78 characters, so the book can quote it unchanged), the
combined file examples2.txt, and the plot data of the new figures.

Every value marked "assumed" is a teaching assumption stated in the chapter.
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
EXPECTED = HERE / "expected"
DATA = HERE.parents[1] / "diagrams" / "data"
ALL: list[str] = []


def emit(name: str, lines: list[str]) -> None:
    wrapped = []
    for line in lines:
        wrapped += textwrap.wrap(line, 78, subsequent_indent="    ") or [""]
    text = "\n".join(wrapped) + "\n"
    (EXPECTED / f"{name}.txt").write_text(text, encoding="utf-8", newline="\n")
    ALL.append(f"== {name}")
    ALL.extend(wrapped)
    print(text)


def csv(name: str, header: str, rows) -> None:
    with open(DATA / name, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(header + "\n")
        for row in rows:
            fh.write(",".join(row) + "\n")


def main() -> None:
    EXPECTED.mkdir(exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    m = dc.PVM_550
    v_mp26 = 26 * m.v_mp

    # ---- resistivity spectrum (order-of-magnitude textbook values) -------------------
    spectrum = [("silver", 1.59e-8), ("copper", 1.72e-8), ("aluminium", 2.82e-8),
                ("iron", 9.7e-8), ("stainless steel", 6.9e-7), ("nichrome", 1.1e-6),
                ("sea water", 0.2), ("intrinsic silicon", 2.3e3), ("glass", 1e12),
                ("PVC", 1e13), ("XLPE", 1e16)]
    csv("ch06-resistivity.csv", "index,material,log10_rho",
        [(str(i), n, f"{math.log10(r):.2f}") for i, (n, r) in enumerate(spectrum)])
    emit("ex_spectrum", [f"{n:18s} rho = {r:.2e} ohm m" for n, r in spectrum]
         + [f"ratio XLPE / copper = 10^{math.log10(1e16 / 1.72e-8):.1f}"])

    # ---- insulation resistance --------------------------------------------------------
    r_cable = dc.cylinder_insulation_resistance(1e13, 1.13e-3, 2.9e-3, 100.0)
    lines = [f"100 m PV cable, rho_ins = 1e13 ohm m (assumed), r1 = 1.13 mm, "
             f"r2 = 2.9 mm: R_ins = {r_cable / 1e9:.1f} GOhm"]
    per_inverter = 7 * 24 * 26
    for label, r_mod in (("dry", 1e9), ("wet morning", 5e7)):
        lines.append(f"modules {label}: {r_mod / 1e6:.0f} MOhm each (assumed); "
                     f"{per_inverter} modules on one inverter -> "
                     f"{r_mod / per_inverter / 1e3:.1f} kOhm; whole plant (109,096) -> "
                     f"{r_mod / 109_096 / 1e3:.2f} kOhm")
    emit("ex_insulation", lines)

    # ---- non-ohmic elements ---------------------------------------------------------------
    v = np.linspace(0, 0.8, 81)
    i_d = dc.diode_current(v, saturation_a=1e-12)
    csv("ch06-nonohmic-iv.csv", "v,i_resistor,i_diode",
        [(f"{a:.3f}", f"{a / 0.1:.4f}", f"{min(b, 12.0):.4f}") for a, b in zip(v, i_d)])
    v_fwd = 0.7
    emit("ex_blocking_diode", [
        f"blocking diode, forward drop {v_fwd} V at {m.i_mp} A: "
        f"{v_fwd * m.i_mp:.2f} W per string",
        f"4196 strings: {4196 * v_fwd * m.i_mp / 1000:.1f} kW = "
        f"{100 * v_fwd / v_mp26:.3f} % of the string voltage",
        f"diode current ratio for +{0.0257 * math.log(10) * 1000:.1f} mV: "
        f"{float(dc.diode_current(0.6592) / dc.diode_current(0.6)):.2f}",
    ])

    # ---- energy as an integral --------------------------------------------------------------
    p_max = 26 * 0.550
    exact = p_max * 24 / math.pi
    t = np.arange(6, 19, 1.0)
    p = p_max * np.sin(math.pi * (t - 6) / 12)
    trap = float(np.sum((p[1:] + p[:-1]) / 2))
    simpson = float((p[0] + 4 * p[1:-1:2].sum() + 2 * p[2:-1:2].sum() + p[-1]) / 3)
    rect = float(p[:-1].sum())
    tt = np.linspace(6, 18, 121)
    csv("ch06-sine-day.csv", "t,p", [(f"{a:.2f}", f"{p_max * math.sin(math.pi * (a - 6) / 12):.3f}") for a in tt])
    day = datapack.load_hourly("day_summer")
    p_hours = 14.3 * day["ghi_wm2"].to_numpy() / 1000 * sc.PR_DC
    emit("ex_energy", [
        f"P(t) = {p_max:.2f} kW sin(pi (t - 6)/12), 06:00 to 18:00",
        f"exact integral = {p_max:.2f} x 24/pi = {exact:.3f} kWh",
        f"hourly samples: left rectangles {rect:.3f}, trapezoid {trap:.3f}, "
        f"Simpson {simpson:.3f} kWh",
        f"errors: rectangles {rect - exact:+.3f}, trapezoid {trap - exact:+.3f}, "
        f"Simpson {simpson - exact:+.4f} kWh",
        f"data pack summer day, one string, screening model: "
        f"{p_hours.sum():.1f} kWh (sum of hourly means x 1 h)",
    ])

    # ---- Wheatstone bridge with a PT100 ---------------------------------------------------
    lines = []
    for temp in (0, 25, 50, 100):
        r_t = dc.pt100_resistance(temp)
        out = dc.bridge_output(5.0, 100, 100, 100, r_t)
        lin = 5.0 * (r_t - 100) / 400
        lines.append(f"T = {temp:3d} C: R = {r_t:7.2f} ohm, output {out * 1000:7.2f} mV, "
                     f"linear model {lin * 1000:6.2f} mV")
    emit("ex_bridge", lines)

    # ---- mesh currents and superposition for the two-source circuit ------------------------
    a = np.array([[6.0, -4.0], [-4.0, 7.0]])
    b = np.array([10.0, -5.0])
    ia, ib = np.linalg.solve(a, b)
    v_from_10 = 10 * dc.parallel(3, 4) / (2 + dc.parallel(3, 4))
    v_from_5 = 5 * dc.parallel(2, 4) / (3 + dc.parallel(2, 4))
    emit("ex_mesh", [
        "mesh equations: 6 Ia - 4 Ib = 10 ; -4 Ia + 7 Ib = -5",
        f"Ia = {ia:.4f} A, Ib = {ib:.4f} A; I2 = Ia - Ib = {ia - ib:.4f} A; "
        f"V_x = 4 (Ia - Ib) = {4 * (ia - ib):.4f} V",
        f"superposition: 10 V alone -> {v_from_10:.4f} V; 5 V alone -> "
        f"{v_from_5:.4f} V; sum = {v_from_10 + v_from_5:.4f} V",
    ])

    # ---- parallel battery racks (assumed values) --------------------------------------------
    emf, r_int, cables, load = 1331.2, 0.050, (0.005, 0.010, 0.020), 300.0
    resistors, sources = [], []
    for k, rc in enumerate(cables):
        src_node = 2 + k
        sources.append((src_node, 0, emf))
        resistors.append((src_node, 1, r_int + rc))
    sol = dc.solve_dc(2 + len(cables), resistors, sources, [(1, 0, load)])
    v_bus = sol.node_voltages[1]
    shares = [(emf - v_bus) / (r_int + rc) for rc in cables]
    lines = [f"3 racks, EMF {emf} V, internal {r_int * 1000:.0f} mOhm (assumed), "
             f"cables 5/10/20 mOhm, load {load:.0f} A",
             f"bus voltage = {v_bus:.2f} V"]
    for k, (rc, i_k) in enumerate(zip(cables, shares), 1):
        lines.append(f"rack {k}: R = {(r_int + rc) * 1000:.0f} mOhm, I = {i_k:6.1f} A "
                     f"({100 * i_k / load:.1f} %)")
    lines.append(f"KCL: sum = {sum(shares):.2f} A")
    emit("ex_racks", lines)

    # ---- capacitors, inductors, RC ------------------------------------------------------------
    c_link, v_link, r_bleed = 0.010, 1100.0, 50e3
    tau = r_bleed * c_link
    l_loop = 4e-7 * 180 * math.log(0.05 / math.sqrt(240 / math.pi) * 1000)
    emit("ex_dclink", [
        f"DC-link 10 mF at {v_link:.0f} V (assumed): E = {dc.capacitor_energy(c_link, v_link):.0f} J",
        f"bleeder {r_bleed / 1e3:.0f} kOhm: tau = RC = {tau:.0f} s; time to 50 V = "
        f"tau ln(1100/50) = {dc.rc_time_to_discharge(v_link, 50, r_bleed, c_link):.0f} s "
        f"= {dc.rc_time_to_discharge(v_link, 50, r_bleed, c_link) / 60:.1f} min",
        f"feeder loop inductance (180 m, 50 mm spacing, r = 8.74 mm): "
        f"L = {l_loop * 1e6:.0f} uH; energy at 314.64 A = "
        f"{dc.inductor_energy(l_loop, 314.64):.1f} J",
        "bench RC: 1000 uF, 10 kOhm, tau = 10 s; from 9 V: " + ", ".join(
            f"{s} s -> {float(dc.rc_discharge(9, 10e3, 1e-3, s)):.2f} V" for s in (5, 10, 20, 30)),
    ])
    ts = np.linspace(0, 50, 101)
    csv("ch06-rc-curves.csv", "t,v_charge,v_discharge",
        [(f"{a:.1f}", f"{float(dc.rc_charge(9, 10e3, 1e-3, a)):.4f}",
          f"{float(dc.rc_discharge(9, 10e3, 1e-3, a)):.4f}") for a in ts])

    # ---- numerical method: Euler against the exact discharge ----------------------------------
    lines = ["Euler, C dv/dt = -v/R, 9 V, tau = 10 s, value at t = 30 s"]
    exact30 = float(dc.rc_discharge(9, 10e3, 1e-3, 30))
    for dt in (5.0, 2.0, 1.0, 0.5, 0.1):
        _, vv = dc.rc_discharge_euler(9, 10e3, 1e-3, 30, dt)
        lines.append(f"dt = {dt:4.1f} s: {vv[-1]:.5f} V, error {vv[-1] - exact30:+.5f} V")
    lines.append(f"exact: {exact30:.5f} V")
    emit("ex_euler", lines)

    # ---- fault currents: PV against battery ----------------------------------------------------
    i_string = m.i_sc
    i_cb = 24 * m.i_sc
    i_rack = emf / (r_int + 0.005)
    k_al = dc.adiabatic_k("aluminium", 90, 250)
    k_cu = dc.adiabatic_k("copper", 90, 250)
    emit("ex_fault", [
        f"PV string short circuit: {i_string:.2f} A; 24 strings: {i_cb:.1f} A",
        f"battery rack (assumed EMF {emf} V, 50 mOhm + 5 mOhm cable): "
        f"{i_rack / 1000:.1f} kA",
        f"adiabatic k (90 -> 250 C): copper {k_cu:.1f}, aluminium {k_al:.1f} "
        f"A s^0.5/mm2; copper 70 -> 160 C: {dc.adiabatic_k('copper', 70, 160):.1f}",
        f"240 mm2 Al withstands {i_rack / 1000:.1f} kA for "
        f"{dc.adiabatic_withstand_time(i_rack, 240, k_al):.2f} s and 10 kA for "
        f"{dc.adiabatic_withstand_time(10_000, 240, k_al):.1f} s",
    ])
    csv("ch06-fault-currents.csv", "index,label,current_a",
        [("0", "string", f"{i_string:.2f}"), ("1", "combiner", f"{i_cb:.1f}"),
         ("2", "rack", f"{i_rack:.0f}")])

    # ---- transient heating of a string cable ---------------------------------------------------
    r20 = dc.conductor_resistance(1.0, 4.0, "copper", 20.0)
    r_th = 1 / (10 * math.pi * 0.006)
    c_cu = dc.VOLUMETRIC_HEAT_CAPACITY["copper"] * 4e-6
    c_ins = 1.9e6 * math.pi * ((2.9e-3) ** 2 - (1.13e-3) ** 2)
    tau_th = r_th * (c_cu + c_ins)
    t_final = dc.conductor_temperature_closed_form(40, r20, dc.TEMP_COEFF["copper"], 30, r_th)
    emit("ex_transient", [
        f"4 mm2 cable per metre: C_th = copper {c_cu:.1f} + insulation {c_ins:.1f} "
        f"= {c_cu + c_ins:.1f} J/(K m) (insulation c_v 1.9e6 J/(m3 K), assumed)",
        f"R_th = {r_th:.2f} K m/W; tau = R_th C_th = {tau_th:.0f} s = {tau_th / 60:.1f} min",
        f"step to 40 A from 30 C: final {t_final:.1f} C; after one tau about "
        f"{30 + (t_final - 30) * (1 - math.exp(-1)):.1f} C; after 3 tau "
        f"{30 + (t_final - 30) * (1 - math.exp(-3)):.1f} C",
    ])

    # ---- cell temperature and V_oc over the data-pack year --------------------------------------
    hourly = datapack.load_hourly()
    g = hourly["ghi_wm2"].to_numpy()
    ta = hourly["t_air_c"].to_numpy()
    tc = dc.cell_temperature_noct(ta, g, 45.0)
    lit = g > 0
    voc = np.where(lit, 26 * m.v_oc * (1 + m.beta_voc_pct_per_c / 100 * (tc - 25)), np.nan)
    i_hot = int(np.nanargmax(np.where(lit, tc, np.nan)))
    i_cold = int(np.nanargmin(np.where(lit, tc, np.nan)))
    emit("ex_celltemp", [
        f"data: {datapack.cite('S0', '1.0.0')}; T_cell = T_air + 25/800 G (NOCT 45 C)",
        f"daylight hours: {int(lit.sum())}; coldest lit hour {hourly.index[i_cold]}: "
        f"air {ta[i_cold]:.1f} C, G {g[i_cold]:.0f} W/m2, cell {tc[i_cold]:.1f} C",
        f"hottest cell hour {hourly.index[i_hot]}: air {ta[i_hot]:.1f} C, "
        f"G {g[i_hot]:.0f} W/m2, cell {tc[i_hot]:.1f} C",
        f"highest string V_oc in the year (26 modules): {np.nanmax(voc):.1f} V; "
        f"27 modules: {np.nanmax(voc) * 27 / 26:.1f} V",
        f"hours with GHI above 1000 W/m2: {int((g > 1000).sum())}",
        "caution: at sunrise V_oc is lower than this model says (low irradiance) "
        "and cells can be colder than air on clear nights; chapter 10 refines this",
    ])
    days = hourly.index.day_of_year.to_numpy()
    rows = []
    for d in range(1, 366):
        sel = (days == d) & lit
        if sel.any():
            rows.append((str(d), f"{np.nanmax(voc[sel]):.1f}"))
    csv("ch06-voc-year.csv", "day,voc_max", rows)

    # ---- Kelvin's law with illustrative economics ------------------------------------------------
    k_loss = 4215 * 240                     # kWh mm2 per year, from E20 (240 mm2 Al)
    price, cost_mm2_m, length_cond, annuity = 0.05, 0.015, 360.0, 0.08
    c_area = cost_mm2_m * length_cond
    a_opt = dc.kelvin_optimum_area(k_loss, price, c_area, annuity)
    lines = [f"K = 4215 kWh x 240 mm2 = {k_loss:,} kWh mm2/yr; energy value {price} "
             f"units/kWh; conductor {cost_mm2_m} units/(mm2 m) x {length_cond:.0f} m; "
             f"annuity {annuity} (all fictional)",
             f"optimum A* = sqrt({price} x {k_loss:,} / ({annuity} x {c_area:.1f})) "
             f"= {a_opt:.0f} mm2"]
    rows = []
    for area in (120, 150, 185, 240, 300, 400, 500, 630):
        capital = annuity * c_area * area
        losses = price * k_loss / area
        lines.append(f"{area:4d} mm2: capital {capital:7.1f} + losses {losses:7.1f} "
                     f"= {capital + losses:7.1f} units/yr")
    for area in range(100, 701, 10):
        rows.append((str(area), f"{annuity * c_area * area:.2f}", f"{price * k_loss / area:.2f}",
                     f"{annuity * c_area * area + price * k_loss / area:.2f}"))
    csv("ch06-kelvin.csv", "area,capital,losses,total", rows)
    emit("ex_kelvin", lines)

    # ---- DC control power to a trip coil ----------------------------------------------------------
    lines = ["110 V DC system: battery at end of discharge 93.5 V, coil 5 A, needs "
             ">= 77 V, route 250 m one way, copper at 30 C (all assumed)"]
    for area in (2.5, 4.0, 6.0):
        f = dc.feeder(5.0, 250, area, "copper", 30)
        lines.append(f"{area:3.1f} mm2: loop R {f.loop_resistance_ohm:.3f} ohm, drop "
                     f"{f.drop_v:5.2f} V, coil sees {93.5 - f.drop_v:5.2f} V "
                     + ("OK" if 93.5 - f.drop_v >= 77 else "TOO LOW"))
    emit("ex_trip", lines)

    # ---- whole-plant DC loss budget -------------------------------------------------------------------
    lines = []
    g_sel = g
    pr = sc.PR_DC
    i_str_h = m.i_mp * pr * g_sel / 1000
    i_cb_h = 24 * i_str_h
    p_str_h = v_mp26 * i_str_h / 1000          # kW per string, V assumed constant
    for area_s in (4.0, 6.0):
        r_s = dc.feeder(1, 70, area_s, "copper", 50).loop_resistance_ohm
        stc = dc.power_i2r(m.i_mp, r_s)
        annual = float((r_s * i_str_h ** 2).sum()) / 1000
        lines.append(f"string cable {area_s:.0f} mm2 Cu, 70 m one way: loop {r_s:.4f} ohm; "
                     f"STC loss {stc:.1f} W = {100 * stc / (v_mp26 * m.i_mp):.2f} %; "
                     f"annual {annual:.1f} kWh = {100 * annual / p_str_h.sum():.2f} %")
    for area_f in (240, 400):
        r_f = dc.feeder(1, 180, area_f, "aluminium", 50).loop_resistance_ohm
        stc = dc.power_i2r(24 * m.i_mp, r_f)
        annual = float((r_f * i_cb_h ** 2).sum()) / 1000
        lines.append(f"feeder {area_f} mm2 Al: STC {100 * stc / (v_mp26 * 24 * m.i_mp):.2f} %; "
                     f"annual {100 * annual / (24 * p_str_h.sum()):.2f} %")
    r4 = dc.feeder(1, 70, 4.0, "copper", 50).loop_resistance_ohm
    r240 = dc.feeder(1, 180, 240, "aluminium", 50).loop_resistance_ohm
    total_stc = (100 * r4 * m.i_mp / v_mp26) + (100 * r240 * 24 * m.i_mp / v_mp26)
    ann_s = float((r4 * i_str_h ** 2).sum()) / p_str_h.sum() / 10
    ann_f = float((r240 * i_cb_h ** 2).sum()) / (24 * p_str_h.sum()) / 10
    lines.append(f"base case (4 mm2 + 240 mm2): STC {total_stc:.2f} %, annual "
                 f"{ann_s + ann_f:.2f} % of DC energy")
    lines.append(f"plant DC energy (screening): {4196 * p_str_h.sum() / 1e6:.1f} GWh/yr; "
                 f"loss {4196 * p_str_h.sum() * (ann_s + ann_f) / 100 / 1e3:.0f} MWh/yr")
    emit("ex_dcbudget", lines)

    # ---- induced voltage in a cable loop (lightning nearby, illustrative) ------------------------------
    di_dt = 30e3 / 1e-6
    lines = ["lightning current 30 kA rising in 1 us (illustrative), straight channel "
             "50 m away: dB/dt = 2e-7 x (dI/dt) / d"]
    db_dt = 2e-7 * di_dt / 50
    lines.append(f"dB/dt = {db_dt:.0f} T/s")
    for area in (10.0, 1.0, 0.1):
        lines.append(f"loop area {area:5.1f} m2: induced peak about {db_dt * area:7.0f} V")
    emit("ex_lightning", lines)

    # ---- power transferred against load resistance (figure data) -------------------------------------
    rows = []
    for rl in np.linspace(0.2, 20, 100):
        i = 6 / (2 + rl)
        rows.append((f"{rl:.2f}", f"{i * i * rl:.4f}", f"{rl / (2 + rl):.4f}"))
    csv("ch06-power-vs-load.csv", "rl,p,eta", rows)

    (EXPECTED / "examples2.txt").write_text("\n".join(ALL) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
