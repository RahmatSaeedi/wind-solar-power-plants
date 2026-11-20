"""Chapter 8 - the small worked examples of the lessons (lines E01, E02, ...).

Run from the project root:   python -m companion.ch08.worked
Writes companion/ch08/expected/worked.txt; the text quotes "line Enn".
Teaching values only (A-047, A-111 .. A-122); no vendor data.
"""
from __future__ import annotations

import math

from companion.ch08.common import emit
from plantp import machines as m

OUT: list[str] = []
MU0 = 4e-7 * math.pi
S3 = math.sqrt(3)


def e(eid: str, text: str, more: str = "") -> None:
    OUT.append(f"{eid}: {text}")
    if more:                              # continuation, split by hand
        OUT.append(f"     {more}")


def section_a() -> None:
    e("E01", f"100 turns, flux 0 -> 0.01 Wb in 10 ms: e = N dPhi/dt = "
             f"{100 * 0.01 / 0.010:.0f} V")
    e("E02", f"force on 0.5 m of conductor with 500 A in 0.9 T: "
             f"{0.9 * 500 * 0.5:.0f} N")
    a = 0.01
    r_air = 0.006 / (MU0 * a)
    r_fe = 1.2 / (MU0 * 2000 * a)
    e("E03", f"reluctance air {r_air:,.0f} + iron {r_fe:,.0f} = "
             f"{r_air + r_fe:,.0f} A/Wb;",
      f"200 turns: L = N^2/R = {1000 * 200 ** 2 / (r_air + r_fe):.1f} mH")
    e("E04", f"4 poles: {m.sync_speed_rpm(50, 4):.0f} rpm at 50 Hz, "
             f"{m.sync_speed_rpm(60, 4):.0f} rpm at 60 Hz")
    e("E05", f"E = 4.44 x 50 x 100 x 0.01 x 0.93 = "
             f"{m.emf_rms(50, 100, 0.01, 0.93):.0f} V")
    e("E06", f"E 1.5 pu, V 1 pu, X_s 1.2 pu, delta 30 deg: P = "
             f"{m.sm_power(1.5, 1.0, 1.2, math.radians(30)):.3f} pu, Q = "
             f"{m.sm_reactive(1.5, 1.0, 1.2, math.radians(30)):.3f} pu")
    e("E07", f"slip frequency 0.1 Hz: beat period {1 / 0.1:.0f} s;",
      f"10 deg phase error: |dV| = 2 sin(5 deg) = "
      f"{2 * math.sin(math.radians(5)):.3f} pu")
    e("E08", "induction generator 32.4 kW absorbing 20.8 kvar:",
      "a 20.8 kvar capacitor makes pf 1 at that point only")
    for v in (7.0, 10.0):
        w = 8.25 * v / 75
        e("E09", f"tip-speed ratio 8.25, R 75 m, {v:.0f} m/s: omega "
                 f"{w:.3f} rad/s = {w * 60 / (2 * math.pi):.2f} rpm")
    e("E10", f"PM machine 690 V at 1155 rpm: {690 * 600 / 1155:.0f} V and "
             f"{m.electrical_freq_hz(600, 6):.0f} Hz at 600 rpm;",
      f"{690 * 1.15:.0f} V at 15 % overspeed")
    i_r = 5.4e6 / (S3 * 690)
    e("E11", f"5.4 MVA at 690 V: {i_r:,.0f} A; per unit base current the same")
    e("E12", f"shaft 5.32 MW at 1155 rpm (A-047): torque "
             f"{m.torque_nm(5.32e6, 1155) / 1e3:.1f} kN m")


def section_b_c_d() -> None:
    e("E13", f"aluminium cage bar 1 kA, rotor slip 1 %: rotor frequency "
             f"{0.01 * 50:.1f} Hz",
      "(slow: deep-bar effects small in running)")
    e("E14", f"bearing life ratio for 10 % more load (ball, exponent 3): "
             f"{1 / 1.1 ** 3:.2f}")
    e("E15", f"first bending critical speed 1.5 x 1155 = {1.5 * 1155:.0f} rpm; "
             f"margin {100 * (1.5 - 1):.0f} %")
    u = m.residual_unbalance(3000, 2.5, 1155)
    e("E16", f"unbalance force at 1155 rpm {u['force_n']:.0f} N;",
      f"same rotor at 20 % overspeed {u['force_n'] * 1.44:.0f} N (x 1.44)")
    e("E17", f"copper winding 1.842 mohm at 18 C -> at 95 C "
             f"{m.r_at_temperature(1.842, 18, 95):.3f} mohm")
    e("E18", f"winding 2.296 mohm hot, 1.842 at 18 C: "
             f"{m.temperature_from_resistance(1.842, 18, 2.296):.1f} C")
    e("E19", f"polarisation index 2050 / 820 = {2050 / 820:.2f}")
    e("E20", f"short-circuit ratio 0.40 -> x_d about {1 / 0.40:.1f} pu")
    b = m.bearing_freqs(1155, 14, 0.040, 0.220)
    e("E21", f"BPFO {b['bpfo']:.1f} Hz = {b['bpfo'] / b['fr']:.2f} x shaft; "
             f"BPFI {b['bpfi']:.1f} Hz = {b['bpfi'] / b['fr']:.2f} x shaft")
    e("E22", f"heat for 1 kW of loss over a year: {8.76:.2f} MWh;",
      f"generator 723.8 MWh/yr = {723.8 / 8.76:.0f} kW average")
    e("E23", f"rated torque 44.0 kN m, gearbox 1:110 -> rotor "
             f"{44.0 * 110 / 1e3:.2f} MN m (losses ignored)")


if __name__ == "__main__":
    section_a()
    section_b_c_d()
    emit("worked", OUT)
