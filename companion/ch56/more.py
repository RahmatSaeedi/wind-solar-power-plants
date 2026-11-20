"""Chapter 56, more lessons on the Afghanistan dossier: the connection
voltage between the two levels in use, which grid island the plant would
join, late payment by the buyer in the chapter 21 model, the written
questions by addressee, and the numerical answers.

Run from the project root:   python -m companion.ch56.more
Writes companion/ch56/expected/m_*.txt and solutions.txt.
Scenario values are TEACHING values (A-557 to A-561).
"""
from __future__ import annotations

import contextlib
import io
import math

import numpy as np

from companion.ch56 import common  # noqa: F401  (path)
from companion.ch56 import run
from companion.ch56 import sources as src
from companion.ch56.common import emit

P_MW, PF = 100.0, 0.95
LOSS_132 = 754.0


def voltage() -> dict:
    rows = []
    for u in (110, 132, 220):
        i = P_MW * 1e6 / (math.sqrt(3) * u * 1e3 * PF)
        rows.append((u, i, LOSS_132 * (132 / u) ** 2))
    from companion.ch56.common import csv
    csv("ch56-voltage.csv", "k,kv,amp,loss", [(k + 1, u, round(i), round(l))
                                             for k, (u, i, l) in enumerate(rows)])
    st = {110: "in use (AF-11)", 132: "no source (AF-12)", 220: "in use (AF-11)"}
    lines = ["the two voltages in use against the book's 132 kV (100 MW, pf 0.95;",
             "the ch 18 conductor kept for a like-for-like loss comparison)",
             "  kV    current A   line loss MWh/yr   status"]
    lines += [f"  {u:3d} {i:11.0f} {l:18.0f}   {st[u]}" for u, i, l in rows]
    lines += ["  a 100 MW plant at 110 kV carries 1.2 times the 132 kV current;",
              "  at 220 kV 0.6 times - the design follows the level DABS names",
              "  for the substation the plant joins"]
    emit("m_voltage", lines)
    return dict(rows=rows)


ISLANDS = [   # system, how it is fed (secondary, AF-10), what it means for a 100 MW plant
    ("north-east system (NEPS)", "imports from Uzbekistan and Tajikistan",
     "frequency set by the exporting system or by the island itself?"),
    ("Herat zone", "imports from Iran and Turkmenistan",
     "the wind resource is here (AF-16); isolated from NEPS"),
    ("south (Kandahar)", "described as unconnected to the central grid",
     "small system: a 100 MW plant could be most of its load"),
]


def islands() -> list:
    lines = ["which grid island would Plant P join? (AF-10, secondary)"]
    for s, fed, q in ISLANDS:
        lines += [f"  {s}", f"      fed by: {fed}", f"      question: {q}"]
    lines += ["  the island decides the fault level, the frequency behaviour",
              "  and how much variable output it can absorb - it is the first",
              "  question of the grid-data request, before any study"]
    emit("m_islands", lines)
    return ISLANDS


def late_payment() -> dict:
    from companion.ch21 import model
    lines = ["the buyer pays part of year 3 late (chapter 21 model, teaching)",
             f"  {'months late':12s} {'min DSCR':>9s} {'equity IRR':>11s}"]
    out = {}
    for m in (0, 3, 6, 9):
        r = model.run(default_months=m, debt=model.run()["debt"])
        out[m] = r
        lines.append(f"  {m:12d} {r['min_dscr']:9.2f} {r['equity_irr']:11.1%}")
    worst = out[9]
    lines += [f"  nine months late in one year: minimum DSCR {worst['min_dscr']:.2f}"
              " - the six-",
              "  month reserve and a payment-security instrument are what a",
              "  lender asks for when payment terms are unpublished (AF-29)"]
    emit("m_late", lines)
    return out


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


