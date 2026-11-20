"""Chapter 58, more lessons: decision rules with measurement uncertainty,
what a zero-failure sample can claim, certificate validity against the
schedule, document types and lifecycle stages in the register, the
research log of this chapter's own verification, and the register's
revision diff.

Run from the project root:   python -m companion.ch58.more
Writes companion/ch58/expected/m_*.txt and diagrams/data/ch58-*.csv.
Teaching values: A-567 to A-570.
"""
from __future__ import annotations

import collections
import math
import re
from datetime import date

import numpy as np

from companion.ch58 import common  # noqa: F401  (path)
from companion.ch58 import sources as src
from companion.ch58.common import csv, emit
from plantp import compliance, stdreg
from plantp.quality import phi


def rows() -> list[dict]:
    return stdreg.load(src.REGISTER)


# [start: decision]
def p_above(measured: float, limit: float, u_exp: float,
            k: float = 2.0) -> float:
    """Chance that the true value exceeds an upper limit, for a reading with
    expanded uncertainty u_exp at coverage factor k (normal, teaching)."""
    return 1.0 - phi((limit - measured) / (u_exp / k))


def verdict(measured: float, limit: float, u_exp: float, rule: str) -> str:
    """Simple acceptance: pass if the reading is at or below the limit.
    Guarded acceptance: pass only if reading + U is at or below the limit;
    fail only if reading - U is above it; otherwise undecided."""
    if rule == "simple":
        return "pass" if measured <= limit else "fail"
    if measured + u_exp <= limit:
        return "pass"
    if measured - u_exp > limit:
        return "fail"
    return "undecided"
# [end: decision]


def decision() -> dict:
    limit, u = 65.0, 1.6           # K; U teaching (A-570), k = 2
    readings = [("T1, read correctly", 66.5), ("T1, 2-minute reading", 62.0),
                ("unit at 64.2 K", 64.2), ("unit at 65.4 K", 65.4),
                ("unit at 67.0 K", 67.0)]
    lines = ["decision rules on the winding-rise limit (65 K) with U = 1.6 K, k = 2",
             f"  {'reading':22s} {'K':>5s} {'P(true > 65)':>13s} {'simple':>7s} {'guarded':>10s}"]
    out = {}
    for name, x in readings:
        p = p_above(x, limit, u)
        s, g = verdict(x, limit, u, "simple"), verdict(x, limit, u, "guarded")
        out[name] = (x, p, s, g)
        lines.append(f"  {name:22s} {x:5.1f} {p:13.0%} {s:>7s} {g:>10s}")
    xs = np.linspace(60.0, 70.0, 101)
    csv("ch58-decision.csv", "x,p", [(round(float(v), 2), round(p_above(float(v), limit, u), 4))
                                    for v in xs])
    lines += ["  a reading of 64.2 K passes the simple rule with a 16 % chance",
              "  that the true rise is above the limit; the guarded rule leaves",
              "  it undecided - which rule applies is written in the purchase",
              "  clause, with who carries the risk (JCGM 106, STD-009)"]
    emit("m_decision", lines)
    return out


def sample_bound() -> dict:
    """Upper 95 % bound on the defect rate after n units tested, 0 failures:
    1 - 0.05^(1/n) (exact binomial, zero failures)."""
    ns = (1, 3, 5, 13, 32, 80, 125, 315)
    lines = ["what a passed sample can claim: n units tested, none failed",
             f"  {'n':>5s} {'95 % upper bound on the defect rate':>38s}"]
    out = {}
    for n in ns:
        b = 1 - 0.05 ** (1 / n)
        out[n] = b
        lines.append(f"  {n:5d} {b:38.1%}")
    csv("ch58-sample.csv", "n,b", [(n, round(1 - 0.05 ** (1 / n), 5)) for n in range(1, 321)])
    n1 = math.ceil(math.log(0.05) / math.log(0.99))
    lines += [f"  to claim below 1 % with no failure: n >= {n1} (rule of three: 3/n)",
              "  a type test on 1 to 3 samples proves the design can pass; it",
              "  says almost nothing about the rate of defects in production"]
    emit("m_sample", lines)
    return dict(out=out, n1=n1)


