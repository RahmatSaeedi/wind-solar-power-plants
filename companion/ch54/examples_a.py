"""Chapter 54, lessons A-C on the fictional Country Z: the source types of
the register, conflicts on one parameter, a contract that cannot loosen a
permit, applicability to Plant P, source freshness, language of the
official text, the register's status, clarification ageing, and the
records an edition change touches.

Run from the project root:   python -m companion.ch54.examples_a
Writes companion/ch54/expected/a_*.txt, b_*.txt, c_*.txt.
Fictional teaching data (A-546 to A-548).
"""
from __future__ import annotations

from companion.ch54 import sources as src
from companion.ch54.common import emit
from plantp import compliance as cp


# ------------------------------------------------ A1. source types
def types() -> dict:
    out = {}
    for r in src.REQS:
        t = src.DOCS[r["document"]][0]
        out.setdefault(t, []).append(r["id"])
    lines = ["the project's register by source type, highest first (fictional Country Z)"]
    for t in sorted(out, key=cp.rank):
        lines.append(f"  {cp.rank(t)}. {t:20s} {', '.join(out[t])}")
    lines += ["  law, regulations and permits bind by law; grid code and",
              "  utility rules by the licence and the connection; contracts by",
              "  agreement; the owner's specification only the project - the",
              "  order is a teaching order, the real one a legal question"]
    emit("a_types", lines)
    return out


# ------------------------------------------------ A2. conflicts on one parameter
def conflict_table() -> dict:
    params = ["power factor at POC", "ramp rate", "night noise at dwellings",
              "ride-through at 0 pu"]
    out = {pr: cp.conflicts(src.REQS, pr) for pr in params}
    lines = ["one parameter, several sources: the range every source allows",
             f"  {'parameter':24s} {'min':>5s} {'max':>5s} {'result':8s} sources"]
    for pr, r in out.items():
        lo = "-" if r["lo"] is None else f"{r['lo']:g}"
        hi = "-" if r["hi"] is None else f"{r['hi']:g}"
        lines.append(f"  {pr:24s} {lo:>5s} {hi:>5s} "
                     f"{'ok' if r['feasible'] else 'CONFLICT':8s} {','.join(r['sources'])}")
    bad = [pr for pr, r in out.items() if not r["feasible"]]
    lines += [f"  conflicts: {', '.join(bad)} - no design satisfies both; the",
              "  answer is a written clarification (CQ-01), not an engineer's",
              "  choice of the convenient source"]
    emit("a_conflict", lines)
    return out


# ------------------------------------------------ A3. a contract cannot loosen a permit
def precedence() -> dict:
    rows = [r for r in src.REQS if r["parameter"] == "night noise at dwellings"]
    gov = min(r["value"] for r in rows)
    lines = ["night noise at dwellings in three sources (dB(A))"]
    lines += [f"  {r['id']} {src.DOCS[r['document']][0]:18s} {r['value']:.0f}" for r in rows]
    lines += [f"  governing: {gov:.0f} dB(A), the permit's - all three apply at once,",
              "  so the design meets the strictest; the PPA's 48 does not loosen",
              "  the permit, and meeting 40 also meets the regulation's 45.",
              "  Rank decides only when sources cannot all be met together",
              "  (ch 33 noise model works to 40)"]
    emit("a_preced", lines)
    return dict(gov=gov)


# ------------------------------------------------ B1. applicability to the project
def applicability() -> dict:
    apply_ = [r["id"] for r in src.REQS if cp.applies(r, src.PROJECT)]
    out_ = [r["id"] for r in src.REQS if not cp.applies(r, src.PROJECT)]
    lines = [f"Plant P: {src.PROJECT['voltage_kv']} kV, {src.PROJECT['ownership']}, "
             f"{src.PROJECT['location']}, {src.PROJECT['technology']}",
             f"  requirements that apply: {len(apply_)}; outside the scope: {', '.join(out_)}",
             "  Z-011 is a distribution rule for 33 kV and below: it would",
             "  apply to a collector connected to the distribution network,",
             "  not to a 132 kV transmission connection - applicability is",
             "  decided by voltage, ownership and location, and recorded"]
    emit("b_apply", lines)
    return dict(apply=apply_, out=out_)


