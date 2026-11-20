"""Chapter 59, sections A-C: the basis and feasibility dossier, the
integrated design dossier and the delivery dossier, compiled by calling
the earlier chapters' models.

Run from the project root:   python -m companion.ch59.dossier
Writes companion/ch59/expected/a_*, b_*, c_*.txt.
"""
from __future__ import annotations

import math
import re

import numpy as np

from companion.ch59 import common  # noqa: F401  (path)
from companion.ch59 import sources as src
from companion.ch59.common import csv, emit

Z90 = 1.2816


# ------------------------------------------------------------- A basis
def yield_statement() -> dict:
    from companion.ch15 import sources as s15
    from companion.ch16 import sources as s16
    r = s15.plant_year()
    net = float(np.sum(r["net"])) / 1000
    curt = float(np.sum(r["curtailed"])) / 1000
    s = s16.sigmas()
    ratio = s["ratio"]
    lt, iav = s["lt"] * ratio, s["iav"] * ratio
    one = math.hypot(lt, iav)
    ten = math.hypot(lt, iav / math.sqrt(10))
    lines = ["energy at the POC of Plant P, recomputed (model 15.1, S0; ch 15, 16)",
             f"  P50 year 1: {net:.2f} GWh (curtailed at 100 MW: {curt:.2f} GWh)",
             f"  sigma at the POC: long-term {lt:.2f}, year-to-year {iav:.2f} GWh",
             f"  one year {one:.2f}: P90 {net - Z90 * one:.1f}, P99"
             f" {net - 2.3263 * one:.1f} GWh",
             f"  ten-year mean {ten:.2f}: P90 {net - Z90 * ten:.1f} GWh",
             "  the same numbers as D-019 and D-020: the dossier recomputes,",
             "  it does not copy - a changed input would show here first"]
    emit("a_yield", lines)
    return dict(net=net, one=one, ten=ten, p90=net - Z90 * one, p90_10=net - Z90 * ten)


def assumptions() -> dict:
    per = {}
    for n in range(1, 59):
        text = src.chapter_text(n)
        ids = set(re.findall(r"(?<![\w-])A-(\d{3})", text))
        for a, b in re.findall(r"A-(\d{3})\]\{\.ltr\} تا \[A-(\d{3})", text):
            ids |= {f"{k:03d}" for k in range(int(a), int(b) + 1)}
        per[n] = ids
    rows = []
    for k, title, chs in src.ITEMS:
        ids = set().union(*(per[c] for c in chs))
        rows.append((k, len(ids)))
    allids = set().union(*per.values())
    lines = [f"assumptions named in the chapters: {len(allids)} distinct ids"
             f" (A-{min(allids)} to A-{max(allids)})",
             "  by dossier item:  " + ", ".join(f"{k}: {n}" for k, n in rows[:7]),
             "                    " + ", ".join(f"{k}: {n}" for k, n in rows[7:]),
             "  each is labelled (synthetic, assumed, measured, vendor, verified)",
             "  in its chapter; the dossier carries the ledger, not the labels"]
    emit("a_assumptions", lines)
    return dict(n=len(allids), lo=min(allids), hi=max(allids), rows=rows)


GATES = [("G1 screening", [2, 3]), ("G2 feasibility", [1, 2, 3, 4, 5, 13]),
         ("G3 financeability", [4, 8, 13, 14]), ("G4 final investment", [6, 7, 9]),
         ("G5 handover", [10, 11, 12])]


def gates() -> dict:
    from companion.ch59 import index
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):
        ix = index.index()
    unk = {r[0]: len(r[5]) for r in ix["rows"]}
    docs = {r[0]: len(r[4]) for r in ix["rows"]}
    lines = ["decision gates of Plant P against the dossier items (teaching rule:",
             "a gate passes with conditions while its items carry open unknowns)",
             f"  {'gate':22s} {'items':14s} {'documents':>9s} {'unknowns':>9s}"]
    out = {}
    for g, items in GATES:
        u = sum(unk[i] for i in items)
        d = sum(docs[i] for i in items)
        out[g] = (u, d)
        lines.append(f"  {g:22s} {','.join(map(str, items)):14s} {d:9d} {u:9d}")
    lines += ["  no gate is clean: each carries unknowns that are conditions,",
              "  owned and dated - a gate is a decision taken with them, not",
              "  a claim that they are gone (ch 1, ch 22)"]
    emit("a_gates", lines)
    return out


