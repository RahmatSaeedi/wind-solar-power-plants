"""Chapter 39, manufacturing and industrialisation: what the buyer
verifies in each supplier's factory (and which of chapters 40-48 teaches
the process behind it), a sampling plan and a mean-power check for PV
modules at the factory, and what source inspection is worth.

Run from the project root:   python -m companion.ch39.examples_v
Writes companion/ch39/expected/v_*.txt.
Teaching values (A-429); fictional factories; no process recipes.
"""
from __future__ import annotations

import math

from scipy import stats

from companion.ch39 import sources as src  # noqa: F401  (plantp on path)
from companion.ch39.common import emit
from plantp import quality as qa

# ------------------------------------------ verification across packages
# [start: verify]
VERIFY = [  # package, what the buyer verifies at the factory, H/W, chapter
    ("PV modules", "EL images, flash test, BOM lock", 2, 41),
    ("wind turbines", "blade inspection, drive-train test", 3, 42),
    ("unit transformers", "heat run, losses, insulation", 3, 43),
    ("inverters", "routine test, firmware version", 2, 44),
    ("battery containers", "cell traceability, module test", 3, 45),
    ("MV cables, switchgear", "routine tests, PD where applicable", 2, 46),
    ("structures, foundations", "weld and coating records", 1, 47),
    ("SCADA, metering", "FAT of the integrated system", 2, 48),
]
# [end: verify]


def verification() -> dict[str, float]:
    days_point = 1.5                       # inspector-days a hold/witness
    lines = ["what the buyer verifies at each factory (H/W points a batch)",
             "  package                  points  chapter  verifies"]
    total = 0
    for pkg, what, pts, ch in VERIFY:
        total += pts
        lines.append(f"  {pkg:24s} {pts:6d}  {ch:7d}  {what}")
    lines += [f"  {total} points a batch, about {total * days_point:.0f} "
              "inspector-days with travel",
              "  the buyer verifies the controls, the factory owns them:",
              "  chapters 40-48 show what each control proves, so the",
              "  inspector knows what a record should look like"]
    emit("v_verify", lines)
    return dict(points=total, days=total * days_point)


# ------------------------------------------------ PV module sampling
def module_power() -> dict[str, float]:
    n_lot = 3000
    n, c = qa.find_plan(0.01, 0.04)
    mean, sd, k, name = 548.2, 2.4, 50, 550.0
    t = stats.t.ppf(0.95, k - 1)
    lower = mean - t * sd / math.sqrt(k)
    lines = [f"PV modules at the factory: lots of {n_lot:,}",
             f"  defect sampling (AQL 1 %, LTPD 4 %): n = {n}, accept if"
             f" <= {c}",
             f"  power: {k} modules flashed, mean {mean} W, sd {sd} W",
             f"  one-sided 95 % lower bound of the mean: {lower:.1f} W",
             f"  nameplate {name:.0f} W with no negative tolerance: the lot",
             f"  is {'held' if lower < name else 'released'}; the whole lot's"
             " power is in doubt,",
             "  not one module - the sample says the line is set low",
             "  (flash calibration or cell bin), a question for ch 41"]
    emit("v_modules", lines)
    return dict(n=n, c=c, lower=lower)


# ------------------------------------------ what source inspection is worth
def inspection_value() -> dict[str, float]:
    p_sys, consequence = 0.05, 400.0       # systematic fault; k u at site
    find_factory = 0.6                     # share found by the inspector
    cost_day, days = 1.2, 27.0             # k u an inspector-day
    saved = p_sys * find_factory * consequence * len(VERIFY)
    cost = cost_day * days
    lines = ["what source inspection is worth over the eight packages",
             f"  chance of a systematic fault in a package: {p_sys:.0%}; cost",
             f"  if it reaches site: {consequence:.0f} k u; found at the "
             f"factory: {find_factory:.0%}",
             f"  expected saving: {saved:.0f} k u; inspection: {days:.0f} "
             f"days x {cost_day} = {cost:.0f} k u",
             "  inspection pays here because a site fault is costly; it",
             "  does not replace the factory's own control - it checks it"]
    emit("v_value", lines)
    return dict(saved=saved, cost=cost)


# --------------------------- business-interruption cover and the spare
def interruption() -> dict[str, float]:
    day_ku = 5.0 * 0.22 * 24 * 70 / 1000          # one PV block, k u a day
    wait, indemnity = 60, 365                      # days
    deduct = 25.0                                  # k u on the damage claim
    lines = ["a unit transformer fails in operation: who carries the loss?",
             f"  one block out costs {day_ku:.2f} k u a day (5 MW, CF 0.22)",
             "  case                       days out  insured  not insured"]
    out = {}
    for label, days in (("no spare (new unit)", 30 * 7), ("spare on site", 14)):
        insured = max(0, min(days, indemnity) - wait) * day_ku
        lost = days * day_ku
        out[label] = lost - insured
        lines.append(f"  {label:26s} {days:8d}  {insured:7.0f}  {lost - insured:11.0f}")
    lines += [f"  (business interruption pays after a {wait}-day waiting period;",
              f"  the repair claim carries a {deduct:.0f} k u deductible)",
              "  without a spare the owner still carries the first 60 days;",
              "  with one, the outage ends inside the waiting period - the",
              "  spare, not the policy, protects the cash flow, and the",
              "  lenders read both (concepts only, not advice)"]
    emit("v_interrupt", lines)
    return out


# ------------------------------- on-site stock of inverter power modules
def module_stock() -> dict[int, float]:
    from companion.ch39.examples_s import poisson_cdf
    from companion.ch39.common import csv
    modules, rate, lead_w = 60, 0.08, 12            # in service; a year; weeks
    mu = modules * rate * lead_w / 52
    short_cost = 0.25 * 5.0 * 0.22 * 24 * 70 / 1000 * 7 * lead_w / 2
    lines = [f"on-site stock of inverter power modules ({modules} in service)",
             f"  failures a year {rate:.0%} each; restock lead {lead_w} weeks:"
             f" mean demand {mu:.2f}",
             "  stock  chance of no stock-out  holding k u"]
    out, rows = {}, []
    for k in range(0, 6):
        p = poisson_cdf(k, mu)
        out[k] = p
        rows.append((k, round(p, 4)))
        lines.append(f"  {k:5d}  {p:22.1%}  {8.0 * k:11.0f}")
    csv("ch39-stock.csv", "k,p", rows)
    lines += [f"  three modules give 97 %; a stock-out derates a block by a",
              f"  quarter for half a lead time on average (~{short_cost:.0f} k u)",
              "  the stock level is a service requirement in the contract",
              "  (lesson E), checked at each restock, not a hope"]
    emit("v_stock", lines)
    return out


if __name__ == "__main__":
    verification()
    module_power()
    inspection_value()
    interruption()
    module_stock()
