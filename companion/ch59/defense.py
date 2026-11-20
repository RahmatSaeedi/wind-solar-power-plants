"""Chapter 59, section D: the defense table and four change cases
recomputed through the yield model (ch 15) and the finance model (ch 21).

Run from the project root:   python -m companion.ch59.defense
Writes companion/ch59/expected/d_*.txt.
"""
from __future__ import annotations

from dataclasses import replace

import numpy as np

from companion.ch59 import common  # noqa: F401  (path)
from companion.ch59.common import csv, emit


def _net(cfg) -> float:
    from companion.ch15 import sources as s15
    return float(np.sum(s15.plant_year(cfg)["net"])) / 1000


# [start: cases]
def cases() -> dict:
    """Four changes to the basis: resource, export limit, capex, battery."""
    from companion.ch15 import sources as s15
    from companion.ch21 import model
    base_cfg = s15.ModelConfig()
    e0 = _net(base_cfg)
    b = model.run()
    runs = {
        "base": (e0, b),
        "wind resource -10 %": None,
        "export limit 80 MW": None,
        "capex +15 %": (e0, model.run(capex_scale=1.15, debt=b["debt"])),
        "no battery (S0)": (e0, model.run(battery=False)),
    }
    e1 = _net(replace(base_cfg, lt_wind=base_cfg.lt_wind * 0.9))
    runs["wind resource -10 %"] = (e1, model.run(energy_scale=e1 / e0,
                                                 debt=b["debt"]))
    e2 = _net(replace(base_cfg, export_mw=80.0))
    runs["export limit 80 MW"] = (e2, model.run(energy_scale=e2 / e0,
                                                debt=b["debt"]))
    return runs
# [end: cases]


def change() -> dict:
    runs = cases()
    lines = ["four changes to the basis, recomputed (ch 15 yield, ch 21 finance;",
             "debt held at the size of the base case except for 'no battery')",
             f"  {'case':22s} {'GWh':>7s} {'min DSCR':>9s} {'equity IRR':>11s}"
             f" {'NPV k u':>9s}"]
    for k, (e, r) in runs.items():
        lines.append(f"  {k:22s} {e:7.1f} {r['min_dscr']:9.2f} {r['equity_irr']:11.1%}"
                     f" {r['npv']:9,.0f}")
    csv("ch59-cases.csv", "k,dscr,irr",      # no text column: '%' is a TeX comment
        [(i + 1, round(r["min_dscr"], 3), round(100 * r["equity_irr"], 2))
         for i, (k, (e, r)) in enumerate(runs.items())])
    worst = min(runs.items(), key=lambda kv: kv[1][1]["min_dscr"])
    w = worst[1][1]["min_dscr"]
    where = ("below the 1.05 default covenant" if w < 1.05 else
             "below the 1.10 lock-up" if w < 1.10 else
             "above the 1.10 lock-up, below the 1.20 sizing target" if w < 1.20 else
             "at or above the 1.20 sizing target")
    lines += [f"  lowest minimum DSCR: {worst[0]}, {w:.2f} - {where}",
              "  (ch 21 terms); each case names the decision it reopens and",
              "  the evidence that would close it"]
    emit("d_change", lines)
    return {k: (e, r["min_dscr"], r["equity_irr"], r["npv"]) for k, (e, r) in runs.items()}


