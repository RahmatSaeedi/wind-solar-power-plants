"""Chapter 55, three integrated examples for Plant P - Iran, the dossier
review and the basis D-059, and the numerical answers P01-P24.

Run from the project root:   python -m companion.ch55.integrated
Writes companion/ch55/expected/int_*.txt and solutions.txt.
"""
from __future__ import annotations

import contextlib
import io

from companion.ch55 import run
from companion.ch55 import sources as src
from companion.ch55.common import emit


def quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        return run.main()


def by_hand(r: dict) -> None:
    tot = r["status"]["tot"]
    n = len(src.FACTS)
    a = r["approvals"]
    lines = ["three numbers by hand",
             f"  verified share: {tot['verified']} / {n} = {tot['verified'] / n:.0%}",
             "  longest approval path: S1 2 + S2 4 + S3 0.5 + S4 2 + S8 3 ="
             f" {a['total']:.1f} months",
             f"  connection path S1 + S5 + S6 = 2 + 6 + 2 = 10.0 months:"
             f" slack {a['slack']['S5']:.1f} months",
             f"  grid inputs given: {12 - len(r['grid']['missing'])} / 12 ="
             f" {r['grid']['complete']:.0%}"]
    emit("int_hand", lines)


def review(r: dict) -> dict:
    checks = [
        ("every institution named with a source", r["status"]["tab"]["A"]["to-confirm"] == 0),
        ("the framework bylaw in force on the project date", False),
        ("connection voltage confirmed", False),
        ("grid-code documents identified", False),
        ("written grid-data request prepared", True),
        ("land route and lease conditions sourced", True),
        ("environmental route sourced and current", False),
        ("mandatory standards identified for each item", False),
        ("sale route and its legal basis sourced", True),
        ("PPA terms known", False),
        ("sanctions reviewed by qualified counsel", False),
        ("community and heritage obligations sourced", False),
    ]
    ok = sum(v for _, v in checks)
    lines = ["Plant P - Iran: dossier readiness on 2026-11-17"]
    lines += [f"  [{'x' if v else ' '}] {t}" for t, v in checks]
    lines += [f"  {ok} of {len(checks)}: the framework, land and sale routes have",
              "  sources; the technical connection rules, the current form of",
              "  the bylaw and the contract terms do not - those are the",
              "  written questions of section D"]
    emit("int_review", lines)
    return dict(ok=ok, n=len(checks))


def basis() -> None:
    lines = ["Iran dossier basis of Plant P (D-059):",
             f"  1 {len(src.FACTS)} statements, each with status and source"
             f" (IR-01..{len(src.FACTS)});",
             f"    {sum(f['status'] == 'verified' for f in src.FACTS)} verified,"
             f" {sum(f['status'] == 'project-dependent' for f in src.FACTS)}"
             " project-dependent,"
             f" {sum(f['status'] == 'to-confirm' for f in src.FACTS)} to-confirm",
             "  2 counterparty SATBA under Art 61; IGMC stability standards to",
             "    be obtained; regional company and Tavanir for connection",
             "  3 land through SATBA and Agriculture Jihad; lease cap 20 %;",
             "    one year to start works; foreign eligibility to confirm",
             "  4 environment: DOE inquiry under the 1402 bylaw while it is in",
             "    force; hybrid-vs-two-plants reading and the 1405 bylaw to confirm",
             "  5 132 kV is a teaching assumption until the regional company",
             "    names the connection voltage",
             "  6 base case: no service revenue; sale route as scenarios until",
             "    PPA terms are known; sanctions by qualified counsel",
             "  7 21 written questions to 15 addressees (section D)",
             "  8 review by engineers and regulatory specialists familiar with",
             "    current practice in Iran before any use or publication"]
    emit("int_basis", lines)


def solutions(r: dict) -> None:
    tot = r["status"]["tot"]
    a = r["approvals"]
    g = r["grid"]
    cert_not = sum(1 for x in r["cert"] if x[1] != "shown")
    tr = r["traces"]
    out = [
        f"P01 facts: {len(src.FACTS)}; verified {tot['verified']}, project-dependent"
        f" {tot['project-dependent']}, to-confirm {tot['to-confirm']}",
        f"P02 to-confirm resting on secondary sources only: {r['status']['sec']}",
        f"P03 topic with most to-confirm: A ({r['status']['tab']['A']['to-confirm']}"
        f" of {sum(r['status']['tab']['A'].values())})",
        f"P04 undated sources: {sum(1 for _, x in r['stale'] if x is None)};"
        f" older than 3 years: {sum(1 for _, x in r['stale'] if x is not None)}",
        f"P05 approval path (teaching): {a['total']:.1f} months",
        f"P06 critical path: {' > '.join(a['crit'])}",
        f"P07 steps not verified: {len(a['tc'])}; on the critical path:"
        f" {', '.join(a['tcc'])}",
        f"P08 slack of the connection studies: {a['slack']['S5']:.1f} months",
        f"P09 grid inputs complete: {g['complete']:.0%}; missing {len(g['missing'])}",
        f"P10 certificate items not shown: {cert_not} of {len(r['cert'])}",
        f"P11 open stages: IR-43 {len(tr['IR-43'])}, IR-05 {len(tr['IR-05'])}",
        f"P12 services verified: {r['services']['verified']} of 6",
        f"P13 finance items verified: {r['finance']['verified']} of 9",
        f"P14 open issues: {sum(r['issues'].values())} to {len(r['issues'])} addressees",
        "P15 lease cap: 20 % of the regional land value a year (IR-24)",
        "P16 EIA rule of the 1402 bylaw: none above 100 MW, DOE inquiry (IR-43)",
        "P17 DOE answer period: one week; silence = consent (amendment)",
        "P18 bylaw validity: two years from entry into force (IR-10)",
        "P19 renewables target of the amendment: 30,000 MW (IR-11)",
        "P20 mandatory import list for inverters: up to 5 kW (IR-28)",
        "P21 if S5 takes 8 months: path 2 + 8 + 2 = 12.0 > 11.5 months",
        "P22 hybrid as two plants: 60 and 50 MW, each below 100 MW",
        "P23 if the bylaw lapsed: IR-23, 24, 43, 45, 46 need a new source",
        "P24 readiness review: see int_review",
    ]
    emit("solutions", out)


if __name__ == "__main__":
    res = quiet()
    by_hand(res)
    review(res)
    basis()
    solutions(res)
