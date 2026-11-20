"""Chapter 58 lessons: the book's standards register as data, verbal forms,
dated and undated references, conformity evidence and certificates, and
the traceability lab on the transformer temperature-rise requirement.

Run from the project root:   python -m companion.ch58.run
Writes companion/ch58/expected/*.txt and diagrams/data/ch58-*.csv.
"""
from __future__ import annotations

import collections
import copy
import re

import numpy as np

from companion.ch58 import common  # noqa: F401  (path)
from companion.ch58 import sources as src
from companion.ch58.common import csv, emit
from plantp import compliance, stdreg


def rows() -> list[dict]:
    return stdreg.load(src.REGISTER)


# ------------------------------------------------------------- A literacy
def register() -> dict:
    r = rows()
    c = stdreg.completeness(r)
    lines = [f"the book's standards register: {len(r)} rows, {len(stdreg.REQUIRED)}"
             " required fields each",
             "  fields: " + ", ".join(stdreg.REQUIRED[:5]) + ",",
             "          " + ", ".join(stdreg.REQUIRED[5:]),
             f"  empty required fields: {sum(c['missing'].values())};"
             f" incomplete rows: {len(c['incomplete'])}",
             "  complete is not the same as current: a filled 'edition' field",
             "  records what was verified on 'date_verified', nothing more"]
    emit("a_register", lines)
    return dict(n=len(r), c=c)


def verbal() -> dict:
    out = collections.Counter()
    lines = ["verbal forms in a teaching Plant P specification"]
    for i, s in enumerate(src.SPEC, 1):
        k, v = stdreg.verbal_form(s)
        out[k] += 1
        lines += [f"  S{i:02d} {k:15s} vague: {', '.join(v) or '-'}", f"      {s}"]
    req = out["requirement"] + out["prohibition"]
    bad = sum(1 for s in src.SPEC if stdreg.verbal_form(s)[1]
              and stdreg.verbal_form(s)[0] in ("requirement", "prohibition"))
    lines += ["  " + ", ".join(f"{k} {v}" for k, v in sorted(out.items())),
              f"  {bad} of {req} requirements cannot be verified as written (a",
              "  vague word); they are rewritten with a value and a test",
              "  before the specification is issued"]
    emit("a_verbal", lines)
    return dict(counts=dict(out), vague=bad, req=req)


def references() -> dict:
    cat = src.CATALOGUE
    refs = ["IEC 62548-1", "IEC 62548-1:2023", "IEC 60529", "IEC 60529:1989",
            "IEC 61400-24", "IEC 60076-2", "IEC 60076-2:2011"]
    lines = ["dated and undated references resolved against the register"]
    out = {}
    for ref in refs:
        parts = stdreg.resolve(ref, cat)
        out[ref] = parts
        lines.append(f"  {ref:18s} -> {' + '.join(parts)}")
    later = copy.deepcopy(cat)
    later["IEC 60076-2"].append(src.FUTURE)
    fut = stdreg.resolve("IEC 60076-2", later)
    lines += ["  if edition 4 of IEC 60076-2 is published (teaching placeholder):",
              f"  IEC 60076-2        -> {fut[0]}",
              f"  IEC 60076-2:2011   -> {stdreg.resolve('IEC 60076-2:2011', later)[0]}",
              "  an undated reference moves with the standard; a dated one",
              "  stays - a specification chooses which, on purpose"]
    emit("a_refs", lines)
    return dict(out=out, future=fut)


