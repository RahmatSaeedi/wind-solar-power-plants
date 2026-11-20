"""Engineering records for Plant P: document numbers, revisions, status codes,
calculation sheets, comment-resolution sheets and fingerprints (chapter 2).

    from plantp import records as rec
    rec.doc_number("GEN", "CAL", 2)          # 'PLP-GEN-CAL-0002'
    rec.next_revision("B")                   # 'C'   (pre-approval revisions are letters)
    rec.next_revision("B", approve=True)     # '0'   (first approved issue)
    sheet = rec.CalcSheet(...); print("\n".join(sheet.render()))

The numbering and status scheme is the BOOK'S TEACHING CONVENTION for Plant P. Real
projects define their own in a document-control procedure agreed between owner and
contractors; the ideas (unique number, revision, status, traceable inputs, independent
check) are what carries over.
"""
from __future__ import annotations

import hashlib
import json
import re
import textwrap
from dataclasses import asdict, dataclass, field
from pathlib import Path

PROJECT = "PLP"
DISCIPLINES = {
    "GEN": "general / multidisciplinary",
    "ELE": "electrical",
    "CIV": "civil and structural",
    "MEC": "mechanical",
    "CTL": "control and communications",
    "ENV": "environment and social",
    "PRJ": "project management",
}
DOC_TYPES = {
    "CAL": "calculation",
    "DWG": "drawing",
    "SPC": "specification",
    "REP": "report",
    "REG": "register",
    "PRO": "procedure",
    "LST": "list or schedule",
}
#: Plant P status codes and the transitions the procedure allows
STATUS = {
    "WIP": "work in progress (not for use)",
    "IFR": "issued for review",
    "IFI": "issued for information",
    "IFA": "issued for approval",
    "APP": "approved",
    "IFC": "issued for construction",
    "ASB": "as built",
    "SUP": "superseded",
    "VOID": "withdrawn",
}
TRANSITIONS = {
    "WIP": {"IFR", "IFI", "VOID"},
    "IFR": {"WIP", "IFA", "IFI", "VOID"},
    "IFI": {"WIP", "IFR", "SUP", "VOID"},
    "IFA": {"WIP", "APP", "VOID"},
    "APP": {"IFC", "SUP", "VOID"},
    "IFC": {"ASB", "SUP"},
    "ASB": {"SUP"},
    "SUP": set(),
    "VOID": set(),
}
#: evidence status of every input (the hierarchy of chapter 1)
EVIDENCE = ("synthetic", "assumed", "measured", "vendor", "verified")

_DOC_RE = re.compile(rf"^{PROJECT}-([A-Z]{{3}})-([A-Z]{{3}})-(\d{{4}})$")


def doc_number(discipline: str, doc_type: str, seq: int) -> str:
    """Unique Plant P document number, e.g. PLP-ELE-CAL-0012."""
    if discipline not in DISCIPLINES:
        raise ValueError(f"unknown discipline {discipline!r}")
    if doc_type not in DOC_TYPES:
        raise ValueError(f"unknown document type {doc_type!r}")
    if not 1 <= seq <= 9999:
        raise ValueError("sequence number must be 1..9999")
    return f"{PROJECT}-{discipline}-{doc_type}-{seq:04d}"


def parse_doc_number(number: str) -> tuple[str, str, int]:
    match = _DOC_RE.match(number)
    if not match or match.group(1) not in DISCIPLINES or match.group(2) not in DOC_TYPES:
        raise ValueError(f"{number!r} is not a valid Plant P document number")
    return match.group(1), match.group(2), int(match.group(3))


def next_revision(rev: str | None, approve: bool = False) -> str:
    """Next revision code. Drafts before the first approval are A, B, ..., Z, AA, ...;
    the first approved issue is 0 and later approved issues 1, 2, ...

    next_revision(None) -> 'A'; next_revision('C') -> 'D';
    next_revision('C', approve=True) -> '0'; next_revision('0') -> '1'
    """
    if rev is None:
        return "0" if approve else "A"
    if rev.isdigit():
        return str(int(rev) + 1)
    if not re.fullmatch(r"[A-Z]+", rev):
        raise ValueError(f"invalid revision {rev!r}")
    if approve:
        return "0"
    letters = list(rev)
    i = len(letters) - 1
    while i >= 0 and letters[i] == "Z":
        letters[i] = "A"
        i -= 1
    if i < 0:
        return "A" + "".join(letters)
    letters[i] = chr(ord(letters[i]) + 1)
    return "".join(letters)


def check_transition(old: str, new: str) -> None:
    """Raise ValueError if the document procedure does not allow old -> new."""
    if old not in STATUS or new not in STATUS:
        raise ValueError(f"unknown status in {old!r} -> {new!r}")
    if new not in TRANSITIONS[old]:
        raise ValueError(f"status change {old} -> {new} is not allowed")


