"""Standards-register helpers (chapter 58).

Reading a project standards register (the book's own
glossary/standards-register.csv), checking that every row has the fields
a register needs, finding open items, grouping by the topics of the
handoff, reading editions and ages, resolving dated and undated
references, sorting the verbal forms of a clause, and checking a test
laboratory's accredited scope. Teaching helpers on plain data: they read
titles, editions and statuses - never the text of a standard.
"""
from __future__ import annotations

import csv
import re
from datetime import date

# [start: fields]
REQUIRED = ("designation", "title", "issuing_body", "edition",
            "adoption_or_legal_status", "official_source", "discipline",
            "applicability_in_book", "date_verified")


def load(path) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def completeness(rows: list[dict], fields=REQUIRED) -> dict:
    """Missing (empty) values per field, and the ids of incomplete rows."""
    missing = {f: 0 for f in fields}
    bad = []
    for r in rows:
        gaps = [f for f in fields if not (r.get(f) or "").strip()]
        for f in gaps:
            missing[f] += 1
        if gaps:
            bad.append(r.get("id", "?"))
    return dict(missing=missing, incomplete=bad)
# [end: fields]


def open_items(rows: list[dict], words=("confirm",)) -> list[str]:
    """Rows whose edition, status or note still asks for a check."""
    out = []
    for r in rows:
        text = " ".join((r.get(k) or "") for k in
                        ("edition", "adoption_or_legal_status", "note")).lower()
        if any(w in text for w in words):
            out.append(r["id"])
    return out


# [start: topics]
TOPICS = [   # (topic, keywords); first match wins
    ("PV", ("pv", "photovoltaic", "solar")),
    ("wind", ("wind", "61400", "iecre")),
    ("inverters", ("inverter", "power conversion",
                   "power electronics", "62109", "converter")),
    ("transformers", ("transformer", "60076")),
    ("switchgear", ("switchgear", "lv assemblies", "enclosure",
                    "62271", "61439", "installations (substations)")),
    ("protection", ("overcurrent", "short circuit", "60255",
                    "dc power systems")),
    ("grounding", ("earthing", "grounding", "lightning")),
    ("power quality", ("power quality", "harmonic", "flicker", "61000",
                       "voltages", "grid connection", "grid studies")),
    ("communications", ("communication", "telecontrol", "61850",
                        "60870", "cyber", "data", "modbus", "dnp",
                        "time", "network", "62443")),
    ("environment", ("environment", "life cycle", "lca", "14040",
                     "14044", "14001", "water", "safeguards",
                     "social", "carbon", "14067")),
    ("safety", ("safety", "fire", "battery", "energy storage", "(ess)",
                "emergency", "45001", "transport testing")),
    # beyond the handoff's eleven: topics the register also needs
    ("cables and substations", ("cable", "installations (substations)")),
    ("metering and instruments", ("metering", "instrument", "measuring")),
    ("quality and reliability", ("quality", "reliability", "sampling",
                                 "statistics", "non-destructive",
                                 "material testing", "laboratories",
                                 "manufacturing")),
]
HANDOFF_TOPICS = 11          # the first eleven entries are the handoff's list


def topic(row: dict) -> str:
    """Topic by the register's discipline and designation first, by the
    title only when those say nothing."""
    for fields in (("discipline", "designation"), ("title",)):
        text = " ".join((row.get(k) or "") for k in fields).lower()
        for name, keys in TOPICS:
            if any(k in text for k in keys):
                return name
    return "other"
# [end: topics]


def key(designation: str) -> str:
    """A designation reduced for comparison: case, 'Std', spaces and the
    separator before the year removed ('IEEE Std 519-2022' = 'IEEE 519:2022')."""
    d = designation.upper().replace("STD ", "").replace(" CSV", "")
    d = d.split("+")[0].replace(" ", "")      # a consolidated version is the same edition
    return re.sub(r"[-:](\d{4})$", r":\1", d)


