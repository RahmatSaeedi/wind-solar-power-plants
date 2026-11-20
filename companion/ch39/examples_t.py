"""Chapter 39, further lessons on service, connection works, labour due
diligence, financeable contracts and supplier data in numbers: an
availability target split by failure weight, a year of downtime
simulated with and without spares on site, a last-time buy, outage
windows for the connection works, how many sites to audit and a
working-hours sample, three guarantees that measure different things,
delay damages down the contract chain, and the timeliness of supplier
data.

Run from the project root:   python -m companion.ch39.examples_t
Writes companion/ch39/expected/t_*.txt and diagrams/data/ch39-*.csv.
Teaching values (A-429 to A-432); concepts, not legal advice.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch39 import sources as src  # noqa: F401  (plantp on path)
from companion.ch39.common import csv, emit
from companion.ch39.examples_s import poisson_cdf

# ------------------------------------------- weighted RAM allocation
PARTS = {  # part: (failures a year expected, mean hours down a failure)
    "inverter": (1.6, 30.0), "unit transformer": (0.01, 2000.0),
    "MV switchgear": (0.05, 48.0), "SCADA link": (2.0, 6.0)}


def allowed_hours(target: float = 0.97) -> dict[str, float]:
    """Downtime budget of each part, weighted by its expected downtime."""
    budget_h = (1 - target) * 8760
    down = {p: f * h for p, (f, h) in PARTS.items()}
    return {p: budget_h * d / sum(down.values()) for p, d in down.items()}


def ram_weighted() -> dict[str, float]:
    target = 0.97
    budget_h = (1 - target) * 8760
    down = {p: f * h for p, (f, h) in PARTS.items()}
    total = sum(down.values())
    lines = [f"PV block target {target:.0%}: {budget_h:.0f} h a year of "
             "downtime to share",
             "  part              expected h  share of budget  allowed h"]
    out = {}
    for p, d in down.items():
        allowed = budget_h * d / total
        out[p] = allowed
        lines.append(f"  {p:16s} {d:10.1f}  {d / total:15.1%}  "
                     f"{allowed:9.1f}")
    lines += [f"  expected downtime {total:.0f} h: inside the budget, with "
              f"{budget_h - total:.0f} h margin",
              "  an equal split (lesson E) would give the transformer 66 h",
              "  and the SCADA link 66 h; weighting by expected downtime",
              "  asks each supplier for what its part can deliver, and the",
              "  transformer's rare, long outage is covered by the spare"]
    emit("t_ram", lines)
    return out


# -------------------------------------- a year of downtime, simulated
def downtime(spares_on_site: bool, years: int = 2000, seed: int = 391):
    rng = np.random.default_rng(seed)
    f, _ = PARTS["inverter"]
    out = []
    for _ in range(years):
        n = rng.poisson(f)
        hours = 0.0
        for _ in range(n):
            respond = rng.lognormal(math.log(18), 0.5)
            parts = 0.0 if spares_on_site else rng.lognormal(math.log(96), 0.6)
            repair = rng.lognormal(math.log(6), 0.4)
            hours += respond + parts + repair
        out.append(hours)
    return np.array(out)


def service_sim() -> dict[str, float]:
    allowed = allowed_hours()["inverter"]     # weighted share, lesson above
    lines = ["inverter downtime a year, 2,000 simulated years",
             "  case               mean h   90 % h   chance over budget"]
    out, rows = {}, []
    for label, flag in (("spares on site", True), ("spares at depot", False)):
        d = downtime(flag)
        p90 = float(np.quantile(d, 0.9))
        over = float(np.mean(d > allowed))
        out[label] = over
        lines.append(f"  {label:16s} {d.mean():7.1f}  {p90:7.1f}  "
                     f"{over:17.1%}")
        hist, edges = np.histogram(d, bins=np.arange(0, 601, 25))
        rows.append(hist / len(d))
    csv("ch39-downtime.csv", "h,site,depot",
        [(int(e), round(a, 4), round(b, 4))
         for e, a, b in zip(np.arange(0, 600, 25), rows[0], rows[1])])
    lines += [f"  budget {allowed:.0f} h (the weighted share above): with",
              "  stock on site the bad years stay inside it; with parts at",
              "  a depot even the average year misses it. The contract",
              "  asks for response, repair and stock on site, not only",
              "  for an availability figure"]
    emit("t_service", lines)
    return out


# ----------------------------------------------------- last-time buy
def last_time_buy() -> dict[str, float]:
    boards, rate, years = 10 * 6, 0.02, 20          # a board-year rate
    mu = boards * rate * years
    k = 0
    while poisson_cdf(k, mu) < 0.95:
        k += 1
    lines = ["last-time buy of inverter control boards (end of production)",
             f"  {boards} boards in service, {rate:.0%} fail a year, "
             f"{years} years left",
             f"  expected failures: {mu:.0f}; to cover them with 95 %: "
             f"{k} boards",
             f"  buying only the mean ({mu:.0f}) runs short "
             f"{1 - poisson_cdf(int(mu), mu):.0%} of the time",
             "  the obsolescence clause of lesson E gives the notice that",
             "  makes this purchase possible; storage and testing of the",
             "  stock are part of its cost"]
    emit("t_ltb", lines)
    return dict(mu=mu, k=k)


# ---------------------------------------------------- outage windows
def outages() -> dict[str, float]:
    need = {"33 kV bay at the utility substation": 3,
            "line crossing under the 132 kV": 2,
            "protection tests end to end": 2}
    windows = {"Mar": 6, "Apr": 6, "Oct": 5, "Nov": 5}   # days the grid offers
    lines = ["outage windows for the connection works (days)"]
    total = sum(need.values())
    for k, v in need.items():
        lines.append(f"  need {v}  {k}")
    lines.append("  offered: " + ", ".join(f"{m} {d}" for m, d in
                                           windows.items()))
    longest = max(windows.values())
    lines += [f"  needed {total} days in sequence (tests come last); "
              f"offered {sum(windows.values())},",
              f"  but no window is longer than {longest} days: the works take",
              "  March and April together, and a week's slip at the bay",
              "  sends the end-to-end tests to October - six months. The",
              "  works plan is fixed with the grid operator before the",
              "  contracts are signed (ch 28)"]
    emit("t_outage", lines)
    return dict(need=total, offered=sum(windows.values()))


# ------------------------------------------- audits and hours samples
def audits_needed(prevalence: float, conf: float = 0.9) -> int:
    """Sites to audit for a chance `conf` to find at least one bad one."""
    return math.ceil(math.log(1 - conf) / math.log(1 - prevalence))


def wilson(k: int, n: int, z: float = 1.645) -> tuple[float, float]:
    p = k / n
    den = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return mid - half, mid + half


def labour_samples() -> dict[str, float]:
    lines = ["how many supplier sites to audit (90 % to find one, if any)",
             "  share of sites with a problem   sites to audit"]
    out = {}
    for prev in (0.30, 0.20, 0.10, 0.05):
        n = audits_needed(prev)
        out[prev] = n
        lines.append(f"  {prev:30.0%}   {n:13d}")
    k, n = 9, 120
    lo, hi = wilson(k, n)
    lines += ["  a timesheet sample at one sub-supplier: 9 of 120 weeks",
              f"  over 60 hours = {k / n:.1%} (90 % interval {lo:.1%} to "
              f"{hi:.1%})",
              "  the finding is the sample and its interval - a verified",
              "  fact for the remediation plan, kept apart from the",
              "  supplier's declaration that 'no one works overtime'"]
    emit("t_labour", lines)
    out["lo"], out["hi"] = lo, hi
    return out


# ------------------------------------ three guarantees, three measures
def guarantees() -> dict[str, float]:
    year = dict(hours=8760, grid_out_h=300, forced_h=120, planned_h=90,
                energy_lost_forced=0.020, energy_lost_grid=0.025)
    epc = 1 - year["forced_h"] / (year["hours"] - year["grid_out_h"])
    om = 1 - year["energy_lost_forced"]
    ppa = 1 - year["energy_lost_forced"] - year["energy_lost_grid"]
    lines = ["one year, three guarantees that measure different things",
             f"  EPC: time-based, grid outages excluded: {epc:.2%} "
             "(guarantee 98 %)",
             f"  O&M: energy-based, grid excluded:      {om:.2%} "
             "(guarantee 97 %)",
             f"  PPA: contracted energy delivered:       {ppa:.2%} "
             "(minimum 96 %)",
             "  EPC and O&M pass; the PPA falls short because grid",
             "  outages count against the plant there - the gap belongs",
             "  to no contractor unless the grid contract or insurance",
             "  covers it: the interface matrix names its owner (ch 21)"]
    emit("t_guarantee", lines)
    return dict(epc=epc, om=om, ppa=ppa)


# ------------------------------------- delay damages down the chain
def ld_chain() -> dict[str, float]:
    weeks = 8
    owner_loss_week = 145.0 + 40.0          # lost energy + debt and PPA, k u
    epc_rate, epc_price = 0.0025, 60_000.0   # EPC damages a week, contract
    epc = weeks * epc_rate * epc_price
    sub_ld = weeks * 0.005 * 1_160
    lines = [f"delay damages down the chain, {weeks} weeks late (k u)",
             f"  owner's loss: {weeks} x {owner_loss_week:.0f} = "
             f"{weeks * owner_loss_week:,.0f}",
             f"  EPC pays the owner {epc_rate:.2%} a week of 60,000: "
             f"{epc:,.0f}",
             f"  transformer supplier pays the EPC 0.5 % of 1,160: "
             f"{sub_ld:.1f}",
             f"  owner covered {epc / (weeks * owner_loss_week):.0%}; "
             f"EPC recovers {sub_ld / epc:.1%} of what it pays",
             "  the EPC carries the difference: why it buffers the",
             "  schedule and watches the supplier, not the damages;",
             "  the lenders read this chain before financial close"]
    emit("t_ldchain", lines)
    return dict(owner=weeks * owner_loss_week, epc=epc, sub=sub_ld)


# -------------------------------------------- supplier data timeliness
DATA_DUE = {  # item: (week needed, week delivered) after the order
    "general arrangement": (6, 5), "rating plate data": (20, 22),
    "routine test report": (32, 31), "FAT record": (32, 36),
    "O&M manual": (40, 52), "spares list with part numbers": (40, 44),
    "3D model": (10, 9), "asset register rows": (40, 47)}


def data_timeliness() -> dict[str, float]:
    late = {k: d - n for k, (n, d) in DATA_DUE.items() if d > n}
    lines = ["supplier data of the U-A order: needed and delivered (week)"]
    for k, (n, d) in DATA_DUE.items():
        lines.append(f"  {k:30s} need {n:2d}  got {d:2d}"
                     f"  {'late ' + str(d - n) if d > n else ''}")
    share = 1 - len(late) / len(DATA_DUE)
    lines += [f"  on time: {share:.0%}; late items wait for the plant, not",
              "  the other way round: commissioning needs the FAT record",
              "  and O&M needs the manual and the register rows (lesson I);",
              "  the contract ties a payment to accepted data, not to",
              "  a count of files"]
    emit("t_data", lines)
    return dict(on_time=share, late=sum(late.values()))


if __name__ == "__main__":
    ram_weighted()
    service_sim()
    last_time_buy()
    outages()
    labour_samples()
    guarantees()
    ld_chain()
    data_timeliness()