def ages() -> dict:
    r = rows()
    yrs = [y for y in (stdreg.edition_year(x) for x in r) if y]
    age = [src.TODAY.year - y for y in yrs]
    bins = [(0, 2), (3, 5), (6, 10), (11, 20), (21, 60)]
    counts = [sum(lo <= a <= hi for a in age) for lo, hi in bins]
    csv("ch58-ages.csv", "k,label,n", [(i + 1, f"{lo}-{hi}", n)
                                      for i, ((lo, hi), n) in enumerate(zip(bins, counts))])
    amend = [x["id"] for x in r if re.search(r"amd|amendment", x["edition"] + x["designation"], re.I)]
    old = sorted(((src.TODAY.year - stdreg.edition_year(x), x["id"], x["designation"])
                  for x in r if stdreg.edition_year(x)), reverse=True)[:5]
    lines = [f"edition age of {len(yrs)} dated rows on {src.TODAY} (years since the edition)",
             "  " + "  ".join(f"{lo}-{hi}: {n}" for (lo, hi), n in zip(bins, counts)),
             f"  median age {int(np.median(age))} years; rows with an amendment: {len(amend)}",
             "  oldest editions:"]
    lines += [f"    {a:2d} years  {i}  {d}" for a, i, d in old]
    lines += ["  an old edition may still be current - a standard is not",
              "  replaced on a schedule; each row's currency is checked, not",
              "  assumed from its age"]
    emit("a_ages", lines)
    return dict(counts=counts, median=float(np.median(age)), amend=len(amend), n=len(yrs))


def adoption() -> dict:
    r = rows()
    cats = collections.Counter()
    for x in r:
        s = x["adoption_or_legal_status"].lower()
        if "not verified" in s:
            cats["adoption not verified"] += 1
        elif "industry" in s:
            cats["industry standard"] += 1
        elif "guide" in s or "directives" in s or "drafting" in s:
            cats["guide or rules"] += 1
        elif "technical specification" in s or "report" in s:
            cats["TS or TR"] += 1
        else:
            cats["international standard (status only)"] += 1
    lines = ["adoption and legal status as the register records it"]
    lines += [f"  {k:40s} {v:4d}" for k, v in cats.most_common()]
    lines += ["  no row records a verified national adoption in Iran,",
              "  Afghanistan or Tajikistan: legal force comes from a law, a",
              "  grid code or a contract that names the standard (ch 54-57)"]
    emit("a_adoption", lines)
    return dict(cats=dict(cats))


# ------------------------------------------------------------ B research
def topics() -> dict:
    r = rows()
    c = collections.Counter(stdreg.topic(x) for x in r)
    order = [t for t, _ in stdreg.TOPICS] + ["other"]
    csv("ch58-topics.csv", "k,topic,n", [(i + 1, t, c.get(t, 0)) for i, t in enumerate(order)])
    lines = [f"register rows by topic (the handoff's {stdreg.HANDOFF_TOPICS} first, then three more)"]
    for i, t in enumerate(order):
        mark = "  (added)" if stdreg.HANDOFF_TOPICS <= i < len(stdreg.TOPICS) else ""
        lines.append(f"  {t:26s} {c.get(t, 0):4d}{mark}")
    thin = [t for t, _ in stdreg.TOPICS[:stdreg.HANDOFF_TOPICS] if c.get(t, 0) <= 3]
    lines += [f"  thin topics (3 rows or fewer): {', '.join(thin)}",
              "  a thin topic is a research gap only if the plant needs more",
              "  there: grounding and protection rest on few documents but",
              "  on many project calculations (ch 26)"]
    emit("b_topics", lines)
    return dict(c=dict(c), thin=thin)


def catalogues() -> dict:
    r = rows()
    dom = collections.Counter(re.sub(r"^https?://(www\.)?", "", x["official_source"]).split("/")[0]
                              for x in r)
    unread = sum(1 for x in r if re.search(r"clause content not reviewed|no clause",
                                           x["note"] + x["applicability_in_book"], re.I))
    lines = ["where the register's sources are (official catalogues first)"]
    lines += [f"  {d:34s} {n:4d}" for d, n in dom.most_common(8)]
    lines += [f"  other sources: {len(r) - sum(n for _, n in dom.most_common(8))}",
              f"  rows that state no clause was read or quoted: {unread} of {len(r)}",
              "  the register records that a document exists, its title and",
              "  edition - the text itself is bought and read for the project"]
    emit("b_catalogues", lines)
    return dict(dom=dom.most_common(8), unread=unread)


