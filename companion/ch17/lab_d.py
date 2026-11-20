"""Chapter 17, lab D - the requirements lab: the chapter's worked example
(peak demand and annual energy from hourly data, then the grid
information request list) and a requirements register with verified,
assumed and open entries.

Run from the project root:   python -m companion.ch17.lab_d
Writes companion/ch17/expected/d_*.txt.
Synthetic loads A-284, network teaching values A-285.
"""
from __future__ import annotations

from collections import Counter

import numpy as np

from companion.ch17 import sources as src
from companion.ch17.common import emit
from plantp import demand as dm


def worked() -> None:
    p = src.regional()["total"]
    hour, dow, month, _ = src.calendar()
    ok = np.isfinite(p).all() and len(p) == 8760
    m = dm.metrics(p)
    k = m["peak_at"]
    q = src.regional_15min()
    lines = ["worked example: the regional load from hourly data",
             f"  1 data check: {len(p)} values, gaps {int((~np.isfinite(p)).sum())},"
             f" negative {int((p < 0).sum())}: {'usable' if ok else 'not usable'}",
             f"  2 annual energy: sum of hourly MW x 1 h = {m['energy']:,.0f} MWh"
             f" ({m['energy'] / 1e3:.1f} GWh)",
             f"  3 peak: {m['peak']:.2f} MW, day {k // 24 + 1}, {hour[k]:02d}:00"
             f" (month {month[k] + 1}, {'weekday' if dow[k] < 5 else 'weekend'})",
             f"  4 load factor: {m['mean']:.2f} / {m['peak']:.2f} = {m['load_factor']:.3f}",
             f"  5 resolution: 15-minute peak {q.max():.2f} MW"
             f" (+{100 * (q.max() / m['peak'] - 1):.1f} %)",
             f"  6 minimum {m['min']:.2f} MW: the plant's 100 MW export flows up",
             "    whenever it exceeds the local load",
             "  7 what the analysis cannot tell, and must be asked (request list):",
             "    the measured load, its resolution and quality; transformer and",
             "    line ratings; the outage cases the operator plans for; the",
             "    short-circuit power; other generators and planned loads"]
    emit("d_worked", lines)


# [start: register]
def register() -> list:
    R = dm.Requirement
    return [
        R("REQ-001", "export at the POC up to the agreed capacity",
          "metered export <= 100 MW (15-min mean)", "connection offer",
          "assumed", "must", ["D-002"]),
        R("REQ-002", "deliver the P50 yield statement",
          "net energy 295 GWh/yr P50 at the POC (model 15.1)", "owner",
          "verified", "must", ["D-019", "D-020"]),
        R("REQ-003", "reactive power capability at the POC",
          "pf 0.95 lead/lag at full export, test per grid code", "grid code",
          "open", "must", ["U-059"]),
        R("REQ-004", "voltage at the POC within the operator's window",
          "window from the operator; rise < 1.1 % at 100 MW", "grid operator",
          "open", "must", ["U-057"]),
        R("REQ-005", "ride through grid faults",
          "profile from the grid code; type test + plant study", "grid code",
          "open", "must", []),
        R("REQ-006", "keep critical loads on loss of grid",
          "200 kW for 24 h from battery or back-up", "owner",
          "assumed", "should", ["A-284"]),
        R("REQ-007", "limit export when the operator orders",
          "set-point followed within 60 s, logged", "grid operator",
          "assumed", "must", []),
        R("REQ-008", "meter export and import separately",
          "revenue meters, class per contract, both directions", "PPA",
          "assumed", "must", []),
        R("REQ-009", "provide a day-ahead forecast",
          "hourly forecast by 12:00 day before; skill vs persistence", "PPA",
          "open", "should", ["U-056"]),
        R("REQ-010", "plant is easy to keep running",
          "", "operator (O&M)", "open", "could", []),
        R("REQ-011", "water use for cleaning within the permit",
          "<= permitted m3/yr, metered monthly", "permit",
          "open", "must", ["U-053"]),
        R("REQ-012", "noise at the nearest camp",
          "<= limit from the permit at the receptor, survey", "permit",
          "open", "must", ["U-051"]),
    ]
# [end: register]


def register_report() -> None:
    reg = register()
    st = Counter(r.status for r in reg)
    pr = Counter(r.priority for r in reg)
    not_meas = [r.rid for r in reg if not r.is_measurable()]
    no_link = [r.rid for r in reg if not r.links]
    lines = [f"requirements register (PLP-PRJ-REG-0007, draft): {len(reg)} entries",
             f"  status: verified {st['verified']}, assumed {st['assumed']}, open {st['open']}",
             f"  priority: must {pr['must']}, should {pr['should']}, could {pr['could']}",
             f"  without a measurable criterion: {', '.join(not_meas) or 'none'}",
             f"  without a link to a decision, assumption or unknown: {', '.join(no_link)}",
             "  the crude check (a number in the measure) flags four: three",
             "  are measurable by reference (the number lives in the grid",
             "  code, the contract or the permit, which must be named);",
             "  REQ-010 is a wish, not a requirement, until it names a",
             "  measure (availability, mean time to repair); unlinked entries",
             "  need a source document before the baseline is frozen"]
    emit("d_register", lines)


def request_list() -> None:
    items = [
        ("load at the grid substation, 15-min, 3 years", "peaks, minimum, growth", "operator"),
        ("transformer and line ratings, normal and N-1", "thermal checks", "operator"),
        ("short-circuit power, max and min, at the POC", "equipment duty, SCR", "operator"),
        ("network model or equivalent at the POC", "voltage and stability", "operator"),
        ("voltage window and reactive requirement", "REQ-003, REQ-004", "operator/code"),
        ("fault ride-through and protection settings", "REQ-005, chapter 27", "operator/code"),
        ("other generators and queued projects nearby", "hosting, curtailment", "operator"),
        ("planned reinforcements and their dates", "export limits over time", "operator"),
        ("outage statistics of the line and substation", "ch 15 outage hours", "operator"),
        ("metering, telemetry and dispatch interfaces", "REQ-007, REQ-008", "operator/buyer"),
        ("connection costs and who pays which works", "boundary, chapter 21", "operator"),
        ("connection application steps and deadlines", "schedule, chapter 38", "operator"),
    ]
    lines = ["grid information request list (PLP-ELE-LST-0003, draft):",
             "  no  item                                          why"]
    for i, (item, why, who) in enumerate(items, 1):
        lines.append(f"  {i:2d}  {item:46s}{why}")
    shared = sum(1 for _, _, w in items if "/" in w)
    lines += [f"  {len(items)} items, all to the grid operator ({shared} also via the code",
              "  or the buyer); each answer closes an open requirement or unknown"]
    emit("d_request", lines)


if __name__ == "__main__":
    worked()
    register_report()
    request_list()
