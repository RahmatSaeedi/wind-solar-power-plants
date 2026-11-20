"""Chapter 32, lab I: the physical-security management plan of Plant P -
its elements and the evidence that each works, a week of gate records
reconciled against authorisations (and what that means for a muster
count), the proportionality of asset-protection measures in money and
in hazard, the notification timeline of a synthetic intrusion alarm with
its link to OT incident response, and the evidence behind a security
provider's declarations.

Run from the project root:   python -m companion.ch32.lab_i
Writes companion/ch32/expected/i_*.txt.
Synthetic teaching values (A-375). Records and reporting only: no
tactical procedure, no guarding pattern, no equipment placement; no one
approaches an intruder or enters an energised building alone.
"""
from __future__ import annotations

from companion.ch32 import sources as src  # noqa: F401  (puts plantp on the path)
from companion.ch32.common import emit

# ---------------------------------------------------------------- plan
PLAN = [  # (element, what the plan states, evidence that it works, links)
    ("risk assessment", "threats, who is harmed, proportionate measures",
     "screen reviewed yearly and after each event", "H, G"),
    ("access authorisation", "who may enter which area and why",
     "gate records reconciled weekly", "A (permits)"),
    ("visitors and contractors", "host, induction, escort where needed",
     "visitor log complete, inductions in date", "A (contractors)"),
    ("asset protection", "stores, marking, records of spares and cable",
     "stock counts match the records", "ch 52"),
    ("detection and reporting", "what is reported to whom, how fast",
     "notification times in the incident log", "control room"),
    ("roles and conduct", "who does what; conduct code; training",
     "training records; complaints reviewed", "ch 33"),
    ("incident response, evidence", "report, keep records, never confront",
     "records kept unchanged; police reference", "H"),
    ("community interface", "liaison; grievance route for security",
     "grievances closed with an outcome", "G, ch 33"),
    ("OT incident link", "entry to a control building -> OT check",
     "OT check logged after each entry event", "ch 36"),
    ("business continuity", "what is lost, how and when restored",
     "restore times exercised", "ch 36, ch 51"),
]


def plan() -> None:
    lines = ["the site-security management plan: ten elements",
             "  element                       evidence that it works"]
    for el, states, ev, link in PLAN:
        lines += [f"  {el:29s} {ev}",
                  f"      states: {states}; links: {link}"]
    lines += ["  an element without evidence is a declaration; the plan is",
              "  reviewed with the emergency plan (H) and the OT incident",
              "  response plan (ch 36), and owned by a named manager"]
    emit("i_plan", lines)


# ------------------------------------------------- access reconciliation
# [start: gate]
EMPLOYEES = [f"E{k:02d}" for k in range(1, 31)]
FIRMS = {"A": 10, "B": 8, "C": 5}          # contractor firms and people
INDUCTION_UNTIL = {f"B{k:02d}": 4 for k in (2, 5, 7)}   # expired after day 4
SUBSTATION_LIST = set(EMPLOYEES[:8]) | {f"C{k:02d}" for k in range(1, 6)}
VISITORS = [(f"V{k:02d}", 1 + k % 6, k not in (4, 9)) for k in range(1, 11)]
# (visitor, day, host recorded)
# [end: gate]


def gate_records() -> list[dict]:
    """One synthetic week (days 1-6 worked) at two gates, with the
    planted findings of lesson I."""
    recs = []
    for day in range(1, 7):
        for e in EMPLOYEES:
            recs.append(dict(day=day, who=e, kind="employee", gate="main",
                             out=True))
        for firm, n in FIRMS.items():
            for k in range(1, n + 1):
                who = f"{firm}{k:02d}"
                recs.append(dict(day=day, who=who, kind="contractor",
                                 gate="main", out=True))
        for v, d, host in VISITORS:
            if d == day:
                recs.append(dict(day=day, who=v, kind="visitor", gate="main",
                                 out=True, host=host))
        for e in EMPLOYEES[:6]:              # substation work by employees
            recs.append(dict(day=day, who=e, kind="employee",
                             gate="substation", out=True))
        for c in ("C01", "C02"):             # authorised contractors
            recs.append(dict(day=day, who=c, kind="contractor",
                             gate="substation", out=True))
    for who in ("A03", "A08"):               # not on the substation list
        recs.append(dict(day=3, who=who, kind="contractor",
                         gate="substation", out=True))
    for r in recs:                           # exits not badged on day 5
        if r["day"] == 5 and r["gate"] == "main" and r["who"] in (
                "E11", "E19", "E24", "B03"):
            r["out"] = False
    return recs


