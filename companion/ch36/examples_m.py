"""Chapter 36, deeper round: what one compromised office PC could reach
in a flat network and in zones, independent backup copies, certificates
that expire, how long an intruder goes unseen against how often logs are
read, removable media at the HMIs, alert triage, the ladder of recovery
objectives, the cost of an outage against the cost of controls, and the
review of vendor sessions.

Run from the project root:   python -m companion.ch36.examples_m
Writes companion/ch36/expected/m_*.txt and diagrams/data/ch36-*.csv.
Synthetic data and teaching values (A-401 to A-408); defensive only.
"""
from __future__ import annotations

import numpy as np

from companion.ch36 import sources as src
from companion.ch36.common import csv, emit


def reach() -> None:
    ot_devices = sum(d["devices"] for z, d in src.ZONES.items()
                     if z.startswith("field") or z == "control")
    lines = ["what one compromised office PC could reach (synthetic counts)",
             f"  flat network: every one of the {ot_devices} control and field devices",
             "  zones and conduits: none - the business zone has no",
             "    conduit into control; it reaches only the historian copy",
             "    in the DMZ, read-only",
             "  segmentation does not make a device secure; it limits how",
             "  far one mistake or one infected machine can spread - the",
             "  'reach' of each zone is what the conduit table decides"]
    emit("m_reach", lines)


def backup_copies() -> None:
    p = 0.05                              # chance a copy is lost in one bad event
    lines = ["independent backup copies (teaching: each lost with 5 % in an event)",
             "  copies   where                          chance all are lost"]
    for n, note in ((1, "on the server"), (2, "server and a local disk"),
                    (3, "and one offline, off site")):
        lines.append(f"  {n:6d}   {note:30s} {p ** n * 100:10.4f} %")
    lines += ["  copies only help if they do not fail together: a copy on",
              "  the same server, the same network or the same building as",
              "  the original shares its fate; one copy is offline and",
              "  elsewhere, so a fault or a mistake on the network cannot",
              "  reach it - and every copy is restored in a test (lesson C)"]
    emit("m_copies", lines)


def certificates(seed: int = 363) -> None:
    rng = np.random.default_rng(seed)
    n = 120
    months = rng.integers(0, 36, n)                # month each expires in
    by_month = np.bincount(months, minlength=36)
    worst = int(by_month.max())
    csv("ch36-certs.csv", "m,n", [(m, int(by_month[m])) for m in range(36)])
    lines = ["certificates of the control system expiring (synthetic, 120)",
             f"  in the next 12 months: {int(by_month[:12].sum())}",
             f"  busiest month: {worst} at once",
             "  an expired certificate stops a connection as surely as a",
             "  cut cable - the historian copy, a gateway, the jump host;",
             "  every certificate is in the inventory with its expiry",
             "  date and owner, and renewal starts 60 days before"]
    emit("m_certs", lines)


def dwell() -> None:
    lines = ["how long an unusual event goes unseen (teaching)",
             "  logs read           mean days to notice   worst days"]
    rows = []
    for name, every in (("every day", 1), ("every week", 7), ("every month", 30),
                        ("only after a fault", 180)):
        lines.append(f"  {name:19s} {every / 2:19.1f}   {every:10d}")
        rows.append((every, every / 2))
    lines += ["  a log nobody reads protects nobody: the few events that",
              "  matter (logins and changes on controllers, new devices,",
              "  rule hits on the deny rule) are read every day, by a",
              "  named person, and the rest are kept for when a question",
              "  is asked"]
    emit("m_dwell", lines)


def removable_media() -> None:
    hmis, inserts_month = 6, 20
    lines = ["removable media at the HMIs (teaching counts)",
             f"  {hmis} HMIs, about {inserts_month} insertions a month in commissioning",
             "  policy: ports blocked on HMIs and servers; files enter",
             "    through one scanning station in the DMZ, logged",
             f"  insertions refused and logged in a month: {inserts_month}",
             "  the refusals are not a nuisance to be switched off; each",
             "  is a person who needed a file and now uses the station -",
             "  and the log shows when somebody keeps trying"]
    emit("m_media", lines)


def triage(seed: int = 364) -> None:
    rng = np.random.default_rng(seed)
    alerts = rng.poisson(40, 30)                  # alerts a day for a month
    true_share = 0.02
    lines = ["alerts of the security monitoring in a month (synthetic)",
             f"  {alerts.sum():,} alerts, {alerts.mean():.0f} a day on average",
             f"  if 2 % need action: about {alerts.sum() * true_share:.0f} a month",
             "  at 5 min each, reading all of them takes"
             f" {alerts.sum() * 5 / 60:.0f} h a month",
             "  alerts are tuned until most of them mean something:",
             "  known maintenance is announced to the monitoring, noisy",
             "  rules are fixed, and every closed alert says why - the",
             "  same discipline as the plant's alarms (ch 35)"]
    emit("m_triage", lines)


LADDER = [  # system, recovery time h, recovery point h (teaching objectives)
    ("protection relay settings", 8, 0),
    ("plant controller", 4, 0),
    ("SCADA servers", 8, 0.25),
    ("firewalls and switches", 2, 0),
    ("historian", 24, 1),
    ("CMMS (business)", 48, 24)]


def ladder() -> None:
    lines = ["recovery objectives of each system (teaching)",
             "  system                        time h   data lost h"]
    for s, rto, rpo in LADDER:
        lines.append(f"  {s:29s} {rto:6.0f}   {rpo:11.2f}")
    lines += ["  configurations lose nothing: every change is backed up",
              "  before and after (lesson C); the historian may lose an",
              "  hour because the devices' buffers refill it (ch 35); the",
              "  business system may lose a day. The objectives decide",
              "  how backups are made, not the other way round"]
    emit("m_ladder", lines)


def outage_cost() -> None:
    mwh_h = 295_100 / 8760
    price = 50.0
    days = 5
    loss = mwh_h * 24 * days * price
    controls = 60_000.0                            # u a year, teaching
    lines = ["the plant stopped for 5 days after a control-system incident (teaching)",
             f"  energy not sold at {price:.0f} u/MWh: {loss:,.0f} u",
             f"  security controls of this chapter: about {controls:,.0f} u a year",
             f"  break-even: one such event every {loss / controls:.1f} years",
             "  the comparison is rough on purpose - it only shows that",
             "  availability, not secrecy, is what the plant's security",
             "  protects; the risk register (lesson A) is the real tool"]
    emit("m_cost", lines)


def vendor_sessions() -> None:
    sessions = [("V1", 3.5, "firmware study", "recorded"),
                ("V1", 2.0, "fault analysis", "recorded"),
                ("V2", 6.0, "commissioning help", "not recorded"),
                ("V3", 1.0, "licence renewal", "recorded")]
    hours = sum(s[1] for s in sessions)
    lines = ["vendor sessions of a quarter (synthetic register)",
             "  vendor  hours   purpose               record"]
    for v, h, p, r in sessions:
        lines.append(f"  {v:6s} {h:6.1f}   {p:21s} {r}")
    lines += [f"  {hours:.1f} h in the quarter; one session without a recording",
              "  is a finding: the jump host records every session, so a",
              "  missing recording means a path around it",
              "  the quarterly review matches each session to a request",
              "  and a purpose"]
    emit("m_sessions", lines)


if __name__ == "__main__":
    reach()
    backup_copies()
    certificates()
    dwell()
    removable_media()
    triage()
    ladder()
    outage_cost()
    vendor_sessions()
