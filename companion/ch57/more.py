"""Chapter 57, more lessons on the Tajikistan dossier: connection voltage,
research log, letters, interpretations, the month plan, IFC map, risks,
what Plant P can offer against Resolution 449, decisions touched, source
watch, the hydro season and curtailment under two readings, a USD-fixed
tariff seen from the buyer, PPA term and payment days in the chapter 21
model, metering class, seismic zones, approval cases, three dossiers by
one engine, and the numerical answers.

Run from the project root:   python -m companion.ch57.more
Writes companion/ch57/expected/m_*.txt and solutions.txt.
Scenario values are TEACHING values (A-562 to A-566).
"""
from __future__ import annotations

import contextlib
import copy
import io
import math

import numpy as np

from companion.ch57 import common  # noqa: F401  (path)
from companion.ch57 import run
from companion.ch57 import sources as src
from companion.ch57.common import csv, emit

P_MW, PF = 100.0, 0.95
LOSS_132 = 754.0          # MWh/yr on the ch 18 line at 132 kV (ch 56 m_voltage)
NET_GWH = 295.14          # model 15.1, P50 year 1 at the POC (D-019)
PRICE = 70.0              # u/MWh, ch 21 PPA tariff (A-307)
QUIET = staticmethod(lambda *a, **k: None)


def voltage() -> dict:
    rows = []
    for u in (110, 132, 220, 500):
        i = P_MW * 1e6 / (math.sqrt(3) * u * 1e3 * PF)
        rows.append((u, i, LOSS_132 * (132 / u) ** 2))
    csv("ch57-voltage.csv", "k,kv,amp,loss", [(k + 1, u, round(i), round(l))
                                             for k, (u, i, l) in enumerate(rows)])
    st = {110: "secondary (TJ-21)", 132: "no source", 220: "Sughd site (TJ-20)",
          500: "secondary (TJ-21)"}
    lines = ["connection voltage for 100 MW (pf 0.95; the ch 18 conductor kept",
             "for a like-for-like loss comparison)",
             "  kV    current A   line loss MWh/yr   source"]
    lines += [f"  {u:3d} {i:11.0f} {l:18.0f}   {st[u]}" for u, i, l in rows]
    lines += ["  220 kV is the level named next to a real tender site; 500 kV",
              "  is a backbone level, not a connection level for 100 MW; the",
              "  level comes in the technical conditions (TJ-23)"]
    emit("m_voltage", lines)
    return dict(rows=rows)


SITES = [
    ("mewr.tj", "read (RFQ pdf, Resolution 449 docx)"),
    ("barqitojik.tj", "read (structure, tariffs)"), ("shib.tj", "read"),
    ("standard.tj", "read"), ("investcom.tj", "read"), ("khf.tj", "read (warnings)"),
    ("adlia.tj (legal portal)", "unreachable"), ("mmk.tj (legal portal)", "unreachable"),
    ("egov.tj", "listing only"), ("environment committee", "no own site found"),
]


def sites() -> dict:
    by = {"read": 0, "not read": 0}
    for s, r in SITES:
        by["read" if r.startswith("read") else "not read"] += 1
    lines = ["research log: official sites, 2026-11-17"]
    lines += [f"  {s:24s} {r}" for s, r in SITES]
    lines += [f"  read {by['read']}, not read {by['not read']} of {len(SITES)}",
              "  with both legal portals down, laws were read in the FAOLEX and",
              "  UN-ESCAP repositories: the text is official, but whether it is",
              "  the latest consolidated version needs a dated check"]
    emit("m_sites", lines)
    return by


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