def solutions(r: dict, v: dict, late: dict, by: dict) -> None:
    tot = r["status"]["tot"]
    a = r["approvals"]
    out = [
        f"P01 facts: {len(src.FACTS)}; verified {tot['verified']}, project-dependent"
        f" {tot['project-dependent']}, to-confirm {tot['to-confirm']}",
        f"P02 to-confirm on secondary sources only: {r['status']['sec']}",
        f"P03 approval path (teaching): {a['total']:.1f} months",
        f"P04 critical path: {' > '.join(a['crit'])}",
        f"P05 not verified on the critical path: {', '.join(a['tcc'])}",
        f"P06 grid inputs complete: {r['grid']['complete']:.0%};"
        f" missing {len(r['grid']['missing'])} of {len(src.GRID_NEED)}",
        f"P07 certificate items not shown: {sum(1 for x in r['cert'] if x[1] != 'shown')}"
        f" of {len(r['cert'])}",
        f"P08 open stages: AF-17 {len(r['traces']['AF-17'])}, AF-14"
        f" {len(r['traces']['AF-14'])}",
        f"P09 services verified: {r['services']['verified']} of 6",
        f"P10 finance items verified: {r['finance']['verified']} of 9",
        f"P11 open issues: {sum(r['issues'].values())} to {len(r['issues'])} addressees",
        "P12 options with every constraint met and known: "
        + ", ".join(k for k, x in r["compare"].items()
                    if x["fails"] == 0 and x["unknown"] == 0),
        f"P13 current at 110 / 220 kV: {v['rows'][0][1]:.0f} / {v['rows'][2][1]:.0f} A",
        f"P14 min DSCR with 9 months late: {late[9]['min_dscr']:.2f}",
        "P15 generated domestically vs imported (Aug 2025, secondary): 250 vs 800 MW",
        "P16 contracts of 27 Mar 2025: 228.45 MW, AFN 20.7 bn (AF-32)",
        "P17 contracts of 11 Feb 2026: 845 MW (AF-33)",
        "P18 ESIA authorisation validity: 3 years (AF-35)",
        "P19 generation licence term in the 2016 law: up to 25 years (AF-06)",
        "P20 connection answer in the 2016 law: 40 business days (AF-13)",
    ]
    emit("solutions", out)


SITES = [
    ("mew.gov.af", "read (posts to 17 Nov 2026)"), ("dpmea.gov.af", "read"),
    ("nepa.gov.af", "read (document links script-only)"), ("asqa.gov.af", "read"),
    ("main.dabs.af", "script-only, not read"), ("mudh.gov.af", "read (last item 2025)"),
    ("ansa.gov.af", "does not resolve"), ("mudl.gov.af", "does not resolve"),
    ("nwara.gov.af", "does not resolve"), ("aop.gov.af", "certificate error"),
]


def sites() -> dict:
    by = {"read": 0, "not read": 0}
    for s, r in SITES:
        by["read" if r.startswith("read") else "not read"] += 1
    lines = ["research log: official and de facto authority sites, 2026-11-17"]
    lines += [f"  {s:14s} {r}" for s, r in SITES]
    lines += [f"  read {by['read']}, not read {by['not read']} of {len(SITES)}",
              "  pre-2021 laws were read as gazette PDFs or the ministry's",
              "  English translation; whether each is applied is a separate",
              "  question (the review of earlier laws has no published result)"]
    emit("m_sites", lines)
    return by


INTERPS = [
    ("IN-01", "AF-06", "is the 2016 licence regime applied to a new IPP today?",
     "licence, guarantee and term of the plant"),
    ("IN-02", "AF-03", "what does the Economic Commission's approval contain?",
     "what the contract with DABS may rely on"),
    ("IN-03", "AF-09", "which body leases state land, on which terms?",
     "the land route and its security for lenders"),
    ("IN-04", "AF-18", "which water-permit category fits a power plant?",
     "water for construction and cleaning"),
    ("IN-05", "AF-34", "which ESIA category does a 100 MW hybrid fall in?",
     "preliminary or full ESIA, and its time"),
    ("IN-06", "AF-28", "may the PPA be priced or indexed in a foreign currency?",
     "currency risk of the whole revenue"),
]


def interps() -> list:
    lines = ["interpretations the Afghanistan dossier needs in writing"]
    for i, f, q, why in INTERPS:
        lines += [f"  {i} ({f}) {q}", f"      decides: {why}"]
    lines += [f"  {len(INTERPS)} readings, each a written question with a dated answer"]
    emit("m_interps", lines)
    return INTERPS


