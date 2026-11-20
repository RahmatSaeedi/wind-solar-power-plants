"""Chapter 6 — the Plant P DC feeder (combiner box to inverter) and its sensitivities.

Run from the project root:   python -m companion.ch06.feeder_report
Writes companion/ch06/expected/feeder_report.txt and the plot data of the
chapter's figures (diagrams/data/ch06-*.csv).

Teaching case (all values assumed; see the chapter's assumptions table):
  one combiner box collects 24 strings of 26 PVM-550 modules; the feeder to the
  inverter is 180 m long (one way), aluminium, and the conductor is assumed to
  run at 50 C under full sun.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plantp import dc  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

N_STRINGS = 24
N_SERIES = 26
LENGTH_M = 180.0
T_COND_C = 50.0
MATERIAL = "aluminium"
AREA_MM2 = 240.0
MAX_DROP_FRACTION = 0.01     # a common design target: 1 % of operating voltage (assumed)


def main() -> None:
    m = dc.PVM_550
    v_mp_string = N_SERIES * m.v_mp
    i_mp_string = m.i_mp
    i_feeder = N_STRINGS * i_mp_string
    p_feeder_in = v_mp_string * i_feeder
    L = []
    out = L.append
    # Every printed line stays within 78 characters, so the book can quote
    # the report without wrapping.
    out("Plant P - DC feeder, combiner box to inverter (chapter 6 case)")
    out(f"string:   {N_SERIES} x PVM-550 in series")
    out(f"          V_mp = {N_SERIES} x {m.v_mp} = {v_mp_string:.1f} V, I_mp = {i_mp_string} A")
    out(f"          V_oc(25 C) = {dc.string_voc(m, N_SERIES, 25):.1f} V")
    out(f"combiner: {N_STRINGS} strings in parallel")
    out(f"          I = {N_STRINGS} x {i_mp_string} = {i_feeder:.2f} A, "
        f"P = {p_feeder_in / 1000:.1f} kW at STC")
    out(f"feeder:   {LENGTH_M:.0f} m one way, {MATERIAL}, {AREA_MM2:.0f} mm2, "
        f"conductor at {T_COND_C:.0f} C")
    r = dc.feeder(i_feeder, LENGTH_M, AREA_MM2, MATERIAL, T_COND_C, source_voltage_v=v_mp_string)
    rho = dc.resistivity_at(MATERIAL, T_COND_C)
    out(f"          rho({T_COND_C:.0f} C) = {rho:.3e} ohm m")
    out(f"          R one conductor = {r.loop_resistance_ohm / 2:.4f} ohm, "
        f"loop R = {r.loop_resistance_ohm:.4f} ohm")
    out(f"result:   drop = {r.drop_v:.2f} V = {100 * r.drop_fraction:.2f} % of V_mp")
    out(f"          loss = {r.loss_w:.0f} W = {100 * r.loss_w / p_feeder_in:.2f} % of feeder power")
    out("")
    out("sensitivity to cross-section, aluminium at 50 C")
    out("     area    drop V   drop %   loss W   loss %")
    rows_area = []
    for a in (120, 150, 185, 240, 300, 400):
        rr = dc.feeder(i_feeder, LENGTH_M, a, MATERIAL, T_COND_C, source_voltage_v=v_mp_string)
        out(f"  {a:4d} mm2  {rr.drop_v:7.2f}  {100 * rr.drop_fraction:7.2f}  "
            f"{rr.loss_w:7.0f}  {100 * rr.loss_w / p_feeder_in:7.2f}")
        rows_area.append((a, rr.drop_v, 100 * rr.drop_fraction, rr.loss_w))
    out("sensitivity to cross-section, copper at 50 C")
    out("     area    drop V   drop %   loss W   loss %")
    rows_cu = []
    for a in (120, 150, 185, 240, 300, 400):
        rr = dc.feeder(i_feeder, LENGTH_M, a, "copper", T_COND_C, source_voltage_v=v_mp_string)
        out(f"  {a:4d} mm2  {rr.drop_v:7.2f}  {100 * rr.drop_fraction:7.2f}  "
            f"{rr.loss_w:7.0f}  {100 * rr.loss_w / p_feeder_in:7.2f}")
        rows_cu.append((a, rr.drop_v, 100 * rr.drop_fraction, rr.loss_w))
    out("sensitivity to conductor temperature, aluminium 240 mm2")
    for t in (20, 50, 70, 90):
        rr = dc.feeder(i_feeder, LENGTH_M, AREA_MM2, MATERIAL, t, source_voltage_v=v_mp_string)
        out(f"  {t:3d} C: loop R {rr.loop_resistance_ohm:.4f} ohm, "
            f"drop {rr.drop_v:.2f} V, loss {rr.loss_w:.0f} W")
    need = dc.area_for_drop(i_feeder, LENGTH_M, MAX_DROP_FRACTION * v_mp_string, MATERIAL, T_COND_C)
    out(f"smallest aluminium section for {100 * MAX_DROP_FRACTION:.0f} % drop: {need:.0f} mm2 "
        f"-> standard {dc.next_standard_area(need):.0f} mm2")
    out("")
    out("string voltage window (PVM-550, 26 in series, 1500 V system):")
    for t in (-20, -10, 0, 25, 45, 65, 75):
        out(f"  cell {t:4d} C: V_oc = {dc.string_voc(m, N_SERIES, t):7.1f} V")
    for n in (26, 27, 28, 29):
        out(f"  {n} modules at -10 C: V_oc = {dc.string_voc(m, n, -10):7.1f} V"
            + ("   EXCEEDS 1500 V" if dc.string_voc(m, n, -10) > 1500 else ""))
    out("string short-circuit current (26 modules):")
    for g in (200, 600, 1000, 1200):
        out(f"  G = {g:4d} W/m2, 25 C: I_sc = {dc.string_isc(m, g, 25):6.2f} A "
            f"(I_mp at STC = {m.i_mp} A)")
    out("")
    out(f"fault in a string: I_sc is only {100 * (m.i_sc / m.i_mp - 1):.1f} % above "
        "the operating current,")
    out("so a fuse cannot tell a fault in the string from normal operation;")
    out("it protects against current fed from the OTHER strings (chapter 24).")

    text = "\n".join(L) + "\n"
    (HERE / "expected").mkdir(exist_ok=True)
    (HERE / "expected" / "feeder_report.txt").write_text(text, encoding="utf-8", newline="\n")
    print(text)

    # ---- plot data --------------------------------------------------------
    data = ROOT / "diagrams" / "data"
    data.mkdir(parents=True, exist_ok=True)
    with open(data / "ch06-drop-vs-area.csv", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("area_mm2,drop_pct_al,drop_pct_cu,loss_w_al,loss_w_cu\n")
        for (a, _, dal, lal), (_, _, dcu, lcu) in zip(rows_area, rows_cu):
            fh.write(f"{a},{dal:.3f},{dcu:.3f},{lal:.1f},{lcu:.1f}\n")
    with open(data / "ch06-resistance-vs-temperature.csv", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("temp_c,r_rel_cu,r_rel_al\n")
        for t in range(-40, 121, 10):
            fh.write(f"{t},{dc.resistivity_at('copper', t) / dc.RESISTIVITY_20C['copper']:.4f},"
                     f"{dc.resistivity_at('aluminium', t) / dc.RESISTIVITY_20C['aluminium']:.4f}\n")
    with open(data / "ch06-loss-vs-current.csv", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("current_a,loss_w\n")
        r_loop = dc.feeder(1.0, LENGTH_M, AREA_MM2, MATERIAL, T_COND_C).loop_resistance_ohm
        for i in range(0, 361, 20):
            fh.write(f"{i},{dc.power_i2r(i, r_loop):.1f}\n")
    v = np.linspace(0, dc.string_voc(m, N_SERIES, -10), 300)
    with open(data / "ch06-string-iv.csv", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("v,i_1000_25,i_1000_65,i_500_25,p_1000_25\n")
        i_a = dc.pv_iv_curve(m, N_SERIES, v, 1000, 25)
        i_b = dc.pv_iv_curve(m, N_SERIES, v, 1000, 65)
        i_c = dc.pv_iv_curve(m, N_SERIES, v, 500, 25)
        for vv, a, b, c in zip(v, i_a, i_b, i_c):
            fh.write(f"{vv:.1f},{a:.3f},{b:.3f},{c:.3f},{vv * a / 1000:.3f}\n")
    with open(data / "ch06-source-vi.csv", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("i,v_ideal,v_real\n")
        for i in np.linspace(0, 10, 21):
            fh.write(f"{i:.1f},12.0,{12.0 - 0.4 * i:.2f}\n")


if __name__ == "__main__":
    main()
