"""Chapter 41, lab D - production data of a module lot.

1. write the flash file of a 3,000-module lot (synthetic, with data
   faults planted: duplicate serials, missing values, a reading in kW)
2. parse and validate it
3. find the flash tester's drift from the golden-module checks
4. flag outliers with robust z-scores and trace each to a failure mode
5. power classes before and after the drift correction
6. cell mismatch in a string and module mismatch in a string
7. the factory control plan and the plant's incoming-inspection checklist

Run from the project root:   python -m companion.ch41.lab_d
Writes companion/ch41/data/flash_lot.csv, expected/d_*.txt and plot data.
Teaching values (A-446, A-447); nothing here is a real maker's data.
"""
from __future__ import annotations

import csv as csvmod
import math
import random
from collections import Counter
from statistics import mean, median, pstdev

from companion.ch41 import sources as src
from companion.ch41.common import HERE, csv, emit
from plantp import pvfab as fab
from plantp import quality as qa
from plantp.mppt import Curve

DATA_FILE = HERE / "data" / "flash_lot.csv"
GOLDEN_TRUE = 551.0                 # W, the golden module's own value


# ------------------------------------------------------ 1. write the file
def write_lot(seed: int = 4107) -> None:
    rng = random.Random(seed)
    DATA_FILE.parent.mkdir(exist_ok=True)
    rows = []
    for k, p in enumerate(src.FLASH):
        drift = 1.0 + (2.4 / 552.4 if k >= 2400 else 0.0)
        s = math.sqrt(p / (552.4 * drift)) if p > 400 else 1.0
        isc = 13.98 * s * (1 + rng.gauss(0, 0.002)) * drift
        voc = 49.90 * s * (1 + rng.gauss(0, 0.002))
        if p < 400:                                  # a shorted bypass diode
            voc = 49.90 * 2 / 3 * (1 + rng.gauss(0, 0.002))
        if k in (402, 1555, 2049):                   # higher-bin cells
            isc = 13.98 * 1.017
        if k in (211, 655, 1023, 1490, 1902, 2777):  # cracks: current lost
            isc = 13.98 * (p / 552.4) * (1 + rng.gauss(0, 0.002))
        ff = p / (voc * isc)
        rows.append([f"PVM-{k + 1:05d}", k, f"{p:.1f}", f"{voc:.2f}",
                     f"{isc:.3f}", f"{ff:.4f}", src.EL_GRADES[k],
                     f"{25 + rng.gauss(0, 0.3):.1f}"])
    rows[1777][2] = ""                              # missing
    rows[2650][3] = ""                              # missing
    rows[1200][2] = f"{float(rows[1200][2]) / 1000:.4f}"   # kW slipped in
    rows.insert(901, list(rows[900]))               # duplicate serial
    rows.insert(2101, list(rows[2100]))             # duplicate serial
    golden = []
    for g in range(0, 3000, 100):
        shift = 2.4 if g >= 2400 else 0.0
        golden.append(["GOLDEN", g, f"{GOLDEN_TRUE + shift + rng.gauss(0, 0.3):.1f}",
                       "", "", "", "", "25.0"])
    with open(DATA_FILE, "w", encoding="utf-8", newline="") as fh:
        w = csvmod.writer(fh, lineterminator="\n")
        w.writerow(["serial", "seq", "pmax_w", "voc_v", "isc_a", "ff",
                    "el_grade", "t_c"])
        w.writerows(rows + golden)