def schedule() -> dict:
    tasks = {k: (v["months"], v["after"]) for k, v in src.APPROVALS.items()}
    es, ef, order, done = {}, {}, [], set()
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
    emit("m_schedule", lines)
    return dict(es=es, ef=ef)


IFC = [
    ("PS1 E&S assessment and management", "ESIA regulation listed (AF-34)"),
    ("PS2 labour and working conditions", "no source read"),
    ("PS3 resource efficiency, pollution", "water guideline (AF-17)"),
    ("PS4 community health, safety, security", "no source read"),
    ("PS5 land acquisition, resettlement", "2016 law Art 23 (AF-37), status tbc"),
    ("PS6 biodiversity", "ESIA screening (AF-34)"),
    ("PS7 indigenous peoples", "applicability by qualified review only"),
    ("PS8 cultural heritage", "2004 law (AF-40), procedure tbc"),
]


def ifc() -> list:
    lines = ["IFC Performance Standards (STD-108) against the Afghanistan sources",
             "  (they apply only if the lenders require them)"]
    for ps, where in IFC:
        lines += [f"  {ps}", f"      Afghanistan sources: {where}"]
    lines += ["  lenders that can lend at all (AF-25, AF-27) bring their own",
              "  frameworks; the dossier records which one, with its source"]
    emit("m_ifc", lines)
    return IFC


PRE2021 = {   # fact -> records of Plant P that would rest on it (if applied)
    "AF-05": ["approval map S4", "regulator in the PPA dispute clause"],
    "AF-06": ["licence term 25 years in ch 21 model", "financial guarantee"],
    "AF-13": ["connection schedule S8 (40 business days)"],
    "AF-19": ["water permit basis (with AF-17)"],
    "AF-20": ["land lease route S6", "lenders' security over land"],
    "AF-37": ["resettlement plan (ch 33, appendix L)"],
    "AF-38": ["land acquisition route"],
}


def pre2021() -> dict:
    n = sum(len(v) for v in PRE2021.values())
    lines = ["records that would rest on pre-2021 instruments (text read,",
             "application unknown - the review of earlier laws has no result)"]
    for f, recs in PRE2021.items():
        lines += [f"  {f}: {r}" for r in recs]
    lines += [f"  {n} records on {len(PRE2021)} facts: each is designed as if the",
              "  instrument applied AND carries a question to the ministry or",
              "  counsel - the design does not wait, the label does not change"]
    emit("m_pre2021", lines)
    return dict(n=n)


RISKS = [
    ("R01", "payments delayed or blocked (banking, currency)", "AF-27", 4, 5, "finance lead"),
    ("R02", "tariff and contract terms unpublished", "AF-29", 4, 5, "commercial lead"),
    ("R03", "island system too small or weak for 100 MW", "AF-10", 4, 4, "grid engineer"),
    ("R04", "no connection rules, studies on assumptions", "AF-14", 4, 3, "grid engineer"),
    ("R05", "land title contested (state-land declarations)", "AF-39", 3, 5, "counsel"),
    ("R06", "import route closed, equipment delayed", "AF-41", 4, 4, "logistics lead"),
    ("R07", "no local service for turbines or inverters", "AF-42", 4, 4, "O&M lead"),
    ("R08", "sanctions regimes other than US not reviewed", "AF-26", 3, 4, "counsel"),
    ("R09", "pre-2021 law not applied as written", "AF-06", 3, 3, "counsel"),
    ("R10", "imported equipment rejected at inspection", "AF-22", 3, 3, "procurement"),
]


def risks() -> list:
    from companion.ch56.common import csv
    csv("ch56-risks.csv", "id,l,i", [(r[0], r[3], r[4]) for r in RISKS])
    rows = sorted(RISKS, key=lambda r: -(r[3] * r[4]))
    lines = ["country risk register of Plant P - Afghanistan (TEACHING scores 1-5)",
             "  id   L  I  score  owner             fact"]
    for i, t, f, l, im, o in rows:
        lines += [f"  {i}  {l}  {im}  {l * im:5d}  {o:17s} {f}", f"       {t}"]
    top = [r[0] for r in rows if r[3] * r[4] >= 16]
    lines += [f"  score 16 and above: {', '.join(top)}",
              "  the scores are teaching values; the facts behind them carry",
              "  their own labels, most of them secondary"]
    emit("m_risks", lines)
    return rows


