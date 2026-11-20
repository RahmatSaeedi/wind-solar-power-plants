"""Chapter 32 - three integrated Plant P examples: two safety results by
hand, the safety and emergency package in numbers, and the safety, fire
and emergency basis (D-036).

Run from the project root:   python -m companion.ch32.integrated
Writes companion/ch32/expected/int_*.txt.
"""
from __future__ import annotations

from companion.ch32 import sources as src
from companion.ch32.common import emit
from companion.ch32 import examples_d, lab_c, lab_f, lab_h
from plantp import safety as sf


def by_hand() -> None:
    r, lo, hi = sf.incident_rate(11, 1_050_000)
    auto = sf.autonomy_minutes(src.TANK["reserve_m3"], 3000)
    lines = ["two safety results checked by hand",
             f"  recordable rate: 11 x 200,000 / 1,050,000 = {11 * 200_000 / 1_050_000:.2f};"
             f" code {r:.2f}",
             f"  reserve autonomy: 180 m3 x 1,000 / 3,000 L/min = {180_000 / 3000:.0f} min;"
             f" code {auto:.0f}",
             "  the interval of the rate (1.18-3.47) has no hand form -",
             "  it is checked against a table of the chi-square law"]
    del lo, hi
    emit("int_hand", lines)


def package() -> None:
    t = examples_d.arrival()
    reg = lab_c.REGISTER
    high = sum(1 for r in reg if sf.risk_band(sf.risk_score(r[3], r[4])) == "high")
    jha_after = max(sf.risk_score(r[5], r[6]) for r in lab_f.JHA if r[0][0] != "6")
    lines = ["the safety, fire and emergency package of Plant P in numbers",
             f"  fire scenarios in the register: {len(reg)}, of them high: {high}",
             f"  protection matrix: {len(lab_c.MATRIX)} areas x 6 questions",
             f"  cause-and-effect: {len(lab_c.INPUTS)} inputs, {len(lab_c.OUTPUTS)} outputs;"
             f" draft findings {len(lab_c.check(lab_c.DRAFT, lab_c.OUTPUTS))}",
             f"  fire-service arrival P50 {sorted(t)[len(t) // 2]:.0f} min; reserve 60 min",
             f"  JHA of the yaw motor: 9 steps, residual at most {jha_after} after revision",
             f"  emergency scenarios: {len(lab_h.SCENARIOS)}; exercise gaps found: 8",
             "  the package is mostly registers, matrices and plans: the",
             "  numbers in it are few, sourced and marked placeholders",
             "  where the strategy or the authority must set them"]
    emit("int_package", lines)


def basis() -> None:
    lines = ["D-036 safety, fire and emergency basis of Plant P (teaching)",
             "  1 safety management: teaching 5 x 5 matrix, hierarchy of",
             "    controls, permit office with shared isolation points,",
             "    prequalification with a minimum on every criterion",
             "  2 hazards: PV DC treated as energised in daylight; restraint",
             "    or retracting devices where clearance is short; summer",
             "    early shifts; wind chill on nacelle roofs; site speeds",
             "  3 fire: register F01-F09, matrix by area, C&E rules (alarm",
             "    for every input, own location, position feedback);",
             "    methods, rates and separations from the fire strategy",
             "    and the authority (U-105, U-110)",
             "  4 water: 180 m3 reserve lasts 60 min at the placeholder",
             "    rate; the fire service arrives after it in about 31 %",
             "    of draws - tankers and meeting point agreed in advance",
             "  5 lifecycle: evidence ladder, test intervals by PFD,",
             "    impairment register, management of change, restore",
             "  6 welfare: town housing or a camp with its own water (a",
             "    camp would use 61 % of the wells); buses; school hours",
             "  7 emergency: 12 scenarios with levels; two rescuers on",
             "    every crew; night work only with the team on site;",
             "    satellite phones in duty vehicles; exercise programme",
             "  8 findings of the later lessons: the control building as",
             "    drawn loses the race with smoke (second exit, drilled",
             "    'leave now'); AEDs in every vehicle; gates too tight for",
             "    a fire appliance (familiarisation drive); the erection",
             "    contractor's rate above its funnel band; 4 barriers to a",
             "    container explosion leave the teaching target missed",
             "  open: fire strategy and authority acceptance (U-105,",
             "    U-110); medical provider's response times (U-111);",
             "    findings: ch 29 construction water rises to 87,460 m3",
             "    with ch 22's workforce (corrected there)"]
    emit("int_basis", lines)


if __name__ == "__main__":
    by_hand()
    package()
    basis()
