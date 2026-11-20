"""Chapter 5, section E - asset-information laboratory.

    E1 the register: hierarchy, tags, criticality (rev A, released at handover)
    E2 validate rev B; E3 reconcile rev B with the approved change notice
    E4 controlled export to a mock CMMS and import back: what is lost
    E5 linked records in a small database: tests, warranties, work orders
Run from the project root:   python -m companion.ch05.lab_e
All records are synthetic (A-094, A-095); vendors are placeholders.
"""
from __future__ import annotations

import csv
import hashlib
import io
import sqlite3
from collections import Counter

from companion.ch05.common import HERE, emit
from plantp import assets, datapack


def e1_register() -> list[dict]:
    reg = datapack.load_register("A")
    systems = Counter(r["tag"].split("-")[1] for r in reg)
    depth = Counter(r["tag"].count("-") - 1 for r in reg)
    crit = Counter(r["criticality"] for r in reg)
    children = Counter(r["parent"] for r in reg if r["parent"])
    emit("e_register", [
        f"register rev A: {len(reg)} records, validation issues: "
        f"{len(assets.validate_register(reg))}",
        "  by system: " + ", ".join(f"{k} {v}" for k, v in sorted(systems.items())),
        f"  levels: plant 1, system-level items {depth[1] - 1}, components {depth[2]}",
        "  criticality: " + ", ".join(f"{k} {v}" for k, v in sorted(crit.items())),
        f"  most children: {children.most_common(1)[0][0]} with {children.most_common(1)[0][1]}",
        "tag = PLP-<system>-<nn>[-<component>], e.g. PLP-WTG-07-GEN (teaching scheme, A-094)",
    ])
    return reg


def e2_validate() -> list[dict]:
    reg_b = datapack.load_register("B")
    issues = assets.validate_register(reg_b)
    emit("e_validate", [f"register rev B: {len(reg_b)} records, {len(issues)} issue(s):"]
         + [f"  {i}" for i in issues])
    return reg_b


def e3_reconcile(reg_a, reg_b) -> None:
    notice = datapack.load_change_notice()
    r = assets.reconcile(reg_a, reg_b, notice)
    lines = [f"change notices CN-001..CN-005: {len(notice)} approved line(s)"]
    for key in ("approved", "unapproved", "not_done"):
        lines.append(f"{key} ({len(r[key])}):")
        for x in r[key]:
            if not x.isascii():                       # keep code blocks left-to-right
                x = x.split(" '")[0] + " changed (Persian text, letter forms)"
            lines.append(f"  {x}" if len(x) < 74 else f"  {x[:70]}...")
    lines.append("the duplicated PLP-INV-07 does not appear in the diff (keyed by tag):")
    lines.append("  validate BEFORE comparing")
    emit("e_reconcile", lines)


def e4_cmms(reg_a) -> None:
    out = assets.to_cmms(reg_a)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(out[0]), lineterminator="\n")
    w.writeheader()
    w.writerows(out)
    text = buf.getvalue()
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    (HERE / "output").mkdir(exist_ok=True)
    (HERE / "output" / "cmms_export_rev_A.csv").write_text(text, encoding="utf-8")
    back = assets.from_cmms(list(csv.DictReader(io.StringIO(text))))
    unmapped = sorted(set(reg_a[0]) - set(assets.CMMS_MAP))
    cut = [a["tag"] for a, b in zip(reg_a, back) if a["description"] != b["description"]]
    same = sum(1 for a, b in zip(reg_a, back)
               if all(a[k] == b[k] for k in assets.CMMS_MAP))
    emit("e_cmms", [
        f"export: {len(out)} rows, {len(out[0])} fields, SHA-256 {digest[:24]}...",
        f"  record count in = out: {len(reg_a) == len(out)}; tags unique: "
        f"{len({r['FUNC_LOC'] for r in out}) == len(out)}",
        f"fields with no place in the CMMS (kept only in the register): {unmapped}",
        f"descriptions cut to 40 characters: {len(cut)}, e.g. {cut[0]}, {cut[-1]}",
        f"round trip: {same} of {len(reg_a)} records identical in the mapped fields",
        "decision needed from the information owner: shorten texts at the source,",
        "  or keep the long text in the register and link it (no silent truncation)",
    ])


def e5_links(reg_a) -> None:
    db = sqlite3.connect(":memory:")
    db.executescript("""
        CREATE TABLE asset (tag TEXT PRIMARY KEY, parent TEXT, serial TEXT, commissioned TEXT);
        CREATE TABLE document (doc TEXT, tag TEXT REFERENCES asset(tag), kind TEXT);
        CREATE TABLE warranty (tag TEXT REFERENCES asset(tag), start TEXT, years INTEGER);
        CREATE TABLE work_order (wo TEXT PRIMARY KEY, tag TEXT REFERENCES asset(tag),
                                 opened TEXT, closed TEXT, text TEXT);
    """)
    db.executemany("INSERT INTO asset VALUES (?,?,?,?)",
                   [(r["tag"], r["parent"], r["serial"], r["commissioned"]) for r in reg_a])
    years = {"GEN": 5, "GBX": 5, "TRF": 2, "INV": 5}
    rows = []
    for r in reg_a:
        part = r["tag"].split("-")[-1] if r["tag"].count("-") == 3 else r["tag"].split("-")[1]
        if part in years and r["commissioned"]:
            rows.append((r["tag"], r["commissioned"], years[part]))
    db.executemany("INSERT INTO warranty VALUES (?,?,?)", rows)
    db.executemany("INSERT INTO document VALUES (?,?,?)",
                   [("PLP-ELE-REP-0101", "PLP-TRF-01", "factory test report"),
                    ("PLP-ELE-REP-0102", "PLP-SWG-01", "factory test report"),
                    ("PLP-MEC-REP-0201", "PLP-WTG-07-GEN", "inspection report")])
    db.executemany("INSERT INTO work_order VALUES (?,?,?,?,?)",
                   [("WO-0012", "PLP-WTG-07-GEN", "2026-01-20", "2026-03-15",
                     "bearing noise; generator exchanged (CN-001)"),
                    ("WO-0019", "PLP-INV-04", "2026-02-02", None, "fan alarm")])
    expiring = db.execute(
        "SELECT tag, date(start, '+' || years || ' years') AS ends FROM warranty "
        "WHERE ends <= '2027-12-31' ORDER BY ends, tag").fetchall()
    open_wo = db.execute("SELECT wo, tag, text FROM work_order WHERE closed IS NULL").fetchall()
    no_doc = db.execute(
        "SELECT count(*) FROM asset a WHERE a.tag LIKE '%TRF%' AND NOT EXISTS "
        "(SELECT 1 FROM document d WHERE d.tag = a.tag)").fetchone()[0]
    in_warranty = db.execute(
        "SELECT w.tag FROM work_order o JOIN warranty w ON o.tag = w.tag "
        "WHERE o.opened <= date(w.start, '+' || w.years || ' years')").fetchall()
    emit("e_links", [
        f"warranties ending by 2027-12-31: {len(expiring)} "
        f"(first {expiring[0][0]} on {expiring[0][1]})",
        f"open work orders: {open_wo}",
        f"transformers without a linked test document: {no_doc} of 13 "
        "(the turbine transformers: documents never received?)",
        f"work orders opened inside a warranty period: {[t for (t,) in in_warranty]}",
        "  -> claim against the supplier is possible only if the link tag -> serial ->",
        "     warranty -> work order is complete and trustworthy",
    ])


if __name__ == "__main__":
    a = e1_register()
    b = e2_validate()
    e3_reconcile(a, b)
    e4_cmms(a)
    e5_links(a)
