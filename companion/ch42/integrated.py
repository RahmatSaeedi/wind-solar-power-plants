"""Chapter 42 - three integrated Plant P examples: a turbine's numbers by
hand, the fleet's manufacturing quality in numbers, and the turbine
component quality and acceptance basis D-046.

Run from the project root:   python -m companion.ch42.integrated
Writes companion/ch42/expected/int_*.txt.
"""
from __future__ import annotations

from companion.ch42 import examples_a, examples_b, examples_c, examples_e, lab_d
from companion.ch42 import sources as src
from companion.ch42.common import emit
from plantp import turbinemfg as tm


def by_hand() -> None:
    t = src.TURBINE
    pull = tm.insert_tension(t["flap_mnm"] * 1e6, 96, 3.2)
    lines = ["a turbine's numbers by hand",
             f"  insert pull = 4 x 15.4e6 / (96 x 3.2) = {pull / 1e3:.0f} kN "
             "against 320 kN preload",
             f"  drivetrain = 0.997 x 0.980 x 0.975 x 0.985 = "
             f"{0.997 * 0.980 * 0.975 * 0.985:.3f}",
             f"  back-to-back grid power = 5000 x (1/0.98^2 - 1) = "
             f"{tm.back_to_back_power(5000, 0.98):.0f} kW",
             f"  generator balance e = 2.5 / 121 = {2.5 / 121.0 * 1000:.1f} um",
             "  a hand check catches a moment in kN m read as MN m, an",
             "  efficiency chain that left out a stage, or a bench sized for",
             "  the test power instead of the losses"]
    emit("int_hand", lines)


def fleet() -> None:
    a = examples_a.allocation()
    r = examples_a.replacements()
    m = examples_b.matching()
    run = lab_d.runin()
    e = examples_e.torque()
    held = sum(1 for v in run.values() if v != "accept")
    lines = ["the twelve-turbine fleet's manufacturing quality in numbers",
             f"  downtime {a['hours']:.0f} h a turbine-year; major replacements "
             f"{a['big']:.0%} of it",
             f"  about {r['total']:.0f} crane campaigns in 25 years",
             f"  blade sets after sorting {m['sorted']:.2f} t m against "
             f"{m['random']:.2f} at random",
             f"  run-in: {held} of 10 gearboxes held, each with a diagnosis",
             f"  {e['total']:,} tightening operations a turbine; logged tools "
             f"take the expected loose joints from {e['manual']:.0f} to "
             f"{e['logged']:.1f}",
             "  the fleet's reliability starts in the factory records: each",
             "  number here is a record the plant can ask for"]
    emit("int_fleet", lines)


def basis() -> None:
    lines = ["D-046 turbine component quality and acceptance basis",
             "  1 blades: fibre fraction and voids on cap coupons; DSC cure",
             "    evidence; UT of caps and bond lines with a measured POD;",
             "    receptor resistance; weighing and set matching on record",
             "  2 root joint shown closed at the extreme load (the teaching",
             "    joint opens at 2 x operating - the maker's design decides)",
             "  3 hub castings judged by stress zones; NCR to the designer",
             "  4 gearboxes: back-to-back run-in with spectra at 1x, 2x and",
             "    mesh sidebands; oil sample; units held until re-run",
             "  5 generators: balance to the grade, insulation index before",
             "    energising, winding sensors tested; hot-climate cooling",
             "  6 torque-and-angle logged tools on every bolted joint;",
             "    500 h re-tension in commissioning",
             "  7 storage plan with shaft turning; field repairs only within",
             "    the maker's categories and weather windows",
             "  8 NCR authority by severity; late reports escalate",
             "  9 every blade: flap frequency with its weight (stiffness);",
             "    static-test deflection (+0.6 m) fed into the clearance",
             "    budget; saddles laid out against the target moment",
             " 10 gear case depth per heat to the edge-load floor (HT-43",
             "    held); alignment and case depth judged together",
             " 11 flange contact faces bare; settling in the re-tension",
             "    plan; nacelles weighed with their centre of gravity;",
             "    shock logs read before erection (N-05, N-11 checked)",
             " 12 efficiency from the back-to-back loss measurement; leak",
             "    tests with temperature; coating by mean and minimum",
             " 13 process FMEA ranked by severity sets the holds; nine",
             "    critical characteristics asked for at receipt",
             "  open: maker's type and component certificates and test",
             "    evidence for this configuration (U-123)"]
    emit("int_basis", lines)


if __name__ == "__main__":
    by_hand()
    fleet()
    basis()
