"""Chapter 24 - three integrated Plant P examples: one cable checked by
hand, the circuit basis of the collector and the export, and the
procurement and acceptance schedule (D-028).

Run from the project root:   python -m companion.ch24.integrated
Writes companion/ch24/expected/int_*.txt.
"""
from __future__ import annotations

import math

from companion.ch24 import sources as src
from companion.ch24.common import emit
from plantp import cables as cb


def by_hand() -> None:
    i = 4 * 5e6 / 0.95 / (math.sqrt(3) * 33e3)
    d = src.MV_CABLES[630]
    k = 0.97 * 0.88 * 0.93 * 0.85
    r = cb.r_at(d["r20"], 90, 0.00403)
    lines = ["the first section of WS1 by hand (630 mm2 Al):",
             f"  current {i:.0f} A; rating in place {d['i0']:.0f} x {k:.3f} = {d['i0'] * k:.0f} A",
             f"  r at 90 C {r:.4f} ohm/km; drop over 1.1 km"
             f" {cb.drop_pct(i, 1.1, r, d['x'], 0.95, 33):.2f} %",
             f"  12.5 kA for 1 s needs {12.5e3 / 94:.0f} mm2; 630 mm2 carries"
             f" {cb.withstand_ka(630, 1, 94):.1f} kA",
             "  all three checks pass with the trench's factors applied"]
    emit("int_hand", lines)


def basis() -> None:
    lines = ["circuit basis of Plant P (D-028; PLP-ELE-CAL-0009):",
             "  wind strings: 630 mm2 first section, 240 mm2 beyond",
             "    (graded; cost + losses least of the allowed plans)",
             "  PV feeders: PVF1's first section (4 blocks) 630 mm2, the",
             "    rest of PVF1, PVF2, PVF3 and the battery feeders 240 mm2;",
             "    route bends at least 15 x the cable's diameter",
             "  installation: 1.0 m depth, two circuits 0.4 m apart; soil",
             "    1.5 K m/W until the thermal survey (U-093)",
             "  33 kV gear 25 kA 3 s, 63 kA peak; LV board 15 kA",
             "  export: single-circuit 132 kV overhead line (D-022) - the",
             "    cable option kept for crossings the line cannot make",
             "  LV feeders: 25 mm2 Cu minimum unless a current-limiting",
             "    breaker's let-through allows less; long feeders by drop",
             "  DC: trip circuits checked at the end-of-discharge voltage",
             "  added after the first draft:",
             "    rating on a high percentile of the soil survey, hot spots",
             "    (crossings, dry stretches) backfilled or grouted; DTS fibre",
             "    in the collector trenches",
             "    screens checked with the feeder relay for cross-country",
             "    faults (35 mm2 at 0.3 s); incomers 1,600 A (ch 26)",
             "    PV string cables 6 mm2 (losses priced); LV checked for",
             "    loop impedance with the chosen breaker types",
             "    132 kV line: rating on hot, still days limits export",
             "    (study with the weather data); creepage from a site",
             "    pollution assessment; tower footing resistance recorded",
             "    vacuum-switched unit transformers: arresters or RC",
             "    snubbers per the makers' study; SF6 density monitored"]
    emit("int_basis", lines)


def procurement() -> None:
    items = [("33 kV cable 630 mm2", "km", 3 * 1.1 + 0.6, "type, routine per drum"),
             ("33 kV cable 240 mm2", "km", 3 * 3.3 + 3 * 0.6 + 2 * 1.8 + 4 * 0.6,
              "type, routine per drum"),
             ("33 kV joints and terminations", "sets", 38 + 52, "type-tested kits, records"),
             ("33 kV switchgear panels", "panels", 18, "type tests, routine, FAT"),
             ("LV cables Cu", "m", 1_955, "maker's certificates"),
             ("132 kV line materials", "km", 7.06, "conductor, insulator tests")]
    lines = ["procurement and acceptance schedule (quantities bounded):",
             "  item                            unit       qty  evidence"]
    for n, u, q, e in items:
        lines.append(f"  {n:31s} {u:6s} {q:8,.1f}  {e}")
    lines += ["  quantities carry the +/- 15 % of the routes until the",
              "  survey; every item names the evidence that accepts it"]
    emit("int_procurement", lines)


if __name__ == "__main__":
    by_hand()
    basis()
    procurement()
