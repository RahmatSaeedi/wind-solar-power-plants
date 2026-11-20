"""Chapter 22 - further lessons: preliminary cost ranges by site, the
schedule risk of the development network, trade-off rates from the
finance model, how far one score can fall, a gated decision tree per
site, supply-chain lead times, construction weather windows from the
data pack, labour influx, development funding routes, export-route
options, cumulative effects and a grievance log.

Run from the project root:   python -m companion.ch22.examples_h
Writes companion/ch22/expected/h_*.txt and diagrams/data/ch22-*.csv.
All values are teaching values (A-311 to A-314); the ecology and
social numbers are invented to show the method, not real thresholds.
"""
from __future__ import annotations

import numpy as np

from companion.ch21 import model
from companion.ch22 import examples_c, lab_b, lab_d, sources as src
from companion.ch22.common import csv, emit
from plantp import appraisal as ap
from plantp import datapack

RNG = np.random.default_rng(22)
SHARES = {"wind": 0.523, "PV": 0.242, "substation": 0.101,
          "battery": 0.087, "development": 0.047}

# [start: ranges]
CLASS = {   # (low, high) range of each item by estimate class (A-314)
    "feasibility": {"wind": (-0.10, 0.20), "PV": (-0.10, 0.15),
                    "substation": (-0.15, 0.30), "battery": (-0.15, 0.20),
                    "development": (-0.05, 0.25)},
    "screening": {"wind": (-0.25, 0.45), "PV": (-0.20, 0.40),
                  "substation": (-0.30, 0.60), "battery": (-0.25, 0.40),
                  "development": (-0.10, 0.50)},
}


def cost_draws(name: str, n: int = 20_000) -> tuple[float, np.ndarray]:
    """Base cost without contingency and n Monte Carlo totals: each
    item triangular (low, base, high); grid works on their own range."""
    f = src.SITES[name]
    base = f["capex"] / 1.05                     # remove the 5 % allowance
    cls = CLASS["screening" if f["energy_q"] < 0.5 else "feasibility"]
    tot = np.zeros(n)
    for item, share in SHARES.items():
        b = base * share
        lo, hi = cls[item]
        tot += RNG.triangular(b * (1 + lo), b, b * (1 + hi), n)
    if f["reinforce"]:
        r = f["reinforce"]
        tot += RNG.triangular(0.8 * r, r, 1.6 * r, n)
    return base + f["reinforce"], tot
# [end: ranges]


def cost_ranges() -> None:
    lines = ["preliminary cost ranges (Monte Carlo of items, k u):",
             "  site       base     P50      P80      P90    contingency to P80"]
    for n in src.SITES:
        base, t = cost_draws(n)
        p50, p80, p90 = np.percentile(t, [50, 80, 90])
        lines.append(f"  {n:9s} {base:7,.0f}  {p50:7,.0f}  {p80:7,.0f}  {p90:7,.0f}"
                     f"   {(p80 / base - 1) * 100:6.1f} %")
    lines += ["  the base is the sum of most-likely values; skewed ranges",
              "  put the P50 above it, so a 5 % allowance is too thin even",
              "  for P-Central; P-North's screening-class range and its grid",
              "  works widen everything - its P80 is far above the others",
              "  (items drawn independently: correlated prices would widen",
              "  the range further)"]
    emit("h_costs", lines)


# [start: schedule]
THREE = {   # optimistic, most likely, pessimistic months (A-314)
    "wind campaign (12 mo)": (12, 12, 13), "grid study and offer": (6, 9, 16),
    "ESIA baseline and report": (12, 14, 20),
    "land options and access": (3, 4, 7),
    "land agreements": (6, 9, 16), "geotechnical survey": (3, 4, 6),
    "energy yield report": (1, 2, 3), "permits": (6, 8, 14),
    "front-end design": (5, 6, 8), "PPA negotiation": (6, 8, 14),
    "financing and close": (4, 6, 9),
}


