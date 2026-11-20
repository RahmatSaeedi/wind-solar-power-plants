"""Chapter 55, more lessons on the Iran dossier: the connection voltage as
scenarios, equipment classes against the mandatory lists, what a lapse of
the 1402 bylaw would reopen, the written questions grouped by addressee,
and why the sale terms matter (the chapter 21 model at three prices).

Run from the project root:   python -m companion.ch55.more
Writes companion/ch55/expected/m_*.txt.
Scenario values are TEACHING values (A-552 to A-556).
"""
from __future__ import annotations

import math

from companion.ch55 import common  # noqa: F401  (path)
from companion.ch55 import sources as src
from companion.ch55.common import emit
from plantp import compliance as cp

P_MW, PF = 100.0, 0.95
LOSS_132 = 754.0          # MWh/yr, single-circuit 132 kV line of ch 18 (f_export)


def voltage() -> dict:
    rows = []
    for u in (63, 132, 230, 400):
        i = P_MW * 1e6 / (math.sqrt(3) * u * 1e3 * PF)
        loss = LOSS_132 * (132 / u) ** 2
        rows.append((u, i, loss))
    from companion.ch55.common import csv
    csv("ch55-voltage.csv", "k,kv,amp,loss", [(k + 1, u, round(i), round(l))
                                             for k, (u, i, l) in enumerate(rows)])
    lines = ["the connection voltage as scenarios (100 MW at pf 0.95; the ch 18",
             "line conductor kept for a like-for-like loss comparison)",
             "  kV    current A   line loss MWh/yr   status of the voltage"]
    st = {63: "named (secondary, IR-17)", 132: "not in any source (A-556)",
          230: "named (secondary, IR-17)", 400: "named (secondary, IR-17)"}
    lines += [f"  {u:3d} {i:11.0f} {l:18.0f}   {st[u]}" for u, i, l in rows]
    lines += ["  the current, and with it the line loss and the switchgear,",
              "  follows the voltage the regional company names: at 63 kV the",
              f"  same line loses {rows[0][2] / rows[1][2]:.1f} times the 132 kV loss -",
              "  a different conductor, transformer and bay, not a footnote"]
    emit("m_voltage", lines)
    return dict(rows=rows)


CLASSES = [   # equipment class -> (status for Plant P, fact)
    ("main and unit power transformers", "mandatory national standard", "IR-30"),
    ("33 kV cables", "mandatory national standard", "IR-30"),
    ("battery cells (lithium)", "listed; scope for large ESS to confirm", "IR-49"),
    ("UPS and station batteries (VRLA)", "mandatory national standard", "IR-49"),
    ("PV inverters 5.5 MVA", "not on the list (list stops at 5 kW)", "IR-28"),
    ("PV modules", "not on the lists", "IR-29"),
    ("wind turbines", "not on the lists", "IR-29"),
]


def classes() -> list:
    lines = ["equipment classes of Plant P against the INSO mandatory lists"]
    for c, st, f in CLASSES:
        lines += [f"  {c:34s} {f}", f"      {st}"]
    must = sum(1 for _, st, _ in CLASSES if st.startswith("mandatory"))
    lines += [f"  {must} classes need a national conformity certificate on the",
              "  evidence found; for the others 'not listed' is not 'no rule':",
              "  each goes into the questions to INSO (IR-31) before ordering"]
    emit("m_classes", lines)
    return CLASSES


LINKS = {   # fact -> (instrument, Plant P records that rely on it)
    "IR-23": ("bylaw 1402", ["ch 14 land register", "ch 22 land parcels"]),
    "IR-24": ("bylaw 1402", ["ch 21 land lease in opex", "ch 49 start of works"]),
    "IR-43": ("bylaw 1402", ["ch 33 E&S plan", "approval map S3"]),
    "IR-45": ("bylaw 1402", ["ch 14 setback layers", "ch 30 layout"]),
    "IR-46": ("bylaw 1402", ["ch 33 land and livelihood plan"]),
    "IR-18": ("amendment 1403", ["ch 21 transmission charges = 0"]),
    "IR-36": ("amendment 1403", ["ch 21 sale-route scenarios"]),
    "IR-39": ("amendment 1403", ["ch 39 import and FX plan"]),
}