CERT_DATES = {   # equipment -> (certificate valid to, delivery, end of warranty) teaching
    "PV module": (date(2029, 3, 31), date(2028, 2, 1), date(2033, 2, 1)),
    "PV inverter": (date(2028, 1, 10), date(2028, 3, 1), date(2033, 3, 1)),
    "wind turbine (type)": (date(2030, 6, 30), date(2028, 6, 1), date(2033, 6, 1)),
    "main transformer": (None, date(2028, 4, 1), date(2031, 4, 1)),
    "MV switchgear": (date(2027, 11, 30), date(2028, 1, 15), date(2030, 1, 15)),
    "battery system": (date(2029, 12, 31), date(2028, 5, 1), date(2038, 5, 1)),
    "revenue meter": (date(2031, 1, 1), date(2028, 2, 15), date(2033, 2, 15)),
}


def validity() -> dict:
    lines = ["certificate validity against the delivery schedule (teaching dates)",
             f"  {'equipment':22s} {'valid to':>11s} {'delivery':>11s}  verdict"]
    bad = []
    for eq, (v, d, w) in CERT_DATES.items():
        if v is None:
            verdict_ = "unit test report (ch 43)"
        elif v < d:
            verdict_ = "EXPIRES BEFORE DELIVERY"
            bad.append(eq)
        elif v < w:
            verdict_ = "valid at delivery"
        else:
            verdict_ = "valid through warranty"
        lines.append(f"  {eq:22s} {str(v) if v else '-':>11s} {str(d):>11s}  {verdict_}")
    lines += [f"  expiring before delivery: {', '.join(bad)}",
              "  a certificate is checked on the delivery date, not on the bid",
              "  date: a renewal or a re-test is a condition of the order"]
    emit("m_validity", lines)
    return dict(bad=bad)


def doc_types() -> dict:
    r = rows()
    c = collections.Counter()
    for x in r:
        d, s = x["designation"], x["adoption_or_legal_status"].lower()
        if re.search(r"\bTS\b", d) or "technical specification" in s:
            c["technical specification (TS)"] += 1
        elif re.search(r"\bTR\b", d) or "technical report" in s:
            c["technical report (TR)"] += 1
        elif "guide" in d.lower() or "guide" in s or "jcgm" in d.lower():
            c["guide"] += 1
        elif d.startswith(("IEC", "ISO", "EN", "CEN")):
            c["international or European standard"] += 1
        else:
            c["industry, national or other"] += 1
    lines = ["document types in the register"]
    lines += [f"  {k:38s} {v:4d}" for k, v in c.most_common()]
    lines += ["  a technical specification or report is not an International",
              "  Standard: it can be cited, but its status (and its likely",
              "  revision into a standard) is recorded with it"]
    emit("m_types", lines)
    return dict(c=dict(c))


STAGE_WORDS = [("design", ("design", "selection", "rating", "sizing", "calculation")),
               ("manufacture and factory test", ("factory", "manufactur", "type", "routine",
                                                 "qualification", "process")),
               ("site test and commissioning", ("commission", "site test", "acceptance",
                                                "inspection", "verification")),
               ("operation and maintenance", ("operation", "maintenance", "monitoring",
                                              "o&m", "performance"))]


def lifecycle() -> dict:
    r = rows()
    c = collections.Counter()
    none = 0
    for x in r:
        text = x["applicability_in_book"].lower()
        hit = [s for s, ws in STAGE_WORDS if any(w in text for w in ws)]
        for s in hit:
            c[s] += 1
        none += not hit
    lines = ["register rows by lifecycle stage (keywords in the applicability field;",
             "a row may serve several stages)"]
    lines += [f"  {s:32s} {c.get(s, 0):4d}" for s, _ in STAGE_WORDS]
    lines += [f"  rows with no stage word: {none} of {len(r)}",
              "  the book's applicability field names chapters and purposes,",
              "  seldom the stage; a project register gives each row a stage",
              "  column, because one standard is read at several stages"]
    emit("m_lifecycle", lines)
    return dict(c=dict(c), none=none)


