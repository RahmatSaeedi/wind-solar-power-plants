"""Chapter 53, lesson D (worked example): repair or replace the twelve main
gearboxes at operating year 18, compared over the years left with
lifecycle cost, downtime energy, remaining life and disposal.

Options, per gearbox:
  A  run to failure, repair on failure (380 k u, 900 h down; a repair
     takes the virtual age back by 60 % - teaching restoration factor)
  B  run to failure, replace on failure (620 k u, 900 h down; new unit)
  C  planned replacement now, in low-wind months (620 k u, 700 h down at
     June wind; new unit)
Failures from the conditional Weibull of each unit's virtual age; energy
valued at 70 u/MWh to year 20 and 45 after (ch 21); discounted at 7.5 %.

Run from the project root:   python -m companion.ch53.lab_d
Writes companion/ch53/expected/d_*.txt and diagrams/data/ch53-decision.csv.
Teaching values (A-541).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch15 import sources as s15
from companion.ch53 import sources as src
from companion.ch53.common import csv, emit

RUN = 0.93 * 8760                        # running hours a year
DISPOSAL_K = -8.0 + 2.0                  # steel credit, oil disposal (k u per old gearbox)


def turbine_mw():
    y = s15.plant_year()
    w = np.asarray(y["w_av"], float) / 12
    m = np.asarray(y["month"])
    return float(w.mean()), float(w[m == 5].mean())      # mean, June


def next_failure(v: float, k: float, c: float, u: float) -> float:
    """Running hours to the next failure of a unit of virtual age v."""
    return c * ((v / c) ** k - math.log(u)) ** (1 / k) - v


def simulate(option: str, years: int, n_sim: int = 2000, seed: int = 541,
             k: float = None, restore: float = None, price_after: float = None) -> dict:
    g = src.GEARBOX
    k = g["k"] if k is None else k
    c = g["c"]
    restore = g["life_after_repair"] if restore is None else restore
    p_after = src.PRICE_AFTER if price_after is None else price_after
    mw, mw_june = turbine_mw()
    rng = np.random.default_rng(seed)
    horizon = years * RUN
    costs, downs, fails = [], [], []

    def price(t_h):
        year = src.YEAR_NOW + t_h / RUN
        return src.PRICE if year <= src.PPA_YEARS else p_after

    def disc(t_h):
        return (1 + src.RATE) ** -(t_h / RUN)

    for _ in range(n_sim):
        cost = down = nf = 0.0
        for _unit in range(g["units"]):
            t, v = 0.0, g["hours"]
            if option == "C":
                cost += (g["replace_k"] + DISPOSAL_K) * disc(0)
                cost += g["down_replace_h"] * mw_june * price(0) / 1000
                down += g["down_replace_h"]
                v = 0.0
            while True:
                dt = next_failure(v, k, c, rng.random())
                if t + dt > horizon:
                    break
                t += dt
                nf += 1
                d = disc(t)
                cost += g["down_repair_h"] * mw * price(t) / 1000 * d
                down += g["down_repair_h"]
                if option == "A":
                    cost += g["repair_k"] * d
                    v = (v + dt) * (1 - restore)
                else:
                    cost += (g["replace_k"] + DISPOSAL_K) * d
                    v = 0.0
        costs.append(cost)
        downs.append(down)
        fails.append(nf)
    return dict(mean=float(np.mean(costs)), p90=float(np.percentile(costs, 90)),
                down=float(np.mean(downs)), fails=float(np.mean(fails)))


# ------------------------------------------------ 1. options and inputs
def options() -> dict:
    g = src.GEARBOX
    mw, june = turbine_mw()
    lines = ["decision: the twelve main gearboxes at year 18 (each run "
             f"{g['hours']:,.0f} h)",
             f"  Weibull k {g['k']}, c {g['c']:,.0f} h (fitted fleet data, ch 37/52)",
             f"  A repair on failure   {g['repair_k']:.0f} k u, {g['down_repair_h']:.0f} h down, "
             f"restores {g['life_after_repair']:.0%} of life",
             f"  B replace on failure  {g['replace_k']:.0f} k u, {g['down_repair_h']:.0f} h down",
             f"  C replace now         {g['replace_k']:.0f} k u, {g['down_replace_h']:.0f} h down "
             "in June",
             f"  energy lost per down hour: mean {mw:.2f} MW, June {june:.2f} MW;",
             f"  {src.PRICE:.0f} u/MWh to year 20, {src.PRICE_AFTER:.0f} after; discount {src.RATE:.1%}",
             f"  disposal of each old gearbox: steel credit and oil {DISPOSAL_K:+.0f} k u"]
    emit("d_options", lines)
    return dict(mw=mw, june=june)


# ------------------------------------------------ 2. result over the years to 25
def result(years: int = 7, name: str = "d_result") -> dict:
    out = {o: simulate(o, years) for o in "ABC"}
    best = min(out, key=lambda o: out[o]["mean"])
    lines = [f"present cost of the fleet over {years} years (k u), 2,000 simulated fleets",
             "  option   mean cost   P90 cost   failures   down h"]
    lines += [f"  {o:6s} {r['mean']:10,.0f} {r['p90']:10,.0f} {r['fails']:10.1f} {r['down']:9,.0f}"
              for o, r in out.items()]
    lines += [f"  lowest mean cost: {best}; difference to the next "
              f"{sorted(r['mean'] for r in out.values())[1] - out[best]['mean']:,.0f} k u",
              "  spread P90 - mean: " + ", ".join(f"{o} {r['p90'] - r['mean']:,.0f}"
                                               for o, r in out.items())]
    emit(name, lines)
    return out


# ------------------------------------------------ 3. life extension to 30 years
def extension() -> dict:
    out = result(12, "d_extension")
    return out


# ------------------------------------------------ 4. sensitivity
def sensitivity() -> dict:
    rows = []
    for label, kw in (("base", {}), ("shape k 2.0", dict(k=2.0)), ("shape k 3.0", dict(k=3.0)),
                      ("repair restores 30 %", dict(restore=0.3)),
                      ("price after PPA 60", dict(price_after=60.0))):
        r = {o: simulate(o, 7, n_sim=800, **kw)["mean"] for o in "ABC"}
        rows.append((label, r["A"], r["B"], r["C"], min(r, key=r.get)))
    csv("ch53-decision.csv", "case,A,B,C", [(i + 1, round(a), round(b), round(c))
                                           for i, (_, a, b, c, _) in enumerate(rows)])
    lines = ["sensitivity over 7 years: mean present cost (k u) and the cheapest option",
             "  case                      A        B        C    cheapest"]
    lines += [f"  {l:22s} {a:8,.0f} {b:8,.0f} {c:8,.0f}    {w}" for l, a, b, c, w in rows]
    winners = {w for *_, w in rows}
    lines += [f"  cheapest across the cases: {', '.join(sorted(winners))}"]
    emit("d_sens", lines)
    return dict(rows=rows, winners=winners)


# ------------------------------------------------ 5. disposal and evidence plan
def evidence() -> list:
    items = [("Weibull fit with its censored records and interval", "ch 37/52 CMMS"),
             ("oil and vibration trends of each gearbox", "lesson B of ch 52"),
             ("repair quotes and the repair shop's restoration record", "supplier"),
             ("crane and low-wind window availability", "ch 31, ch 51"),
             ("price after the PPA, or a new contract", "owner, ch 21"),
             ("permit and grid position if repowered instead", "lesson B, ch 54-58"),
             ("waste route for 12 old gearboxes and 14 t of oil", "lesson C"),
             ("decision record with the options, numbers and assumptions", "this lab")]
    lines = ["evidence the decision rests on, and where it comes from"]
    lines += [f"  {k + 1}. {a} [{b}]" for k, (a, b) in enumerate(items)]
    lines += ["  the decision is re-taken when any of them changes - a",
              "  decision record without its assumptions cannot be re-taken"]
    emit("d_evidence", lines)
    return items


if __name__ == "__main__":
    options()
    result()
    extension()
    sensitivity()
    evidence()
