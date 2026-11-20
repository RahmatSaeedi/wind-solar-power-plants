"""Chapter 18, lab E - compare two architectures under common assumptions
(the chapter's first worked example):

  A1 separate: AC-coupled battery on its own 33 kV bays, 240 mm2
     collector, two 63 MVA transformers, single-circuit line;
  A2 compact:  DC-coupled battery in the PV blocks, 630 mm2 collector,
     one 125 MVA transformer (no spare), double-circuit line.

Energy items come from model 15.1 and sections A, B and F; costs and
reliability are teaching values (A-287, A-288); the price is A-281.
The lab then splits the comparison into separable choices, scores the
criteria money does not show, and states the baseline (D-022).

Run from the project root:   python -m companion.ch18.lab_e
Writes companion/ch18/expected/e_*.txt.
"""
from __future__ import annotations

import numpy as np

from companion.ch15 import sources as s15
from companion.ch18 import examples_a as ea, examples_f as ef, sources as src
from companion.ch18.common import emit
from plantp.yieldrisk import annuity

C, R = src.COST, src.REL
YEARLY = 1.0 / annuity(C["rate"], C["years"]) + C["opex_share"]   # per k u


def trafo_unserved(kind: str) -> float:
    """Expected export lost to main-transformer failures, MWh a year."""
    p = np.minimum(s15.plant_year()["poc"], 100.0).clip(0, None)
    if kind == "2x63":
        return float(2 * R["trafo_fail"] * R["trafo_repair_h"]
                     * np.clip(p - 60.0, 0, None).mean())
    return float(R["trafo_fail"] * R["trafo_repair_h"] * p.mean())


# [start: choices]
def choices() -> list:
    """Each separable choice: (name, A1 option, A2 option, energy gained
    by A2 in MWh a year, extra capex of A2 in k u)."""
    c1 = ef.collector_option("33 kV 240 mm2")
    c2 = ef.collector_option("33 kV 630 mm2")
    l1 = ef.export_option("overhead line, single circuit")
    l2 = ef.export_option("overhead line, double circuit")
    b1, b2 = ea.year("AC"), ea.year("DC")
    return [
        ("collector", "240 mm2", "630 mm2", c1["loss"] - c2["loss"],
         c2["cost"] - c1["cost"]),
        ("export line", "single", "double",
         (l1["loss"] + l1["out"]) - (l2["loss"] + l2["out"]),
         1000 * (l2["cost"] - l1["cost"])),
        ("transformers", "2 x 63", "1 x 125",
         trafo_unserved("2x63") - trafo_unserved("1x125"),
         C["trafo_125"] - 2 * C["trafo_63"]),
        ("coupling", "AC", "DC", b2["back"] - b1["back"],
         20 * C["dcdc_per_mw"]
         - (20 * C["bess_inv_per_mw"] + C["bess_ac_mv"])),
    ]
# [end: choices]


def common() -> None:
    lines = ["common assumptions for both architectures:",
             "  resource and losses: model 15.1 (D-019), S1 battery 20 MW / 40 MWh",
             "  export limit 100 MW, 132 kV line 7.06 km, W2b collector",
             f"  price {C['price']:.0f} u/MWh (A-281); capex to a yearly cost at"
             f" {100 * C['rate']:.0f} %, {C['years']} years,",
             f"    plus opex {100 * C['opex_share']:.0f} % a year:"
             f" {1000 * YEARLY:.1f} u a year per k u",
             "  battery counted here only for energy that would be lost;",
             "  its market uses (chapters 19-21) are scored, not priced"]
    emit("e_common", lines)


def separable() -> None:
    lines = ["A2 against A1, choice by choice (k u a year; + favours A2):",
             "  choice        A1       A2        MWh/yr  value  capex/yr    net"]
    tot_e = tot_v = tot_c = 0.0
    for name, o1, o2, de, dk in choices():
        value = de * C["price"] / 1000
        cost = dk * YEARLY
        tot_e, tot_v, tot_c = tot_e + de, tot_v + value, tot_c + cost
        lines.append(f"  {name:12s}  {o1:8s} {o2:8s} {de:7,.0f} {value:6.1f}"
                     f"  {cost:8.1f}  {value - cost:6.1f}")
    lines += [f"  {'total':12s}  {'':8s} {'':8s} {tot_e:7,.0f} {tot_v:6.1f}"
              f"  {tot_c:8.1f}  {tot_v - tot_c:6.1f}",
              "  A2 gains energy but costs more each year; the totals hide",
              "  that the choices are separable: the coupling pays in A2,",
              "  the larger cable and the second circuit do not, and the",
              "  single transformer saves money but loses energy"]
    emit("e_separable", lines)


# [start: matrix]
CRITERIA = {        # weight, score A1, score A2 (1 poor .. 5 good), teaching
    "yearly money (above)":           (25, 4, 3),
    "tail risk (longest outage)":     (20, 5, 2),
    "battery market uses":            (15, 5, 2),
    "maintainability and spares":     (10, 4, 3),
    "interfaces and integration":     (10, 4, 2),
    "technology maturity":            (10, 5, 4),
    "expansion":                      (10, 4, 3),
}
# [end: matrix]


def matrix() -> None:
    lines = ["weighted criteria (scores 1-5, teaching judgements):",
             "  criterion                       weight  A1  A2"]
    t1 = t2 = 0
    for k, (w, a, b) in CRITERIA.items():
        lines.append(f"  {k:31s} {w:5d}   {a:2d}  {b:2d}")
        t1, t2 = t1 + w * a, t2 + w * b
    lines += [f"  weighted total (out of 500)            {t1:3d} {t2:3d}"]
    lines += ["  A1 scores at least as high on every criterion, so no choice",
              "  of weights makes A2 win; only different scores could, and",
              "  each score must be argued in the record, not tuned"]
    emit("e_matrix", lines)


def baseline() -> None:
    gain = {n: (de * C["price"] / 1000 - dk * YEARLY) for n, _, _, de, dk in choices()}
    take = [n for n, v in gain.items() if v > 0]
    lines = ["baseline (D-022, conditional on U-065..U-068):",
             "  A1 as the reference architecture: AC-coupled battery,",
             "  240 mm2 33 kV collector, two 63 MVA transformers,",
             "  single-circuit 132 kV overhead line",
             "  choices whose money favours A2: " + (", ".join(take) or "none"),
             "  the transformers stay two: a few k u a year do not buy",
             "  a six-month outage risk (section B)",
             "  kept open: the coupling (DC pays a little for lost energy",
             "  but loses the battery's wind and market uses), cable size",
             "  after the cable offers, line circuits after the operator's",
             "  security rules; each change goes through change control"]
    emit("e_baseline", lines)


if __name__ == "__main__":
    common()
    separable()
    matrix()
    baseline()
