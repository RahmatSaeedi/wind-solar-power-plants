"""Chapter 53, lessons E and F: asset management and resilience (long-lead
spares, obsolescence, climate exposure, business continuity, insurance
evidence, feedback into specifications) and reliability-centred
lifecycle decisions (continue / maintain / upgrade / replace / retire,
and the value of inspecting before deciding).

Run from the project root:   python -m companion.ch53.examples_e
Writes companion/ch53/expected/e_*.txt and f_*.txt. Teaching values (A-542, A-543).
"""
from __future__ import annotations

import numpy as np

from companion.ch53 import sources as src
from companion.ch53.common import emit
from plantp import datapack


# ------------------------------------------------ E1. long-lead spares
def long_lead() -> dict:
    items = {"main transformer": (12, 0.01 * 2), "132 kV breaker": (9, 0.02),
             "turbine main bearing": (6, 0.05 * 12), "BESS PCS": (5, 0.5 * 4),
             "PV unit transformer": (8, 0.02 * 10)}           # months lead, failures a year
    rows = {k: (m, lam, 1 - np.exp(-lam * m / 12)) for k, (m, lam) in items.items()}
    lines = ["long-lead items: months to deliver and the chance a failure arrives",
             "  while one is on order (fleet rate x lead time)",
             "  item                    lead mo   failures/yr   P(another in lead)"]
    lines += [f"  {k:22s} {m:7d} {l:12.2f} {p:14.0%}" for k, (m, l, p) in rows.items()]
    lines += ["  the PCS reorders often (a fleet of 4 at 0.5 a year), the",
              "  transformer rarely - but each transformer month is half the",
              "  export (ch 52 lesson F): stock follows consequence, not count"]
    emit("e_longlead", lines)
    return rows


# ------------------------------------------------ E2. climate exposure
def climate(shift: float = 1.5, limit: float = 40.0) -> dict:
    t = datapack.load_hourly()["t_air_c"].to_numpy(float)
    now = int(np.sum(t >= limit))
    later = int(np.sum(t + shift >= limit))
    hot35 = int(np.sum(t >= 35)), int(np.sum(t + shift >= 35))
    lines = [f"hours at or above {limit:.0f} C (inverter derating, teaching) in the data year,",
             f"  and with the whole year {shift} K warmer (a teaching stress, not a forecast)",
             f"  >= {limit:.0f} C: {now} h now, {later} h warmer; >= 35 C: {hot35[0]} h now, "
             f"{hot35[1]} h warmer",
             "  the derating hours multiply while the mean barely moves:",
             "  climate exposure is read in the tail - cooling margins and",
             "  heat-work rules (ch 51) are reviewed against it"]
    emit("e_climate", lines)
    return dict(now=now, later=later, h35=hot35)


# ------------------------------------------------ E3. business continuity
def continuity() -> dict:
    steps = [("control room unusable (fire, access)", "operate from the substation panel",
              2.0), ("SCADA servers lost", "PPC fallback + local HMI", 0.5),
             ("WAN to grid operator lost", "phone instructions, logged", 0.1),
             ("key staff unavailable", "contractor on call (ch 52 skills)", 8.0)]
    lines = ["business continuity: loss, the fallback, and hours to restore operation"]
    for a, b, h in steps:
        lines += [f"  {a:38s} {h:4.1f} h", f"     -> {b}"]
    lines += ["  each fallback is exercised once a year (ch 51 drills) - an",
              "  untested fallback is a hidden failure (ch 52)"]
    emit("e_bcp", lines)
    return dict(n=len(steps))


# ------------------------------------------------ E4. insurance evidence
def insurance() -> dict:
    claims = [("gearbox failure T05", True, True, True), ("hail on 4 PV blocks", True, False, True),
              ("lightning on T09 blade", False, True, True), ("theft of cable", True, True, False)]
    names = ["maintenance record", "condition before loss", "loss quantified"]
    lines = ["insurance claims and the evidence an insurer asks for"]
    for k, *ev in claims:
        miss = [n for n, e in zip(names, ev) if not e]
        lines.append(f"  {k:24s} " + ("complete" if not miss else "missing: " + ", ".join(miss)))
    lines += ["  the evidence is the same as the warranty's (ch 52 I): a",
              "  plant that keeps its records can claim; one that does not",
              "  pays its own losses"]
    emit("e_insure", lines)
    return dict(incomplete=sum(1 for _, *e in claims if not all(e)))