RESEARCH = [   # (document, what was looked for, what the official source showed, result)
    ("ISO/IEC 17025", "2017, edition 3", "2017, edition 3, confirmed", "as expected"),
    ("ISO/IEC 17065", "2012", "2012; draft amendment listed 2025", "note added"),
    ("ISO/IEC 17020", "2012", "2012 withdrawn; 2026 edition 3", "CORRECTED"),
    ("ISO/IEC 17050-1", "2010", "2004 (no 2010 edition found)", "CORRECTED"),
    ("ISO/IEC Guide 21-1", "2005", "2005; newer edition not seen", "confirm"),
    ("ISO/IEC Directives Part 2", "2021", "2021, 9th edition; 2026 amendment", "confirm"),
    ("drafting page (iso.org)", "rule text", "HTTP 403: not readable", "other source used"),
]


def research() -> dict:
    lines = ["research log of this chapter's own verification (2026-11-18)"]
    for d, want, got, res in RESEARCH:
        lines += [f"  {d:26s} {res}", f"      looked for {want}; found {got}"]
    n = collections.Counter(r[3] for r in RESEARCH)
    eds = [x for x in RESEARCH if "edition" in x[1] or x[1][:2] == "20"]
    wrong = sum(1 for x in eds if x[3] == "CORRECTED")
    lines += [f"  {wrong} of {len(eds)} editions were wrong as first written: the edition",
              "  in memory or in a secondary source is a lead, the catalogue",
              "  entry is the record"]
    emit("m_research", lines)
    return dict(n=dict(n))


def revision() -> dict:
    """The register's revision in this chapter as a diff (ch 54 helper)."""
    r = rows()
    new = {x["id"]: {k: x[k] for k in ("designation", "edition", "note")} for x in r}
    old = {}
    for i, f in new.items():
        if i in ("STD-187", "STD-188", "STD-189", "STD-190", "STD-191"):
            continue
        g = dict(f)
        g["note"] = re.sub(r";? ?Alias of STD-\d{3}.*$", "", g["note"])
        old[i] = g
    d = compliance.register_diff(old, new)
    lines = ["the register's revision in chapter 58 (diff of two versions)",
             f"  added: {', '.join(d['added'])}",
             f"  removed: {', '.join(d['removed']) or 'none'}",
             f"  changed: {len(d['changed'])}"]
    lines += [f"    {rid} {field}: alias note added" for rid, field, _, _ in d["changed"]]
    lines += ["  every revision of the register is issued with this list and",
              "  the impact run for each changed or added row (ch 38, ch 54)"]
    emit("m_revision", lines)
    return d


def intervals() -> dict:
    r = rows()
    pairs = []
    for x in r:
        y0, y1 = stdreg.replaced_year(x), stdreg.edition_year(x)
        if y0 and y1 and y1 > y0:
            pairs.append((y1 - y0, x["id"], x["designation"], y0, y1))
    iv = sorted(p[0] for p in pairs)
    q1, med, q3 = (float(np.percentile(iv, q)) for q in (25, 50, 75))
    bins = [(1, 5), (6, 10), (11, 15), (16, 30)]
    counts = [sum(lo <= v <= hi for v in iv) for lo, hi in bins]
    csv("ch58-intervals.csv", "k,label,n", [(i + 1, f"{lo}-{hi}", n)
                                           for i, ((lo, hi), n) in enumerate(zip(bins, counts))])
    sp = sorted(pairs)
    lines = [f"years between an edition and the one before it ({len(pairs)} rows that",
             "name the edition they replace)",
             f"  quartiles {q1:.0f} / {med:.0f} / {q3:.0f} years; shortest {iv[0]}, longest {iv[-1]}",
             "  " + "  ".join(f"{lo}-{hi}: {n}" for (lo, hi), n in zip(bins, counts)),
             "  shortest:"]
    lines += [f"    {a:2d}  {d} (from {y0})" for a, _, d, y0, _ in sp[:3]]
    lines += ["  longest:"]
    lines += [f"    {a:2d}  {d} (from {y0})" for a, _, d, y0, _ in sp[-3:]]
    p5 = sum(1 for v in iv if v <= 5) / len(iv)
    two = sum(1 for v in iv if v <= 12) / len(iv)
    lines += [f"  {p5:.0%} lasted five years or less; {two:.0%} twelve or less, i.e. at",
              "  that pace two new editions within a 25-year plant life - the",
              "  register is kept, not written once"]
    emit("m_intervals", lines)
    return dict(n=len(pairs), med=med, q1=q1, q3=q3, p5=p5, two=two, lo=iv[0], hi=iv[-1])


