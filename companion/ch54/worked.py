"""Chapter 54, small worked examples (E01-E08) and the numerical answers of
the end-of-chapter problems (P01-P43), each computed from the chapter's
companion code.

Run from the project root:   python -m companion.ch54.worked
Writes companion/ch54/expected/worked.txt and solutions.txt.
"""
from __future__ import annotations

import math
from datetime import date

import numpy as np

from companion.ch54 import examples_a as ea
from companion.ch54 import examples_b as eb
from companion.ch54 import examples_e as ee
from companion.ch54 import examples_s as es
from companion.ch54 import integrated as ig
from companion.ch54 import lab_d
from companion.ch54 import sources as src
from companion.ch54.common import emit
from plantp import compliance as cp
from plantp import finance as fn


def small() -> None:
    t95 = math.tan(math.acos(0.95))
    out = [f"E01 Q at 60 MW for pf 0.95: {60 * t95:.2f} Mvar",
           f"E02 tan phi for pf 0.90: {math.tan(math.acos(0.90)):.3f}",
           f"E03 days CQ-04 has waited on {src.TODAY}:"
           f" {(src.TODAY - date(2026, 11, 15)).days}",
           f"E04 chance of a change within 2 years at 0.5 a year:"
           f" {1 - math.exp(-1.0):.0%}",
           f"E05 PV of 65 k u a year for 20 years at 7.5 %:"
           f" {fn.pv(np.full(20, 65.0), 0.075):,.0f} k u",
           f"E06 clause 7.1 in force on 2027-01-01:"
           f" {cp.consolidated(src.GCZ_CLAUSES, date(2027, 1, 1))['7.1'][0]}",
           f"E07 interest grossed up for 10 % withholding: {0.06 / 0.9:.2%}",
           f"E08 strictest of noise limits 40, 45, 48 dB(A):"
           f" {min(40, 45, 48)} dB(A)"]
    emit("worked", out)