INTERPS = [
    ("IN-01", "TJ-11", "does a 100 MW plant need a permit under Law 1968?",
     "an approval step and its time (S10)"),
    ("IN-02", "TJ-26", "curtailment: rules say no breach, the model PPA pays",
     "lost profit - which governs, and what is 'permitted'?"),
    ("IN-03", "TJ-50", "what are the 'state guarantees' for late payment?",
     "the payment security lenders will ask for"),
    ("IN-04", "TJ-40", "GOST 32144-2013 or GOST 13109-97 for power quality?",
     "the limits the plant is tested against"),
    ("IN-05", "TJ-56", "which EIA rules apply while the new Code enters force?",
     "the content and time of S6"),
    ("IN-06", "TJ-13", "who is the single buyer and dispatcher before 2027?",
     "the PPA counterparty and the SCADA end point"),
    ("IN-07", "TJ-45", "is the RES conformity certificate still required?",
     "a test and a certificate before first sale"),
]


def interps() -> list:
    lines = ["interpretations the Tajikistan dossier needs in writing"]
    for i, f, q, why in INTERPS:
        lines += [f"  {i} ({f}) {q}", f"      decides: {why}"]
    lines += [f"  {len(INTERPS)} readings, each a written question with a dated answer"]
    emit("m_interps", lines)
    return INTERPS


def _es_ef(approvals: dict):
    tasks = {k: (v["months"], v["after"]) for k, v in approvals.items()}
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
    return es, ef, order


def schedule() -> dict:
    es, ef, order = _es_ef(src.APPROVALS)
    lines = ["month-by-month plan from the approval map (teaching durations)",
             "  step  start  finish  what"]
    for t in sorted(order, key=lambda x: (es[x], int(x[1:]))):
        lines.append(f"  {t:4s} {es[t]:6.1f} {ef[t]:7.1f}  {src.APPROVALS[t]['what']}")
    emit("m_schedule", lines)
    return dict(es=es, ef=ef)


IFC = [
    ("PS1 E&S assessment and management", "EIA rules in transition (TJ-56, TJ-57)"),
    ("PS2 labour and working conditions", "no source read"),
    ("PS3 resource efficiency, pollution", "Water Code permit (TJ-31)"),
    ("PS4 community health, safety, security", "mudflow warnings (TJ-35)"),
    ("PS5 land acquisition, resettlement", "state land, use rights (TJ-36, TJ-60)"),
    ("PS6 biodiversity", "KBA near the Sughd site (TJ-61)"),
    ("PS7 indigenous peoples", "applicability by qualified review only"),
    ("PS8 cultural heritage", "heritage law (TJ-59)"),
]


def ifc() -> list:
    lines = ["IFC Performance Standards (STD-108) against the Tajikistan sources",
             "  (the World Bank Group backs the Sughd tender, TJ-54)"]
    for ps, where in IFC:
        lines += [f"  {ps}", f"      Tajikistan sources: {where}"]
    lines += ["  where a lender applies its standards, they sit beside the",
              "  national rules; the stricter requirement governs (ch 54 A)"]
    emit("m_ifc", lines)
    return IFC


RISKS = [
    ("R01", "summer curtailment, compensation unclear", "TJ-26", 4, 4, "commercial lead"),
    ("R02", "single buyer and dispatcher not designated", "TJ-13", 4, 4, "commercial lead"),
    ("R03", "late-payment remedy undefined", "TJ-50", 3, 5, "finance lead"),
    ("R04", "convertibility and repatriation", "TJ-51", 3, 5, "finance lead"),
    ("R05", "no adopted grid code, studies on assumptions", "TJ-22", 4, 3, "grid engineer"),
    ("R06", "seismic qualification of substation equipment", "TJ-34", 3, 4, "electrical lead"),
    ("R07", "EIA rules in transition", "TJ-56", 4, 3, "E&S lead"),
    ("R08", "heavy loads on mountain routes", "TJ-37", 3, 4, "logistics lead"),
    ("R09", "two power-quality standards cited", "TJ-40", 3, 2, "grid engineer"),
    ("R10", "land use rights for a foreign-owned company", "TJ-36", 3, 4, "counsel"),
]


