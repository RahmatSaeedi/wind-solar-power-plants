"""Chapter 28, lesson A: the POC as a Thevenin source at its maximum and
minimum strength, checks on a submitted data sheet, and the state of the
study inputs by owner and status.

Run from the project root:   python -m companion.ch28.examples_a
Writes companion/ch28/expected/a_*.txt. Teaching values (A-341).
"""
from __future__ import annotations

import math
from collections import Counter

from companion.ch28 import register as reg
from companion.ch28 import sources as src
from companion.ch28.common import emit
from plantp import gridstudy as gs


def thevenin() -> None:
    lines = ["the POC seen as a Thevenin source (132 kV, base 100 MVA)",
             "  case   S_sc MVA   X/R   z pu      R ohm   X ohm   I_k kA   SCR (100 MW)"]
    zb = 132.0 ** 2 / 100
    for case, g in src.GRID.items():
        z = gs.thevenin(g["s_sc"], g["xr"])
        ik = g["s_sc"] / (math.sqrt(3) * 132)
        lines.append(f"  {case:5s}  {g['s_sc']:8.0f}   {g['xr']:3.0f}   {abs(z):6.4f}   "
                     f"{z.real * zb:5.2f}   {z.imag * zb:5.1f}   {ik:6.2f}   {g['s_sc'] / 100:12.1f}")
    lines += ["  the maximum case sizes equipment (largest fault current);",
              "  the minimum case tests protection sensitivity, voltage",
              "  changes and control stability (weakest grid) - a study",
              "  asks the operator for both, with the outages behind each"]
    emit("a_thevenin", lines)


# [start: checks]
SHEET = {   # a submitted data sheet with planted errors (teaching)
    "main transformer": dict(s_mva=63.0, uk_pct=12.0, base_mva=100.0),
    "line": dict(km_drawing=7.06, km_sheet=7.60, c_per_km=9.0, c_unit="uF"),
    "units": dict(wind_in_model=13, wind_on_one_line=12, mv_kv=34.5),
    "grid": dict(s_sc_max=1500.0, s_sc_min=1700.0, xr=8.0),
}


def check_sheet(sh: dict) -> list[tuple[str, bool, str]]:
    t, ln = sh["main transformer"], sh["line"]
    u, g = sh["units"], sh["grid"]
    c_ok = ln["c_unit"] == "nF" or ln["c_per_km"] < 0.05
    return [
        ("uk stated on own rating", t["base_mva"] == t["s_mva"],
         f"uk {t['uk_pct']} % on {t['base_mva']:.0f} MVA, not 63"),
        ("line length agrees",
         abs(ln["km_drawing"] - ln["km_sheet"]) < 0.05,
         f"{ln['km_sheet']} km sheet, {ln['km_drawing']} km drawing"),
        ("line capacitance plausible", c_ok,
         f"{ln['c_per_km']} {ln['c_unit']}/km: 1,000 x too large"),
        ("unit count agrees",
         u["wind_in_model"] == u["wind_on_one_line"],
         f"{u['wind_in_model']} in model, "
         f"{u['wind_on_one_line']} on one-line"),
        ("MV nominal voltage", u["mv_kv"] == 33.0,
         f"{u['mv_kv']} kV, the plant is 33 kV"),
        ("min below max", g["s_sc_min"] < g["s_sc_max"],
         f"min {g['s_sc_min']:.0f} > max {g['s_sc_max']:.0f} MVA"),
        ("X/R plausible", 3 <= g["xr"] <= 20, f"X/R {g['xr']}"),
    ]
# [end: checks]


def checks() -> None:
    res = check_sheet(SHEET)
    lines = ["checks on a submitted study data sheet (planted errors, teaching)",
             "  check                          result   note"]
    for name, ok, note in res:
        lines.append(f"  {name:30s} {'pass' if ok else 'FAIL':6s}   {'' if ok else note}")
    n_fail = sum(not ok for _, ok, _ in res)
    lines += [f"  {n_fail} of {len(res)} checks fail; each would have cost a study run",
              "  (or worse, passed into an approved result) - a submission",
              "  is checked for units, bases, counts and consistency with",
              "  the drawings before any study starts"]
    emit("a_checks", lines)


def inputs_state() -> None:
    by = Counter((i[2], i[3]) for i in reg.INPUTS)
    owners = ("operator", "plant", "OEM")
    states = ("received", "requested", "assumed", "missing")
    lines = ["state of the study inputs for Plant P's POC (register of 30 items)",
             "  owner      " + "".join(f"{s:>11s}" for s in states) + "   total"]
    for o in owners:
        row = [by[(o, s)] for s in states]
        lines.append(f"  {o:9s}  " + "".join(f"{v:11d}" for v in row) + f"   {sum(row):5d}")
    blocked = sorted({s for i in reg.INPUTS if i[3] in ("missing", "requested")
                      for s in i[5].split()})
    op_open = sum(1 for i in reg.INPUTS if i[2] == "operator" and i[3] != "received")
    lines += ["  studies waiting for at least one input: " + ", ".join(blocked),
              f"  {op_open} of the operator's 13 items are still open: a study started",
              "  now runs on assumptions, and each is logged with the",
              "  result it could change"]
    emit("a_inputs", lines)


if __name__ == "__main__":
    thevenin()
    checks()
    inputs_state()