def solutions() -> None:
    c = eb.clauses()
    con = ea.conflict_table()
    pre = ea.precedence()
    tr = eb.transition()
    au = eb.authorities()
    ap = ea.applicability()
    fr = ea.freshness()
    lg = ea.language()
    rs = eb.research()
    ow = eb.ownership()
    st = ea.status()
    cl = ea.clarifications()
    ed = ea.edition_change()
    fl = eb.fields()
    ra = eb.raci()
    rv = eb.revisions()
    it = eb.interpretations()
    so = lab_d.source()
    tc = lab_d.trace()
    dp = lab_d.disposition()
    ev = lab_d.evidence()
    rg = ee.register()
    pm = ee.premium()
    dpn = ee.depreciation()
    fx = ee.currency()
    rp = ee.repatriation()
    wh = ee.withholding()
    ad = ee.advisors()
    fm = es.forms()
    gt = es.gates()
    wt = es.watch()
    mx = es.matrix()
    rw = ig.review()
    hd = ig.by_hand()
    fx2, fx4 = fx["cases"][0.02], fx["cases"][0.04]
    out = [
        f"P01 binding pieces of the extract: {c['binding']} of {len(src.CLAUSES)}",
        f"P02 normative but vague: {', '.join(c['vague'])}",
        f"P03 governing night noise: {pre['gov']:.0f} dB(A)",
        f"P04 power factor every source allows: at least {con['power factor at POC']['lo']}",
        f"P05 ramp every source allows: at most {con['ramp rate']['hi']:g} %/min",
        "P06 conflict: " + ", ".join(k for k, v in con.items() if not v["feasible"]),
        f"P07 clauses that differ, filing vs energisation: {', '.join(tr['diff'])}",
        f"P08 authority topics not verified: {len(au['gaps'])} of {len(src.AUTHORITIES)}",
        f"P09 requirements that apply: {len(ap['apply'])}; outside: {', '.join(ap['out'])}",
        f"P10 requirements with source problems: {len(fr)} of {len(src.REQS)}",
        f"P11 read only in translation: {', '.join(lg['risky'])}",
        f"P12 research records with all four fields: {rs['full']} of {len(src.RESEARCH)}",
        f"P13 requirements added under O2 / O3: {ow[list(ow)[1]]} / {ow[list(ow)[2]]}",
        f"P14 status: verified {st['verified']}, project-dependent"
        f" {st['project-dependent']}, to-confirm {st['to-confirm']}",
        "P15 open past 30 days: " + ", ".join(f"{i} {d} d" for i, d in cl["old"]),
        f"P16 records to re-check after a grid-code edition: {len(ed)}",
        f"P17 register cells filled {fl['share']:.0%}, complete rows {len(fl['full'])} of 6",
        f"P18 preparer/reviewer/approver problems: {len(ra['issues'])}",
        f"P19 R2 to R3: {len(rv['changed'])} changes, added {', '.join(rv['added'])},"
        f" removed {', '.join(rv['removed'])}",
        f"P20 interpretations not in writing: {len(it['oral'])} of"
        f" {len(src.INTERPRETATIONS)}",
        f"P21 Q needed at 100 MW: {so['q100']:.2f} Mvar",
        f"P22 Q needed at 10 MW: {10 * math.tan(math.acos(0.95)):.2f} Mvar",
        f"P23 Z-001 open stages: {', '.join(tc['gaps1'])}",
        f"P24 Z-009 open stages: {len(tc['gaps2'])} of {len(cp.STAGES)}",
        f"P25 export cap where 30.6 Mvar meets pf 0.95: {dp['p_ok']:.1f} MW",
        f"P26 hours above the cap: {dp['hours']}, energy {dp['mwh']:,.0f} MWh",
        f"P27 lost revenue {dp['lost_k']:.0f} k u a year, {dp['pv_lost']:,.0f} k u"
        " over 20 years",
        f"P28 compensator 360 k u against the cap's {dp['pv_lost']:,.0f} k u:"
        f" {'compensator' if 360 < dp['pv_lost'] else 'cap'}",
        f"P29 closing evidence in hand: {sum(ok for *_, ok in ev)} of {len(ev)}",
        f"P30 finance items: verified {rg.get('verified', 0)}, project-dependent"
        f" {rg.get('project-dependent', 0)}, to-confirm {rg.get('to-confirm', 0)}",
        f"P31 premium: extra debt {pm['with_p']['debt'] - pm['base']['debt']:,.0f} k u;"
        f" min DSCR if never paid {pm['fails']['min_dscr']:.2f}",
        f"P32 five-year depreciation: equity IRR"
        f" {(dpn['fast']['equity_irr'] - dpn['base']['equity_irr']) * 100:+.2f}"
        f" points, min DSCR {dpn['fast']['min_dscr']:.2f}",
        f"P33 currency 2 %/yr: min DSCR {fx2['min']:.2f}, below 1.10 from year"
        f" {fx2['first']}, short from {fx2['short']}",
        f"P34 currency 4 %/yr: min DSCR {fx4['min']:.2f}",
        f"P35 dividends held 2 years: equity IRR {rp['irr0']:.2%} -> {rp['irr1']:.2%}",
        f"P36 withholding gross-up: rate {wh['rate']:.2%}, min DSCR {wh['w']['min_dscr']:.2f}",
        "P37 open items by reviewer: " + ", ".join(f"{k} {len(v)}" for k, v in
                                                 sorted(ad.items(), key=lambda kv:
                                                        -len(kv[1]))[:2]),
        f"P38 pf vs Q/Pmax at 20 MW: {fm['ratio']:.1f} times",
        f"P39 not verified at financial close: {', '.join(gt['financial close'])}",
        f"P40 change rate {wt['rate']:.2f} a year; before energisation {wt['p_conn']:.0%};"
        f" over 25 years {wt['life']:.0f}",
        "P41 disciplines with a to-confirm item: " + ", ".join(
            d for d, r in sorted(mx.items()) if r["to-confirm"]),
        f"P42 readiness review: {rw['ok']} of {rw['n']}",
        f"P43 by hand: Q {hd['q']:.2f} Mvar, cap {hd['p_ok']:.1f} MW",
    ]
    emit("solutions", out)


if __name__ == "__main__":
    small()
    solutions()