def lapse() -> dict:
    hit = cp.edition_impact(LINKS, "bylaw 1402")
    hit2 = cp.edition_impact(LINKS, "amendment 1403")
    lines = ["if the 1402 bylaw lapsed (IR-10) - and with it its amendment",
             f"  records resting on the bylaw: {len(hit)}"]
    lines += [f"    {f}: {r}" for f, r in hit]
    lines += [f"  records resting on the 1403 amendment: {len(hit2)}"]
    lines += [f"    {f}: {r}" for f, r in hit2]
    lines += ["  one written answer (in force? extended? replaced?) decides",
              f"  {len(hit) + len(hit2)} records across six chapters: the first letter",
              "  to the Cabinet secretariat and SATBA"]
    emit("m_lapse", lines)
    return dict(n=len(hit) + len(hit2))


def letters() -> dict:
    by = {}
    for f in src.FACTS:
        if f["status"] != "verified":
            by.setdefault(f.get("ask", "project team"), []).append(f)
    lines = ["written questions, one letter per addressee"]
    for who, fs in sorted(by.items(), key=lambda kv: -len(kv[1])):
        lines.append(f"  to {who} ({len(fs)}):")
        lines += [f"    {f['id']}: {f['text']}" for f in fs]
    emit("m_letters", lines)
    return by


def routes() -> dict:
    from companion.ch21 import model
    lines = ["why the sale terms matter: the chapter 21 model at three prices",
             "(teaching; the real price comes from the contract or the market)",
             f"  {'price vs base':14s} {'debt k u':>9s} {'min DSCR':>9s} {'equity IRR':>11s}"]
    out = {}
    for k in (0.8, 1.0, 1.2):
        r = model.run(price_scale=k, sizing_price=k)
        out[k] = r
        lines.append(f"  {k:14.0%} {r['debt']:9,.0f} {r['min_dscr']:9.2f}"
                     f" {r['equity_irr']:11.1%}")
    lines += [f"  a 20 % lower price takes {out[1.0]['debt'] - out[0.8]['debt']:,.0f} k u"
              " of debt away and moves",
              f"  the equity IRR by {(out[0.8]['equity_irr'] - out[1.0]['equity_irr']) * 100:+.1f}"
              " points: without IR-38 (term, currency,",
              "  indexation, security) there is no base case, only a range"]
    emit("m_routes", lines)
    return out


SITES = [   # official sites tried on 2026-11-17: (site, result)
    ("satba.gov.ir", "no answer"), ("moe.gov.ir", "no answer"),
    ("tavanir.org.ir", "no answer"), ("igmc.ir", "no answer"), ("doe.ir", "no answer"),
    ("irenex.ir", "no answer"), ("mcls.gov.ir", "no answer"), ("mcth.ir", "no answer"),
    ("qavanin.ir", "blocked (script check)"), ("cao.ir", "blocked (HTTP 403)"),
    ("inso.gov.ir", "read"), ("wrm.ir", "read"), ("frw.ir", "read"),
]


def sites() -> dict:
    by = {}
    for s, r in SITES:
        key = "read" if r == "read" else ("blocked" if r.startswith("blocked") else "no answer")
        by[key] = by.get(key, 0) + 1
    lines = ["research log: official sites tried on 2026-11-17"]
    lines += [f"  {s:16s} {r}" for s, r in SITES]
    lines += [f"  read {by.get('read', 0)}, no answer {by.get('no answer', 0)},"
              f" blocked {by.get('blocked', 0)} of {len(SITES)}",
              "  the laws and bylaws came from the Majlis Research Center prints;",
              "  an unreachable site is a finding with a date and a retry, not",
              "  a reason to use a summary instead"]
    emit("m_sites", lines)
    return by


INTERPS = [   # id, fact, question, why it matters
    ("IN-01", "IR-43", "is a hybrid of 60 MW wind + 50 MW PV one plant or two?",
     "100 MW threshold for the environmental route"),
    ("IN-02", "IR-26", "may a company with foreign shareholders take national land?",
     "who can hold the land lease"),
    ("IN-03", "IR-18", "what is 'network capacity' and who declares it?",
     "curtailment without compensation"),
    ("IN-04", "IR-24", "what counts as works started within a year?",
     "loss of the land before financial close"),
    ("IN-05", "IR-43", "does silence after a week cover every inquiry?",
     "start of works without a written answer"),
    ("IN-06", "IR-18", "how does the financing law limit the no-fee rule?",
     "transmission charges in the model"),
]


