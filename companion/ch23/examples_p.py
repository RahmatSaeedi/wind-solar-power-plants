"""Chapter 23 - more of what the one-line carries: the per-unit impedance
diagram (checked against the MVA method of lab G), fault levels at the
low-voltage buses of the units, a radial against an open-ring collector
by expected energy not served, the energisation stages traced through
the one-line, interlocks derived from it (with one across an ownership
boundary), and the status of the drawing register.

Run from the project root:   python -m companion.ch23.examples_p
Writes companion/ch23/expected/p_*.txt. Teaching values (A-316
extended: cable failure rate, repair and switching times, capacity
factor; A-320: network values).
"""
from __future__ import annotations

import math
from collections import Counter, deque

from companion.ch23 import sources as src
from companion.ch23.common import emit

BASE = 100.0                     # MVA


def zpu_own(z: float, s_own: float) -> float:
    """Impedance in pu on its own rating -> on the common base."""
    return z * BASE / s_own


def zpu_ohm(z_ohm: float, kv: float) -> float:
    return z_ohm / (kv ** 2 / BASE)


def per_unit() -> None:
    grid = BASE / 1500.0
    line = zpu_ohm(7.06 * 0.418, 132.0)
    t1 = zpu_own(0.12, 63.0)
    cab = zpu_ohm(1.1 * 0.116, 33.0)
    ut = zpu_own(0.07, 5.6)
    z33 = grid + line + t1
    rows = [("grid (1,500 MVA)", "1/15", grid), ("line 7.06 km, 0.418 ohm/km", "Z/Zbase", line),
            ("T1 63 MVA, 12 %", "0.12 x 100/63", t1), ("cable 1.1 km, 0.116 ohm/km", "Z/Zbase", cab),
            ("unit transformer 5.6 MVA, 7 %", "0.07 x 100/5.6", ut)]
    lines = ["per-unit impedance diagram on a 100 MVA base (reactances, teaching):",
             "  base impedance: 132 kV -> 174.2 ohm; 33 kV -> 10.89 ohm",
             "  element                          rule              x pu"]
    lines += [f"  {a:32s} {b:16s}  {c:6.4f}" for a, b, c in rows]
    lines += [f"  to the 33 kV bus (one T): {z33:.4f} pu -> {BASE / z33:.0f} MVA,"
              f" {BASE / z33 / (math.sqrt(3) * 33):.1f} kA",
              "  the same 365 MVA as the MVA method of lab G: two",
              "  notations of one calculation; per unit lets a single",
              "  diagram carry 132, 33 and 0.69 kV without ratios"]
    emit("p_perunit", lines)


def lv_faults() -> None:
    z33 = BASE / 1500 + zpu_ohm(7.06 * 0.418, 132) + zpu_own(0.12, 63)
    cases = [("turbine LV, 0.69 kV (5.6 MVA, 7 %, far end)", 0.69, 5.6, 0.07, 4 * 1.1, 5.26),
             ("PV station LV, 0.60 kV (5.5 MVA, 6 %)", 0.60, 5.5, 0.06, 4 * 0.6, 5.0),
             ("station service, 0.40 kV (0.25 MVA, 4.5 %)", 0.40, 0.25, 0.045, 0.0, 0.0)]
    lines = ["fault levels at the units' low-voltage buses (teaching):",
             "  bus                                         from MV kA  units kA  total kA"]
    for name, kv, s, z, km, s_unit in cases:
        zt = z33 + zpu_ohm(km * 0.116, 33) + zpu_own(z, s)
        i_mv = BASE / zt / (math.sqrt(3) * kv)
        i_conv = 1.2 * s_unit / (math.sqrt(3) * kv)
        lines.append(f"  {name:43s} {i_mv:10.1f}  {i_conv:8.1f}  {i_mv + i_conv:8.1f}")
    lines += ["  the unit transformer limits the LV fault, yet 5.6 MVA at",
              "  690 V still gives about 60 kA: the turbine's LV breaker and",
              "  busbar are rated for it (the maker's design), and the",
              "  converter adds its own share; a smaller transformer",
              "  impedance would raise both - a one-line value with",
              "  consequences inside the nacelle"]
    emit("p_lvfaults", lines)