def chapters() -> dict:
    r = rows()
    per = {x["id"]: stdreg.chapters(x) for x in r}
    hubs = sorted(per.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:6]
    by_ch = collections.Counter(c for s in per.values() for c in s)
    top = by_ch.most_common(6)
    ident = {x["id"]: x["designation"] for x in r}
    lines = ["standards against chapters (applicability field)"]
    lines += ["  most-cited standards:"]
    lines += [f"    {i} {ident[i][:30]:30s} {len(cs)} chapters" for i, cs in hubs]
    lines += ["  chapters with most standards:"]
    lines += [f"    ch {c:2d}: {n}" for c, n in top]
    lines += [f"  rows tied to one chapter only: {sum(1 for s in per.values() if len(s) == 1)}",
              "  a hub standard changes many records when its edition changes"]
    emit("b_chapters", lines)
    return dict(hubs=hubs, top=top)


def open_items() -> dict:
    r = rows()
    ids = stdreg.open_items(r)
    by = collections.Counter(stdreg.topic(x) for x in r if x["id"] in ids)
    dups = stdreg.duplicates(r)
    lines = [f"open items in the register: {len(ids)} of {len(r)} rows ask to confirm",
             "  an edition, a status or a reported revision"]
    lines += [f"  {t:26s} {n:3d}" for t, n in by.most_common(6)]
    lines += [f"  duplicates (same document and edition): {len(dups)} groups:"]
    lines += [f"    {' = '.join(g)}" for g in dups]
    lines += ["  duplicates are kept as aliases because chapters cite both ids;",
              "  a register meant for a project merges them before issue"]
    emit("b_open", lines)
    return dict(n=len(ids), dups=dups, by=dict(by))


# ---------------------------------------------------------- C conformity
def evidence() -> dict:
    kinds = "TRSF"
    lines = ["evidence Plant P asks for, by equipment (chapters 40-50)",
             "  " + f"{'equipment':34s}" + "".join(f"{k:>3s}" for k in kinds)]
    tot = collections.Counter()
    for eq, ev in src.EVIDENCE.items():
        lines.append("  " + f"{eq:34s}" + "".join(f"{'x' if c != '-' else '.':>3s}" for c in ev))
        for c in ev:
            if c != "-":
                tot[c] += 1
    lines += ["  " + "; ".join(f"{k} {v}" for k, v in src.KINDS.items()),
              f"  type {tot['T']}, routine {tot['R']}, sample {tot['S']}, site {tot['F']} of"
              f" {len(src.EVIDENCE)}",
              "  a type test shows the design; only routine and site tests",
              "  speak for the unit delivered"]
    emit("c_evidence", lines)
    return dict(tot=dict(tot))


def certificates() -> dict:
    out = {}
    lines = ["certificates against the specification and the lab's scope",
             f"  {'equipment':28s} {'edition':8s} {'scope':6s} verdict"]
    for eq, (need, cert, scope) in src.CERTS.items():
        same = need == cert
        ok_scope = stdreg.in_scope(scope, cert)
        test_named = need.split(":")[0] == cert.split(":")[0]
        if same and ok_scope:
            v = "accept"
        elif test_named and ok_scope:
            v = "gap analysis (older edition)"
        else:
            v = "reject: not in the lab's scope"
        out[eq] = v
        lines.append(f"  {eq:28s} {'same' if same else 'older':8s} {'yes' if ok_scope else 'no':6s} {v}")
    n = collections.Counter(out.values())
    lines += ["  " + "; ".join(f"{k}: {v}" for k, v in n.items()),
              "  an older edition is not a failure, it is a question: which",
              "  clauses changed, and does the change touch this product?"]
    emit("c_certs", lines)
    return dict(out=out, n=dict(n))


# --------------------------------------------------------- D traceability
STAGES = ("clause", "decision", "procurement", "inspection", "test", "approval",
          "register", "trigger")


