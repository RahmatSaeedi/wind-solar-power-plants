"""Chapter 38, four more lessons on design data: a checker for the wording
of requirements, the difference between two revisions of a cable schedule
with the check that every change carries a revision note, an audit of
the common data environment's publishing log against its permissions,
and transmittals reconciled with the document register.

Run from the project root:   python -m companion.ch38.examples_t
Writes companion/ch38/expected/t_*.txt.
Synthetic teaching records (A-424).
"""
from __future__ import annotations

import re

from companion.ch38 import sources as src  # noqa: F401  (plantp on path)
from companion.ch38.common import emit

# ------------------------------------------------- requirement wording
# [start: wording]
VAGUE = ["adequate", "as required", "if possible", "approximately",
         "etc", "user-friendly", "sufficient", "as appropriate"]
UNIT = re.compile(r"\d[\d.,]*\s*(%|MW|MVAr|kV|ms|s|h|A|dB|years?|m3)\b")


def wording(text: str) -> list[str]:
    """Problems in one requirement statement."""
    t = text.lower()
    out = [f"vague: '{w}'" for w in VAGUE if re.search(rf"\b{w}\b", t)]
    if t.count(" shall ") > 1:
        out.append(f"{t.count(' shall ')} requirements in one")
    if re.search(r"\d", t) and not UNIT.search(text):
        out.append("number without a unit")
    if " shall " not in f" {t} ":
        out.append("no 'shall': a wish, not a requirement")
    return out
# [end: wording]


STATEMENTS = [  # (id, text) - synthetic, A-424
    ("R-01", "The plant shall limit export at the POC to 100 MW."),
    ("R-02", "The auxiliary supply shall be adequate for operation."),
    ("R-03", "Protection shall clear MV faults within 120 ms."),
    ("R-04", "The SCADA should store data for 10."),
    ("R-05", "The BESS area shall have fire detection, and the inverter"
     " rooms shall be ventilated, and lighting shall be provided."),
    ("R-06", "Noise at the camp shall be approximately 45 dB."),
    ("R-07", "Earthing shall limit touch voltage as required."),
    ("R-08", "The control system shall keep time to 1 ms."),
    ("R-09", "The skid shall be user-friendly to maintain."),
    ("R-10", "Water use shall stay within the permitted 6,000 m3 a year."),
]


def requirements_check() -> dict[str, list[str]]:
    lines = ["wording of ten requirement statements"]
    out = {}
    for rid, text in STATEMENTS:
        probs = wording(text)
        out[rid] = probs
        lines.append(f"  {rid}  {'ok' if not probs else '; '.join(probs)}")
    bad = [r for r, p in out.items() if p]
    lines += [f"  statements with a problem: {len(bad)} of {len(STATEMENTS)}",
              "  a requirement that cannot be verified cannot be closed in",
              "  the RVTM: 'adequate' has no test; 'approximately 45 dB'",
              "  has no limit; three 'shall's in one line need three IDs"]
    emit("t_wording", lines)
    return out


# --------------------------------------------- revision diff of a schedule
REV1 = {  # cable schedule PLP-ELE-LST-0005 rev 1 (part): tag -> (mm2, km)
    "=PVF2-W1": (240, 0.90), "=PVF2-W2": (240, 1.10),
    "=PVF2-W3": (185, 0.70), "=WS1-W1": (300, 2.40), "=WS1-W2": (300, 1.80),
}
REV2 = {  # rev 2 as issued
    "=PVF2-W1": (240, 0.90), "=PVF2-W2": (300, 1.10),
    "=PVF2-W3": (185, 0.75), "=WS1-W1": (300, 2.40), "=WS3-W1": (300, 2.10),
}
NOTES2 = {"=PVF2-W2": "C-021 larger section after the cable study",
          "=WS3-W1": "C-022 feeder WS3 added"}


def diff(a: dict, b: dict) -> list[tuple[str, str]]:
    out = []
    for tag in sorted(set(a) | set(b)):
        if tag not in b:
            out.append((tag, "removed"))
        elif tag not in a:
            out.append((tag, "added"))
        elif a[tag] != b[tag]:
            out.append((tag, f"{a[tag][0]} mm2 {a[tag][1]:.2f} km -> "
                             f"{b[tag][0]} mm2 {b[tag][1]:.2f} km"))
    return out


