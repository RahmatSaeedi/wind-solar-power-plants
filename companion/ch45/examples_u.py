"""Chapter 45, round u: field returns by cause and the control that would
have stopped each, the value of recycled material by chemistry, screening
aged modules for a second life, an invariant that catches a bug in a new
version of the simulator, consistency rules for the BMS configuration,
the cost of finding one defect at each stage, coulombic efficiency and
life, and the coverage of interface signals at the factory test.

Run from the project root:   python -m companion.ch45.examples_u
Writes companion/ch45/expected/u_*.txt.
Teaching values (A-478 to A-481); nothing here is a real battery's data.
"""
from __future__ import annotations

import numpy as np

from companion.ch45 import lab_d
from companion.ch45 import sources as src
from companion.ch45.common import csv, emit
from plantp import cellmfg as cf

C, B = src.CELL, src.BUILD


# ------------------------------------------------ 1. returns by cause
RETURNS = [   # cause, returns in two years, control that would stop it
    ("weld or busbar joint", 9, "every weld measured (lesson B)"),
    ("BMS sensor or wiring", 7, "sensor map check at assembly"),
    ("cell leaker (self-discharge)", 4, "14-day rest and K file"),
    ("BMS configuration", 3, "limit check and fingerprint"),
    ("HVAC fan or controller", 3, "HVAC test at the factory"),
    ("contactor or fuse", 2, "functional test, certificates"),
    ("transport damage", 1, "shock logs, receiving inspection"),
]


def returns() -> dict:
    tot = sum(r[1] for r in RETURNS)
    lines = ["module and rack returns of a fleet in two years by cause",
             f"  (synthetic, {tot} returns)",
             "  cause                          n   share   cumulative"]
    cum = 0
    out = {}
    for cause, n, _ in RETURNS:
        cum += n
        out[cause] = n
        lines.append(f"  {cause:28s} {n:3d}   {n / tot:5.0%}   {cum / tot:10.0%}")
    csv("ch45-returns.csv", "k,n", [(k + 1, r[1]) for k, r in enumerate(RETURNS)])
    top2 = RETURNS[0][1] + RETURNS[1][1]
    lines += [f"  the two largest causes are {top2 / tot:.0%} of returns, and both are",
              "  assembly controls of the integrator, not the cell: the cell",
              "  is not where most trouble starts - the joints and the",
              "  wiring around it are (as for inverters, ch 44)"]
    emit("u_returns", lines)
    return dict(total=tot, top2=top2 / tot)


# ------------------------------------------------ 2. recycled value by chemistry
def recycle_value() -> dict:
    """Teaching material values (k u per t recovered) and costs (k u per t of
    cells processed)."""
    value = {"cathode (LFP)": 0.6, "graphite": 0.2, "copper foil": 7.0,
             "aluminium foil and case": 1.6, "binders, tabs, other": 0.1}
    process_cost = 1.2
    n_cells = B["s_module"] * B["m_rack"] * B["r_container"]
    masses = {k: v * n_cells / 1000 for k, v in src.MATERIALS.items()}      # t
    rec = cf.recovered(masses, src.RATES)
    worth = sum(rec[k] * value.get(k, 0.0) for k in rec)
    cost = sum(masses.values()) * process_cost
    nmc_cathode = 18.0                                                    # k u/t
    worth_nmc = worth - rec["cathode (LFP)"] * value["cathode (LFP)"] + \
        rec["cathode (LFP)"] * nmc_cathode
    lines = ["value of one container's cells at the recycler (teaching prices)",
             f"  recovered {sum(rec.values()):.1f} t worth {worth:.1f} k u; "
             f"processing {sum(masses.values()):.1f} t costs {cost:.1f} k u",
             f"  net for LFP: {worth - cost:+.1f} k u a container",
             f"  the same mass with a nickel-cobalt cathode: {worth_nmc - cost:+.1f} "
             "k u",
             "  an LFP battery is likely to cost money to recycle, not earn",
             "  it: the take-back fee and who pays it belong in the purchase",
             "  contract, with the route and its records (ch 39, ch 53)"]
    emit("u_recycle", lines)
    return dict(net_lfp=worth - cost, net_nmc=worth_nmc - cost)


