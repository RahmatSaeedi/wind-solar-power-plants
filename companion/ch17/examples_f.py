"""Chapter 17, further lessons - the industrial self-supply variant (how
much of a factory's demand Plant P could meet hour by hour), a faulty
load series and the checks that catch its faults, the regional load's
reactive demand and the transformer check in MVA, the plant's own use
from its own generation against imports, and a verification matrix by
project phase.

Run from the project root:   python -m companion.ch17.examples_f
Writes companion/ch17/expected/f_*.txt and diagrams/data/ch17-*.csv.
Synthetic data A-284 (factory, faults, power factor), A-285.
"""
from __future__ import annotations

from collections import Counter

import numpy as np

from companion.ch15 import sources as s15
from companion.ch17 import lab_d, sources as src
from companion.ch17.common import csv, emit
from plantp import demand as dm


def self_supply() -> None:
    """The factory buys Plant P's output up to its demand each hour; the
    rest is exported; shortfalls are imported (teaching contract)."""
    f = src.factory()
    gen = np.clip(s15.plant_year()["net"], 0, None)
    used = np.minimum(gen, f)
    lines = ["industrial self-supply variant (factory A-284, model 15.1 output):",
             f"  factory: {f.sum() / 1e3:.1f} GWh, peak {f.max():.1f} MW,"
             f" load factor {dm.metrics(f)['load_factor']:.3f}",
             f"  covered by the plant {used.sum() / 1e3:.1f} GWh"
             f" ({100 * used.sum() / f.sum():.1f} % of the factory's energy)",
             f"  still imported {(f - used).sum() / 1e3:.1f} GWh; exported surplus"
             f" {(gen - used).sum() / 1e3:.1f} GWh",
             f"  hours fully covered {int((gen >= f).sum())} of 8760",
             "  a flat industrial load and a variable plant meet only part of",
             "  the time: the contract prices the matched energy, the import",
             "  and the export separately; storage and a larger plant raise",
             "  the cover with falling returns (chapters 19 and 21)"]
    emit("f_selfsupply", lines)
    hour = np.arange(8760) % 24
    csv("ch17-selfsupply.csv", "h,factory,plant,used",
        [(hh, f"{f[hour == hh].mean():.2f}", f"{gen[hour == hh].mean():.2f}",
          f"{used[hour == hh].mean():.2f}") for hh in range(24)])


def faulty_series() -> dict:
    """The regional load with five faults (A-284): a 6-hour gap, a spike
    of 10x, a stuck value for 30 hours, quarter-hour values mislabelled
    as hourly in one week (x4), and a repeated hour at a clock change."""
    p = src.regional()["total"].copy()
    p[1000:1006] = np.nan
    p[2000] = p[2000] * 10
    p[3000:3030] = p[3000]
    p[4000:4168] = p[4000:4168] * 4
    p = np.insert(p, 2018, p[2017])                     # repeated hour
    return {"series": p}


# [start: qc]
def load_checks(p) -> dict:
    """Simple checks on an hourly load series."""
    p = np.asarray(p, float)
    ok = np.isfinite(p)
    med = np.nanmedian(p)
    runs, k = 0, 1
    while k < len(p):                      # runs of 6 equal values
        j = k
        while j < len(p) and p[j] == p[j - 1]:
            j += 1
        runs += int(j - k + 1 >= 6)
        k = j + 1
    return {"length": len(p), "gaps": int((~ok).sum()),
            "spikes": int((p[ok] > 3 * med).sum()),
            "stuck_runs": runs,
            "energy_vs_median": float(np.nansum(p) / (med * len(p)))}
# [end: qc]