def families() -> dict:
    r = rows()
    by = collections.defaultdict(list)
    for x in r:
        s = stdreg.series(x["designation"])
        if s:
            by[s].append(x["designation"])
    top = sorted(by.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:5]
    lines = ["standards that come in series (parts of one number in the register)"]
    for s, ds in top:
        parts = sorted({re.sub(r"^(IEC|ISO|EN)\s+(TS\s+|TR\s+)?", "", d).split(":")[0]
                        for d in ds})
        lines.append(f"  {s} ({len(ds)} rows):")
        line = "    "
        for p_ in parts:
            if len(line) + len(p_) > 74:
                lines.append(line.rstrip(", "))
                line = "    "
            line += p_ + ", "
        lines.append(line.rstrip(", "))
    lines += ["  part 1 is usually general and the others particular: a",
              "  particular part is read with its general part, in the",
              "  editions it names"]
    emit("m_families", lines)
    return dict(top=[(s, len(ds)) for s, ds in top])


EQUIP = [("PV modules", "IEC 61215-2:2021"), ("PV modules", "IEC 61730-2:2023"),
         ("PV inverters", "IEC 62109-1:2010"), ("PV inverters", "IEC 62116:2014"),
         ("battery systems", "IEC 62619:2022"), ("MV switchgear", "IEC 62271-200:2021")]


def clauses() -> dict:
    lines = ["type-test clauses written from the register (dated, verifiable)"]
    bad = 0
    for eq, d in EQUIP:
        c = stdreg.clause(eq, d)
        k, v = stdreg.verbal_form(c)
        bad += bool(v) or k != "requirement"
        lines += [f"  [{k}; vague: {', '.join(v) or '-'}]", f"  {c}"]
    lines += [f"  clauses with a vague word or no requirement: {bad} of {len(EQUIP)}",
              "  the clause names the edition, the lab's scope and what the",
              "  report must show - the three checks of section C"]
    emit("m_clauses", lines)
    return dict(n=len(EQUIP), bad=bad)


def iran() -> dict:
    """Iran's mandatory national standards (ch 55) beside the register."""
    from companion.ch55 import sources as s55
    facts = {f["id"]: f for f in s55.FACTS}
    pairs = [("power transformers", "IR-30", ["STD-120", "STD-173"]),
             ("MV cables", "IR-30", ["STD-114"]),
             ("stationary VRLA and lithium cells", "IR-49", ["STD-096"]),
             ("PV inverters up to 5 kW (import list)", "IR-28", ["STD-044"]),
             ("PV modules, wind turbines", "IR-29", ["STD-056", "STD-080"])]
    ident = {x["id"]: x["designation"] for x in rows()}
    lines = ["Iran: mandatory national standards (ch 55) beside the register"]
    for eq, f, stds in pairs:
        lines += [f"  {eq}",
                  f"      register: {', '.join(ident[s] for s in stds)}",
                  f"      {f} ({facts[f]['status']}): {facts[f]['text']}"]
    lines += ["  where a national standard is mandatory, an IEC certificate is",
              "  not enough: the national certificate is a second, separate",
              "  piece of evidence in the order (ch 39, ch 55)"]
    emit("m_iran", lines)
    return dict(n=len(pairs))


VCRM = [   # PV inverter requirements (teaching): id, source, method, stage, evidence or None
    ("INV-01 safety of the converter", "STD-044", "test", "type", "type-test report"),
    ("INV-02 islanding prevention", "STD-048", "test", "type", None),
    ("INV-03 output at 45 C ambient", "spec", "test", "factory", "heat run record"),
    ("INV-04 efficiency curve", "STD-049", "test", "type", "efficiency report"),
    ("INV-05 EMC emission and immunity", "STD-052", "test", "type", "EMC report"),
    ("INV-06 reactive capability at the terminals", "spec", "test", "factory", None),
    ("INV-07 firmware version as approved", "spec", "inspection", "site", "configuration record"),
    ("INV-08 enclosure protection", "STD-119", "test", "type", "IP report"),
    ("INV-09 plant reactive power at the POC", "grid", "analysis", "study", "model report"),
    ("INV-10 plant ride-through", "grid", "demonstration", "site", None),
]


