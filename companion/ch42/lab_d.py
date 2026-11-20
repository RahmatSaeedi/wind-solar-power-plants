"""Chapter 42, lab D - manufacturing and condition data of the turbine.

1. run-in vibration of ten gearboxes on the bench: spectra, the lines at
   1x, 2x and the mesh with its sidebands, and a diagnosis per unit
2. the blade quality plan: steps, hold/witness/record, method, record
3. nonconformity escalation: disposition authority, deadline, ageing
4. the transport and installation interface map, with the nacelle-tower
   interface items added to the tower-section traveler of ch 30

Run from the project root:   python -m companion.ch42.lab_d
Writes companion/ch42/expected/d_*.txt and diagrams/data/ch42-*.csv.
Teaching values (A-455, A-456); synthetic signals; no test procedures.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch42 import sources as src
from companion.ch42.common import csv, emit
from plantp import turbinemfg as tm

F1 = 1155.0 / 60.0
MESH = 27 * F1


# ------------------------------------------------ 1. run-in vibration
# [start: diagnose]
def lines_of(x, fs):
    f, a = tm.amplitude_spectrum(x, fs)
    one = tm.band_peak(f, a, F1)
    two = tm.band_peak(f, a, 2 * F1)
    mesh = tm.band_peak(f, a, MESH)
    sb = tm.band_peak(f, a, MESH - F1) + tm.band_peak(f, a, MESH + F1)
    rms = float(np.sqrt(np.mean(np.square(np.asarray(x) - np.mean(x)))))
    return dict(one=one, two=two, mesh=mesh, sb=sb / mesh, rms=rms)


def diagnose(d) -> str:
    """First guess from the shape of the spectrum (teaching limits)."""
    found = []
    if d["one"] > 0.8:
        found.append("imbalance (1x)")
    if d["two"] > 0.6:
        found.append("misalignment (2x)")
    if d["sb"] > 0.3:
        found.append("tooth damage (sidebands)")
    return ", ".join(found) or "accept"
# [end: diagnose]


def runin() -> dict[str, str]:
    fs, units = src._runin()
    out, rms = {}, {}
    lines = ["run-in of ten gearboxes at 1155 rpm (synthetic, acceleration units)",
             f"  shaft {F1:.2f} Hz, mesh {MESH:.1f} Hz (27 x shaft)",
             "  unit    1x     2x    mesh   sidebands/mesh   rms   finding"]
    for name, x in units.items():
        d = lines_of(x, fs)
        out[name] = diagnose(d)
        rms[name] = d["rms"]
        lines.append(f"  {name}  {d['one']:5.2f}  {d['two']:5.2f}  {d['mesh']:5.2f}"
                     f"   {d['sb']:14.2f}  {d['rms']:5.2f}   {out[name]}")
    f, a = tm.amplitude_spectrum(units["G04"], fs)
    m = (f > MESH - 60) & (f < MESH + 60)
    csv("ch42-sidebands.csv", "f,a",
        [(round(float(x), 2), round(float(y), 4)) for x, y in zip(f[m], a[m])])
    f7, a7 = tm.amplitude_spectrum(units["G07"], fs)
    m7 = f7 < 120
    csv("ch42-g07.csv", "f,a",
        [(round(float(x), 2), round(float(y), 4)) for x, y in zip(f7[m7], a7[m7])])
    bad = {k: v for k, v in out.items() if v != "accept"}
    good = sorted(v for k, v in rms.items() if k not in bad)
    med = good[len(good) // 2]
    lines += ["  units held:"] + [f"    {k}: {v}" for k, v in bad.items()]
    lines += ["  the overall level hides what the lines show: G04's rms is",
              f"  only {rms['G04'] / med - 1:.0%} above the good units', yet its "
              "sidebands say one tooth is struck",
              "  each turn; each finding opens an NCR (step 3) and the unit",
              "  is not released until the cause is found and re-run"]
    emit("d_runin", lines)
    return out


# ------------------------------------------------ 2. blade quality plan
# [start: plan]
PLAN = [  # step, H/W/R, method, record
    ("materials receipt", "R", "certificates, shelf life", "batch log"),
    ("mould preparation", "R", "release, surface check", "mould card"),
    ("lay-up of caps and shell", "W", "ply count, orientation", "ply map"),
    ("infusion", "R", "fill, vacuum hold", "infusion record"),
    ("cure", "H", "DSC samples, Tg", "cure record"),
    ("bonding of shells and webs", "W", "bond width, squeeze-out", "bond log"),
    ("ultrasonic scan", "H", "caps, bond lines (POD)", "scan maps"),
    ("lightning system", "H", "receptor-root resistance", "LPS test"),
    ("root machining, inserts", "W", "flatness, insert pulls", "root sheet"),
    ("weighing", "H", "mass, first mass moment", "weighing sheet"),
    ("dimensions", "W", "twist, chord, pre-bend", "3D scan"),
    ("finish and coating", "R", "thickness, edge layer", "paint log"),
    ("final release", "H", "dossier, NCRs closed", "release note"),
]
# [end: plan]


def quality_plan() -> dict[str, int]:
    counts = {k: sum(1 for r in PLAN if r[1] == k) for k in "HWR"}
    lines = ["blade inspection and quality plan (H hold, W witness, R record)",
             "  step                        point  method                    "
             "record"]
    for step, pt, how, rec in PLAN:
        lines.append(f"  {step:27s} {pt:5s}  {how:25s} {rec}")
    lines += [f"  {counts['H']} holds, {counts['W']} witness points, "
              f"{counts['R']} records",
              "  a hold stops the blade until released; a witness lets the",
              "  buyer attend; a record is reviewed later - holds sit where",
              "  a defect becomes hidden (cure, scan) or costly (release)"]
    emit("d_plan", lines)
    return counts


# ------------------------------------------------ 3. NCR escalation
AUTHORITY = {1: ("supervisor", 5), 2: ("quality engineer", 10),
             3: ("design authority", 15)}         # who, days to decide


def escalation() -> dict[str, int]:
    lines = ["nonconformity reports: who decides and by when (teaching)",
             "  NCR       sev  where     decides            limit  open  status"]
    late = 0
    for nid, part, what, sev, where, days in src.NCRS:
        who, limit = AUTHORITY[sev]
        st = "late" if days > limit else "open"
        late += st == "late"
        lines.append(f"  {nid}  {sev:3d}  {where:8s}  {who:18s} {limit:5d}  "
                     f"{days:4d}  {st}")
    lines += [f"  {late} report(s) past their limit: escalated one level up",
              "  the disposition - use as is, repair, scrap - is made by",
              "  the authority for the severity; 'use as is' on a",
              "  load-path part is the designer's decision with a written",
              "  justification (ch 40, concession)"]
    emit("d_ncr", lines)
    return dict(late=late)


# ------------------------------------------------ 4. interface map
MAP = [  # part, transport, lifting, preservation, installation hold
    ("blade", "road, root and tip frames", "two-point yoke", "covers, tip",
     "inserts torqued, LPS tested"),
    ("hub", "road, own frame", "lugs on hub", "desiccant, sealed",
     "pitch bearing seals checked"),
    ("nacelle", "road, low-loader", "lifting yoke", "heaters, desiccant",
     "yaw flange flat, bolts"),
    ("tower section", "road, saddles", "flange lifting tools", "covers",
     "flange flatness, earthing"),
    ("converter", "in nacelle or tower", "with its module", "dry, heated",
     "insulation index"),
]


def interface_map() -> dict[str, int]:
    lines = ["transport and installation interfaces (ch 31 plan)",
             "  part           transport / lifting / preservation",
             "                 installation hold point"]
    for part, tr, lift, pres, hold in MAP:
        lines += [f"  {part:14s} {tr}; {lift}; {pres}",
                  f"  {'':14s} hold: {hold}"]
    extra = ["yaw flange: flatness against the tower top flange",
             "bolt pattern of tower top and yaw bearing matched",
             "contact faces left bare of paint (friction joint)",
             "earthing straps across each flange joint"]
    lines += ["  added to the tower-section traveler of ch 30 (top section):"]
    lines += [f"    - {e}" for e in extra]
    lines += ["  each hold is where a part from one maker meets another's:",
              "  the record carries both serials (lesson A, interfaces)"]
    emit("d_map", lines)
    return dict(parts=len(MAP), extra=len(extra))


if __name__ == "__main__":
    runin()
    quality_plan()
    escalation()
    interface_map()