def qc() -> None:
    clean = load_checks(src.regional()["total"])
    bad = load_checks(faulty_series()["series"])
    lines = ["checks on the clean and the faulty regional load:",
             "  check                      clean     faulty"]
    for k in ("length", "gaps", "spikes", "stuck_runs"):
        lines.append(f"  {k:24s} {clean[k]:7d}   {bad[k]:7d}")
    lines.append(f"  {'energy / (median x n)':24s} {clean['energy_vs_median']:7.3f}"
                 f"   {bad['energy_vs_median']:7.3f}")
    lines += ["  length 8761 shows the repeated hour; the spike check also",
              "  flags the week of quarter-hour values (x4); the stuck run is",
              "  found; the energy ratio moves: compare with the meter's",
              "  billing totals before any number is used"]
    emit("f_qc", lines)


def reactive() -> None:
    """Regional load power factor 0.92 lagging (A-284): apparent power on
    the two 63 MVA transformers, normal and with one out."""
    p = src.regional()["total"]
    s = p / 0.92
    lines = ["the regional load in MVA (power factor 0.92, A-284):",
             f"  peak {p.max():.2f} MW = {s.max():.2f} MVA; reactive"
             f" {np.sqrt(s.max() ** 2 - p.max() ** 2):.2f} Mvar",
             f"  two transformers (126 MVA): loading {100 * s.max() / 126:.1f} %",
             f"  one out (63 MVA): loading {100 * s.max() / 63:.1f} %",
             f"  growth that reaches 63 MVA with one out: about"
             f" {100 * ((63 / s.max()) ** (1 / 10) - 1):.2f} % a year over ten years",
             "  checking in MW at unity power factor (section A) was too kind:",
             "  equipment carries current, which follows MVA"]
    emit("f_reactive", lines)


def own_use() -> None:
    """The plant's own loads (A-284) covered by its own generation in the
    same hour, and the rest imported."""
    pl = src.plant_loads_hourly()
    own = sum(pl.values())
    r = s15.plant_year()
    gen_mv = r["mv"]                                     # before own use
    covered = np.where(gen_mv > own, own, np.clip(gen_mv, 0, None))
    lines = ["the plant's own loads, from its own output or imported:",
             f"  own loads {own.sum():,.0f} MWh a year (classes of section A)",
             f"  covered in the same hour by generation {covered.sum():,.0f} MWh",
             f"  imported {(own - covered).sum():,.0f} MWh in"
             f" {int((gen_mv < own).sum())} hours",
             "  most own use never crosses the meter; the import is small but",
             "  priced by its own contract; the auxiliary supply must still",
             "  take the full load from the grid when the plant is still"]
    emit("f_ownuse", lines)


def verification() -> None:
    phases = {"REQ-001": ("design", "test at commissioning"),
              "REQ-002": ("design", "analysis, then first-year comparison"),
              "REQ-003": ("procurement", "type test, then site test"),
              "REQ-004": ("design", "study, then site measurement"),
              "REQ-005": ("procurement", "type test and plant study"),
              "REQ-006": ("commissioning", "demonstration"),
              "REQ-007": ("commissioning", "test"),
              "REQ-008": ("construction", "inspection and test"),
              "REQ-009": ("operation", "analysis of three months"),
              "REQ-010": ("operation", "analysis of repair records"),
              "REQ-011": ("operation", "inspection of meter readings"),
              "REQ-012": ("commissioning", "test at the receptor")}
    reg = {r.rid: r for r in lab_d.register()}
    c = Counter(v[0] for v in phases.values())
    lines = ["verification matrix: the phase where each requirement is first",
             "  proven and how:"]
    for rid, (ph, how) in phases.items():
        lines.append(f"  {rid}  {reg[rid].priority:6s}  {ph:13s}  {how}")
    lines.append("  by phase: " + ", ".join(f"{k} {v}" for k, v in c.items()))
    lines += ["  half are proven only at commissioning or later: the design",
              "  must keep the evidence route open (test points, data, access)"]
    emit("f_verification", lines)


if __name__ == "__main__":
    self_supply()
    qc()
    reactive()
    own_use()
    verification()
