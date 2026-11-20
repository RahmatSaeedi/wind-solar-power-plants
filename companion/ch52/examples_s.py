"""Chapter 52, round s: maintenance indicators and backlog, blade erosion
and the value of a repair, pitch-battery life against cabinet heat,
tracker-drive current, contractor response against the agreement,
whether a corrective action worked (rate ratio), age replacement of
pitch batteries, a repairable pair with one or two repair crews, block
importance in the export path, a sensitivity table of the energy case,
robot against truck over ten years, drone line patrol, the 'other'
failure code, and closing delays of work orders.

Run from the project root:   python -m companion.ch52.examples_s
Writes companion/ch52/expected/s_*.txt. Teaching values (A-530 to A-537).
"""
from __future__ import annotations

import math

import numpy as np
from scipy import stats

from companion.ch52 import lab_f
from companion.ch52 import sources as src
from companion.ch52.common import emit
from plantp import ram


# ------------------------------------------------ 1. indicators and backlog
def indicators(cap_week: float = 225.0) -> dict:
    pm_due, pm_on_time = 412, 361
    cm, pm = 88, 412
    backlog_h = 1_240.0
    weeks = backlog_h / cap_week
    lines = ["maintenance indicators for a quarter (teaching targets in brackets)",
             f"  PM done on time {pm_on_time / pm_due:.0%} [90 %]; corrective share of orders "
             f"{cm / (cm + pm):.0%} [<20 %]",
             f"  backlog {backlog_h:,.0f} h = {weeks:.1f} crew-weeks at {cap_week:.0f} h a week "
             "[2-4]",
             f"  backlog {'above' if weeks > 4 else 'inside'} the band and PM on time "
             f"{'below' if pm_on_time / pm_due < 0.9 else 'at'} target:",
             "  work is late and piling up; the late PM tasks are the ones",
             "  that wait for an outage window (ch 51) - the cause is in the",
             "  plan, and a crew with spare hours (lesson A) cannot fix it"]
    emit("s_kpi", lines)
    return dict(on_time=pm_on_time / pm_due, weeks=weeks)


# ------------------------------------------------ 2. blade erosion
def erosion(aep_mwh: float = 16_100.0, price: float = 70.0) -> dict:
    cat = {"cat 1 (coating)": (5, 0.0), "cat 2 (laminate exposed)": (4, 0.4),
           "cat 3 (leading edge open)": (2, 1.5)}           # turbines, AEP loss %
    repair_u = 9_000.0                                        # per turbine, rope access
    rows = []
    for k, (n, loss) in cat.items():
        lost = n * aep_mwh * loss / 100
        value = lost * price
        rows.append((k, n, loss, lost, value, value > n * repair_u))
    lines = [f"blade leading edges from the drone survey (12 turbines, AEP {aep_mwh:,.0f} MWh "
             "each)",
             "  category                    turbines  AEP loss  MWh/yr   u/yr   repair pays"]
    lines += [f"  {k:27s} {n:8d} {l:8.1f}% {m:7.0f} {v:8,.0f}   {'yes' if p else 'no'}"
              for k, n, l, m, v, p in rows]
    pay2 = 4 * repair_u / rows[1][4]
    lines += [f"  a repair costs {repair_u:,.0f} u a turbine: category 3 pays in one year,",
              f"  category 2 after {pay2:.1f} years - but erosion grows, so",
              "  category 2 is repaired in the next low-wind window before",
              "  it becomes 3 (ch 11 erosion, ch 42 repair)"]
    emit("s_erosion", lines)
    return {k: (m, p) for k, n, l, m, v, p in rows}