CAPABILITY = [
    ("reactive power at 100 MW, 25 C", "+46 / -63 Mvar (study model)", "ch 28"),
    ("frequency droop (battery S1)", "4 % on 110 MW, 20 MW cap", "ch 20"),
    ("island support (grid-forming)", "not offered in the base (D-024)", "ch 20"),
    ("ramp limiting", "PPC setting, any value asked", "ch 20"),
    ("telemetry", "IEC 60870-5-104 or IEC 61850 at the PPC", "ch 35"),
]


def capability() -> list:
    lines = ["what Plant P can offer an island system (teaching values)"]
    for c, v, ch in CAPABILITY:
        lines += [f"  {c:34s} {ch}", f"      {v}"]
    lines += ["  in a small island a 100 MW plant may be asked for what the",
              "  base does not offer (grid-forming, reserve): the request",
              "  would reopen D-024 and the battery case of ch 19-21"]
    emit("m_capability", lines)
    return CAPABILITY


def spares() -> dict:
    """Spares to hold at 90 % for three import lead times (ch 52 rates)."""
    from companion.ch52 import sources as s52
    from plantp import ram
    rows = []
    for cls in ("PV inverter", "wind turbine (major)", "BESS PCS"):
        n, rate = s52.CLASSES[cls][0], s52.CLASSES[cls][1]
        fleet = n * rate / 8760.0
        rows.append((cls, n, rate, [ram.spares_needed(fleet, w * 168.0, 0.90)
                                    for w in (8, 16, 26)]))
    lines = ["spares held in the country at 90 % confidence (ch 52 failure rates)",
             f"  {'class':22s} {'units':>5s} {'rate/yr':>8s}   lead 8 wk  16 wk  26 wk"]
    for cls, n, rate, s in rows:
        lines.append(f"  {cls:22s} {n:5d} {rate:8.2f}   {s[0]:9d} {s[1]:6d} {s[2]:6d}")
    inv = rows[0][3]
    lines += [f"  PV inverters: {inv[0]} spares at 8 weeks, {inv[2]} at 26 - a closed import",
              "  route that stretches the lead time raises the stock; a major",
              "  turbine part stays at one, but waiting 26 weeks for it IS the",
              "  outage: spares are a priced service decision (ch 52, AF-41)"]
    emit("m_spares", lines)
    return dict(rows=rows)


DECISIONS = {
    "AF-10": ["D-032 grid study", "D-024 control"],
    "AF-11": ["D-022 architecture", "D-029 transformers"],
    "AF-14": ["D-031 power quality", "D-032 grid study"],
    "AF-29": ["D-025 finance"],
    "AF-27": ["D-025 finance"],
    "AF-41": ["D-035 logistics", "D-043 procurement"],
    "AF-42": ["D-056 maintenance", "D-043 procurement"],
    "AF-17": ["D-033 civil and water"],
    "AF-34": ["D-037 E&S basis"],
    "AF-39": ["D-026 site", "D-037 E&S basis"],
}


def decisions() -> dict:
    by = {}
    for f, ds in DECISIONS.items():
        for d in ds:
            by.setdefault(d, []).append(f)
    top = sorted(by.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    lines = ["earlier Plant P decisions that the Afghanistan dossier touches"]
    lines += [f"  {d:24s} {', '.join(fs)}" for d, fs in top]
    lines += [f"  {len(by)} decisions; four carry two open facts each:",
              f"  {top[0][0]}, {top[1][0]},",
              f"  {top[2][0]}, {top[3][0]} - revised with a change record (ch 38)"]
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
             "  the official pages of the current authorities are watched",
             "  for the outcome of the review of earlier laws"]
    emit("m_watch", lines)
    return dict(n=len(issuers), monthly=len(monthly))


