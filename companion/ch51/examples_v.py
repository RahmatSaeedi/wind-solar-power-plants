"""Chapter 51, round v: overrides and temporary changes, PV tracker stow in
high wind, inverter trips by cause, investigations and their actions, a
curtailment compensation claim, a forecast-feed outage, UPS battery life
in a warm room, hot-work permits and fire watch, the well level against
the drought trigger, protection operations reviewed, truck speeds near
the village, asset criticality, heat-stress hours of the day shift, and
the service payment curve.

Run from the project root:   python -m companion.ch51.examples_v
Writes companion/ch51/expected/v_*.txt and diagrams/data/ch51-heat.csv,
ch51-payment.csv. Teaching values (A-522 to A-529).
"""
from __future__ import annotations

import numpy as np

from companion.ch15 import sources as s15
from companion.ch20 import sources as s20
from companion.ch51.common import csv, emit
from plantp import control, datapack


# ------------------------------------------------ 1. overrides and temporary changes
OVERRIDES = [   # item, days open, approved by the shift lead and engineer?
    ("alarm inhibit T07 pitch battery", 41, True), ("forced value PVF2 irradiance", 3, True),
    ("bypass: BESS-A door switch", 19, False), ("alarm inhibit SST fan", 76, True),
    ("temporary jumper in WS3 panel", 12, False), ("PPC Q limit 30.6 Mvar", 120, True)]


def overrides(max_days: int = 14) -> dict:
    old = [(i, d) for i, d, _ in OVERRIDES if d > max_days]
    unapp = [i for i, _, a in OVERRIDES if not a]
    lines = [f"overrides and temporary changes open on the last day (review after "
             f"{max_days} days)"]
    lines += [f"  {i:34s} {d:4d} days  " + ("approved" if a else "NOT APPROVED")
              for i, d, a in OVERRIDES]
    lines += [f"  {len(old)} older than {max_days} days, {len(unapp)} never approved: a",
              "  bypassed door switch is a battery safety function out of",
              "  service - an impairment with its own permit; the Q limit is",
              "  not temporary at all and belongs in the limit register",
              "  (round t) and the deviation DEV-11"]
    emit("v_overrides", lines)
    return dict(old=len(old), unapp=len(unapp))


# ------------------------------------------------ 2. tracker stow
def stow(gust_limit: float = 15.0, gust_factor: float = 1.4, loss: float = 0.25) -> dict:
    h = datapack.load_hourly()
    v10 = h["ws_60m_ms"].to_numpy(float) * (10 / 60) ** 0.143
    pv = s15.plant_year()["pv_av"]
    stow_h = (v10 * gust_factor >= gust_limit) & (pv > 0)
    lost = float(np.sum(pv[stow_h]) * loss)
    lines = [f"PV trackers stow when the expected gust reaches {gust_limit:.0f} m/s "
             f"(mean x {gust_factor}, teaching)",
             f"  daylight hours in stow over the data-pack year: {int(stow_h.sum())}",
             f"  PV energy in those hours {np.sum(pv[stow_h]):,.0f} MWh; lost at "
             f"{loss:.0%}: {lost:,.0f} MWh",
             f"  = {lost / np.sum(pv):.2%} of the PV year: stow protects the",
             "  trackers for a small price, and its hours are logged with the",
             "  wind that caused them (lost-energy cause 'stow', lesson B)"]
    emit("v_stow", lines)
    return dict(hours=int(stow_h.sum()), lost=lost, share=lost / float(np.sum(pv)))


# ------------------------------------------------ 3. inverter trips by cause
TRIPS = {"DC insulation fault (morning dew)": 37, "grid over-voltage": 22,
         "fan / over-temperature": 18, "communication watchdog": 9,
         "IGBT stack fault": 3, "unknown": 11}


