"""Chapter 30, lesson K: independent verification and monitoring - the
review matrix of the structural package, design-review findings by
severity, settlement of a foundation over time (fitted on log time), and
the re-tension check of the anchor bolts after the first months.

Run from the project root:   python -m companion.ch30.examples_k
Writes companion/ch30/expected/k_*.txt and diagrams/data/ch30-settle.csv.
Teaching values (A-362).
"""
from __future__ import annotations

import numpy as np

from companion.ch30.common import csv, emit


def review_matrix() -> None:
    rows = [("design basis and load set", "turbine maker", "certification body"),
            ("tower (strength, buckling, fatigue)", "maker's engineer", "certification body"),
            ("foundation (geotechnical)", "geotechnical engineer", "independent checker"),
            ("foundation (structural)", "structural engineer", "independent checker"),
            ("anchor cage and grout", "maker / engineer", "independent checker"),
            ("PV structures and piles", "PV structure supplier", "owner's engineer + tests"),
            ("line towers and foundations", "line designer", "network operator / checker"),
            ("substation structures", "substation designer", "owner's engineer")]
    lines = ["who designs and who checks the structural package (teaching)"]
    for item, des, chk in rows:
        lines.append(f"  {item}")
        lines.append(f"      designed by {des}; checked by {chk}")
    lines += ["  the checker is independent of the designer and checks",
              "  with its own calculation, not by reading the designer's;",
              "  site-specific foundations of type-certified turbines are",
              "  part of the site assessment (ch 11) - the owner's",
              "  engineer only follows the findings to closure"]
    emit("k_matrix", lines)


def findings() -> None:
    cats = [("load set does not match the turbine's class", "major", 1, 0),
            ("groundwater range not used (ch 29 Q6)", "major", 1, 1),
            ("fatigue of door frame welds not shown", "major", 1, 0),
            ("rocking stiffness below the maker's value at T07", "major", 1, 0),
            ("drawing and calculation give different cover", "minor", 3, 0),
            ("missing bar marks in the schedule", "minor", 5, 2),
            ("units mixed in one table", "editorial", 4, 0)]
    lines = ["findings of the independent design review (synthetic)",
             "  finding                                            class      n  open"]
    for f, c, n, o in cats:
        lines.append(f"  {f:50s} {c:9s} {n:2d}  {o:4d}")
    open_major = sum(o for _, c, _, o in cats if c == "major")
    lines += [f"  open major findings: {open_major} -> construction of the affected",
              "  foundation waits; a major finding closes with a revised",
              "  calculation the checker accepts, not with a reply letter"]
    emit("k_findings", lines)


def settlement() -> None:
    t = np.array([7, 30, 60, 120, 240, 365])                    # days after loading
    s = np.array([6.0, 9.5, 11.0, 12.6, 14.1, 15.0])            # mm, T07 base edge (synthetic)
    a, b = np.polyfit(np.log10(t), s, 1)
    pred_25y = a * np.log10(25 * 365) + b
    csv("ch30-settle.csv", "t,s,fit", [(int(x), f"{y:.1f}", f"{a * np.log10(x) + b:.1f}")
                                       for x, y in zip(t, s)])
    lines = ["settlement of the T07 foundation edge after erection (synthetic survey)",
             "  days   " + "  ".join(f"{x:5d}" for x in t),
             "  mm     " + "  ".join(f"{x:5.1f}" for x in s),
             f"  fit s = {a:.2f} log10(t) + {b:.2f}; at 25 years about {pred_25y:.0f} mm",
             "  settlement slows with log time, as creep of sand does;",
             "  the 25-year projection is checked against the designer's",
             "  limit and the survey goes on until the readings flatten -",
             "  a straight line on a linear time axis would be a warning"]
    emit("k_settle", lines)


def retension() -> None:
    rng = np.random.default_rng(301)
    ratio = np.clip(0.96 + 0.025 * rng.standard_normal(160), 0.85, 1.02)
    ratio[[17, 88]] = (0.86, 0.88)
    low = ratio < 0.90
    lines = ["anchor-bolt re-tension check after six months (160 bolts, synthetic)",
             f"  remaining preload: mean {100 * ratio.mean():.1f} %, lowest {100 * ratio.min():.0f} %",
             f"  below 90 %: {int(low.sum())} bolts -> re-tensioned and recorded",
             "  some loss is expected (grout creep, embedding); two bolts",
             "  far below the rest point at a local cause - grout under",
             "  that sector is inspected before they are simply retightened"]
    emit("k_retension", lines)


if __name__ == "__main__":
    review_matrix()
    findings()
    settlement()
    retension()
