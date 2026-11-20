"""Chapter 40 - three integrated Plant P examples: three factory numbers by
hand, the skid line in numbers, and the manufacturing quality basis D-044.

Run from the project root:   python -m companion.ch40.integrated
Writes companion/ch40/expected/int_*.txt.
"""
from __future__ import annotations

from companion.ch40 import examples_a, examples_b, lab_d
from companion.ch40 import sources as src
from companion.ch40.common import emit
from plantp import quality as qa


def by_hand() -> None:
    y = qa.rty([r[4] for r in src.ROUTE])
    t = qa.takt(4 * 40, 10)
    pa = qa.p_accept(20, 0, 0.05)
    lines = ["three factory numbers checked by hand",
             "  RTY = 0.97 x 0.99 x 0.99 x 0.95 x 0.98 x 0.94 x 0.99 x 0.92"
             f" x 1.00 = {y:.3f}",
             f"  takt = 4 weeks x 40 h / 10 skids = {t:.0f} h",
             f"  P(accept) of n = 20, c = 0 at 5 % defective = 0.95^20 = "
             f"{pa:.3f}",
             "  a hand check catches a yield entered as 95 instead of 0.95,",
             "  or a takt computed from calendar hours instead of shifts"]
    emit("int_hand", lines)


def line() -> None:
    r = examples_a.route()
    tb = examples_a.takt_balance()
    cap = examples_b.capability()
    found = lab_d.dossier_audit()
    tr = lab_d.defect_trace()
    good = cap["good tools (35 joints)"]
    lines = ["the PV station skid line in numbers",
             f"  79 touch hours a skid; RTY {r['rty']:.3f}; takt "
             f"{tb['takt']:.0f} h",
             f"  bottleneck S1 {tb['frames made']:.2f} h with frames made,"
             f" S3 {tb['frames bought']:.2f} h with frames bought",
             f"  joint resistance Cpk {good[2]:.2f} with good tools; the",
             "  drifted wrench put about 2 % of joints over the limit",
             f"  S-07 dossier: {len(found)} findings in 13 entries",
             f"  the escaped defect cost {tr['total']:.1f} k u; the actions"
             f" cut escapes {tr['before'] / tr['after']:.0f} times"]
    emit("int_line", lines)


def basis() -> None:
    lines = ["D-044 manufacturing quality basis of the PV station skids",
             "  1 route OP10-OP90 with a traveler per skid; frames bought",
             "    from a qualified maker (first-article inspection kept);",
             "    the line starts a week early - it takes 66 h to fill",
             "  2 PFMEA ranked by severity class, then S x O; four critical",
             "    characteristics, each with a control-plan row",
             "  3 ITP: functional test a hold; IR, relay injection and LV",
             "    busbar visual witnessed; records reviewed",
             "  4 torque: logged wrenches, shift checks, paint marks;",
             "    joint resistance on five joints a skid, all if one > 17",
             "  5 gauge: micro-ohmmeter with fixture (%GRR 11.5)",
             "  6 lugs: incoming plan n = 132, c = 3; die checked at press",
             "  7 genealogy: serial, lot, tool and person links (15 a skid)",
             "  8 dossier accepted on validity, not on 'pass' (lesson D)",
             "  9 burn-in of control boards only if a failure trips a block",
             " 10 relay injection on every skid (p 3 % > k1/k2 0.9 %); wiring",
             "    by an automatic tester from the design wiring list",
             " 11 crimp pull Cpk 0.94 - raise the mean (factorial) before",
             "    serial build; IR compared at 20 C only",
             "  open: the integrator's own capability data before award",
             "    (U-121); a second certified jointer before serial build"]
    emit("int_basis", lines)


if __name__ == "__main__":
    by_hand()
    line()
    basis()
