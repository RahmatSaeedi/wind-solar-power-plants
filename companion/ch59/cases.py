"""Chapter 59, cases E-J: reliability, forecasting and services, export,
project finance, land and social safeguards, asset-information handover.
Each case calls the chapter that built its model; teaching evidence and
KPIs are labelled (A-572 to A-575).

Run from the project root:   python -m companion.ch59.cases
Writes companion/ch59/expected/e_* ... j_*.txt.
"""
from __future__ import annotations

import contextlib
import copy
import io

import numpy as np

from companion.ch59 import common  # noqa: F401  (path)
from companion.ch59.common import csv, emit


# ------------------------------------------------------- E reliability
def e_allocation() -> dict:
    from companion.ch52 import lab_f
    with contextlib.redirect_stdout(io.StringIO()):
        ex = lab_f.expected()
        s = lab_f.series()
    tot = sum(ex.values())
    year = float(s["wind"].sum() + s["pv"].sum())      # as ch 52 (energy_case)
    rows = sorted(((k, v) for k, v in ex.items() if v > 0), key=lambda kv: -kv[1])
    lines = ["energy unavailability by class (ch 52 register and model)",
             f"  {'class':34s} {'MWh/yr':>8s} {'share':>6s} {'cum.':>6s}"]
    cum = 0.0
    for k, v in rows:
        cum += v
        lines.append(f"  {k:34s} {v:8,.0f} {v / tot:6.0%} {cum / tot:6.0%}")
    top3 = sum(v for _, v in rows[:3]) / tot
    lines += [f"  total {tot:,.0f} MWh of {year / 1000:.1f} GWh: energy availability"
              f" {1 - tot / year:.2%}",
              f"  the three largest classes carry {top3:.0%}: the availability",
              "  objective is allocated to them first (turbines and their services)"]
    emit("e_alloc", lines)
    return dict(tot=tot, year=year, top3=top3, rows=rows)


STAGES_EVID = [   # (stage, unit-years of exposure, failures) for the 10 PV inverters (A-572)
    ("factory burn-in", 0.3, 0), ("commissioning", 2.5, 1),
    ("operating year 1", 10.0, 7), ("operating year 2", 10.0, 6),
]


# [start: bayes]
def gamma_update(alpha: float, beta: float, failures: int, exposure: float):
    """Gamma prior on a failure rate (alpha failures in beta unit-years)
    updated with Poisson evidence: (alpha + failures, beta + exposure)."""
    return alpha + failures, beta + exposure
# [end: bayes]


def e_bayes() -> dict:
    from companion.ch52 import lab_f
    from companion.ch52 import sources as s52
    from scipy.stats import gamma
    rate0 = s52.CLASSES["PV inverter"][1]
    a, b = 2.0, 2.0 / rate0                       # prior: mean 0.5, worth 4 unit-years
    lines = ["PV inverter failure rate updated stage by stage (gamma-Poisson;",
             f"prior mean {rate0:.2f}/unit-yr from ch 18, worth {b:.0f} unit-years)",
             f"  {'stage':20s} {'exp.':>5s} {'fail':>5s} {'mean':>6s} {'90 % interval':>16s}"]
    out = []
    lines.append(f"  {'prior':20s} {'':5s} {'':5s} {a / b:6.2f} "
                 f"{gamma.ppf(0.05, a, scale=1 / b):7.2f}-{gamma.ppf(0.95, a, scale=1 / b):.2f}")
    for st, expo, f in STAGES_EVID:
        a, b = gamma_update(a, b, f, expo)
        lo, hi = gamma.ppf(0.05, a, scale=1 / b), gamma.ppf(0.95, a, scale=1 / b)
        out.append((st, a / b))
        lines.append(f"  {st:20s} {expo:5.1f} {f:5d} {a / b:6.2f} {lo:7.2f}-{hi:.2f}")
    cls = copy.deepcopy(s52.CLASSES)
    t = list(cls["PV inverter"])
    t[1] = a / b
    cls["PV inverter"] = tuple(t)
    with contextlib.redirect_stdout(io.StringIO()):
        e0 = lab_f.expected()["PV inverter"]
        e1 = lab_f.expected(cls)["PV inverter"]
    lines += [f"  posterior mean {a / b:.2f} against the prior {rate0:.2f}: inverter energy lost",
              f"  {e0:,.0f} -> {e1:,.0f} MWh/yr; the model's rate is replaced by the",
              "  evidence once the exposure outweighs the prior (ch 37, 52)"]
    emit("e_bayes", lines)
    return dict(post=a / b, prior=rate0, e0=e0, e1=e1, out=out)


