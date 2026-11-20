"""Chapter 52, round t: the maintenance budget, opportunistic work while a
turbine is down, module hot spots, transformer radiators, SF6 density,
battery cell spread, turbine yaw error, causes ranked from an alarm's
history, cold standby against active redundancy, an availability
interval from a short record, weather as a common cause, the day for a
transformer outage, soiling-station triggers, locating a cable fault, an
asset-register field audit, and tag naming.

Run from the project root:   python -m companion.ch52.examples_t
Writes companion/ch52/expected/t_*.txt. Teaching values (A-530 to A-537).
"""
from __future__ import annotations

import math
import re

import numpy as np

from companion.ch15 import sources as s15
from companion.ch52.common import emit


# ------------------------------------------------ 1. maintenance budget
def budget(mw: float = 110.0) -> dict:   # 60 MW wind + 50 MW PV (AC)
    items = {"own crew (10 x 52 k u)": 520.0, "turbine service agreement": 1_380.0,
             "parts and consumables": 410.0, "HV contractor": 102.0,
             "cleaning (16 campaigns)": 106.0, "tools, software, training": 95.0}
    tot = sum(items.values())
    lines = [f"maintenance budget of a year (k u, teaching) for {mw:.0f} MW"]
    lines += [f"  {k:30s} {v:7,.0f}  {v / tot:4.0%}" for k, v in items.items()]
    lines += [f"  total {tot:,.0f} k u = {tot / mw:.1f} k u per MW a year",
              f"  the turbine agreement is {items['turbine service agreement'] / tot:.0%}: its terms",
              "  (response, availability guarantee, parts) are the largest",
              "  maintenance decision of the plant (ch 39, U-133)"]
    emit("t_budget", lines)
    return dict(tot=tot, per_mw=tot / mw)


# ------------------------------------------------ 2. opportunistic maintenance
def opportunistic(tasks_h: float = 6.0, stops: int = 9, mw: float = 1.87) -> dict:
    saved_stops = stops
    saved_mwh = saved_stops * tasks_h * mw
    lines = [f"turbine tasks due within a month done during an unplanned stop: {stops} stops",
             f"  each saves a separate {tasks_h:.0f} h stop later: {saved_mwh:.0f} MWh a year",
             "  (mean turbine output 1.87 MW); the rule needs the due tasks",
             "  listed per turbine and the parts in the van - the CMMS",
             "  shows them on the corrective order (lesson I)"]
    emit("t_opport", lines)
    return dict(mwh=saved_mwh)


# ------------------------------------------------ 3. module hot spots
def hotspots() -> dict:
    dt = np.array([4, 6, 12, 25, 8, 31, 5, 15, 9, 41, 7, 11, 22, 3, 18])   # K over neighbours
    classes = {"observe (< 10 K)": dt < 10, "check at next visit (10-20 K)": (dt >= 10) & (dt < 20),
               "replace (>= 20 K)": dt >= 20}
    lines = ["hot spots found by the thermography flight, 15 modules (K over neighbours)",
             "  " + " ".join(f"{x:2d}" for x in dt)]
    lines += [f"  {k:30s} {int(v.sum())}" for k, v in classes.items()]
    lines += ["  teaching classes - the survey and its classification follow",
              "  the project's thermography procedure (ch 41, STD-068); a",
              "  module over the replace class goes to the warranty claim",
              "  with its image"]
    emit("t_hotspots", lines)
    return {k: int(v.sum()) for k, v in classes.items()}