def duplicates(rows: list[dict]) -> list[list[str]]:
    """Groups of row ids that name the same document and edition."""
    by: dict[str, list[str]] = {}
    for r in rows:
        by.setdefault(key(r["designation"]), []).append(r["id"])
    return [ids for ids in by.values() if len(ids) > 1]


def chapters(row: dict) -> set[int]:
    return {int(x) for x in re.findall(r"ch(\d\d)", row.get("applicability_in_book") or "")}


def edition_year(row: dict) -> int | None:
    """Year of the edition from the designation (':YYYY') or the edition field."""
    m = re.search(r":(\d{4})", row.get("designation") or "")
    if m:
        return int(m.group(1))
    m = re.search(r"(19|20)\d{2}", row.get("edition") or "")
    return int(m.group(0)) if m else None


# [start: resolve]
def resolve(ref: str, catalogue: dict) -> list[str]:
    """Which parts apply for a reference. catalogue: designation -> list of
    (year, part) in order, e.g. [(2023, 'IEC 62548-1:2023'),
    (2025, 'Amd 1:2025')], with editions marked 'edition'. A dated reference
    ('X:2023') takes that edition alone; an undated one ('X') the latest
    edition with every amendment issued since."""
    base, _, year = ref.partition(":")
    parts = catalogue[base]
    if year:
        return [p for y, p, kind in parts
                if kind == "edition" and y == int(year)]
    last = max(i for i, (_, _, kind) in enumerate(parts)
               if kind == "edition")
    return [p for _, p, _ in parts[last:]]
# [end: resolve]


# [start: verbal]
FORMS = [("shall not", "prohibition"), ("shall", "requirement"),
         ("should", "recommendation"), ("may", "permission"),
         ("can", "possibility")]
VAGUE = ("adequate", "suitable", "sufficient", "appropriate", "as required",
         "where necessary", "good practice")


def verbal_form(sentence: str) -> tuple[str, list[str]]:
    """The provision type of a sentence by its verbal form, and any vague
    words that make a requirement impossible to verify."""
    s = " " + sentence.lower() + " "
    kind = "statement"
    for word, name in FORMS:
        if f" {word} " in s:
            kind = name
            break
    vague = [w for w in VAGUE if w in s]
    return kind, vague
# [end: verbal]


def replaced_year(row: dict) -> int | None:
    """Year of the edition a row says it replaces ('replaces the 2016
    edition', 'Replaces ISO 9060:1990', 'replaces 485-2010'); a number that
    is part of a designation ('ISO 1940', 'EN 1997') is not a year."""
    text = (row.get("edition") or "") + "; " + (row.get("note") or "")
    m = re.search(r"replac\w*([^;,]*)", text, re.I)
    if not m:
        return None
    phrase = m.group(1)
    for y in re.finditer(r"(19|20)\d{2}", phrase):
        before = phrase[:y.start()]
        if before.endswith((":", "(", "-", "the ", " ")) and not re.search(
                r"(ISO|IEC|EN)\s*$", before):
            return int(y.group(0))
    return None


def series(designation: str) -> str | None:
    """Series of a designation: body and number ('IEC 61400-24:2019' ->
    'IEC 61400')."""
    m = re.match(r"(IEC|ISO|EN)\s+(?:TS\s+|TR\s+)?(\d{4,5})", designation)
    return f"{m.group(1)} {m.group(2)}" if m else None


# [start: clause]
def clause(equipment: str, designation: str, lab: str = "ISO/IEC 17025") -> str:
    """A dated, verifiable type-test clause for a purchase specification."""
    return (f"The {equipment} shall be type-tested to {designation} by a "
            f"laboratory accredited to {lab} with {designation} in its scope; "
            f"the report shall name the model, the edition and the date.")
# [end: clause]


def in_scope(lab_scope: list[str], needed: str) -> bool:
    """An accredited scope covers a test only for the same document and
    edition (teaching rule: a different edition needs its own extension)."""
    return needed in lab_scope


def age_years(row: dict, today: date) -> int | None:
    y = edition_year(row)
    return None if y is None else today.year - y
