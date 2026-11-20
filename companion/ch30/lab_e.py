"""Chapter 30, lab E (worked example): a fabrication traveler and
inspection plan for tower section 1 (D 4.50-4.12 m, 25 m, ch 11), with
the checks that need qualified engineers and inspectors - weld
parameters against the procedure window, ovality and flange flatness,
coating thickness, and ultrasonic testing of the seams.

Run from the project root:   python -m companion.ch30.lab_e
Writes companion/ch30/expected/e_*.txt. Teaching tolerances and readings
(A-362): the maker's specification and the code set the real ones.
"""
from __future__ import annotations

import numpy as np

from companion.ch30.common import emit
from plantp import materials as mt

# [start: traveler]
TRAVELER = [   # step, record, acceptance (teaching), signed by, H/W/R
    ("plate receipt", "mill inspection certificate, heat no.",
     "grade, toughness", "QC", "H"),
    ("cutting and bevels", "cut list, bevel gauge", "drawing", "fitter", "R"),
    ("rolling of cans", "ovality on the roll", "tolerance", "QC", "W"),
    ("longitudinal seams (SAW)", "WPS no., welder, parameters",
     "WPS window", "welding coord.", "W"),
    ("circumferential seams", "WPS no., welder, parameters",
     "WPS window", "welding coord.", "W"),
    ("flange fit-up and weld", "flatness before and after",
     "flatness", "QC", "H"),
    ("door frame weld", "WPS, preheat record", "WPS window",
     "welding coord.", "H"),
    ("UT of seams, MT of door", "NDT reports", "no rejectable flaw",
     "NDT level 2", "H"),
    ("dimensional survey", "length, ovality, straightness", "tolerances",
     "surveyor", "H"),
    ("blast and coating", "profile, DFT, adhesion", "coating spec",
     "coating insp.", "H"),
    ("internals and marking", "checklist, serial no.", "drawing", "QC", "R"),
    ("release for shipping", "data book complete", "all above closed",
     "client insp.", "H"),
]
# [end: traveler]


def traveler() -> None:
    lines = ["fabrication traveler of tower section 1 (H hold, W witness, R record)"]
    for k, (step, rec, acc, who, t) in enumerate(TRAVELER, 1):
        lines.append(f"  {k:2d} [{t}] {step:25s} {rec}")
        lines.append(f"         accept: {acc}; signed by {who}")
    n_h = sum(t == "H" for *_, t in TRAVELER)
    lines += [f"  {n_h} hold points; every record carries the section's serial",
              "  number and the plates' heat numbers, so any later finding",
              "  traces back to the steel mill (supplier traceability)"]
    emit("e_traveler", lines)


def weld_window() -> None:
    wps = dict(V=(30.0, 34.0), A=(550.0, 650.0), s=(8.0, 11.0), q=(1.3, 2.2))   # q kJ/mm
    passes = [(32, 600, 9.5), (33, 620, 9.0), (31, 590, 10.5), (34, 660, 9.2),
              (32, 610, 7.0), (30, 560, 10.0)]
    lines = ["submerged-arc circumferential seam: recorded passes against the WPS",
             "  (window V 30-34, A 550-650, travel 8-11 mm/s, heat input 1.3-2.2 kJ/mm)",
             "  pass   V    A    mm/s   kJ/mm   result"]
    for k, (v, a, sp) in enumerate(passes, 1):
        q = mt.weld_heat_input(v, a, sp)                  # kJ/mm, efficiency 0.8
        bad = [n for n, x in (("V", v), ("A", a), ("s", sp), ("q", q))
               if not wps[n][0] <= x <= wps[n][1]]
        lines.append(f"  {k:4d}  {v:3.0f}  {a:4.0f}  {sp:5.1f}   {q:5.2f}   "
                     f"{'ok' if not bad else 'OUT: ' + ', '.join(bad)}")
    lines += ["  pass 4 runs above the current range and pass 5 too slow",
              "  (heat input too high): both go to the welding coordinator;",
              "  the weld is assessed (and tested) before acceptance - the",
              "  WPS was qualified only inside its window"]
    emit("e_weld", lines)