def vcrm() -> dict:
    by_m = collections.Counter(v[2] for v in VCRM)
    by_s = collections.Counter(v[3] for v in VCRM)
    open_ = [v[0].split()[0] for v in VCRM if v[4] is None]
    lines = ["verification cross-reference matrix: PV inverter (teaching)"]
    for req, srcid, m, st, ev in VCRM:
        lines += [f"  {req}  [{srcid}]",
                  f"      {m}, {st} stage: {ev or 'OPEN'}"]
    lines += ["  methods: " + ", ".join(f"{k} {v}" for k, v in by_m.most_common()),
              "  stages: " + ", ".join(f"{k} {v}" for k, v in by_s.most_common()),
              f"  open: {', '.join(open_)}",
              "  every requirement has one method and one stage; a row with",
              "  no evidence is a decision someone must still make"]
    emit("m_vcrm", lines)
    return dict(open=open_, m=dict(by_m), s=dict(by_s))


CHANGES = [   # change after the type test -> (class, what to do) teaching rules
    ("same model, new production site", "major", "factory audit + routine tests; type test reviewed"),
    ("new firmware, control parameters only", "minor", "regression test of the affected functions"),
    ("new firmware, protection functions", "major", "repeat the affected type tests"),
    ("power semiconductor from another maker", "major", "repeat thermal and safety type tests"),
    ("enclosure paint colour", "none", "no test; record in the configuration"),
    ("larger DC capacitor, same rating", "minor", "engineering assessment by the cert body"),
    ("new edition of the safety standard", "review", "gap analysis of changed clauses"),
]


def changes() -> dict:
    n = collections.Counter(c[1] for c in CHANGES)
    lines = ["is the type test still valid after a change? (teaching rules)"]
    for what, cls, todo in CHANGES:
        lines += [f"  [{cls:6s}] {what}", f"           {todo}"]
    lines += ["  " + ", ".join(f"{k} {v}" for k, v in n.most_common()),
              "  the certification body decides the class; the purchaser asks",
              "  to be told of every change, in the contract (ch 44)"]
    emit("m_changes", lines)
    return dict(n=dict(n))


LABS = {   # laboratory -> accredited scope (teaching)
    "Lab A": {"IEC 62109-1:2010", "IEC 62109-2:2011", "IEC 61683:1999"},
    "Lab B": {"IEC 62116:2014", "IEC 61000-6-2:2016", "IEC 61000-6-4:2018"},
    "Lab C": {"IEC 62109-1:2010", "IEC 62116:2014", "IEC 60529:1989+AMD1:1999+AMD2:2013"},
    "Lab D": {"IEC 61000-6-2:2016", "IEC 61000-6-4:2018", "IEC 61683:1999"},
}
NEEDED = {"IEC 62109-1:2010", "IEC 62109-2:2011", "IEC 62116:2014", "IEC 61683:1999",
          "IEC 61000-6-2:2016", "IEC 61000-6-4:2018", "IEC 60529:1989+AMD1:1999+AMD2:2013"}


def labs() -> dict:
    """Fewest laboratories whose accredited scopes cover every needed test
    (exhaustive search over subsets - four labs is small)."""
    from itertools import combinations
    best = None
    for k in range(1, len(LABS) + 1):
        for combo in combinations(sorted(LABS), k):
            cover = set().union(*(LABS[c] for c in combo))
            if NEEDED <= cover:
                best = combo
                break
        if best:
            break
    lines = ["fewest accredited laboratories for the inverter's type tests (teaching)",
             f"  tests needed: {len(NEEDED)}"]
    for lab, sc in sorted(LABS.items()):
        lines.append(f"  {lab}: {len(sc & NEEDED)} of {len(NEEDED)}")
    lines += [f"  smallest set covering all: {', '.join(best)} ({len(best)} labs)",
              "  no single lab covers all seven; each report is checked",
              "  against its own lab's scope, test by test"]
    emit("m_labs", lines)
    return dict(best=best)


