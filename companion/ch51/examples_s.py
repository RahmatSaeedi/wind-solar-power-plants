"""Chapter 51, round s: night shifts in a row, instructions repeated back,
outages and their repair times, export-limit excursions, changes closed
with their records, curtailment classified by who ordered it, a control-
room HVAC failure in summer, wash-water quality, forecast skill by
horizon and season, service activations, line faults and reclosing,
grievances in operation, firmware drift after a year, and tag data
quality.

Run from the project root:   python -m companion.ch51.examples_s
Writes companion/ch51/expected/s_*.txt.
Teaching values (A-522 to A-529).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch20 import sources as s20
from companion.ch51.common import emit
from plantp import operations


# ------------------------------------------------ 1. nights in a row
def fatigue(limit: int = 4) -> list:
    rota = {"operator 1": "NNNNNNDDOO", "operator 2": "DDNNNOODDN", "operator 3": "NNNNNDDOOO",
            "shift lead A": "DDDNNNOODD", "authorised person": "NNNNNNNOOO"}
    over = []
    for p, r in rota.items():
        run = best = 0
        for c in r:
            run = run + 1 if c == "N" else 0
            best = max(best, run)
        if best > limit:
            over.append((p, best))
    lines = ["ten-day rota (D day, N night, O off): consecutive nights",
             f"  against a teaching limit of {limit}"]
    lines += [f"  {p:18s} {r}" for p, r in rota.items()]
    lines += [f"  over the limit: {', '.join(f'{p} ({n})' for p, n in over)}",
              "  the authorised person works seven nights because nobody else",
              "  covers shift C (lesson A): the roster gap becomes a fatigue",
              "  risk on the very person who switches"]
    emit("s_fatigue", lines)
    return over


# ------------------------------------------------ 2. repeat-back
INSTR = [   # instruction, repeated back?, logged with time?
    ("cap export 80 MW 11-15", True, True), ("hold Q at 0 Mvar", True, False),
    ("open WS3 for the network owner's work", False, True),
    ("release cap", True, True), ("reduce ramp to 5 MW/min", False, False)]


def repeat_back() -> dict:
    no_rb = [i for i, rb, _ in INSTR if not rb]
    no_t = [i for i, _, t in INSTR if not t]
    lines = ["grid operator's instructions in a week: repeated back and logged?"]
    lines += [f"  {i:38s} repeat-back {'yes' if rb else 'NO '}  time {'yes' if t else 'NO'}"
              for i, rb, t in INSTR]
    lines += [f"  {len(no_rb)} not repeated back, {len(no_t)} without a time: an instruction",
              "  that was not read back may have been heard wrong; one",
              "  without a time cannot be matched to the plant's response",
              "  in a dispute - both are a line in the shift-lead check"]
    emit("s_repeat", lines)
    return dict(no_rb=no_rb, no_t=no_t)


# ------------------------------------------------ 3. outages and repair times
OUTAGES = [   # equipment, hours down, waiting h (parts, access, permit)
    ("T03 converter", 46, 30), ("T07 pitch", 18, 6), ("PVF2-1 inverter", 70, 52),
    ("T11 yaw", 9, 2), ("WS2 feeder", 4, 1), ("PVF1-3 combiner", 26, 20),
    ("T05 gearbox oil", 31, 12), ("BESS-A PCS", 22, 15)]


def outages() -> dict:
    down = sum(h for _, h, _ in OUTAGES)
    wait = sum(w for *_, w in OUTAGES)
    mttr = down / len(OUTAGES)
    lines = ["forced outages of the first year (hours down, of which waiting)"]
    lines += [f"  {e:18s} {h:4d} h  waiting {w:3d} h" for e, h, w in OUTAGES]
    lines += [f"  {len(OUTAGES)} outages, {down} h; mean time to restore {mttr:.1f} h",
              f"  waiting for parts, access or permits {wait} h = {wait / down:.0%} of the time",
              "  the repair itself is the smaller part: spares, access and",
              "  permits are where availability is won (ch 37 waiting,",
              "  ch 52 maintenance)"]
    emit("s_outages", lines)
    return dict(down=down, wait=wait, mttr=mttr)


# ------------------------------------------------ 4. export-limit excursions
def excursions(seed: int = 54, cap: float = 100.0) -> dict:
    rng = np.random.default_rng(seed)
    p = np.clip(cap - 3.0 + rng.normal(0, 0.7, 60 * 24), 0, None)    # a capped day, 1-min
    p[700:704] += np.array([4.5, 6.0, 4.5, 3.6])                        # gust before the limiter acts
    over = p > cap
    gust = int(over[700:704].sum())
    lines = [f"export at the POC on a capped day, 1-minute values, limit {cap:.0f} MW",
             f"  minutes above the limit: {over.sum()}; highest {p.max():.1f} MW",
             f"  {gust} of them in one gust, before the controller's next",
             "  cycle: each is an operating-limit excursion recorded with",
             "  its cause; the controller holds a margin below the limit",
             "  for that reason (ch 20 export)"]
    emit("s_excursions", lines)
    return dict(minutes=int(over.sum()), peak=float(p.max()))


# ------------------------------------------------ 5. management of change
CHANGES = {   # change: (drawings updated, procedure updated, training done)
    "inverter firmware 4.3 on block 2": (True, True, False),
    "new alarm grouping by feeder": (True, False, True),
    "battery SOC window 12-88 %": (True, True, True),
    "second RTU in the substation": (False, False, False),
    "export ramp limit 8 MW/min": (True, False, False)}


def moc() -> list:
    open_ = [(c, [n for n, v in zip(("drawings", "procedure", "training"), f) if not v])
             for c, f in CHANGES.items() if not all(f)]
    lines = ["changes of the first year: closed with their records?"]
    lines += [f"  {c:36s} missing: {', '.join(m)}" for c, m in open_]
    lines += [f"  {len(open_)} of {len(CHANGES)} changes are open; the second RTU has none of",
              "  the three - it is also the tag missing from the asset register",
              "  (lesson M); a change is closed when the plant, its records",
              "  and its people all know about it"]
    emit("s_moc", lines)
    return open_


# ------------------------------------------------ 6. curtailment by who ordered it
CURT = {"grid operator, security of supply": 166.0, "grid operator, planned works": 42.0,
        "plant, export-limit margin": 18.0, "plant, economic (negative price)": 0.0}


def curtailment_classes() -> dict:
    tot = sum(CURT.values())
    lines = ["curtailed energy of the first year by who ordered it and why (MWh)"]
    lines += [f"  {k:36s} {v:6.0f}" for k, v in CURT.items()]
    lines += [f"  total {tot:.0f} MWh; ordered by the grid operator "
              f"{CURT['grid operator, security of supply'] + CURT['grid operator, planned works']:.0f}",
              "  the class decides who carries the loss under the contract",
              "  (compensated or not) - so the record names the instruction,",
              "  not only the energy; the rules are verified locally"]
    emit("s_curtail", lines)
    return dict(tot=tot)


# ------------------------------------------------ 7. control-room HVAC failure
def hvac(t0: float = 24.0, t_out: float = 44.0, heat_kw: float = 9.0, ua_kw_k: float = 0.45,
         c_kj_k: float = 9000.0, limit: float = 35.0) -> dict:
    t_ss = t_out + heat_kw / ua_kw_k
    tau_h = c_kj_k / ua_kw_k / 3600
    t_lim = -tau_h * math.log((t_ss - limit) / (t_ss - t0))
    lines = ["control-room HVAC lost on a summer afternoon (one-node teaching model)",
             f"  outside {t_out:.0f} C, equipment heat {heat_kw} kW, loss {ua_kw_k} kW/K: room "
             f"heads for {t_ss:.0f} C",
             f"  time constant {tau_h:.1f} h; {limit:.0f} C (servers' limit, teaching) in "
             f"{t_lim * 60:.0f} min",
             "  the second HVAC unit (N+1, ch 23) is the plan; without it,",
             "  the procedure sheds non-essential servers and opens the",
             "  emergency ventilation within that time"]
    emit("s_hvac", lines)
    return dict(minutes=t_lim * 60, t_ss=t_ss)


# ------------------------------------------------ 8. wash-water quality
def wash_water(limit_us: float = 500.0) -> list:
    tests = {"well W-1 after RO": 180, "tanker load 14": 620, "tanker load 15": 410,
             "storage tank (week 23)": 530, "well W-2 after RO": 220}
    bad = [k for k, v in tests.items() if v > limit_us]
    lines = [f"wash-water conductivity against the module maker's limit (teaching "
             f"{limit_us:.0f} uS/cm)"]
    lines += [f"  {k:24s} {v:4d}" + ("  OVER" if v > limit_us else "") for k, v in tests.items()]
    lines += [f"  over: {', '.join(bad)}",
              "  washing with it risks deposits and the module warranty",
              "  (ch 10, ch 41); the tank is sampled before each wash",
              "  campaign, and a failed sample stops the trucks"]
    emit("s_washwater", lines)
    return bad


# ------------------------------------------------ 9. forecast skill by horizon
def skill() -> dict:
    act = s20.poc_actual()
    pers = np.roll(act, 1)
    out = {}
    for lead in (1, 3, 24):
        fc = s20.poc_forecast(lead)
        rmse = float(np.sqrt(np.mean((fc - act) ** 2)))
        rp = float(np.sqrt(np.mean((pers - act) ** 2)))
        out[lead] = (rmse, 1 - rmse / rp)
    lines = ["forecast error at the POC by lead time over the year",
             "  lead h   RMSE MW   skill vs 1-h persistence"]
    lines += [f"  {k:6d}   {r:7.1f}   {s:+8.2f}" for k, (r, s) in out.items()]
    lines += ["  the day-ahead forecast is worse than 'same as last hour' for",
              "  the next hour, and it is not meant for it: each decision",
              "  uses the forecast of its own horizon (ch 15, ch 37) - the",
              "  shift of lesson D used the intraday one for that reason"]
    emit("s_skill", lines)
    return out


# ------------------------------------------------ 10. service activations
ACTIVATIONS = [   # requested MW, delivered MW, seconds to 90 %
    (5.0, 5.0, 0.8), (5.0, 4.9, 0.9), (3.0, 3.0, 0.7), (5.0, 3.6, 0.8), (5.0, 5.0, 1.4)]


def activations(t_limit: float = 1.0, tol: float = 0.95) -> dict:
    bad = [(k + 1, r, d, t) for k, (r, d, t) in enumerate(ACTIVATIONS)
           if d < tol * r or t > t_limit]
    lines = [f"service activations in a month: delivered >= {tol:.0%} of requested",
             f"  within {t_limit} s (teaching)"]
    lines += [f"  #{k + 1}: requested {r} MW, delivered {d} MW, {t} s"
              for k, (r, d, t) in enumerate(ACTIVATIONS)]
    lines += [f"  failed: {', '.join(f'#{k}' for k, *_ in bad)} - #4 ran into the SOC floor",
              "  (lesson B), #5 was slow while a tap changer moved; the",
              "  settlement counts each event, and the operator reports",
              "  both with their causes"]
    emit("s_activations", lines)
    return dict(bad=len(bad))


# ------------------------------------------------ 11. line faults and reclosing
FAULTS = [   # fault, auto-reclose, minutes to restore
    ("bird at T09 (transient)", True, 0.0), ("lightning at T14 (transient)", True, 0.0),
    ("vegetation T13-T18", False, 410.0), ("insulator flashover T05", False, 95.0)]


def line_faults() -> dict:
    perm = [(f, m) for f, ar, m in FAULTS if not ar]
    lines = ["132 kV line faults of the first year"]
    lines += [f"  {f:30s} {'reclosed' if ar else 'locked out'}"
              + ("" if ar else f", restored after {m:.0f} min") for f, ar, m in FAULTS]
    lines += [f"  the two permanent faults cost {sum(m for _, m in perm) / 60:.1f} h of export;",
              "  the vegetation fault is the late patrol of lesson K: the",
              "  cheapest outage was the one the patrol would have prevented"]
    emit("s_faults", lines)
    return dict(perm=len(perm), hours=sum(m for _, m in perm) / 60)


# ------------------------------------------------ 12. grievances in operation
def grievances(ack_days: int = 3, close_days: int = 30) -> dict:
    g = [(2, 1, 12), (3, 2, 20), (5, 4, 41), (2, 1, 8), (1, 6, 35), (2, 2, 15)]
    late_ack = sum(1 for _, a, _ in g if a > ack_days)
    late_close = sum(1 for *_, c in g if c > close_days)
    lines = [f"grievances in the first operating year: {len(g)} (teaching)",
             f"  acknowledged after {ack_days} days: {late_ack}; closed after {close_days} days: "
             f"{late_close}",
             "  fewer than in construction (ch 49), two still slow to close:",
             "  the O&M team is smaller and the complaints (dust from",
             "  washing trucks, a track blocked by a crane) touch the",
             "  contractor - the mechanism keeps its times in operation too"]
    emit("s_griev", lines)
    return dict(n=len(g), late_ack=late_ack, late_close=late_close)


# ------------------------------------------------ 13. firmware drift
def firmware() -> dict:
    baseline = {"inverters": "4.3.0", "turbine controllers": "7.2", "switches": "6.2.1",
                "RTUs": "8.4", "gateways": "2.3.0"}
    found = {"inverters": ["4.3.0"] * 8 + ["4.2.0"] * 2, "turbine controllers": ["7.2"] * 12,
             "switches": ["6.2.1"] * 30 + ["6.1.9"], "RTUs": ["8.4", "8.3"],
             "gateways": ["2.3.0", "2.3.0"]}
    drift = {k: sum(v != baseline[k] for v in found[k]) for k in baseline}
    lines = ["firmware against the baseline after a year (ch 48 baseline)"]
    lines += [f"  {k:20s} {baseline[k]:6s} {len(found[k]):3d} devices, {drift[k]} off baseline"
              for k in baseline]
    lines += [f"  {sum(drift.values())} devices off: two inverters replaced from old stock,",
              "  one switch swapped after a fault, the second RTU - each",
              "  a change without its configuration step (the change records",
             "  above)"]
    emit("s_firmware", lines)
    return drift


# ------------------------------------------------ 14. tag data quality
def data_quality() -> dict:
    tags = 4200
    bad = {"stale (no update > 10 min)": 63, "flagged invalid": 21, "frozen value": 38,
           "out of range": 12}
    tot = sum(bad.values())
    lines = [f"SCADA tag quality on one day: {tags:,} tags"]
    lines += [f"  {k:28s} {v:4d}" for k, v in bad.items()]
    lines += [f"  {tot} tags ({tot / tags:.1%}) not usable that day; frozen values are the",
              "  hardest to see - the number looks right and never moves",
              "  (ch 35 quality flags, ch 37 validation); the daily report",
              "  lists them by owner"]
    emit("s_quality", lines)
    return dict(tot=tot, share=tot / tags)


if __name__ == "__main__":
    fatigue()
    repeat_back()
    outages()
    excursions()
    moc()
    curtailment_classes()
    hvac()
    wash_water()
    skill()
    activations()
    line_faults()
    grievances()
    firmware()
    data_quality()