def schedule_draws(n: int = 4_000):
    totals, crit_count = [], {t: 0 for t in THREE}
    for _ in range(n):
        tasks = {t: (RNG.triangular(*THREE[t]), pre)
                 for t, (_, pre) in examples_c.TASKS.items()}
        total, crit, _ = ap.critical_path(tasks)
        totals.append(total)
        for t in crit:
            crit_count[t] += 1
    return np.array(totals), {t: c / n for t, c in crit_count.items()}
# [end: schedule]


def schedule_risk() -> None:
    tot, ci = schedule_draws()
    p50, p80 = np.percentile(tot, [50, 80])
    lines = ["schedule risk of the development network (4,000 draws):",
             f"  plan (most likely durations) 28 months to financial close",
             f"  P50 {p50:.1f} months, P80 {p80:.1f} months;"
             f" chance of 28 or less {np.mean(tot <= 28) * 100:.0f} %",
             "  criticality index (share of draws in which a task is critical):"]
    for t in THREE:
        if ci[t] > 0.005:
            lines.append(f"    {t:28s} {ci[t] * 100:5.0f} %")
    lines += ["  the plan's date is the most likely path, not the likely",
              "  date: with skewed durations and parallel chains the chance",
              "  of meeting it is small; which chain is critical changes",
              "  from draw to draw, so both need managing; the grid and land",
              "  chains keep their slack here - until a review finds them",
              "  late (section C)"]
    emit("h_schedule", lines)
    csv("ch22-schedule.csv", "months,share",
        [(m, f"{np.mean(tot <= m):.3f}") for m in range(24, 45)])


def tradeoffs() -> None:
    base = model.run()
    e = model.run(energy_scale=1.01, sizing_energy=1.01)
    c = model.run(capex_scale=1.01)
    d_e = e["npv"] - base["npv"]
    d_c = c["npv"] - base["npv"]
    d_m = base["npv"] * (1 - 1.075 ** (-1 / 12))
    gwh = 2.9514                                  # 1 % of 295.14
    lines = ["trade-off rates from the chapter 21 model (NPV at close, k u):",
             f"  +1 % energy ({gwh:.2f} GWh a year)  {d_e:+8,.0f}"
             f"   equity IRR {(e['equity_irr'] - base['equity_irr']) * 100:+.2f} pt",
             f"  +1 % capital cost ({src.SITES['P-Central']['capex'] / 100:,.0f} k u)"
             f" {d_c:+8,.0f}   equity IRR {(c['equity_irr'] - base['equity_irr']) * 100:+.2f} pt",
             f"  one month later financial close  {-d_m:+8,.0f}  (NPV today)",
             "  exchange rates:",
             f"    1,000 k u of capital = {1000 / (src.SITES['P-Central']['capex'] / 100) * -d_c / d_e * gwh:.1f}"
             " GWh a year of energy",
             f"    one month later = {d_m / d_e * gwh:.2f} GWh a year of energy"]
    dn = src.SITES["P-North"]
    de_gwh = dn["energy"] - 295.14
    dcap = dn["capex"] + dn["reinforce"] - src.SITES["P-Central"]["capex"]
    lines += ["  P-North against P-Central in these rates:",
              f"    energy +{de_gwh:.1f} GWh a year      {de_gwh / gwh * d_e:+8,.0f}",
              f"    cost incl. grid +{dcap:,.0f}    {dcap / (src.SITES['P-Central']['capex'] / 100) * d_c:+8,.0f}",
              f"    22 months later close         {-22 * d_m:+8,.0f} (approx.)",
              "  the linear rates reproduce the model's answer within a few",
              "  hundred k u: the energy lead buys the grid works, and the",
              "  delay takes the rest - a trade-off made explicit, not hidden",
              "  in a weight"]
    emit("h_tradeoffs", lines)