def trips() -> dict:
    tot = sum(TRIPS.values())
    order = sorted(TRIPS.items(), key=lambda kv: -kv[1])
    cum = 0
    lines = [f"PV inverter trips of the first year by cause ({tot} trips)"]
    for k, n in order:
        cum += n
        lines.append(f"  {k:36s} {n:3d}  cumulative {cum / tot:4.0%}")
    top2 = (order[0][1] + order[1][1]) / tot
    lines += [f"  the two largest causes are {top2:.0%} of the trips: dew on the DC",
              "  side every winter morning and over-voltage on light-load",
              "  afternoons - one for the maintainer, one for the grid study",
              "  (ch 28 voltage); 'unknown' is the share to shrink first"]
    emit("v_trips", lines)
    return dict(tot=tot, top2=top2, unknown=TRIPS["unknown"])


# ------------------------------------------------ 4. investigations and actions
def investigations(limit: int = 30) -> dict:
    inv = [("near miss: crane over live line route", 12, 3, 3),
           ("trip of WS2 on a wrong setting", 41, 4, 2),
           ("first-aid case: heat", 9, 2, 2),
           ("BESS container door found open", 33, 3, 1),
           ("diesel failed to start in test", 25, 2, 0)]   # days to close, actions, closed
    late = [i for i, d, *_ in inv if d > limit]
    acts = sum(a for *_, a, _ in inv)
    done = sum(c for *_, c in inv)
    lines = [f"incident investigations: days to the report (target {limit}) and actions"]
    lines += [f"  {i:38s} {d:3d} d  actions {a}, closed {c}" for i, d, a, c in inv]
    lines += [f"  {len(late)} late; actions closed {done} of {acts} ({done / acts:.0%})",
              "  a report on time with its actions open has not yet changed",
              "  anything: the register tracks actions to their evidence",
              "  (ch 32 lessons), not reports to their date"]
    emit("v_investig", lines)
    return dict(late=len(late), acts=acts, done=done)


# ------------------------------------------------ 5. curtailment compensation
def compensation(price: float = 70.0) -> dict:
    cls = {"grid operator, security of supply": (166.0, True),
           "grid operator, planned works": (42.0, False),
           "plant, export-limit margin": (18.0, False)}
    claim = sum(e for e, c in cls.values() if c) * price
    lines = [f"curtailment compensation under the teaching contract ({price:.0f} u/MWh)"]
    lines += [f"  {k:36s} {e:5.0f} MWh  " + ("compensated" if c else "not compensated")
              for k, (e, c) in cls.items()]
    lines += [f"  claim {claim:,.0f} u; its evidence: each instruction with its time",
              "  (round s repeat-back), the energy the plant could have given",
              "  in those hours (availability x resource, not the schedule),",
              "  and the meter - the rules are the contract's, verified",
              "  locally"]
    emit("v_compensation", lines)
    return dict(claim=claim)


# ------------------------------------------------ 6. forecast-feed outage
def feed_outage(start_day: int = 150, days: int = 3) -> dict:
    act = np.minimum(s20.poc_actual(), 100.0)
    fc = np.minimum(s20.poc_forecast(24), 100.0)
    h0, h1 = start_day * 24, (start_day + days) * 24
    pers = act[h0 - 24:h1 - 24]
    sh, lo = s20.IMBALANCE["short"], s20.IMBALANCE["long"]
    c_fc = control.imbalance(fc[h0:h1], act[h0:h1], sh, lo)
    c_p = control.imbalance(pers, act[h0:h1], sh, lo)
    lines = [f"forecast feed lost for {days} days from day {start_day}: the schedule falls "
             "back",
             "  to 24-hour persistence (yesterday's output, hour by hour)",
             f"  imbalance with the forecast {c_fc:,.0f} u; with persistence {c_p:,.0f} u",
             f"  the outage cost {c_p - c_fc:+,.0f} u - the fallback is written down",
             "  and tested before the feed fails, and the shift log names",
             "  the hours it was used (lesson A, the schedule deadline)"]
    emit("v_feed", lines)
    return dict(fc=c_fc, pers=c_p)


