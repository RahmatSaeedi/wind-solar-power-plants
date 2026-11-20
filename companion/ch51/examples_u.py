"""Chapter 51, round u: handover length against items missed, curtailment
response against the ramp limit, battery containers available, night
import through the POC, a field audit of procedure use, invoices against
meters, two forecast providers, the service payment, HVAC filters in the
dust season, fire-pump weekly runs, RO recovery and membrane cleaning,
substation thermography, local purchasing, drawing redlines waiting for
as-built, and gate entries against inductions.

Run from the project root:   python -m companion.ch51.examples_u
Writes companion/ch51/expected/u_*.txt.
Teaching values (A-522 to A-529).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch20 import sources as s20
from companion.ch51.common import emit
from plantp import control


# ------------------------------------------------ 1. handover length
def handover_length() -> dict:
    minutes = np.array([8, 15, 12, 6, 20, 9, 14, 5, 18, 11])
    missed = np.array([2, 0, 1, 3, 0, 1, 0, 3, 0, 1])
    r = float(np.corrcoef(minutes, missed)[0, 1])
    short = minutes < 10
    lines = ["ten handovers: minutes taken and checklist items missed",
             "  minutes " + " ".join(f"{m:3d}" for m in minutes),
             "  missed  " + " ".join(f"{m:3d}" for m in missed),
             f"  correlation {r:+.2f}; items missed on average: under 10 min "
             f"{missed[short].mean():.1f},",
             f"  10 min or more {missed[~short].mean():.1f}",
             "  a correlation is not a cause - a busy shift both hurries the",
             "  handover and has more to hand over - but the remedy is the",
             "  same: the checklist is read item by item, whatever the clock"]
    emit("u_handover", lines)
    return dict(r=r, short=float(missed[short].mean()), long=float(missed[~short].mean()))


# ------------------------------------------------ 2. curtailment response
CURT_EVENTS = [   # export before, cap ordered (MW), minutes allowed (teaching)
    (96, 80, 10), (140, 80, 10), (150, 60, 10), (120, 100, 5), (110, 30, 15)]


def curtail_response(ramp: float = 8.0) -> list:
    rows = []
    for p0, cap, allowed in CURT_EVENTS:
        need = max(p0 - cap, 0) / ramp
        rows.append((p0, cap, allowed, need, need <= allowed))
    late = [r for r in rows if not r[4]]
    lines = [f"cap instructions against the {ramp:.0f} MW/min ramp limit of the controller",
             "  before  cap  allowed min  needed min"]
    lines += [f"  {p0:6.0f} {cap:4.0f} {a:12.0f} {n:11.1f}" + ("" if ok else "  LATE")
              for p0, cap, a, n, ok in rows]
    lines += [f"  {len(late)} instruction(s) cannot be met at the ramp limit: whether a",
              "  cap overrides the ramp limit is the grid operator's rule;",
              "  the procedure states it, and the controller is set to",
              "  match - the first time is not the night it is needed"]
    emit("u_curtail_resp", lines)
    return late


# ------------------------------------------------ 3. battery containers available
def containers() -> dict:
    out_h = [0, 0, 120, 0, 36, 0, 410, 0]          # hours out in the year, 8 containers
    hours = 8760
    avail = [1 - h / hours for h in out_h]
    e_avail = float(np.mean(avail))
    full = sum(1 for h in out_h if h == 0)
    lines = ["battery: eight containers, hours out of service in the first year",
             "  " + " ".join(f"{h:4d}" for h in out_h),
             f"  energy availability {e_avail:.2%}; containers never out: {full} of 8",
             f"  container 7 alone is {out_h[6] / sum(out_h):.0%} of the lost container-hours",
             "  (a cooling fault waiting for a part): one bad unit sets the",
             "  battery's availability (ch 19 spares)"]
    emit("u_containers", lines)
    return dict(e=e_avail, worst=out_h[6] / sum(out_h))


# ------------------------------------------------ 4. night import
def night_import() -> dict:
    p = s20.poc_actual()
    imp = p < 0
    e_imp = float(-p[imp].sum())
    starts = 24 * np.cumsum([0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30])
    by_month = np.add.reduceat(-np.where(imp, p, 0.0), starts).round(1)
    worst = int(np.argmax(by_month)) + 1
    lines = ["hours the plant draws from the grid at the POC (data-pack year)",
             f"  hours importing: {int(imp.sum())}; energy imported {e_imp:.1f} MWh",
             f"  most in month {worst} ({by_month[worst - 1]:.1f} MWh), least in month "
             f"{int(np.argmin(by_month)) + 1} ({by_month.min():.1f} MWh): calm nights",
             "  the import is metered and billed in its own register",
             "  (ch 48: a reversed CT would have shown it as export); it is",
             "  not 'lost energy' but a cost the operating report carries"]
    emit("u_import", lines)
    return dict(hours=int(imp.sum()), mwh=e_imp, worst=worst,
                worst_mwh=float(by_month[worst - 1]))


# ------------------------------------------------ 5. field audit of procedure use
def wilson(k: int, n: int, z: float = 1.96) -> tuple:
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return c - h, c + h


def field_audit() -> dict:
    n, k = 24, 17                      # tasks observed, done with the procedure at hand
    lo, hi = wilson(k, n)
    lines = [f"field audit: {n} tasks observed, {k} done with the current procedure",
             f"  share {k / n:.0%}, 95 % interval {lo:.0%} to {hi:.0%} (Wilson)",
             f"  even the top of the interval is short of 'always': of the {n - k},",
             "  five were routine tasks done from memory and two used a",
             "  superseded copy - the audit finds what the procedure",
             "  register cannot"]
    emit("u_audit", lines)
    return dict(share=k / n, lo=lo, hi=hi)


# ------------------------------------------------ 6. invoices against meters
INVOICE = {   # month: (invoiced MWh, main meter MWh, SCADA MWh)
    1: (21_300, 21_300, 21_480), 2: (23_900, 23_900, 24_050), 3: (28_100, 27_640, 27_800),
    4: (26_400, 26_400, 26_610), 5: (27_200, 27_200, 27_390), 6: (24_800, 24_800, 25_020)}


def invoices(tol: float = 0.005) -> dict:
    bad = [m for m, (i, mm, _) in INVOICE.items() if abs(i - mm) / mm > tol]
    scada = [(s - mm) / mm for _, mm, s in INVOICE.values()]
    lines = [f"invoiced energy against the main meter and SCADA (tolerance {tol:.1%})",
             "  month  invoiced   meter    SCADA"]
    lines += [f"  {m:5d} {i:9,d} {mm:7,d} {s:8,d}" + ("  CHECK" if m in bad else "")
              for m, (i, mm, s) in INVOICE.items()]
    lines += [f"  month(s) to check: {', '.join(map(str, bad))}; SCADA reads "
              f"{min(scada):+.1%} to {max(scada):+.1%}",
              "  above the meter every month (it counts before the losses to",
              "  the POC): SCADA explains, the meter settles; the March",
              "  invoice used a schedule, not the meter - a credit note"]
    emit("u_invoice", lines)
    return dict(bad=bad, smin=min(scada), smax=max(scada))


# ------------------------------------------------ 7. two forecast providers
def providers(seed: int = 57) -> dict:
    act = np.minimum(s20.poc_actual(), 100.0)
    a = np.minimum(s20.poc_forecast(24), 100.0)
    rng = np.random.default_rng(seed)
    b = np.clip(act + 2.5 + rng.normal(0, 9.0, act.size), 0, 100)   # provider B, a trial
    sh, lo = s20.IMBALANCE["short"], s20.IMBALANCE["long"]
    out = {}
    for name, fc in (("A (in use)", a), ("B (trial)", b)):
        err = fc - act
        cost = control.imbalance(fc, act, sh, lo)
        out[name] = (float(np.abs(err).mean()), float(err.mean()), float(cost))
    by_mae = min(out, key=lambda k: out[k][0])
    by_cost = min(out, key=lambda k: out[k][2])
    lines = ["day-ahead providers over the year (schedule = forecast, capped at",
             "  the export limit): mean absolute error, bias, imbalance cost",
             "  provider       MAE MW   bias MW   cost u"]
    lines += [f"  {k:12s} {m:8.1f} {b_:+8.1f} {c:10,.0f}" for k, (m, b_, c) in out.items()]
    if by_mae == by_cost:
        lines += [f"  {by_cost} is better on both counts."]
    else:
        lines += [f"  smaller error: {by_mae}; lower cost: {by_cost} - they disagree"]
    lines += ["  a positive bias schedules more than the plant gives, and a",
              f"  shortfall costs {sh / lo:.0f} times a surplus (A-301): bias, not only the",
              "  size of the error, sets the cost - a provider is judged on",
              "  the plant's own cost over a full year of trial before the",
              "  contract changes"]
    emit("u_providers", lines)
    return dict(out=out, by_mae=by_mae, by_cost=by_cost)


# ------------------------------------------------ 8. service payment
def service_payment(a: float = 113 / 120, price: float = 8.0, lo: float = 0.85) -> dict:
    target = s20.SERVICE["availability"]
    factor = min(1.0, max(0.0, (a - lo) / (target - lo)))
    full = 120 * s20.SERVICE["mw"] * price
    lines = [f"service payment for the month: {full:,.0f} u at full availability",
             f"  ({price} u per MW-h, teaching)",
             f"  rule (teaching): full at {target:.0%}, falling straight to zero at "
             f"{lo:.0%}",
             f"  availability {a:.1%} -> factor {factor:.3f} -> {full * factor:,.0f} u "
             f"({full * (1 - factor):,.0f} u less)",
             f"  {120 - round(a * 120)} hours of 120 ({1 - a:.1%}) cost {1 - factor:.1%} of the "
             "payment: the",
             "  curve makes the last per cents the dearest; four of those",
             "  hours were the SOC floor of lesson B"]
    emit("u_payment", lines)
    return dict(factor=factor, lost=full * (1 - factor), full=full)


# ------------------------------------------------ 9. HVAC filters
def filters(limit_pa: float = 250.0) -> dict:
    weeks = np.arange(10)
    dp = np.array([120, 126, 131, 138, 143, 175, 182, 188, 195, 201], float)  # storm in week 5
    slope = float(np.polyfit(weeks[5:], dp[5:], 1)[0])
    weeks_left = (limit_pa - dp[-1]) / slope
    lines = [f"battery-container HVAC filter pressure drop, weekly (limit {limit_pa:.0f} Pa)",
             "  " + " ".join(f"{x:4.0f}" for x in dp),
             f"  a dust storm in week 5 added {dp[5] - dp[4]:.0f} Pa at once; since then "
             f"{slope:.1f} Pa a week",
             f"  limit reached in about {weeks_left:.0f} weeks: the change is planned",
             "  for the next service visit, not after the HVAC trips on a hot",
             "  afternoon (ch 19 HVAC, ch 45 cells and heat)"]
    emit("u_filters", lines)
    return dict(slope=slope, weeks=weeks_left)


# ------------------------------------------------ 10. fire-pump weekly runs
def pump_runs(band=(7.0, 8.0)) -> dict:
    runs = {w: p for w, p in enumerate([7.4, 7.5, None, 7.3, 7.4, 6.8, 7.3, None, None,
                                        7.4, 7.5, 7.2, 6.6, 7.4], start=1)}
    missing = [w for w, p in runs.items() if p is None]
    low = [w for w, p in runs.items() if p is not None and not band[0] <= p <= band[1]]
    lines = ["fire-pump weekly runs: churn pressure (bar) against the band",
             f"  {band[0]}-{band[1]} (teaching)",
             "  " + " ".join("  - " if p is None else f"{p:4.1f}" for p in runs.values()),
             f"  weeks missed: {', '.join(map(str, missing))}; out of band: "
             f"{', '.join(map(str, low))}",
             "  two weeks missed in a row is an impairment, with its permit",
             "  and compensating measures (ch 32); the low readings go to",
             "  the maintainer with the trend, not one at a time"]
    emit("u_pump", lines)
    return dict(missing=missing, low=low)


# ------------------------------------------------ 11. RO recovery
def ro(drop: float = 0.10) -> dict:
    perm = np.array([10.0, 9.9, 9.7, 9.5, 9.2, 8.9, 9.9, 9.8, 9.6, 9.3])   # m3/h normalised
    clean = [i for i in range(1, perm.size) if perm[i] > perm[i - 1] + 0.5]
    first = next(i for i in range(perm.size) if perm[i] < (1 - drop) * perm[0])
    lines = ["RO unit: normalised permeate flow by month (m3/h)",
             "  " + " ".join(f"{x:4.1f}" for x in perm),
             f"  cleaning trigger at a {drop:.0%} drop (teaching): month {first + 1}; "
             f"cleaned in month {clean[0] + 1}",
             f"  ({clean[0] - first} month after the trigger)",
             "  normalising to feed temperature and pressure is what makes",
             "  the trend readable; the cleaning restored the flow, and the",
             "  next trigger is the record that books the chemicals and the",
             "  water for it (ch 29)"]
    emit("u_ro", lines)
    return dict(first=first + 1, clean=clean[0] + 1)


# ------------------------------------------------ 12. thermography
HOTSPOTS = {"T1 HV bushing B": 4, "WS2 cable box L2": 14, "SST LV fuse F3": 32,
            "BESS-A feeder joint": 9, "coupler disconnector L1": 21, "VT secondary MCB": 2}


def thermography(classes=((10, "monitor"), (20, "plan repair"), (999, "repair now"))) -> dict:
    def cls(dt):
        return next(c for lim, c in classes if dt < lim)
    groups = {}
    for k, dt in HOTSPOTS.items():
        groups.setdefault(cls(dt), []).append(k)
    lines = ["substation thermography: temperature rise over a similar part (K)"]
    lines += [f"  {k:24s} {dt:3d} K  {cls(dt)}" for k, dt in HOTSPOTS.items()]
    lines += [f"  repair now: {len(groups.get('repair now', []))}; plan repair: "
              f"{len(groups.get('plan repair', []))} (teaching classes)",
              "  the survey is done under load with the readings normalised to",
              "  it; repairs are done dead, under a permit, never on the hot",
              "  part live"]
    emit("u_thermo", lines)
    return groups


# ------------------------------------------------ 13. local purchasing
def local_spend(target: float = 0.30) -> dict:
    spend = {"services": (1_850, 940), "consumables": (620, 410), "spares": (3_100, 120),
             "transport": (480, 420)}                         # k u: (total, local)
    tot = sum(t for t, _ in spend.values())
    loc = sum(l for _, l in spend.values())
    lines = [f"O&M purchasing in the first year (k u): total and local, target {target:.0%}"]
    lines += [f"  {k:12s} {t:6,d} {l:6,d}  {l / t:4.0%}" for k, (t, l) in spend.items()]
    lines += [f"  local share {loc / tot:.0%}: spares come from the makers and cannot be",
              "  local; without spares the share is "
              f"{(loc - 120) / (tot - 3_100):.0%} - the commitment's",
              "  basis (with or without spares) belongs in the register,",
              "  or the report argues about the denominator"]
    emit("u_local", lines)
    return dict(share=loc / tot, share_ex=(loc - 120) / (tot - 3_100))


# ------------------------------------------------ 14. redlines waiting
def redlines(today: int = 365, limit: int = 90) -> dict:
    red = {"DWG-0005 one-line rev E": 210, "WS1 schematic": 300, "BESS-A cable route": 330,
           "PPC wiring": 140, "SST LV board": 352, "fire panel zones": 95}
    old = {k: today - d for k, d in red.items() if today - d > limit}
    lines = [f"field redlines waiting for an as-built revision on day {today}"]
    lines += [f"  {k:26s} marked day {d:3d}, waiting {today - d:3d} days" + (
        "  OLD" if k in old else "") for k, d in red.items()]
    lines += [f"  {len(old)} older than {limit} days; the one-line rev E has waited "
              f"{old.get('DWG-0005 one-line rev E', 0)}",
              "  days - the switching programs are written from it"]
    emit("u_redlines", lines)
    return old


# ------------------------------------------------ 15. gate entries against inductions
def gate(days: int = 7) -> dict:
    entries = {"O&M staff": (420, 420), "maker's technicians": (64, 58),
               "contractor (washing)": (96, 80), "visitors (escorted)": (22, 22),
               "delivery drivers": (35, 35)}            # (entries, with induction record)
    gap = {k: e - i for k, (e, i) in entries.items() if e != i}
    lines = [f"gate entries in {days} days against induction records"]
    lines += [f"  {k:22s} {e:4d} entries, {i:4d} inducted" for k, (e, i) in entries.items()]
    lines += [f"  {sum(gap.values())} entries without an induction record: the washing",
              f"  contractor's new crew ({gap['contractor (washing)']}) and maker's technicians "
              f"({gap[chr(109) + 'aker' + chr(39) + 's technicians']}) -",
              "  the gate checks the record, not the company badge (who may",
              "  enter is a safety record)"]
    emit("u_gate", lines)
    return gap


if __name__ == "__main__":
    handover_length()
    curtail_response()
    containers()
    night_import()
    field_audit()
    invoices()
    providers()
    service_payment()
    filters()
    pump_runs()
    ro()
    thermography()
    local_spend()
    redlines()
    gate()