# ------------------------------------------------------ 2. parse, validate
# [start: parse]
def parse(path=DATA_FILE):
    """Read the flash file; return good records, golden checks and a list
    of data problems (never silently fixed)."""
    good, golden, problems, seen = [], [], [], set()
    with open(path, encoding="utf-8") as fh:
        for row in csvmod.DictReader(fh):
            if row["serial"] == "GOLDEN":
                golden.append((int(row["seq"]), float(row["pmax_w"])))
                continue
            if row["serial"] in seen:
                problems.append((row["serial"], "duplicate serial"))
                continue
            seen.add(row["serial"])
            if not row["pmax_w"] or not row["voc_v"]:
                problems.append((row["serial"], "missing value"))
                continue
            p = float(row["pmax_w"])
            if p < 10:
                problems.append((row["serial"], f"Pmax {p} - kW, not W?"))
                continue
            good.append(dict(serial=row["serial"], seq=int(row["seq"]),
                             p=p, voc=float(row["voc_v"]),
                             isc=float(row["isc_a"]), el=row["el_grade"]))
    return good, golden, problems
# [end: parse]


def validate() -> dict[str, int]:
    write_lot()
    good, golden, problems = parse()
    lines = [f"flash file: {len(good) + len(problems):,} module rows, "
             f"{len(golden)} golden-module checks",
             f"  usable records {len(good):,}; data problems {len(problems)}:"]
    for s, what in problems:
        lines.append(f"    {s}: {what}")
    lines += ["  each problem goes back to the factory with the serial: a",
              "  duplicate may hide a module never flashed, a value in kW",
              "  is a software or unit change - the data is evidence only",
              "  when the file itself is checked first"]
    emit("d_validate", lines)
    return dict(good=len(good), problems=len(problems))


# ------------------------------------------------------ 3. tester drift
def drift() -> dict[str, float]:
    _, golden, _ = parse()
    before = [p for s, p in golden if s < 2400]
    after = [p for s, p in golden if s >= 2400]
    lim = 3 * pstdev(before)
    first = next(s for s, p in golden if abs(p - GOLDEN_TRUE) > max(lim, 1.0))
    shift = mean(after) - mean(before)
    lines = ["golden module flashed every 100 modules (its value 551.0 W)",
             f"  checks before seq 2400: mean {mean(before):.1f} W, sd "
             f"{pstdev(before):.2f}",
             f"  first check outside +-{max(lim, 1.0):.1f} W: seq {first}",
             f"  shift after it: {shift:+.2f} W ({shift / GOLDEN_TRUE:+.2%})",
             "  the modules flashed since the last good check read high:",
             "  they are corrected or re-flashed after the reference is",
             "  restored - and the cause (reference cell, lamp, spectrum)",
             "  is found before the line restarts"]
    emit("d_drift", lines)
    return dict(first=first, shift=shift)


def corrected(good, d):
    out = []
    for r in good:
        r = dict(r)
        if r["seq"] >= d["first"]:
            k = 1 - d["shift"] / GOLDEN_TRUE
            r["p"], r["isc"] = r["p"] * k, r["isc"] * k
        out.append(r)
    return out


# ------------------------------------------------- 4. outliers and causes
# [start: diagnose]
def diagnose(r, med_voc: float, med_isc: float) -> str:
    """A first guess at the failure mode from the shape of the reading."""
    if r["voc"] < 0.8 * med_voc:
        return "bypass diode shorted (a third of Voc gone)"
    if r["el"] == "C":
        return "cracked cells (EL grade C, current lost)"
    if r["isc"] > 1.01 * med_isc:
        return "cells of a higher bin (Isc high)"
    return "unexplained - re-flash and inspect"
# [end: diagnose]


