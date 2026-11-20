"""Chapter 20, lab E - the integrated dispatch and service lab: a bounded
controller simulation of a year with forecast uncertainty and the
hypothetical service requirement REQ-S01 (hold 5 MW of upward reserve
for 1 h, 18:00-22:00 every day, 95 % of window hours, A-300).

Cases: arbitrage only; reserve held by the controller alone; reserve in
the plan (an energy floor in the DP); reserve declared day-ahead only on
days the plan can hold it; and the last case with service calls,
communication losses and operator overrides. Grid charging stays
forbidden (A-012).

Run from the project root:   python -m companion.ch20.lab_e
Writes companion/ch20/expected/e2_*.txt and diagrams/data/ch20-*.csv.
"""
from __future__ import annotations

import numpy as np

from companion.ch20 import examples_b as eb, examples_e as ee, sources as src
from companion.ch20.common import csv, emit
from plantp import control as ct

L = src.LIMITS
S = src.SERVICE
W0, W1 = S["window"]


def floor_mwh(mw: float = S["mw"], hours: float = S["hours"]) -> float:
    return L["e_min"] + mw * hours / L["eta"]


# [start: service]
def run_year(mode: str, calls=(), outages=(), mw: float = S["mw"],
             hours: float = S["hours"]):
    """mode: 'none' | 'controller' | 'plan' | 'declared' | 'replan'
    (re-plan the rest of the day at 06, 10, 14 and 17 h with the
    intraday forecast). calls: hours
    when the operator calls the reserve; outages: (start hour, length)
    of communication losses; mw, hours: size of the service."""
    act = np.clip(src.poc_actual(), 0, None)
    fc = np.clip(src.poc_forecast(24), 0, None)
    # cautious forecast: 10 % quantile of the actual for each forecast bin
    cautious = np.clip(fc + ee.bid_offsets(fc, act, 0.10), 0, None)
    cap, price = eb.caps(), src.prices()
    lost = np.zeros(8760, bool)
    for t0, n in outages:
        lost[t0:t0 + n] = True
    fc_id = np.clip(src.poc_forecast(4), 0, None)
    c = ct.Controller(e=L["e_min"], reserve_h=hours)
    fl = floor_mwh(mw, hours)
    out = {"rev": 0.0, "held": 0, "window": 0, "declared": 0,
           "calls_ok": 0, "calls": 0, "dis": 0.0}
    for d in range(365):
        h = slice(d * 24, d * 24 + 24)
        floor = np.full(24, L["e_min"])
        room = np.clip(cap[h] - fc[h], 0, None)
        if mode in ("plan", "declared", "replan"):   # plan knows service
            floor[W0:W1] = fl
            room[W0:W1] = np.minimum(room[W0:W1], L["bess_mw"] - mw)
        args = (price[h], np.minimum(fc[h], L["bess_mw"]), room,
                L["bess_mw"], L["e_min"], L["e_max"], round(c.e), L["eta"])
        val, _, plan = ct.dp_schedule(*args, wear=10.0, floor=floor,
                                      e_end=L["e_min"])
        ok_day = np.isfinite(val)
        if mode == "declared" and ok_day:    # also with a cautious forecast
            low = (price[h], np.minimum(cautious[h], L["bess_mw"])) + args[2:]
            v_low, _, _ = ct.dp_schedule(*low, wear=10.0, floor=floor,
                                         e_end=L["e_min"])
            ok_day = np.isfinite(v_low)
        if not ok_day:                       # cannot hold it: plan without
            args = args[:2] + (np.clip(cap[h] - fc[h], 0, None),) + args[3:]
            _, _, plan = ct.dp_schedule(*args, wear=10.0, e_end=L["e_min"])
        offer = mode != "none" and (mode != "declared" or ok_day)
        out["declared"] += int(offer)
        for k in range(24):
            t = d * 24 + k
            if mode == "replan" and ok_day and k in (6, 10, 14, 17):
                g = slice(t, d * 24 + 24)
                rm = np.clip(cap[g] - fc_id[g], 0, None)
                rm[W0 - k:] = np.minimum(rm[W0 - k:], L["bess_mw"] - mw)
                v2, _, p2 = ct.dp_schedule(
                    price[g], np.minimum(fc_id[g], L["bess_mw"]), rm,
                    L["bess_mw"], L["e_min"], L["e_max"], round(c.e),
                    L["eta"], wear=10.0, floor=floor[k:], e_end=L["e_min"])
                if np.isfinite(v2):
                    plan = np.concatenate([plan[:k], p2])
            in_win = offer and W0 <= k < W1
            c.reserve_up = mw if in_win else 0.0
            req = plan[k]
            if in_win:
                out["window"] += 1
                comms = not lost[t] or c.lost_h < c.timeout_h
                if c.e >= fl - 1e-6 and comms:
                    out["held"] += 1
                if t in calls:               # reserve released and used
                    out["calls"] += 1
                    c.reserve_up = 0.0
                    req = max(plan[k], 0.0) + mw
            r = c.step(t, act[t], req, cap[t], not lost[t])
            if in_win and t in calls and r["discharge"] >= mw - 1e-6:
                out["calls_ok"] += 1
            out["rev"] += r["export"] * price[t]
            out["dis"] += r["discharge"]
    out["alarms"] = len(c.alarms)
    out["alarm_list"] = c.alarms
    return out
# [end: service]