# ------------------------------------------------ 7. UPS battery life in a warm room
def ups_life(ref: float = 20.0) -> dict:
    room = [21, 22, 24, 27, 30, 33, 35, 34, 30, 26, 23, 21]     # monthly mean C
    rate = [2 ** ((t - ref) / 10) for t in room]
    used = sum(rate) / 12
    lines = ["UPS battery room by month (C); life is used at twice the rate",
             f"  for each 10 K over {ref:.0f} C",
             "  " + " ".join(f"{t:3d}" for t in room),
             f"  life used in the year: {used:.2f} design years",
             f"  a 10-year battery lasts about {10 / used:.1f} years in this room: the",
             "  fan fault of ch 50 is not a comfort issue but a battery",
             "  replacement brought forward (teaching halving rule)"]
    emit("v_upslife", lines)
    return dict(used=used, years=10 / used)


# ------------------------------------------------ 8. hot-work permits
def hot_work() -> dict:
    permits = [(True, True), (True, True), (True, False), (True, True), (False, True),
               (True, True), (True, False), (True, True), (True, True), (True, True)]
    # (fire watch recorded, final check 60 min after recorded)
    no_watch = sum(1 for w, _ in permits if not w)
    no_final = sum(1 for _, f in permits if not f)
    lines = [f"hot-work permits of a quarter: {len(permits)}",
             f"  without a fire watch recorded: {no_watch}; without the final check: "
             f"{no_final}",
             "  hot work near cable trenches and transformers is a fire",
             "  source the site creates itself: the permit is closed only",
             "  with both records (ch 32 permits, no universal prescription",
             "  of times - the site's fire strategy sets them)"]
    emit("v_hotwork", lines)
    return dict(no_watch=no_watch, no_final=no_final)


# ------------------------------------------------ 9. well level and drought trigger
def well(trigger: float = 62.0) -> dict:
    months = np.arange(12)
    level = np.array([48.2, 48.6, 49.1, 49.9, 50.8, 51.6, 52.5, 53.1, 53.4, 53.6,
                      53.9, 54.5])                       # m below ground
    slope = float(np.polyfit(months, level, 1)[0])
    months_left = (trigger - level[-1]) / slope
    lines = ["production well W-1: water level by month (m below ground),",
             f"  drought trigger {trigger:.0f} m",
             "  " + " ".join(f"{x:4.1f}" for x in level),
             f"  falling {slope:.2f} m a month on average: trigger in about "
             f"{months_left:.0f} months",
             "  the drought plan (ch 33) acts before the trigger: washing",
             "  by measured benefit only (lesson H) and tankers booked"]
    emit("v_well", lines)
    return dict(slope=slope, months=months_left)


# ------------------------------------------------ 10. protection operations
def protection_ops() -> dict:
    ops = {"correct (fault cleared by the right relay)": 14,
           "unwanted (no fault, or not its zone)": 3,
           "failed to operate (backup cleared)": 1}
    tot = sum(ops.values())
    lines = [f"protection operations of the first year reviewed: {tot}"]
    lines += [f"  {k:44s} {n:3d}" for k, n in ops.items()]
    lines += [f"  dependability {ops['correct (fault cleared by the right relay)'] / (tot - 3):.0%} "
              "of operations on a fault;",
              f"  {ops['unwanted (no fault, or not its zone)']} unwanted trips, each "
              "investigated with its",
              "  settings file and event record (ch 26); the failure to",
              "  operate is the most serious - a relay that did not see",
              "  its fault is retested before it is trusted again"]
    emit("v_protops", lines)
    return dict(tot=tot, dep=ops["correct (fault cleared by the right relay)"] / (tot - 3))