# ------------------------------------------------ E5. feedback into specifications
def feedback() -> list:
    items = [("inverters", "derating at 40 C ambient with 1.5 K margin", "lesson E"),
             ("PV connectors", "100 % pull check at installation", "ch 52 D"),
             ("gearboxes", "online CMS with oil sensor, 8-week P-F", "ch 52 B"),
             ("work orders", "asset, code and test record required to close", "ch 52 I"),
             ("pitch cabinets", "temperature alarm and fan redundancy", "ch 52 s"),
             ("spares", "strategic spares by consequence, not Poisson alone", "ch 52 A")]
    lines = ["lessons fed into the specification of the next project (and of a",
             "  repowering)"]
    lines += [f"  {k:14s} {s:46s} [{src_}]" for k, s, src_ in items]
    lines += ["  a lesson is closed when the next specification carries it -",
              "  not when it is written in a report (ch 38 requirements)"]
    emit("e_feedback", lines)
    return items


# ------------------------------------------------ F1. lifecycle decision matrix
ASSETS = {   # asset: (condition 1-5 good, consequence 1-5, obsolescence 1-5 high, cost of action)
    "PV modules": (4, 3, 1, "high"), "PV inverters": (2, 3, 5, "medium"),
    "turbine gearboxes": (2, 4, 2, "high"), "turbine blades": (3, 4, 1, "medium"),
    "main transformers": (4, 5, 1, "very high"), "BESS containers": (3, 2, 3, "high"),
    "SCADA and PPC": (3, 5, 5, "low"), "33 kV switchgear": (4, 4, 2, "medium")}


def decide(cond: int, cons: int, obs: int) -> str:
    if obs >= 5 and cond <= 3:
        return "replace / upgrade"
    if cond <= 2 and cons >= 4:
        return "monitor, repair at failure (D)"
    if cond <= 2:
        return "replace at failure"
    if obs >= 4:
        return "upgrade (support ending)"
    return "continue"


def lifecycle_matrix() -> dict:
    out = {k: decide(c, q, o) for k, (c, q, o, _) in ASSETS.items()}
    lines = ["continue / maintain / upgrade / replace / retire (teaching rule)",
             "  asset              cond cons obsol  decision"]
    lines += [f"  {k:18s} {c:4d} {q:4d} {o:5d}  {out[k]}" for k, (c, q, o, _) in ASSETS.items()]
    lines += ["  SCADA and PPC: good enough today, but unsupported software in",
              "  a safety-relevant controller is a decision now (ch 36, ch 52",
              "  obsolescence); 'retire' is a plant decision, not an asset's"]
    emit("f_matrix", lines)
    return out


# ------------------------------------------------ F2. value of inspecting before deciding
def inspect_value(p_bad: float = 0.4, cost_inspect: float = 25.0) -> dict:
    # replace a blade set (cost 300) if bad; if bad and not replaced, loss 900; if good, replacing wastes 300
    replace_all = 300.0
    leave_all = p_bad * 900.0
    inspect = cost_inspect + p_bad * 300.0
    best_blind = min(replace_all, leave_all)
    lines = [f"one turbine's blades: bad with probability {p_bad:.0%} (from erosion data, ch 52)",
             f"  replace blind {replace_all:.0f} k u; leave blind {leave_all:.0f} k u expected;",
             f"  inspect first ({cost_inspect:.0f} k u) and replace only if bad: {inspect:.0f} k u",
             f"  value of the inspection: {best_blind - inspect + cost_inspect:.0f} k u against its "
             f"cost {cost_inspect:.0f}",
             "  remaining-life evidence pays when the decision would change",
             "  with it; if every outcome leads to the same choice, the",
             "  inspection is worth nothing (ch 22 value of information)"]
    emit("f_inspect", lines)
    return dict(blind=best_blind, inspect=inspect)


if __name__ == "__main__":
    long_lead()
    climate()
    continuity()
    insurance()
    feedback()
    lifecycle_matrix()
    inspect_value()