def interps() -> list:
    lines = ["interpretations the Iran dossier needs in writing"]
    for i, f, q, why in INTERPS:
        lines += [f"  {i} ({f}) {q}", f"      decides: {why}"]
    lines += [f"  {len(INTERPS)} readings; none may be settled by the design team -",
              "  each is a written question to the authority or counsel (ch 54 C)"]
    emit("m_interps", lines)
    return INTERPS


def schedule() -> dict:
    tasks = {k: (v["months"], v["after"]) for k, v in src.APPROVALS.items()}
    es, ef = {}, {}
    order, done = [], set()
    while len(order) < len(tasks):
        for t, (_, pre) in tasks.items():
            if t not in done and all(p in done for p in pre):
                order.append(t)
                done.add(t)
    for t in order:
        d, pre = tasks[t]
        es[t] = max((ef[p] for p in pre), default=0.0)
        ef[t] = es[t] + d
    lines = ["month-by-month plan from the approval map (teaching durations)",
             "  step  start  finish  what"]
    for t in sorted(order, key=lambda x: (es[x], x)):
        lines.append(f"  {t:4s} {es[t]:6.1f} {ef[t]:7.1f}  {src.APPROVALS[t]['what']}")
    first = [t for t in order if es[t] == 0.0]
    lines += [f"  month 0: {', '.join(first)} and every letter of section D;",
              "  the written answers decide whether these months hold"]
    emit("m_schedule", lines)
    return dict(es=es, ef=ef)


IFC = [   # performance standard -> where Plant P - Iran needs it if lenders apply it
    ("PS1 E&S assessment and management", "law asks an inquiry only (IR-43)"),
    ("PS2 labour and working conditions", "Labour Code (secondary, IR not listed)"),
    ("PS3 resource efficiency, pollution", "water permit (IR-21), waste"),
    ("PS4 community health, safety, security", "no rule found below 300 MW"),
    ("PS5 land acquisition, resettlement", "compensation sourced (IR-46)"),
    ("PS6 biodiversity", "setbacks sourced (IR-45); habitats to screen"),
    ("PS7 indigenous peoples", "applicability by qualified review only"),
    ("PS8 cultural heritage", "heritage setback (IR-45); procedure tbc"),
]


def ifc() -> list:
    lines = ["IFC Performance Standards (STD-108) against the Iran sources",
             "  (they apply only if the lenders require them)"]
    for ps, where in IFC:
        lines += [f"  {ps}", f"      Iran sources: {where}"]
    lines += ["  where the law is silent and the lenders are not, the project's",
              "  own commitments carry the item - recorded as commitments"]
    emit("m_ifc", lines)
    return IFC


CAPABILITY = [   # what Plant P can offer if asked; source chapter of the number
    ("reactive power at 100 MW, 25 C", "+46 / -63 Mvar (study model)", "ch 28"),
    ("reactive power at 100 MW, test", "30.6 Mvar lagging (DEV-11)", "ch 50"),
    ("unit ride-through", "as the maker's type-test report states", "ch 44"),
    ("frequency droop (battery S1)", "4 % on 110 MW, 20 MW cap", "ch 20"),
    ("ramp limiting", "PPC setting, any value asked", "ch 20"),
    ("telemetry", "IEC 60870-5-104 or IEC 61850 at the PPC", "ch 35"),
]


def capability() -> list:
    lines = ["what Plant P can offer if the grid operator asks (teaching values)"]
    for c, v, ch in CAPABILITY:
        lines += [f"  {c:34s} {ch}", f"      {v}"]
    lines += ["  capability is ready; requirement, qualification and payment are",
              "  not sourced (IR-19, IR-33): nothing is offered in the base"]
    emit("m_capability", lines)
    return CAPABILITY