# ------------------------------------------------ 11. truck speeds near the village
def speeds(limit: float = 30.0, seed: int = 61) -> dict:
    rng = np.random.default_rng(seed)
    v = np.concatenate([rng.normal(27, 4, 140), rng.normal(36, 3, 20)])   # washing trucks last
    over = float(np.mean(v > limit))
    n_over = int(np.sum(v > limit))
    n_new = int(np.sum(v[140:] > limit))
    lines = [f"truck speeds past the village school (GPS logs, limit {limit:.0f} km/h)",
             f"  {v.size} passes; over the limit {over:.0%}; 85th percentile "
             f"{np.percentile(v, 85):.0f} km/h",
             f"  of the {n_over} passes over the limit, {n_new} are the washing",
             f"  contractor's new drivers ({n_new} of their 20 passes) and "
             f"{n_over - n_new} the",
             "  regular trucks: a briefing for the new crew alone would not",
             "  fix it - the speed log goes to every contractor each week,",
             "  and the commitment to the village (ch 33) is reported with it"]
    emit("v_speeds", lines)
    return dict(over=over, p85=float(np.percentile(v, 85)), n_over=n_over, n_new=n_new)


# ------------------------------------------------ 12. asset criticality
ASSETS = {   # asset: (consequence 1-5, likelihood 1-5)
    "main transformer T1": (5, 2), "132 kV line": (5, 2), "PPC": (5, 1),
    "turbine gearbox (each)": (3, 3), "PV inverter (each)": (2, 4),
    "BESS PCS (each)": (3, 2), "SCADA server": (4, 2), "fire pump": (4, 2)}


def criticality() -> list:
    rank = sorted(ASSETS.items(), key=lambda kv: (-kv[1][0] * kv[1][1], -kv[1][0]))
    lines = ["asset criticality = consequence x likelihood (1-5 each, teaching)"]
    lines += [f"  {k:24s} {c} x {p} = {c * p:2d}" for k, (c, p) in rank]
    lines += ["  the ranking decides spares, inspection intervals and who",
              "  gets the maintainer first; ties are broken by consequence -",
              "  ch 52 builds the maintenance plan from it"]
    emit("v_critical", lines)
    return [k for k, _ in rank]


# ------------------------------------------------ 13. heat-stress hours
def heat(threshold: float = 35.0) -> dict:
    h = datapack.load_hourly()
    t = h["t_air_c"].to_numpy(float)
    hr = np.arange(t.size) % 24
    day = (hr >= 7) & (hr < 19)
    by_hour = [int(np.sum((t >= threshold) & (hr == k))) for k in range(24)]
    csv("ch51-heat.csv", "hour,hours", [(k, n) for k, n in enumerate(by_hour)])
    peak = int(np.argmax(by_hour))
    lines = [f"hours at or above {threshold:.0f} C in the data-pack year, by hour of day",
             f"  on the day shift (07-19): {int(np.sum((t >= threshold) & day))}; peak "
             f"hour {peak:02d}:00 with {by_hour[peak]}",
             f"  at or above 38 C on the day shift: {int(np.sum((t >= 38) & day))}",
             "  the work-rest plan of ch 32 is set by these hours: heavy",
             "  outdoor work moves to the morning, and the shift log records",
             "  the breaks (dry-bulb only here; the site plan uses the",
             "  heat index its authority accepts)"]
    emit("v_heat", lines)
    return dict(day=int(np.sum((t >= threshold) & day)), peak=peak,
                h38=int(np.sum((t >= 38) & day)))


# ------------------------------------------------ 14. payment curve data
def payment_curve(lo: float = 0.85) -> None:
    target = s20.SERVICE["availability"]
    rows = [(round(a, 3), round(min(1, max(0, (a - lo) / (target - lo))), 3))
            for a in np.arange(0.80, 1.0001, 0.005)]
    csv("ch51-payment.csv", "a,factor", rows)


if __name__ == "__main__":
    overrides()
    stow()
    trips()
    investigations()
    compensation()
    feed_outage()
    ups_life()
    hot_work()
    well()
    protection_ops()
    speeds()
    criticality()
    heat()
    payment_curve()