ISLANDS_T = (300.0, 600.0, 1200.0)   # teaching island sizes, MW of load (A-561)


def island_frequency() -> dict:
    """Plant P trips in islands of teaching size (ch 28 aggregated model,
    no load shedding modelled). H 3 s, governors 5 % droop, 20 % respond."""
    from plantp import gridstudy as gs
    t = np.arange(0.0, 20.0, 0.01)
    rows, curves = [], {}
    for s in ISLANDS_T:
        for loss in (100.0, 50.0):
            o = gs.freq_event(t, s, 3.0, loss, gov=(0.05, 6.0, 0.20))
            rows.append((s, loss, o["nadir"], o["rocof"]))
            if loss == 100.0:
                curves[s] = o["f"]

    def largest(s, limit=49.0):
        lo, hi = 0.0, s
        for _ in range(40):
            mid = (lo + hi) / 2
            if gs.freq_event(t, s, 3.0, mid, gov=(0.05, 6.0, 0.20))["nadir"] >= limit:
                lo = mid
            else:
                hi = mid
        return lo
    big = {s: largest(s) for s in ISLANDS_T}
    lines = ["Plant P trips in an island (teaching sizes, no load shedding)",
             f"  {'island MW':>9s} {'loss MW':>8s} {'nadir Hz':>9s} {'RoCoF Hz/s':>11s}"]
    for s, loss, nad, rc in rows:
        lines.append(f"  {s:9.0f} {loss:8.0f} {nad:9.2f} {rc:11.2f}")
    lines.append("  largest single loss with the nadir at or above 49.0 Hz (teaching):")
    lines += [f"    island {s:5.0f} MW: {big[s]:5.1f} MW" for s in ISLANDS_T]
    lines += ["  if one fault can trip the whole plant, the loss is 100 MW; a",
              "  design in which no single fault trips more than half halves it -",
              "  a question for DABS with its shedding settings (AF-10, AF-14)"]
    emit("m_island_f", lines)
    from companion.ch56.common import csv
    idx = range(0, len(t), 20)
    csv("ch56-island.csv", "t,f300,f600,f1200",
        [(round(t[i], 2), round(curves[300.0][i], 3), round(curves[600.0][i], 3),
          round(curves[1200.0][i], 3)) for i in idx])
    return dict(rows=rows, big=big)


def derate() -> dict:
    """Teaching derating curve of ch 9 (knee 40 C, 2 %/K; 1 %/100 m above
    1,000 m) at teaching site values; the real curve is the maker's."""
    from plantp import pe
    temps = (35.0, 40.0, 45.0, 48.0, 50.0)
    alts = (0.0, 1000.0, 1800.0, 2500.0)
    lines = ["PV inverter output (per unit) by ambient and altitude (teaching curve)",
             "  " + f"{'C / m':>6s}" + "".join(f"{a:>8.0f}" for a in alts)]
    for tc in temps:
        lines.append("  " + f"{tc:6.0f}" + "".join(
            f"{float(pe.derating(tc, a)):8.3f}" for a in alts))
    k = float(pe.derating(48.0, 1800.0))
    n_need = int(np.ceil(50.0 / (5.5 * k)))
    lines += [f"  at 48 C and 1,800 m (A-558): {k:.3f} - ten 5.5 MVA units give"
              f" {10 * 5.5 * k:.1f} MVA",
              f"  for 50 MW AC at that corner: {n_need} units, or accept a lower",
              "  output on the hottest hours and record it in the capability",
              "  statement given to DABS (ch 9, 28)"]
    emit("m_derate", lines)
    return dict(k=k, n=n_need)