def risks() -> list:
    csv("ch57-risks.csv", "id,l,i", [(r[0], r[3], r[4]) for r in RISKS])
    rows = sorted(RISKS, key=lambda r: -(r[3] * r[4]))
    lines = ["country risk register of Plant P - Tajikistan (TEACHING scores 1-5)",
             "  id   L  I  score  owner             fact"]
    for i, t, f, l, im, o in rows:
        lines += [f"  {i}  {l}  {im}  {l * im:5d}  {o:17s} {f}", f"       {t}"]
    top = [r[0] for r in rows if r[3] * r[4] >= 16]
    lines += [f"  score 16 and above: {', '.join(top)}",
              "  the scores are teaching values; the facts behind them carry",
              "  their own labels"]
    emit("m_risks", lines)
    return rows


CAPABILITY = [
    ("real-time data to the dispatcher (TJ-24)", "SCADA gateway, IEC 60870-5-104", "ch 35"),
    ("remote curtailment (TJ-24)", "PPC set point, any value asked", "ch 20"),
    ("hourly forecasts (TJ-24)", "day-ahead and intraday forecasts", "ch 15"),
    ("power-factor control (TJ-23)", "+46 / -63 Mvar at 100 MW (study model)", "ch 28"),
    ("anti-islanding and f/V tripping (TJ-23)", "protection settings file", "ch 26"),
    ("metering class 0.5S (TJ-25)", "revenue metering chain", "ch 48"),
]


def capability() -> list:
    lines = ["what Plant P offers against the obligations of Resolution 449"]
    for c, v, ch in CAPABILITY:
        lines += [f"  {c:42s} {ch}", f"      {v}"]
    lines += ["  each obligation has a design answer in earlier chapters; what",
              "  is missing are the values (protocol, forecast format, tripping",
              "  settings) that the technical conditions will give"]
    emit("m_capability", lines)
    return CAPABILITY


DECISIONS = {
    "TJ-22": ["D-032 grid study", "D-030 protection"],
    "TJ-24": ["D-039 SCADA", "D-024 control"],
    "TJ-25": ["D-052 metering hardware"],
    "TJ-26": ["D-025 finance", "D-024 control"],
    "TJ-34": ["D-034 structures", "D-029 transformers"],
    "TJ-40": ["D-031 power quality"],
    "TJ-14": ["D-025 finance"],
    "TJ-37": ["D-035 logistics"],
    "TJ-56": ["D-037 E&S basis"],
    "TJ-36": ["D-026 site"],
}


def decisions() -> dict:
    by = {}
    for f, ds in DECISIONS.items():
        for d in ds:
            by.setdefault(d, []).append(f)
    top = sorted(by.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    two = [d for d, fs in top if len(fs) >= 2]
    lines = ["earlier Plant P decisions that the Tajikistan dossier touches"]
    lines += [f"  {d:24s} {', '.join(fs)}" for d, fs in top]
    lines += [f"  {len(by)} decisions; {len(two)} carry two open facts each:",
              f"  {', '.join(two)} - revised with a change record (ch 38)"]
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
             "  the legal portals are re-tried each month for consolidated",
             "  texts; the new Environmental Code is watched for its start"]
    emit("m_watch", lines)
    return dict(n=len(issuers), monthly=len(monthly))


