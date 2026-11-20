"""Chapter 33 - three integrated Plant P examples: two results by hand,
the environmental and social package in numbers, and the basis D-037.

Run from the project root:   python -m companion.ch33.integrated
Writes companion/ch33/expected/int_*.txt.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch33 import sources as src
from companion.ch33.common import emit
from companion.ch33 import lab_d
from plantp import envsocial as es


def by_hand() -> None:
    d = 806.0
    lp = es.noise_at(106, d, 2.0)
    total = es.inventory_total({k: (a, f) for k, (a, f, _c) in src.LCA.items()}) / 1000
    lines = ["two environmental results checked by hand",
             f"  one turbine at 806 m: 106 - 20 log10(806) - 11 - 2 x 0.806"
             f" = {106 - 20 * math.log10(d) - 11 - 1.612:.1f} dB(A); code {lp:.1f}",
             f"  modules: 60,000 kWp x 450 kg = {60_000 * 450 / 1000:,.0f} t of {total:,.0f} t"
             " (S0 manufacture)",
             "  a hand check of one term guards the sums of the whole",
             "  inventory against a wrong unit or exponent"]
    emit("int_hand", lines)


def package() -> None:
    errs = lab_d.check(lab_d.REGISTER)
    lines = ["the environmental and social package of Plant P in numbers",
             f"  register rows: {len(lab_d.REGISTER)}; draft findings {len(errs)}; permit rows 6",
             "  receptors under the night-noise placeholder: 5 of 5",
             "  flicker at the dwellings with W2b: 0 h (W2: 112 h at the camp)",
             "  raptor collisions estimated: about 5 a year (study first)",
             "  bat curtailment: about 1 % of wind energy",
             "  land: 147 ha taken, 3.1 ha of customary grazing, one route",
             "  water: plant 13 % of local withdrawals in operation;",
             "    construction water trucked in, never pumped locally",
             "  footprint: about 12.5 g CO2e/kWh (S0), 13.3 (S1), ranges overlap",
             "  budget of the E&S plan: 270 k u a year, 1.3 % of revenue"]
    emit("int_package", lines)


def basis() -> None:
    lines = ["D-037 environmental and social basis of Plant P (teaching)",
             "  1 assessment: screening, noise with background, flicker",
             "    avoided by W2b, raptor study before the final layout,",
             "    bat cut-in on autumn nights, visibility accepted with",
             "    photomontages, cumulative effects with other projects",
             "  2 people: stakeholder map, disclosure ahead of decisions,",
             "    land register with customary use, herders' route kept",
             "    (fence gap), water point offered, commitments only if",
             "    approved and funded",
             "  3 monitoring: register E01-E06, S01-S03 with owners and",
             "    indicators; P rows wait for the permit text",
             "  4 fire aftermath: communication, sampling grid, waste",
             "    routes, pond tested before any release",
             "  5 water: village first in drought, monitoring well,",
             "    construction water from outside the aquifer",
             "  6 footprint: functional unit 1 kWh at the POC, inventory",
             "    and avoided emissions reported apart, supplier data",
             "    verified before it replaces generic factors",
             "  7 change control: triggers per topic (1 dB, any flicker,",
             "    10 % of collisions); T06's 150 m move trips the noise one",
             "  8 monitoring: bat carcass rounds every 3 days, raptor",
             "    rounds every 14; noise survey repeated in the camp's",
             "    season (margin under 1 dB); quarterly RAG report",
             "  9 community: no night convoys through the village (trucks",
             "    add 4.2 dB), site medic, verified local-content numbers,",
             "    trained guards only, detection-activated lights if allowed",
             "  open: permit conditions (U-112), raptor and bat surveys",
             "    (U-113), aquifer recharge and rights (U-114); the",
             "    framework's answers on land and consultation (lab G)"]
    emit("int_basis", lines)


if __name__ == "__main__":
    by_hand()
    package()
    basis()
