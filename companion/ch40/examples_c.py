"""Chapter 40, lesson C (nonconformity and evidence) and the test ladder:
containment by genealogy, the root cause as a chain of whys and cause
categories, a concession record, preservation in storage, receipt
inspection at site, a supplier change notice, warranty traceability, and
what each kind of test proves.

Run from the project root:   python -m companion.ch40.examples_c
Writes companion/ch40/expected/c_*.txt.
Teaching values (A-434 to A-440); a fictional integrator.
"""
from __future__ import annotations

from companion.ch40 import sources as src
from companion.ch40.common import emit


# [start: contain]
def suspect_skids(tool: str, last_good: int, first_bad: int) -> list[str]:
    """Skids whose OP40 used the tool after its last good check and up
    to the check that found it out of tolerance."""
    out = []
    for serial, g in src.GENEALOGY.items():
        start, end = g["op40"]
        if g["tool"] == tool and end > last_good and start <= first_bad:
            out.append(serial)
    return out
# [end: contain]


def last_good_check(tool_checks: dict[int, float], fail_day: int,
                    tol: float = 1.4) -> int:
    good = [d for d, v in tool_checks.items()
            if d < fail_day and abs(v - 70.0) <= tol]
    return max(good)


def contain() -> list[str]:
    fail = max(src.TOOL_CHECKS)
    good = last_good_check(src.TOOL_CHECKS, fail)
    suspects = suspect_skids("TW-14", good, fail)
    all_tw14 = [s for s, g in src.GENEALOGY.items() if g["tool"] == "TW-14"]
    lines = ["containment of the drifted torque wrench TW-14",
             f"  check on day {fail}: {src.TOOL_CHECKS[fail]:.1f} N m shown at "
             "70 set (limit 1.4)",
             f"  last good check: day {good}; days without a check: "
             f"{', '.join(str(d) for d in range(good + 1, fail))}",
             f"  suspect skids: {', '.join(suspects)}",
             f"  without genealogy: every skid with TW-14 ({len(all_tw14)}) "
             f"or all ten",
             "  S-03 and S-04 used TW-14 too, but checks on days 8-11",
             "  bracket their work: the record clears them",
             "  the three suspects had shipped: containment moves to site"]
    lugs = [s for s, g in src.GENEALOGY.items() if g["lugs"] == "L-2208"]
    lines.append(f"  (a lug-lot query works the same: L-2208 -> "
                 f"{', '.join(lugs)})")
    emit("c_contain", lines)
    return suspects


WHYS = [
    "S-06 tripped on an LV busbar fault in its first July",
    "a busbar joint overheated: its bolt was under-torqued",
    "TW-14 read 12 % high after it was dropped on day 12",
    "the drop went unreported; the daily check was skipped 4 days",
    "no hold when a check was missing; no one reviewed the log",
]
CAUSES = {  # category: finding (A-438)
    "method": "daily tool check with no hold when missing",
    "measurement": "joint resistance not measured at FAT",
    "machine": "wrench without drop indicator",
    "people": "no habit of reporting a dropped tool",
    "management": "FMEA rated detection 8 but no action was required",
}


def root_cause() -> None:
    lines = ["root cause: five whys, then the categories"]
    for k, w in enumerate(WHYS, 1):
        lines.append(f"  why {k}: {w}")
    lines.append("  cause categories:")
    for cat, f in CAUSES.items():
        lines.append(f"    {cat:12s} {f}")
    lines += ["  the root cause is in the system (no hold, no detection),",
              "  not in the person who dropped the tool; blaming the",
              "  person fixes nothing that the next drop will not repeat"]
    emit("c_rootcause", lines)


CONCESSION = dict(  # the S-07 deviation written up properly (A-438)
    number="CR-012", serial="S-07", requirement="cable gland type G1, IP66",
    deviation="gland type G2 fitted", reason="G1 out of stock",
    risk="G2 is IP66 and same thread; no change to fire rating",
    affected=["S-07"], decided_by="owner's engineer",
    decision="accept, record in as-built", before_shipment=True)


def concession() -> None:
    needed = ["number", "requirement", "deviation", "reason", "risk",
              "affected", "decided_by", "decision", "before_shipment"]
    missing = [k for k in needed if not CONCESSION.get(k)]
    lines = ["concession for the S-07 gland (it came 'agreed by phone')"]
    for k in needed:
        v = CONCESSION[k]
        v = ", ".join(v) if isinstance(v, list) else (
            ("yes" if v else "no") if isinstance(v, bool) else v)
        lines.append(f"  {k:15s} {v}")
    lines += [f"  fields missing: {len(missing)}",
              "  a concession accepts a known nonconformity in writing,",
              "  for named serials, before shipment, by the person with",
              "  the authority; a phone call is none of these"]
    emit("c_concession", lines)