# ------------------------------------------------ 3. second-life screening
def second_life(seed: int = 4509, n: int = 768, soh_min: float = 0.70,
                r_max: float = 1.6) -> dict:
    """Aged modules: health and resistance growth (teaching distributions)."""
    rng = np.random.default_rng(seed)
    soh = rng.normal(0.74, 0.035, n)
    r_rel = rng.normal(1.35, 0.15, n) + np.clip(0.74 - soh, 0, None) * 3
    ok = (soh >= soh_min) & (r_rel <= r_max)
    lines = [f"{n} modules after 20 years (synthetic): health mean "
             f"{soh.mean():.0%}, resistance x {r_rel.mean():.2f}",
             f"  second-life screen: health >= {soh_min:.0%} and resistance "
             f"<= x {r_max}",
             f"  pass on health {int((soh >= soh_min).sum())}, on resistance "
             f"{int((r_rel <= r_max).sum())}, on both {int(ok.sum())} "
             f"({ok.mean():.0%})",
             "  the modules that pass carry their whole history - lot,",
             "  temperatures, replacements: without the record a buyer of",
             "  used modules must test every one, and the price falls",
             "  (ch 19 second life, ch 53)"]
    emit("u_second", lines)
    return dict(passed=int(ok.sum()), share=float(ok.mean()))


# ------------------------------------------------ 4. a bug the invariant catches
# [start: v11]
class SocSimV11(cf.SocSim):
    """Version 1.1 'tidied' the charge branch and applied the efficiency
    twice (a planted bug)."""

    def step(self, i_a: float, dt_s: float) -> float:
        if i_a > 0:
            ah = i_a * dt_s / 3600.0
            room = (self.hi - self.soc) * self.q_ah / self.eta_c
            take = min(ah, max(room, 0.0))
            self.soc += take * self.eta_c * self.eta_c / self.q_ah   # bug
            self.ah_in += take
            self.refused_ah += ah - take
            return take * 3600.0 / dt_s
        return super().step(i_a, dt_s)
# [end: v11]


def regression() -> dict:
    out = {}
    for name, cls in (("v1.0", cf.SocSim), ("v1.1", SocSimV11)):
        sim = cls(q_ah=C["q_ah"], soc=0.30)
        for i in lab_d.day_profile():
            sim.step(i, 900.0)
        out[name] = (sim.soc, sim.balance_error(0.30),
                     sim.lo - 1e-9 <= sim.soc <= sim.hi + 1e-9)
    lines = ["the same day run on two versions of the educational simulator",
             "  version   end SOC   balance error Ah   in window"]
    for name, (s, e, w) in out.items():
        lines.append(f"  {name:7s}   {s:7.4f}   {e:16.3f}   {'yes' if w else 'NO'}")
    lines += ["  v1.1 stays in the window and looks fine; only the balance",
              "  invariant shows that it loses charge on every charging step",
              "  - a test on the outcome alone would have passed it; the",
              "  invariant is in the test list of every release"]
    emit("u_regress", lines)
    return out


# ------------------------------------------------ 5. configuration rules
CONFIG = {   # setting: value (a delivered configuration with planted faults)
    "v_trip_hi": 3.60, "v_alarm_hi": 3.62, "v_balance_start": 3.40,
    "v_alarm_lo": 2.70, "v_trip_lo": 2.60, "t_trip_charge_hi": 50.0,
    "t_alarm_charge_hi": 47.0, "t_trip_charge_lo": 2.0, "i_trip_a": 160.0,
    "i_alarm_a": 170.0, "soc_lo": 0.10, "soc_hi": 0.90,
}
# [start: rules]
RULES = [   # name, rule as a function of the configuration c
    ("alarm before trip, high voltage",
     lambda c: c["v_alarm_hi"] < c["v_trip_hi"]),
    ("alarm before trip, low voltage",
     lambda c: c["v_alarm_lo"] > c["v_trip_lo"]),
    ("balance below the high alarm",
     lambda c: c["v_balance_start"] < c["v_alarm_hi"]),
    ("alarm before trip, temperature",
     lambda c: c["t_alarm_charge_hi"] < c["t_trip_charge_hi"]),
    ("charge window ordered",
     lambda c: c["t_trip_charge_lo"] < c["t_trip_charge_hi"]),
    ("alarm before trip, current",
     lambda c: c["i_alarm_a"] < c["i_trip_a"]),
    ("SOC window ordered",
     lambda c: 0 <= c["soc_lo"] < c["soc_hi"] <= 1),
]
# [end: rules]