def approval_cases() -> dict:
    from plantp import appraisal
    import copy
    cases = [("base (teaching)", {}),
             ("land lease 8 months", {"S6": 8.0}),
             ("land lease 12 months", {"S6": 12.0}),
             ("full ESIA 10 months", {"S5": 10.0}),
             ("contract with DABS 6 months", {"S3": 6.0}),
             ("2016 licence before the contract", "lic")]
    lines = ["approval plan under changed durations (teaching, months)",
             f"  {'case':34s} {'total':>6s}  critical path"]
    out = {}
    for name, ch in cases:
        a = copy.deepcopy(src.APPROVALS)
        if ch == "lic":
            a["S3"]["after"] = ["S2", "S4"]
        else:
            for k, v in ch.items():
                a[k]["months"] = v
        tasks = {k: (v["months"], v["after"]) for k, v in a.items()}
        total, crit, _ = appraisal.critical_path(tasks)
        out[name] = (total, crit)
        lines.append(f"  {name:34s} {total:6.1f}  {' > '.join(crit)}")
    base_t = out["base (teaching)"][0]
    tasks0 = {k: (v["months"], v["after"]) for k, v in src.APPROVALS.items()}
    fl = appraisal.critical_path(tasks0)[2]["S5"]
    add = out["full ESIA 10 months"][0] - base_t
    lines += ["  a month added to a step on the critical path is a month added",
              f"  to the plan (land lease, contract); the ESIA has {fl:.0f} months of",
              f"  float, so 6 more months add {add:.0f}; a licence before the",
              f"  contract adds {out['2016 licence before the contract'][0] - base_t:.0f}"
              " by putting S4 on the path"]
    emit("m_cases", lines)
    return out


def iran_vs() -> dict:
    from companion.ch55 import engine as en
    from companion.ch55 import sources as s55
    quiet = lambda *a, **k: None
    rows = []
    for name, s in (("Iran", s55), ("Afghanistan", src)):
        st = en.status_table(s, quiet)
        ap = en.approvals(s, quiet)
        g = en.grid_gaps(s, quiet)
        c = en.cert(s, quiet)
        iss = en.issues(s, quiet)
        n = len(s.FACTS)
        rows.append((name, n, st["tot"]["verified"] / n, st["sec"], ap["total"],
                     len(ap["tcc"]), g["complete"],
                     sum(1 for r in c if r[1] != "shown"), len(c),
                     sum(iss.values()), len(iss)))
    lines = ["two dossiers by the same engine (ch 55 and ch 56)",
             f"  {'measure':38s} {'Iran':>8s} {'Afgh.':>8s}"]
    labels = [("facts", 1, "{:d}"), ("verified share", 2, "{:.0%}"),
              ("to-confirm on secondary sources only", 3, "{:d}"),
              ("approval plan, months (teaching)", 4, "{:.1f}"),
              ("unverified steps on the critical path", 5, "{:d}"),
              ("grid-study inputs given", 6, "{:.0%}")]
    for lab, i, f in labels:
        lines.append(f"  {lab:38s} {f.format(rows[0][i]):>8s} {f.format(rows[1][i]):>8s}")
    lines.append(f"  {'certificate items not shown':38s} "
                 f"{f'{rows[0][7]}/{rows[0][8]}':>8s} {f'{rows[1][7]}/{rows[1][8]}':>8s}")
    lines.append(f"  {'open items / addressees':38s} "
                 f"{f'{rows[0][9]}/{rows[0][10]}':>8s} {f'{rows[1][9]}/{rows[1][10]}':>8s}")
    lines += ["  the same method gives different gaps: in Iran mostly project",
              "  values under rules in force; in Afghanistan also whether the",
              "  written rules apply at all (pre-2021 texts)"]
    emit("m_iran_vs", lines)
    return dict(rows=rows)


def reserve() -> dict:
    """Months of debt service a reserve must hold so that a late buyer in
    year 3 does not leave service unpaid (ch 21 model, teaching)."""
    from companion.ch21 import model
    base = model.run()
    ds3 = float(base["ds"][2])
    lines = ["reserve needed against late payment in year 3 (ch 21 model, teaching)",
             f"  debt service in year 3: {ds3:,.0f} k u",
             f"  {'months late':12s} {'CFADS k u':>10s} {'shortfall k u':>14s}"
             f" {'reserve months':>15s}"]
    out = {}
    for m in (3, 6, 9, 12):
        r = model.run(default_months=m, debt=base["debt"])
        cf = float(r["cfads"][2])
        short = max(ds3 - cf, 0.0)
        months = short / (ds3 / 12)
        out[m] = months
        lines.append(f"  {m:12d} {cf:10,.0f} {short:14,.0f} {months:15.1f}")
    cover = max(m for m, v in out.items() if v <= 6.0)
    lines += [f"  a six-month reserve covers up to {cover} months late in one year;",
              "  longer delays need a payment guarantee or a liquidity facility",
              "  (ch 21 F; teaching values, not advice)"]
    emit("m_reserve", lines)
    return dict(ds=ds3, months=out, cover=cover)