# [start: path]
def x_pu(br) -> float:
    """Series reactance of a one-line branch on the 100 MVA base."""
    r = br.rating
    if br.kind == "transformer":
        return zpu_own(r["z_pu"], r.get("mva", r.get("kva", 0) / 1e3))
    if br.kind == "cable":
        return zpu_ohm(r["km"] * 0.116, 33.0)
    if br.kind == "line":
        return zpu_ohm(r["km"] * 0.418, 132.0)
    return 0.0                      # breakers, disconnectors
# [end: path]


def path_profile() -> None:
    g = src.plant()
    z = BASE / 1500.0
    lines = ["fault level along the energy path, grid to the farthest turbine",
             "  (reactances on 100 MVA, coupler open, grid part only):",
             "  after branch      kind           x pu    total pu    fault MVA"]
    for br in g.path("GRID", "WS1-4-LV"):
        dx = x_pu(br)
        z += dx
        if dx > 0 or br.kind == "breaker" and br.tag in ("=E1-Q1", "=T1-Q2", "=WS1-Q1"):
            lines.append(f"  {br.tag:16s}  {br.kind:12s} {dx:6.4f}   {z:8.4f}   {BASE / z:9.0f}")
    lines += ["  the fault level falls step by step away from the grid; the",
              "  unit transformer is the largest single step (1.25 pu): the",
              "  turbine's terminals see about 64 MVA from the grid, which",
              "  is also a measure of how stiff the grid looks to the",
              "  turbine's controls (ch 20, ch 28)"]
    emit("p_path", lines)


def energised(closed: set) -> set:
    g = src.plant()
    live, q = {"GRID"}, deque(["GRID"])
    while q:
        b = q.popleft()
        for br in g.branches:
            if br.kind in ("breaker", "disconnector") and br.tag not in closed:
                continue
            for x, y in ((br.a, br.b), (br.b, br.a)):
                if x == b and y not in live:
                    live.add(y)
                    q.append(y)
    return live


STAGES = [("S0 utility bay live", {"=G1-Q1"}),
          ("S1 line live to the plant bay", {"=G1-Q1", "=G1-Q9", "=E1-Q9"}),
          ("S2 132 kV bus and T1", {"=G1-Q1", "=G1-Q9", "=E1-Q9", "=E1-Q1", "=T1-Q1"}),
          ("S3 33 kV section A, station service", {"=G1-Q1", "=G1-Q9", "=E1-Q9", "=E1-Q1",
                                                   "=T1-Q1", "=T1-Q2", "=A1-Q1"}),
          ("S4 first wind string", {"=G1-Q1", "=G1-Q9", "=E1-Q9", "=E1-Q1", "=T1-Q1",
                                    "=T1-Q2", "=A1-Q1", "=WS1-Q1"})]


def staging() -> None:
    lines = ["energisation stages traced through the one-line (states only):",
             "  stage                                   live buses  newly live"]
    before: set = set()
    for name, closed in STAGES:
        live = energised(closed)
        new = sorted(live - before)
        show = ", ".join(new[:3]) + (f" +{len(new) - 3}" if len(new) > 3 else "")
        lines.append(f"  {name:39s} {len(live):10d}  {show}")
        before = live
    lines += ["  each stage moves the boundary between live and dead plant:",
              "  the tests of everything newly live come before it, the",
              "  permits and the operator's switching rules change with it,",
              "  and the drawings of the stage must be issued for",
              "  construction - the one-line becomes a series of states"]
    emit("p_staging", lines)