# ------------------------------------------------ 4. transformer radiators
def radiators() -> dict:
    load = np.array([0.55, 0.62, 0.70, 0.75, 0.80, 0.85])
    rise_clean = 8.0 + 38.0 * load ** 1.6                       # K top oil over ambient
    rise_now = rise_clean * 1.12                                # dusty radiators
    excess = rise_now - rise_clean
    lines = ["main transformer T1: top-oil rise over ambient (K) at the same loads,",
             "  model of the clean unit (heat run, ch 43) against this summer",
             "  load pu   clean   now   excess"]
    lines += [f"  {l:7.2f} {c:7.1f} {n:5.1f} {e:7.1f}" for l, c, n, e in
              zip(load, rise_clean, rise_now, excess)]
    lines += [f"  {excess[-1]:.1f} K more at 0.85 pu: dust on the radiators - washed in",
              "  the next outage; a residual against the model finds it, a",
              "  fixed alarm level on top-oil temperature would not"]
    emit("t_radiators", lines)
    return dict(excess=float(excess[-1]))


# ------------------------------------------------ 5. SF6 density
def sf6(alarm: float = 0.62, now: float = 0.66) -> dict:
    months = np.arange(8)
    d = now + 0.0 - 0.0035 * months + np.array([0, .001, -.001, 0, .001, 0, -.001, 0])
    slope = float(np.polyfit(months, d, 1)[0])
    to_alarm = (alarm - d[-1]) / slope
    lines = ["33 kV breaker WS2: gas density (MPa, temperature-compensated),",
             f"  monthly; alarm {alarm}",
             "  " + " ".join(f"{x:.3f}" for x in d),
             f"  falling {-slope * 1000:.1f} kPa a month: alarm in about {to_alarm:.0f} months",
             "  a slow leak found by the trend, not by the alarm: the repair",
             "  is planned with the maker (gas handling by certified people,",
             "  ch 25, ch 46) before the breaker is blocked"]
    emit("t_sf6", lines)
    return dict(slope=slope, months=to_alarm)


# ------------------------------------------------ 6. battery cell spread
def cell_spread() -> dict:
    spread = [18, 19, 21, 22, 26, 31]            # mV, max-min in a rack at rest, by month
    lines = ["BESS-A rack 7: cell voltage spread at rest (mV), monthly",
             "  " + " ".join(f"{x:3d}" for x in spread),
             f"  up {spread[-1] - spread[0]} mV in five months, faster lately: balancing is",
             "  losing - the BMS log of balancing duty (ch 45) tells a weak",
             "  cell from a weak balancer before the rack is derated"]
    emit("t_cells", lines)
    return dict(rise=spread[-1] - spread[0])


# ------------------------------------------------ 7. yaw error
def yaw(err_deg: float = 6.0, aep: float = 16_100.0) -> dict:
    loss = 1 - math.cos(math.radians(err_deg)) ** 2           # teaching cos^2 rule
    lines = [f"T09: nacelle {err_deg:.0f} deg off the wind (from SCADA power against "
             "direction bins)",
             f"  teaching loss 1 - cos^2: {loss:.1%} of {aep:,.0f} MWh = {loss * aep:.0f} MWh a year",
             "  the vane offset after a sensor change (ch 13 vane offset):",
             "  realigned and verified by the same SCADA test - small per",
             "  turbine, but invisible without it"]
    emit("t_yaw", lines)
    return dict(loss=loss, mwh=loss * aep)


# ------------------------------------------------ 8. causes ranked from history
def causes() -> dict:
    hist = {"fan failed": 11, "filter blocked": 7, "sensor fault": 4, "coolant pump": 2,
            "IGBT stack": 1}                         # causes found after 'over-temperature'
    tot = sum(hist.values())
    lines = [f"inverter alarm 'over-temperature': causes found in {tot} past orders"]
    lines += [f"  {k:16s} {v:3d}  P = {v / tot:.2f}" for k, v in
              sorted(hist.items(), key=lambda kv: -kv[1])]
    lines += ["  the technician checks the fan and the filter first (72 % of",
              "  past cases) and takes those parts; the history exists only",
              "  if each order records the cause found (lesson I)"]
    emit("t_causes", lines)
    return dict(top=max(hist, key=hist.get), share2=(11 + 7) / tot)


