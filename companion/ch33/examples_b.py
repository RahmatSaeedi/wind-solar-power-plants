"""Chapter 33, lesson B: stakeholders and social performance in numbers -
a stakeholder map, disclosure before decisions, the land register, the
herders' longer walk to the spring, vulnerable groups, supplier due
diligence, heritage buffers and chance finds, and a commitments
register that refuses unfunded promises.

Run from the project root:   python -m companion.ch33.examples_b
Writes companion/ch33/expected/b_*.txt and diagrams/data/ch33-map.csv.
Teaching values (A-380, A-381); the fictional community of ch 14 and 22.
Legal triggers, consultation duties and land processes depend on the
governing framework and qualified local social and legal experts.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch33 import sources as src
from companion.ch33.common import csv, emit

# [start: stakeholders]
STAKEHOLDERS = [  # (group, influence 1-5, interest/impact 1-5)
    ("herding families (5)", 2, 5), ("village council", 4, 4),
    ("farm 1 owner", 2, 4), ("corridor strip owners (8)", 2, 3),
    ("women's group", 1, 4), ("rangeland authority", 5, 3),
    ("environment authority", 5, 3), ("grid operator", 5, 2),
    ("lenders", 5, 3), ("local contractors", 3, 4),
    ("road users", 1, 2), ("regional NGO", 3, 3)]
# [end: stakeholders]


def stakeholder_map() -> None:
    rows = []
    lines = ["stakeholder map: influence and interest (teaching scores)",
             "  group                        infl  int   engagement"]
    for g, i, t in STAKEHOLDERS:
        if t >= 4 and i <= 2:
            how = "involve: high impact, low voice"
        elif t >= 4:
            how = "collaborate"
        elif i >= 4:
            how = "consult and inform"
        else:
            how = "inform"
        rows.append((i, t))
        lines.append(f"  {g:28s} {i:4d}  {t:3d}   {how}")
    csv("ch33-map.csv", "influence,interest", rows)
    lines += ["  the groups most affected and least able to be heard - the",
              "  herders, the women's group, the farm owner - get the most",
              "  deliberate engagement: their own meetings, languages and",
              "  times, not a seat at the authority's table"]
    emit("b_map", lines)


def disclosure() -> None:
    docs = [("scoping summary", 45, "meeting, radio, leaflet"),
            ("draft impact assessment", 60, "summary in local language, meetings"),
            ("grievance mechanism", 30, "posters, phone line, box at the school"),
            ("resettlement or livelihood plan (if any)", 60, "household visits"),
            ("annual monitoring report", 30, "village board, meeting")]
    lines = ["disclosure before decisions (days are PLACEHOLDERS of the framework)",
             "  document                                   days ahead"]
    for d, days, how in docs:
        lines += [f"  {d:42s} {days:10d}", f"      how: {how}"]
    lines += ["  disclosure is useful only if people can read it in time",
              "  and in their language, and if what they say can still",
              "  change the decision - comments and the answers to them",
              "  are recorded (lesson H)"]
    emit("b_disclose", lines)


def land_register() -> None:
    rows = [("state rangeland", "state, customary use", 126.0, "lease (authority)"),
            ("farm 1", "private title", 0.9, "lease or easement"),
            ("farm 2", "private title", 0.0, "none"),
            ("customary grazing", "customary (herders)", 3.1, "agreement + plan"),
            ("village lands", "communal", 0.0, "none; route kept"),
            ("corridor strips (8)", "private, informal use", 0.6, "easements (towers)")]
    lines = ["land register of the project footprint (teaching; tenure to verify)",
             "  parcel                tenure                    ha    instrument"]
    for p, t, ha, ins in rows:
        lines.append(f"  {p:21s} {t:24s} {ha:6.1f}  {ins}")
    lines += ["  formal title is only part of the picture: customary",
              "  grazing and informal use of the strips are rights people",
              "  live by, and the register records them too - which",
              "  process applies (lease, easement, acquisition) is set by",
              "  the law and the lenders' framework with local experts"]
    emit("b_land", lines)


def livelihood() -> None:
    h = src.HERDERS
    extra = (h["detour_km"] - h["route_to_spring_km"]) * 2      # there and back
    days = 200
    lines = ["the herders' route to the spring and its cost (teaching)",
             f"  {h['households']} households, {h['animals']} animals; route {h['route_to_spring_km']} km,"
             f" detour {h['detour_km']} km",
             f"  extra walking: {extra:.1f} km a day, {extra * days:,.0f} km over {days} grazing days",
             f"  grazing income supported: {h['animals'] * h['income_per_animal']:.0f} k u a year",
             "  at 5 % loss of condition from the longer walk (teaching):"
             f" {h['animals'] * h['income_per_animal'] * 0.05:.1f} k u a year",
             "  a gap in the PV fence and a crossing over the cable trench",
             "  restore the old route for much less than any payment;",
             "  what is offered, and whether compensation applies, is",
             "  agreed with the families under the framework (lab G)"]
    emit("b_livelihood", lines)


def vulnerable() -> None:
    groups = [("women-headed households", "fewer jobs, harder to attend meetings",
               "women-only meetings, job quota"),
              ("elderly herders", "long detours, little cash", "route kept, water point"),
              ("seasonal camp families", "away during consultations", "visits at the camp"),
              ("people without title", "left out of land lists", "register customary use"),
              ("children near the haul road", "traffic", "school-hour truck hold (ch 32)")]
    lines = ["vulnerable groups and the measures that reach them (teaching)",
             "  group                        why vulnerable here"]
    for g, why, m in groups:
        lines += [f"  {g:28s} {why}", f"      measure: {m}"]
    lines += ["  vulnerability is local: the screening asks who could be",
              "  harmed more or helped less, and checks each plan against",
              "  them"]
    emit("b_vulnerable", lines)


def due_diligence() -> None:
    suppliers = [("modules S1", 0.95, 1, 1, 1), ("modules S2", 0.40, 0, 1, 0),
                 ("turbines", 0.80, 1, 1, 1), ("steel structures", 0.70, 1, 0, 1),
                 ("cables", 0.60, 1, 1, 0)]
    lines = ["supplier due diligence on labour and supply chain (teaching scores)",
             "  supplier          traced   audit   code   grievance   score   action"]
    for name, traced, audit, code, griev in suppliers:
        score = traced * 0.4 + audit * 0.2 + code * 0.2 + griev * 0.2
        flag = "plan" if score < 0.7 else ""
        lines.append(f"  {name:16s} {traced * 100:5.0f} %   {audit:5d}   {code:4d}"
                     f"   {griev:9d}   {score:5.2f}   {flag}")
    lines += ["  forced and child labour risks sit deep in raw-material",
              "  chains: traceability to the source, independent audits",
              "  and a supplier grievance channel are asked for in the",
              "  tender; a weak score leads to a corrective plan with",
              "  dates, and the lenders' and the law's rules decide the rest"]
    emit("b_supply", lines)


def heritage() -> None:
    works = {"cemetery": [(6000, 4400), (5600, 4800)], "ruin": [(9800, 3380), (10200, 3500)]}
    sites = {"cemetery": src.CEMETERY, "ruin": src.RUIN}
    buffer = {"cemetery": 300.0, "ruin": 200.0}
    lines = ["heritage buffers and chance finds (teaching)",
             "  site       buffer m   nearest planned works m   ok?"]
    for k, xy in sites.items():
        d = min(math.hypot(x - xy[0], y - xy[1]) for x, y in works[k])
        lines.append(f"  {k:9s}  {buffer[k]:8.0f}   {d:23.0f}   {'yes' if d >= buffer[k] else 'NO'}")
    trench_km, rate = 45.0, 0.04
    lines += [f"  expected chance finds in {trench_km:.0f} km of trenches at {rate} a km:"
              f" {trench_km * rate:.1f}",
              "  the ruin's buffer is breached by the corridor works: the",
              "  route moves or the works are watched by an archaeologist;",
              "  every crew knows the chance-find rule - stop, protect,",
              "  report - and the authority decides what happens next"]
    emit("b_heritage", lines)


def commitments() -> None:
    rows = [("local hiring share 40 %", True, True, "HR manager"),
            ("water point for herders", True, True, "E&S manager"),
            ("new school roof", False, False, "-"),
            ("paved village road", False, False, "-"),
            ("school-hour truck hold", True, True, "logistics lead"),
            ("community fund 0.5 % of revenue", True, False, "owner")]
    lines = ["commitments register: only approved and funded promises (teaching)",
             "  commitment                         approved   funded   owner"]
    bad = 0
    for c, ap, fu, o in rows:
        flag = "" if (ap and fu) else "  DO NOT PROMISE" if not ap else "  fund first"
        bad += 0 if (ap and fu) else 1
        lines.append(f"  {c:34s} {str(ap):8s}   {str(fu):6s}   {o}{flag}")
    lines += [f"  {bad} items are not ready to be promised: an unfunded promise",
              "  made in a meeting becomes a grievance later; the register",
              "  is what staff may say, and it is reported back each year"]
    emit("b_commit", lines)


if __name__ == "__main__":
    stakeholder_map()
    disclosure()
    land_register()
    livelihood()
    vulnerable()
    due_diligence()
    heritage()
    commitments()