# ---------------------------------------------- F forecasting, services
def f_forecast() -> dict:
    from companion.ch15 import forecast as fc
    w_, pv, *_ = fc.truth()
    act = w_ + pv
    lines = ["forecast validation, reproducible (ch 15 synthetic archive, fixed seeds)",
             f"  {'lead h':>6s} {'RMSE % of 110 MW':>17s} {'bias MW':>8s}"]
    out = {}
    for lead in (1, 6, 24, 36):
        wf, pf = fc.nwp(lead)
        e = act - (wf + pf)
        rmse = float(np.sqrt(np.mean(e ** 2))) / fc.CAP
        out[lead] = (rmse, float(e.mean()))
        lines.append(f"  {lead:6d} {rmse:17.1%} {e.mean():8.2f}")
    wf, pf = fc.nwp(24)
    e = act - (wf + pf)
    half = 8760 // 2
    q10, q90 = np.percentile(e[:half], [10, 90])
    cov = float(np.mean((e[half:] >= q10) & (e[half:] <= q90)))
    short = -np.clip(e[half:] - q10, None, 0)        # below the P10 band
    over20 = float(np.mean(-e[half:] > 20.0))
    lines += [f"  day-ahead band P10-P90 learned on Jan-Jun: [{q10:.1f}, {q90:.1f}] MW",
              f"  coverage on Jul-Dec: {cov:.0%} (target 80 %)",
              f"  hours the plant falls more than 20 MW short of its forecast: {over20:.1%}",
              "  - the battery's 20 MW covers the rest; a reserve offer is sized",
              "  on that tail, not on the RMSE"]
    emit("f_forecast", lines)
    return dict(out=out, cov=cov, q10=q10, q90=q90, over20=over20)


SEPARATION = [   # (claim, what proves it, status for Plant P)
    ("forecast skill", "archived forecasts scored by horizon (ch 15, 37)", "shown"),
    ("technical capability", "model and plant tests of the PPC and battery (ch 20, 50)",
     "partly shown"),
    ("contractual qualification", "the operator's prequalification test (ch 20, 51)",
     "not offered"),
    ("delivered performance", "settlement data, activations met (ch 51)", "none yet"),
]


def f_separation() -> dict:
    lines = ["four claims a service offer must keep apart (ch 59 F)"]
    for c, p, st in SEPARATION:
        lines += [f"  {c:28s} {st}", f"      proof: {p}"]
    lines += ["  a good forecast is not a qualified service; a capable plant",
              "  is not a delivered one - the base case books no service revenue"]
    emit("f_separation", lines)
    return dict(n=len(SEPARATION))


# ------------------------------------------------------------ G export
def g_export() -> dict:
    from companion.ch18 import examples_f
    from companion.ch21 import sources as s21
    from plantp import finance as fn
    price, wacc, years = s21.TERMS["tariff"], s21.TERMS["wacc"], 25
    lines = ["export options over the plant life (ch 18 options; 70 u/MWh, WACC 7.5 %,",
             "25 years; energy priced at the PPA, teaching)",
             f"  {'option':30s} {'capex':>6s} {'loss+out':>9s} {'PV energy':>10s} {'total':>7s}"]
    out = {}
    for name in ("overhead line, single circuit", "overhead line, double circuit",
                 "underground cable"):
        with contextlib.redirect_stdout(io.StringIO()):
            e = examples_f.export_option(name)
        mwh = e["loss"] + e["out"]
        pv_e = fn.pv(np.full(years, mwh * price / 1e6), wacc)    # M u
        tot = e["cost"] + pv_e
        out[name] = (e["cost"], mwh, pv_e, tot)
        lines.append(f"  {name:30s} {e['cost']:6.2f} {mwh:9,.0f} {pv_e:10.2f} {tot:7.2f}")
    best = min(out.items(), key=lambda kv: kv[1][3])[0]
    lines += [f"  lowest life cost: {best} (M u)",
              "  the cable's long repairs and the double circuit's capital are",
              "  priced in one number; route, permits and ownership still decide"]
    emit("g_export", lines)
    return dict(out=out, best=best)


