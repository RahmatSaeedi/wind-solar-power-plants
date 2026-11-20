"""Chapter 44, round s: deeper lessons - coolant warming along the cold
plate and swapped hoses, one blocked plate among four, sensor calibration
across the fleet, a staged firmware rollout, torque marks against a torque
audit, the test bench as the factory's bottleneck, floor-life tracking of
moisture-sensitive parts, spares and downtime from the product tree, an
ESR guard band at incoming inspection, MPPT step size, transition coverage
of the state machine, ESD energy, and burn-in of boards.

Run from the project root:   python -m companion.ch44.examples_s
Writes companion/ch44/expected/s_*.txt.
Teaching values (A-466 to A-472); no process recipes, nothing deployable.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch44 import examples_a as ea
from companion.ch44 import lab_d
from companion.ch44 import sources as src
from companion.ch44.common import emit
from plantp import convmfg as cm
from plantp import mppt
from plantp import pe

S, I = src.STACKUP, src.INVERTER
R_PATH = S["r_jc"] + cm.tim_r(S["tim_um"], S["tim_k"], S["tim_area_cm2"]) + S["r_hs"]


# ------------------------------------------------ 1. coolant along the plate
def plate(flow_kg_s: float = 0.975, cp: float = 3600.0, rows: int = 6):
    """Coolant warms row by row; T1/T4 modules sit in the upstream rows."""
    q = I["loss_stack_kw"] * 1000
    rise = q / (flow_kg_s * cp)
    t_row = [I["coolant_c"] + rise * (k + 0.5) / rows for k in range(rows)]
    p_out, p_in = S["p_module_w"], 772.0 / 2              # T1/T4 and T2/T3
    up = np.mean([t + p_out * R_PATH for t in t_row[:3]])
    down = np.mean([t + p_out * R_PATH for t in t_row[3:]])
    life = pe.relative_cycle_life(down - I["coolant_c"], up - I["coolant_c"])
    lines = [f"one stack's cold plate: {q / 1000:.1f} kW into {flow_kg_s} kg/s of "
             f"glycol (cp {cp / 1000:.1f} kJ/kg K)",
             f"  coolant rises {rise:.1f} K from inlet to outlet over {rows} rows",
             "  row:   " + "  ".join(f"{t:5.1f}" for t in t_row) + "  C",
             f"  outer-switch modules upstream (rows 1-3): mean Tj {up:.1f} C",
             f"  hoses swapped, the same modules downstream: mean Tj {down:.1f} C",
             f"  swing {up - I['coolant_c']:.1f} -> {down - I['coolant_c']:.1f} K: "
             f"cycle life x {life:.2f}",
             "  the layout puts the hottest devices where the coolant is",
             "  coldest; arrows on the plate and keyed hose fittings keep the",
             "  factory from undoing it, and the flow direction is a check",
             f"  (inner modules carry {p_in:.0f} W and sit downstream)"]
    emit("s_plate", lines)
    return dict(rise=rise, up=up, down=down, life=life)


# ------------------------------------------------ 2. one blocked plate
def blocked(k_factor: float = 2.0, flow_total: float = 3.9, plates: int = 4):
    """Plates in parallel on one pump: flow shares by 1/sqrt(k)."""
    w = [1.0] * plates
    w[2] = 1 / math.sqrt(k_factor)
    shares = [x / sum(w) for x in w]
    q = flow_total * shares[2]
    q0 = flow_total / plates
    rise0 = I["loss_stack_kw"] * 1000 / (q0 * 3600)
    rise = I["loss_stack_kw"] * 1000 / (q * 3600)
    r_hc = S["r_hs"] * (q / q0) ** -0.8                  # convection ~ v^0.8
    r0 = R_PATH
    r1 = R_PATH - S["r_hs"] + r_hc
    tj0 = I["coolant_c"] + rise0 * 0.25 + S["p_module_w"] * r0
    tj1 = I["coolant_c"] + rise * 0.25 + S["p_module_w"] * r1
    lines = [f"{plates} cold plates in parallel on one pump, {flow_total} kg/s;",
             f"  plate 3 partly blocked (resistance x {k_factor:.0f})",
             "  flow shares: " + ", ".join(f"{x:.3f}" for x in shares),
             f"  plate 3 flow {q:.2f} kg/s instead of {q0:.3f} "
             f"({q / q0 - 1:+.0%}); total unchanged",
             f"  coolant rise on plate 3: {rise0:.1f} -> {rise:.1f} K",
             f"  plate-to-coolant resistance {S['r_hs']:.3f} -> {r_hc:.4f} K/W",
             f"  first-row outer module: Tj {tj0:.1f} -> {tj1:.1f} C "
             f"(+{tj1 - tj0:.1f} K)",
             "  the end-of-line flow test reads the total flow and passes;",
             "  only a reading per plate - a flow sensor or the outlet",
             "  temperature of each plate in the full-power run - finds it"]
    emit("s_blocked", lines)
    return dict(share=shares[2], dtj=tj1 - tj0)


# ------------------------------------------------ 3. calibration across the fleet
def calibration(seed: int = 4402, units: int = 10, sd_raw: float = 0.003,
                sd_cal: float = 0.0005, lot_bias: float = 0.004):
    rng = np.random.default_rng(seed)
    raw = rng.normal(0.0, sd_raw, units)
    cal = rng.normal(0.0, sd_cal, units)
    biased = raw + lot_bias
    e_year = 11.0                                         # GWh a unit, teaching
    lines = [f"current-sensor gain error of {units} inverters (teaching):",
             f"  sd {sd_raw:.1%} uncalibrated, {sd_cal:.2%} after calibration",
             "  case                         worst unit   plant total   "
             "worst unit GWh",
             f"  uncalibrated                 {np.abs(raw).max():+8.2%}"
             f"   {raw.mean():+9.3%}     {np.abs(raw).max() * e_year:8.3f}",
             f"  calibrated at end of line    {np.abs(cal).max():+8.2%}"
             f"   {cal.mean():+9.3%}     {np.abs(cal).max() * e_year:8.3f}",
             f"  one sensor lot biased {lot_bias:+.1%}  "
             f"{np.abs(biased).max():+8.2%}   {biased.mean():+9.3%}     "
             f"{np.abs(biased).max() * e_year:8.3f}",
             f"  random errors shrink in the plant total (sd / sqrt({units}) ="
             f" {sd_raw / math.sqrt(units):.2%});",
             "  a shared bias does not: it shows in every unit and in the",
             "  total, and makes one block look better than another in",
             "  monitoring (ch 37) - calibration constants are a",
             "  configuration item, checked against a reference at the end",
             "  of the line"]
    emit("s_calib", lines)
    return dict(raw_max=float(np.abs(raw).max()), total_raw=float(raw.mean()),
                total_bias=float(biased.mean()))


# ------------------------------------------------ 4. staged firmware rollout
def rollout(p_bad: float = 0.05, rate: float = 0.1, units: int = 10,
            pilot_days: float = 14.0, rollback_days: float = 2.0,
            mwh_trip: float = 2.5):
    """Expected unit-trips of a firmware update with a hidden defect that
    trips an updated unit at `rate` a day until rolled back."""
    # all at once: first trip anywhere after 1/(units*rate) days
    t_detect = 1 / (units * rate)
    trips_all = units * rate * (t_detect + rollback_days)
    # staged: one pilot unit; caught in the pilot with chance c
    c = 1 - math.exp(-rate * pilot_days)
    trips_pilot_caught = rate * (1 / rate + rollback_days)
    trips_staged = c * trips_pilot_caught + (1 - c) * trips_all   # no pilot trip
    e_all = p_bad * trips_all * mwh_trip
    e_staged = p_bad * trips_staged * mwh_trip
    lines = [f"firmware update for {units} inverters; chance {p_bad:.0%} that it "
             "hides a defect",
             f"  tripping an updated unit {rate} times a day (teaching)",
             f"  all at once: first trip after {t_detect:.1f} day, rollback "
             f"{rollback_days:.0f} days: {trips_all:.1f} trips if bad",
             f"  pilot unit for {pilot_days:.0f} days catches the defect with "
             f"chance {c:.0%}; trips if bad: {trips_staged:.1f}",
             f"  expected loss: all at once {e_all:.2f} MWh, staged "
             f"{e_staged:.2f} MWh ({mwh_trip} MWh a trip)",
             "  the saving in energy is small; the real gain is that a bad",
             "  image meets one unit, not ten, and that a defect with a",
             "  safety side (island detection, ride-through) is found before",
             "  the fleet carries it - the pilot's record is part of the",
             "  release (ch 36)"]
    emit("s_rollout", lines)
    return dict(all=trips_all, staged=trips_staged, c=c)


# ------------------------------------------------ 5. torque marks or audit
def torque_audit(joints: int = 400, missed: int = 2, visual: float = 0.95):
    def p_detect(n: int) -> float:
        return 1 - math.comb(joints - missed, n) / math.comb(joints, n)
    need = next(n for n in range(1, joints + 1) if p_detect(n) >= 0.90)
    marks = 1 - (1 - visual) ** missed
    lines = [f"{joints} bolted joints in one inverter, {missed} left untorqued "
             "(teaching)",
             "  torque audit of n random joints with a wrench:",
             "    n:       " + "  ".join(f"{n:5d}" for n in (10, 40, 100, 200)),
             "    finds:   " + "  ".join(f"{p_detect(n):5.0%}" for n in
                                         (10, 40, 100, 200)),
             f"    {need} joints to find at least one with 90 % chance",
             f"  torque marks checked by eye on all {joints}, each seen with "
             f"{visual:.0%}: {marks:.1%}",
             "  a mark turns an invisible state into a visible one: the eye",
             "  checks every joint in minutes, the wrench a sample in hours;",
             "  the audit then checks the wrench and the record, not the",
             "  joints one by one"]
    emit("s_torque", lines)
    return dict(need=need, marks=marks, p40=p_detect(40))


# ------------------------------------------------ 6. the test bench
def bench(units: int = 10, retests: int = 3, run_h: float = 8.0,
          setup_h: float = 4.0, hours_day: float = 16.0):
    """Back-to-back bench: two inverters run against each other."""
    runs = math.ceil(units / 2)
    extra = retests                                     # a partner each time
    h = (runs + extra) * (run_h + setup_h)
    stations = [("board line (per inverter set)", 6.0), ("stack assembly", 10.0),
                ("cabinet integration and wiring", 24.0),
                ("low-voltage tests and firmware", 4.0),
                ("full-power bench (per unit)", (run_h + setup_h) / 2)]
    lines = [f"factory hours for {units} inverters (teaching): two crews,",
             f"  the bench {hours_day:.0f} h a day",
             "  station                              h a unit   h for all"]
    for name, hu in stations:
        lines.append(f"  {name:36s} {hu:8.1f}   {hu * units:9.0f}")
    cab_days = 24 * units / (2 * hours_day)
    run_days = (run_h + setup_h) / hours_day
    limit = math.floor(cab_days / run_days) - runs
    lines += [f"  bench runs: {runs} pairs + {extra} re-runs (INV-04, INV-09,",
              f"    the reprinted unit, each with a partner) = {h:.0f} h",
              f"  bench {h / hours_day:.1f} days (without re-runs "
              f"{runs * run_days:.2f}); cabinet station {cab_days:.1f} days",
              f"  the cabinet station sets the pace; the bench takes over "
              f"after {limit + 1} re-runs,",
              "  because a re-test costs a whole run: the partner runs too -",
              "  re-tests grouped into pairs, or a second bench, keep it",
              "  from setting the shipping date"]
    emit("s_bench", lines)
    return dict(hours=h, days=h / hours_day, cab=cab_days, limit=limit + 1)


# ------------------------------------------------ 7. floor life of sensitive parts
REELS = [   # reel, events (hours open on the floor, then 'dry' = in dry storage)
    ("R101", [8, "dry", 16, "dry", 40]),
    ("R102", [72, "dry", 72, "dry", 30]),
    ("R103", [24, 24, 24, "dry", 24]),
    ("R104", [120, 60]),
]


def floor_life(limit_h: float = 168.0) -> list:
    lines = [f"moisture-sensitive parts: floor life {limit_h:.0f} h after the dry "
             "bag is opened",
             "  (teaching); dry storage pauses the clock",
             "  reel   exposure h   left h   verdict"]
    out = []
    for reel, ev in REELS:
        used = sum(e for e in ev if e != "dry")
        left = limit_h - used
        ok = left >= 0
        out.append((reel, used, ok))
        lines.append(f"  {reel}   {used:10.0f}   {left:6.0f}   "
                     f"{'use' if ok else 'hold: maker procedure before use'}")
    bad = [r for r, _, ok in out if not ok]
    lines += [f"  {len(bad)} reels over their floor life ({', '.join(bad)}): moisture",
              "  in the package can crack it during soldering; the record of",
              "  every opening is the only way to know - the recovery is the",
              "  part maker's procedure, not a factory improvisation"]
    emit("s_msl", lines)
    return out


# ------------------------------------------------ 8 and 9. spares and downtime
MTTR_H = {"IGBT module": 72, "gate-driver board": 10, "DC-link capacitor": 24,
          "control board": 10, "current and voltage sensors": 8,
          "auxiliary power supply": 8, "pump, fans, heat exchanger": 6,
          "DC switch, AC breaker, contactors": 24}


def _fits():
    mult = ea._counts()
    out = {}
    for nid, parent, name, n, kg, ku, f in src.TREE:
        if parent is not None and f > 0:
            out[name] = mult[nid] * f
    return out


def spares(units: int = 10, lead_weeks: float = 12.0, cover: float = 0.90):
    fits = _fits()
    hours = lead_weeks * 7 * 24
    lines = [f"spares for {units} inverters: failures in a {lead_weeks:.0f}-week "
             "resupply time,",
             f"  stock for {cover:.0%} no-stock-out (Poisson)",
             "  item                              failures/yr   in lead   stock"]
    out = {}
    for name, f in sorted(fits.items(), key=lambda x: -x[1]):
        per_year = units * f * 8760 / 1e9
        mean = units * f * hours / 1e9
        k, cum, term = 0, math.exp(-mean), math.exp(-mean)
        while cum < cover:
            k += 1
            term *= mean / k
            cum += term
        out[name] = k
        lines.append(f"  {name:34s} {per_year:11.2f}   {mean:7.2f}   {k:5d}")
    zero = [k for k, v in out.items() if v == 0]
    lines += ["  the stock follows the failure rate: one each of the four",
              f"  most frequent items; {len(zero)} items get none on this rule and",
              "  wait the lead time after a failure - whether to hold one",
              "  anyway is a question of the energy lost while waiting",
              "  (next lesson, ch 52)"]
    emit("s_spares", lines)
    return out


def downtime(units: int = 10, p_avg_mw: float = 1.25):
    fits = _fits()
    lines = [f"downtime and energy by item for {units} inverters, {p_avg_mw} MW "
             "lost",
             "  while a unit is down (teaching mean)",
             "  item                              failures/yr  MTTR h   MWh/yr"
             "   share"]
    rows = []
    for name, f in fits.items():
        n = units * f * 8760 / 1e9
        mwh = n * MTTR_H[name] * p_avg_mw
        rows.append((name, n, MTTR_H[name], mwh))
    tot = sum(r[3] for r in rows)
    for name, n, h, mwh in sorted(rows, key=lambda r: -r[3]):
        lines.append(f"  {name:34s} {n:11.2f}  {h:6.0f}   {mwh:6.1f}   "
                     f"{mwh / tot:5.0%}")
    top = max(rows, key=lambda r: r[3])
    lines += [f"  total {tot:.0f} MWh a year; the largest share is {top[0]}:",
              "  rare failures with a long repair cost more energy than",
              "  frequent short ones - spares and repair time, not the",
              "  failure rate alone, set the energy at risk"]
    emit("s_downtime", lines)
    return dict(total=tot, top=top[0], share=top[3] / tot)


# ------------------------------------------------ 10. ESR guard band
def esr_guard(limit: float = 1.15, sd: float = 0.06, u: float = 0.03,
              n: int = 200000, seed: int = 4403):
    rng = np.random.default_rng(seed)
    true = rng.normal(1.0, sd, n)
    meas = true + rng.normal(0.0, u / 2, n)              # U = 2 standard u
    out = {}
    for name, acc in (("limit", limit), ("limit - U", limit - u)):
        accept = meas <= acc
        fa = float(np.mean(accept & (true > limit)))
        fr = float(np.mean(~accept & (true <= limit)))
        out[name] = (fa, fr)
    parts, c_part, c_field = 480, 0.12, 5.0     # caps of the fleet; k u
    lines = [f"incoming ESR check of film capacitors: class limit {limit:.2f} x "
             "nominal,",
             f"  parts sd {sd:.0%}, measurement U {u:.0%} (teaching); cost of a "
             f"rejected part {c_part} k u,",
             f"  of a bad part in the field {c_field:.0f} k u, {parts} parts",
             "  accept when measured <=   false accepts   false rejects"
             "   cost k u"]
    cost = {}
    for name, (fa, fr) in out.items():
        cost[name] = parts * (fa * c_field + fr * c_part)
        lines.append(f"  {name:24s}   {fa * 1e6:9.0f} ppm   {fr * 1e6:9.0f} ppm"
                     f"   {cost[name]:8.2f}")
    best = min(cost, key=cost.get)
    lines += [f"  cheaper rule: accept at '{best}' - the guard band trades",
              "  rejected good parts for fewer bad parts let in; a bad",
              "  capacitor in a bank of twelve takes more ripple than its",
              "  share and ages first (lesson B); with a cheap part and a",
              "  costly field repair the guard band pays (ch 43)"]
    emit("s_esr", lines)
    return dict(rates=out, cost=cost, best=best)


# ------------------------------------------------ 11. MPPT step size
def _track(tr, curves, v0: float) -> np.ndarray:
    v, got = v0, []
    for c in curves:
        v = min(max(v, 0.0), c.voc)
        i = float(c.i(v))
        got.append(v * i)
        v = tr.update(v, i)
    return np.array(got)


def step_size(n_series: int = 26):
    flat = [mppt.PVM_550.at(1000.0, 45.0, n_series)] * 300
    ramp = [mppt.PVM_550.at(300.0 + 7.0 * k, 45.0, n_series) for k in range(100)]
    p_flat = flat[0].mpp()[1]
    p_ramp = np.array([c.mpp()[1] for c in ramp])
    v_flat, v_ramp = flat[0].mpp()[0], ramp[0].mpp()[0]
    rows = []
    for step in (1.0, 2.0, 4.0, 8.0, 16.0):
        res = []
        for make in (lambda: mppt.PerturbObserve(v_ref=0.0, step=step),
                     lambda: lab_d.DriftFreePO(v_ref=0.0, step=step)):
            tr = make()
            tr.v_ref = v_flat
            steady = _track(tr, flat, v_flat)[150:].mean() / p_flat
            rr = []
            for d in (1.0, -1.0):
                tr = make()
                tr.v_ref, tr.direction = v_ramp, d
                rr.append(_track(tr, ramp, v_ramp).sum() / p_ramp.sum())
            res.append((steady, rr[0], rr[1]))
        rows.append((step, res))
    lines = ["MPPT step size (educational trackers of lab D): steady at "
             "1000 W/m2 after",
             "  settling; ramp 300 -> 1000 W/m2 in 100 s, starting with the",
             "  step going up or down",
             "  step V   P&O steady  ramp up/down     hold-cmp steady  "
             "ramp up/down"]
    for step, ((s1, u1, d1), (s2, u2, d2)) in rows:
        lines.append(f"  {step:6.0f}   {s1:9.3%}  {u1:6.2%} {d1:6.2%}     "
                     f"{s2:9.3%}      {u2:6.2%} {d2:6.2%}")
    po_spread = max(abs(u - d) for _, ((_, u, d), _) in rows)
    lines += ["  steady: the step costs a little at the top of the curve, and",
              "  more as it grows (the tracker oscillates around the peak);",
              f"  ramp: plain P&O depends on the way it happens to be going",
              f"  when the ramp starts (up to {po_spread:.0%} apart) - one",
              "  dynamic run proves little; repeat it from several starting",
              "  points. The hold-compare tracker does not care; its price is",
              "  a measure and a hold step, so it moves a third as often"]
    emit("s_step", lines)
    return rows


# ------------------------------------------------ 12. transition coverage
EVENTS = ["start", "tick", "grid_ok", "synced", "grid_lost", "stop", "fault",
          "reset"]


def coverage() -> dict:
    states = ["OFF", "PRECHARGE", "READY", "SYNC", "RUN", "FAULT"]
    seen = set()
    for _, events, _ in lab_d.CASES:
        sim = cm.ConverterSim()
        for ev, kw in events:
            before = sim.state
            sim.event(ev, **kw)
            seen.add((before, ev))
    defined = set()
    for st in states:
        for ev in EVENTS:
            sim = cm.ConverterSim(state=st)
            kw = {"v_dc": 900} if ev == "tick" else {}
            if ev == "reset":
                kw = {"cause_cleared": True}
            sim.event(ev, **kw)
            if sim.state != st:
                defined.add((st, ev))
    tested = defined & seen
    missing = sorted(defined - seen)
    pairs = len(states) * len(EVENTS)
    lines = [f"transition coverage of the test list: {len(states)} states x "
             f"{len(EVENTS)} events = {pairs} pairs",
             f"  pairs that change the state: {len(defined)}; exercised by "
             f"the {len(lab_d.CASES)} cases: {len(tested)} "
             f"({len(tested) / len(defined):.0%})",
             f"  all pairs exercised (incl. ignored events): {len(seen)} of "
             f"{pairs} ({len(seen) / pairs:.0%})",
             "  state-changing pairs never tested:"]
    for k in range(0, len(missing), 3):
        lines.append("    " + "; ".join(f"{s} + {e}" for s, e in missing[k:k + 3]))
    lines += ["  a test list that passes says nothing about the transitions",
              "  it never visits: every pair above - a stop while running, a",
              "  fault during precharge - needs a case before the release",
              "  (exercise)"]
    emit("s_cover", lines)
    return dict(defined=len(defined), tested=len(tested), missing=missing)


# ------------------------------------------------ 13. ESD energy
def esd(c_pf: float = 100.0, r_ohm: float = 1500.0):
    lines = [f"electrostatic discharge, body model {c_pf:.0f} pF through "
             f"{r_ohm:.0f} ohm (teaching)",
             "  body voltage   energy uJ   peak current A"]
    out = {}
    for v in (100, 500, 2000, 8000):
        e = 0.5 * c_pf * 1e-12 * v ** 2 * 1e6
        i = v / r_ohm
        out[v] = (e, i)
        lines.append(f"  {v:9d} V   {e:9.2f}   {i:14.2f}")
    lines += ["  a person does not feel a discharge of a few hundred volts,",
              "  yet a gate or a sensor input can be weakened by far less",
              "  energy than a felt spark - damage is latent and passes the",
              "  tests: earthed wrist straps, dissipative floors and",
              "  shielding bags are process controls with their own records"]
    emit("s_esd", lines)
    return out


# ------------------------------------------------ 14. burn-in of boards
def burnin(beta: float = 0.5, eta_h: float = 2.0e7, boards: int = 520,
           af: float = 10.0, hours: float = 48.0, cost_h: float = 0.004,
           field_cost: float = 3.0):
    """Infant mortality with a Weibull shape below one."""
    def F(t):
        return 1 - math.exp(-(t / eta_h) ** beta)
    eq = af * hours
    first_year = F(8760)
    removed = F(eq)
    after = (F(eq + 8760) - F(eq)) / (1 - F(eq))
    saved = boards * (first_year - after)
    cost = boards * hours * cost_h
    lines = [f"board infant mortality, Weibull shape {beta}, scale "
             f"{eta_h:.0e} h (teaching);",
             f"  {boards} boards",
             f"  burn-in {hours:.0f} h at acceleration {af:.0f} = {eq:.0f} h of "
             "field life",
             f"  share failing in the burn-in: {removed:.2%}",
             f"  first-year field failures: {boards * first_year:.1f} without, "
             f"{boards * after:.1f} with burn-in",
             f"  saved: {saved:.1f} field failures x {field_cost:.0f} k u = "
             f"{saved * field_cost:.1f} k u; burn-in costs {cost:.1f} k u",
             f"  verdict: {'pays' if saved * field_cost > cost else 'does not pay'}"
             " at these values - with a shape near",
             "  one there are no early failures to remove and it never pays",
             "  (ch 40); the shape comes from the maker's field data"]
    emit("s_burnin", lines)
    return dict(saved=saved, cost=cost, pays=saved * field_cost > cost)


if __name__ == "__main__":
    plate()
    blocked()
    calibration()
    rollout()
    torque_audit()
    bench()
    floor_life()
    spares()
    downtime()
    esr_guard()
    step_size()
    coverage()
    esd()
    burnin()
