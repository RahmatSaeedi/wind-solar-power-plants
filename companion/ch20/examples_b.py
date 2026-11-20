"""Chapter 20, section B - constraints and algorithms: curtailment under
operator caps shared between wind and PV by three rules, ramp-rate
smoothing of a broken-cloud minute day with the battery, the plant's
P-Q capability envelope at the POC against a teaching requirement, and
the power a battery can hold for a service at each SOC.

Run from the project root:   python -m companion.ch20.examples_b
Writes companion/ch20/expected/b_*.txt and diagrams/data/ch20-*.csv.
Teaching values A-299 and A-302.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch12 import sources as s12
from companion.ch15 import sources as s15
from companion.ch20 import sources as src
from companion.ch20.common import csv, emit
from plantp import control as ct

L = src.LIMITS


def caps() -> np.ndarray:
    """Operator caps (teaching, A-302): 80 MW on 40 sunny days from
    11:00 to 15:00, 100 MW otherwise."""
    rng = np.random.default_rng(2001)
    cap = np.full(8760, L["export_mw"])
    pv = s15.plant_year()["pv_av"].reshape(365, 24)
    sunny = np.argsort(pv[:, 11:15].sum(axis=1))[-120:]
    days = rng.choice(sunny, 40, replace=False)
    for d in days:
        cap[d * 24 + 11:d * 24 + 15] = 80.0
    return cap


def allocation() -> None:
    r = s15.plant_year()
    w, pv, poc = r["w_av"], r["pv_av"], r["poc"]
    cap = caps()
    cut = np.clip(poc - cap, 0, None)
    share_w = np.where(w + pv > 0, w / np.maximum(w + pv, 1e-9), 0)
    rules = {"pro rata by output": (cut * share_w, cut * (1 - share_w)),
             "PV first": (np.clip(cut - pv, 0, None), np.minimum(cut, pv)),
             "wind first": (np.minimum(cut, w), np.clip(cut - w, 0, None))}
    lines = ["curtailment with operator caps (80 MW on 40 days, 11-15 h, A-302):",
             f"  total curtailed {cut.sum():,.0f} MWh in {int((cut > 0).sum())} hours",
             "  rule                  wind MWh    PV MWh"]
    for k, (cw, cp) in rules.items():
        lines.append(f"  {k:20s} {cw.sum():9,.0f}  {cp.sum():8,.0f}")
    lines += ["  the plant loses the same energy under every rule; who loses",
              "  it matters when wind and PV have different owners, prices or",
              "  certificates: the rule is a contract term, and the plant",
              "  controller only carries it out (chapter 15 allocation)"]
    emit("b_allocation", lines)


def ramp() -> None:
    """Broken-cloud minute day scaled to 50 MW of PV; export ramps held
    to a limit with the battery (teaching)."""
    g = s12.minute_days()["broken"]["true"]
    pv = np.clip(50.0 * g / 1000.0 * 0.9, 0, 50.0)
    lines = ["ramp-rate limit on a broken-cloud day (50 MW PV, minute data):",
             f"  largest PV change in a minute {np.abs(np.diff(pv)).max():.1f} MW",
             "  limit MW/min   battery power MW   battery energy MWh"]
    rows = []
    for lim in (10.0, 5.0, 2.0):
        out = ct.rate_limit(pv, lim)
        gap = out - pv                                      # + battery gives
        e = np.cumsum(gap) / 60.0
        lines.append(f"  {lim:12.0f}   {np.abs(gap).max():16.1f}   {e.max() - e.min():18.2f}")
        if lim == 5.0:
            rows = [(k, f"{pv[k]:.2f}", f"{out[k]:.2f}") for k in range(600, 960)]
    lines += ["  a tighter ramp limit needs a little energy but a lot of",
              "  power: the battery that smooths ramps is power-sized; a",
              "  ramp limit is applied only if the grid rules ask for it"]
    emit("b_ramp", lines)
    csv("ch20-ramp.csv", "m,pv,out", rows)


def envelope() -> None:
    """Q the units can give at each plant P, less what transformers and
    the line use, against pf 0.95 at the POC (teaching, A-302). Wind and
    PV units are capped at 0.33 of rating; an idle battery inverter can
    give its whole rating as Mvar (chapter 18)."""
    rows = []
    lines = ["P-Q envelope at the POC (losses as chapter 18; A-302):",
             "  P MW   losses Mvar   at POC without battery   with battery   asked"]
    for p in (0, 20, 40, 60, 80, 100, 110):
        frac = p / 110.0
        q_re = (12 * float(ct.q_limit(frac * 5.0, 5.6, 0.33))
                + 10 * float(ct.q_limit(frac * 5.0, 5.5, 0.33)))
        q_bess = 4 * float(ct.q_limit(0.0, 5.5, 1.0))
        s_ = p / 0.95
        loss = (0.12 * s_ ** 2 / 126 + (s_ / 132) ** 2 * 2.82 - 0.35
                + 0.06 * (s_ * 60 / 110) ** 2 / 67.2 + 0.06 * (s_ * 50 / 110) ** 2 / 55)
        asked = p * math.tan(math.acos(0.95))
        lines.append(f"  {p:4.0f}   {loss:11.1f}   {q_re - loss:22.1f}   {q_re + q_bess - loss:12.1f}"
                     f"   {asked:5.1f}")
        rows.append((p, f"{q_re - loss:.2f}", f"{q_re + q_bess - loss:.2f}", f"{asked:.2f}"))
    lines += ["  without the battery the plant falls short of the teaching",
              "  requirement above about 85 MW; with idle battery inverters it",
              "  meets it at every output, but only while the battery is not",
              "  also giving full active power; the controller must know this",
              "  envelope to refuse a set point it cannot reach (chapter 18)"]
    emit("b_envelope", lines)
    csv("ch20-pq.csv", "p,qre,qall,asked", rows)


def soc_rooms() -> None:
    lines = ["power the S1 battery can hold for a service, by stored energy:",
             "  stored MWh   up 1 h   down 1 h   up 15 min   down 15 min"]
    for e in (4, 10, 20, 30, 36):
        u1, d1 = ct.soc_room(e, L["e_min"], L["e_max"], L["eta"], 1.0)
        u4, d4 = ct.soc_room(e, L["e_min"], L["e_max"], L["eta"], 0.25)
        lines.append(f"  {e:10d}   {min(u1, 20):6.1f}   {min(d1, 20):8.1f}"
                     f"   {min(u4, 20):9.1f}   {min(d4, 20):11.1f}")
    lines += ["  (capped at the 20 MW converter)",
              "  a full battery cannot hold downward reserve, an empty one",
              "  cannot hold upward; a service sets a band for the SOC, not",
              "  just a power; shorter services need less energy"]
    emit("b_rooms", lines)


def delta_cost() -> None:
    """Upward reserve of 5 MW, 18-22 h, held by running the renewables
    below their available power (delta control) instead of the battery."""
    r = s15.plant_year()
    poc = np.clip(r["poc"], 0, None)
    price = src.prices()
    cap = caps()
    hours = np.array([(t % 24) in range(18, 22) for t in range(8760)])
    avail = np.minimum(poc, cap)
    can = avail >= 5.0
    lost = np.where(hours & can, 5.0, np.where(hours, avail, 0.0))
    held = (hours & can).sum() / hours.sum() * 100
    cost = float((lost * price).sum())
    lines = ["5 MW of upward reserve 18-22 h held by the renewables (delta):",
             f"  window hours with at least 5 MW to hold back: {held:.1f} %",
             f"  energy not sold {lost.sum():,.0f} MWh, worth {cost / 1000:,.0f} k u",
             "  the plant could hold it in too few hours for REQ-S01 (95 %)",
             "  and the battery held the same reserve for about 58 k u (lab E):",
             "  the renewables lose their energy every hour the reserve is",
             "  held, the battery only the margin of shifting it gives up;",
             "  delta control fits when there is curtailment to use anyway",
             "  or when a short, fast response is asked and no battery exists"]
    emit("b_delta", lines)


if __name__ == "__main__":
    allocation()
    ramp()
    envelope()
    soc_rooms()
    delta_cost()
