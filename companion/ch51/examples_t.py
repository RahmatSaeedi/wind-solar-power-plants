"""Chapter 51, round t: staff numbers for a 24-hour post, the operating-
limit register, battery SOC drift between calibrations, reactive set-point
following, competence expiry, availability re-declarations, ramp warnings
from the forecast, energy recovery after service activations, diesel test
loads, station-battery capacity trend, fire false alarms by detector
type, the line's weather-dependent rating over the data-pack year,
community notice of works, spares counted against the register, and
emergency contacts checked.

Run from the project root:   python -m companion.ch51.examples_t
Writes companion/ch51/expected/t_*.txt.
Teaching values (A-522 to A-529).
"""
from __future__ import annotations

import math
from datetime import date

import numpy as np

from companion.ch20 import sources as s20
from companion.ch51 import sources as src
from companion.ch51.common import emit
from plantp import datapack, operations


# ------------------------------------------------ 1. people for a 24-h post
def staffing(hours_person: float = 2184 - 200 - 120 - 60) -> dict:
    posts = {k: v for k, v in src.NEED.items() if k != "first aider"}
    n_posts = sum(posts.values())
    need = n_posts * 8760 / hours_person
    have = sum(sum(src.ROSTER[k].values()) for k in posts)
    short = need - have
    lines = [f"posts filled around the clock: {n_posts} (first aid is a qualification)",
             "  hours a person can work a year: 2,184 - leave 200",
             f"  - training 120 - sickness 60 = {hours_person:,.0f}",
             f"  people needed: {n_posts} x 8,760 / {hours_person:,.0f} = {need:.1f}; on the "
             f"roster: {have}",
             f"  short by {short:.1f} people = {short * hours_person:,.0f} h of overtime a year,",
             f"  {short * hours_person / have:.0f} h for each person on the roster: four shifts",
             "  of four are not enough once leave and training are counted",
             "  (lesson A)"]
    emit("t_staffing", lines)
    return dict(need=need, have=have, overtime=short * hours_person)


# ------------------------------------------------ 2. operating-limit register
LIMITS_REG = {   # limit: (source value, PPC setting, procedure value, source)
    "export limit MW": (100, 100, 100, "connection agreement rev 3"),
    "ramp limit MW/min": (8, 8, 10, "grid operator instruction GI-07"),
    "battery SOC window %": ("12-88", "12-88", "12-88", "battery maker letter"),
    "Q at full output Mvar": (33, 30.6, 33, "REQ-G05 with DEV-11"),
    "service reserve MW": (5, 5, 5, "service agreement"),
    "comms timeout h": (1, 1, 1, "control basis D-024")}


def limits_register() -> list:
    bad = [(k, s, p, o) for k, (s, p, o, _) in LIMITS_REG.items() if not s == p == o]
    lines = ["operating limits: source document, controller setting, procedure"]
    lines += [f"  {k:22s} {str(s):>6s} {str(p):>6s} {str(o):>6s}  {r}"
              for k, (s, p, o, r) in LIMITS_REG.items()]
    lines += [f"  {len(bad)} limits disagree: the ramp limit changed in the controller",
              "  but not in the procedure (the open change of round s); Q",
              "  is set to the 30.6 Mvar the plant can give under deviation",
              "  DEV-11 while the procedure still promises 33 - the operator",
              "  would offer what the plant cannot deliver"]
    emit("t_limits", lines)
    return bad


# ------------------------------------------------ 3. SOC drift between calibrations
def soc_drift(drift_pct_day: float = 0.35, margin_pct: float = 2.0) -> dict:
    full = [2, 3, 9, 17, 18, 29]          # days of a month the BESS reached the top
    gaps = [b - a for a, b in zip([0] + full, full + [31])]
    worst = max(gaps)
    lines = [f"battery SOC estimate drifts {drift_pct_day} %/day until a full charge "
             "recalibrates it",
             f"  days with a full charge in a month: {', '.join(map(str, full))}",
             f"  longest gap {worst} days: error up to {worst * drift_pct_day:.1f} % against "
             f"a {margin_pct:.0f} % margin",
             f"  the margin allows {margin_pct / drift_pct_day:.1f} days: a rule that asks for",
             "  a calibration charge after five days without one keeps the",
             "  service floor honest (ch 45 lesson: the flat LFP curve",
             "  hides SOC error between 20 and 80 %)"]
    emit("t_socdrift", lines)
    return dict(worst=worst, err=worst * drift_pct_day, days=margin_pct / drift_pct_day)


