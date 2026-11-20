"""Country-dossier helpers (chapters 55-57).

Facts carry a status (verified / project-dependent / to-confirm), a
source and a document date. The helpers count statuses by topic, flag
old or undated sources, review what an equipment certificate does and
does not show against a project's needs, list gaps between a grid data
pack and the inputs a study needs, and compare equipment options against
local constraints without turning an unknown into a pass. Teaching
helpers on plain data, not legal advice.
"""
from __future__ import annotations

from datetime import date

STATUSES = ("verified", "project-dependent", "to-confirm")


# [start: status]
def status_by(facts: list[dict], key: str = "topic") -> dict:
    """Count statuses per value of `key`."""
    out = {}
    for f in facts:
        row = out.setdefault(f[key], {s: 0 for s in STATUSES})
        row[f["status"]] += 1
    return out
# [end: status]


# [start: stale]
def stale(facts: list[dict], today: date, years: float = 3.0) -> list:
    """Facts whose source is undated or older than `years` on `today`:
    (id, age in years or None)."""
    out = []
    for f in facts:
        d = f.get("doc_date")
        if d is None:
            out.append((f["id"], None))
        else:
            age = (today - d).days / 365.25
            if age > years:
                out.append((f["id"], round(age, 1)))
    return out
# [end: stale]


# [start: cert]
def cert_review(cert: dict, need: dict) -> list:
    """Compare a certificate with what the project needs. Returns
    (item, 'shown' / 'NOT SHOWN' / 'differs', note) rows."""
    def mark(ok: bool, bad: str = "NOT SHOWN") -> str:
        return "shown" if ok else bad

    rows = [("model", mark(cert["model"] == need["model"], "differs"),
             f"certificate {cert['model']}, project {need['model']}"),
            ("standard and edition",
             mark(cert["standard"] == need["standard"], "differs"),
             f"certificate {cert['standard']}, project {need['standard']}")]
    for t in need["tests"]:
        rows.append((f"test: {t}", mark(t in cert["tests"]), ""))
    hot, alt = cert.get("ambient_max_c"), cert.get("altitude_m")
    valid = cert.get("valid_to")
    rows += [("site ambient",
              mark(hot is not None and hot >= need["ambient_max_c"]),
              f"tested to {hot} C, site {need['ambient_max_c']} C"),
             ("site altitude",
              mark(alt is not None and alt >= need["altitude_m"]),
              f"tested to {alt} m, site {need['altitude_m']} m"),
             ("valid on delivery",
              mark(valid is not None and valid >= need["delivery"]),
              f"valid to {valid}, delivery {need['delivery']}"),
             ("issuer accredited for the scope",
              mark(bool(cert.get("accreditation"))),
              cert.get("accreditation") or "no accreditation reference")]
    for item in need.get("plant_level", []):
        rows.append((item, "NOT SHOWN",
                     "plant level: a product certificate cannot show it"))
    return rows
# [end: cert]


# [start: gaps]
def data_gaps(provided: dict, needed: dict) -> dict:
    """needed: item -> required quality ('measured', 'model', 'value');
    provided: item -> quality given. Missing items and items given at a
    lower quality than needed (measured > model > value)."""
    order = {"value": 1, "model": 2, "measured": 3}
    missing = [i for i in needed if i not in provided]
    weak = [(i, provided[i], q) for i, q in needed.items()
            if i in provided and order[provided[i]] < order[q]]
    good = len(needed) - len(missing) - len(weak)
    return dict(missing=missing, weak=weak, complete=good / len(needed))
# [end: gaps]


# [start: compare]
def compare(options: dict, constraints: dict) -> dict:
    """options: name -> {constraint: value or None}; constraints:
    constraint -> (kind 'min'/'max', limit). A None value is 'unknown',
    never a pass. Returns per option the verdicts and the counts."""
    out = {}
    for name, vals in options.items():
        verdicts = {}
        for c, (kind, lim) in constraints.items():
            v = vals.get(c)
            if v is None:
                verdicts[c] = "unknown"
            elif (kind == "min" and v >= lim) or (kind == "max" and v <= lim):
                verdicts[c] = "ok"
            else:
                verdicts[c] = "fails"
        counts = {k: sum(1 for x in verdicts.values() if x == k)
                  for k in ("ok", "fails", "unknown")}
        out[name] = dict(verdicts=verdicts, **counts)
    return out
# [end: compare]