def outliers() -> dict[str, int]:
    good, _, _ = parse()
    d = dict(first=2400, shift=2.4)
    d.update(drift_quiet())
    fixed = corrected(good, d)
    ps = [r["p"] for r in fixed]
    flags = fab.flag_outliers(ps)
    mv = median(r["voc"] for r in fixed)
    mi = median(r["isc"] for r in fixed)
    causes = Counter()
    lines = [f"robust z of Pmax (median {median(ps):.1f} W) after the drift "
             "correction",
             f"  flagged {len(flags)} of {len(ps):,} (|z| > 3.5):",
             "  serial      Pmax W   Voc V   Isc A   EL  first guess"]
    for k in flags:
        r = fixed[k]
        why = diagnose(r, mv, mi)
        causes[why.split(" (")[0]] += 1
        lines.append(f"  {r['serial']}  {r['p']:6.1f}  {r['voc']:6.2f}  "
                     f"{r['isc']:6.3f}  {r['el']:2s}  {why.split(' (')[0]}")
    raw = fab.flag_outliers([r["p"] for r in good])
    lines += [f"  without the drift correction {len(raw)} flags, some only "
              "because",
              "  the last 600 read high; the shape of each reading (Voc, Isc,",
              "  EL) points at the process step to look at"]
    emit("d_outliers", lines)
    rows = [(r["seq"], round(r["p"], 1)) for r in good]
    csv("ch41-flash.csv", "seq,p", rows[::3])
    return dict(flags=len(flags), raw=len(raw), **causes)


def drift_quiet() -> dict[str, float]:
    _, golden, _ = parse()
    before = [p for s, p in golden if s < 2400]
    after = [p for s, p in golden if s >= 2400]
    lim = max(3 * pstdev(before), 1.0)
    first = next(s for s, p in golden if abs(p - GOLDEN_TRUE) > lim)
    return dict(first=first, shift=mean(after) - mean(before))


