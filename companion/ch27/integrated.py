"""Chapter 27 - three integrated Plant P examples: power factor and
resonance by hand, the permanent power-quality monitoring plan, and the
power-quality and service basis (D-031).

Run from the project root:   python -m companion.ch27.integrated
Writes companion/ch27/expected/int_*.txt.
"""
from __future__ import annotations

import math

from companion.ch27.common import emit
from plantp import ac


def by_hand() -> None:
    i = 100e6 / (math.sqrt(3) * 132e3 * 0.95)
    lines = ["by hand: current at pf 0.95 and a resonance order",
             f"  I = 100 MW / (sqrt3 x 132 kV x 0.95) = {i:.0f} A",
             f"  h = sqrt(365 MVA / 6.77 Mvar) = {math.sqrt(365 / 6.77):.2f}",
             f"  code: {ac.line_current_a(100e6, 132e3, 0.95):.0f} A and"
             f" {ac.resonance_order(365, 6.77):.2f}"]
    emit("int_hand", lines)


def monitoring() -> None:
    rows = [("POC", "class A, V and I harmonics, flicker, unbalance, events", "permanent"),
            ("33 kV bus A and B", "V and I harmonics, events", "permanent"),
            ("filter (if fitted)", "branch currents, capacitor unbalance", "permanent"),
            ("each unit type", "I harmonics against power (sample)", "yearly, 2 weeks"),
            ("service tests", "steps, droop, P-Q points", "after any change")]
    lines = ["Plant P power-quality monitoring plan (teaching):"]
    for a, b, c in rows:
        lines += [f"  {a}: {b}", f"      when: {c}"]
    lines += ["  one time source; 10-minute and event data kept 5 years;",
              "  weekly 95th percentiles reported to the operator if asked;",
              "  firmware or setting changes trigger a repeat of the",
              "  affected service tests"]
    emit("int_monitoring", lines)


def basis() -> None:
    lines = ["power-quality and service basis of Plant P (D-031):",
             "  emission: assessed at the POC against the operator's",
             "    allocation; screening by in-phase summation, then measured",
             "  resonance: no plain capacitor bank on the 33 kV; if Mvar or",
             "    filtering is needed, a filter tuned near the 4.7th with",
             "    unbalance protection; frequency scan in the grid study",
             "  reactive power: from the units, checked at the POC with the",
             "    losses between; hot, still days read with the line rating",
             "  services: acceptance matrix with metric, place, method and",
             "    record for each claim; telemetry gaps counted by length",
             "  investigation: workflow with records; comparisons within",
             "    fixed hours; currents and on/off tests before conclusions",
             "  later findings: the 33 kV resonance moves with the units",
             "    online (11th with ~8, 13th with ~3): scans and remedies",
             "    are judged at the worst unit count and order; the filter",
             "    seen from 132 kV resonates near 4.3 - the network's",
             "    ripple-signal frequencies go into its design data; the",
             "    reactor tap is set on site after the capacitors are",
             "    measured; Q capability is checked at 0.9 pu (43 Mvar,",
             "    not 68); the voltage controller reads the POC or",
             "    compensates the line; a whole-plant trip while giving",
             "    33 Mvar is a 3 % step at the POC; HVAC drives need",
             "    chokes or active front ends on the 400 V board",
             "  open: the operator's emission allocation (U-100), the",
             "    background harmonic levels at the POC (U-101)"]
    emit("int_basis", lines)


if __name__ == "__main__":
    by_hand()
    monitoring()
    basis()