def interlocks() -> None:
    g = src.plant()
    lines = ["interlocks derived from the one-line: a disconnector may move",
             "  only with its neighbouring breaker open (no load breaking):"]
    for d in (b for b in g.branches if b.kind == "disconnector"):
        nb = [b for b in g.branches if b.kind == "breaker" and {b.a, b.b} & {d.a, d.b}]
        for b in nb:
            cross = b.owner != d.owner
            lines.append(f"  {d.tag} needs {b.tag} open"
                         f"{'  - ACROSS an ownership boundary' if cross else ''}")
    lines += ["  an interlock inside one owner's gear is wired; one across",
              "  the boundary (the utility's breaker, the plant's",
              "  disconnector) needs a key system or a joint operating",
              "  procedure - an item for the connection agreement (U-065)"]
    emit("p_interlocks", lines)


REGISTER = (["IFC"] * 14 + ["IFA"] * 9 + ["IFR"] * 6 + ["superseded"] * 3)


def register() -> None:
    c = Counter(REGISTER)
    live = len(REGISTER) - c["superseded"]
    lines = ["status of the electrical drawing register (teaching, 32 entries):"]
    lines += [f"  {k:11s} {v:3d}" for k, v in c.items()]
    lines += [f"  issued for construction: {c['IFC'] / live:.0%} of the {live} current drawings",
              "  IFR issued for review, IFA issued for approval, IFC issued",
              "  for construction; superseded drawings stay in the register",
              "  but leave the site; a stage may be energised only when its",
              "  drawings are IFC and its as-built mark-ups are recorded"]
    emit("p_register", lines)


def mimic() -> None:
    g = src.plant()
    c = Counter(b.kind for b in g.branches)
    iso = sum(b.isolation for b in g.branches)
    lines = ["from the design one-line to the operator's mimic (counts from the model):"]
    lines += [f"  {k:13s} {v:3d}" for k, v in sorted(c.items())]
    lines += [f"  isolation points (each with an earthing switch on the mimic): {iso}",
              "    (19 with the DC detail of one PV block, as counted in lesson A)",
              "  the mimic keeps every switchable device, its state and its",
              "  interlocks, the live/dead colouring and the earths; it",
              "  drops ratings, cable lengths and the status of data; the",
              "  design one-line is the reverse - one model feeds both, so",
              "  a change on one shows on the other (ch 34 for SCADA)"]
    emit("p_mimic", lines)


def phase_shift() -> None:
    groups = [("unit transformer (Dyn11, teaching)", 30), ("main transformer YNd11", 30)]
    total = sum(s for _, s in groups)
    lines = ["phase shift along the path, turbine terminals to 132 kV:",
             "  clock number 11: the low-voltage side leads by 30 degrees"]
    lines += [f"  {a:36s} LV leads by {s} deg" for a, s in groups]
    lines += [f"  690 V leads 132 kV by {total} degrees; every source of the plant",
              "  passes the same main transformer, so all agree at the bus",
              "  the shifts matter where two sides are compared: the",
              "  differential relay (ch 26) and synchro-check across a",
              "  transformer compensate for them, and a meter wired across",
              "  the wrong pair of VTs reads a wrong power - the vector",
              "  group belongs on the one-line beside each transformer"]
    emit("p_phase", lines)


def comms() -> None:
    n_t, per_link = 12, 0.995
    lines = ["the communications one-line on the power one-line (teaching):",
             "  fibre runs in every collector trench beside the cable;",
             f"  {n_t} turbines on 3 strings, PV stations and BESS on their feeders",
             "  each string as a chain of switches back to the substation:"]
    for name, k in (("first turbine", 1), ("last turbine", 4)):
        lines.append(f"    {name}: {k} links, available {per_link ** k:.4f}")
    ring = 1 - (1 - per_link ** 4) * (1 - per_link ** 1)
    lines += [f"  closing the chain into a ring (fibre back along the next string):",
              f"    last turbine available {ring:.6f} - two paths instead of one",
              "  a fibre ring is cheap where trenches already exist, unlike",
              "  the power ring of ch 18; the comms one-line shows each",
              "  switch, its supply (UPS of lesson F) and its owner, and",
              "  joins the interface register (lesson B)"]
    emit("p_comms", lines)


if __name__ == "__main__":
    per_unit()
    lv_faults()
    path_profile()
    staging()
    interlocks()
    register()
    mimic()
    phase_shift()
    comms()