def water_request() -> dict:
    """Quantity for the water-use permit request (AF-17): ch 29's demand
    (A-352), RO recovery of ch 29, three washing policies (teaching)."""
    from companion.ch29 import sources as s29
    from companion.ch29 import examples_g as g29
    d = s29.DEMAND
    wash = d["modules"] * d["wash_l_module"] / 1000.0
    staff_y = d["staff"] * d["staff_l_day"] * 365 / 1000.0
    policies = [("ch 10 trigger (14 washes)", 14), ("dusty year (24 washes)", 24),
                ("drought: robots + 4 washes", 4)]
    lines = ["water-use permit request: raw water a year (teaching, A-352)",
             f"  one wash: {wash:.1f} m3 treated = {wash / g29.RO_RECOVERY:.1f} m3 raw"
             f" (RO {g29.RO_RECOVERY:.0%})",
             f"  staff: {staff_y:.0f} m3 a year",
             f"  {'policy':30s} {'raw m3/yr':>10s} {'peak month m3':>14s}"]
    out = {}
    for name, n in policies:
        raw = n * wash / g29.RO_RECOVERY + staff_y
        per_month = max(round(n * w / 14) for w in d["washes"]) if n else 0
        peak = per_month * wash / g29.RO_RECOVERY + staff_y / 12
        out[name] = (raw, peak)
        lines.append(f"  {name:30s} {raw:10,.0f} {peak:14,.0f}")
    hi = max(v[0] for v in out.values())
    lo = min(v[0] for v in out.values())
    lines += [f"  the request states a range ({lo:,.0f}-{hi:,.0f} m3 a year) and the",
              "  drought policy; the rule's conditions (aquifer balance, no harm",
              "  to residents) need a hydrogeological study (ch 29, AF-17, AF-18)"]
    emit("m_water", lines)
    return out


def permit_life(n: int = 20_000) -> dict:
    """Does the 3-year environmental permit (AF-35) outlast the start or the
    end of construction? Triangular durations (0.8 d, d, 2 d) for each
    approval step, financial close (6, 9, 18) and construction 18 months -
    all teaching (A-557)."""
    from plantp import appraisal
    rng = np.random.default_rng(56)
    tasks0 = {k: (v["months"], v["after"]) for k, v in src.APPROVALS.items()}
    permit, start, cod = np.empty(n), np.empty(n), np.empty(n)
    for i in range(n):
        tasks = {k: (rng.triangular(0.8 * d, d, 2.0 * d), pre)
                 for k, (d, pre) in tasks0.items()}
        total, _, _ = appraisal.critical_path(tasks)
        ef = {}
        for k in ("S1", "S5"):
            d, pre = tasks[k]
            ef[k] = d + max((ef[p] for p in pre), default=0.0)
        permit[i] = ef["S5"]
        start[i] = total + rng.triangular(6.0, 9.0, 18.0)
        cod[i] = start[i] + 18.0
    p_start = float(np.mean(start - permit > 36.0))
    p_cod = float(np.mean(cod - permit > 36.0))
    lines = ["does the 3-year environmental permit outlast the works? (teaching)",
             f"  permit issued, month P50/P90: {np.percentile(permit, 50):.1f} /"
             f" {np.percentile(permit, 90):.1f}",
             f"  construction start P50/P90: {np.percentile(start, 50):.1f} /"
             f" {np.percentile(start, 90):.1f}",
             f"  end of construction P50/P90: {np.percentile(cod, 50):.1f} /"
             f" {np.percentile(cod, 90):.1f}",
             f"  chance the start falls after the permit's 3 years: {p_start:.1%}",
             f"  chance the end of construction falls after it:    {p_cod:.0%}",
             "  what the validity covers (start, works or operation) is a",
             "  written question to NEPA (AF-35); the plan carries a renewal",
             "  step if it covers the works"]
    emit("m_permit", lines)
    return dict(p_start=p_start, p_cod=p_cod)