# ---- fingerprints ------------------------------------------------------------------
def file_sha256(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_json(data) -> str:
    """Stable text of a data structure: sorted keys, no spaces, floats as repr."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(data) -> str:
    """SHA-256 of the canonical JSON text: identical inputs give identical digests."""
    return hashlib.sha256(canonical_json(data).encode("ascii")).hexdigest()


# ---- calculation sheet ---------------------------------------------------------------
@dataclass
class Input:
    id: str
    name: str
    value: float | str
    unit: str
    status: str          # one of EVIDENCE
    source: str          # where it comes from: file, document, data sheet, register id

    def __post_init__(self):
        if self.status not in EVIDENCE:
            raise ValueError(f"input {self.id}: status must be one of {EVIDENCE}")
        if not self.source:
            raise ValueError(f"input {self.id}: every input needs a source")


@dataclass
class Comment:
    id: str
    by: str
    location: str
    text: str
    category: str        # "major", "minor", "editorial" or "question"
    response: str = ""
    status: str = "open"  # "open", "closed" or "hold"

    def __post_init__(self):
        if self.category not in ("major", "minor", "editorial", "question"):
            raise ValueError(f"comment {self.id}: unknown category {self.category!r}")
        if self.status not in ("open", "closed", "hold"):
            raise ValueError(f"comment {self.id}: unknown status {self.status!r}")


@dataclass
class Revision:
    rev: str
    date: str            # ISO 8601, YYYY-MM-DD
    status: str
    description: str
    prepared: str
    checked: str = ""
    approved: str = ""


@dataclass
class CalcSheet:
    number: str
    title: str
    purpose: str
    revisions: list[Revision]
    inputs: list[Input]
    method: list[str]
    results: list[tuple[str, str]]          # (description, value with unit)
    checks: list[tuple[str, str, str]]       # (check, result, verdict)
    limitations: list[str] = field(default_factory=list)
    comments: list[Comment] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    file_digests: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        parse_doc_number(self.number)
        ids = [i.id for i in self.inputs]
        if len(ids) != len(set(ids)):
            raise ValueError("input ids must be unique")
        if not self.revisions:
            raise ValueError("a calculation sheet needs at least one revision")
        for older, newer in zip(self.revisions, self.revisions[1:]):
            if older.rev == newer.rev:          # same revision re-issued: status must move legally
                check_transition(older.status, newer.status)

    @property
    def current(self) -> Revision:
        return self.revisions[-1]

    def inputs_digest(self) -> str:
        return digest([asdict(i) for i in self.inputs])

    def open_comments(self) -> list[Comment]:
        return [c for c in self.comments if c.status != "closed"]

    def render(self, width: int = 78) -> list[str]:
        """The calculation record as plain text, every line at most `width` characters."""
        rule = "=" * width
        out: list[str] = []

        def para(text: str, indent: str = "", sub: str = "    "):
            out.extend(textwrap.wrap(text, width, initial_indent=indent,
                                     subsequent_indent=indent + sub) or [""])

        cur = self.current
        out += [rule, f"{self.number}  Rev {cur.rev}  status {cur.status} "
                      f"({STATUS[cur.status]})"]
        para(self.title)
        out.append(rule)
        para("Purpose: " + self.purpose)
        out.append("")
        out.append("Revision history")
        for r in self.revisions:
            para(f"{r.rev:>2}  {r.date}  {r.status:4s} {r.description}; prepared {r.prepared}"
                 + (f", checked {r.checked}" if r.checked else "")
                 + (f", approved {r.approved}" if r.approved else ""), "  ")
        out.append("")
        out.append("Inputs (id, quantity, value, status, source)")
        for i in self.inputs:
            para(f"{i.id:5s} {i.name} = {i.value} {i.unit} [{i.status}] <- {i.source}", "  ")
        out.append(f"  inputs digest (SHA-256) {self.inputs_digest()[:16]}...")
        for name, h in self.file_digests.items():
            para(f"file {name} sha256 {h[:16]}...", "  ")
        out.append("")
        out.append("Method")
        for k, step in enumerate(self.method, 1):
            para(f"{k}. {step}", "  ")
        out.append("")
        out.append("Results")
        for desc, val in self.results:
            para(f"{desc}: {val}", "  ")
        out.append("")
        out.append("Checks")
        for chk, res, verdict in self.checks:
            para(f"[{verdict}] {chk}: {res}", "  ")
        if self.limitations:
            out.append("")
            out.append("Limitations")
            for lim in self.limitations:
                para("- " + lim, "  ")
        if self.comments:
            out.append("")
            out.append("Review comments (id, by, category, status)")
            for c in self.comments:
                para(f"{c.id} {c.by} {c.category} {c.status.upper()}: {c.text}", "  ")
                if c.response:
                    para("response: " + c.response, "      ")
        if self.references:
            out.append("")
            out.append("References")
            for ref in self.references:
                para("- " + ref, "  ")
        out.append(rule)
        return out