def score_margin() -> None:
    s = lab_b.score_matrix()
    w = np.array(lab_b.WEIGHTS["developer"])
    tot = ap.weighted(s, w)
    c = lab_b.NAMES.index("P-Central")
    margin = tot[c] - max(t for i, t in enumerate(tot) if i != c)
    lines = ["how far one P-Central score may fall before it loses first place",
             f"(developer weights; lead over the second {margin:.2f}):",
             "  criterion           weight  score  fall needed  possible"]
    for k, (lab, *_r) in enumerate(lab_b.CRITERIA):
        need = margin / w[k]
        lines.append(f"  {lab:18s} {w[k]:6.2f} {s[c, k]:6.2f} {need:12.2f}"
                     f"  {'yes' if need <= s[c, k] else 'no'}")
    lines += ["  no single score can fall far enough: even the energy score",
              "  would have to drop by more than it has; only several errors",
              "  together, or other weights (lab B), could change the first",
              "  place - the evidence effort goes to energy and cost, the two",
              "  heaviest criteria"]
    emit("h_margin", lines)


# [start: tree]
def rollback(stages, value: float) -> float:
    """stages: [(cost, pass probability)] in order; each stage is an
    option to stop, so a branch never goes below zero."""
    ev = value
    for cost, p in reversed(stages):
        ev = max(0.0, p * ev - cost)
    return ev
# [end: tree]


def site_tree() -> None:
    dev_back = 3_000.0                 # development recovered at close
    c = lab_d.site_finance("P-Central")
    n = lab_d.site_finance("P-North")
    keep = src.SITES["P-South"]["energy"]
    src.SITES["P-South"]["energy"] = lab_d.LIFTED
    s_l = lab_d.site_finance("P-South")
    src.SITES["P-South"]["energy"] = keep
    trees = {
        "P-Central": ([(2_200, 0.75), (2_500, 0.80)], c["npv_today"] + dev_back),
        "P-North": ([(120, 0.50), (1_800, 0.60), (2_600, 0.60), (2_500, 0.75)],
                    n["npv_today"] + dev_back),
        "P-South (limit lifted)": ([(950, 0.75), (2_200, 0.70), (2_500, 0.80)],
                                   s_l["npv_today"] + dev_back),
    }
    lines = ["development decision tree per site from today (k u):",
             "  site                    value at close  P(close)  EV of going on"]
    for name, (stages, v) in trees.items():
        p = float(np.prod([q for _, q in stages]))
        lines.append(f"  {name:22s} {v:14,.0f}  {p * 100:7.0f} %  {rollback(stages, v):12,.0f}")
    ev_s = 0.4 * rollback(trees["P-South (limit lifted)"][0],
                          trees["P-South (limit lifted)"][1]) - 250
    lines += [f"  P-South with its 250 k u grid study first (40 % chance the",
              f"  limit is lifted): EV {ev_s:,.0f}",
              "  only P-Central is worth developing at the teaching tariff:",
              "  P-North's surveys, resettlement plan and long wait buy too",
              "  small a chance of too small a value; P-South pays only if",
              "  the grid limit goes and the price is higher - it stays on",
              "  file, unfunded, with its one deciding question"]
    emit("h_tree", lines)


def supply_chain() -> None:
    items = [  # lead time from order, month needed after close (A-314)
        ("main transformers 2 x 63 MVA", 24, 12, 4_000),
        ("wind turbines (12)", 18, 10, 52_000),
        ("HV switchgear", 15, 10, 2_500),
        ("battery containers", 10, 12, 11_000),
        ("PV inverters", 9, 8, 3_000),
        ("PV modules", 6, 6, 18_000),
    ]
    lines = ["supply-chain lead times against the building plan (months):",
             "  item                           lead  needed  early order"]
    at_risk = 0.0
    for name, lead, need, value in items:
        early = max(0, lead - need)
        if early:
            at_risk += 0.10 * value
        lines.append(f"  {name:30s} {lead:4d}  {need:6d}  {early:5d} before close")
    lines += [f"  reservation payments at risk before close (10 %): {at_risk:,.0f} k u",
              "  transformers, turbines and switchgear must be reserved",
              "  before financial close or the plan slips: the developer",
              "  spends at risk, or the lenders accept a later COD; the",
              "  makers' slots and lead times are evidence for the",
              "  financeability gate, not a factory process design"]
    emit("h_supply", lines)