RISKS = [   # id, risk, fact, likelihood 1-5, impact 1-5, owner (TEACHING scores)
    ("R01", "the 1402 bylaw lapsed, routes reopen", "IR-10", 3, 4, "permitting lead"),
    ("R02", "connection voltage other than 132 kV", "IR-17", 4, 4, "grid engineer"),
    ("R03", "no published connection requirements", "IR-19", 4, 3, "grid engineer"),
    ("R04", "land returned if works do not start in a year", "IR-24", 2, 5, "permitting lead"),
    ("R05", "curtailment 'within capacity' without pay", "IR-18", 3, 3, "commercial lead"),
    ("R06", "sanctions block equipment, payment or lenders", "IR-40", 4, 5, "counsel"),
    ("R07", "FX allocation for imports delayed", "IR-39", 3, 4, "finance lead"),
    ("R08", "PPA terms unknown, revenue a range", "IR-38", 4, 5, "commercial lead"),
    ("R09", "national certificate needed after ordering", "IR-31", 3, 3, "procurement"),
    ("R10", "heritage find during works, no procedure", "IR-48", 2, 3, "E&S manager"),
]


def risks() -> list:
    rows = sorted(RISKS, key=lambda r: -(r[3] * r[4]))
    from companion.ch55.common import csv
    csv("ch55-risks.csv", "id,l,i", [(r[0], r[3], r[4]) for r in RISKS])
    lines = ["country risk register of Plant P - Iran (TEACHING scores 1-5)",
             "  id   L  I  score  owner             fact"]
    for i, t, f, l, im, o in rows:
        lines.append(f"  {i}  {l}  {im}  {l * im:5d}  {o:17s} {f}")
        lines.append(f"       {t}")
    top = [r[0] for r in rows if r[3] * r[4] >= 16]
    lines += [f"  score 16 and above: {', '.join(top)} - each carries an action",
              "  (a letter, a design option, counsel) and a date; the scores",
              "  are teaching values, the facts behind them are sourced"]
    emit("m_risks", lines)
    return rows


DECISIONS = {   # fact -> earlier Plant P decisions it touches
    "IR-17": ["D-022 architecture", "D-029 transformers", "D-032 grid study"],
    "IR-19": ["D-024 control", "D-031 power quality", "D-032 grid study"],
    "IR-18": ["D-025 finance"],
    "IR-38": ["D-025 finance"],
    "IR-24": ["D-026 site and schedule", "D-053 construction start"],
    "IR-43": ["D-037 E&S basis"],
    "IR-21": ["D-033 civil and water"],
    "IR-30": ["D-043 procurement", "D-050 cable and switchgear"],
    "IR-40": ["D-043 procurement", "D-025 finance"],
}


def decisions() -> dict:
    by = {}
    for f, ds in DECISIONS.items():
        for d in ds:
            by.setdefault(d, []).append(f)
    lines = ["earlier Plant P decisions that the Iran dossier touches"]
    for d, fs in sorted(by.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        lines.append(f"  {d:28s} {', '.join(fs)}")
    top = sorted(by.items(), key=lambda kv: -len(kv[1]))
    lines += [f"  {len(by)} decisions, one from each of {len(by)} chapters; {top[0][0]}"
              f" carries {len(top[0][1])} facts,",
              f"  {top[1][0]} and {top[2][0]} {len(top[1][1])} each - each decision is"
              " revised",
              "  when its answers arrive, with a change record (ch 38)"]
    emit("m_decisions", lines)
    return by


def watch() -> dict:
    issuers = {}
    for f in src.FACTS:
        key = f["source"].split(";")[0].split(",")[0][:38]
        issuers.setdefault(key, []).append(f["status"])
    monthly = [k for k, v in issuers.items() if "to-confirm" in v]
    lines = [f"source watch: {len(issuers)} distinct sources behind {len(src.FACTS)} facts",
             f"  checked monthly (a to-confirm fact rests on them): {len(monthly)}",
             f"  checked before each gate (all verified): {len(issuers) - len(monthly)}",
             "  each check is dated in the register, and 'no change' is",
             "  recorded too (ch 54 B)"]
    emit("m_watch", lines)
    return dict(n=len(issuers), monthly=len(monthly))


if __name__ == "__main__":
    decisions()
    watch()
    risks()
    voltage()
    classes()
    lapse()
    letters()
    routes()
    sites()
    interps()
    schedule()
    ifc()
    capability()