# ----------------------------------------------------------- H finance
def h_finance() -> dict:
    from companion.ch21 import model
    from plantp import finance as fn
    b = model.run()
    cases = [("base", {}), ("P90 one-year energy", {"energy_scale": 275.9 / 295.14}),
             ("capex +10 %", {"capex_scale": 1.10}), ("one year late", {"delay_years": 1}),
             ("price -10 %", {"price_scale": 0.9}),
             ("P90 + capex +10 %", {"energy_scale": 275.9 / 295.14, "capex_scale": 1.10})]
    lines = ["finance cases (ch 21 model, debt held at the base size)",
             f"  {'case':22s} {'min DSCR':>9s} {'LLCR':>6s} {'equity IRR':>11s}"]
    out = {}
    for k, ch in cases:
        r = model.run(debt=b["debt"], **ch)
        out[k] = r
        lines.append(f"  {k:22s} {r['min_dscr']:9.2f} {r['min_llcr']:6.2f} {r['equity_irr']:11.1%}")
    be = fn.breakeven(lambda t: model.run(tariff=t, debt=b["debt"])["min_dscr"], 50.0, 90.0, 1.05)
    be_npv = fn.breakeven(lambda t: model.run(tariff=t)["npv"], 50.0, 90.0, 0.0)
    low = min(out.items(), key=lambda kv: kv[1]["min_dscr"])
    lines += [f"  break-even tariff for min DSCR 1.05 (default): {be:.1f} u/MWh",
              f"  break-even tariff for NPV 0 at WACC: {be_npv:.1f} u/MWh",
              f"  lowest case: {low[0]}, min DSCR {low[1]['min_dscr']:.2f}"
              f" ({low[1]['min_dscr'] - 1.05:+.2f} against the default);",
              "  financeable at teaching terms, with the tariff as the thin margin"]
    emit("h_finance", lines)
    return dict(out={k: (r["min_dscr"], r["equity_irr"]) for k, r in out.items()},
                be=be, be_npv=be_npv)


ALLOC = [   # risk, carried by, instrument (teaching, ch 21, 39, 54)
    ("energy below P50", "owner", "sizing on P90; DSRA"),
    ("construction cost overrun", "EPC contractor", "fixed price; LDs; security"),
    ("late completion", "EPC contractor", "delay LDs capped; insurance"),
    ("equipment defects", "suppliers", "warranties; performance guarantees"),
    ("grid curtailment", "buyer above a threshold", "PPA clause (country)"),
    ("buyer late payment", "owner, then buyer", "payment security; DSRA"),
    ("change in law", "shared", "PPA change-in-law clause"),
    ("currency", "depends on the PPA", "indexation; hedge (country)"),
]


def h_alloc() -> dict:
    lines = ["contract-risk allocation of Plant P (teaching)"]
    for r, who, how in ALLOC:
        lines += [f"  {r:28s} {who}", f"      {how}"]
    lines += [f"  {len(ALLOC)} risks; each row is checked against the signed contracts",
              "  by counsel - this table is a design for them, not advice"]
    emit("h_alloc", lines)
    return dict(n=len(ALLOC))


# ------------------------------------------------------------ I social
KPIS = [   # name, value, target, tolerance, higher is better (teaching, A-574)
    ("local hiring, share of workforce %", 33.0, 40.0, 5.0, True),
    ("grievances closed within 30 days %", 82.0, 90.0, 10.0, True),
    ("raptor fatalities a year (estimate)", 4.8, 3.0, 2.0, False),
    ("construction water, % of recharge", 112.0, 100.0, 10.0, False),
    ("night noise exceedances at dwellings", 0.0, 0.0, 1.0, False),
    ("women in consultation meetings %", 18.0, 30.0, 10.0, True),
    ("land users with signed agreements %", 96.0, 100.0, 5.0, True),
    ("chance finds reported on time %", 100.0, 100.0, 5.0, True),
]


