"""Chapter 27 - expansion round 8: what a reactive-power service earns
against the losses it causes, the voltage difference between the plant's
132 kV bus and the POC (where the controller measures), and power-factor
signs under the generator convention (D-010).

Run from the project root:   python -m companion.ch27.examples_w
Writes companion/ch27/expected/w_*.txt. Teaching prices and values.
"""
from __future__ import annotations

import math

from companion.ch27.common import emit
from plantp import ac


def service_value() -> None:
    price_mvarh, energy_price = 0.6, 70.0              # teaching u per Mvar-h, u per MWh
    r_line = 0.12 * 7.06
    lines = ["a reactive-power service at full export: payment against extra losses",
             "  (teaching: 0.6 u per Mvar-h paid; losses valued at 70 u/MWh; line only)",
             "  pf     Q Mvar   paid u/h   extra line loss kW   loss cost u/h   net u/h"]
    i1 = ac.line_current_a(100e6, 132e3, 1.0)
    for pf in (0.98, 0.95, 0.90):
        q = 100 * math.tan(math.acos(pf))
        i = ac.line_current_a(100e6, 132e3, pf)
        dl = 3 * (i * i - i1 * i1) * r_line / 1e3
        paid = q * price_mvarh
        cost = dl / 1e3 * energy_price
        lines.append(f"  {pf:4.2f}   {q:6.1f}   {paid:8.1f}   {dl:18.0f}   {cost:13.1f}   {paid - cost:7.1f}")
    lines += ["  the line loss alone eats a little of the payment; the",
              "  transformers' and cables' extra losses (ch 25) and the",
              "  curtailment on a hot day (lesson B) eat more - a service",
              "  price is judged against the plant's whole cost of",
              "  providing it (ch 21), not the line alone"]
    emit("w_value", lines)


def control_point() -> None:
    z_base = 132 ** 2 / 100
    r = 0.12 * 7.06 / z_base
    x = 0.40 * 7.06 / z_base
    lines = ["voltage at the plant's 132 kV bus against the POC (100 MW, 7.06 km line)",
             "  Q at the POC Mvar   bus above POC %",
             ]
    for q in (-33, 0, 33):
        du = (1.0 * r + q / 100 * x) * 100
        lines.append(f"  {q:17d}   {du:16.2f}")
    lines += ["  the controller that measures at the plant bus sees a",
              "  voltage up to a per cent away from the POC's: the voltage",
              "  set-point is either measured at the POC (remote signal)",
              "  or corrected for the line (line-drop compensation) - the",
              "  requirement is at the POC, wherever the controller reads",
              "  (lesson E, location)"]
    emit("w_control", lines)


def pf_signs() -> None:
    cases = [(80.0, 20.0), (80.0, -20.0), (-15.0, 5.0), (-15.0, -5.0)]
    lines = ["power factor and its sign under the generator convention (D-010:",
             "  P > 0 export; Q > 0 the plant supplies reactive power)",
             "  P MW    Q Mvar   pf      plant is            usual name"]
    names = {(True, True): "lagging (overexcited)", (True, False): "leading (underexcited)",
             (False, True): "leading load", (False, False): "lagging load"}
    for p, q in cases:
        pf = abs(p) / math.hypot(p, q)
        mode = ("exporting" if p > 0 else "importing") + (", giving Q" if q > 0 else ", taking Q")
        lines.append(f"  {p:5.0f}   {q:6.0f}   {pf:5.3f}   {mode:19s} {names[(p > 0, q > 0)]}")
    lines += ["  the same plant giving reactive power is 'lagging' as a",
              "  generator and a 'leading load' when it imports (charging):",
              "  the words change with the side and the convention - a",
              "  report states P and Q with their signs and the convention,",
              "  never 'pf 0.97' alone"]
    emit("w_signs", lines)


if __name__ == "__main__":
    service_value()
    control_point()
    pf_signs()
