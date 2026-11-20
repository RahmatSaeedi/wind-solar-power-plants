"""Chapter 50, lesson D (commissioning lab, the chapter's worked example):
a commissioning pack for the converter block =PVF1-3 - each step with its
prerequisites, method reference, safety boundary, expected evidence,
responsible party and the disposition when it fails - checked for
completeness, then a failed step followed to its disposition.

Run from the project root:   python -m companion.ch50.lab_d
Writes companion/ch50/expected/d_*.txt.
"""
from __future__ import annotations

from companion.ch50 import examples_b as eb
from companion.ch50.common import emit

FIELDS = ["prerequisites", "method", "boundary", "evidence", "by", "fails"]

# [start: pack]
ROWS = [   # step, prerequisites, method, boundary, evidence, by, if it fails
    ("C01 documents and certificates",
     "FAT reports (ch 44), MC certificate (ch 49)", "CP-PV-01 review",
     "none (paper)", "review sheet, list of gaps", "owner's engineer",
     "hold the pack; request the missing records"),
    ("C02 visual and mechanical", "C01; area handed over",
     "CP-PV-02 checklist", "de-energised, isolated, locked (permit)",
     "checklist, photos", "test team",
     "punch item A or B; retest after closure"),
    ("C03 string polarity, Voc, Isc",
     "C02; strings connected at combiners only",
     "CP-PV-03 (approved, per IEC 62446-1)",
     "DC live in daylight: qualified team, PPE per procedure",
     "string record with G and T", "test team",
     "isolate string; find cause; retest"),
    ("C04 insulation resistance", "C03", "CP-PV-04 (approved)",
     "as C03", "IR record", "test team",
     "isolate; locate fault; repair; retest"),
    ("C05 inverter pre-energisation checks", "C04; settings loaded",
     "maker's commissioning manual", "", "maker's checklist",
     "maker's engineer", "maker's disposition, recorded"),
    ("C06 MV energisation of the unit transformer",
     "lesson A prerequisites; authority signed",
     "CP-MV-01 switching programme",
     "switching by the authorised person only",
     "switching log, readings", "authorised person",
     "de-energise; investigate before retry"),
    ("C07 inverter start, functional tests", "C05, C06",
     "maker's manual + CP-PV-07", "energised plant: permit rules", "",
     "maker's engineer + test team", "maker's disposition, recorded"),
    ("C08 SCADA and controller points", "C07; loop checks (ch 48)",
     "CP-CTL-02", "no change to live settings without permit",
     "point list signed", "SCADA integrator", "punch; retest the point"),
    ("C09 block performance check", "C08; 3 clear days", "CP-PV-09",
     "normal operation", "PR of the block", "owner's engineer", ""),
]
PACK = [dict(zip(["step"] + FIELDS, r)) for r in ROWS]
# [end: pack]


def completeness() -> dict:
    gaps = [(p["step"], f) for p in PACK for f in FIELDS if not p.get(f)]
    lines = [f"commissioning pack of the converter block =PVF1-3: {len(PACK)} steps, "
             f"{len(FIELDS)} fields each"]
    lines += [f"  {p['step']:38s} by {p['by']}" for p in PACK]
    lines += ["  fields left empty:"]
    lines += [f"    {s}: {f}" for s, f in gaps]
    lines += [f"  {len(gaps)} gaps: C05 has no safety boundary, C07 no evidence,",
              "  C09 no disposition - a step without a boundary is a step",
              "  without a permit, and a step without evidence cannot pass"]
    emit("d_pack", lines)
    return dict(gaps=gaps, steps=len(PACK))


def disposition() -> list:
    ir = eb.insulation()
    steps = [f"isolate {', '.join(s for s in ir if s != 'S13')} at the combiner (lock, tag, record)",
             "repeat S13's test: a missing record is a test not done",
             "locate the fault section by section (approved method)",
             "repair: replace the damaged cable or connector; record what",
             "retest; record the new value with the instrument's number",
             "close the punch item and update the string record",
             "update the asset data (lesson I); then C05 may start"]
    lines = ["a failed step followed to its disposition (C04, insulation)"]
    lines += [f"  {k}. {s}" for k, s in enumerate(steps, 1)]
    lines += ["  the disposition is written in the pack before the test, so",
              "  a failure is handled the same way late on the last working",
              "  day of the week as on the first morning"]
    emit("d_dispo", lines)
    return ir


if __name__ == "__main__":
    completeness()
    disposition()