# ------------------------------------------------ 3. pitch batteries and heat
def pitch_heat(ref: float = 25.0, life_yr: float = 6.0) -> dict:
    cab = {"T03 (fan seized)": 41.0, "T05": 30.0, "T07": 29.0, "T11": 31.0}
    out = {k: life_yr / 2 ** ((t - ref) / 10) for k, t in cab.items()}
    lines = ["pitch-cabinet mean temperature and expected battery life",
             f"  (teaching {life_yr:.0f} years at {ref:.0f} C, halving each 10 K)"]
    lines += [f"  {k:18s} {t:5.1f} C  life {out[k]:4.1f} years" for k, t in cab.items()]
    others = np.mean([v for k, v in out.items() if not k.startswith("T03")])
    lines += [f"  T03's batteries live {out['T03 (fan seized)'] / others:.0%} as long as the others': "
              "the repeat failures",
              "  of lesson C are the cabinet fan, not the batteries - the",
              "  corrective action is the fan and a temperature alarm"]
    emit("s_pitch", lines)
    return out


# ------------------------------------------------ 4. tracker-drive current
def tracker(limit_pct: float = 25.0) -> dict:
    rows = {"row 112": [4.1, 4.2, 4.2, 4.3], "row 540": [4.0, 4.4, 4.9, 5.4],
            "row 873": [4.2, 4.1, 4.3, 4.2], "row 1310": [4.1, 4.6, 5.0, 5.3]}   # A at stow test
    rise = {k: (v[-1] / v[0] - 1) * 100 for k, v in rows.items()}
    bad = [k for k, r in rise.items() if r > limit_pct]
    lines = ["tracker drives: motor current in the quarterly stow test (A);",
             f"  flag a rise over {limit_pct:.0f} %"]
    lines += [f"  {k:9s} " + " ".join(f"{x:4.1f}" for x in v) + f"   {rise[k]:+5.1f} %"
              for k, v in rows.items()]
    lines += [f"  flagged: {', '.join(bad)} - a stiff bearing or a slew drive",
              "  wearing; the stow test that proves safety also measures",
              "  condition, if its current is logged and trended"]
    emit("s_tracker", lines)
    return dict(bad=bad)


# ------------------------------------------------ 5. contractor response
def response(agreed_h: float = 4.0) -> dict:
    times = np.array([1.5, 2.0, 3.5, 6.0, 2.5, 9.0, 3.0, 2.2, 4.5, 1.8, 12.0, 3.2])
    late = int(np.sum(times > agreed_h))
    lines = [f"HV contractor: hours from call to arrival, twelve call-outs (agreed {agreed_h:.0f} h)",
             "  " + " ".join(f"{x:4.1f}" for x in times),
             f"  late {late} of {times.size}; median {np.median(times):.1f} h, worst "
             f"{times.max():.0f} h",
             "  the median meets the agreement and the tail does not: the",
             "  agreement states a percentile (e.g. 90 % within 4 h) and a",
             "  maximum, or the worst nights are not covered at all"]
    emit("s_response", lines)
    return dict(late=late, median=float(np.median(times)))


# ------------------------------------------------ 6. did the corrective action work?
def rate_ratio(before=(9, 12 * 6), after=(2, 12 * 6)) -> dict:
    (k1, t1), (k2, t2) = before, after
    # exact conditional test: k2 ~ Binomial(k1 + k2, t2 / (t1 + t2)) under equal rates
    p = stats.binom.cdf(k2, k1 + k2, t2 / (t1 + t2))
    lines = ["converter trips on voltage dips, fleet of 12, before and after the",
             "  settings check at hand-back (turbine-months)",
             f"  before {k1} in {t1} turbine-months; after {k2} in {t2}",
             f"  rate ratio {(k2 / t2) / (k1 / t1):.2f}; chance of so few by luck if nothing "
             f"changed: {p:.3f}",
             "  the drop is unlikely to be chance, but two failures are few:",
             "  the record is kept another six months before the action is",
             "  closed as effective (ch 37, ch 40 8D)"]
    emit("s_ratio", lines)
    return dict(ratio=(k2 / t2) / (k1 / t1), p=float(p))