# ------------------------------------------------ 4. Q set-point following
def q_following(tol: float = 1.5) -> dict:
    # 10-minute intervals of an afternoon: grid operator's Q set-point and
    # the plant's capability at that output (Mvar)
    sp = [0, 0, 10, 10, 10, 20, 20, 20, 20, 5, 5, 0]
    cap = [33, 33, 33, 32, 31, 30.6, 30.6, 18, 18, 30, 33, 33]   # two blocks off at 7-8
    act, prev = [], 0.0
    for k, (s, c) in enumerate(zip(sp, cap)):
        target = min(s, c)
        act.append(prev + 0.8 * (target - prev))   # one interval to settle
        prev = act[-1]
    steps = {k for k in range(1, len(sp)) if sp[k] != sp[k - 1]}
    out = [k for k in range(len(sp)) if k not in steps and abs(act[k] - sp[k]) > tol]
    lines = [f"reactive set-point following, 10-minute values, tolerance +/-{tol} Mvar",
             "  k   set   capability   measured"]
    lines += [f"  {k:2d}  {s:4.0f}   {c:10.1f}   {a:8.1f}" + ("  OUT" if k in out else "")
              for k, (s, c, a) in enumerate(zip(sp, cap, act))]
    lines += [f"  intervals out of tolerance after settling: {len(out)}",
              "  each is a capability limit (two PV blocks off), not a control",
              "  fault: the operator tells the grid operator the reduced",
              "  capability at once, rather than letting the error stand"]
    emit("t_qfollow", lines)
    return dict(out=len(out))


# ------------------------------------------------ 5. competence expiry
COMPETENCE = {   # person: {course: expiry day}; today day 365, next month 395
    "AP-1": {"HV authorisation": 380, "first aid": 500},
    "AP-2": {"HV authorisation": 410, "fire warden": 400},
    "AP-3": {"HV authorisation": 372, "first aid": 360},
    "AP-4": {"HV authorisation": 600},
    "lead A": {"switching": 390, "first aid": 358},
    "lead B": {"switching": 700}, "lead C": {"switching": 520},
    "lead D": {"switching": 388}}


def competence(today: int = 365, horizon: int = 30) -> dict:
    expired = [(p, c) for p, cs in COMPETENCE.items() for c, d in cs.items() if d < today]
    soon = [(p, c, d) for p, cs in COMPETENCE.items() for c, d in cs.items()
            if today <= d < today + horizon]
    ap_ok = [p for p, cs in COMPETENCE.items()
             if cs.get("HV authorisation", 0) >= today + horizon]
    lines = [f"competence records on day {today}: expired and expiring within "
             f"{horizon} days"]
    lines += [f"  expired: {p} {c}" for p, c in expired]
    lines += [f"  expires day {d}: {p} {c}" for p, c, d in soon]
    lines += [f"  authorised persons still valid next month: {len(ap_ok)} of 4 "
              f"({', '.join(ap_ok)})",
              "  four shifts cannot each have one: the renewals are booked",
              "  now, or the roster of next month already has a hole"]
    emit("t_competence", lines)
    return dict(expired=len(expired), soon=len(soon), ap_ok=len(ap_ok))