# ------------------------------------------------------------ hydro season
def _monthly():
    rows = []
    path = common.DATA / "ch15-monthly.csv"
    with open(path, encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            m, w, p, n = line.strip().split(",")
            rows.append((int(m), float(w), float(p), float(n)))
    return rows


SUMMER = (5, 6, 7, 8, 9)          # high-water months, teaching (TJ-27)


def season() -> dict:
    rows = _monthly()
    tot = sum(r[3] for r in rows)
    summer = sum(r[3] for r in rows if r[0] in SUMMER)
    winter = sum(r[3] for r in rows if r[0] in (10, 11, 12, 1, 2, 3))
    w_s = sum(r[1] for r in rows if r[0] in SUMMER) / sum(r[1] for r in rows)
    p_s = sum(r[2] for r in rows if r[0] in SUMMER) / sum(r[2] for r in rows)
    lines = ["Plant P's monthly energy (model 15.1, data-pack site) against a",
             "hydro system that is long in summer and short in winter",
             f"  net {tot:.1f} GWh; May-Sep {summer:.1f} ({summer / tot:.0%});"
             f" Oct-Mar {winter:.1f} ({winter / tot:.0%})",
             f"  share in May-Sep: wind {w_s:.0%}, PV {p_s:.0%}",
             "  the energy the system needs most (winter) and the energy it",
             "  may curtail (summer, high water) - the PPA decides who bears",
             "  the summer risk (TJ-26, TJ-27; profile from the data-pack site)"]
    emit("m_season", lines)
    return dict(tot=tot, summer=summer, winter=winter, share=summer / tot)


PERMITTED = 0.02                   # teaching 'permitted' curtailment, share of year


def curtail() -> dict:
    """Two readings of TJ-26: (A) rules - curtailment is never compensated;
    (B) model PPA - lost profit is paid beyond a permitted value (teaching
    2 % of the year's energy). Summer curtailment of 0-40 % of May-Sep."""
    from companion.ch21 import model
    s = season()["share"]
    base = model.run()
    lines = ["curtailment in the high-water months under two readings (ch 21",
             f"model, debt as sized; permitted = {PERMITTED:.0%} of the year, teaching)",
             f"  {'summer cut':>10s} {'year cut':>9s}   {'A: min DSCR':>11s} {'IRR':>6s}"
             f"   {'B: min DSCR':>11s} {'IRR':>6s}"]
    out = {}
    for c in (0.0, 0.10, 0.20, 0.40):
        y = s * c
        a = model.run(curtail_extra=y, debt=base["debt"])
        b = model.run(curtail_extra=min(y, PERMITTED), debt=base["debt"])
        out[c] = (y, a, b)
        lines.append(f"  {c:10.0%} {y:9.1%}   {a['min_dscr']:11.2f} {a['equity_irr']:6.1%}"
                     f"   {b['min_dscr']:11.2f} {b['equity_irr']:6.1%}")
    y20, a20, b20 = out[0.20]
    lines += [f"  at 20 % of summer energy ({y20:.1%} of the year) the readings give",
              f"  a minimum DSCR of {a20['min_dscr']:.2f} against {b20['min_dscr']:.2f};"
              f" equity IRR {a20['equity_irr']:.1%} against",
              f"  {b20['equity_irr']:.1%}: the reading (IN-02) is settled in writing"
              " before the bid"]
    emit("m_curtail", lines)
    return out


# ------------------------------------------------- USD tariff, buyer's view
TJS_USD = 9.2027                   # 12.11.2026 (secondary, TJ-51 note)
PRICE_USD_KWH = 0.040              # teaching purchase price (A-564)
HOME = 0.4137                      # TJS/kWh incl. VAT (TJ-48)
INDUSTRY = 0.9465


def buyer() -> dict:
    lines = ["a USD-fixed price paid in somoni, seen from the buyer (teaching",
             f"price {PRICE_USD_KWH * 1000:.0f} USD/MWh; rate {TJS_USD} TJS/USD; retail"
             " tariffs held flat)",
             f"  household tariff {HOME} TJS/kWh, industry {INDUSTRY} (incl. VAT, TJ-48)",
             f"  {'somoni weakens':>14s} {'yr 0':>6s} {'yr 5':>6s} {'yr 10':>6s}"
             f" {'yr 15':>6s}  above the household tariff from"]
    out, curves = {}, {}
    for w in (0.0, 0.03, 0.06):
        cost = [PRICE_USD_KWH * TJS_USD / (1 - w) ** y for y in range(26)]
        curves[w] = cost
        first = next((y for y, c in enumerate(cost) if c > HOME), None)
        out[w] = (cost, first)
        lines.append(f"  {w:14.0%} {cost[0]:6.3f} {cost[5]:6.3f} {cost[10]:6.3f}"
                     f" {cost[15]:6.3f}  {('year ' + str(first)) if first is not None else 'never'}")
    csv("ch57-buyer.csv", "y,w0,w3,w6,home",
        [(y, round(curves[0.0][y], 4), round(curves[0.03][y], 4),
          round(curves[0.06][y], 4), HOME) for y in range(26)])
    lines += [f"  the purchase price alone starts at {out[0.0][0][0] / HOME:.0%} of the"
              " household tariff,",
              "  before network costs and losses: a USD-fixed price moves the",
              "  currency risk to the buyer, and the buyer's margin is where",
              "  payment risk (R03) begins - figures teaching, not a forecast"]
    emit("m_buyer", lines)
    return out


# ------------------------------------------- PPA term and payment days
def terms() -> dict:
    from companion.ch21 import model
    from companion.ch21 import sources as s21
    keep = copy.deepcopy(s21.TERMS)
    out = {}
    lines = ["PPA term and payment days in the ch 21 model (teaching)",
             f"  {'case':34s} {'min DSCR':>9s} {'equity IRR':>11s} {'debt k u':>10s}"]
    cases = [("PPA 15 years (minimum, TJ-12)", {"ppa_years": 15}),
             ("PPA 20 years (ch 21 base)", {}),
             ("PPA 25 years (Sughd tender, TJ-14)", {"ppa_years": 25}),
             ("paid in 10 banking days (TJ-49)", {"receivable_days": 14}),
             ("paid at the 30-day cap (TJ-49)", {"receivable_days": 30})]
    try:
        for name, ch in cases:
            s21.TERMS.clear()
            s21.TERMS.update(copy.deepcopy(keep))
            s21.TERMS.update(ch)
            r = model.run()
            out[name] = r
            lines.append(f"  {name:34s} {r['min_dscr']:9.2f} {r['equity_irr']:11.1%}"
                         f" {r['debt']:10,.0f}")
    finally:
        s21.TERMS.clear()
        s21.TERMS.update(keep)
    b = out["PPA 20 years (ch 21 base)"]
    p15 = out["PPA 15 years (minimum, TJ-12)"]
    p25 = out["PPA 25 years (Sughd tender, TJ-14)"]
    lines += [f"  15 against 20 years: equity IRR {p15['equity_irr'] - b['equity_irr']:+.1%};"
              f" 25 years: {p25['equity_irr'] - b['equity_irr']:+.1%}",
              "  the debt (15 years) sits inside even the shortest PPA; the",
              "  years after the PPA are merchant at the teaching 45 u/MWh"]
    emit("m_terms", lines)
    return out


def metering() -> dict:
    lines = ["meter class and the money it can move (teaching price, ch 21)",
             f"  energy at the POC {NET_GWH} GWh a year (model 15.1)",
             f"  {'class':6s} {'+/- GWh':>8s} {'+/- k u a year':>15s} {'over 15 yr':>11s}"]
    out = {}
    for cl, pct in (("0.5S", 0.5), ("1.0", 1.0)):
        e = NET_GWH * pct / 100
        money = e * 1000 * PRICE / 1000
        out[cl] = (e, money)
        lines.append(f"  {cl:6s} {e:8.2f} {money:15.0f} {money * 15:11.0f}")
    lines += ["  the class is the meter's limit, not its error; with CT and VT",
              "  errors added (ch 48) the chain is wider: choose 0.5S at the",
              "  boundary even where 1.0 is allowed (TJ-25)"]
    emit("m_metering", lines)
    return out


ZONES = {7: 0.10, 8: 0.20, 9: 0.40}   # teaching ag for MSK zones (A-565), not SNiP values


def seismic() -> dict:
    from companion.ch30 import sources as s30
    from plantp import structures as st
    tc = s30.SITE["tc"]

    def sa(t, ag):
        return 2.5 * ag if t <= tc else 2.5 * ag * tc / t

    top = (s30.TOP_T + 0.24 * s30.TOWER_T) * 1e3
    t_turb = 1 / s30.F1_FIXED
    base_tr = st.base_shear(95e3, sa(0.15, s30.SITE["ag"]))
    lines = ["seismic zones of SNiP RT 22-07-2018 (TJ-34) with TEACHING ground",
             f"accelerations (ch 30 spectrum; ch 30 basis ag = {s30.SITE['ag']} g)",
             f"  {'zone':>4s} {'ag g':>5s} {'transformer kN':>15s} {'vs ch 30':>9s}"
             f" {'turbine MN m':>13s}"]
    out = {}
    for z, ag in ZONES.items():
        v_tr = st.base_shear(95e3, sa(0.15, ag))
        m_t = st.base_shear(top, sa(t_turb, ag)) * s30.HUB / 1e6
        out[z] = (v_tr, v_tr / base_tr, m_t)
        lines.append(f"  {z:4d} {ag:5.2f} {v_tr / 1e3:15.0f} {v_tr / base_tr:9.2f}"
                     f" {m_t:13.0f}")
    wind = s30.LOADS["extreme (parked, 50-yr gust)"]["m_mnm"]
    lines += [f"  turbine: wind ({wind:.0f} MN m) still governs in zone 9;",
              f"  transformer: zone 9 is {out[9][1]:.1f} times the ch 30 basis - anchors,",
              "  plinth and bushings are re-checked; the code's own coefficients",
              "  (not read here) replace the teaching ag (TJ-34; Khujand 8, Dushanbe 9)"]
    emit("m_seismic", lines)
    return out


def approval_cases() -> dict:
    from plantp import appraisal
    cases = [("base (teaching)", {}),
             ("competitive procedure 9 months", {"S1": 9.0}),
             ("EIA under the new Code 10 months", {"S6": 10.0}),
             ("energy-expertise issuer found late +3", {"S8": 5.0}),
             ("Law 1968 permit before the PPA", "permit")]
    lines = ["approval plan under changed durations (teaching, months)",
             f"  {'case':38s} {'total':>6s}  critical path"]
    out = {}
    for name, ch in cases:
        a = copy.deepcopy(src.APPROVALS)
        if ch == "permit":
            a["S3"]["after"] = ["S1", "S10"]
        else:
            for k, v in ch.items():
                a[k]["months"] = v
        tasks = {k: (v["months"], v["after"]) for k, v in a.items()}
        total, crit, _ = appraisal.critical_path(tasks)
        out[name] = (total, crit)
        lines.append(f"  {name:38s} {total:6.1f}  {' > '.join(crit)}")
    b = out["base (teaching)"][0]
    lines += [f"  every case on the S1 > S6 > S8 > S9 chain adds its full change;",
              f"  the permit before the PPA adds {out['Law 1968 permit before the PPA'][0] - b:.0f}"
              " (S3 has 7 months of float)"]
    emit("m_cases", lines)
    return out


def three() -> dict:
    from companion.ch55 import engine as en
    from companion.ch55 import sources as s55
    from companion.ch56 import sources as s56
    quiet = lambda *a, **k: None
    rows = []
    for s in (s55, s56, src):
        st = en.status_table(s, quiet)
        ap = en.approvals(s, quiet)
        g = en.grid_gaps(s, quiet)
        c = en.cert(s, quiet)
        iss = en.issues(s, quiet)
        n = len(s.FACTS)
        rows.append((n, st["tot"]["verified"] / n, st["sec"], ap["total"], len(ap["tcc"]),
                     g["complete"], sum(1 for r in c if r[1] != "shown"), len(c),
                     sum(iss.values()), len(iss)))
    lines = ["three dossiers by one engine (ch 55, 56, 57)",
             f"  {'measure':34s} {'Iran':>7s} {'Afgh.':>7s} {'Tajik.':>7s}"]
    fm = [("facts", 0, "{:d}"), ("verified share", 1, "{:.0%}"),
          ("to-confirm on secondary only", 2, "{:d}"),
          ("approval plan, months (teaching)", 3, "{:.1f}"),
          ("unverified on the critical path", 4, "{:d}"),
          ("grid-study inputs given", 5, "{:.0%}")]
    for lab, i, f in fm:
        lines.append(f"  {lab:34s}" + "".join(f" {f.format(r[i]):>7s}" for r in rows))
    lines.append(f"  {'certificate items not shown':34s}"
                 + "".join(f" {str(r[6]) + '/' + str(r[7]):>7s}" for r in rows))
    lines.append(f"  {'open items / addressees':34s}"
                 + "".join(f" {str(r[8]) + '/' + str(r[9]):>7s}" for r in rows))
    lines += ["  Tajikistan has the newest connection rules of the three",
              "  (Resolution 449, 2026) and the longest teaching plan: its",
              "  route runs through a competitive procedure and two expertises"]
    emit("m_three", lines)
    return dict(rows=rows)


def solutions(r: dict, v: dict) -> None:
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
        f"P08 open stages: TJ-25 {len(r['traces']['TJ-25'])}, TJ-24"
        f" {len(r['traces']['TJ-24'])}, TJ-22 {len(r['traces']['TJ-22'])}",
        f"P09 services verified: {r['services']['verified']} of 6",
        f"P10 finance items verified: {r['finance']['verified']} of 9",
        f"P11 open issues: {sum(r['issues'].values())} to {len(r['issues'])} addressees",
        "P12 options with every constraint met and known: "
        + ", ".join(k for k, x in r["compare"].items()
                    if x["fails"] == 0 and x["unknown"] == 0),
        f"P13 current at 220 kV: {v['rows'][2][1]:.0f} A",
        "P14 PPA minimum term above 1 MW: 15 years (TJ-12); Sughd: 25 (TJ-14)",
        "P15 technical conditions: free, within 30 working days (TJ-23)",
        "P16 payment: in somoni, 10 banking days, <= 30 days after month-end (TJ-49)",
        "P17 meter class at the boundary: 1.0 or 0.5S (TJ-25)",
        "P18 seismic zone: Khujand 8, Dushanbe 9 MSK-64 (TJ-34)",
        "P19 household / industry tariff incl. VAT: 0.4137 / 0.9465 TJS/kWh (TJ-48)",
        "P20 SCADA, real-time data, remote curtailment, forecasts above 1 MW (TJ-24)",
    ]
    emit("solutions", out)