def dimensions() -> None:
    rng = np.random.default_rng(30)
    d_nom = 4.50
    dmax = d_nom + 0.010 + 0.004 * rng.random(8)
    dmin = d_nom - 0.010 - 0.004 * rng.random(8)
    dmax[5], dmin[5] = d_nom + 0.019, d_nom - 0.018
    oval = 100 * (dmax - dmin) / d_nom
    flat = np.array([0.3, 0.6, 0.4, 0.9, 1.4, 0.5, 0.3, 0.8, 0.4, 0.7, 0.5, 0.6])
    lines = ["dimensional survey (teaching tolerances: ovality <= 0.7 % of D;",
             "  flange flatness <= 1.2 mm over the circle, read at 12 points)",
             "  can   ovality %   result"]
    for k, o in enumerate(oval, 1):
        lines.append(f"  {k:3d}   {o:9.2f}   {'ok' if o <= 0.7 else 'OUT'}")
    lines += [f"  flange flatness at 12 points, mm: {' '.join(f'{x:.1f}' for x in flat)}",
              f"  range {flat.max() - flat.min():.1f} mm -> "
              f"{'ok' if flat.max() - flat.min() <= 1.2 else 'OUT'}",
              "  can 6 is out of round: re-rounding or a concession from",
              "  the designer (ovality lowers the buckling strength,",
              "  lesson B); the flange is within tolerance - it is",
              "  measured again after welding, when heat distorts it"]
    emit("e_dimensions", lines)


def coating() -> None:
    rng = np.random.default_rng(31)
    nominal = 320.0
    dft = np.round(345 + 35 * rng.standard_normal(40), 0)
    dft[7] = 248.0
    low = dft < 0.8 * nominal
    lines = ["dry film thickness of the outer coating, 40 readings (um)",
             "  (teaching acceptance: mean >= nominal 320; none below 80 %;",
             "   the coating specification sets the real rule)",
             f"  mean {dft.mean():.0f}, s {dft.std(ddof=1):.0f}, lowest {dft.min():.0f},"
             f" above 400: {int((dft > 400).sum())}",
             f"  readings below {0.8 * nominal:.0f}: {int(low.sum())}"
             f" -> {'repair the spot and re-measure' if low.any() else 'ok'}",
             "  a good mean hides a thin spot: the rule has two parts,",
             "  and thick spots are noted too (they crack); adhesion",
             "  is tested on a witness panel, not on the tower"]
    emit("e_coating", lines)


def ndt() -> None:
    seams_m = 4 * 3.14 * 4.3 + 25.0 * 2
    found = 3
    lines = ["ultrasonic testing of the section's seams (teaching numbers)",
             f"  circumferential and longitudinal seams: about {seams_m:.0f} m, 100 % UT",
             f"  rejectable indications found: {found} (lack of fusion, slag)",
             "  repair: excavate, re-weld to the repair WPS, re-test the",
             "  repaired length and a margin either side",
             f"  repair rate {100 * found * 0.3 / seams_m:.1f} % of length (0.3 m a repair)",
             "  a rising repair rate is a process signal (a welder, a",
             "  consumable lot, a machine) - the welding coordinator",
             "  reviews it weekly; the NDT operator is certified (level 2)",
             "  and the method qualified for the thickness"]
    emit("e_ndt", lines)


def approvals() -> None:
    rows = [("tower design and its load set", "turbine maker's structural engineer"),
            ("design verification", "independent verifier / certification body"),
            ("welding procedures (WPS/PQR)", "welding engineer; witnessed qualification"),
            ("welder qualifications", "examiner of the qualification body"),
            ("NDT procedures and results", "NDT level 3 (procedures), level 2 (tests)"),
            ("concessions (out-of-tolerance)", "designer, in writing, before release"),
            ("coating", "certified coating inspector"),
            ("release of the section", "client's inspector, final hold point")]
    lines = ["checks that need qualified people (not the traveler's author)"]
    for what, who in rows:
        lines.append(f"  {what:34s} {who}")
    lines += ["  the traveler records what was done; these people decide",
              "  whether it is good enough - their names and certificates",
              "  are part of the data book"]
    emit("e_approvals", lines)


if __name__ == "__main__":
    traveler()
    weld_window()
    dimensions()
    coating()
    ndt()
    approvals()