# ------------------------------------------------ 6. re-declarations
def redeclare(threshold: float = 5.0) -> dict:
    declared = [150] * 24
    actual = [150] * 6 + [138] * 4 + [150] * 3 + [126] * 5 + [150] * 6   # a turbine, then a block
    redecl = {7: 138, 14: 126, 18: 150}           # hour sent: new value
    cur, late, missed = declared[0], [], 0
    for h in range(24):
        if h in redecl:
            cur = redecl[h]
        if abs(actual[h] - cur) > threshold:
            missed += 1
            late.append(h)
    lines = ["available capacity declared to the grid operator vs actual;",
             f"  re-declare within the hour when it moves > {threshold:.0f} MW (teaching)",
             "  turbine out 06-10, PV block out 13-18; re-declarations sent at",
             f"  {', '.join(f'{h:02d}:00' for h in redecl)}",
             f"  hours with the declaration wrong by more than {threshold:.0f} MW: "
             f"{missed} ({', '.join(f'{h:02d}' for h in late)})",
             "  both outages were re-declared an hour late, and the turbine's",
             "  return at 10:00 not at all: in two hours the grid operator",
             "  counted on 12 MW that was not there, in three it planned",
             "  without 12 MW that was - re-declaration is part of the",
             "  outage procedure, not an afterthought"]
    emit("t_redeclare", lines)
    return dict(missed=missed, late=late)


# ------------------------------------------------ 7. ramp warnings
def ramp_warnings(threshold: float = 20.0) -> dict:
    act = s20.poc_actual()
    fc = s20.poc_forecast(3)
    da = np.abs(np.diff(act)) > threshold
    df = np.abs(np.diff(fc)) > threshold
    hits = int(np.sum(da & df))
    misses = int(np.sum(da & ~df))
    false = int(np.sum(~da & df))
    pod = hits / (hits + misses)
    far = false / (hits + false)
    lines = [f"ramp warnings from the 3-h forecast: |change| > {threshold:.0f} MW in an hour",
             f"  actual ramps {hits + misses}, warned {hits}, missed {misses}, false "
             f"warnings {false}",
             f"  probability of detection {pod:.0%}, false-alarm ratio {far:.0%}",
             "  a warning gives the shift time to free battery room or warn",
             "  the grid operator; the miss rate says why the shift still",
             "  watches the plant and not only the forecast (ch 15 ramps)"]
    emit("t_ramps", lines)
    return dict(hits=hits, misses=misses, false=false, pod=pod, far=far)


# ------------------------------------------------ 8. recovery after activations
def recovery(p_mw: float = 5.0, minutes: float = 15.0, p_rec: float = 4.0) -> dict:
    lim = s20.LIMITS
    eta = lim["eta"]
    floor = lim["e_min"] + p_mw / eta
    used = p_mw * minutes / 60 / eta
    t_rec = used / (p_rec * eta) * 60
    after3 = floor - 3 * used
    hours_left = (after3 - lim["e_min"]) * eta / p_mw
    lines = [f"service activation {p_mw} MW for {minutes:.0f} min from the floor "
             f"{floor:.2f} MWh",
             f"  energy drawn {used:.2f} MWh; recovery at {p_rec} MW takes {t_rec:.0f} min",
             f"  three activations without recovery: {after3:.2f} MWh left,",
             f"  enough for {hours_left:.2f} h of the service",
             "  below the one-hour floor, the service is declared reduced",
             "  until the energy is back: recovery is part of the service",
             "  (ch 20 floor), and its minutes are in the shift log"]
    emit("t_recovery", lines)
    return dict(used=used, t_rec=t_rec, after3=after3, hours_left=hours_left)


# ------------------------------------------------ 9. diesel test loads
def diesel_tests(rating_kw: float = 100.0, low: float = 0.30) -> dict:
    load = [12, 15, 60, 10, 14, 70, 13, 12, 65, 11, 16, 62]
    light = [m + 1 for m, x in enumerate(load) if x < low * rating_kw]
    quarters_ok = [q + 1 for q in range(4)
                   if max(load[3 * q:3 * q + 3]) >= 0.5 * rating_kw]
    lines = [f"monthly diesel test runs, load against a {rating_kw:.0f} kW rating (teaching)",
             "  " + " ".join(f"{x:3d}" for x in load) + "  kW",
             f"  {len(light)} runs below {low:.0%} load: unburnt fuel builds up when the",
             "  engine never warms (teaching rule: a loaded run each quarter)",
             f"  quarters with a run at half load or more: {len(quarters_ok)} of 4",
             "  the light runs prove the engine starts; the loaded runs",
             "  prove it carries the station - both are in the record"]
    emit("t_diesel", lines)
    return dict(light=len(light), quarters=len(quarters_ok))


