"""Chapter 54, three integrated Plant P examples: numbers by hand, a
compliance-readiness review at the design stage, and the compliance-method
basis D-058.

Run from the project root:   python -m companion.ch54.integrated
Writes companion/ch54/expected/int_*.txt.
"""
from __future__ import annotations

import math

from companion.ch54 import examples_a as ea
from companion.ch54 import examples_b as eb
from companion.ch54 import examples_s as es
from companion.ch54 import lab_d
from companion.ch54 import sources as src
from companion.ch54.common import emit


def by_hand() -> dict:
    q = 100 * math.tan(math.acos(0.95))
    p_ok = 30.6 / math.tan(math.acos(0.95))
    w = es.watch()
    lines = ["three numbers by hand",
             f"  Q needed at 100 MW, pf 0.95: 100 x tan(acos 0.95) = {q:.2f} Mvar",
             f"  P where 30.6 Mvar meets pf 0.95: 30.6 / 0.3287 = {p_ok:.1f} MW",
             f"  chance of a rule change within a year at 0.5 a year:"
             f" 1 - e^-0.5 = {1 - math.exp(-0.5):.0%}",
             f"  (programs: {q:.2f}, {p_ok:.1f}, {w['p_conn']:.0%})"]
    emit("int_hand", lines)
    return dict(q=q, p_ok=p_ok)


def review() -> dict:
    auth = eb.authorities()
    res = eb.research()
    fld = eb.fields()
    rac = eb.raci()
    itp = eb.interpretations()
    con = ea.conflict_table()
    fr = ea.freshness()
    cl = ea.clarifications()
    gt = es.gates()
    tr = lab_d.trace()
    asked = all(any(pr.split()[0] in subj for _, _, subj, _, _ in src.CLARIFICATIONS)
                for pr, r in con.items() if not r["feasible"])
    checks = [
        ("every topic has a named authority", not auth["gaps"]),
        ("every requirement has an official source", "Z-011" not in fr),
        ("every source read in the current edition",
         not any("superseded" in "; ".join(v) for v in fr.values())),
        ("research records second-checked", not res["weak"]),
        ("register rows complete", len(fld["full"]) == 6),
        ("each requirement has an independent approver", not rac["issues"]),
        ("no conflict without a written request", asked),
        ("interpretations in writing", not itp["oral"]),
        ("clarifications answered within 30 days", not cl["old"]),
        ("financial-close requirements verified", not gt["financial close"]),
        ("ownership scenario decided before the search",
         src.OWNERSHIP_BASE in src.OWNERSHIP),
        ("a trace closed end to end", not tr["gaps1"]),
    ]
    ok = sum(v for _, v in checks)
    lines = ["compliance-readiness review at the design stage (2027-03-01)"]
    lines += [f"  [{'x' if v else ' '}] {t}" for t, v in checks]
    lines += [f"  {ok} of {len(checks)} in place: the method exists (register, requests,",
              "  ownership); the evidence behind it is thin - sources,",
              "  approvals and written interpretations"]
    emit("int_review", lines)
    return dict(ok=ok, n=len(checks))


def basis() -> None:
    lines = ["compliance-method basis of Plant P (D-058):",
             "  1 one register, one row per requirement: source type, issuer,",
             "    clause, edition, status (verified / project-dependent /",
             "    to-confirm), applicability, consequence, evidence, owner,",
             "    approver, date verified, revision",
             "  2 the strictest applicable source governs; rank decides only",
             "    a true conflict, and a conflict goes out as a written request",
             "  3 sources read in the official language and current",
             "    consolidated text; checked again before each gate and",
             "    monthly by a named person",
             "  4 every interpretation the design depends on is in writing",
             "  5 a requirement closes only with accepted evidence and the",
             "    named approver's decision; Z-001 waits on DEV-11 (TSOZ)",
             "  6 the ownership scenario of the line is an input, decided",
             "    before the search (O1 in the base)",
             "  7 finance and fiscal items: verified in the base case,",
             "    to-confirm only as sensitivities, each closed by a dated",
             "    opinion of a qualified local reviewer",
             "  8 the method, not Country Z's values, carries to ch 55-58"]
    emit("int_basis", lines)


if __name__ == "__main__":
    by_hand()
    review()
    basis()