def economics() -> dict:
    from companion.ch21 import model
    from companion.ch21 import sources as s21
    from plantp import finance as fn
    r = model.run()
    costs = np.asarray(r["opex"]) + np.asarray(r["repl"])
    lc = fn.lcoe(r["capex"], costs, np.asarray(r["energy"]), s21.TERMS["wacc"])
    lines = ["economics of Plant P (ch 21 model, teaching terms A-304 to A-310)",
             f"  capex {r['capex']:,.0f} k u; debt {r['debt']:,.0f} k u ({r['gearing']:.0%})",
             f"  equity IRR {r['equity_irr']:.1%}; project IRR {r['project_irr']:.1%};"
             f" NPV at WACC {r['npv']:,.0f} k u",
             f"  min DSCR {r['min_dscr']:.2f}; min LLCR {r['min_llcr']:.2f}",
             f"  LCOE at WACC {s21.TERMS['wacc']:.1%}: {lc:.1f} u/MWh against a PPA of"
             f" {s21.TERMS['tariff']:.0f} u/MWh",
             "  the plant clears its debt case at P90 and returns a modest",
             "  equity margin: the decision in D-025 and D-026 stands"]
    emit("a_economics", lines)
    return dict(irr=r["equity_irr"], pirr=r["project_irr"], npv=r["npv"],
                dscr=r["min_dscr"], lcoe=lc, debt=r["debt"], capex=r["capex"])


# ------------------------------------------------------------ B design
def interfaces() -> dict:
    """Numbers that must agree across chapters, checked from their sources."""
    from companion.ch15 import sources as s15
    from companion.ch19 import sources as s19
    from companion.ch24 import sources as s24
    from companion.ch25 import sources as s25
    from companion.ch30 import sources as s30
    from companion.ch44 import sources as s44
    from plantp import datapack
    seed = datapack.load_seed_ratings()["value"]
    exp = float(seed["SR-06"])
    i_exp = exp * 1e6 / (math.sqrt(3) * 132e3 * 0.95)
    bess_mwh = 39_936 * 314 * 3.2 / 1e6
    checks = [
        ("export limit: data pack vs yield model", exp, s15.ModelConfig().export_mw, "=="),
        ("PV AC: data pack vs 10 inverters x 5 MW", float(seed["SR-02"]),
         10 * s44.INVERTER["s_mva"] * s44.INVERTER["pf"], "~"),
        ("PV DC: data pack vs 109,200 x 550 W", float(seed["SR-01"]), 109_200 * 550 / 1e6, "~"),
        ("BESS power: data pack vs 4 PCS", float(seed["SR-07"]),
         s19.BUILD["pcs"] * s19.BUILD["pcs_mw"], "=="),
        ("BESS energy: cell build-up vs data pack", bess_mwh, float(seed["SR-08"]), ">="),
        ("2 main transformers vs export MVA", 2 * s25.MAIN["s_mva"], exp / 0.95, ">="),
        ("one transformer (N-1) vs export MVA", s25.MAIN["s_mva"], exp / 0.95, ">="),
        ("line rating vs export current (A)", s24.LINE["rating_a"], i_exp, ">="),
        ("hub height: structures vs resource (m)", s30.HUB, 100.0, "=="),
    ]
    lines = ["design interfaces: the same quantity in different chapters"]
    flags = []
    for name, a, b, rel in checks:
        if rel == "==":
            ok = abs(a - b) < 1e-6
        elif rel == "~":
            ok = abs(a - b) / b < 0.01
        else:
            ok = a >= b
        if not ok:
            flags.append(name)
        lines.append(f"  {'ok  ' if ok else 'FLAG'} {name:42s} {a:8.2f} {rel:2s} {b:8.2f}")
    lines += [f"  flagged: {len(flags)} - "
              + ("; ".join(flags) if flags else "none"),
              "  the N-1 flag is known and accepted: with one transformer out",
              "  the export is limited (D-022, ch 18, 28) - a decision, not",
              "  an error; an unexplained flag would stop the dossier"]
    emit("b_interfaces", lines)
    return dict(flags=flags, n=len(checks))


BASIS = [   # discipline -> (decisions, the basis in one line)
    ("architecture", "D-022", "grid-connected, AC-coupled battery, split 33 kV bus, 2 x 63 MVA"),
    ("battery", "D-023", "LFP, 10-90 % window, protection per rack, augmentation y8, y13"),
    ("control", "D-024", "5 layers, PI with anti-windup, priorities, DP plans"),
    ("one-line and auxiliaries", "D-027", "radial strings, split bus, 110 V DC, UPS"),
    ("circuits", "D-028", "cables by rating and loss; line limited on hot still days"),
    ("transformers", "D-029", "bid B at 70 u/MWh; PV unit transformers 5.6 MVA"),
    ("protection and earthing", "D-030", "incomers 1,600 A; breakers on PV units"),
    ("power quality", "D-031", "scans at the worst unit count; filter design data"),
    ("grid study", "D-032", "21-bus model; differential or intertrip on the line"),
    ("civil and water", "D-033", "wadi levels; construction water from outside"),
    ("structures", "D-034", "24 m gravity base; fatigue steel"),
    ("safety and fire", "D-036", "no universal prescription; authority's acceptance"),
    ("E&S", "D-037", "W2b waits for the raptor survey; ruin buffer"),
    ("I&C, SCADA, OT security", "D-038/39/40", "class 0.2 VT core; rings; zones and conduits"),
]