def schedule_risk(n: int = 20_000) -> dict:
    """Approval plan with triangular durations (0.8 d, d, 2 d) for every
    step (teaching, A-562): P50/P80/P90 and how often each step is on the
    critical path (criticality index)."""
    from plantp import appraisal
    rng = np.random.default_rng(57)
    tasks0 = {k: (v["months"], v["after"]) for k, v in src.APPROVALS.items()}
    tot = np.empty(n)
    crit = {k: 0 for k in tasks0}
    for i in range(n):
        tasks = {k: (rng.triangular(0.8 * d, d, 2.0 * d), pre)
                 for k, (d, pre) in tasks0.items()}
        t, c, _ = appraisal.critical_path(tasks)
        tot[i] = t
        for k in c:
            crit[k] += 1
    p50, p80, p90 = (float(np.percentile(tot, q)) for q in (50, 80, 90))
    lines = ["approval plan with uncertain durations (triangular 0.8 d - d - 2 d,",
             f"teaching; {n:,} runs)",
             f"  deterministic 16.0 months; P50 {p50:.1f}, P80 {p80:.1f}, P90 {p90:.1f}",
             "  step  on the critical path in"]
    order = sorted(crit, key=lambda k: -crit[k])
    lines += [f"  {k:4s} {crit[k] / n:6.0%}   {src.APPROVALS[k]['what']}" for k in order
              if crit[k] > 0]
    cr = {k: v / n for k, v in crit.items()}
    lines += [f"  the expertise chain (S8, S9) is critical in {cr['S8']:.0%} of runs,"
              f" S6 in {cr['S6']:.0%};",
              f"  the land and water branch (S2, S7, S11) in {cr['S7']:.0%}, the"
              f" connection branch",
              f"  (S4, S5 into S8) in {cr['S5']:.0%}: the plan is longer than its"
              " deterministic",
              f"  16 months in {float(np.mean(tot > 16.0)):.0%} of runs"]
    emit("m_schedrisk", lines)
    return dict(p50=p50, p80=p80, p90=p90, crit={k: v / n for k, v in crit.items()})