def trace() -> dict:
    lines = ["one verified clause traced through Plant P (transformer temperature rise)"]
    for s in STAGES:
        lines += [f"  {s:12s} {src.TRACE[s][:62]}"]
        rest = src.TRACE[s][62:]
        while rest:
            lines.append(f"  {'':12s} {rest[:62]}")
            rest = rest[62:]
    gaps = [s for s in STAGES if not src.TRACE.get(s)]
    lines += [f"  stages without a record: {len(gaps)} of {len(STAGES)}",
              "  the edition register and the change trigger are stages too:",
              "  a trace that ends at approval goes stale with the standard"]
    emit("d_trace", lines)
    return dict(gaps=gaps)


def reproduce() -> dict:
    """The check of ch 43 repeated with its method varied (teaching)."""
    from companion.ch43 import sources as s43
    from plantp import xfmrdesign as xd
    T = s43.TESTS
    r_cold, t_cold, amb = T["r_hv_ohm"], T["r_temp_c"], T["ambient_c"]

    def rise(r0, k=235.0):
        return r0 / r_cold * (k + t_cold) - k - amb

    t, r = T["cool_t_min"], T["cool_r_hv"]
    full = xd.cooling_curve(t, r)
    four = xd.cooling_curve(t[:4], r[:4])
    cases = [("fit to all 8 readings, copper 235", rise(full["r0"])),
             ("fit to the first 4 readings", rise(four["r0"])),
             ("first reading at 2 min, no fit", rise(r[0])),
             ("all 8, aluminium constant 225", rise(full["r0"], 225.0))]
    limit = s43.MAIN_B["winding_rise"]
    lines = ["the winding-rise check of T1 (ch 43) with its method varied",
             f"  project limit (PLP-ELE-SPC-0010 C-2.5): {limit:.0f} K;"
             " method of IEC 60076-2:2011 (STD-173)",
             f"  {'method':36s} {'rise K':>7s}  verdict"]
    out = {}
    for name, v in cases:
        out[name] = v
        lines.append(f"  {name:36s} {v:7.1f}  {'exceeds' if v > limit else 'within'}")
    lines += ["  the verdict turns on the method: the edition named in the",
              "  specification fixes how the rise is read, not only the limit;",
              "  the constant 225 is for aluminium - T1 is copper (ch 43)"]
    emit("d_reproduce", lines)
    return out


def impact() -> dict:
    lines = ["records to re-check when an edition changes (ch 54 helper)"]
    out = {}
    for doc in ("STD-173", "STD-120", "STD-013"):
        recs = compliance.edition_impact(src.LINKS, doc)
        out[doc] = recs
        lines.append(f"  {doc}: {len(recs)} records")
        lines += [f"    {rid}: {rec}" for rid, rec in recs]
    lines += ["  each record gets a dated decision: unchanged, revised, or",
              "  kept on the old edition by contract (and why)"]
    emit("d_impact", lines)
    return out


def watch() -> dict:
    r = rows()
    open_ids = set(stdreg.open_items(r))
    linked = {doc for doc, _ in src.LINKS.values()}
    n = collections.Counter()
    checks = 0
    for x in r:
        if x["id"] in open_ids:
            k = "open item"
        elif x["id"] in linked or len(stdreg.chapters(x)) >= 3:
            k = "linked or hub"
        else:
            k = "other"
        n[k] += 1
        checks += 12 // src.REVIEW_MONTHS[k]
    lines = ["standards watch: re-verification a year (teaching intervals)",
             f"  {'class':22s} {'rows':>5s} {'every':>6s}"]
    for k in ("open item", "linked or hub", "other"):
        lines.append(f"  {k:22s} {n[k]:5d} {src.REVIEW_MONTHS[k]:4d} mo")
    lines += [f"  checks a year: {checks} (about {checks / 50:.0f} a working week)",
              "  each check: catalogue entry read, edition and status compared,",
              "  date_verified updated, impact run if anything changed"]
    emit("d_watch", lines)
    return dict(n=dict(n), checks=checks)


def main() -> dict:
    res = {}
    for f in (register, verbal, references, ages, adoption, topics, catalogues,
              chapters, open_items, evidence, certificates, trace, reproduce,
              impact, watch):
        res[f.__name__] = f()
    return res


if __name__ == "__main__":
    main()
