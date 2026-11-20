"""Chapter 32, lab F (worked example 2): a job hazard analysis for a
maintenance task - replacing a yaw-drive motor in a nacelle - with the
risk before and after controls, a check that every severe hazard has a
control above PPE, and the residual risks that remain for the permit
and the supervisor.

Run from the project root:   python -m companion.ch32.lab_f
Writes companion/ch32/expected/f_*.txt and diagrams/data/ch32-jha.csv.
Teaching scores (A-373). A real JHA is written by the crew that does
the work, with the maker's manual and the site's procedures; isolation
steps are named by purpose here, not given as a procedure.
"""
from __future__ import annotations

from companion.ch32 import sources as src  # noqa: F401  (puts plantp on the path)
from companion.ch32.common import csv, emit
from plantp import safety as sf

# kinds of control, highest first
RANK = {"E": "eliminate", "S": "substitute", "G": "engineer",
        "A": "administrate", "P": "protect"}

# [start: jha]
JHA = [  # (step, hazard, L0, S0, [(kind, control)], L1, S1)
    ("1 plan, permit, weather", "work started in high wind or heat",
     3, 4, [("A", "permit with wind and heat limits"),
            ("A", "forecast checked")], 1, 4),
    ("2 climb to the nacelle", "fall from the ladder",
     2, 5, [("G", "service lift"), ("G", "fall-arrest rail"),
            ("A", "rescue kit up")], 1, 5),
    ("3 isolate the yaw drives", "unexpected movement or energy",
     3, 5, [("G", "yaw lock pins"), ("A", "isolation by the permit"),
            ("A", "verified dead by an authorised person")], 1, 5),
    ("4 rig the service crane", "dropped load, overload",
     2, 4, [("G", "crane rated for the motor"),
            ("A", "lift plan, exclusion zone")], 1, 4),
    ("5 remove the old motor", "hand crushed, back strain",
     3, 3, [("G", "lifting aid"), ("P", "gloves")], 2, 2),
    ("6 lower it through the hatch", "fall through the open hatch",
     2, 5, [("P", "harness clipped on")], 2, 5),
    ("7 fit the new motor", "pinch points, wrong torque",
     3, 3, [("G", "guide pins"), ("A", "torque record")], 1, 3),
    ("8 remove locks, test yaw", "movement with a person in reach",
     2, 5, [("A", "everyone clear and counted"),
            ("A", "permit cancelled in order")], 1, 5),
    ("9 descend, hand back", "fatigue, haste at day's end",
     2, 4, [("A", "time limit, buddy check")], 1, 4),
]
# [end: jha]


def table(jha) -> list[str]:
    lines = ["  step                          before        after   top control"]
    for step, hz, l0, s0, ctl, l1, s1 in jha:
        b, a = sf.risk_score(l0, s0), sf.risk_score(l1, s1)
        top = min(ctl, key=lambda c: list(RANK).index(c[0]))
        lines.append(f"  {step:29s} {b:3d} {sf.risk_band(b):8s} {a:3d} {sf.risk_band(a):7s}"
                     f" {RANK[top[0]]}")
    return lines


def check(jha) -> list[str]:
    """Rules: risk may not rise; a hazard of severity 5 needs a control
    above administration and PPE; residual 'high' or worse stops the job."""
    out = []
    for step, hz, l0, s0, ctl, l1, s1 in jha:
        if sf.risk_score(l1, s1) > sf.risk_score(l0, s0):
            out.append(f"{step}: risk rises after controls")
        kinds = {c[0] for c in ctl}
        if s0 == 5 and not kinds & {"E", "S", "G"}:
            out.append(f"{step}: severity 5 with only {', '.join(RANK[k] for k in kinds)}")
        if sf.risk_band(sf.risk_score(l1, s1)) in ("high", "very high"):
            out.append(f"{step}: residual {sf.risk_band(sf.risk_score(l1, s1))}")
    return out


def analysis() -> None:
    lines = ["job hazard analysis: replace a yaw-drive motor (draft)"] + table(JHA)
    errs = check(JHA)
    lines.append(f"  checker findings: {len(errs)}")
    lines += [f"    {e}" for e in errs]
    emit("f_draft", lines)


def revised() -> None:
    jha = list(JHA)
    jha[5] = ("6 lower it through the hatch", "fall through the open hatch", 2, 5,
              [("G", "hatch guard rail"), ("G", "winch lowering"),
               ("P", "harness on a fixed anchor")], 1, 5)
    jha[7] = ("8 remove locks, test yaw", "movement with a person in reach", 2, 5,
              [("G", "trapped-key interlock on the yaw panel"),
               ("A", "everyone clear and counted"),
               ("A", "permit cancelled in order")], 1, 5)
    rows = [(r[0].split()[0], sf.risk_score(r[2], r[3]), sf.risk_score(r[5], r[6]))
            for r in jha]
    csv("ch32-jha.csv", "step,before,after", rows)
    before = sum(b for _, b, _ in rows)
    after = sum(a for _, _, a in rows)
    five = sum(1 for r in jha if r[6] == 5)
    lines = ["job hazard analysis: steps 6 and 8 revised, the residual risk"]
    lines += table(jha)
    lines += [f"  checker findings: {len(check(jha))}",
              f"  sum of scores {before} before, {after} after controls",
              f"  {five} steps keep severity 5 at likelihood 1: the climb, the",
              "  isolation, the hatch and the yaw test. Controls cut the",
              "  likelihood, not the consequence - the permit, the",
              "  authorised person and a rescue-ready crew are what hold",
              "  those rows at 5 every time the job is done"]
    emit("f_revised", lines)


if __name__ == "__main__":
    analysis()
    revised()