def preservation() -> dict[str, float]:
    vol, ach, dw = 30.0, 0.5, 10.0          # m3, air changes a day, g/m3
    gel, uptake = 4.0, 0.20                  # kg silica gel, share it holds
    ingress = vol * ach * dw                 # g of water a day
    days = gel * 1000 * uptake / ingress
    lines = ["preservation of a skid in storage (teaching values)",
             f"  enclosure {vol:.0f} m3, breathing {ach} air changes a day,",
             f"  outside air {dw:.0f} g/m3 wetter than inside",
             f"  water in: {ingress:.0f} g a day; gel holds "
             f"{gel * uptake * 1000:.0f} g",
             f"  the desiccant lasts {days:.1f} days",
             "  storage before energisation is weeks, not days: the",
             "  preservation plan seals openings, inspects the gel's",
             "  colour weekly, replaces it, or powers the anti-",
             "  condensation heaters from a temporary supply"]
    emit("c_preserve", lines)
    return dict(ingress=ingress, days=days)


RECEIPT = [  # site receipt inspection of the ten skids (A-438)
    ("S-02", "desiccant colour shows saturated", "replace, check insides"),
    ("S-04", "shock indicator tripped (ch 31)", "hold, inspect, maker"),
    ("S-09", "test dossier not in the delivery", "hold acceptance"),
]


def receipt() -> None:
    lines = ["receipt inspection at site: ten skids",
             f"  skids with findings: {len(RECEIPT)}"]
    for s, f, act in RECEIPT:
        lines.append(f"  {s}  {f}; {act}")
    lines += ["  receipt is the first site record of each serial; a",
              "  finding not written here becomes a dispute later about",
              "  whether it happened in transport or in storage"]
    emit("c_receipt", lines)


def supplier_change() -> list[str]:
    change_day, lot_after = 18, "L-2209"
    used = [s for s, g in src.GENEALOGY.items() if g["lugs"] == lot_after]
    lines = ["supplier change notice: lug plating changed from day "
             f"{change_day}",
             f"  first lot after the change: {lot_after}",
             f"  used in: {', '.join(used)} - without first-article tests",
             "  rule: a change to a critical part needs notice before",
             "  shipment, first-article inspection and the buyer's",
             "  release; here: pull tests on retained lugs of the lot",
             "  and resistance checks on the two skids before release"]
    emit("c_change", lines)
    return used


WARRANTY = [  # item, starts at, months (A-440)
    ("transformer (U-A)", "delivery", 60),
    ("inverter", "commissioning", 60),
    ("skid workmanship (integrator)", "COD (or 30 months after"
     " delivery)", 24),
]


def warranty() -> None:
    lines = ["warranty traceability of skid S-06"]
    for item, start, months in WARRANTY:
        lines += [f"  {item}", f"      {months} months from {start}"]
    lines += ["  the hot joint is workmanship: the integrator's warranty",
              "  covers it, the transformer's does not - the genealogy",
              "  and the FAT record are the evidence for that claim"]
    emit("c_warranty", lines)


# [start: ladder]
LADDER = [  # test, proves, on, who
    ("design verification", "the design meets its requirements",
     "calculations, models, prototype", "designer"),
    ("type qualification", "a sample of the design passes type tests",
     "one or few units", "accredited lab"),
    ("routine test", "each unit was built as designed",
     "every unit", "maker"),
    ("factory acceptance (FAT)", "the assembled unit meets the order",
     "every skid", "integrator + owner"),
    ("site acceptance (SAT)", "it arrived and was installed intact",
     "every skid", "contractor + owner"),
    ("integrated plant test", "the plant works as a system",
     "the plant", "owner + grid operator"),
]
# [end: ladder]


def ladder() -> None:
    lines = ["the test ladder: what each kind of test proves"]
    for t, proves, on, who in LADDER:
        lines += [f"  {t}", f"      proves: {proves}",
                  f"      on: {on}; by: {who}"]
    lines += ["  type tests use the standard's methods on a sample; a",
              "  routine test on every unit cannot replace them, and they",
              "  cannot replace routine tests. FAT cannot see transport",
              "  damage; SAT cannot see a joint that heats only at full",
              "  load in July - the integrated tests of ch 50 and the",
              "  first-year monitoring of ch 37 close that gap"]
    emit("c_ladder", lines)


if __name__ == "__main__":
    contain()
    root_cause()
    concession()
    preservation()
    receipt()
    supplier_change()
    warranty()
    ladder()