# ------------------------------------------------- 5. power classes
def classes() -> dict[str, int]:
    good, _, _ = parse()
    fixed = corrected(good, drift_quiet())

    def cls(p):
        return int(p // 5 * 5)
    before = Counter(cls(r["p"]) for r in good if r["p"] > 400)
    after = Counter(cls(r["p"]) for r in fixed if r["p"] > 400)
    moved = sum(1 for a, b in zip(good, fixed)
                if a["p"] > 400 and cls(a["p"]) != cls(b["p"]))
    lines = ["power classes (label = class, tolerance 0/+5 W)",
             "  class W   as flashed   corrected"]
    for c in sorted(set(before) | set(after)):
        lines.append(f"  {c:7d}   {before[c]:10d}   {after[c]:9d}")
    lines += [f"  {moved} modules change class with the correction: they",
              "  were labelled one class too high - the labels and the",
              "  flash records of those serials are reissued before",
              "  shipping (the label is a claim the buyer will test)"]
    emit("d_classes", lines)
    return dict(moved=moved)


# --------------------------------- 6. mismatch: cells and modules in strings
def cell_string(scales, half: bool = True) -> list[Curve]:
    k = 0.5 if half else 1.0
    return [Curve(13.98 * k * s, 49.90 / 72, 13.11 * k * s, 41.96 / 72)
            for s in scales]


def mismatch_cells(n: int = 24, trials: int = 40, seed: int = 4108):
    out = {}
    for name, sd in (("binned 0.1 A", 0.002), ("mixed bins", 0.008),
                     ("unsorted", 0.02)):
        rng = random.Random(seed)
        losses = [fab.cell_mismatch_loss(cell_string(
            [rng.gauss(1, sd) for _ in range(n)])) for _ in range(trials)]
        out[name] = mean(losses)
    rng = random.Random(seed)
    scales = [rng.gauss(1, 0.002) for _ in range(n)]
    scales[5] = 0.9
    out["one cell 10 % low"] = fab.cell_mismatch_loss(cell_string(scales))
    return out


def module_curve(r) -> Curve:
    s = r["isc"] / 13.98
    return Curve(r["isc"], r["voc"], 13.11 * s, 41.96 * r["voc"] / 49.90)


def mismatch_modules(seed: int = 4109):
    good, _, _ = parse()
    fixed = [r for r in corrected(good, drift_quiet()) if r["p"] > 400
             and r["el"] != "C"]
    rng = random.Random(seed)
    pick = rng.sample(fixed, 26)
    srt = sorted(fixed, key=lambda r: r["isc"])[1300:1326]
    diode = [r for r in corrected(good, drift_quiet()) if r["p"] < 400][0]
    with_diode = pick[:25] + [diode]
    return {"random 26": fab.mismatch_loss([module_curve(r) for r in pick]),
            "sorted by Isc": fab.mismatch_loss([module_curve(r) for r in srt]),
            "one diode-short module": fab.mismatch_loss(
                [module_curve(r) for r in with_diode])}


def mismatch() -> dict[str, float]:
    c = mismatch_cells()
    m = mismatch_modules()
    lines = ["mismatch by the ch 15 curves",
             "  24 half cells in series, no reverse breakdown (one diode's",
             "  string):"]
    for k, v in c.items():
        lines.append(f"    {k:22s} {max(v, 0.0):7.2%}")
    lines.append("  26 modules from the lot in one string:")
    for k, v in m.items():
        lines.append(f"    {k:22s} {max(v, 0.0):7.2%}")
    lines += ["  binning keeps the cell loss small; one weak cell drags",
              "  its whole string down to its current - the reason cracked",
              "  and low cells are sorted out before stringing; a string",
              "  of lot modules loses little; a diode-short module adds",
              "  almost no mismatch - its loss is its own missing third,",
              "  a defect for the flash and the monitoring to find"]
    emit("d_mismatch", lines)
    return {**c, **m}


# --------------------------------- 7. control plan and incoming inspection
# [start: control]
CONTROL = [  # characteristic, method, frequency, reaction
    ("cell current bin", "cell tester + golden cell", "every cell; shift",
     "hold box, re-sort"),
    ("string joint", "peel test", "per stringer each shift",
     "stop, re-test last lot"),
    ("cracks before lamination", "EL image", "every layup",
     "repair string or scrap"),
    ("gel content", "solvent extraction sample", "per laminator daily",
     "signal: hold, trace"),
    ("frame and sealant", "gauge, visual", "first piece + hourly",
     "contain since last good"),
    ("bypass diodes", "diode check", "every module", "repair box, re-test"),
    ("power and label", "flash + golden module", "every module; 100",
     "drift: hold, re-flash"),
    ("cracks after lamination", "EL image", "every module",
     "grade; C is rejected"),
    ("insulation", "insulation test", "every module", "reject, analyse"),
]
INCOMING = [  # check at the plant, how, sample
    ("documents vs packing list", "serials, classes, BOM rev", "every"),
    ("certificate covers this BOM", "BOM rev vs tested BOM", "every lot"),
    ("container and pallets", "seals, shock tags, damage", "every"),
    ("transport cracks", "EL of a pallet", "1 a container"),
    ("power vs label", "lab flash, decision rule", "12 per 10 MWp"),
    ("flash file", "parse, drift, outliers", "every file"),
    ("visual and connectors", "glass, frame, type match", "AQL plan"),
]
# [end: control]


def plans() -> dict[str, int]:
    n, c = qa.find_plan(0.01, 0.05)
    lines = ["factory control plan for the PVM-550 line (summary)",
             "  characteristic            method                    "
             "frequency / reaction"]
    for ch, how, freq, react in CONTROL:
        lines += [f"  {ch:25s} {how:25s} {freq}",
                  f"  {'':51s} {react}"]
    lines += ["", "plant incoming-inspection checklist",
              "  check                         how                          "
              "sample"]
    for chk, how, smp in INCOMING:
        lines.append(f"  {chk:29s} {how:28s} {smp}")
    lines += [f"  visual AQL plan per container (620 modules): n = {n}, "
              f"accept <= {c}",
              "  the factory plan watches the process; the plant's checks",
              "  test what the factory's records claim - the two meet at",
              "  the serial number and the flash record"]
    emit("d_plans", lines)
    return dict(n=n, c=c, rows=len(CONTROL), checks=len(INCOMING))


if __name__ == "__main__":
    validate()
    drift()
    outliers()
    classes()
    mismatch()
    plans()