def i_kpis() -> dict:
    from plantp import envsocial as es
    lines = ["E&S monitoring dashboard of Plant P (teaching values from ch 33, 49)",
             f"  {'indicator':40s} {'value':>7s} {'target':>7s}  status"]
    n = {}
    for k, v, t, tol, hib in KPIS:
        s = es.kpi_rag(v, t, tol, hib)
        n[s] = n.get(s, 0) + 1
        lines.append(f"  {k:40s} {v:7.1f} {t:7.1f}  {s}")
    lines += ["  " + ", ".join(f"{k} {v}" for k, v in sorted(n.items())),
              "  each red line has a corrective action with an owner and a",
              "  date, reported to the lenders and in the grievance register"]
    emit("i_kpis", lines)
    return n


# ---------------------------------------------------------- J handover
REG = [   # asset register rows to import into the CMMS (teaching, planted faults)
    dict(tag="=PVF1-1-T1", floc="PVF1-1", serial="TR-1101", test="FAT-0401", vendor="V-U-A"),
    dict(tag="=PVF1-1-INV1", floc="PVF1-1", serial="INV-0007", test="FAT-0412", vendor="V-PCI"),
    dict(tag="=PVF1-2-INV1", floc="PVF1-2", serial="", test="FAT-0413", vendor="V-PCI"),
    dict(tag="=WS1-T01", floc="WS1", serial="WT-0001", test="SAT-0101", vendor="V-WT"),
    dict(tag="=WS1-T02", floc="WS1", serial="WT-0002", test="SAT-0102", vendor="V-WT"),
    dict(tag="=WS1-T02", floc="WS1", serial="WT-0003", test="SAT-0103", vendor="V-WT"),
    dict(tag="=SUB-T1", floc="SUB", serial="MT-0001", test="FAT-0001", vendor="V-MT"),
    dict(tag="=SUB-T2", floc="SUB", serial="MT-0002", test="FAT-0099", vendor="V-MT"),
    dict(tag="=BESS-A", floc="BESS", serial="BC-0001", test="SAT-0201", vendor="V-BESS"),
    dict(tag="=PPC", floc="CTL", serial="PPC-01", test="SAT-0301", vendor="V-CTL"),
]
TESTS = {"FAT-0401", "FAT-0412", "FAT-0413", "SAT-0101", "SAT-0102", "SAT-0103",
         "FAT-0001", "FAT-0002", "SAT-0201", "SAT-0301"}
FLOCS = {"PVF1-1", "PVF1-2", "WS1", "SUB", "BESS", "CTL"}


def j_handover() -> dict:
    from plantp import commissioning as cm
    v = cm.validate(REG, ("tag", "floc", "serial", "test", "vendor"), "tag",
                    {"test": TESTS, "floc": FLOCS})
    n = sum(len(x) for x in v.values())
    lines = [f"asset register checked before the CMMS import ({len(REG)} rows, teaching)"]
    for k in ("missing", "duplicate", "dangling"):
        lines += [f"  {k}: {len(v[k])}"] + [f"    {a}: {b}" for a, b in v[k]]
    lines += [f"  {n} problems: the import waits until each is fixed at its",
              "  source record, not in the CMMS (ch 38, ch 50)"]
    emit("j_handover", lines)
    return dict(v={k: len(x) for k, x in v.items()}, n=n)


CHANGE = [   # records touched when inverter INV1 of PVF1-1 is replaced (ch 52)
    "work order with cause and parts", "asset register: serial, date",
    "configuration: firmware and settings checksum", "warranty claim of the old unit",
    "spares stock and reorder", "test record of the new unit (site test)",
    "SCADA point list (unchanged tags, new device id)", "as-built drawing (no change)",
]


def j_change() -> dict:
    lines = ["one repair, the records it touches (replacing inverter =PVF1-1-INV1)"]
    lines += [f"  {i:2d} {r}" for i, r in enumerate(CHANGE, 1)]
    lines += [f"  {len(CHANGE)} records; a repair closed with fewer leaves the register",
              "  describing a machine that is no longer there"]
    emit("j_change", lines)
    return dict(n=len(CHANGE))


def main() -> dict:
    out = {}
    for f in (e_allocation, e_bayes, f_forecast, f_separation, g_export, h_finance,
              h_alloc, i_kpis, j_handover, j_change):
        out[f.__name__] = f()
    return out


if __name__ == "__main__":
    main()
