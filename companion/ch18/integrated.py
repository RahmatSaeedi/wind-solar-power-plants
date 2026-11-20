"""Chapter 18 - three integrated Plant P examples: checking the main
ratings against the capacities (introductory), the water-service basis
(intermediate), and the architecture basis that feeds chapters 19-28
(integrated).

Run from the project root:   python -m companion.ch18.integrated
Writes companion/ch18/expected/i_*.txt.
"""
from __future__ import annotations

import numpy as np

from companion.ch15 import sources as s15
from companion.ch18 import examples_g as eg, sources as src
from companion.ch18.common import emit
from plantp import architecture as ar


def ratings() -> None:
    r = s15.plant_year()
    mv_peak = float(r["mv"].max())
    s_need = 110.0 / 0.95
    lines = ["main ratings against the capacities (S1, teaching):",
             f"  peak at the 33 kV bus in the model year: {mv_peak:.1f} MW",
             f"  wind 60 + PV 50 MW at pf 0.95: {s_need:.1f} MVA against 2 x 63 ="
             " 126 MVA (ok)",
             f"  one transformer out: {63 * 0.95:.1f} MW can still be exported",
             f"  hours above that in the model year: {int((r['poc'] > 59.85).sum()):,d}",
             "  collector string of 4 turbines at 33 kV:"
             f" {float(ar.current_ka(20, 33, 0.95)):.3f} kA (240 mm2 rated 0.41)",
             "  battery 20 MW on its own bays: the export limit, not the",
             "  transformers, caps wind + PV + battery at the POC",
             "  ratings come from suppliers; these checks only screen them"]
    emit("i_ratings", lines)


def water_basis() -> None:
    lines = ["water-service basis (teaching, A-286; PLP-MEC-REP-0002):",
             "  uses: PV cleaning (truck, ch 15 trigger), sanitation for",
             "    25 staff, battery chiller make-up; construction separate",
             "  operating demand 2,804 m3 a year, peak month 433 m3",
             "  source: licensed well 1,500 m3 a month (U-053 open);",
             "    the spring only as a back-up outside Jun-Sep",
             "  storage: 2,500 m3 = 1,600 m3 usable + 900 m3 held reserve",
             "    (placeholder for the fire authority, chapter 32)",
             "  quality: cleaning water to the module maker's limits,",
             "    drinking water treated and kept separate",
             "  priority when short: reserve untouched, then drinking and",
             "    sanitation, then battery cooling, then cleaning",
             "  metering: well, tank outlet, each use; monthly report"]
    emit("i_water", lines)


def basis() -> None:
    reg = src.interfaces()
    bad = sum(1 for i in reg if i.mismatch())
    pairs = len(eg.LINKS)
    lines = ["architecture basis of Plant P (D-022; PLP-ELE-REP-0005):",
             "  mode: grid-connected, grid-following; island only for",
             "    the plant's critical loads behind a transfer switch",
             "  capacities: wind 60 MW (12 x 5), PV 60.06 MWp / 50 MW AC,",
             "    battery S1 20 MW / 40 MWh AC-coupled, export 100 MW",
             "  collector: 33 kV, 3 radial wind strings, 3 PV feeders,",
             "    battery on its own bays; split 33 kV bus",
             "  reactive power: units plus battery inverters (margin 3 Mvar)",
             "    or a compensator, after the grid code (U-067)",
             "  substation: two 63 MVA 33/132 kV transformers",
             "  export: single-circuit 132 kV overhead line, 7.06 km",
             f"  interfaces: {pairs} system pairs; {len(reg)} detailed items in the",
             f"    register (PLP-GEN-REG-0004), {bad} mismatches to close",
             "  water: well, 2,500 m3 tank with a held reserve",
             "  open: POC and line owner (U-065..U-068), coupling, cable",
             "    size, line circuits; change control from here on"]
    emit("i_basis", lines)


if __name__ == "__main__":
    ratings()
    water_basis()
    basis()
