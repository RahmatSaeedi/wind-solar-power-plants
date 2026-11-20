"""Chapter 57, three integrated examples for Plant P - Tajikistan: numbers
by hand, the dossier readiness review and the basis D-061.

Run from the project root:   python -m companion.ch57.integrated
Writes companion/ch57/expected/int_*.txt.
"""
from __future__ import annotations

import contextlib
import io

from companion.ch57 import run
from companion.ch57 import sources as src
from companion.ch57.common import emit


def main() -> None:
    with contextlib.redirect_stdout(io.StringIO()):
        r = run.main()
    tot = r["status"]["tot"]
    n = len(src.FACTS)
    a = r["approvals"]
    d = {k: v["months"] for k, v in src.APPROVALS.items()}
    emit("int_hand", [
        "three numbers by hand",
        f"  verified share: {tot['verified']} / {n} = {tot['verified'] / n:.0%}",
        f"  critical path: S1 {d['S1']:.0f} + S6 {d['S6']:.0f} + S8 {d['S8']:.0f}"
        f" + S9 {d['S9']:.0f} = {d['S1'] + d['S6'] + d['S8'] + d['S9']:.1f} months"
        f" (program: {a['total']:.1f})",
        f"  grid inputs given: {13 - len(r['grid']['missing'])} / 13 ="
        f" {r['grid']['complete']:.0%}"])
    checks = [
        ("connection, metering and SCADA rules sourced (Resolution 449)", True),
        ("route for large plants sourced (competitive procedure, PPA)", True),
        ("single buyer and dispatcher named", False),
        ("connection voltage and bay in technical conditions", False),
        ("ride-through and reactive values in writing", False),
        ("written grid-data request prepared", True),
        ("curtailment reading (rules vs model PPA) in writing", False),
        ("EIA rules under the new Environmental Code confirmed", False),
        ("energy-expertise issuer confirmed", False),
        ("seismic code values for equipment read", False),
        ("convertibility and repatriation reviewed by counsel", False),
        ("land use right route for the project company confirmed", False),
    ]
    ok = sum(v for _, v in checks)
    emit("int_review", ["Plant P - Tajikistan: dossier readiness on 2026-11-17"]
         + [f"  [{'x' if v else ' '}] {t}" for t, v in checks]
         + [f"  {ok} of {len(checks)}: the connection rules, the route and the",
            "  data request stand on sources; the counterparties, the values",
            "  of the grid requirements and the curtailment reading do not"])
    emit("int_basis", [
        "Tajikistan dossier basis of Plant P (D-061):",
        f"  1 {n} statements TJ-01..TJ-{n:02d}: {tot['verified']} verified,",
        f"    {tot['project-dependent']} project-dependent, {tot['to-confirm']} to-confirm",
        "  2 route: competitive procedure, investment agreement, PPA with",
        "    the single buyer (>= 15 years), technical conditions, SIB",
        "  3 connection rules of Resolution 449 designed in: SCADA, remote",
        "    curtailment, hourly forecasts, class 0.5S metering",
        "  4 connection level 220 kV as named in the technical conditions",
        "  5 equipment qualified to the site's seismic zone; transformer",
        "    anchors re-checked above the ch 30 basis",
        "  6 base case: summer curtailment uncompensated beyond the",
        "    permitted value until IN-02 is answered; no service revenue",
        "  7 two expertises (ecological, energy) on the critical path",
        "  8 review by engineers and regulatory specialists familiar with",
        "    current practice in Tajikistan before any use or publication"])


if __name__ == "__main__":
    main()
