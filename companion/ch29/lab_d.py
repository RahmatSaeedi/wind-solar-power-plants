"""Chapter 29, lab D (worked example): review a fictional geotechnical
summary - check each borehole against what the design will need, list
the gaps and their consequences, and frame the questions for the
qualified geotechnical and civil engineers. No foundation solution is
presumed (chapter 30 and the engineers decide).

Run from the project root:   python -m companion.ch29.lab_d
Writes companion/ch29/expected/d_*.txt. Fictional data (A-349).
"""
from __future__ import annotations

import math

from companion.ch29 import sources as src
from companion.ch29.common import emit

REACH_BELOW_FOUNDING = 10.0       # m, teaching screening rule (or into rock)


# [start: review]
def review(bh: src.Borehole) -> list[tuple[str, str]]:
    """Gaps of one borehole against the teaching screening rules:
    (issue, consequence)."""
    out = []
    bottom = bh.layers[-1].bottom
    rock = any("sandstone" in l_.soil for l_ in bh.layers)
    turbine = "(T" in bh.name
    need = src.FOUNDATION_DEPTH + REACH_BELOW_FOUNDING if turbine else 6.0
    if bottom < need and not rock:
        out.append((f"stops at {bottom:.0f} m, no rock",
                    "ground below founding level unknown"))
    if bh.water_m is None:
        out.append(("groundwater not recorded",
                    "uplift, dewatering, concrete exposure"))
    missing = src.NEEDED_LAB - bh.lab
    if missing:
        out.append(("no " + ", ".join(sorted(missing)),
                    "concrete exposure class open"))
    for l_ in bh.layers:
        if "soft" in l_.soil:
            out.append((f"soft layer {l_.top:.1f}-{l_.bottom:.1f} m",
                        "settlement and stiffness need a design check"))
        if "gypsum" in l_.soil:
            out.append(("gypsum in the near surface",
                        "sulphate attack, dissolution"))
    return out
# [end: review]


def boreholes() -> None:
    lines = ["review of the geotechnical summary, borehole by borehole",
             "  (turbines: 10 m below founding level or rock; PV and substation 6 m)"]
    n = 0
    for bh in src.BOREHOLES:
        for issue, cons in review(bh):
            lines.append(f"  {bh.name:19s} {issue}")
            lines.append(f"  {'':19s}   -> {cons}")
            n += 1
    no_bh = [f"T{k:02d}" for k, xy in enumerate(src.TURBINES, 1)
             if not any(math.dist(xy, b.xy) < 1 for b in src.BOREHOLES)]
    lines += [f"  {n} findings; turbines without a borehole: {', '.join(no_bh)}",
              "  also absent from the summary: SPT hammer energy, seismic",
              "  site class, flood levels at the wadi, thermal resistivity",
              "  of the soil for the cables (ch 24), and the laboratory",
              "  strength and stiffness of the soft clay"]
    emit("d_review", lines)


def questions() -> None:
    qs = [
        "Q1  what ground model and design values do you propose at each turbine, and where is it interpolated?",
        "Q2  BH-03 stops at 6 m in sand: is a deeper borehole or a CPT needed at T05?",
        "Q3  BH-04 shows soft clay to 2.5 m at T07: what settlement and rotational stiffness follow?",
        "Q4  which exposure class do sulphate and chloride results give, and where are tests missing?",
        "Q5  BH-07 meets gypsum at T12: what is the risk of attack and of dissolution under wetting?",
        "Q6  groundwater was not recorded at T05 and T12: what level and seasonal range do you assume?",
        "Q7  what hammer energy was used, and how were SPT values corrected?",
        "Q8  what seismic site class and design ground motion apply (to be confirmed locally)?",
        "Q9  what investigation is still needed for T02, T04, T06, T08 and T10 before design?",
        "Q10 which soil thermal resistivity applies to the cable routes (ch 24 used 1.5 K m/W)?",
    ]
    lines = ["questions for the qualified geotechnical and civil engineers",
             "  (no foundation solution presumed - the answers feed ch 30)"]
    import textwrap
    for q in qs:
        w = textwrap.wrap(q, 74)
        lines.append("  " + w[0])
        lines += ["      " + x for x in w[1:]]
    lines += ["  each question names the data it rests on and the decision",
              "  it unblocks; the answers go into the ground model with",
              "  their source, and the open ones into the unknowns (U-104)"]
    emit("d_questions", lines)


if __name__ == "__main__":
    boreholes()
    questions()