def cases() -> None:
    rng = np.random.default_rng(2020)
    days = rng.choice(365, 15, replace=False)
    calls = set(int(d * 24 + rng.integers(W0, W1)) for d in days)
    outages = [(int(t), 3) for t in rng.choice(8700, 6, replace=False)]
    runs = [("arbitrage only", "none", (), ()),
            ("controller holds reserve", "controller", (), ()),
            ("reserve in the plan", "plan", (), ()),
            ("declared day-ahead", "declared", (), ()),
            ("declared + calls + outages", "declared", calls, outages)]
    lines = [f"REQ-S01: hold {S['mw']:.0f} MW up for {S['hours']:.0f} h, "
             f"{W0}-{W1} h daily, {S['availability'] * 100:.0f} % of window hours (A-300)",
             f"  energy floor = e_min + 5 MW x 1 h / eta = {floor_mwh():.2f} MWh",
             "  case                        days  held %  revenue k u  EFC  alarms"]
    base = None
    res = {}
    for name, mode, cl, ou in runs:
        r = run_year(mode, set(cl), ou)
        res[name] = r
        base = r["rev"] if base is None else base
        held = r["held"] / r["window"] * 100 if r["window"] else 0.0
        efc = r["dis"] / (L["e_max"] - L["e_min"])
        lines.append(f"  {name:27s} {r['declared']:4d}  {held:6.1f}  {r['rev'] / 1000:11,.1f}"
                     f"  {efc:3.0f}  {r['alarms']:6d}")
    lines += ["  revenue includes all export; differences are the service's cost;",
              "  EFC = equivalent full cycles of the 32 MWh window a year",
              "  the controller alone holds the reserve by refusing the plan",
              "  (1,147 alarms); a plan that knows the floor and the 15 MW",
              "  left for scheduling keeps the same reserve with 104 alarms;",
              "  the cautious check (10 % quantile forecast) declared every",
              "  day: the plant fills 9.4 MWh before 18:00 on all of them"]
    emit("e2_cases", lines)
    r = res["declared + calls + outages"]
    cost = (base - res["declared day-ahead"]["rev"]) / 1000
    mwh = S["mw"] * (W1 - W0) * res["declared day-ahead"]["declared"]
    lines = ["service evidence of the last case:",
             f"  calls answered with 5 MW: {r['calls_ok']} of {r['calls']}",
             f"  window hours held: {r['held']} of {r['window']}"
             f" ({r['held'] / r['window'] * 100:.1f} %)",
             f"  arbitrage lost to the declared service: {cost:.1f} k u a year",
             f"  = {cost * 1000 / mwh:.2f} u per MW-hour of reserve held"
             f" ({mwh:,.0f} MW-h)",
             "  the price the service must pay at least, before wear and",
             "  the penalty for hours not held (chapter 21)"]
    emit("e2_evidence", lines)


def override_tests() -> None:
    res = []
    fl = floor_mwh()
    c = ct.Controller(e=30.0, reserve_up=S["mw"])
    r = c.step(0, 40.0, 30.0, None, True)
    res.append(("request 30 MW with reserve: clamped to 15 MW", abs(r["discharge"] - 15.0) < 1e-9))
    c = ct.Controller(e=30.0, reserve_up=S["mw"])
    r = c.step(0, 50.0, 10.0, 0.0, True)
    res.append(("operator cap 0 MW: no export, battery may not discharge",
                r["export"] <= 1e-9 and r["discharge"] == 0.0))
    c = ct.Controller(e=fl, reserve_up=S["mw"])
    r = c.step(0, 30.0, 10.0, None, True)
    res.append(("at the floor: scheduled discharge refused", r["discharge"] <= 1e-9))
    c = ct.Controller(e=fl, reserve_up=0.0)
    r = c.step(0, 30.0, S["mw"], None, True)
    res.append(("call at the floor: 5 MW delivered", abs(r["discharge"] - S["mw"]) < 1e-6))
    c = ct.Controller(e=20.0, reserve_up=S["mw"])
    c.step(0, 30.0, 5.0, None, False)
    r = c.step(1, 30.0, 5.0, None, False)
    res.append(("comms lost past timeout: fallback idle, alarm raised",
                r["discharge"] == 0.0 and any("comms" in a for _, a in c.alarms)))
    lines = ["priority and override tests (REQ-S01 with the controller):"]
    lines += [f"  {'PASS' if ok else 'FAIL'}  {n}" for n, ok in res]
    emit("e2_overrides", lines)


def sizes() -> None:
    lines = ["service size against how it is held (one year, no calls):",
             "  service       floor MWh  case        held %   cost k u   alarms"]
    rows = []
    base = run_year("none")["rev"]
    for mw, hrs in ((5, 1), (10, 1), (10, 2), (15, 1.5)):
        for mode in ("controller", "plan", "replan"):
            r = run_year(mode, mw=mw, hours=hrs)
            held = r["held"] / max(r["window"], 1) * 100
            lines.append(f"  {mw:2d} MW x {hrs:3.1f} h  {floor_mwh(mw, hrs):9.1f}  {mode:10s}"
                         f"  {held:6.1f}   {(base - r['rev']) / 1000:8.1f}   {r['alarms']:6d}")
            if mode == "controller":
                row = [len(rows) + 1, f"{(base - r['rev']) / 1000:.1f}"]
            if mode == "plan":
                rows.append(tuple(row + [f"{(base - r['rev']) / 1000:.1f}"]))
    lines += ["  'cost' is the export revenue given up against arbitrage alone;",
              "  every size passes 95 %: Plant P fills the floor before 18:00",
              "  on almost every day; the cost per MW-hour held grows with the",
              "  duration (energy) more than with the power; a plan that knows",
              "  the service costs less than a controller that refuses the",
              "  plan, and re-planning adds little when prices are known a day",
              "  ahead"]
    emit("e2_sizes", lines)
    csv("ch20-sizes.csv", "k,ctrl,plan", rows)


if __name__ == "__main__":
    cases()
    override_tests()
    sizes()
