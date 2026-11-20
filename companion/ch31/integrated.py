"""Chapter 31 - three integrated Plant P examples: two logistics results
by hand, the campaign in numbers, and the logistics basis (D-035).

Run from the project root:   python -m companion.ch31.integrated
Writes companion/ch31/expected/int_*.txt.
"""
from __future__ import annotations

from companion.ch31 import sources as src
from companion.ch31.common import emit
from plantp import logistics as lg


def by_hand() -> None:
    t, r = lg.axle_loads(160, 30, 42, 16, tractor_axles=4, tractor_share=0.05)
    cap = lg.chart_capacity(16, src.CRANE_CHART)
    lines = ["two logistics results checked by hand",
             f"  nacelle trailer axle: (42 + 0.95 x 160) x 9.81 / 16 = {(42 + 152) * 9.81 / 16:.1f} kN;"
             f" code {r:.1f}",
             f"  crane at 16 m: chart point 210 t; use (160 + 8) / 210 = {168 / 210:.2f};"
             f" code {168 / cap:.2f}",
             "  a hand check of one number from each formula protects",
             "  the whole table against a wrong unit or index"]
    del t
    emit("int_hand", lines)


def campaign() -> None:
    per_turbine = sum(n for (*_, n) in src.COMPONENTS.values())
    lines = ["the delivery campaign of Plant P in numbers (teaching)",
             f"  turbine abnormal loads: {12 * per_turbine} (12 x {per_turbine})",
             "  crane: one main crawler crane, about 10 days a turbine plus",
             "    3 days of moving between pads -> about 156 crane days",
             "  weather standby expected: about 14 k u a nacelle lift (lab D),",
             "    with a worst case near 300 k u",
             "  collector drums 186, conductor reels 12, transformer 1 heavy haul",
             "  laydown: about 9,600 m2 at peak (four turbines staged)",
             "  bridges: 2 of 3 need the owner's assessment before any convoy",
             "  hold points per nacelle lift: 8 (lab D)"]
    emit("int_campaign", lines)


def basis() -> None:
    lines = ["logistics basis of Plant P (D-035):",
             "  route: port to site 244 km; abnormal loads at night under the",
             "    permit (U-106); two long bridges assessed by their owner",
             "    before the first convoy; the 4.85 m overpass leaves 5 cm",
             "    for the base section - measured, with a fallback route",
             "  vehicles: 16 trailer axles for the nacelle, 14 for the base",
             "    section (teaching axle limit 120 kN)",
             "  lifts: one crawler crane; nacelle at 0.80 of the chart; tandem",
             "    and near-live lifts critical whatever their use; the",
             "    approved lift plans are the lift engineer's",
             "  weather: lift limits from the maker; the rotor waits longest;",
             "    standby paid as the contract says; nacelles just in time",
             "  receipt and preservation: inspection at unloading; impact",
             "    recorders read; desiccant and heaters logged; every",
             "    hand-over signed (chain of custody)",
             "  emergency: rescue at height by the trained site team during",
             "    lifts; medical transfer agreed with local services; radio",
             "    or satellite where mobile coverage fails (ch 32)",
             "  export works: 186 drums, 12 reels, 5 stringing sections, the",
             "    transformer skidded onto its plinth; each work package",
             "    with its own approval",
             "  campaign: route capacity (night window, parking places) sets",
             "    the pace; a 7-day delivery buffer; start month chosen with",
             "    the wind (159-177 days in the data year); one main crane",
             "    unless the grid date makes a second one pay",
             "  findings: swept paths at every bend; a pusher above 8-10 %",
             "    grades; nacelles on the maker's yoke, never site slings;",
             "    cable duct runs limited by bends and length (joint bays)"]
    emit("int_basis", lines)


if __name__ == "__main__":
    by_hand()
    campaign()
    basis()
