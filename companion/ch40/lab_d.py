"""Chapter 40, lab D (factory-quality lab = the worked examples): the
traveler of skid S-07 built from the route and the genealogy, an audit of
the fictional S-07 test dossier against its ITP, and the torque defect
traced from its cause to the plant consequence and the closure evidence.

Run from the project root:   python -m companion.ch40.lab_d
Writes companion/ch40/expected/d_*.txt.
Teaching values (A-438, A-440); a fictional integrator and dossier.
"""
from __future__ import annotations

from companion.ch40 import sources as src
from companion.ch40.common import emit
from companion.ch40.examples_c import last_good_check
from plantp import quality as qa


def traveler(serial: str = "S-07") -> list[str]:
    g = src.GENEALOGY[serial]
    lines = [f"process traveler of skid {serial} (one line an operation)",
             "  op    work                              record"]
    rec = {"OP20": f"transformer {g['tx']}", "OP40": f"tool {g['tool']}, "
           f"lugs {g['lugs']}, days {g['op40'][0]}-{g['op40'][1]}",
           "OP50": "jointer, kit lot", "OP80": "dossier, ITP points"}
    for op, work, *_ in src.ROUTE:
        lines.append(f"  {op}  {work:33s} {rec.get(op, 'sign, date')}")
    lines += ["  the traveler goes with the skid: each signature is a",
              "  record, and the genealogy is built from its fields"]
    emit("d_traveler", lines)
    return lines


# [start: audit]
def audit(dossier, itp, cal_due, proc_rev, genealogy, tool_checks,
          serial: str = "S-07") -> list[tuple[str, str]]:
    """Findings of a test-dossier audit: (check, finding)."""
    out = []
    fail = max(tool_checks)
    good = last_good_check(tool_checks, fail)
    for e in dossier:
        c, day = e["check"], e["day"]
        inst = e.get("instrument")
        if inst in cal_due and cal_due[inst] < day and inst != "TW-14":
            out.append((c, f"{inst} calibration ran out on day "
                           f"{cal_due[inst]}"))
        if itp.get(c) == "H" and "owner" not in e["signed"]:
            out.append((c, "hold point passed without the owner's release"))
        if "jointer_cert" in e and not e["jointer_cert"]:
            out.append((c, "no jointer certificate number"))
        if c in proc_rev and e.get("procedure_rev") != proc_rev[c][0] \
                and day >= proc_rev[c][1]:
            out.append((c, f"procedure rev {e['procedure_rev']} used, "
                           f"rev {proc_rev[c][0]} released day "
                           f"{proc_rev[c][1]}"))
        if c == "serials against genealogy" and \
                e["result"] != genealogy[serial]["tx"]:
            out.append((c, f"{e['result']} recorded, genealogy says "
                           f"{genealogy[serial]['tx']}"))
        if inst == "TW-14" and day > good:
            out.append((c, f"tool unchecked since day {good} (failed day "
                           f"{fail})"))
        if e.get("deviation"):
            out.append((c, "deviation without a concession number"))
    return out
# [end: audit]


def dossier_audit() -> list[tuple[str, str]]:
    found = audit(src.DOSSIER, src.ITP, src.CAL_DUE, src.PROCEDURE_REV,
                  src.GENEALOGY, src.TOOL_CHECKS)
    lines = [f"audit of the S-07 test dossier: {len(src.DOSSIER)} entries, "
             f"{len(found)} findings"]
    for c, f in found:
        lines += [f"  {c}", f"      {f}"]
    lines += [f"  entries with no finding: "
              f"{len(src.DOSSIER) - len({c for c, _ in found})}",
              "  every result in the dossier 'passed'; the audit does not",
              "  question the numbers, it questions whether they count:",
              "  valid instrument, right procedure, right serial, the",
              "  owner's release, a written concession"]
    emit("d_audit", lines)
    return found


def defect_trace() -> dict[str, float]:
    k = src.CONSEQUENCE
    mwh = k["block_mw"] * k["cf_july"] * 24 * k["outage_days"]
    energy = mwh * k["price"] / 1000
    checks = 2 * k["check_ku"]
    total = energy + k["repair_ku"] + checks
    before = qa.escape(1.0, [0.0, 0.3, 0.0])
    after = qa.escape(1.0, [0.5, 0.3, 0.95])
    prevent = 6.0 + 2.0                        # meter + checking time, k u
    lines = ["the torque defect from cause to consequence (skid S-06)",
             "  cause:     TW-14 dropped, read 12 % high; no check days 12-15",
             "  escape:    no paint mark, visual check, FAT without joint",
             f"             resistance: {before:.0%} of bad joints leave",
             "  event:     first July, a busbar joint overheats, S-06 trips",
             f"  energy:    {k['block_mw']:.0f} MW x {k['cf_july']} x 24 h x "
             f"{k['outage_days']} d = {mwh:.0f} MWh = {energy:.1f} k u",
             f"  repair:    {k['repair_ku']:.0f} k u; checks of S-05 and S-07: "
             f"{checks:.0f} k u",
             f"  total:     {total:.1f} k u (no one hurt; fire risk was real)",
             f"  after the actions {after:.1%} of bad joints would leave",
             f"             ({before / after:.0f} times fewer), for about "
             f"{prevent:.0f} k u",
             "  closure needs evidence, not dates: shift checks logged",
             "  for three months, joint resistance in every FAT, the",
             "  FMEA detection re-rated, S-05/S-07 measured on site"]
    emit("d_trace", lines)
    return dict(mwh=mwh, energy=energy, total=total, before=before,
                after=after)


if __name__ == "__main__":
    traveler()
    dossier_audit()
    defect_trace()