REPORT_FIELDS = ("laboratory", "accreditation number", "standard and edition",
                 "model", "serial or sample id", "firmware", "test dates",
                 "results against criteria", "deviations from the method",
                 "signatory")
REPORT = {   # a teaching type-test report header of the PV inverter
    "laboratory": "Lab C", "accreditation number": "ACC-0417",
    "standard and edition": "IEC 62109-1:2010", "model": "PCI-5500",
    "serial or sample id": "S/N 0007", "firmware": None,
    "test dates": "2027-03-02 to 2027-03-19", "results against criteria": "pass",
    "deviations from the method": None, "signatory": "test manager",
}


def report() -> dict:
    missing = [f for f in REPORT_FIELDS if not REPORT.get(f)]
    lines = ["reading a type-test report: header fields (teaching report)"]
    lines += [f"  {f:28s} {REPORT.get(f) or 'MISSING'}" for f in REPORT_FIELDS]
    lines += [f"  missing: {', '.join(missing)}",
              "  without the firmware the report cannot be tied to the unit",
              "  installed; 'deviations: none' must be written, not left out"]
    emit("m_report", lines)
    return dict(missing=missing)


FORMS_FA = [("نباید", "prohibition"), ("باید", "requirement"),
            ("بهتر است", "recommendation"), ("مجاز است", "permission"),
            ("می‌تواند", "possibility")]
SPEC_FA = [   # Persian translations of src.SPEC, two of them wrong on purpose
    "کنتورِ درآمدی باید در مرزِ مالکیت کلاسِ 0.5S باشد.",
    "مفصلِ کابل نباید درونِ تقاطعِ جاده قرار گیرد.",
    "اینورتر باید برای بیشینهٔ دمای محیطِ ساختگاه رده‌بندی شود.",
    "تأمین‌کننده مجاز است مادهٔ دیگری برای زمین با شاهد پیشنهاد کند.",
    "آزمون‌های ساختگاه می‌تواند با حضورِ شرکتِ شبکه انجام شود.",
    "اتصال به زمین باید برای سطحِ خطا کافی باشد.",
    "بوشینگ‌های ترانسفورماتور باید برای ساختگاه مناسب باشند.",
    "میانگینِ افزایشِ دمای سیم‌پیچ نباید از 65 K بیشتر شود.",
    "حفاظت در برابرِ خوردگی باید طبقِ رویهٔ خوب باشد.",
    "نیروگاه در نقطهٔ اتصال صادر می‌کند.",
    "یدک‌ها بهتر است هر جا لازم باشد نگه داشته شوند.",
    "پیمانکار مجاز است گزارش‌های آزمونِ نوعی را با پیشنهاد بدهد.",
]


def form_fa(sentence: str) -> str:
    for word, name in FORMS_FA:
        if word in sentence:
            return name
    return "statement"


def translation() -> dict:
    lines = ["does the Persian translation keep each provision type?"]
    bad = []
    for i, (en, fa) in enumerate(zip(src.SPEC, SPEC_FA), 1):
        a, b = stdreg.verbal_form(en)[0], form_fa(fa)
        ok = a == b
        if not ok:
            bad.append(f"S{i:02d}")
        lines.append(f"  S{i:02d} English {a:15s} Persian {b:15s} {'' if ok else 'MISMATCH'}")
    lines += [f"  mismatches: {', '.join(bad)}",
              "  a recommendation translated as 'baayad' becomes a requirement,",
              "  and a requirement as 'mojaaz ast' a permission: the type is",
              "  checked sentence by sentence before a translation is issued"]
    emit("m_translation", lines)
    return dict(bad=bad)


if __name__ == "__main__":
    report()
    translation()
    vcrm()
    changes()
    labs()
    intervals()
    families()
    clauses()
    iran()
    decision()
    sample_bound()
    validity()
    doc_types()
    lifecycle()
    research()
    revision()
