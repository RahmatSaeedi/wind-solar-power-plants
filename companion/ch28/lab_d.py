"""Chapter 28, lab D (worked example): the study-input checklist and the
compliance matrix for Plant P's proposed POC, with the gaps each one
leaves, the assumption log and the approval boundaries.

Run from the project root:   python -m companion.ch28.lab_d
Writes companion/ch28/expected/d_*.txt.
Requirements are placeholders for the operator's code (U-102).
"""
from __future__ import annotations

from collections import Counter

from companion.ch28 import register as reg
from companion.ch28.common import emit

LETTER = {"B": "B", "C": "C", "E": "E", "F": "F", "G": "G"}


def checklist() -> None:
    lines = ["study-input checklist for the POC (owner, status, quality A/B/C)",
             "  id     item                                 owner     status    q  for"]
    for iid, item, owner, status, q, use in reg.INPUTS:
        lines.append(f"  {iid}  {item:36s} {owner:9s} {status:9s} {q:1s}  {use}")
    c = Counter(i[3] for i in reg.INPUTS)
    lines += [f"  {c['received']} received, {c['requested']} requested, {c['assumed']} assumed,"
              f" {c['missing']} missing of {len(reg.INPUTS)}",
              "  quality: A measured or certified, B declared by the owner,",
              "  C assumed by the study team - a C input carries an entry",
              "  in the assumption log"]
    emit("d_checklist", lines)


# [start: blocked]
def blocked_by(req: reg.Requirement) -> list[str]:
    """Inputs not yet received that the requirement's studies need."""
    letters = {s.split("-")[0] for s in req.study.split(", ")}
    out = []
    for iid, _, _, status, _, use in reg.INPUTS:
        if status in ("missing", "requested") and \
                (letters & set(use.split()) or "all" in use.split()):
            out.append(iid)
    return out
# [end: blocked]


def matrix() -> None:
    lines = ["compliance matrix: requirement -> study -> model -> test -> evidence",
             "  req      topic                                study          test  evid  in"]
    gaps = []
    for r in reg.REQUIREMENTS:
        b = blocked_by(r)
        lines.append(f"  {r.rid}  {r.topic:36s} {r.study.split(',')[0][:13]:13s}  "
                     f"{'yes' if r.test else ' - ':4s}  {'yes' if r.evidence else ' - ':4s}  {len(b)}")
        if not r.test and not r.evidence:
            gaps.append(f"{r.rid}: neither test nor evidence named")
        elif not r.test:
            gaps.append(f"{r.rid}: closed by {r.evidence}")
    n_more = sum(1 for r in reg.REQUIREMENTS if set(blocked_by(r)) - {"IN-10"})
    lines += [f"  {len(reg.REQUIREMENTS)} requirements: all wait for IN-10 (the code itself);",
              f"  {n_more} also wait for other inputs ('in' counts open inputs)",
              "  requirements without a site test:"] + ["    " + g for g in gaps]
    emit("d_matrix", lines)


def assumptions() -> None:
    log = [("A-341", "minimum POC strength 900 MVA, X/R 6", "B-sc, C-vcontrol, E-weak"),
           ("A-342", "unit transformers uk 6 %, 9 kW/MVA", "B-losses, B-reactive"),
           ("A-343", "ride-through case 0.20 pu for 150 ms", "C-frt"),
           ("A-344", "frequency event systems and droops", "C-freq"),
           ("A-345", "line weather model (rates of ch 18)", "G-contingency, G-line"),
           ("A-346", "zero-sequence ratios (grid 1.5, line 3)", "B-earth"),
           ("A-347", "connection options, locus, emissions", "G-alternatives, B-locus"),
           ("A-348", "values of the later lessons", "C, F, G (several)"),
           ("TA-01", "frequency ranges (IN-05 assumed)", "C-freq, REQ-G08"),
           ("TA-02", "plant element outage rates (IN-30)", "G-contingency"),
           ("TA-03", "line impedance calculated, not measured", "B, G (sensitivity)")]
    lines = ["assumption log of the study (each with the results it can change)",
             "  id      assumption                                 affects"]
    for aid, text, eff in log:
        lines.append(f"  {aid:6s}  {text:42s} {eff}")
    lines += ["  an assumption is closed by evidence (data received or",
              "  measured) and the affected studies are rerun or shown",
              "  insensitive - the log is part of the submission"]
    emit("d_assumptions", lines)


def approvals() -> None:
    lines = ["approval boundaries of the study (who prepares, reviews, approves)",
             "  item                       prepares             approves"]
    for item, prep, _, appr in reg.APPROVALS:
        lines.append(f"  {item:26s} {prep:20s} {appr}")
    lines += ["  the operator owns the network model and the code; the OEM",
              "  owns its models; the plant owns its data and the study;",
              "  no one approves their own work - an independent checker",
              "  and a licensed engineer sign the results"]
    emit("d_approvals", lines)


if __name__ == "__main__":
    checklist()
    matrix()
    assumptions()
    approvals()