def reconcile(recs: list[dict]) -> dict:
    expired = [r for r in recs if r["kind"] == "contractor"
               and r["who"] in INDUCTION_UNTIL
               and r["day"] > INDUCTION_UNTIL[r["who"]]]
    no_host = [r for r in recs if r["kind"] == "visitor" and not r["host"]]
    area = [r for r in recs if r["gate"] == "substation"
            and r["who"] not in SUBSTATION_LIST]
    open_exit = [r for r in recs if not r["out"]]
    return dict(n=len(recs), expired=expired, no_host=no_host, area=area,
                open_exit=open_exit)


def access() -> None:
    recs = gate_records()
    res = reconcile(recs)
    people = sorted({r["who"] for r in res["expired"]})
    lines = ["a week of gate records reconciled with the authorisations",
             f"  entries: {res['n']} at two gates (main, substation)",
             f"  contractor entries after the induction expired: "
             f"{len(res['expired'])} ({len(people)} people, days 5-6)",
             f"  visitors without a host recorded: {len(res['no_host'])}",
             f"  substation entries without area authorisation: "
             f"{len(res['area'])}",
             f"  entries without a recorded exit: {len(res['open_exit'])}"
             " (all on day 5)"]
    on_site = len(res["open_exit"])
    lines += [f"  day 5 at 18:00 the records show {on_site} people on site;",
              "  the call-round found all of them had left (exit not",
              "  badged) - a muster built on these records would have",
              f"  searched for {on_site} people who were at home",
              "  owners: inductions -> the contractor's supervisor; area",
              "  list -> the substation authority; exits -> the gate",
              "  process; hosts -> the visitor procedure"]
    emit("i_access", lines)


# --------------------------------------------------- asset protection
# [start: assets]
EVENTS = {  # type: (rate a year, direct cost k u, outage cost k u)
    "earth conductor at a PV station": (1.0, 3.0, 0.0),
    "spare cable drums from the store": (0.5, 25.0, 0.0),
    "LV cable at a turbine pad": (0.3, 5.0, 3.5),
}
MEASURES = {  # name: (cost k u a year, rate factor by event type)
    "marking and records": (4.0, {"*": 0.7}),
    "stores control": (6.0, {"spare cable drums from the store": 0.2}),
    "community links": (3.0, {"*": 0.8}),
    "longer fence at PV stations": (20.0,
                                    {"earth conductor at a PV station": 0.5}),
}
# [end: assets]


def eal(factors: dict[str, float] | None = None) -> float:
    """Expected annual loss (k u a year) with optional rate factors."""
    total = 0.0
    for ev, (rate, direct, outage) in EVENTS.items():
        f = (factors or {}).get(ev, 1.0)
        total += rate * f * (direct + outage)
    return total


def factors_of(names) -> dict[str, float]:
    out = {ev: 1.0 for ev in EVENTS}
    for name in names:
        for key, f in MEASURES[name][1].items():
            for ev in EVENTS:
                if key in ("*", ev):
                    out[ev] *= f
    return out


def saving(names) -> float:
    """Net saving (k u a year) of a set of measures: loss avoided - cost."""
    return (eal() - eal(factors_of(names))
            - sum(MEASURES[n][0] for n in names))


def best_sets(top: int = 3) -> list[tuple[tuple[str, ...], float]]:
    names = list(MEASURES)
    sets = [tuple(n for k, n in enumerate(names) if mask >> k & 1)
            for mask in range(1, 2 ** len(names))]
    return sorted(((s, saving(s)) for s in sets), key=lambda t: -t[1])[:top]