# ------------------------------------------------ 9. cold standby vs active
def standby(lam_yr: float = 0.5, t_h: float = 24.0 * 30) -> dict:
    lt = lam_yr / 8760 * t_h
    single = math.exp(-lt)
    active = 1 - (1 - single) ** 2
    cold = math.exp(-lt) * (1 + lt)
    lines = [f"two auxiliary units for a month (each {lam_yr} failures a year when running)",
             f"  one unit {single:.5f}; two running in parallel {active:.6f};",
             f"  one running, one cold standby (perfect switch) {cold:.6f}",
             "  the standby wins on paper because it does not age while it",
             "  waits - and loses in practice if its start is never tested:",
             "  the diesel test of ch 51 is the switch in this formula"]
    emit("t_standby", lines)
    return dict(active=active, cold=cold)


# ------------------------------------------------ 10. availability interval from a short record
def bootstrap(seed: int = 527, n: int = 4000) -> dict:
    down = np.array([46, 18, 70, 9, 4, 26, 31, 22], float)    # ch 51 outages, h
    rng = np.random.default_rng(seed)
    hours = 8760.0 * 12                                         # fleet hours (teaching)
    a = 1 - down.sum() / hours
    boot = [1 - rng.choice(down, down.size).sum() / hours for _ in range(n)]
    lo, hi = np.percentile(boot, [5, 95])
    lines = [f"fleet availability from {down.size} outages in a year: {a:.4f}",
             f"  bootstrap 90 % interval {lo:.4f} to {hi:.4f}",
             "  the interval is wider than the gap between many targets and",
             "  results: one year of eight outages cannot show a 0.1 point",
             "  difference - the contract test needs years, or a margin"]
    emit("t_boot", lines)
    return dict(a=a, lo=float(lo), hi=float(hi))


# ------------------------------------------------ 11. weather as a common cause
def hail(p_storm: float = 0.02, blocks_hit: int = 4, days_out: float = 20.0) -> dict:
    block_mwh_day = 300.0 / 10
    exp_loss = p_storm * blocks_hit * days_out * block_mwh_day
    lines = [f"a hail storm (teaching {p_storm:.0%} a year) damages {blocks_hit} PV blocks at once,",
             f"  {days_out:.0f} days to re-module: expected {exp_loss:.0f} MWh a year",
             f"  but {blocks_hit * days_out * block_mwh_day:,.0f} MWh in the year it happens",
             "  - no beta factor between blocks describes it: weather is its",
             "  own event in the tree, with insurance and module stock as",
             "  its remedies (ch 53 resilience)"]
    emit("t_hail", lines)
    return dict(exp=exp_loss, event=blocks_hit * days_out * block_mwh_day)


# ------------------------------------------------ 12. the day for a transformer outage
def trafo_day(hours: int = 24, cap: float = 63.0) -> dict:
    poc = np.asarray(s15.plant_year()["poc"], float)
    over = np.clip(poc - cap, 0, None)
    daily = over[: 365 * 24].reshape(365, 24).sum(axis=1)
    zero = int(np.sum(daily == 0))
    best = int(np.argmin(daily))
    worst = int(np.argmax(daily))
    q = [int(np.sum(daily[k * 91:(k + 1) * 91] == 0)) for k in range(4)]
    lines = [f"one main transformer out for {hours} h: energy lost = output above {cap:.0f} MW",
             f"  days of the data year with nothing above {cap:.0f} MW: {zero}",
             f"  by quarter: {', '.join(map(str, q))}",
             f"  worst day {worst}: {daily[worst]:.0f} MWh; mean day {daily.mean():.0f} MWh",
             f"  {'every' if min(q) > 0 else 'not every'} quarter has days with no loss: "
             "the outage is",
             "  planned on the forecast (ch 51 window), not on the calendar"]
    emit("t_trafoday", lines)
    return dict(zero=zero, worst=float(daily[worst]), mean=float(daily.mean()), best=best,
                q=q)


