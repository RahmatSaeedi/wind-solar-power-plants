"""Chapter 59, three integrated examples: numbers by hand, the readiness
review for financial close, and the dossier basis D-063.

Run from the project root:   python -m companion.ch59.integrated
"""
from __future__ import annotations

import contextlib
import io

from companion.ch59 import cases, defense, dossier, index
from companion.ch59.common import emit


def main() -> None:
    with contextlib.redirect_stdout(io.StringIO()):
        ix = index.index()
        y = dossier.yield_statement()
        ec = dossier.economics()
        sc = dossier.schedule()
        ch = defense.change()
        fi = cases.h_finance()
        ho = cases.j_handover()
    emit("int_hand", [
        "three numbers by hand",
        f"  P90 one year: {y['net']:.2f} - 1.2816 x {y['one']:.2f} = {y['p90']:.1f} GWh",
        f"  dossier: {ix['docs']} documents, {ix['dec']} decisions, {ix['unk']} unknowns"
        " named",
        f"  schedule: 12 + 18 + 9 + 14 + 6 + 4 = {sc['total']:.0f} months to COD"])
    checks = [
        ("every chapter and decision in a dossier item", not ix["missing_ch"] and not ix["missing_dec"]),
        ("yield recomputed and equal to D-019, D-020", abs(y["net"] - 295.14) < 0.01),
        ("design interfaces explained (N-1 accepted)", True),
        ("debt case holds at P90 (min DSCR >= 1.05)", fi["out"]["P90 one-year energy"][0] >= 1.05),
        ("all change cases above the default covenant",
         min(v[1] for v in ch.values()) >= 1.05),
        ("country appendix of the project country closed", False),
        ("grid offer and connection agreement signed", False),
        ("ESIA approved, raptor survey done", False),
        ("land agreements complete", False),
        ("asset register clean for CMMS import", ho["n"] == 0),
        ("EPC and supply contracts with risk allocation", False),
        ("independent engineer's report on the dossier", False),
    ]
    ok = sum(v for _, v in checks)
    emit("int_review", ["Plant P: readiness for financial close (teaching review)"]
         + [f"  [{'x' if v else ' '}] {t}" for t, v in checks]
         + [f"  {ok} of {len(checks)}: the engineering case holds; the conditions",
            "  that remain are permits, land, the grid offer, contracts and",
            "  the independent review - each an owner and a date"])
    emit("int_basis", [
        "capstone dossier basis of Plant P (D-063):",
        f"  1 the 14-item dossier is rebuilt from the chapters ({ix['docs']} documents,",
        f"    {ix['dec']} decisions, {ix['unk']} unknowns named); nothing is retyped",
        f"  2 energy P50 {y['net']:.1f} GWh, P90 one year {y['p90']:.1f} GWh at the POC",
        f"  3 economics: equity IRR {ec['irr']:.1%}, min DSCR {ec['dscr']:.2f},"
        f" LCOE {ec['lcoe']:.1f} u/MWh",
        f"  4 schedule {sc['total']:.0f} months to COD; wind campaign, permits and",
        "    turbines on the critical path",
        "  5 every major decision defended with evidence, uncertainty and",
        "    approver; four change cases recomputed",
        "  6 reliability, forecasting, export, finance, social and handover",
        "    cases each with a computed check and an open-item list",
        "  7 the base case books no service revenue; S0 keeps space for a",
        "    later battery (D-025)",
        "  8 every country use goes through its appendix (ch 55-57) and a",
        "    qualified local review"])


if __name__ == "__main__":
    main()