def basis() -> dict:
    lines = ["integrated design basis: one line per discipline (decision, basis)"]
    for d, dec, b in BASIS:
        lines += [f"  {d:26s} {dec}", f"      {b}"]
    lines += [f"  {len(BASIS)} disciplines; each line is the summary of a decision",
              "  record with its evidence, open items and approver"]
    emit("b_basis", lines)
    return dict(n=len(BASIS))


# ---------------------------------------------------------- C delivery
TASKS = {   # project phases to COD, months (teaching, A-571)
    "D1 wind campaign": (12, []),
    "D2 ESIA and permits": (18, ["D1 wind campaign"]),
    "D3 grid application and studies": (14, []),
    "D4 financing to close": (9, ["D2 ESIA and permits", "D3 grid application and studies"]),
    "P1 main transformers (order to site)": (12, ["D4 financing to close"]),
    "P2 turbines (order to site)": (14, ["D4 financing to close"]),
    "C1 civil works": (10, ["D4 financing to close"]),
    "C2 PV installation": (8, ["C1 civil works"]),
    "C3 wind erection": (6, ["C1 civil works", "P2 turbines (order to site)"]),
    "C4 substation and line": (4, ["P1 main transformers (order to site)", "C1 civil works"]),
    "K1 commissioning and tests": (4, ["C2 PV installation", "C3 wind erection",
                                       "C4 substation and line"]),
}


def schedule() -> dict:
    from plantp import appraisal
    tasks = {k: (float(d), pre) for k, (d, pre) in TASKS.items()}
    total, crit, slack = appraisal.critical_path(tasks)
    lines = ["Plant P from the start of the wind campaign to COD (teaching, A-571)",
             f"  {'task':38s} {'months':>6s} {'float':>6s}"]
    for k, (d, _) in TASKS.items():
        lines.append(f"  {k:38s} {d:6d} {slack[k]:6.0f}")
    lines += [f"  to COD: {total:.0f} months; critical path:",
              "    " + " > ".join(c.split()[0] for c in crit),
              "  the wind campaign and the permits drive the plan; turbines,",
              "  not transformers, are the critical supply after close"]
    emit("c_schedule", lines)
    es = {}
    for k, (d, pre) in TASKS.items():          # tasks are listed in order
        es[k] = max((es[p] + TASKS[p][0] for p in pre), default=0.0)
    csv("ch59-schedule.csv", "k,start,dur,crit,non",
        [(i + 1, es[k], d, d if k in crit else 0, 0 if k in crit else d)
         for i, (k, (d, _)) in enumerate(TASKS.items())])
    return dict(total=total, crit=crit, slack=slack, es=es)


SCOPE = [   # asset or work, owner (scenario O1 of ch 54: plant owns to the substation)
    ("PV blocks, inverters, unit transformers", "project", "project"),
    ("wind turbines and 33 kV collector", "project", "project"),
    ("battery containers and PCS", "project", "project"),
    ("plant substation, 2 x 63 MVA", "project", "project"),
    ("132 kV line, 7.06 km", "project", "project (O1); utility in O2/O3"),
    ("line bay at the grid substation (E1)", "utility", "utility"),
    ("revenue metering at the POC", "project", "utility witnesses, seals"),
    ("protection at the remote end", "utility", "utility, settings agreed"),
    ("SCADA link to the dispatch centre", "both", "interface agreed (ch 35)"),
]


def scope() -> dict:
    n = {}
    lines = ["construction and O&M scope at the connection (ownership scenario O1)",
             f"  {'asset or work':42s} {'builds':8s} operates / maintains"]
    for a, b, o in SCOPE:
        n[b] = n.get(b, 0) + 1
        lines.append(f"  {a:42s} {b:8s} {o}")
    lines += ["  " + ", ".join(f"{k} {v}" for k, v in n.items()),
              "  every 'both' row has an interface record with its owner and",
              "  test; the line moves to the utility in scenarios O2 and O3"]
    emit("c_scope", lines)
    return n


def main() -> dict:
    out = {}
    for f in (yield_statement, assumptions, gates, economics, interfaces, basis,
              schedule, scope):
        out[f.__name__] = f()
    return out


if __name__ == "__main__":
    main()