def weather_windows() -> None:
    df = datapack.load_hourly()
    hour = df.index.hour.to_numpy()
    month = df.index.month.to_numpy()
    ws = df["ws_100m_ms"].to_numpy()
    limit = 10.0                       # teaching; the lift plan sets it
    day = (hour >= 7) & (hour < 18)
    ok = day & (ws < limit)
    lines = [f"construction weather windows at hub height (limit {limit:.0f} m/s,",
             "daylight 07-18 h, data pack year; planning statistic only):",
             "  month   usable daylight hours   days with a 6-hour window"]
    rows = []
    days = df.index.strftime("%Y-%m-%d").to_numpy()
    for m in range(1, 13):
        sel = month == m
        share = ok[sel].sum() / day[sel].sum()
        n_ok = 0
        for d in np.unique(days[sel]):
            run = best = 0
            for v in ok[(days == d) & day]:
                run = run + 1 if v else 0
                best = max(best, run)
            n_ok += best >= 6
        rows.append((m, f"{share:.3f}", n_ok))
        lines.append(f"  {m:5d}   {share * 100:21.0f} %   {n_ok:24d}")
    lo = min(r[2] for r in rows)
    hi = max(r[2] for r in rows)
    lines += [f"  best months {', '.join(str(r[0]) for r in rows if r[2] == hi)} ({hi} days),"
              f" worst {', '.join(str(r[0]) for r in rows if r[2] == lo)} ({lo} days)",
              "  erecting 12 turbines at about 3 window days each needs 36",
              "  window days: five weeks in the best season, two months in",
              "  the worst - the erection season is a schedule input; the",
              "  real wind limit comes from the crane maker and the lift",
              "  plan (ch 47)"]
    emit("h_weather", lines)
    csv("ch22-weather.csv", "month,share,days", rows)


def labour() -> None:
    months = np.arange(1, 19)
    curve = np.sin(np.pi * (months - 0.5) / 18) ** 1.5
    workers = 450 * curve / curve.max()
    local_share = 0.40
    pop = {"P-North": 1_000, "P-Central": 3_500, "P-South": 1_500}
    lines = ["labour influx during building (teaching):",
             f"  peak workforce {workers.max():.0f}; worker-months {workers.sum():,.0f};"
             f" local share {local_share:.0%}",
             "  site       local people  outside workers  influx ratio  class"]
    for n, p in pop.items():
        out = workers.max() * (1 - local_share)
        ratio = out / p
        cls = "low" if ratio < 0.10 else "medium" if ratio < 0.20 else "high"
        lines.append(f"  {n:9s} {p:12,d}  {out:15.0f}  {ratio * 100:11.0f} %  {cls}")
    lines += ["  the same workforce is a small addition near a town and a",
              "  large one beside a village: housing, water, health, road",
              "  safety and conduct rules scale with the ratio; more local",
              "  hiring and training lowers it (worker camps and codes of",
              "  conduct are planned with the community, section G)"]
    emit("h_labour", lines)


def funding() -> None:
    c = lab_d.site_finance("P-Central")
    value = c["npv_today"] + 3_000.0
    stages = [(2_200, 0.75), (2_500, 0.80)]
    own = rollback(stages, value)
    # a partner buys 49 % at G3: pays 49 % of the G3 and G4 spend plus a premium
    share, premium = 0.49, 600.0
    partner = rollback([(2_200 * (1 - share) - premium, 0.75), (2_500 * (1 - share), 0.80)],
                       value * (1 - share))
    spend_own = 2_200 + 0.75 * 2_500
    spend_p = 2_200 * (1 - share) + 0.75 * 2_500 * (1 - share)
    lines = ["development funding routes for P-Central from today (k u):",
             "  route                          EV for developer  expected spend",
             f"  own money to close                   {own:8,.0f}        {spend_own:8,.0f}",
             f"  sell 49 % at G3 (+{premium:,.0f} premium)       {partner:8,.0f}"
             f"        {spend_p:8,.0f}",
             "  a partner halves the money at risk and keeps part of the",
             "  value; the premium pays for the risk already taken; a",
             "  development loan is rare - lenders lend against a built",
             "  plant, not against permits that may never come"]
    emit("h_funding", lines)