# ------------------------------------------------ 10. station battery capacity
def battery_trend(limit: float = 80.0) -> dict:
    q = np.arange(5)
    cap = np.array([100.0, 99.0, 97.6, 96.6, 95.2])   # capacity test, % of rated
    slope, icpt = np.polyfit(q, cap, 1)
    q_lim = (limit - icpt) / slope
    lines = [f"station battery capacity tests by quarter (% of rated), replace at "
             f"{limit:.0f} %",
             "  quarter " + "  ".join(f"{i:5d}" for i in q),
             "  cap %   " + "  ".join(f"{c:5.1f}" for c in cap),
             f"  slope {slope:.2f} %/quarter: reaches {limit:.0f} % after {q_lim:.1f} "
             f"quarters ({q_lim / 4:.1f} years)",
             "  far short of the design life: a fade this fast points at",
             "  the room temperature (the battery-room fan of ch 50) before",
             "  the battery - the trend is the evidence that finds it"]
    emit("t_battery", lines)
    return dict(slope=slope, years=q_lim / 4)


# ------------------------------------------------ 11. fire false alarms
ALARMS = {   # detector type: (installed, real fires, false alarms in the year)
    "point smoke (buildings)": (300, 1, 14), "aspirating (battery)": (16, 0, 1),
    "heat (transformers)": (40, 0, 0), "flame (substation yard)": (6, 0, 5),
    "manual call points": (60, 0, 3)}


def false_alarms() -> dict:
    rate = {k: f / n * 100 for k, (n, _, f) in ALARMS.items()}
    worst = max(rate, key=rate.get)
    tot = sum(f for *_, f in ALARMS.values())
    lines = ["fire alarms of the first year by detector type"]
    lines += [f"  {k:26s} {n:4d} installed, {r} real, {f:3d} false = "
              f"{rate[k]:5.1f} per 100" for k, (n, r, f) in ALARMS.items()]
    lines += [f"  {tot} false alarms; the worst rate: {worst}",
              "  each false alarm costs a response and teaches people to",
              "  ignore the next one: the investigation found sun glint on",
              "  the yard behind the flame detectors - the remedy is the",
              "  designer's (placement, type),",
              "  recorded as a change, never a disabled detector"]
    emit("t_falsealarms", lines)
    return dict(rate=rate, worst=worst, tot=tot)


# ------------------------------------------------ 12. line rating over the year
def line_amps(t_air, v, ghi, t_c: float = 75.0):
    """Teaching heat balance of the 132 kV conductor (as ch 24) with the sun
    from the hourly irradiance."""
    d, eps, alpha = 0.0245, 0.5, 0.5
    r_ac = 0.10e-3 * (1 + 0.00403 * (t_c - 20))
    p_rad = math.pi * d * eps * 5.67e-8 * ((t_c + 273) ** 4 - (t_air + 273) ** 4)
    h = 3.9 + 8.8 * v ** 0.6 if v > 0 else 3.0
    p_conv = math.pi * d * h * (t_c - t_air)
    p_sun = alpha * d * ghi
    return math.sqrt(max(p_conv + p_rad - p_sun, 0) / r_ac)


def line_rating(shear: float = (12 / 60) ** 0.143) -> dict:
    h = datapack.load_hourly()
    t = h["t_air_c"].to_numpy(float)
    v = h["ws_60m_ms"].to_numpy(float) * shear
    g = h["ghi_wm2"].to_numpy(float)
    p = s20.poc_actual()
    amps = np.array([line_amps(a, b, c) for a, b, c in zip(t, v, g)])
    i = p * 1e6 / (math.sqrt(3) * 132e3)
    over = i > amps
    lost = float(np.sum(np.clip(p - amps * math.sqrt(3) * 132e3 / 1e6, 0, None)[over]))
    k = int(amps.argmin())
    both = int(np.sum((t > 35) & (v < 0.74)))
    lines = ["132 kV line: weather-dependent rating over the data-pack year",
             f"  wind at conductor height = 60 m wind x {shear:.2f} (teaching shear)",
             f"  lowest rating {amps.min():.0f} A ({t[k]:.1f} C, {v[k]:.2f} m/s, "
             f"{g[k]:.0f} W/m2); below 437 A: {int(np.sum(amps < 437))} h",
             f"  hours when the export current exceeded the rating: {int(over.sum())}, "
             f"{lost:.1f} MWh",
             f"  hottest hour {t.max():.1f} C; hours above 35 C with wind below "
             f"0.74 m/s: {both}",
             "  ch 24's hot, still day is a design case the data year never",
             f"  reached: the margin was {amps.min() - 437:.0f} A at its smallest. A hotter",
             "  year can still reach it, so the procedure keeps a rating",
             "  for stated weather and asks the network owner for a",
             "  dynamic rating (U-132)"]
    emit("t_linerating", lines)
    return dict(min=float(amps.min()), below=int(np.sum(amps < 437)),
                over=int(over.sum()), lost=lost, tmax=float(t.max()), both=both)