def config_rules() -> dict:
    res = [(name, rule(CONFIG)) for name, rule in RULES]
    bad = [n for n, ok in res if not ok]
    lines = ["consistency rules on a delivered BMS configuration (planted faults)",
             "  rule                                 holds"]
    for name, ok in res:
        lines.append(f"  {name:36s} {'yes' if ok else 'NO'}")
    lines += [f"  {len(bad)} rules broken: an alarm set beyond its own trip never",
              "  warns - the trip comes first; rules like these run on every",
              "  configuration file before it is loaded, alongside the check",
              "  against the cell's limits (lesson B)"]
    emit("u_config", lines)
    return dict(bad=bad)


# ------------------------------------------------ 6. cost of a find by stage
def find_cost() -> dict:
    stages = [("cell maker, rest test", 0.05), ("integrator, receiving", 0.15),
              ("module assembly", 1.0), ("factory test of the container", 4.0),
              ("site acceptance", 12.0), ("operation, before an incident", 25.0),
              ("after an incident", 400.0)]
    csv("ch45-cost.csv", "k,cost", [(k + 1, c) for k, (_, c) in enumerate(stages)])
    lines = ["cost of dealing with one leaking cell, by where it is found "
             "(k u, teaching)",
             "  stage                              cost k u   x first stage"]
    for name, c in stages:
        lines.append(f"  {name:34s} {c:8.2f}   {c / stages[0][1]:13.0f}")
    lines += ["  each stage that misses multiplies the cost; the cheapest",
              "  find is a cell maker's rest test that runs its full time -",
              "  paying for fourteen days of racks is cheap insurance",
              "  against the last row (lesson B, lab D)"]
    emit("u_cost", lines)
    return dict(stages=stages)


# ------------------------------------------------ 7. coulombic efficiency and life
def ce_life(fade_to: float = 0.20) -> dict:
    lines = ["cycles to lose 20 % if each cycle loses (1 - CE) of capacity",
             "  (teaching, linear)",
             "  coulombic efficiency   cycles to 80 %"]
    out = {}
    for ce in (0.9990, 0.9995, 0.99990, 0.99995, 0.99997):
        cyc = fade_to / (1 - ce)
        out[ce] = cyc
        lines.append(f"  {ce:20.5f}   {cyc:14,.0f}")
    lines += ["  telling a 4,000-cycle cell from a 6,700-cycle one means",
              "  measuring CE to about 0.00002 (20 ppm): charge counting of",
              "  that precision is a laboratory test - early-life evidence",
              "  of cycle life comes from such tests, not from a few months",
              "  of cycling (ch 19)"]
    emit("u_ce", lines)
    return out


# ------------------------------------------------ 8. interface signals at FAT
SIGNALS = [   # signal, tested at FAT
    ("rack contactor status", True), ("rack fault", True),
    ("insulation alarm", True), ("cell over-temperature", True),
    ("HVAC fault", True), ("door switch", True),
    ("off-gas detector alarm", False), ("fire panel fault", False),
    ("emergency stop", True), ("PCS trip request", True),
    ("auxiliary supply lost", False), ("BMS watchdog", True),
]


def fat_signals() -> dict:
    tested = [s for s, t in SIGNALS if t]
    untested = [s for s, t in SIGNALS if not t]
    lines = [f"interface signals of one container: {len(SIGNALS)}; tested end to "
             f"end at the factory: {len(tested)}",
             "  not tested: " + ", ".join(untested),
             "  the untested ones are the signals between makers - the",
             "  detector's and the fire panel's (another supplier) and the",
             "  auxiliary supply (the plant): each gets a test at site with",
             "  both owners present, written into the site test plan",
             "  (ch 19 fire interfaces, ch 50)"]
    emit("u_signals", lines)
    return dict(untested=untested)


if __name__ == "__main__":
    returns()
    recycle_value()
    second_life()
    regression()
    config_rules()
    find_cost()
    ce_life()
    fat_signals()