def vat() -> dict:
    """If equipment VAT (14 %, secondary) were a cost - not exempt (TJ-52
    unconfirmed) and not recovered - capex would rise by 14 % of the
    equipment share. Teaching sensitivity, not tax advice."""
    from companion.ch21 import model
    from companion.ch21 import sources as s21
    items = s21.CAPEX
    equip = sum(v for k, v in items.items()
                if k.split()[0] in ("wind", "PV", "substation", "battery"))
    share = equip / sum(items.values())
    base = model.run()
    lines = ["equipment VAT as a cost: a sensitivity (ch 21 model, teaching)",
             f"  equipment share of the capex items: {share:.0%}",
             f"  {'case':36s} {'capex x':>8s} {'min DSCR':>9s} {'equity IRR':>11s}"]
    out = {}
    for name, k in (("exempt (TJ-52, if confirmed)", 0.0),
                    ("14 % VAT on equipment, a cost", 0.14),
                    ("half of it recovered", 0.07)):
        scale = 1 + k * share
        r = model.run(capex_scale=scale, debt=base["debt"])
        out[name] = (scale, r)
        lines.append(f"  {name:36s} {scale:8.3f} {r['min_dscr']:9.2f} {r['equity_irr']:11.1%}")
    d = out["exempt (TJ-52, if confirmed)"][1]["equity_irr"] - \
        out["14 % VAT on equipment, a cost"][1]["equity_irr"]
    lines += [f"  the exemption is worth {d:.1%} of equity IRR with the debt held:",
              "  the extra capex is paid by equity (the minimum DSCR rises a",
              "  little: more depreciation, less tax); a tax advisor confirms",
              "  the rule and its procedure before the bid (not tax advice)"]
    emit("m_vat", lines)
    return out