# ------------------------------------------------ 7. age replacement of pitch batteries
def age_replace(beta: float = 3.0, eta_yr: float = 6.0, c_pm: float = 1.0,
                c_fail: float = 4.0) -> dict:
    grid = np.arange(0.5, 10.01, 0.25)
    rate, t = ram.best_age(beta, eta_yr, c_pm, c_fail, grid)
    run = c_fail / ram.w_mean(beta, eta_yr)
    lines = [f"pitch batteries: Weibull shape {beta}, scale {eta_yr} years; a planned change",
             f"  costs {c_pm:.0f}, a failure in service {c_fail:.0f} (turbine stop, call-out)",
             f"  best replacement age {t:.2f} years: {rate:.3f} cost units a year",
             f"  run to failure: {run:.3f} a year ({(run / rate - 1):.0%} more)",
             "  wear-out (shape > 1) and a dear failure make planned",
             "  replacement pay; with a constant rate it never would"]
    emit("s_age", lines)
    return dict(t=t, rate=rate, run=run)


# ------------------------------------------------ 8. a repairable pair: one or two crews
def pair(lam: float = 0.01 / 8760, mu: float = 1 / 4380) -> dict:
    rho = lam / mu
    # Markov, 2 identical units, states 0/1/2 failed
    two_crews = 1 - (rho / (1 + rho)) ** 2          # independent repair
    p2_one = (2 * rho ** 2) / (1 + 2 * rho + 2 * rho ** 2)   # one crew: birth-death
    one_crew = 1 - p2_one
    lines = ["two main transformers, each 0.01 failures a year, 4,380 h to replace",
             f"  both out, two repair crews (independent): {1 - two_crews:.2e}",
             f"  both out, one repair at a time:           {p2_one:.2e}",
             f"  {p2_one / (1 - two_crews):.1f} times worse with one at a time - for a",
             "  six-month replacement the 'crew' is the factory slot and",
             "  the crane; two failures in one window queue for them"]
    emit("s_pair", lines)
    return dict(two=1 - two_crews, one=p2_one)


# ------------------------------------------------ 9. block importance
def importance() -> dict:
    a = {"line": 1 - 2 * 4.2 / 8760, "T1": 0.9923, "T2": 0.9923, "bus132": 0.99995,
         "PPC": 0.9995, "fallback": 0.99}
    node = ("s", ["line", "bus132", ("p", ["T1", "T2"]), ("p", ["PPC", "fallback"])])
    out = {}
    for k in a:
        hi, lo = dict(a), dict(a)
        hi[k], lo[k] = 1.0, 0.0
        out[k] = ram.rbd(node, hi) - ram.rbd(node, lo)
    rank = sorted(out.items(), key=lambda kv: -kv[1])
    lines = ["Birnbaum importance in 'some export possible': A(block up) - A(block down)"]
    lines += [f"  {k:9s} {v:.5f}" for k, v in rank]
    lines += ["  the line and the bus carry everything; each transformer and",
              "  the controller matter only while their partner is down -",
              "  improve where the importance is, not where failures are",
              "  most frequent"]
    emit("s_importance", lines)
    return out


# ------------------------------------------------ 10. sensitivity of the energy case
def sensitivity() -> dict:
    base = sum(lab_f.expected().values())
    rows = []
    for k in ("wind turbine (major)", "wind turbine (minor)", "PV inverter",
              "132 kV line (permanent fault)"):
        for idx, name in ((1, "rate"), (2, "MTTR"), (3, "delay")):
            c = dict(src.CLASSES)
            row = list(c[k])
            if row[idx] == 0:
                continue
            row[idx] *= 1.5
            c[k] = tuple(row)
            rows.append((k, name, sum(lab_f.expected(c).values()) - base))
    rows.sort(key=lambda r: -r[2])
    lines = ["energy lost a year: change when one input of one class rises 50 % (MWh)"]
    lines += [f"  {k:30s} {n:6s} {d:+7.0f}" for k, n, d in rows]
    lines += [f"  the largest: {rows[0][0]} {rows[0][1]}; the data effort",
              "  goes where the result is most sensitive, not evenly"]
    emit("s_sens", lines)
    return dict(top=rows[0])


