"""Chapter 28 - three integrated Plant P examples: a load-flow result
checked by hand, the study plan by project stage with the inputs each
stage needs, and the grid-study basis (D-032).

Run from the project root:   python -m companion.ch28.integrated
Writes companion/ch28/expected/int_*.txt.
"""
from __future__ import annotations

import math

from companion.ch28 import register as reg
from companion.ch28 import sources as src
from companion.ch28.common import emit
from plantp import gridstudy as gs


def by_hand() -> None:
    z = gs.thevenin(src.GRID["max"]["s_sc"], src.GRID["max"]["xr"])
    du_hand = 1.0 * z.real                      # P = 1 pu (100 MW), Q = 0
    lf = src.q_for_target({"wind": 1.0, "pv": 0.84}, 0.0)[1]
    ik_hand = 1.1 * 1500 / (math.sqrt(3) * 132)
    lines = ["two study results checked by hand (grid max)",
             f"  POC voltage rise for 100 MW at Q = 0: (P R + Q X) = 1.0 x {z.real:.5f}"
             f" = {100 * du_hand:.2f} %",
             f"  load flow: POC at {lf['v'][1]:.4f} pu with the source at 1.0000"
             f" ({lf['s_poc'].real:.1f} MW)",
             f"  POC fault current: 1.1 x 1500 / (1.732 x 132) = {ik_hand:.2f} kA;"
             " study 7.21",
             "  the hand value is a little higher than the load flow: the",
             "  linear formula drops the second-order term (P X)^2 / 2,",
             "  which lowers the voltage - close enough to trust both"]
    emit("int_hand", lines)


def stages() -> None:
    plan = [("feasibility", "B cases and short-circuit screening",
             ["IN-01", "IN-02", "IN-04", "IN-12", "IN-16"]),
            ("application", "B, C (RMS) and G with the operator's cases",
             ["IN-01", "IN-02", "IN-03", "IN-04", "IN-05", "IN-06", "IN-10", "IN-13",
              "IN-15", "IN-16", "IN-18", "IN-19", "IN-20", "IN-22", "IN-23"]),
            ("detailed design", "E (EMT), protection settings, PQ (ch 27)",
             ["IN-03", "IN-07", "IN-08", "IN-09", "IN-11", "IN-21", "IN-24", "IN-26"]),
            ("before energising", "models checked against FAT and type tests",
             ["IN-14", "IN-20", "IN-22", "IN-23"]),
            ("commissioning", "tests, measured line, validated models",
             ["IN-17", "IN-27", "IN-28"])]
    status = {i[0]: i[3] for i in reg.INPUTS}
    lines = ["the study plan by project stage and the inputs each stage needs",
             "  stage               studies                                     have/need"]
    for stage, studies, need in plan:
        have = sum(status[i] == "received" for i in need)
        lines.append(f"  {stage:18s}  {studies:43s} {have:4d}/{len(need)}")
    lines += ["  each stage's studies use only what that stage can know;",
              "  a later stage reruns them with better data - the input",
              "  register shows which stage is ready to start"]
    emit("int_stages", lines)


def basis() -> None:
    lines = ["grid-study basis of Plant P (D-032):",
             "  model: rev C from the POC to aggregated units, grid max and",
             "    min (1,500 / 900 MVA), taps holding the 33 kV bus, the",
             "    controller holding Q = 0 at the POC unless asked",
             "  capability: +46/-63 Mvar at full output (25 C); +33 Mvar is",
             "    NOT met on a 45 C day (29 Mvar): battery share (S1), a",
             "    capacitor bank or a written limit - an operator decision",
             "  losses: the study's curve replaces model 15.1's (4.4 against",
             "    3.3 GWh a year) in the next energy model",
             "  faults: within 31.5 kA (132 kV) and 25 kA (33 kV); the line",
             "    needs a differential scheme or an intertrip at its plant end",
             "  dynamics: ride-through with k = 2 above the teaching envelope;",
             "    voltage-controller gains studied at minimum strength;",
             "    frequency support only by reducing (no headroom in S0)",
             "  islanding: passive relays blind ~1,760 h a year - intertrip",
             "  weak grid: WSCR 3.5-5.8 with the neighbours - EMT study",
             "  models: 5 of 8 need action before submission (versions)",
             "  export: the line's rating did not bind in the data year;",
             "    the line's planned day is the largest N-1 exposure (810",
             "    MWh/yr at random, 76 on a calm day); faults 17 as ch 18",
             "  later findings: voltage-stability limit about twice the",
             "    plant's size; earthed stars carry ~3 kA of network earth",
             "    faults; intertrip within 0.15 s on a supervised channel",
             "    (~2 h/yr residual); export set-point 98-99 MW for gusts;",
             "    harmonic study on the operator's locus, not one point;",
             "    the radial line kept against a tee and 33 kV (recorded)",
             "  open: the code and its values (U-102); the operator's",
             "    network model, minimum strength and neighbours (U-103)"]
    emit("int_basis", lines)


if __name__ == "__main__":
    by_hand()
    stages()
    basis()