def meter_chain() -> dict:
    from plantp import hwmfg
    cases = [("CT 0.2S, VT 0.2, meter 0.5S", (0.2, 0.2, 0.5)),
             ("CT 0.5, VT 0.5, meter 1.0", (0.5, 0.5, 1.0)),
             ("CT 0.2S, VT 0.2, meter 0.2S", (0.2, 0.2, 0.2))]
    lines = ["metering chain: class limits combined (ch 48 helper, teaching)",
             f"  {'chain':30s} {'RSS %':>6s} {'worst %':>8s} {'RSS k u/yr':>11s}"]
    out = {}
    for name, (ct, vt, m) in cases:
        rss, worst = hwmfg.chain_error(ct, vt, m)
        money = NET_GWH * rss / 100 * 1000 * PRICE / 1000
        out[name] = (rss, worst, money)
        lines.append(f"  {name:30s} {rss:6.2f} {worst:8.2f} {money:11.0f}")
    a, b = out[cases[0][0]], out[cases[1][0]]
    lines += [f"  the class-1.0 chain allowed by the rule spans {b[0] / a[0]:.1f} times the",
              "  0.5S chain: Resolution 449 names the meter class only; the",
              "  CT and VT classes come from the network company's conditions"]
    emit("m_chain", lines)
    return out


if __name__ == "__main__":
    schedule_risk()
    vat()
    meter_chain()
    season()
    curtail()
    buyer()
    terms()
    metering()
    seismic()
    approval_cases()
    three()
    risks()
    capability()
    decisions()
    watch()
    with contextlib.redirect_stdout(io.StringIO()):
        res = run.main()
    vv = voltage()
    letters()
    sites()
    interps()
    schedule()
    ifc()
    solutions(res, vv)