# ------------------------------------------------ B2. source freshness
def freshness() -> dict:
    cur = {d: v[2] for d, v in src.DOCS.items()}
    out = {}
    for r in src.REQS:
        pr = cp.freshness(r, src.TODAY, 365, cur)
        if pr:
            out[r["id"]] = pr
    lines = [f"source checks on {src.TODAY}: checked within 365 days, current edition,",
             "  official source"]
    lines += [f"  {k}: {'; '.join(v)}" for k, v in out.items()]
    lines += [f"  {len(out)} of {len(src.REQS)} requirements need work: the ramp rate was",
              "  copied from the 2019 grid code (a later edition exists), the",
              "  transformer standard is an older edition, and one rule has",
              "  no official source - a requirement is only as current as",
              "  its last check"]
    emit("b_fresh", lines)
    return out


# ------------------------------------------------ B3. official language
def language() -> dict:
    risky = [d for d, (off, tr, diff) in src.LANGUAGE.items() if not off and tr]
    lines = ["documents read in their official language, or only in translation"]
    for d, (off, tr, diff) in src.LANGUAGE.items():
        lines.append(f"  {d:7s} official {'yes' if off else 'NO '}  translation "
                     f"{'yes' if tr else 'no '}")
        if diff:
            lines.append(f"          {diff}")
    lines += [f"  read only in translation: {', '.join(risky)} - a translation is a",
              "  reading aid; the official text decides, and a qualified",
              "  reader confirms the clauses the design depends on"]
    emit("b_lang", lines)
    return dict(risky=risky)


# ------------------------------------------------ C1. register status
def status() -> dict:
    s = cp.summary(src.REQS)
    lines = ["register status (verified / project-dependent / to-confirm)"]
    lines += [f"  {k:18s} {v:3d}" for k, v in s.items()]
    lines += ["  verified: the official text was read and its applicability",
              "  recorded; project-dependent: the value comes from a document",
              "  still being negotiated (CA-P draft 3); to-confirm: an open",
              "  question with a request behind it - never silently assumed"]
    emit("c_status", lines)
    return s


# ------------------------------------------------ C2. clarification ageing
def clarifications(limit: int = 30) -> dict:
    old = cp.clarification_ageing([(i, s, a) for i, _, _, s, a in src.CLARIFICATIONS],
                                  src.TODAY, limit)
    lines = [f"written clarification requests on {src.TODAY} (escalate after {limit} days)"]
    for i, to, subj, sent, a in src.CLARIFICATIONS:
        lines += [f"  {i} to {to:18s} sent {sent}  "
                  + (f"answered {a}" if a else "OPEN"), f"        {subj}"]
    first = max(old, key=lambda x: x[1])[0]
    dep = [r["id"] for r in src.REQS if r["document"] == "GCZ"]
    lines += [f"  open past {limit} days: " + ", ".join(f"{i} ({d} days)" for i, d in old),
              f"  {first} (which grid-code edition applies) has waited longest -",
              f"  and {len(dep)} requirements depend on its answer ({', '.join(dep)})"]
    emit("c_clarify", lines)
    return dict(old=old)


# ------------------------------------------------ C3. an edition change
def edition_change() -> list:
    hit = cp.edition_impact(src.LINKS, "GCZ")
    lines = ["the grid code is re-issued: records to re-check (from the trace links)"]
    lines += [f"  {rid}: {rec}" for rid, rec in hit]
    chs = sorted({int(rec.split()[1]) for _, rec in hit})
    lines += [f"  {len(hit)} records across chapters {', '.join(map(str, chs))}: an edition",
              "  change is a design change (ch 38 change impact), reviewed",
              "  record by record, not by re-reading the new code alone"]
    emit("c_edition", lines)
    return hit


if __name__ == "__main__":
    types()
    conflict_table()
    precedence()
    applicability()
    freshness()
    language()
    status()
    clarifications()
    edition_change()
