"""Chapter 39, lessons E to H (reliability and service requirements,
connection works, labour due diligence, financeable contract interfaces):
a plant availability target split into supplier requirements, response
and repair times that meet it, a guarantee tested against chance, the
scope split of the export works, a proportionate labour screen, and the
gaps between the project's contracts.

Run from the project root:   python -m companion.ch39.examples_e
Writes companion/ch39/expected/e_*.txt.
Teaching values (A-429 to A-432); no legal advice, no real company.
"""
from __future__ import annotations

from companion.ch39 import sources as src
from companion.ch39.common import csv, emit
from plantp import procure as pr


def ram_allocation() -> None:
    target = 0.97                                       # PV energy availability (teaching)
    parts = ["inverter", "unit transformer", "MV switchgear", "SCADA link"]
    each = pr.allocate_availability(target, len(parts))
    lines = [f"PV block availability target {target * 100:.0f} %, four parts in series",
             f"  equal share each: {each * 100:.2f} %",
             "  a weighted split instead (teaching):"]
    split = {"inverter": 0.980, "unit transformer": 0.998, "MV switchgear": 0.997,
             "SCADA link": 0.995}
    a = 1.0
    for k, v in split.items():
        a *= v
        lines.append(f"    {k:18s} {v * 100:6.2f} %")
    lines += [f"  product {a * 100:.2f} % - meets the target",
              "  the inverter gets the loosest share because it has the",
              "  most parts and the shortest repairs; each share becomes",
              "  a supplier requirement with its measurement (ch 37)"]
    emit("e_ram", lines)


def response_repair() -> None:
    mtbf = 2_000.0                                      # h, one inverter skid (teaching)
    lines = ["inverter availability from failure and repair times (teaching)",
             "  response h   repair h   availability   meets 98.0 %?"]
    for resp, rep in ((72, 24), (48, 12), (24, 8), (8, 4)):
        a = mtbf / (mtbf + resp + rep)
        lines.append(f"  {resp:10d}   {rep:8d}   {a * 100:10.2f} %   {'yes' if a >= 0.98 else 'NO'}")
    csv("ch39-service.csv", "r,a", [(r, round(mtbf / (mtbf + r + 8) * 100, 3))
                                     for r in range(0, 97, 4)])
    lines += ["  the response time - spares, travel, access - matters more",
              "  than the repair itself; the service contract states both,",
              "  with the spares held on site that make them possible"]
    emit("e_service", lines)


def scope_split() -> None:
    rows = [("line route, land, permits", "plant", "operator approves"),
            ("132 kV line", "plant", "handed over after tests"),
            ("grid bay at the substation", "grid operator", "plant pays via offer"),
            ("protection at both line ends", "both", "agreed together"),
            ("revenue metering", "grid operator", "plant gives space"),
            ("outage for the bay works", "grid operator", "plant plans around it"),
            ("maintenance of the line", "grid operator", "after handover")]
    lines = ["connection works: who builds, owns and maintains (teaching split)",
             "  item                                 responsible     note"]
    for a, b, c in rows:
        lines.append(f"  {a:36s} {b:15s} {c}")
    lines += ["  each line names the boundary of design, construction,",
              "  ownership and warranty; an item built by the plant and",
              "  transferred to the operator needs acceptance tests both",
              "  agree before construction (ch 28, ch 38)"]
    emit("e_scope", lines)


def labour_screen() -> None:
    lines = ["labour due-diligence screen of suppliers (synthetic, A-430)",
             "  party                      tier   risk   evidence             status"]
    for party, tier, ind, ev in src.LABOUR:
        score = sum(ind.values())
        band = "high" if score >= 5 else ("medium" if score >= 3 else "low")
        verified = ev.startswith("audit")
        status = ("verified" if verified else
                  ("claimed only" if ev == "declaration" else "unknown"))
        lines.append(f"  {party:25s} {tier:5d}   {band:6s} {ev:20s} {status}")
    lines += ["  a high risk with no evidence (U-B's winding wire) is not a",
              "  finding of abuse - it is a gap: the supplier is asked to",
              "  map the source and allow an audit, with a remedy plan if",
              "  problems are found; a declaration is recorded as a claim,",
              "  never as a verified result. Workers of the site contractor",
              "  get the project's grievance channel (ch 33)"]
    emit("e_labour", lines)


def contract_gaps() -> None:
    needs = {c: v[0] for c, v in src.CONTRACTS.items()}
    terms = {c: v[1] for c, v in src.CONTRACTS.items()}
    gaps = pr.interface_gaps(needs, terms)
    lines = ["what each contract relies on that no contract covers (A-431)"]
    for c, g in gaps.items():
        lines.append(f"  {c:16s} needs: {', '.join(g)}")
    lines += [f"  {sum(len(g) for g in gaps.values())} gaps; each needs an owner and a"
              " clause before",
              "  financial close. The concepts (guarantee, step-in,",
              "  assignment, security) are explained; the wording is for",
              "  the parties' lawyers"]
    emit("e_gaps", lines)


def guarantee_chance() -> None:
    lines = ["an availability guarantee for the 12 turbines and their real spread",
             "  (ch 37: the same fleet missed 98.5 % in 37 % of years by chance)",
             "  guarantee   years missed by chance   bonus/penalty design"]
    for g, p in ((0.985, 0.372), (0.983, 0.072), (0.980, 0.0)):
        lines.append(f"  {g * 100:8.1f} %   {p * 100:22.1f} %   "
                     f"{'band of +/- 0.5 %' if p > 0.2 else 'one-sided penalty'}")
    lines += ["  a guarantee is a promise to pay, measured one way, over a",
              "  period; it is not evidence that the plant reaches the",
              "  figure - the monitoring of ch 37 is"]
    emit("e_guarantee", lines)


if __name__ == "__main__":
    ram_allocation()
    response_repair()
    scope_split()
    labour_screen()
    contract_gaps()
    guarantee_chance()
