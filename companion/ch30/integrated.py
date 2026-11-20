"""Chapter 30 - three integrated Plant P examples: two structural results
by hand, the design-review package and its evidence, and the structures
basis (D-034).

Run from the project root:   python -m companion.ch30.integrated
Writes companion/ch30/expected/int_*.txt.
"""
from __future__ import annotations

import math

from companion.ch30 import sources as src
from companion.ch30.common import emit
from plantp import structures as st


def by_hand() -> None:
    k = st.rotational_stiffness(25e6, 10.0, 0.35)
    m = (src.TOP_T + 0.24 * src.TOWER_T) * 1e3
    f_rot = math.sqrt(k / (m * src.HUB ** 2)) / (2 * math.pi)
    f = 1 / math.sqrt(1 / src.F1_FIXED ** 2 + 1 / f_rot ** 2)
    r, e = 12.0, 3.0
    a_hand = 2 * (r * r * math.acos(e / r) - e * math.sqrt(r * r - e * e))
    lines = ["two structural results checked by hand",
             f"  T07 rocking: K = 8 x 25e6 x 10^3 / (3 x 0.65) = {k / 1e9:.1f} GN m/rad;",
             f"    f_rot = {f_rot:.3f} Hz; 1/f^2 = 1/0.215^2 + 1/{f_rot:.3f}^2 -> f = {f:.3f} Hz",
             f"    code {st.frequency_with_foundation(src.F1_FIXED, k, m, src.HUB):.3f} Hz",
             f"  24 m base, e = 3 m: A' = 2 (144 acos(0.25) - 3 sqrt(135)) = {a_hand:.1f} m2;",
             f"    code {st.effective_area_circle(r, e):.1f} m2 (of {math.pi * r * r:.0f})",
             "  a hand check of one number from each formula protects",
             "  the whole table against a wrong unit or exponent"]
    emit("int_hand", lines)


def package() -> None:
    docs = [("design basis and load set (maker)", "received", "checked"),
            ("site-specific suitability (ch 11)", "received", "checked"),
            ("foundation geotechnical report (ch 29 Q1-Q10)", "draft", "open"),
            ("foundation structural calculation (24 m)", "received", "1 major open"),
            ("anchor cage and grout calculation", "received", "checked"),
            ("tower fabrication data books (12)", "3 of 12", "in progress"),
            ("PV structure calculation and pile tests", "received", "checked"),
            ("line tower load cases and foundations", "received", "checked"),
            ("substation structures and anchors", "draft", "open"),
            ("erection records: bolting, verticality", "per turbine", "ongoing")]
    lines = ["the structural design-review package of Plant P (teaching status)",
             "  document                                          status      review"]
    for d, s, r in docs:
        lines.append(f"  {d:49s} {s:11s} {r}")
    open_n = sum(1 for _, _, r in docs if "open" in r)
    lines += [f"  {open_n} items still open: the T07 foundation and the substation",
              "  structures wait for the geotechnical answers (ch 29) and",
              "  the checker's acceptance; nothing is built on an open item"]
    emit("int_package", lines)


def basis() -> None:
    lines = ["structures basis of Plant P (D-034):",
             "  loads: the turbine maker's load set (A-356 teaching values),",
             "    site suitability for the 50-year gust; wind governs the",
             "    turbine, earthquake may govern the substation",
             "  tower: buckling and fatigue set the walls; the ch 11",
             "    schedule needs about 32 t more steel low down (teaching)",
             "  foundation: a 24 m gravity base on dense ground (the 20 m",
             "    base of ch 4 / ch 29 lifts off); at T07 new gravel under",
             "    the base or piles, decided by the water range (ch 29 Q6);",
             "    concrete about 893 m3 a turbine (+44 % on ch 29's take-off)",
             "  anchors: preload about 1,250 kN a bolt; grout and flange",
             "    ring checked for it; re-tension after the first months",
             "  PV: lateral load sets the post depth in dense sand (about",
             "    2 m), pull-out the depth in loose silty sand; heavier zinc",
             "    or sacrificial steel where the soil is aggressive",
             "  line: angle points dominate (two to five times the storm",
             "    load); the 86 deg turn is a terminal or split in two",
             "  line: suspension towers more than about 15 m below both",
             "    neighbours lift their insulators on the coldest night",
             "    and swing further in wind - tension towers at the wadi",
             "  verification: independent checks of foundation and anchors;",
             "    type certificate's site assessment for the tower",
             "  findings for the maker: the fatigue steel raises f1 about",
             "    4.5 % (T07 would pass if credited); a 12 % margin rule",
             "    cannot be met by any base - only by a stiffer tower",
             "  open: geotechnical design values (ch 29 U-104..U-107 and Q1-",
             "    Q10); maker's dynamic stiffness requirement (A-359)"]
    emit("int_basis", lines)


if __name__ == "__main__":
    by_hand()
    package()
    basis()