def indexation() -> dict:
    """A contract in afghani (AF-28) with debt in another currency: the
    share of the tariff indexed to the exchange rate needed to keep the
    minimum DSCR at the 1.05 default level (ch 54 method, ch 21 model)."""
    from companion.ch54 import examples_e as e54
    b = model_base()
    lines = ["tariff in afghani, debt in another currency (teaching):",
             "  share of the tariff indexed to the rate for min DSCR >= 1.05",
             f"  {'weakens a year':15s} {'min DSCR, none':>15s} {'share needed':>13s}"]
    out = {}
    for w in (0.02, 0.05, 0.08):
        none = e54.fx_case(b, w)["min"]
        if none >= 1.05:
            need = 0.0
        else:
            lo, hi = 0.0, 1.0
            for _ in range(40):
                mid = (lo + hi) / 2
                if e54.fx_case(b, w * (1 - mid))["min"] >= 1.05:
                    hi = mid
                else:
                    lo = mid
            need = hi
        out[w] = (none, need)
        lines.append(f"  {w:15.0%} {none:15.2f} {need:13.0%}")
    eff = max(w * (1 - n) for w, (_, n) in out.items())
    lines += [f"  in each case the unindexed part may weaken by about {eff:.2%} a year",
              "  at most; the rate itself is not forecast here; what is verified is the",
              "  contract's currency and indexation clause and who carries the",
              "  risk (AF-28, AF-29; ch 54 E; not financial advice)"]
    emit("m_index", lines)
    return out


def model_base() -> dict:
    from companion.ch21 import model
    return model.run()


def line_length() -> dict:
    """Connection line of 100 MW at 110 or 220 kV, the ch 24 teaching
    conductor (0.10 + j0.40 ohm/km, A-324) for both: voltage change and
    loss by length; a 220 kV line would use a larger conductor."""
    from companion.ch24 import sources as s24
    r, x = s24.LINE["r20"], s24.LINE["x"]
    p, q = P_MW, P_MW * math.tan(math.acos(PF))
    lines = ["connection line for 100 MW: voltage change and loss by length",
             f"  (teaching conductor {r:.2f} + j{x:.2f} ohm/km for both levels)",
             f"  {'kV':>4s} {'km':>5s} {'dV % pf 1':>10s} {'dV % pf 0.95':>13s}"
             f" {'loss %':>7s}"]
    rows = []
    for u in (110, 220):
        i = p * 1e6 / (math.sqrt(3) * u * 1e3 * PF)
        for km in (20, 50, 100, 150):
            dv1 = r * km * p / u ** 2 * 100
            dv = (r * km * p + x * km * q) / u ** 2 * 100
            loss = 3 * i ** 2 * r * km / (p * 1e6) * 100
            rows.append((u, km, dv1, dv, loss))
            lines.append(f"  {u:4d} {km:5d} {dv1:10.1f} {dv:13.1f} {loss:7.1f}")
    lim = {u: 5.0 * u ** 2 / (100 * (r * p + x * q)) for u in (110, 220)}
    lines += [f"  5 % change at pf 0.95 is reached at {lim[110]:.0f} km (110 kV) and"
              f" {lim[220]:.0f} km (220 kV)",
              "  a site far from the grid (AF-16: Farah has none) brings the",
              "  line, its owner and its losses into the connection agreement"]
    emit("m_line", lines)
    return dict(rows=rows, lim=lim)


if __name__ == "__main__":
    indexation()
    line_length()
    water_request()
    permit_life()
    island_frequency()
    derate()
    approval_cases()
    iran_vs()
    reserve()
    spares()
    decisions()
    watch()
    pre2021()
    risks()
    capability()
    with contextlib.redirect_stdout(io.StringIO()):
        res = run.main()
    vv = voltage()
    islands()
    lp = late_payment()
    lt = letters()
    sites()
    interps()
    schedule()
    ifc()
    solutions(res, vv, lp, lt)
