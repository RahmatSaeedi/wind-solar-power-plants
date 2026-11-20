"""Chapter 36, lesson E (asset-data lifecycle controls): classes of records
and their custodians, transfers to vendors that expire, configuration and
firmware baselines compared with what runs, retention and readable
archives, integrations that may and may not cross into OT, and media
wiped at retirement.

Run from the project root:   python -m companion.ch36.examples_e
Writes companion/ch36/expected/e_*.txt.
Synthetic records and teaching values (A-404, A-408); defensive only.
"""
from __future__ import annotations

import hashlib

from companion.ch36.common import emit

RECORDS = [  # record type, class, custodian, count (synthetic)
    ("public project summary", "public", "communications", 3),
    ("one-line and layout drawings", "internal", "document control", 420),
    ("network diagrams, address plans", "restricted", "OT lead", 35),
    ("controller and relay configurations", "restricted", "control engineer", 410),
    ("credentials and keys", "secret", "OT lead (vault)", 260),
    ("historian data", "internal", "control engineer", 1),
    ("maintenance records", "internal", "maintenance lead", 18_000),
    ("vendor manuals", "internal", "document control", 900)]


def classify() -> None:
    lines = ["records of the control system by class (synthetic counts)",
             "  record                              class      custodian          count"]
    for r, c, o, n in RECORDS:
        lines.append(f"  {r:35s} {c:10s} {o:17s} {n:7,d}")
    lines += ["  the class decides who may read, copy and send a record;",
              "  network diagrams and configurations are restricted",
              "  because they describe how to reach and change the plant;",
              "  credentials live only in a managed vault. Every class",
              "  has a custodian who answers for it"]
    emit("e_classify", lines)


TRANSFERS = [  # to, what, purpose, days left (negative = expired)
    ("turbine maker", "turbine logs, 3 months", "warranty claim", 40),
    ("inverter maker", "inverter configurations", "firmware study", -25),
    ("integrator", "network diagram, sanitised", "extension design", 10),
    ("insurer", "availability summary", "renewal", -120)]


def transfers() -> None:
    lines = ["data sent to outside parties (synthetic register)",
             "  to                what                          purpose"
             "            days left"]
    expired = 0
    for to, what, why, left in TRANSFERS:
        expired += left < 0
        lines.append(f"  {to:17s} {what:29s} {why:18s} {left:6d}")
    lines += [f"  {expired} transfers past their end: the data is to be returned or",
              "  deleted and the deletion confirmed in writing",
              "  each transfer is approved for a purpose, carries only",
              "  what the purpose needs (a sanitised diagram, not the",
              "  address plan) and ends on a date"]
    emit("e_transfers", lines)


def baselines() -> None:
    def fp(text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()[:12]
    devices = {"SW-R01": ("fw 4.2.1 ring member", "fw 4.2.1 ring member"),
               "SW-R02": ("fw 4.2.1 ring member", "fw 4.1.9 ring member"),
               "FW-1": ("rules rev 14", "rules rev 14"),
               "PPC-A": ("logic v2.8 settings rev 6", "logic v2.8 settings rev 7")}
    lines = ["running configuration against the baseline (synthetic)",
             "  device   baseline       running        result"]
    drift = 0
    for d, (base, run) in devices.items():
        ok = fp(base) == fp(run)
        drift += not ok
        lines.append(f"  {d:8s} {fp(base)}   {fp(run)}   {'same' if ok else 'DIFFERENT'}")
    lines += [f"  {drift} devices differ from their baseline: a switch on older",
              "  firmware and a controller with a settings revision that",
              "  no change record explains - each is an incident until a",
              "  record is found or the baseline restored"]
    emit("e_baselines", lines)


def retention() -> None:
    rows = [("configurations and their history", "plant life + 5 y", 30),
            ("security logs", "1 year online, 3 archived", 4),
            ("access reviews and changes", "plant life", 25),
            ("incident records", "plant life", 25),
            ("vendor transfers register", "plant life", 25)]
    lines = ["retention and archive of security records (teaching)",
             "  record                             kept                      years"]
    for r, k, y in rows:
        lines.append(f"  {r:34s} {k:25s} {y:5d}")
    lines += ["  an archive is useful only if it can still be read: formats",
              "  are moved to current ones every 5 years and a sample is",
              "  read back after each move; the archive is restored in a",
              "  test like any backup"]
    emit("e_retention", lines)


def integrations() -> None:
    rows = [("historian copy to the DMZ, read by business", "allowed, one way"),
            ("CMMS reads running hours from the DMZ copy", "allowed, one way"),
            ("asset register sends tag names to a review", "allowed, reviewed"),
            ("CMMS writes a work order into SCADA", "NOT allowed"),
            ("business single sign-on into OT devices", "NOT allowed"),
            ("maker's cloud reads inverters directly", "NOT allowed as built")]
    lines = ["integrations of business systems with OT (teaching)",
             "  integration                                      verdict"]
    for a, b in rows:
        lines.append(f"  {a:48s} {b}")
    lines += ["  business systems are fed from copies outside the control",
              "  zone; nothing on the business side can change, log into",
              "  or reach a control device (ch 35 lesson F)"]
    emit("e_integrations", lines)


def sanitise() -> None:
    rows = [("SCADA servers", 2, "disks"), ("HMIs", 6, "disks"), ("historian", 1, "disks"),
            ("switches", 34, "flash: configuration"), ("controllers", 2, "flash: logic"),
            ("engineering laptops", 3, "disks")]
    n = sum(r[1] for r in rows)
    lines = ["devices that hold data when retired (synthetic)",
             "  device                 count   holds"]
    for name, c, h in rows:
        lines.append(f"  {name:22s} {c:5d}   {h}")
    lines += [f"  {n} devices to wipe or destroy, each with a certificate,",
              "  when replaced, sold or scrapped; a switch sent back under",
              "  warranty with its configuration still on it gives away",
              "  the plant's network to whoever opens it"]
    emit("e_sanitise", lines)


if __name__ == "__main__":
    classify()
    transfers()
    baselines()
    retention()
    integrations()
    sanitise()
