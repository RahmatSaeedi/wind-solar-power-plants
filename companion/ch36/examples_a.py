"""Chapter 36, lesson A (OT security foundations): what differs between
business IT and plant OT, what there is to protect and what its loss
costs, a teaching risk register, the life cycle and the roles, and the
trust boundaries of the ch 35 logical diagram.

Run from the project root:   python -m companion.ch36.examples_a
Writes companion/ch36/expected/a_*.txt.
Teaching values (A-401, A-408); defensive and non-operational.
"""
from __future__ import annotations

from companion.ch36 import sources as src
from companion.ch36.common import emit
from plantp import ot_security as ot


def priorities() -> None:
    rows = [("first concern", "confidentiality", "safety, then availability"),
            ("life of a device", "3-5 years", "15-25 years"),
            ("change", "patch on release", "tested, in an outage window"),
            ("a reboot means", "a short pause", "a stop or a protection gap"),
            ("a failure hurts", "the business", "people, plant and the grid"),
            ("traffic", "varied, people", "repetitive, machines")]
    lines = ["business IT and plant OT side by side (teaching summary)",
             "  aspect             business IT        plant OT"]
    for a, b, c in rows:
        lines.append(f"  {a:18s} {b:18s} {c}")
    lines += ["  the same tool or rule can be right for one and harmful",
              "  for the other: an automatic reboot that heals an office",
              "  PC can stop the plant controller in the middle of a",
              "  ramp; OT security starts from safety and availability"]
    emit("a_priorities", lines)


def assets_at_stake() -> None:
    mwh_h = 295_100 / 8760                       # mean export MWh an hour (ch 15)
    price = 50.0                                 # u/MWh, ch 16 teaching price
    rows = [("protection relays", "safety, equipment", "none: they trip alone"),
            ("plant controller", "compliance, energy",
             f"{mwh_h * 0.5 * price:,.0f} u an hour at 50 % fallback"),
            ("SCADA servers", "sight, command", "no view; the PPC runs on"),
            ("historian", "evidence, warranty", "a hole in the record"),
            ("fire interface", "life safety", "the panel works alone"),
            ("CMMS, reports", "business", "late work orders")]
    lines = ["what there is to protect at Plant P and what its loss costs (teaching)",
             "  system              at stake             cost of a loss"]
    for a, b, c in rows:
        lines.append(f"  {a:19s} {b:20s} {c}")
    lines += [f"  mean export {mwh_h:.1f} MWh an hour at {price:.0f} u/MWh: the money is in",
              "  availability; the protection relays and the fire panel",
              "  are designed to stay safe whatever happens to the network"]
    emit("a_assets", lines)


RISKS = [  # scenario (generic, defensive), likelihood, consequence (teaching)
    ("vendor remote access left open after support", 4, 4),
    ("infected removable media on an engineering laptop", 3, 4),
    ("firewall rule added for a test and never removed", 4, 3),
    ("backups exist but were never restored", 3, 4),
    ("operator account shared by the shift", 4, 2),
    ("unsupported operating system on the historian", 3, 3),
    ("business network change reaches the control zone", 2, 5)]


def risk_register() -> None:
    lines = ["teaching risk register (likelihood x consequence, 1-5 each)",
             "  scenario                                             L  C  score  band"]
    scored = sorted(((ot.risk_score(l, c), s, l, c) for s, l, c in RISKS), reverse=True)
    for score, s, l, c in scored:
        lines.append(f"  {s:52s} {l:1d}  {c:1d}  {score:5d}  {ot.risk_band(score)}")
    high = sum(ot.risk_band(sc) in ("high", "very high") for sc, *_ in scored)
    lines += [f"  {high} of {len(RISKS)} scenarios high or very high",
              "  the scenarios are generic and defensive: each names a",
              "  weakness a design or a procedure can remove, never a",
              "  method of attack; the scales and bands are teaching",
              "  values, set for a real plant in its own risk method"]
    emit("a_risks", lines)


def lifecycle() -> None:
    phases = [("assess", "inventory, zones, risk register"),
              ("design", "conduits, rules, access, backups, logging"),
              ("build and test", "hardening, factory and site security tests"),
              ("operate", "monitoring, access reviews, restore tests"),
              ("maintain", "patches, changes, supplier notices"),
              ("retire", "data archived, media wiped, accounts closed")]
    lines = ["the security life cycle of the control system (teaching)",
             "  phase            evidence it leaves"]
    for p, e in phases:
        lines.append(f"  {p:16s} {e}")
    lines += ["  security is a property of the whole life, not of the day",
              "  of commissioning: each phase leaves records that the next",
              "  one, and an auditor, can read (asset owner programme,",
              "  STD-156)"]
    emit("a_lifecycle", lines)


def roles() -> None:
    rows = [("asset owner", "accountable", "decides risk, funds controls"),
            ("OT security lead", "responsible", "programme, reviews, incidents"),
            ("control engineer", "responsible", "configurations, backups, changes"),
            ("IT team", "consulted", "business network, identity services"),
            ("operators", "informed / act", "report anomalies, follow procedures"),
            ("vendors, integrators", "responsible for", "their access and products"),
            ("physical security", "consulted", "doors, cabinets, visitors (ch 32)")]
    lines = ["who does what (teaching)",
             "  role                   share            does"]
    for a, b, c in rows:
        lines.append(f"  {a:22s} {b:16s} {c}")
    lines += ["  one named person owns each control; the interfaces with",
              "  IT and physical security are written down with escalation",
              "  paths, so nothing falls between two teams"]
    emit("a_roles", lines)


def trust_boundaries() -> None:
    crossings = [c for c in src.CONDUITS if c["src"] != c["dst"]]
    into_control = [c for c in crossings if c["dst"] == "control"]
    lines = ["trust boundaries of the logical diagram (ch 35)",
             f"  zones: {len(src.ZONES)}; conduits crossing a boundary: {len(crossings)}",
             f"  conduits into the control zone: {len(into_control)}"]
    for c in into_control:
        lines.append(f"    {c['src']:10s} -> control  {c['service']:14s} {c['purpose']}")
    lines += ["  every arrow into the control zone is a door: each has a",
              "  purpose, an owner and a rule; the fewer doors, the fewer",
              "  things to watch - the business zone has none"]
    emit("a_trust", lines)


if __name__ == "__main__":
    priorities()
    assets_at_stake()
    risk_register()
    lifecycle()
    roles()
    trust_boundaries()