def export_route() -> None:
    routes = [  # km, overhead or cable, private parcels, crossings, permit months
        ("A direct line", 12.0, "OHL", 2, 3, 10),
        ("B along the road", 15.0, "OHL", 0, 1, 6),
        ("C cable", 12.0, "cable", 2, 3, 8),
    ]
    per_km = {"OHL": 180.0, "cable": 900.0}
    lines = ["export route options for P-Central (teaching):",
             "  route              km  type   parcels  crossings  cost k u  months"]
    for name, km, kind, parcels, cross, months in routes:
        cost = km * per_km[kind] + 60 * cross
        lines.append(f"  {name:17s} {km:4.0f}  {kind:5s} {parcels:8d} {cross:10d}"
                     f" {cost:9,.0f} {months:7d}")
    cost = {r[0][0]: r[1] * per_km[r[2]] + 60 * r[4] for r in routes}
    lines += ["  route B is 3 km longer but crosses no private land and one",
              f"  road: it costs {cost['B'] - cost['A']:,.0f} k u more than A and saves 4 months of",
              "  land and permits on a chain with no slack left (section C);",
              f"  the cable avoids visual effects at {cost['C'] / cost['A']:.1f} times the cost; the",
              "  grid operator confirms the connection scope and the",
              "  boundary of who builds and owns each part (ch 23)"]
    emit("h_route", lines)


def cumulative() -> None:
    projects = [("Plant P (12 turbines)", 12, 0.05),
                ("existing farm (fictional, 40 turbines)", 40, 0.08),
                ("planned farm (fictional, 25 turbines)", 25, 0.06)]
    threshold = 4.0                    # teaching: per year, set by specialists
    lines = ["cumulative effects: invented collision index of one species",
             f"(teaching numbers; threshold {threshold:.0f} a year set by the specialists):",
             "  project                                    turbines  index  sum"]
    total = 0.0
    for name, nt, rate in projects:
        total += nt * rate
        lines.append(f"  {name:42s} {nt:8d} {nt * rate:6.1f} {total:5.1f}")
    lines += ["  Plant P alone adds 0.6 - far below the threshold - but the",
              "  existing farm plus Plant P reaches 3.8 and the planned farm",
              "  would take the sum past 4: the effect of one project is",
              "  judged with the others in the same area (ch 33), and the",
              "  study and the authority decide, not this screen"]
    emit("h_cumulative", lines)


def grievances() -> None:
    cats = ["dust", "road safety", "land access", "jobs", "water", "noise"]
    p = [0.25, 0.20, 0.15, 0.20, 0.10, 0.10]
    n = 48
    cat = RNG.choice(len(cats), size=n, p=p)
    days = np.round(RNG.gamma(2.0, 9.0, size=n)).astype(int) + 2
    target = 30
    lines = ["grievance log of a building year (invented entries, n = 48):",
             "  category      cases  median days  closed within 30 days"]
    for k, c_ in enumerate(cats):
        d = days[cat == k]
        if len(d):
            lines.append(f"  {c_:12s} {len(d):6d} {np.median(d):12.0f} {np.mean(d <= target) * 100:14.0f} %")
    lines += [f"  all: median {np.median(days):.0f} days, {np.mean(days <= target) * 100:.0f} %"
              f" within {target} days; slowest {days.max()} days",
              "  a grievance channel is known, free, safe and answered: the",
              "  log shows whether it works; repeated categories point to",
              "  a cause to fix, not only to cases to close"]
    emit("h_grievance", lines)


if __name__ == "__main__":
    cost_ranges()
    schedule_risk()
    tradeoffs()
    score_margin()
    site_tree()
    supply_chain()
    weather_windows()
    labour()
    funding()
    export_route()
    cumulative()
    grievances()
