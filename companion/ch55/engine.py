"""Shared engine of the country dossiers (chapters 55, 56, 57).

Each country's `sources` module holds FACTS (with status and source),
APPROVALS (steps, owners, teaching durations), GRID_NEED / GRID_GIVEN,
CERT / CERT_NEED, TRACES, SERVICES and FINANCE. The functions below turn
them into the chapter's outputs through the chapter's own `emit`.
Statuses: verified (official source read), project-dependent, to-confirm.
Durations are TEACHING values: no authority publishes them for Plant P.
"""
from __future__ import annotations

from collections import Counter

from companion.ch55 import common  # noqa: F401  (puts plantp on the path)
from plantp import appraisal, compliance, dossier

TOPICS = {"A": "authorities and approvals", "B": "grid, export, water, land",
          "C": "standards and evidence", "E": "grid services",
          "F": "finance and fiscal", "G": "social and land"}


def status_table(src, emit, name: str = "a_status") -> dict:
    tab = dossier.status_by(src.FACTS)
    tot = Counter(f["status"] for f in src.FACTS)
    sec = sum(1 for f in src.FACTS if f.get("secondary"))
    lines = [f"{src.COUNTRY}: {len(src.FACTS)} facts by topic and status"
             f" (sources read {src.ACCESSED})",
             f"  {'topic':28s} {'verified':>9s} {'proj-dep':>9s} {'to-confirm':>11s}"]
    for t, title in TOPICS.items():
        r = tab.get(t)
        if r:
            lines.append(f"  {t} {title:26s} {r['verified']:9d} {r['project-dependent']:9d}"
                         f" {r['to-confirm']:11d}")
    lines += [f"  {'all':28s} {tot['verified']:9d} {tot['project-dependent']:9d}"
              f" {tot['to-confirm']:11d}",
              f"  of the to-confirm items, {sec} rest only on secondary sources",
              "  (news, lenders' or law firms' summaries): a lead, not a source"]
    emit(name, lines)
    return dict(tab=tab, tot=tot, sec=sec)


def facts_list(src, emit, topic: str, name: str) -> list:
    rows = [f for f in src.FACTS if f["topic"] == topic]
    lines = [f"{src.COUNTRY}, topic {topic} ({TOPICS[topic]}):"]
    for f in rows:
        tag = f["status"] + (" (secondary)" if f.get("secondary") else "")
        lines += [f"  {f['id']} {tag}", f"      {f['text']}"]
    emit(name, lines)
    return rows


def stale(src, emit, today, name: str = "c_stale", years: float = 3.0) -> list:
    out = dossier.stale(src.FACTS, today, years)
    undated = [i for i, a in out if a is None]
    old = [(i, a) for i, a in out if a is not None]
    lines = [f"sources of {src.COUNTRY} older than {years:g} years or undated, on {today}",
             f"  undated: {len(undated)} facts; older: {len(old)} facts"]
    lines += [f"    {i}: {a} years" for i, a in sorted(old, key=lambda x: -x[1])[:8]]
    lines += ["  an old text may still be in force, and a new one may exist",
              "  that the search did not reach: each gets a dated check"]
    emit(name, lines)
    return out


def approvals(src, emit, name: str = "d_approvals") -> dict:
    tasks = {k: (v["months"], v["after"]) for k, v in src.APPROVALS.items()}
    total, crit, slack = appraisal.critical_path(tasks)
    lines = [f"approval map of Plant P - {src.COUNTRY} (durations are TEACHING values)",
             f"  {'step':5s} {'status':18s} {'months':>6s} {'slack':>6s}  authority"]
    for k, v in src.APPROVALS.items():
        lines.append(f"  {k:5s} {v['status']:18s} {v['months']:6.1f} {slack[k]:6.1f}"
                     f"  {v['who']}")
        lines.append(f"        {v['what']}")
    tc = [k for k, v in src.APPROVALS.items() if v["status"] != "verified"]
    tcc = [k for k in crit if src.APPROVALS[k]["status"] != "verified"]
    lines += [f"  time to the last approval: {total:.1f} months; critical path:",
              f"    {' > '.join(crit)}",
              f"  steps not verified: {len(tc)} of {len(src.APPROVALS)};"
              f" on the critical path: {', '.join(tcc) or 'none'}",
              "  a step that is not verified on the critical path is the first",
              "  written clarification to send"]
    emit(name, lines)
    return dict(total=total, crit=crit, slack=slack, tc=tc, tcc=tcc)