DEFENSE = [   # decision, claim, evidence (chapter), uncertainty, approver, if disproven
    ("D-017", "wind P50 191.9 GWh at 100 m hub", "mast + lidar + MCP (ch 13)",
     "sigma 7.6 GWh long-term", "lenders' engineer", "re-size debt; layout W1?"),
    ("D-019", "P50 295.1 GWh at the POC", "model 15.1 (ch 15)", "P90 1y 275.9",
     "owner, lenders' engineer", "finance cases (ch 21)"),
    ("D-022", "AC-coupled, 2 x 63 MVA, single line", "options matrix (ch 18)",
     "N-1 export limit", "owner", "second circuit or third unit"),
    ("D-023", "LFP 20 MW / 40 MWh, optional", "dispatch and fade (ch 19)",
     "repays ~40 % of capital", "owner", "S0 with space kept"),
    ("D-029", "bid B transformers", "loss evaluation (ch 25)", "loss prices",
     "owner", "re-run evaluation"),
    ("D-030", "protection and earthing basis", "coordination by fault case (ch 26)",
     "soil survey U-098", "licensed engineer", "new grid, new settings"),
    ("D-032", "grid-study basis", "21-bus model (ch 28)", "grid data U-102",
     "network operator", "re-study; compensator"),
    ("D-036", "safety, fire, emergency basis", "registers (ch 32)", "authority U-110",
     "authority having jurisdiction", "revise layout and systems"),
    ("D-037", "E&S basis, W2b waits for survey", "registers (ch 33)",
     "raptor survey U-113", "regulator, lenders", "micro-siting or W1"),
    ("D-056", "maintenance and RAM basis", "RAM model (ch 52)", "rates A-288",
     "owner, O&M contractor", "spares and contracts"),
]


def defense() -> dict:
    lines = ["the defense table: each major decision with its evidence (ch 59 D)"]
    for d, claim, ev, unc, appr, alt in DEFENSE:
        lines += [f"  {d} {claim}",
                  f"      evidence: {ev}; uncertainty: {unc}",
                  f"      approver: {appr}; if disproven: {alt}"]
    lines += [f"  {len(DEFENSE)} decisions defended; every row names who must approve",
              "  and what the design becomes if the claim fails"]
    emit("d_defense", lines)
    return dict(n=len(DEFENSE))


TORNADO = [   # (input, low case, high case) as ch 21 model keywords (teaching ranges, A-573)
    ("energy +/- 5 %", {"energy_scale": 0.95}, {"energy_scale": 1.05}),
    ("PPA price +/- 10 %", {"price_scale": 0.90}, {"price_scale": 1.10}),
    ("capex +/- 10 %", {"capex_scale": 1.10}, {"capex_scale": 0.90}),
    ("opex +/- 20 %", {"opex_scale": 1.20}, {"opex_scale": 0.80}),
    ("interest +/- 1 point", {"rate": 0.07}, {"rate": 0.05}),
    ("curtailment 0 / +3 %", {"curtail_extra": 0.03}, {"curtail_extra": 0.0}),
    ("COD one year late / on time", {"delay_years": 1}, {}),
]


def tornado() -> dict:
    from companion.ch21 import model
    b = model.run()
    base = b["equity_irr"]
    rows = []
    for name, lo, hi in TORNADO:
        r_lo = model.run(debt=b["debt"], **lo)
        r_hi = model.run(debt=b["debt"], **hi)
        rows.append((name, r_lo["equity_irr"] - base, r_hi["equity_irr"] - base,
                     r_lo["min_dscr"], r_hi["min_dscr"]))
    csv("ch59-tornado.csv", "k,lo,hi",       # fixed TORNADO order: the figure labels follow it
        [(i + 1, round(100 * r[1], 2), round(100 * r[2], 2)) for i, r in enumerate(rows)])
    rows.sort(key=lambda r: -(abs(r[1]) + abs(r[2])))
    lines = [f"one input at a time around the base (equity IRR {base:.1%}; debt held)",
             f"  {'input':28s} {'low IRR':>8s} {'high IRR':>9s} {'low DSCR':>9s} {'high DSCR':>10s}"]
    for name, dl, dh, sl, sh in rows:
        lines.append(f"  {name:28s} {dl:+8.1%} {dh:+9.1%} {sl:9.2f} {sh:10.2f}")
    lines += [f"  widest: {rows[0][0]}, then {rows[1][0]}, then {rows[2][0]};",
              "  the first two are fixed by contracts (EPC price, PPA), the",
              "  third by the resource evidence (ch 13, 16)"]
    emit("d_tornado", lines)
    return dict(rows=rows, base=base)


def main() -> dict:
    return dict(change=change(), defense=defense(), tornado=tornado())


if __name__ == "__main__":
    main()
