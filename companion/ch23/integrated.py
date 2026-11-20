"""Chapter 23 - three integrated Plant P examples: one PV block's
current by hand at every level, the auxiliary one-line in numbers, and
the electrical basis of Plant P (D-027).

Run from the project root:   python -m companion.ch23.integrated
Writes companion/ch23/expected/int_*.txt.
"""
from __future__ import annotations

import math

from companion.ch23 import sources as src
from companion.ch23.common import emit
from plantp import auxpower as ax


def by_hand() -> None:
    def a(mva, kv):
        return mva * 1e6 / (math.sqrt(3) * kv * 1e3)
    lines = ["one PV block by hand (5 MW, pf 1):",
             "  DC: 20 strings x 21 combiners = 420 strings of 26 modules",
             f"  inverter output 0.6 kV: {a(5, 0.6):,.0f} A",
             f"  block transformer 33 kV side: {a(5, 33):.1f} A",
             f"  PV feeder 1 (4 blocks) at 33 kV: {a(20, 33):.0f} A",
             f"  main transformer T2 132 kV side at 65 MW: {a(65, 132):.0f} A",
             f"  export line at 100 MW: {a(100, 132):.0f} A",
             "  the current falls 55 times from inverter to feeder and the",
             "  same conductor carries 55 x 55 = 3,025 times less loss"]
    emit("int_hand", lines)


def aux_numbers() -> None:
    p, q, s = ax.demand(src.AUX, "normal", src.DIVERSITY)
    pe, _, se = ax.demand(src.AUX, "emergency", src.DIVERSITY)
    raw, ah = ax.battery_ah(src.DC_DUTY)
    kva, kwh = ax.ups(src.UPS_KW, 0.95, src.UPS_MIN)
    lines = ["the auxiliary one-line in numbers:",
             "  two 33/0.4 kV 250 kVA station transformers (one per bus",
             "  section), LV board in two halves with a coupler; ATS to a",
             "  150 kVA standby generator for the essential half",
             f"  demand normal {s:.0f} kVA, emergency {se:.0f} kVA",
             f"  DC 110 V: 250 Ah ({ah:.0f} Ah needed), two 70 A chargers",
             f"  UPS {kva:.0f} kVA, {kwh:.0f} kWh for {src.UPS_MIN:.0f} min",
             "  battery blocks: own auxiliary transformers in the maker's",
             "  package (interface IF-006); turbines and PV inverters take",
             "  their auxiliaries from their own transformers"]
    emit("int_aux", lines)


def basis() -> None:
    lines = ["electrical basis of Plant P (D-027; PLP-ELE-DWG-0005 rev A):",
             "  levels: 0.6/0.69 kV units, 33 kV collector, 132 kV export",
             "  collector: WS1, WS2, PVF3, BESS-A on section A; WS3, PVF1,",
             "    PVF2, BESS-B on section B; coupler normally open",
             "  main transformers 2 x 63 MVA YNd11 (provisional), earthing",
             "    transformers with 400 A resistors on each 33 kV section",
             "  per-transformer limit in the PPC (each section up to 68 MVA)",
             "  export: line bay E1 with disconnector at the boundary; line",
             "    owner and meter place open (U-065); losses between the",
             "    meters 0.26 %",
             "  fault levels: 33 kV about 12.5 kA with the coupler closed",
             "    (25 kA gear), 0.4 kV board 7.9 kA",
             "  auxiliaries: 2 x 250 kVA, generator 150 kVA, DC 250 Ah, UPS",
             "    33 kVA / 60 min; load-shed and cause-and-effect matrices",
             "  open: impedances and vector groups (makers), utility data",
             "    (U-089), autonomy requirement (U-091)"]
    emit("int_basis", lines)


if __name__ == "__main__":
    by_hand()
    aux_numbers()
    basis()
