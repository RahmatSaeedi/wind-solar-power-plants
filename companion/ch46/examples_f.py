"""Chapter 46, lesson B (deeper): the heat of a high-resistance pole at
the plant's current, a breaker's travel curve read against its baseline,
a gas-density trend that finds a slow leak, panels as ordered against as
built, CT records against the CT schedule, what a type-test report covers,
and the interfaces between the cable maker and the switchgear maker.

Run from the project root:   python -m companion.ch46.examples_f
Writes companion/ch46/expected/f_*.txt and diagrams/data/ch46-*.csv.
Teaching values (A-485); no test procedure, no live work.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch46 import sources as src
from companion.ch46.common import csv, emit
from plantp import cablemfg as km


def amps(mw: float, kv: float = 33.0, pf: float = 0.95) -> float:
    return mw * 1e6 / (math.sqrt(3) * kv * 1e3 * pf)


# ------------------------------------------------ 1. heat of a high pole
LOAD_MW = {"WS1": 20, "WS2": 20, "WS3": 20, "PVF1": 20, "PVF2": 15, "PVF3": 15,
           "BESS-A": 10, "BESS-B": 10}


def pole_heat(rated_a: float = 630.0) -> dict:
    l1, l2, l3 = src.CONTACTS["PVF1"]
    extra = (l2 - (l1 + l3) / 2) * 1e-6
    i = amps(LOAD_MW["PVF1"])
    lines = ["extra heat of pole L2 of PVF1 (52 against 35 and 36 micro-ohm)",
             f"  excess resistance {extra * 1e6:.1f} micro-ohm",
             f"  at the plant's full output ({i:.0f} A): {i ** 2 * extra:.1f} W more",
             f"  at the panel's rated current ({rated_a:.0f} A): "
             f"{rated_a ** 2 * extra:.1f} W more",
             f"  the same excess in an incomer at 1,102 A (63 MVA): "
             f"{1102 ** 2 * extra:.1f} W more",
             "  two watts in a feeder will not show on a thermometer for years",
             "  (the incomer's twenty would sooner); the danger is the cause -",
             "  a joint that is loose or dirty gets worse with heat and time -",
             "  so the factory finds it by comparing poles, not by waiting",
             "  for heat at site"]
    emit("f_heat", lines)
    return dict(extra=extra, w=i ** 2 * extra)


# ------------------------------------------------ 2. travel curve
def curve(t_ms, stroke=12.0, start=8.0, dur=20.0):
    """Educational close travel: a smooth S from 0 to the full stroke."""
    out = []
    for t in t_ms:
        u = min(max((t - start) / dur, 0.0), 1.0)
        out.append(stroke * (1 - math.cos(math.pi * u)) / 2)
    return out


def travel(lo: float = 6.0, touch: float = 9.0, tol: float = 0.10) -> dict:
    t = [k * 0.5 for k in range(81)]
    base = curve(t)
    slow = curve(t, dur=26.0)
    csv("ch46-travel.csv", "t,base,slow",
        [(a, round(b, 3), round(c, 3)) for a, b, c in zip(t, base, slow)])

    def window(x):
        t1 = next(a for a, v in zip(t, x) if v >= lo)
        t2 = next(a for a, v in zip(t, x) if v >= touch)
        return t2, (touch - lo) / (t2 - t1)          # mm/ms = m/s

    tb, vb = window(base)
    ts, vs = window(slow)
    lines = ["close travel of breaker WS2 against its factory baseline",
             "  (stroke 12 mm, coil and latch delay 8 ms; teaching)",
             f"  speed is read between {lo:.0f} and {touch:.0f} mm, where the "
             "contacts touch",
             "             touch at ms   speed m/s",
             f"  baseline   {tb:11.1f}   {vb:9.2f}",
             f"  now        {ts:11.1f}   {vs:9.2f}",
             f"  speed change {vs / vb - 1:+.0%} against a teaching tolerance of "
             f"+/-{tol:.0%}",
             f"  the closing time grows only {ts / tb - 1:.0%}: it includes the "
             "fixed coil and",
             "  latch delay, which does not change; the speed in the contact",
             "  zone shows the whole loss of energy (lubricant, spring) - the",
             "  factory baseline makes site and maintenance readings",
             "  comparable (ch 52)"]
    emit("f_travel", lines)
    return dict(vb=vb, vs=vs, tb=tb, ts=ts)


# ------------------------------------------------ 3. gas-density trend
def gas(seed: int = 4613, months: int = 24, alarm: float = 0.93) -> dict:
    rng = np.random.default_rng(seed)
    leak = {p: 0.0 for p in src.PANELS}
    leak["BESS-B"] = 0.012                      # 1.2 % a year
    x = list(range(months + 1))
    res, rows = {}, []
    for p in src.PANELS:
        y = [1.0 - leak[p] * m / 12 + rng.normal(0, 0.002) for m in x]
        b, se = km.trend(x, y)
        res[p] = (b * 12, se * 12)
        if p in ("BESS-B", "WS1"):
            rows.append((p, y))
    csv("ch46-gas.csv", "m,ws1,bessb",
        [(m, round(a, 4), round(b, 4)) for m, a, b in
         zip(x, rows[0][1] if rows[0][0] == "WS1" else rows[1][1],
             rows[1][1] if rows[1][0] == "BESS-B" else rows[0][1])])
    lines = [f"gas density of the sealed compartments, temperature-corrected, "
             f"{months} months",
             "  (relative to the fill; teaching alarm level "
             f"{alarm:.2f})", "  panel    slope %/yr   +/-2 SE   verdict"]
    flagged = []
    for p, (b, se) in res.items():
        sig = b < 0 and abs(b) > 2 * se
        if sig:
            flagged.append(p)
        lines.append(f"  {p:7s} {b * 100:10.2f}   {2 * se * 100:7.2f}   "
                     f"{'LEAK' if sig else 'no trend'}")
    b = res["BESS-B"][0]
    yrs = (1 - alarm) / -b
    lines += [f"  leaking: {', '.join(flagged)}; alarm in about {yrs:.1f} years "
              "from the fill",
              "  each monthly reading moves less than its own noise; only the",
              "  slope over many months shows the leak, years before the",
              "  alarm - so the readings are kept as a series, not just read"]
    emit("f_gas", lines)
    return dict(flagged=flagged, years=yrs, res=res)


# ------------------------------------------------ 4. ordered against built
ORDER = {p: dict(vt="yes" if p.startswith(("INC", "WS", "PVF")) else "no",
                 arresters="yes" if p.startswith(("WS", "PVF", "BESS")) else "no",
                 ct_cores=3 if p.startswith(("INC", "BESS")) else 2,
                 relay="R-300" if p != "SST" else "R-200")
         for p in src.PANELS}
BUILT = {p: dict(v) for p, v in ORDER.items()}
BUILT["WS2"]["arresters"] = "no"
BUILT["BESS-B"]["ct_cores"] = 2
BUILT["PVF2"]["relay"] = "R-200"


def variants() -> list:
    diff = [(p, k, ORDER[p][k], BUILT[p][k]) for p in src.PANELS
            for k in ORDER[p] if ORDER[p][k] != BUILT[p][k]]
    lines = [f"{len(src.PANELS)} panels of four types, each with options: ordered "
             "against built",
             "  panel    option      ordered   built"]
    lines += [f"  {p:7s}  {k:10s}  {o!s:8s}  {b}" for p, k, o, b in diff]
    lines += [f"  {len(diff)} differences in {len(src.PANELS) * 4} option cells: "
              "each panel looks",
              "  complete and passes its own routine tests - a missing arrester",
              "  set, a CT core short for the battery's differential protection",
              "  and the wrong relay model are found only by comparing the",
              "  build record with the order line by line"]
    emit("f_variants", lines)
    return diff


# ------------------------------------------------ 5. CT records
CT_SCHEDULE = {p: (1600 if p.startswith("INC") else 600) for p in src.PANELS
               if p not in ("BC", "SST")}
CT_FAT = {p: (r, "ok") for p, r in CT_SCHEDULE.items()}
CT_FAT["PVF3"] = (400, "ok")
CT_FAT["BESS-B"] = (600, "reversed core 2")


def ct_records(set_51: float = 0.9, set_50: float = 1.6) -> dict:
    lines = ["CT ratio and polarity at the switchgear FAT against the CT schedule",
             "  panel    schedule   found   polarity"]
    odd = []
    for p, r in CT_SCHEDULE.items():
        f, pol = CT_FAT[p]
        if f != r or pol != "ok":
            odd.append(p)
            lines.append(f"  {p:7s}  {r:5d}/1   {f:4d}/1   {pol}")
    f = CT_FAT["PVF3"][0]
    lines += [f"  differing: {', '.join(odd)}",
              f"  PVF3's relay is set for 600/1; with a {f}/1 CT it sees "
              f"{600 / f:.1f} x the current:",
              f"  stage 51 acts at {set_51 * f:.0f} A instead of "
              f"{set_51 * 600:.0f} A,",
              f"  stage 50 at {set_50 * f:.0f} A instead of {set_50 * 600:.0f} A",
              f"  the feeder's full output is {amps(15):.0f} A - no trip in "
              "service, but every",
              "  grading margin of ch 26 is gone; a reversed core in a",
              "  differential zone trips on the first through-fault - both are",
              "  found by reading the record against the schedule, before any",
              "  current flows"]
    emit("f_ct", lines)
    return dict(odd=odd)


# ------------------------------------------------ 6. type-test coverage
ORDERED = {"incomer": dict(ir=1600, ik=25, tk=3, amb=45),
           "feeder": dict(ir=630, ik=25, tk=3, amb=45)}
REPORT = {"incomer": dict(ir=1250, ik=25, tk=1, amb=40),
          "feeder": dict(ir=630, ik=25, tk=3, amb=40)}


def typetest() -> list:
    gaps = []
    lines = ["what the maker's type-test reports cover against the order",
             "  panel     rated A    short-time kA x s    ambient C",
             "            ord/rep    ordered / report     ord/rep"]
    for k in ORDERED:
        o, r = ORDERED[k], REPORT[k]
        ir = f"{o['ir']}/{r['ir']}"
        lines.append(f"  {k:8s}  {ir:9s}  {o['ik']} x {o['tk']} / "
                     f"{r['ik']} x {r['tk']}         {o['amb']}/{r['amb']}")
        if r["ir"] < o["ir"]:
            gaps.append((k, f"{o['ir']} A not type-tested ({r['ir']} A)"))
        cover = (r["ik"] ** 2 * r["tk"]) / (o["ik"] ** 2 * o["tk"])
        if cover < 1:
            gaps.append((k, f"report covers {cover:.0%} of the ordered I2t"))
        if o["amb"] > r["amb"]:
            gaps.append((k, f"ambient {o['amb']} C > {r['amb']} C: maker's "
                            "derating"))
    lines += ["  gaps:"] + [f"    {k}: {g}" for k, g in gaps]
    lines += ["  a type test proves the design that was tested; the 1,600 A",
              "  incomer of ch 26 is a different design until the maker shows",
              "  a report for it or a justified extension - asked for before",
              "  the order, not at the FAT"]
    emit("f_typetest", lines)
    return gaps


# ------------------------------------------------ 7. maker-to-maker interfaces
CONNECTOR = {p: "L" for p in src.PANELS}
CONNECTOR["PVF2"] = "S"
POSITIONS = {p: 1 for p in src.PANELS}
FAMILY_MAX = {"S": 300, "L": 630}


def interfaces() -> list:
    rows = src.schedule()
    first = {}
    count = {}
    for r in rows:
        if r["from"].startswith("SWG/"):
            p = r["from"][4:]
            count[p] = count.get(p, 0) + 1
            size = r["size_mm2"]
            if isinstance(size, str):
                size = int("".join(ch for ch in size if ch.isdigit())[:3])
            first[p] = max(first.get(p, 0), size)
    probs = []
    lines = ["cable maker meets switchgear maker: connectors and positions",
             "  panel    cable mm2   connector (max)   cables   positions"]
    for p in sorted(first):
        fam = CONNECTOR[p]
        lines.append(f"  {p:7s}  {first[p]:9d}   {fam} ({FAMILY_MAX[fam]:3d})"
                     f"           {count[p]:6d}   {POSITIONS[p]:9d}")
        if first[p] > FAMILY_MAX[fam]:
            probs.append(f"{p}: {first[p]} mm2 cable, connector family {fam} "
                         f"up to {FAMILY_MAX[fam]}")
        if count[p] > POSITIONS[p]:
            probs.append(f"{p}: {count[p]} cables, {POSITIONS[p]} position")
    lines += ["  problems:"] + [f"    {x}" for x in probs]
    lines += ["  each maker's drawing is right on its own; the cable schedule",
              "  is the one document that sees both, so the interface check",
              "  runs from it (the schedule has two cables on each battery",
              "  feeder, one to each PCS; the switchgear order was written",
              "  for one)"]
    emit("f_interfaces", lines)
    return probs


if __name__ == "__main__":
    pole_heat()
    travel()
    gas()
    variants()
    ct_records()
    typetest()
    interfaces()
