"""Chapter 9 - small worked calculations, one line each (E01 ...), used by
the text and the self-checks.

Run from the project root:   python -m companion.ch09.worked
Writes companion/ch09/expected/worked.txt.
"""
from __future__ import annotations

import math

from companion.ch09.common import emit
from plantp import pe

S2, S3 = math.sqrt(2), math.sqrt(3)
OUT: list[str] = []


def e(eid: str, text: str, more: str = "") -> None:
    OUT.append(f"{eid}: {text}")
    if more:
        OUT.append(f"     {more}")


def lines() -> None:
    e("E01", f"10 mF at 1000 V: {pe.capacitor_energy_j(0.01, 1000) / 1e3:.1f} kJ")
    e("E02", f"5.5 MVA at 600 V: {5.5e6 / (S3 * 600):,.0f} A; at 690 V: "
             f"{5.5e6 / (S3 * 690):,.0f} A")
    e("E03", f"phase peak of 690 V line-to-line: {690 * S2 / S3:.0f} V")
    e("E04", f"buck 800 V, duty 0.3: mean {0.3 * 800:.0f} V")
    e("E05", f"boost from 500 V with duty 0.5: {500 / (1 - 0.5):.0f} V")
    e("E06", f"diode bridge on 690 V: {pe.rectifier_6p_vdc(690):.1f} V")
    e("E07", f"bridge on 800 V, m 0.9: line voltage "
             f"{0.9 * 800 * S3 / (2 * S2):.1f} V RMS")
    e("E08", f"SVPWM minimum DC for 400 V: {pe.vdc_min(400):.0f} V; "
             f"for 600 V: {pe.vdc_min(600):.0f} V")
    e("E09", f"carrier 3 kHz at 50 Hz: m_f = {3000 / 50:.0f}")
    e("E10", f"IGBT 0.9 V + 0.5 mohm at 1000 A: drop "
             f"{0.9 + 0.5e-3 * 1000:.2f} V")
    e("E11", f"junction: 45 C + 1 kW x 0.05 K/W = {45 + 1000 * 0.05:.0f} C")
    e("E12", f"cycle life, swing 20 -> 30 K, n 5: x "
             f"{pe.relative_cycle_life(30, 20):.3f}")
    e("E13", f"loss peak where c0 = c2 p^2: p = sqrt(2.75 / 11.54) = "
             f"{math.sqrt(2.75 / 11.54):.2f}")
    e("E14", f"derating at 44 C and 800 m: {float(pe.derating(44, 800)):.2f} pu")
    e("E15", f"inductance for the same ripple at 3 x f: x {1 / 3:.3f}")
    e("E16", f"capacitor ripple at m 0.8, pf 1: "
             f"{pe.dclink_ripple_current_rms(1.0, 0.8, 1.0):.3f} of phase "
             "current")
    e("E17", f"overshoot 40 nH x 8 kA/us: {pe.overshoot_v(40e-9, 8e9):.0f} V")
    e("E18", f"dead-time error at twice the frequency: x 2 "
             f"({2 * pe.deadtime_error(500, 3e-6, 3000):.1f} V)")
    e("E19", f"glycol for 81 kW at 8 K: {81e3 / (3600 * 8):.2f} kg/s")
    e("E20", f"SCR at 1000 MVA, 100 MW: {1000 / 100:.0f}")
    iq, ip = pe.frt_currents(0.6)
    e("E21", f"V 0.6 pu, k 2, limit 1.1: I_q {iq:.2f}, I_p {ip:.3f} pu")
    e("E22", f"droop 5 %, dead band 0.2 Hz, 50.7 Hz: reduce by "
             f"{100 * (0.5 / 50) / 0.05:.0f} %")
    e("E23", f"availability with 0.5/yr and 48 h: "
             f"{1 / (1 + 0.5 * 48 / 8760):.5f}")
    e("E24", f"first-pass yield of seven 0.99 stages: {0.99 ** 7:.3f}")


if __name__ == "__main__":
    lines()
    emit("worked", OUT)