def assets() -> None:
    base = eal()
    lines = ["asset protection: expected annual loss and measures (k u/yr)",
             f"  baseline expected loss: {base:.2f}",
             "  measure alone                 cost  benefit     net"]
    alone = 0.0
    for name, (cost, _) in MEASURES.items():
        benefit = base - eal(factors_of([name]))
        alone += benefit
        lines.append(f"  {name:29s} {cost:4.1f}  {benefit:7.2f}"
                     f"  {benefit - cost:+6.2f}")
    lines += [f"  benefits alone add to {alone:.2f} > the loss {base:.2f}:",
              "  measures overlap, so sets are compared, not items",
              "  best sets of the 15 (net saving):"]
    for names, net in best_sets():
        lines.append(f"    {net:+6.2f}  {' + '.join(names)}")
    pv = "earth conductor at a PV station"
    for label, names in (("stores control alone", ["stores control"]),
                         ("with marking and community", [
                             "stores control", "marking and records",
                             "community links"])):
        rate = EVENTS[pv][0] * factors_of(names)[pv]
        lines.append(f"  earth-conductor thefts a year, {label}: {rate:.2f}")
    for label, days in (("monthly inspection", 15.0), ("weekly look", 3.5)):
        lines.append(f"  station-days without earth a year, {label}: "
                     f"{EVENTS[pv][0] * days:.1f}")
    lines += ["  money ranks the measures; it does not rank the hazard: a",
              "  missing earth conductor leaves a station without its fault",
              "  path, so after any theft on site the stations' earthing is",
              "  inspected before anyone works there (ch 26); the owner",
              "  decides with both numbers in front of them"]
    emit("i_assets", lines)


# ------------------------------------------------- incident notification
# [start: incident]
NOTIFY = [  # (who, target minutes from the alarm, actual minutes or None)
    ("control room acknowledges", 5, 2),
    ("police informed", 15, 21),
    ("on-call manager", 15, 10),
    ("OT incident lead (ch 36)", 30, 390),
    ("grid operator (only if export or protection is affected)", 60, None),
    ("insurer (as the policy states)", 48 * 60, 33 * 60),
]
# [end: incident]


def incident() -> None:
    lines = ["intrusion alarm at the substation control building, 02:10",
             "  notification                   target  actual  status"]
    late = []
    for who, target, actual in NOTIFY:
        if actual is None:
            status, act = "not needed", "-"
        else:
            status = "ok" if actual <= target else "LATE"
            act = f"{actual:d}"
            if actual > target:
                late.append(who)
        name = who if len(who) <= 30 else who.split(" (")[0] + " *"
        lines.append(f"  {name:30s} {target:6d}  {act:>6s}  {status}")
    lines += ["  * only if export or protection is affected (it was not)",
              f"  late: {len(late)} - {'; '.join(late)}",
              "  cause of the long delay: the OT lead was not on the call",
              "  list; fix: add the role, and make 'entry to a control",
              "  building' a trigger in the OT response plan (ch 36)",
              "  the OT check found the configuration matching its",
              "  baseline; door and alarm logs were exported and kept",
              "  unchanged for the police; no one entered the building",
              "  until the police and the electrical authority allowed it"]
    emit("i_incident", lines)


# ---------------------------------------------- provider declarations
# [start: provider]
PROVIDER = [  # (item, declared, evidence seen)
    ("conduct code signed by every guard", True, "14 of 16 signed copies"),
    ("trained in the code and human rights", True, None),
    ("screening of past conduct", True, "12 of 16 files"),
    ("named supervising manager", True, "contract and rota"),
    ("security grievances handled outside the chain", True,
     "3 of 3 closed by liaison"),
    ("incident reports reviewed monthly", True, None),
]
# [end: provider]


def partial(evidence: str | None) -> bool:
    """True when the evidence covers only part ('12 of 16 files')."""
    if not evidence or " of " not in evidence:
        return False
    a, b = evidence.split(" of ")[:2]
    return int(a.split()[-1]) < int(b.split()[0])


def provider() -> None:
    verified = [p for p in PROVIDER if p[2]]
    part = [p for p in verified if partial(p[2])]
    lines = ["security provider: declared versus evidenced",
             f"  items declared: {len(PROVIDER)}; with evidence: "
             f"{len(verified)}, of which partial: {len(part)}"]
    for item, _, ev in PROVIDER:
        lines.append(f"  {item:46s} {ev or 'declared only'}")
    lines += ["  decision (owner's, concept): keep the contract on condition",
              "  of training records and the missing files within 30 days;",
              "  an untrained guard does not work (ch 33); the verified",
              "  findings are reported apart from the declarations (ch 39)"]
    emit("i_provider", lines)


if __name__ == "__main__":
    plan()
    access()
    assets()
    incident()
    provider()
