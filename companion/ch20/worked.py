"""Chapter 20 - numerical answers of the small examples (E..) and of the
end-of-chapter problems (P..), each computed here so that the answer key
matches the code.

Run from the project root:   python -m companion.ch20.worked
Writes companion/ch20/expected/worked.txt and solutions.txt.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch20.common import emit
from plantp import control as ct

ETA = math.sqrt(0.86)


def loop(kp, ki, tau):
    wn = math.sqrt(ki / tau)
    z = (1 + kp) / (2 * math.sqrt(tau * ki))
    return wn, z


def worked() -> None:
    wn, z = loop(1.0, 0.5, 2.0)
    lines = [f"E01 kp 1, ki 0.5, tau 2 s: wn {wn:.2f} rad/s, zeta {z:.2f}",
             f"E02 5 % droop on 60 MW at 50.2 Hz: {float(ct.droop_power(0.2, 60, 0.05)):+.1f} MW",
             f"E03 Q limit of 5.5 MVA at 5 MW, cap 0.33: {float(ct.q_limit(5.0, 5.5, 0.33)):.2f} Mvar",
             f"E04 floor for 10 MW x 0.5 h: {4 + 10 * 0.5 / ETA:.2f} MWh",
             f"E05 curtailment 96 - 80 = 16 MW; wind share of 60/36: {16 * 60 / 96:.1f} MW",
             f"E06 penalty schedule 50, delivery 44: {ct.imbalance([50], [44], 30, 10):.0f} u",
             f"E07 three units 5 MW, 1 Hz droop, 3 MW load: f = {50 - 3 / 15:.2f} Hz",
             f"E08 slip 0.2 Hz, window +-15 deg: {1 / 0.2 * 30 / 360:.3f} s in window",
             f"E09 battery 5 MW discharging, 5.5 MVA: Q up to "
             f"{math.sqrt(5.5 ** 2 - 25):.2f} Mvar",
             f"E10 ramp 3 MW/min, drop of 12 MW: battery {12 - 3:.0f} MW in minute 1"]
    emit("worked", lines)


def solutions() -> None:
    out = []
    for i, (kp, ki) in enumerate([(0.5, 0.2), (1.5, 0.8), (6, 8), (3, 2)], 1):
        wn, z = loop(kp, ki, 2.0)
        out.append(f"P{i:02d} kp {kp}, ki {ki}, tau 2: wn {wn:.2f}, zeta {z:.2f}")
    # P05 gains for critical damping with wn = 1 rad/s and tau 2 s
    ki = 2.0
    kp = 2 * math.sqrt(2.0 * ki) - 1
    out.append(f"P05 wn 1 rad/s, zeta 1, tau 2: ki {ki:.1f}, kp {kp:.2f}")
    for i, f in enumerate([49.95, 49.8, 50.25], 6):
        out.append(f"P{i:02d} {f} Hz, 4 % droop, 0.02 Hz db, 110 MW: "
                   f"{float(ct.droop_power(f - 50, 110, 0.04, 0.02)):+.2f} MW")
    for i, v in enumerate([0.99, 1.02, 1.06], 9):
        out.append(f"P{i:02d} V {v} pu, slope 4 %, 33 Mvar: "
                   f"{float(ct.droop_reactive(v - 1, 33, 0.04)):+.1f} Mvar")
    for i, p in enumerate([0.0, 4.0, 5.3], 12):
        out.append(f"P{i:02d} Q limit 5.6 MVA at {p} MW, cap 0.33: "
                   f"{float(ct.q_limit(p, 5.6, 0.33)):.2f} Mvar")
    for i, e in enumerate([6.0, 18.0, 33.0], 15):
        up, dn = ct.soc_room(e, 4, 36, ETA, 1.0)
        out.append(f"P{i:02d} E {e} MWh, 1 h: up {min(up, 20):.1f}, down {min(dn, 20):.1f} MW")
    out.append(f"P18 band for 8 MW up and 6 MW down 1 h: "
               f"{4 + 8 / ETA:.2f} to {36 - 6 * ETA:.2f} MWh")
    out.append(f"P19 floor 15 MW x 2 h: {4 + 30 / ETA:.1f} MWh > 36: infeasible")
    rev, _, _ = ct.dp_schedule(np.array([20, 60, 20, 60.]), [10] * 4, [10] * 4,
                               10, 0, 10, 0, 1.0, 1.0)
    out.append(f"P20 DP 10 MW / 10 MWh, prices 20 60 20 60, eta 1: {rev:.0f} u")
    rev2, _, _ = ct.dp_schedule(np.array([20, 60, 20, 60.]), [10] * 4, [10] * 4,
                                10, 0, 10, 0, 1.0, 1.0, wear=45.0)
    out.append(f"P21 same with wear 45 u/MWh: {rev2:.0f} u")
    out.append(f"P22 newsvendor short 40 long 10: q* {10 / 50:.2f}; "
               f"short 20 long 20: {20 / 40:.2f}")
    out.append(f"P23 penalty S 60/60/60, A 50/65/58: "
               f"{ct.imbalance([60, 60, 60], [50, 65, 58], 30, 10):.0f} u")
    f = (5 * 50.2 + 15 * 50 - 6) / 20
    out.append(f"P24 4 units, one set 50.2 Hz, load 6 MW: f {f:.3f} Hz, "
               f"P1 {5 * (50.2 - f):.2f}, others {5 * (50 - f):.2f} MW")
    out.append(f"P25 secondary shift to restore 50 Hz at 6 MW, equal: "
               f"{6 / 20:.2f} Hz")
    for i, s in enumerate([0.05, 0.3], 26):
        out.append(f"P{i:02d} slip {s} Hz, +-10 deg: in window {1 / s * 20 / 360:.2f} s,"
                   f" worst wait {1 / s * (1 - 20 / 360):.1f} s")
    out.append(f"P28 delta 5 MW, 4 h, 365 d, at 50 u: up to {5 * 4 * 365 * 50 / 1000:.0f} k u")
    out.append(f"P29 cost per MW-h: 57.7 k / 7,300 = {57.7e3 / 7300:.2f};"
               f" 211.9 k / 14,600 = {211.9e3 / 14600:.2f} u")
    out.append(f"P30 black start 1.47 MW for 8 h: {1.472 * 8:.1f} MWh of 32")
    out.append(f"P31 ramp limit energy 2 MW/min, 20 MW step down: battery "
               f"{sum(20 - 2 * k for k in range(1, 10)) / 60:.2f} MWh")
    loss = 0.5 * 160
    out.append(f"P32 cap margin 0.5 MW x 160 h: {loss:.0f} MWh")
    out.append(f"P33 Q asked at pf 0.95 for 90 MW: {90 * math.tan(math.acos(0.95)):.1f} Mvar")
    out.append("P34 hold 1 h, then fallback: a 3 h outage idles the battery 2 h")
    e = 6.4 + 20 * ETA
    out.append(f"P35 hour 11 by hand: export 80, curtail 5.2, E after {e:.1f} MWh")
    out.append(f"P36 alarms ratio controller/plan 1,147/104 = {1147 / 104:.1f}")
    out.append(f"P37 imbalance cut by intraday (1,245-919)/1,245 = "
               f"{(1245 - 919) / 1245 * 100:.0f} %")
    out.append(f"P38 day-ahead penalty share of export revenue 1,245/13,781 = "
               f"{1245 / 13781 * 100:.1f} %")
    out.append(f"P39 7 states, 15 transitions, 2 cases each: {2 * 15} cases")
    out.append(f"P40 evening P95 48 MWh vs window 32 x 0.927 = {32 * ETA:.1f} MWh")
    for i, r in enumerate([9, 4, 1.5], 41):
        z = 0.5 * math.sqrt(r)
        os_ = 100 * math.exp(-math.pi * z / math.sqrt(1 - z * z)) if z < 1 else 0.0
        out.append(f"P{i:02d} cascade ratio {r}: zeta {z:.2f}, overshoot {os_:.1f} %")
    out.append(f"P44 inner 0.5 s: outer >= {4 * 0.5:.1f} s for no overshoot")
    dv = 0.03 * 0.8 + 0.15 * (-0.1)
    out.append(f"P45 dV = 0.03 x 0.8 + 0.15 x (-0.1) = {dv:.3f} pu")
    out.append(f"P46 droop factor X 0.2, Qmax 0.33, s 0.04: {1 / (1 + 0.2 * 0.33 / 0.04):.2f}")
    z = 1 / 4
    x, r = z * 3 / math.sqrt(10), z / math.sqrt(10)
    out.append(f"P47 SCR 4, X/R 3, 100 MW: dV {r * 100:.2f} %, Q for 0: {-r / x * 100:.1f} Mvar")
    out.append(f"P48 single PPC MTBF 20,000 h, MTTR 48 h: "
               f"{8760 / 20000 * 48:.1f} h a year in fallback")
    out.append(f"P49 delay budget 315 ms + 2 s polling (avg 1,000): {315 + 1000} ms")
    out.append(f"P50 island floor 10 MWh, 1.57 MW: battery alone "
               f"{(10 - 4) * ETA / 1.57:.1f} h")
    out.append(f"P51 end target cost per MWh above floor: 30.6/6 = {30.6 / 6:.1f}, "
               f"87.8/16 = {87.8 / 16:.1f} k u")
    out.append(f"P52 alarms 756 + 391 = {756 + 391}; plan 34 + 70 = {34 + 70}")
    out.append(f"P53 sampling: ZOH delay ~ ts/2: ts 0.5 s -> {0.25:.2f} s")
    fr = 100 / 110
    caps = (12 * float(ct.q_limit(fr * 5, 5.6, 0.33)),
            10 * float(ct.q_limit(fr * 5, 5.5, 0.33)),
            4 * float(ct.q_limit(0, 5.5, 1.0)))
    out.append(f"P54 Q caps at 100 MW {caps[0]:.1f}/{caps[1]:.1f}/{caps[2]:.1f};"
               f" ask 30: WTG {30 * caps[0] / sum(caps):.1f} Mvar")
    out.append(f"P55 pf 0.95 at 85 MW: {85 * math.tan(math.acos(0.95)):.1f} Mvar asked")
    emit("solutions", out)


if __name__ == "__main__":
    worked()
    solutions()