def revision_diff() -> list[tuple[str, str]]:
    changes = diff(REV1, REV2)
    lines = ["cable schedule rev 1 -> rev 2: every change and its note"]
    unnoted = []
    for tag, what in changes:
        note = NOTES2.get(tag)
        if not note:
            unnoted.append(tag)
        lines += [f"  {tag:9s} {what}", f"      note: {note or 'NONE'}"]
    lines += [f"  changes {len(changes)}; without a revision note: "
              f"{', '.join(unnoted)}",
              "  a silent change is the dangerous one: =PVF2-W3 grew by",
              "  50 m and =WS1-W2 vanished, and no reader of the revision",
              "  table would know; the diff is run before every issue"]
    emit("t_diff", lines)
    return changes


# ------------------------------------------------------ CDE permissions
PERMIT = {  # role: actions allowed (A-424)
    "author": {"edit WIP", "share"},
    "checker": {"comment", "share"},
    "approver": {"approve", "publish"},
    "document controller": {"publish", "archive"},
}
LOG = [  # (who, role, action, document)
    ("user 1", "author", "share", "PLP-ELE-DWG-0012"),
    ("user 2", "approver", "approve", "PLP-ELE-DWG-0012"),
    ("user 3", "document controller", "publish", "PLP-ELE-DWG-0012"),
    ("user 1", "author", "publish", "PLP-ELE-CAL-0009"),
    ("user 4", "checker", "approve", "PLP-CIV-DWG-0031"),
    ("user 3", "document controller", "publish", "PLP-CIV-DWG-0031"),
    ("user 2", "approver", "approve", "PLP-CTL-SPC-0002"),
    ("user 2", "approver", "publish", "PLP-CTL-SPC-0002"),
]


def cde_audit() -> list[tuple]:
    bad = [e for e in LOG if e[2] not in PERMIT[e[1]]]
    approved = {e[3] for e in LOG if e[2] == "approve" and e not in bad}
    no_appr = [e for e in LOG if e[2] == "publish" and e[3] not in approved]
    lines = [f"publishing log of the CDE: {len(LOG)} actions"]
    for who, role, act, doc in bad:
        lines.append(f"  not permitted: {role} '{act}' on {doc}")
    for who, role, act, doc in no_appr:
        lines.append(f"  published without a valid approval: {doc}")
    lines += ["  the check is of roles, not of people: an author cannot",
              "  publish and a checker cannot approve - otherwise the",
              "  'approved' status means nothing"]
    emit("t_cde", lines)
    return bad + no_appr


# ------------------------------------------------- transmittals
SENT = {  # transmittal: documents and the status written on it
    "TR-0141": {"PLP-ELE-DWG-0012": "IFC", "PLP-ELE-CAL-0009": "IFA"},
    "TR-0142": {"PLP-CIV-DWG-0031": "IFC", "PLP-CTL-SPC-0002": "IFC"},
    "TR-0143": {"PLP-MEC-DWG-0004": "IFR"},
}
REGISTER = {"PLP-ELE-DWG-0012": "IFC", "PLP-ELE-CAL-0009": "IFR",
            "PLP-CIV-DWG-0031": "APP", "PLP-CTL-SPC-0002": "IFC",
            "PLP-MEC-DWG-0004": "IFR"}


def transmittals() -> list[tuple]:
    out = []
    for tr, docs in SENT.items():
        for d, st in docs.items():
            if REGISTER.get(d) != st:
                out.append((tr, d, st, REGISTER.get(d)))
    lines = ["transmittals reconciled with the register"]
    for tr, d, st, reg in out:
        lines.append(f"  {tr}  {d}: sent as {st}, register says {reg}")
    lines += [f"  mismatches: {len(out)} of "
              f"{sum(len(v) for v in SENT.values())}",
              "  the contractor builds from what was sent: a drawing sent",
              "  'IFC' while the register says 'APP' may be built before",
              "  it is issued - the register and the transmittal are",
              "  reconciled weekly, and the transmittal is corrected"]
    emit("t_transmit", lines)
    return out


if __name__ == "__main__":
    requirements_check()
    revision_diff()
    cde_audit()
    transmittals()
