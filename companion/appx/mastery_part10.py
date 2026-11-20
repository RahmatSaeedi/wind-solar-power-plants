"""Appendix X - answers of the Part X diagnostic mastery test (chapters
54-59): the compliance method, the country dossiers, standards literacy and
the capstone dossier - with the numbers computed from the chapters'
companion code.

Run from the project root:   python -m companion.appx.mastery_part10
Writes companion/appx/expected/mastery_part10.txt.
Data pack 1.1.0 (synthetic), decisions D-058 to D-063.
Values marked (test) are used only here.
"""
from __future__ import annotations

import math
from datetime import date

from scipy.stats import gamma, norm

from companion.appx.common import emit
from plantp import appraisal, compliance, dossier, stdreg

OUT: list[str] = []


def p(pid: str, text: str) -> None:
    OUT.append(f"{pid}: {text}")


def method() -> None:
    reqs = [dict(id="GC-1", source_type="grid code", parameter="frt_ms", kind="min", value=150),
            dict(id="UR-4", source_type="utility rule", parameter="frt_ms", kind="max", value=100),
            dict(id="OS-9", source_type="owner spec", parameter="frt_ms", kind="min", value=120)]
    c = compliance.conflicts(reqs, "frt_ms")
    p("M137", f"ride-through at 0 pu (test): every source allows {c['lo']} to {c['hi']} ms,"
              f" feasible {c['feasible']} - an empty range is a written question,"
              " not a designer's choice")
    q100 = 100 * math.tan(math.acos(0.95))
    q20 = 20 * math.tan(math.acos(0.95))
    p("M138", f"pf 0.95 at the POC: {q100:.2f} Mvar at 100 MW, {q20:.2f} at 20 MW;"
              f" a fixed +/-{q100:.0f} Mvar rule asks {q100 / q20:.0f} times more at 20 MW"
              " - the form of the rule is read from the official text")
    lam, months = 0.5, 18
    pr = 1 - math.exp(-lam * months / 12)
    p("M139", f"rule changes 0.5 a year (test), 18 months to energisation:"
              f" P(at least one) = {pr:.0%} - the register is watched, not filed")
    trace = dict(source="Z-001 GCZ 2024 cl 5.2", design="CAL-0014", procurement="SPC-0007",
                 construction="REG-0031", test="REP-0010", approval=None, retained=None)
    gaps = compliance.trace_gaps(trace)
    p("M140", f"trace of one requirement over {len(compliance.STAGES)} stages: missing"
              f" {', '.join(gaps)} - a passed test is not compliance until"
              " it is accepted and its evidence kept")


def countries() -> None:
    cons = {"ambient_c": ("min", 48), "altitude_m": ("min", 1800)}
    opts = {"inverter A": {"ambient_c": 50, "altitude_m": 2000},
            "inverter B": {"ambient_c": 45, "altitude_m": None}}
    r = dossier.compare(opts, cons)
    p("M141", "equipment against site needs (test): "
              + "; ".join(f"{k} ok {v['ok']} fails {v['fails']} unknown {v['unknown']}"
                          for k, v in r.items()) + " - an unknown is never a pass")
    tasks = {"S1 eligibility": (2, []), "S2 permit": (3, ["S1 eligibility"]),
             "S3 environment": (5, ["S1 eligibility"]), "S4 grid": (4, ["S2 permit"]),
             "S5 contract": (2, ["S3 environment", "S4 grid"])}
    t, crit, slack = appraisal.critical_path(tasks)
    p("M142", f"approvals (test): {t:.0f} months, critical {' > '.join(crit)};"
              f" S3 slack {slack['S3 environment']:.0f} month(s) - a to-confirm step"
              " on the critical path gets the first letter")
    facts = [dict(id="X-01", doc_date=date(2011, 2, 23)), dict(id="X-02", doc_date=date(2024, 11, 24)),
             dict(id="X-03", doc_date=None), dict(id="X-04", doc_date=date(2023, 6, 1))]
    st = dossier.stale(facts, date(2026, 11, 17))
    p("M143", "sources older than 3 years or undated on 2026-11-17 (test): "
              + ", ".join(f"{i} {'undated' if a is None else f'{a:.1f} y'}" for i, a in st))
    from companion.ch55 import sources as ir
    from companion.ch56 import sources as af
    from companion.ch57 import sources as tj
    shares = []
    for m in (ir, af, tj):
        n = len(m.FACTS)
        v = sum(1 for f in m.FACTS if f["status"] == "verified")
        shares.append(f"{m.COUNTRY} {v}/{n} = {v / n:.0%}")
    p("M144", "verified share of the three dossiers: " + ", ".join(shares)
              + " - the rest is project-dependent or to-confirm, each with an addressee")


