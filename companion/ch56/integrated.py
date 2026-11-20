"""Chapter 56, three integrated examples for Plant P - Afghanistan: numbers
by hand, the dossier readiness review and the basis D-060.

Run from the project root:   python -m companion.ch56.integrated
Writes companion/ch56/expected/int_*.txt.
"""
from __future__ import annotations

import contextlib
import io

from companion.ch56 import run
from companion.ch56 import sources as src
from companion.ch56.common import emit


def main() -> None:
    with contextlib.redirect_stdout(io.StringIO()):
        r = run.main()
    tot = r["status"]["tot"]
    n = len(src.FACTS)
    a = r["approvals"]
    emit("int_hand", [
        "three numbers by hand",
        f"  verified share: {tot['verified']} / {n} = {tot['verified'] / n:.0%}",
        "  branch 1: S1 2 + S2 2 + S3 3 + S8 3 = 10.0 months",
        "  branch 2: S1 2 + S2 2 + S6 4 + S7 2 = 10.0 months"
        f" (program: {a['total']:.1f})",
        f"  grid inputs given: {13 - len(r['grid']['missing'])} / 13 ="
        f" {r['grid']['complete']:.0%}"])
    checks = [
        ("approval route sourced from current official pages", True),
        ("application of the 2016 law confirmed", False),
        ("grid island and connection voltage named by DABS", False),
        ("connection requirements in writing", False),
        ("written grid-data request prepared", True),
        ("water route sourced (guideline)", True),
        ("land body and title confirmed", False),
        ("import inspection standards known", False),
        ("tariff, currency and payment terms known", False),
        ("all sanctions regimes reviewed by counsel", False),
        ("ESIA category confirmed", False),
        ("local service plan for turbines and inverters", False),
    ]
    ok = sum(v for _, v in checks)
    emit("int_review", ["Plant P - Afghanistan: dossier readiness on 2026-11-17"]
         + [f"  [{'x' if v else ' '}] {t}" for t, v in checks]
         + [f"  {ok} of {len(checks)}: the route, the water permit and the data request",
            "  stand on sources; the law in force, the grid, land, payment and",
            "  service capability do not"])
    emit("int_basis", [
        "Afghanistan dossier basis of Plant P (D-060):",
        f"  1 {n} statements AF-01..AF-{n:02d}: {tot['verified']} verified,",
        f"    {tot['project-dependent']} project-dependent, {tot['to-confirm']} to-confirm",
        "  2 route: investment committee, Economic Commission, contract",
        "    with DABS; the 2016 licence regime kept as to-confirm",
        "  3 a pre-2021 text is designed to AND labelled to-confirm until",
        "    its application is confirmed in writing",
        "  4 first grid question: which island; 110 or 220 kV as DABS names",
        "  5 equipment chosen with local service capability and import",
        "    route; unknowns never count as a pass",
        "  6 base case: no service revenue; no base case without tariff,",
        "    currency and payment terms; payment security sought",
        "  7 land and title reviewed in the field before any contract",
        "  8 review by engineers and regulatory specialists familiar with",
        "    current practice in Afghanistan before any use or publication"])


if __name__ == "__main__":
    main()
