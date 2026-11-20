"""A synthetic asset register for Plant P, chapter 5 (again in 38, 49-53).

    TAG_PATTERN        PLP-<system>-<nn>[-<component>], e.g. PLP-WTG-07-GEN
    validate_register  unique tags, known parents, required fields, dates
    diff_registers     what changed between two revisions of the register
    reconcile          a revision checked against the approved change notice
    to_cmms, from_cmms a controlled export/import to a mock maintenance system

Records are dictionaries with keys: tag, parent, description,
description_fa, vendor, model, serial, location, delivered, installed,
commissioned (ISO dates or empty), criticality (A, B or C), doc_ref.
The tag scheme is a teaching convention, not a published designation
standard.
"""
from __future__ import annotations

import re
import unicodedata
from datetime import date

#: Arabic letters that look like Persian ones but are other code points
ARABIC_LOOKALIKES = {"ي": "ی", "ك": "ک",
                     "ى": "ی"}


def normalise_persian(text: str) -> str:
    """NFC form; Arabic yeh, kaf and alef maksura -> Persian letters."""
    text = unicodedata.normalize("NFC", text)
    return "".join(ARABIC_LOOKALIKES.get(ch, ch) for ch in text)


# [start: tags]
SYSTEMS = {"PLT": "plant", "WTG": "wind turbine", "PVB": "PV block",
           "INV": "inverter", "TRF": "transformer", "SWG": "switchgear",
           "BES": "battery system", "MET": "met mast", "SUB": "substation"}
TAG_PATTERN = re.compile(
    r"^PLP-(PLT|WTG|PVB|INV|TRF|SWG|BES|MET|SUB)-\d{2}(-[A-Z]{3})?$")
REQUIRED = ("tag", "description", "criticality")
DATES = ("delivered", "installed", "commissioned")
# [end: tags]


def _date(text):
    return date.fromisoformat(text) if text else None


# [start: validate]
def validate_register(records: list[dict]) -> list[str]:
    """Every problem of the register, one short text each."""
    issues: list[str] = []
    seen = set()
    for r in records:
        if r.get("tag", "") in seen:
            issues.append(f"{r['tag']}: duplicate tag")
        seen.add(r.get("tag", ""))
    for r in records:
        t = r.get("tag", "")
        for key in REQUIRED:
            if not r.get(key):
                issues.append(f"{t or '?'}: {key} is missing")
        if t and not TAG_PATTERN.match(t):
            issues.append(f"{t}: tag does not follow PLP-<sys>-<nn>[-<XXX>]")
        parent = r.get("parent", "")
        if parent and parent not in seen:
            issues.append(f"{t}: parent {parent} not in the register")
        if not parent and not t.startswith("PLP-PLT"):
            issues.append(f"{t}: only the plant may have no parent")
        crit = r.get("criticality")
        if crit and crit not in ("A", "B", "C"):
            issues.append(f"{t}: criticality {crit!r} is not A, B or C")
        try:
            d = [_date(r.get(k, "")) for k in DATES]
        except ValueError as e:
            issues.append(f"{t}: bad date ({e})")
            continue
        known = [(k, v) for k, v in zip(DATES, d) if v]
        for (k1, v1), (k2, v2) in zip(known[:-1], known[1:]):
            if v2 < v1:
                issues.append(f"{t}: {k2} {v2} is before {k1} {v1}")
        component = t.count("-") == 3
        if component and r.get("commissioned") and not r.get("serial"):
            issues.append(f"{t}: commissioned component without a serial "
                          "number")
        fa = r.get("description_fa", "")
        if fa and fa != normalise_persian(fa):
            issues.append(f"{t}: Arabic letter form in the Persian "
                          "description")
    return issues
# [end: validate]


def diff_registers(old: list[dict], new: list[dict]) -> dict:
    """{'added': [...], 'removed': [...], 'changed': {tag: {field: (a, b)}}}"""
    a = {r["tag"]: r for r in old}
    b = {r["tag"]: r for r in new}
    changed = {}
    for t in sorted(set(a) & set(b)):
        keys = set(a[t]) | set(b[t])
        fields = {k: (a[t].get(k, ""), b[t].get(k, "")) for k in keys
                  if a[t].get(k, "") != b[t].get(k, "")}
        if fields:
            changed[t] = dict(sorted(fields.items()))
    return {"added": sorted(set(b) - set(a)),
            "removed": sorted(set(a) - set(b)), "changed": changed}


# [start: reconcile]
def reconcile(old: list[dict], new: list[dict], notice: list[dict]) -> dict:
    """Compare a register revision with the approved change notice.

    A change is approved when the notice names the tag and the field (or
    '(added)' / '(removed)') and, for a field, exactly the new value."""
    d = diff_registers(old, new)
    want = {(n["tag"], n["field"]): n["new_value"] for n in notice}
    approved, unapproved, done = [], [], set()
    for kind, tags in (("(added)", d["added"]), ("(removed)", d["removed"])):
        for t in tags:
            ok = (t, kind) in want
            (approved if ok else unapproved).append(f"{t}: {kind[1:-1]}")
            done.add((t, kind))
    for t, fields in d["changed"].items():
        for f, (a, b) in fields.items():
            ok = want.get((t, f)) == b
            (approved if ok else unapproved).append(f"{t}: {f} {a!r} -> {b!r}")
            done.add((t, f))
    not_done = [f"{t}: {f}" for (t, f) in want if (t, f) not in done]
    return {"approved": approved, "unapproved": unapproved,
            "not_done": not_done}
# [end: reconcile]


CMMS_MAP = {"tag": "FUNC_LOC", "parent": "SUPERIOR", "description": "TEXT",
            "vendor": "MANUF", "model": "MODEL_NO", "serial": "SERIAL_NO",
            "commissioned": "START_UP", "criticality": "ABC_IND"}


def to_cmms(records: list[dict]) -> list[dict]:
    """Rename fields for the mock CMMS; TEXT is cut to its 40 characters."""
    out = []
    for r in records:
        row = {CMMS_MAP[k]: r.get(k, "") for k in CMMS_MAP}
        row["TEXT"] = row["TEXT"][:40]
        out.append(row)
    return out


def from_cmms(rows: list[dict]) -> list[dict]:
    back = {v: k for k, v in CMMS_MAP.items()}
    return [{back[k]: v for k, v in row.items()} for row in rows]
