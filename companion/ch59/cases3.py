"""Chapter 59, more dossier lessons: the data pack's assumption labels,
triage of the unknowns, the measured PV degradation in the finance model,
the footprint statement, and the three countries' design drivers.

Run from the project root:   python -m companion.ch59.cases3
"""
from __future__ import annotations

import collections
import contextlib
import io

import numpy as np

from companion.ch59 import common  # noqa: F401  (path)
from companion.ch59.common import emit


def a_ledger() -> dict:
    from plantp import datapack
    a = datapack.load_assumptions()
    st = a["status"].value_counts().to_dict()
    by_ch = a["introduced_in"].value_counts().sort_index()
    lines = [f"the data pack's assumption ledger (release 1.1.0): {len(a)} rows",
             "  status: " + ", ".join(f"{k} {v}" for k, v in st.items()),
             "  introduced in: " + ", ".join(f"{k} {v}" for k, v in by_ch.items()),
             "  measured, vendor or verified: "
             f"{sum(v for k, v in st.items() if k in ('measured', 'vendor', 'verified'))}",
             "  a fictional plant ends the book with no measured input in its",
             "  pack: every row is a place where a real project puts evidence"]
    emit("a_ledger", lines)
    return dict(n=len(a), st=st)


def a_triage() -> dict:
    from companion.ch59 import index
    with contextlib.redirect_stdout(io.StringIO()):
        ix = index.index()
    seen = collections.Counter()
    for n, title, chs, dec, docs, unk in ix["rows"]:
        for u in unk:
            seen[u] += 1
    multi = sorted(u for u, k in seen.items() if k >= 2)
    by_item = {r[0]: len(r[5]) for r in ix["rows"]}
    top = sorted(by_item.items(), key=lambda kv: -kv[1])[:4]
    lines = [f"unknowns named in the dossier: {len(seen)}; in two items or more: {len(multi)}",
             "    " + ", ".join(multi[:10]),
             "    " + ", ".join(multi[10:20]) if len(multi) > 10 else "",
             "  items with most unknowns: " + ", ".join(f"{k} ({v})" for k, v in top),
             "  triage: an unknown shared by two items is closed first; then",
             "  those of the next gate (ch 59 A); the rest are dated conditions"]
    emit("a_triage", [x for x in lines if x.strip()])
    return dict(n=len(seen), multi=multi, top=top)


def c_degradation() -> dict:
    """ch 53 measured PV degradation 0.37 %/yr against the 0.5 %/yr of the
    ch 21 model: the energy path through the life, debt held."""
    from companion.ch21 import model
    from companion.ch21 import sources as s21
    b = model.run()
    n = s21.TERMS["years"]
    path = ((1 - 0.0037) / (1 - 0.005)) ** np.arange(n)
    pv_share = 108.36 / 295.14                    # PV share of the energy (ch 15 balance)
    mixed = 1 + pv_share * (path - 1)
    r = model.run(energy_path=mixed, debt=b["debt"])
    gain = float((np.asarray(r["energy"]) - np.asarray(b["energy"])).sum())
    lines = ["PV degradation measured in operation (ch 53) in the finance model",
             f"  model 0.50 %/yr, measured 0.37 %/yr on the PV share ({pv_share:.0%} of energy)",
             f"  energy over {n} years: {gain:+.1f} GWh; year {n}: {mixed[-1] - 1:+.2%}",
             f"  equity IRR {b['equity_irr']:.2%} -> {r['equity_irr']:.2%};"
             f" NPV {b['npv']:,.0f} -> {r['npv']:,.0f} k u",
             "  small for the debt (the early years barely move), worth more",
             "  to the tail: the finding goes back to ch 15 and ch 21"]
    emit("c_degradation", lines)
    return dict(gain=gain, irr0=b["equity_irr"], irr1=r["equity_irr"], npv0=b["npv"],
                npv1=r["npv"])


def h_footprint() -> dict:
    from companion.ch33 import lab_i
    from companion.ch33 import sources as s33
    from plantp import envsocial as es
    out = {}
    lines = ["lifecycle footprint per kWh, boundary: cradle to grave of the plant",
             "(ch 33 inventory and operation, Monte Carlo of the factors)",
             f"  {'case':4s} {'GWh/yr':>7s} {'P5':>6s} {'P50':>6s} {'P95':>6s}  g CO2e/kWh"]
    for case, items in lab_i._cases().items():
        mc = es.inventory_mc(items)
        mc = mc * (1 + s33.OPERATION["replacements_share"]) + lab_i._operation_t() * 1000
        kwh = s33.ENERGY_GWH[case] * 1e6 * s33.LIFE_YEARS
        g = mc * 1000 / kwh
        p5, p50, p95 = np.percentile(g, [5, 50, 95])
        out[case] = (p5, p50, p95)
        lines.append(f"  {case:4s} {s33.ENERGY_GWH[case]:7.1f} {p5:6.1f} {p50:6.1f} {p95:6.1f}")
    lines += ["  the battery case overlaps the plant without it: the footprint",
              "  is reported with its boundary and range, and it does not",
              "  decide the battery (D-037); avoided emissions are kept apart"]
    emit("h_footprint", lines)
    return out


def y_countries() -> dict:
    from companion.ch55 import engine as en
    from companion.ch55 import sources as s55
    from companion.ch56 import sources as s56
    from companion.ch57 import sources as s57
    quiet = lambda *a, **k: None
    rows = []
    for name, s, volt in (("Iran", s55, "63 or 230 kV (132 no source)"),
                          ("Afghanistan", s56, "110 or 220 kV (island first)"),
                          ("Tajikistan", s57, "220 kV at the tender site")):
        ap = en.approvals(s, quiet)
        cn = s.CERT_NEED
        rows.append((name, volt, cn["ambient_max_c"], cn["altitude_m"], ap["total"],
                     len(s.FACTS)))
    lines = ["what each country changes in the design of Plant P (ch 55-57)",
             f"  {'country':12s} {'connection':30s} {'amb C':>5s} {'alt m':>6s} {'approvals':>9s}"]
    for name, volt, amb, alt, m, nf in rows:
        lines.append(f"  {name:12s} {volt:30s} {amb:5.0f} {alt:6.0f} {m:7.1f} mo")
    lines += ["  plus: Iran - INSO certificates for transformers, cables, batteries;",
              "  Afghanistan - import route and local service; Tajikistan - seismic",
              "  zone and the curtailment clause; site values and durations are",
              "  teaching values of the chapters"]
    emit("y_countries", lines)
    return dict(rows=rows)


def main() -> dict:
    out = {}
    for f in (a_ledger, a_triage, c_degradation, h_footprint, y_countries):
        out[f.__name__] = f()
    return out


if __name__ == "__main__":
    main()
