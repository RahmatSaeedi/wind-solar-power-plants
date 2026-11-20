"""Chapter 33, lab H (worked examples 3 and 4): a stakeholder and grievance
workflow with evidence and remedy tracking, the assessment of a
contractor's worker-accommodation and community-traffic plan, a
responsibility and budget matrix, and the response to a chance find.

Run from the project root:   python -m companion.ch33.lab_h
Writes companion/ch33/expected/h_*.txt and diagrams/data/ch33-grievance.csv.
Teaching values (A-381, A-382); the fictional community of ch 14 and 22.
"""
from __future__ import annotations

import numpy as np

from companion.ch33 import sources as src  # noqa: F401  (puts plantp on the path)
from companion.ch33.common import csv, emit

# [start: workflow]
STAGES = [  # (stage, target days, evidence kept)
    ("received and logged", 1, "entry, channel, language"),
    ("acknowledged to complainant", 3, "dated message or visit note"),
    ("assessed and assigned", 7, "category, owner, risk"),
    ("investigated", 21, "site visit, photos, witnesses"),
    ("resolution proposed", 30, "letter in plain language"),
    ("agreed or escalated", 45, "signed note, or appeal opened"),
    ("remedy delivered and checked", 60, "proof of the remedy"),
    ("closed with complainant", 75, "closure note, satisfaction")]
# [end: workflow]


def workflow(seed: int = 33) -> None:
    rng = np.random.default_rng(seed)
    n = 40
    late = []
    for k, (st, target, _ev) in enumerate(STAGES):
        actual = rng.gamma(4.0, target / 4.0 * 1.05, n)
        late.append(float(np.mean(actual > target)))
    csv("ch33-grievance.csv", "stage,late", [(k + 1, round(x, 3)) for k, x in enumerate(late)])
    lines = ["grievance workflow: stages, target days and evidence (teaching)",
             "  stage                            target d   late %"]
    for (st, target, ev), lt in zip(STAGES, late):
        lines += [f"  {st:32s} {target:8d}   {lt * 100:6.0f}", f"      evidence: {ev}"]
    lines += [f"  {min(late) * 100:.0f}-{max(late) * 100:.0f} % of cases miss each stage's target: either",
              "  the targets or the staffing are wrong, and the quarterly",
              "  review fixes one of them;",
              "  each stage leaves evidence, so a closed case can be",
              "  shown, not just claimed; confidential cases (conduct,",
              "  harassment) take a protected route, and nobody who",
              "  complains is penalised (non-retaliation is stated in",
              "  every leaflet); the log is reported, anonymised, each",
              "  quarter to the community and the lenders"]
    emit("h_workflow", lines)


def remedy() -> None:
    cases = [("dust on crops, farm 1", "spray schedule, crop payment", True),
             ("blocked track to the spring", "fence gap opened", True),
             ("unpaid wages, subcontractor", "paid via main contractor, audit", True),
             ("night noise at camp", "reduced mode, monitoring", False),
             ("road damage at village edge", "repair scheduled", False)]
    lines = ["remedy tracking: from proposal to proof (synthetic)",
             "  case                             remedy"]
    done = 0
    for c, r, ok in cases:
        done += ok
        lines += [f"  {c:32s} {r}", f"      delivered and checked: {'yes' if ok else 'not yet'}"]
    lines += [f"  {done} of {len(cases)} remedies proven; the others stay open in",
              "  the report until the complainant confirms - a promised",
              "  remedy is not a delivered one"]
    emit("h_remedy", lines)


def accommodation_traffic() -> None:
    checks = [("camp water from its own source", False, "uses site wells (ch 32: 61 %)"),
              ("rooms: space, ventilation, separate sanitation", True, "plan meets lender standard"),
              ("code of conduct, training, sanctions", True, "signed by all workers"),
              ("worker grievance channel independent of the foreman", False, "foreman only"),
              ("bus schedule avoids school hours", True, "05:30 and 18:00"),
              ("haul trucks: 30 km/h in village, marshal at school", False, "no marshal"),
              ("community told of the traffic calendar", True, "monthly notice")]
    lines = ["contractor's accommodation and community-traffic plan: review",
             "  requirement                                          ok?"]
    gaps = 0
    for r, ok, f in checks:
        gaps += not ok
        lines += [f"  {r:52s} {'yes' if ok else 'NO':4s}", f"      {f}"]
    lines += [f"  {gaps} gaps: the plan goes back with dated corrective actions",
              "  before mobilisation - water source, an independent worker",
              "  channel, a school marshal; the review and its closure are",
              "  part of the contract (lesson C, ch 32)"]
    emit("h_plan", lines)


def budget_matrix() -> None:
    rows = [("livelihood measures (fence gap, water point)", "E&S manager", 55),
            ("grievance mechanism (staff, phone, visits)", "community liaison", 40),
            ("biodiversity surveys and carcass search", "E&S manager", 90),
            ("noise and water monitoring", "O&M manager", 35),
            ("training: conduct, induction", "HR manager", 20),
            ("independent audit, twice a year", "owner", 30)]
    total = sum(b for *_, b in rows)
    lines = ["responsibility and budget for the E&S plan (teaching, k u a year)",
             "  item                                           owner                budget"]
    for i, o, b in rows:
        lines.append(f"  {i:46s} {o:20s} {b:6d}")
    revenue = 70 * 295_100 / 1000                       # k u a year at 70 u/MWh (ch 21)
    lines += [f"  total {total} k u a year - about {total / revenue * 100:.1f} % of the yearly revenue",
              "  a plan without a named owner and a budget line is a wish:",
              "  the matrix goes into the project budget and is audited"]
    emit("h_budget", lines)


def chance_find() -> None:
    steps = [(0, "excavator operator sees bones or worked stone: stops"),
             (5, "supervisor fences 30 m around, no further digging there"),
             (30, "E&S manager informed; photos, location, no removal"),
             (240, "authority informed by the agreed route"),
             (2880, "archaeologist or authority visits; community elders told"),
             (10080, "decision: record, move, or re-route the works")]
    lines = ["response to a chance find in a cable trench (teaching timeline)",
             "  minutes   action"]
    for m, a in steps:
        lines.append(f"  {m:7d}   {a}")
    lines += ["  the work moves elsewhere while the find waits; human",
              "  remains near the cemetery are treated with the community's",
              "  customs - the authority and the elders decide, and the",
              "  delay is planned for in the schedule's float"]
    emit("h_chance", lines)


if __name__ == "__main__":
    workflow()
    remedy()
    accommodation_traffic()
    budget_matrix()
    chance_find()