def standards() -> None:
    cat = {"IEC 62548-1": [(2023, "IEC 62548-1:2023", "edition"),
                           (2025, "Amd 1:2025", "amendment")]}
    dated = stdreg.resolve("IEC 62548-1:2023", cat)
    undated = stdreg.resolve("IEC 62548-1", cat)
    p("M145", f"dated reference -> {', '.join(dated)}; undated -> {', '.join(undated)}"
              " - a contract is written with dated references")
    s = ["The transformer shall be type-tested to IEC 60076-2:2011.",
         "Cable trays should have adequate spare space.",
         "The contractor may propose a different layout."]
    forms = [stdreg.verbal_form(x) for x in s]
    p("M146", "verbal forms: " + "; ".join(f"{k}{' (vague: ' + ', '.join(v) + ')' if v else ''}"
                                           for k, v in forms))
    n = math.ceil(math.log(0.05) / math.log(0.99))
    p("M147", f"zero failures in n units shows < 1 % defective at 95 %: n = {n}")
    meas, lim, u = 64.2, 65.0, 1.6
    risk = 1 - norm.cdf((lim - meas) / (u / 2))
    p("M148", f"winding rise {meas} K, limit {lim} K, U = {u} K (k = 2): simple rule"
              f" {'passes' if meas <= lim else 'fails'}, guarded rule"
              f" {'passes' if meas + u <= lim else 'fails'}; chance the true rise"
              f" exceeds the limit {risk:.0%} - the contract names the rule")


def capstone() -> None:
    p50, sig = 295.14, 14.99
    p90 = p50 - norm.ppf(0.9) * sig
    p("M149", f"P90 one year = {p50} - {norm.ppf(0.9):.4f} x {sig} = {p90:.1f} GWh at the POC")
    a, b = 2.0 + 3, 4.0 + 20.0                  # gamma prior (2, 4) + evidence
    lo, hi = gamma.ppf([0.05, 0.95], a, scale=1 / b)
    p("M150", f"prior 0.5 /yr worth 4 unit-years, then 3 failures in 20 unit-years (test):"
              f" posterior mean {a / b:.3f} /yr, 90 % interval {lo:.3f} to {hi:.3f}")
    w, s_ = 10.3, 3.0
    ind = math.hypot(w, s_)
    cor = math.sqrt(w * w + s_ * s_ + 2 * 0.3 * w * s_)
    p("M151", f"day-ahead error wind {w} MW, PV {s_} MW: plant {ind:.2f} MW if"
              f" independent, {cor:.2f} MW with correlation 0.3 (test) - errors add as"
              " RSS in MW, not as percentages")
    from companion.ch59 import dossier as d59
    tasks = {k: (float(dd), pre) for k, (dd, pre) in d59.TASKS.items()}
    t, crit, slack = appraisal.critical_path(tasks)
    c1 = slack["C1 civil works"]
    late = dict(tasks)
    late["C1 civil works"] = (tasks["C1 civil works"][0] + 3, tasks["C1 civil works"][1])
    t3 = appraisal.critical_path(late)[0]
    p("M152", f"capstone plan {t:.0f} months; civil works slack {c1:.0f} months;"
              f" civil works 3 months late -> {t3:.0f} months - slack is spent"
              " before the end date moves")


def main() -> None:
    method()
    countries()
    standards()
    capstone()
    emit("mastery_part10", ["Part X diagnostic test - computed answers"] + OUT)


if __name__ == "__main__":
    main()
