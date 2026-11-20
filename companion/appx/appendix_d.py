"""Appendix D - a filled calculation sheet with an independent check: the
voltage drop of one 33 kV collector feeder computed by the chapter 24
approximation and checked by an exact phasor solution, with a units check
and a reasonableness range. Teaching values, stated in the sheet.

Run from the project root:   python -m companion.appx.appendix_d
Writes companion/appx/expected/appd_sheet.txt.
"""
from __future__ import annotations

import cmath
import math

from companion.appx.common import emit

# inputs (teaching values; status in the sheet)
P_MW = 20.0          # four 5 MW turbines at full output
PF = 0.95            # lagging, at the receiving end
U_KV = 33.0          # nominal line-to-line
L_KM = 6.0           # route length
R_KM = 0.100         # ohm/km, 400 mm2 Al at 90 C (teaching)
X_KM = 0.110         # ohm/km (teaching)


def method_a() -> float:
    """Chapter 24 approximation: dU = sqrt(3) I L (R cos phi + X sin phi)."""
    i = P_MW * 1e6 / (math.sqrt(3) * U_KV * 1e3 * PF)
    phi = math.acos(PF)
    du = math.sqrt(3) * i * L_KM * (R_KM * math.cos(phi) + X_KM * math.sin(phi))
    return du / (U_KV * 1e3) * 100


def method_b() -> float:
    """Exact per-phase phasor: Vs = Vr + I Z, with Vr fixed at nominal."""
    vr = U_KV * 1e3 / math.sqrt(3)
    i_mag = P_MW * 1e6 / (3 * vr * PF)
    i = cmath.rect(i_mag, -math.acos(PF))
    z = complex(R_KM * L_KM, X_KM * L_KM)
    vs = vr + i * z
    return (abs(vs) - vr) / vr * 100


def main() -> None:
    a, b = method_a(), method_b()
    i = P_MW * 1e6 / (math.sqrt(3) * U_KV * 1e3 * PF)
    diff = abs(a - b) / b * 100
    lines = ["CALCULATION SHEET (teaching example)",
             "  title:     voltage difference along collector feeder WS-x at full",
             "             output (turbine end above the 33 kV bus)",
             "  inputs:    P 20 MW (four 5 MW units, design value)",
             "             pf 0.95 at the bus, units exporting Q (assumed)",
             "             U 33 kV nominal (verified, one-line)",
             "             L 6.0 km (route drawing, project-dependent)",
             "             R 0.100, X 0.110 ohm/km at 90 C (maker's data, assumed)",
             f"  current:   I = P / (sqrt3 U pf) = {i:.1f} A",
             f"  method A:  chapter 24 approximation      dU = {a:.3f} %",
             f"  method B:  exact phasor, bus at 33 kV     dU = {b:.3f} %",
             f"  agreement: {diff:.2f} % apart (approximation drops the",
             "             quadrature term; acceptable below 1 %)",
             "  units:     A x km x ohm/km = V; V / V = 1 (checked)",
             "  range:     a few per cent on a 33 kV feeder of a few km is",
             "             normal; above 5 % would call for a larger cable",
             f"  result:    dU = {b:.2f} % at full output (within a 3 % design",
             "             limit - the limit is the project's, not universal)",
             "  checker:   independent method, units and range - signed"]
    emit("appd_sheet", lines)


if __name__ == "__main__":
    main()