# ------------------------------------------------ 11. robot against truck over ten years
def robot_vs_truck(years: int = 10, rate: float = 0.06, campaigns: int = 16) -> dict:
    from companion.ch52 import examples_g as eg
    truck = eg.campaign_cost("truck with brush, RO water") * campaigns
    robot_capex = 2_100 * 1_500.0
    robot = eg.campaign_cost("waterless robot (dry brush)") * 52 + 2_100 * 60.0  # weekly, upkeep
    rec_t, rec_r = 3.4, 2.6
    gain = (rec_t - rec_r) / 100 * 300 * 70 * 365 * 0.25          # teaching: lower recovery
    af = (1 - (1 + rate) ** -years) / rate
    npv_t = truck * af
    npv_r = robot_capex + (robot + gain) * af
    lines = [f"cleaning over {years} years at {rate:.0%} (teaching costs)",
             f"  truck + brush: {campaigns} campaigns a year {truck:,.0f} u/yr -> NPV {npv_t:,.0f} u",
             f"  dry robots: capital {robot_capex:,.0f} u, weekly runs and upkeep {robot:,.0f} u/yr,",
             f"  plus energy not recovered {gain:,.0f} u/yr -> NPV {npv_r:,.0f} u",
             f"  {'the truck' if npv_t < npv_r else 'the robot'} is cheaper here; the robot uses no",
             "  water - in a drought year (ch 51) water may decide what money",
             "  does not, so both are kept in the comparison"]
    emit("s_robot", lines)
    return dict(npv_t=npv_t, npv_r=npv_r)


# ------------------------------------------------ 12. drone line patrol
def patrol(km: float = 14.5) -> dict:
    foot = dict(h_km=1.6, find=0.70, cost_h=45.0)
    drone = dict(h_km=0.35, find=0.85, cost_h=160.0)
    out = {}
    for k, d in (("foot", foot), ("drone", drone)):
        h = km * d["h_km"]
        out[k] = (h, h * d["cost_h"], d["find"])
    lines = [f"132 kV line patrol, {km} km (teaching rates)",
             "  method   hours   cost u   share of defects found"]
    lines += [f"  {k:6s} {h:7.1f} {c:8,.0f} {f:12.0%}" for k, (h, c, f) in out.items()]
    lines += ["  the drone is cheaper and finds more from above (insulators,",
              "  fittings); the foot patrol still sees the corridor and the",
              "  tower bases - the network owner's plan uses both (ch 51 K)"]
    emit("s_patrol", lines)
    return out


# ------------------------------------------------ 13. the 'other' failure code
def other_code() -> dict:
    codes = {"CNV-IGBT": 9, "PIT-BAT": 7, "FAN": 11, "FUSE-OPEN": 14, "GBX-BRG": 2,
             "HVAC-FLT": 5, "OTHER": 19}
    tot = sum(codes.values())
    share = codes["OTHER"] / tot
    lines = ["corrective orders of the year by failure code"]
    lines += [f"  {k:10s} {v:3d}" for k, v in sorted(codes.items(), key=lambda kv: -kv[1])]
    lines += [f"  'OTHER' is {share:.0%} - the largest code: the list lacks the codes",
              "  people need; a monthly read of the 'OTHER' texts adds codes",
              "  (teaching rule: revise above 10 %)"]
    emit("s_other", lines)
    return dict(share=share)


# ------------------------------------------------ 14. closing delays
def closing() -> dict:
    lag = np.array([0, 1, 1, 2, 0, 14, 3, 1, 30, 2, 5, 1, 45, 2, 0, 3])   # days, done to closed
    lines = ["days from work done to work order closed, sixteen orders",
             "  " + " ".join(f"{x:2d}" for x in lag),
             f"  median {np.median(lag):.1f} days; over a week: {int(np.sum(lag > 7))}",
             "  an order closed a month late misses the monthly reliability",
             "  report and the warranty clock (lesson I): closing is part",
             "  of the job, done with the test record on site"]
    emit("s_closing", lines)
    return dict(median=float(np.median(lag)), late=int(np.sum(lag > 7)))


if __name__ == "__main__":
    indicators()
    erosion()
    pitch_heat()
    tracker()
    response()
    rate_ratio()
    age_replace()
    pair()
    importance()
    sensitivity()
    robot_vs_truck()
    patrol()
    other_code()
    closing()