# ------------------------------------------------ 13. soiling-station triggers
def soiling_triggers(trigger: float = 0.97, seed: int = 528) -> dict:
    rng = np.random.default_rng(seed)
    sr, ratio, washes = 1.0, [], []
    for d in range(365):
        sr -= 0.0012 + (0.03 if rng.random() < 0.02 else 0.0)    # daily rate + storms
        if rng.random() < 0.04:
            sr = min(1.0, sr + 0.02)                               # rain
        if sr < trigger:
            washes.append(d)
            sr = 0.995
        ratio.append(sr)
    lines = [f"soiling station: ratio over the year, wash when it falls below {trigger}",
             f"  washes triggered: {len(washes)}; mean ratio {np.mean(ratio):.3f}",
             f"  shortest gap {min(np.diff(washes))} day(s), longest {max(np.diff(washes))} days",
             "  storms bring the trigger early, rain postpones it: the",
             "  measured trigger (ch 10) spaces washes as the weather does,",
             "  where a fixed 23-day calendar would not; a one-day gap (a",
             "  storm right after a wash) shows the rule also needs a",
             "  minimum interval or a look at the dust forecast"]
    emit("t_soilstation", lines)
    return dict(n=len(washes), mean=float(np.mean(ratio)),
                gmin=int(min(np.diff(washes))), gmax=int(max(np.diff(washes))))


# ------------------------------------------------ 14. locating a cable fault
def cable_fault(km: float = 4.5) -> dict:
    methods = {"sectionalise at joints and re-test": 26.0, "TDR from the end, then walk": 9.0,
               "TDR plus acoustic pinpointing": 5.0}           # hours to locate
    lines = [f"33 kV collector fault on a {km} km feeder: hours to locate (teaching)"]
    lines += [f"  {k:36s} {v:4.0f} h" for k, v in methods.items()]
    lines += ["  the location equipment and a trained contractor are part of",
              "  the spares plan; locating, not repairing, decided the 120 h",
              "  of ch 18 - measurements by qualified people under a permit"]
    emit("t_cablefault", lines)
    return methods


# ------------------------------------------------ 15. asset-register field audit
def field_audit(n: int = 50, wrong: int = 7) -> dict:
    p = wrong / n
    z = 1.96
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    lines = [f"asset register checked in the field: {n} assets, nameplate against register",
             f"  {wrong} differ ({p:.0%}); 95 % interval {c - h:.0%} to {c + h:.0%} (Wilson, ch 51)",
             "  serial numbers changed by repairs that never reached the",
             "  register: each one breaks a warranty claim and a failure",
             "  history - the fix is the change step in every work order"]
    emit("t_register", lines)
    return dict(p=p, lo=c - h, hi=c + h)


# ------------------------------------------------ 16. tag naming
def naming() -> dict:
    tags = ["=PVF2-3-INV", "=PVF2-3-CB01", "=WT03-GBX", "WT07_GBX", "=BESS-A-PCS1",
            "=PVF2-3-cb02", "=WT11-YAW", "=SUB-T1", "=PVF1-1-INV-", "=BESS-A-C2"]
    rule = re.compile(r"^=[A-Z0-9]+(-[A-Z0-9]+)*$")
    bad = [t for t in tags if not rule.match(t)]
    lines = ["asset IDs against the naming rule (ch 23 reference designations)"]
    lines += [f"  {t:15s} {'ok' if t not in bad else 'BREAKS THE RULE'}" for t in tags]
    lines += [f"  {len(bad)} of {len(tags)} break it: a lower-case letter, an underscore,",
              "  a trailing dash - each makes a second asset that the",
              "  history of the first never reaches"]
    emit("t_naming", lines)
    return dict(bad=bad)


if __name__ == "__main__":
    budget()
    opportunistic()
    hotspots()
    radiators()
    sf6()
    cell_spread()
    yaw()
    causes()
    standby()
    bootstrap()
    hail()
    trafo_day()
    soiling_triggers()
    cable_fault()
    field_audit()
    naming()