# ------------------------------------------------ 13. community notice of works
WORKS_NOTICE = [   # work affecting neighbours, days of notice given
    ("blade inspection with a crane at T06", 10), ("line vegetation T05-T08", 3),
    ("wash campaign block 2 (trucks)", 7), ("night transformer move", 1),
    ("road grading to the village", 9)]


def notice(required: int = 7) -> list:
    short = [(w, d) for w, d in WORKS_NOTICE if d < required]
    lines = [f"planned works that touch neighbours: notice against the {required}-day "
             "commitment"]
    lines += [f"  {w:38s} {d:3d} days" + ("  SHORT" if d < required else "")
              for w, d in WORKS_NOTICE]
    lines += [f"  {len(short)} short: the vegetation work waited for an outage window",
              "  and the transformer move for a road permit - the notice",
              "  belongs in the outage request, so the date and the message",
              "  move together"]
    emit("t_notice", lines)
    return short


# ------------------------------------------------ 14. spares count
SPARES = {   # item: (register, counted, unit value k u)
    "IGBT stack PCI-5500": (2, 2, 48.0), "pitch motor": (3, 2, 9.5),
    "33 kV cable joint kit": (6, 6, 1.2), "yaw brake pads (set)": (10, 14, 0.4),
    "module PVM-550": (120, 104, 0.12), "SCADA switch": (4, 3, 2.1),
    "battery module": (8, 8, 6.0)}


def spares() -> dict:
    diff = {k: (c - r, (c - r) * v) for k, (r, c, v) in SPARES.items() if c != r}
    lines = ["spares: register against a physical count at the end of the year"]
    lines += [f"  {k:24s} register {r:4d}  counted {c:4d}"
              + (f"  {c - r:+d}" if c != r else "") for k, (r, c, _) in SPARES.items()]
    short_val = -sum(v for _, v in diff.values() if v < 0)
    lines += [f"  {len(diff)} lines differ; missing value {short_val:.1f} k u",
              "  the pitch motor and the switch were used and not booked out:",
              "  the work orders exist, the store transactions do not - the",
              "  register thinks the spare is there on the night it is needed"]
    emit("t_spares", lines)
    return dict(diff=len(diff), short=short_val)


# ------------------------------------------------ 15. emergency contacts
CONTACTS = {"fire service": date(2029, 5, 2), "ambulance base": date(2029, 1, 15),
            "grid operator control": date(2029, 5, 20), "network owner duty": None,
            "village representative": date(2028, 12, 1), "hospital": date(2029, 4, 9),
            "turbine maker hotline": date(2029, 2, 27), "police": date(2029, 5, 28)}


def contacts(max_days: int = 90) -> list:
    old = operations.stale(CONTACTS, src.TODAY, max_days)
    lines = [f"emergency contact list on {src.TODAY}: numbers called to check within "
             f"{max_days} days"]
    lines += [f"  {k:24s} {d if d else 'never checked'}" + ("  STALE" if k in old else "")
              for k, d in CONTACTS.items()]
    lines += [f"  {len(old)} stale; the network owner's duty number was never",
              "  checked - it is the one a line fault needs first"]
    emit("t_contacts", lines)
    return old


if __name__ == "__main__":
    staffing()
    limits_register()
    soc_drift()
    q_following()
    competence()
    redeclare()
    ramp_warnings()
    recovery()
    diesel_tests()
    battery_trend()
    false_alarms()
    line_rating()
    notice()
    spares()
    contacts()