def grid_gaps(src, emit, name: str = "d_gridgaps") -> dict:
    g = dossier.data_gaps(src.GRID_GIVEN, src.GRID_NEED)
    lines = [f"grid-study inputs for Plant P - {src.COUNTRY}: what the public",
             "sources give against what the studies need (ch 28 register)",
             f"  needed {len(src.GRID_NEED)}; complete {g['complete']:.0%};"
             f" missing {len(g['missing'])}; too weak {len(g['weak'])}"]
    lines += [f"    missing: {m}" for m in g["missing"]]
    lines += [f"    weak:    {i} (given as {a}, needs {b})" for i, a, b in g["weak"]]
    lines += [f"  the request goes to: {src.GRID_REQUEST_TO}"]
    emit(name, lines)
    return g


def cert(src, emit, name: str = "d_cert") -> list:
    rows = dossier.cert_review(src.CERT, src.CERT_NEED)
    lines = [f"what an equipment certificate shows for Plant P - {src.COUNTRY}",
             f"  certificate: {src.CERT['what']}"]
    for item, verdict, note in rows:
        lines.append(f"  {verdict:10s} {item}")
        if note:
            lines.append(f"             {note}")
    not_shown = [r[0] for r in rows if r[1] != "shown"]
    lines += [f"  not shown: {len(not_shown)} of {len(rows)} items",
              f"  national rule: {src.CERT_NATIONAL}"]
    emit(name, lines)
    return rows


def traces(src, emit, name: str = "d_trace") -> dict:
    out = {}
    lines = [f"traces of sourced requirements - {src.COUNTRY}"]
    for rid, (title, trace) in src.TRACES.items():
        gaps = compliance.trace_gaps(trace)
        out[rid] = gaps
        lines.append(f"  {rid}: {title}")
        for st in compliance.STAGES:
            lines.append(f"    {st:12s} {trace.get(st) or 'OPEN'}")
        lines.append(f"    open stages: {len(gaps)} of {len(compliance.STAGES)}")
    emit(name, lines)
    return out


def services(src, emit, name: str = "e_services") -> dict:
    by = Counter(s[1] for s in src.SERVICES)
    lines = [f"grid services for Plant P - {src.COUNTRY}: what a source requires or allows"]
    for svc, st, note in src.SERVICES:
        lines += [f"  {svc:34s} {st}", f"      {note}"]
    lines += [f"  verified {by['verified']}, project-dependent {by['project-dependent']},"
              f" to-confirm {by['to-confirm']}",
              "  a service not found is not offered in the base: no capability,",
              "  test or revenue is assumed for it (ch 20, 54)"]
    emit(name, lines)
    return by


def finance(src, emit, name: str = "f_finance") -> dict:
    by = Counter(f[2] for f in src.FINANCE)
    lines = [f"finance and fiscal sources - {src.COUNTRY}"]
    for item, kind, st, who in src.FINANCE:
        lines += [f"  {item:44s} {st}", f"      source: {kind}; review: {who}"]
    lines += [f"  verified {by['verified']}, project-dependent {by['project-dependent']},"
              f" to-confirm {by['to-confirm']}",
              "  only verified items enter the base case (ch 54 E); every item",
              "  closes with a dated opinion of a qualified local reviewer"]
    emit(name, lines)
    return by


def issues(src, emit, name: str = "g_issues") -> dict:
    open_ = [f for f in src.FACTS if f["status"] != "verified"]
    by = Counter(f.get("ask", "project team") for f in open_)
    lines = [f"unresolved-issue log - {src.COUNTRY}: {len(open_)} items, by whom to ask"]
    lines += [f"  {who:44s} {n:3d}" for who, n in by.most_common()]
    lines += ["  each item: a written request, a date sent, an owner, and the",
              "  decision it holds up (ch 54 C)"]
    emit(name, lines)
    return by
