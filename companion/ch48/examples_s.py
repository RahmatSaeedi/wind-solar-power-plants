"""Chapter 48, round s: enclosure ratings by location, EMC test records,
surge protection of outdoor signal lines, a calibration interval from the
drift budget, the money in the metering error, spare switch ports, fibre
cores allocated, redundant power supplies loaded, loop-check coverage,
and a wrong value traced through the stages.

Run from the project root:   python -m companion.ch48.examples_s
Writes companion/ch48/expected/s_*.txt.
Teaching values (A-498 to A-505); defensive administration only.
"""
from __future__ import annotations

import math

from companion.ch48 import sources as src
from companion.ch48.common import emit
from plantp import hwmfg as hw

# ------------------------------------------------ 1. enclosure ratings
NEED = {"outdoor, dust": (5, 5), "outdoor": (5, 4), "turbine tower": (5, 4),
        "indoor, clean": (2, 0)}
INSTALLED = {   # cabinet: (location, IP)
    "MET-1": ("outdoor", "IP55"), "WTG-T05": ("turbine tower", "IP54"),
    "SUB-RTU": ("indoor, clean", "IP42"), "PV-B07": ("outdoor, dust", "IP65"),
    "PV-B03": ("outdoor, dust", "IP54"), "CAM-12": ("outdoor", "IP44"),
}


def ip() -> list:
    bad = []
    lines = ["enclosure rating against its location (IP: first digit dust,",
             "  second water; teaching minimum by location)",
             "  cabinet   location          need    installed   verdict"]
    for c, (loc, code) in INSTALLED.items():
        d, w = int(code[2]), int(code[3])
        nd, nw = NEED[loc]
        ok = d >= nd and w >= nw
        if not ok:
            bad.append(c)
        lines.append(f"  {c:8s}  {loc:16s}  IP{nd}{nw}    {code:9s}   "
                     f"{'ok' if ok else 'LOW'}")
    lines += [f"  low: {', '.join(bad)} - PV-B03 has the dust digit but not the",
              "  water one for a block washed by the cleaning robots of ch 10;",
              "  CAM-12's camera box lets in the dust of the access road; the",
              "  rating is read from the nameplate, not the order"]
    emit("s_ip", lines)
    return bad


# ------------------------------------------------ 2. EMC records
EMC = {   # device: (location class, report on file, immunity class tested)
    "RTU-1": ("substation", True, "heavy industrial"),
    "SW-SUB": ("substation", True, "substation"),
    "GW-PV1": ("substation", True, "light industrial"),
    "CLK-1": ("substation", False, ""),
    "SW-T05": ("turbine", True, "heavy industrial"),
}
LEVEL = {"light industrial": 1, "heavy industrial": 2, "substation": 3}
NEEDS = {"substation": 3, "turbine": 2}


def emc() -> list:
    bad = []
    lines = ["EMC immunity reports against the place each device works"]
    for d, (loc, rep, cls) in EMC.items():
        if not rep:
            v = "NO REPORT"
        elif LEVEL[cls] < NEEDS[loc]:
            v = f"tested '{cls}', needs '{loc}'"
        else:
            v = "ok"
        if v != "ok":
            bad.append(d)
        lines.append(f"  {d:7s}  {loc:10s}  {v}")
    lines += [f"  short: {', '.join(bad)}",
              "  a substation has switching surges and fields an office never",
              "  sees: a gateway tested for light industry may reset when a",
              "  breaker opens - exactly when its data matter; the report",
              "  is asked for before the order (ch 39), not after a reset"]
    emit("s_emc", lines)
    return bad


# ------------------------------------------------ 3. surge protection
OUTDOOR = [   # cable, from, to, surge protector at the cabinet entry
    ("C-201", "met mast pyranometer", "MET-1", True),
    ("C-202", "met mast anemometer", "MET-1", True),
    ("C-203", "met mast wind vane", "MET-1", False),
    ("C-204", "PV string monitor", "PV-B07", True),
    ("C-205", "fence camera", "CAM-12", False),
]


def surge() -> list:
    bad = [(c, f) for c, f, _, spd in OUTDOOR if not spd]
    lines = ["outdoor signal lines entering cabinets: surge protector at the entry?"]
    lines += [f"  {c}  {f:22s} -> {t:7s}  {'yes' if s else 'NO'}"
              for c, f, t, s in OUTDOOR]
    lines += [f"  {len(bad)} lines without: the wind vane's cable runs down the same",
              "  mast as the others and brings a lightning surge straight to",
              "  the logger the others protect - a protector on every line,",
              "  bonded to the cabinet's earth bar (lesson A), or none works"]
    emit("s_surge", lines)
    return bad


# ------------------------------------------------ 4. calibration interval
def interval(target_pct: float = 2.5) -> dict:
    spec, rdg, fs, _ = src.SPECS["pyranometer"]
    lines = [f"pyranometer: years until the RSS budget at 45 C reaches {target_pct} % "
             "of the reading"]
    yrs = None
    for k in range(0, 61):
        y = k / 10
        b = hw.error_budget(spec, 45.0, y, rdg, fs)
        if b["rss"] / rdg * 100 > target_pct:
            yrs = y
            break
    lines += [f"  the budget passes {target_pct} % after about {yrs:.1f} years",
              "  so the recalibration interval is set by the drift the plant",
              "  can afford, not by the maker's default of two years; the",
              "  reference cell and the spare pyranometer swap in so the",
              "  station never stops measuring (ch 12, ch 34)"]
    emit("s_interval", lines)
    return dict(years=yrs)


# ------------------------------------------------ 5. money in the metering error
def money(gwh: float = 295.0, price: float = 70.0) -> dict:
    rss, worst = hw.chain_error(src.METER["ct"], src.METER["vt"], src.METER["meter"])
    mwh = gwh * 1000 * rss / 100
    lines = [f"what the metering chain's error is worth (teaching price {price:.0f} u/MWh)",
             f"  {rss:.2f} % of {gwh:.0f} GWh = {mwh:,.0f} MWh = {mwh * price / 1000:,.0f} k u "
             "a year either way",
             f"  worst case {worst:.2f} %: {gwh * 10 * worst * price / 1000:,.0f} k u a year",
             "  the meter, its transformers and their site test are paid for",
             "  many times over in the first year: settlement disputes are",
             "  settled by the test record, not by the meter's nameplate"]
    emit("s_money", lines)
    return dict(mwh=mwh, ku=mwh * price / 1000)


# ------------------------------------------------ 6. spare ports
SWITCHES = {"SW-T05": (8, 7), "SW-T09": (8, 6), "SW-SUB": (24, 22), "SW-PV1": (16, 11),
            "SW-CTRL": (24, 15)}


def spare_ports(rule: float = 0.2) -> list:
    bad = [s for s, (n, u) in SWITCHES.items() if (n - u) / n < rule]
    lines = [f"spare ports on each switch (teaching rule {rule:.0%})"]
    lines += [f"  {s:8s} {n:3d} ports, {u:3d} used, {(n - u) / n:4.0%} spare"
              for s, (n, u) in SWITCHES.items()]
    lines += [f"  below the rule: {', '.join(bad)} - the substation core has two",
              "  ports left for the whole plant's life; one more PV block or a",
              "  second historian means a new switch in a full cabinet",
              "  (spare terminals, ch 46)"]
    emit("s_ports", lines)
    return bad


# ------------------------------------------------ 7. fibre cores
CORES = {   # cable: core -> use
    "FO-W1": {1: "ring T01", 2: "ring T01", 3: "CCTV", 4: "spare", 5: "ring T01",
              6: "spare"},
    "FO-E1": {1: "ring T12", 2: "ring T12", 3: "spare", 4: "PPC link", 5: "PPC link",
              6: "spare"},
}
PLAN_CORES = {"FO-W1": {"ring T01": 2, "CCTV": 1}, "FO-E1": {"ring T12": 2, "PPC link": 2}}


def cores() -> dict:
    out = {}
    lines = ["fibre core allocation of two cables against the plan"]
    for c, alloc in CORES.items():
        use = {}
        for k, u in alloc.items():
            if u != "spare":
                use[u] = use.get(u, 0) + 1
        diff = {u: (use.get(u, 0), n) for u, n in PLAN_CORES[c].items()
                if use.get(u, 0) != n}
        spare = sum(1 for u in alloc.values() if u == "spare")
        out[c] = (diff, spare)
        lines.append(f"  {c}: spare cores {spare}; differences: "
                     + (", ".join(f"{u} uses {a}, plan {b}" for u, (a, b) in diff.items())
                        or "none"))
    lines += ["  FO-W1's ring uses a third core that the plan does not show:",
              "  a technician who takes 'spare' core 5 for a repair cuts the",
              "  ring - the core table is part of the as-built schedule"]
    emit("s_cores", lines)
    return out


# ------------------------------------------------ 8. redundant power supplies
PSU = {   # cabinet: (load W, PSU rating W each, PSUs)
    "SUB-CORE": (180, 120, 2), "SUB-RTU": (95, 150, 2), "CTRL-SCADA": (420, 500, 2),
    "MET-1": (35, 60, 1),
}


def psu() -> list:
    bad = []
    lines = ["redundant power supplies: can one carry the cabinet alone?",
             "  cabinet      load W   one PSU W   PSUs   verdict"]
    for c, (load, r, n) in PSU.items():
        if n == 1:
            v = "single" if load <= r else "OVER"
        else:
            v = "N+1 ok" if load <= r else "NOT N+1"
        if v in ("NOT N+1", "OVER"):
            bad.append(c)
        lines.append(f"  {c:11s}  {load:6d}   {r:9d}   {n:4d}   {v}")
    lines += [f"  {', '.join(bad)}: two supplies that share the load but cannot",
              "  carry it alone - redundancy on the drawing, not in fact; the",
              "  first failure trips the second (and lesson B found both on",
              "  one UPS as well)"]
    emit("s_psu", lines)
    return bad


# ------------------------------------------------ 9. loop-check coverage
LOOPS = {"wind turbines": (12 * 48, 12 * 48), "PV blocks": (10 * 36, 10 * 34),
         "battery": (8 * 24, 8 * 24), "substation": (310, 296), "met stations": (40, 31)}


def loops() -> dict:
    lines = ["point-to-point loop checks: points tested from the field device to",
             "  the SCADA display",
             "  system           points   tested   coverage"]
    tot = sum(a for a, _ in LOOPS.values())
    done = sum(b for _, b in LOOPS.values())
    for s, (a, b) in LOOPS.items():
        lines.append(f"  {s:15s}  {a:6d}   {b:6d}   {b / a:8.1%}")
    lines += [f"  all: {done} of {tot} ({done / tot:.1%}); {tot - done} points untested",
              "  the met stations are the worst: 9 of 40 points never seen at",
              "  the display - including two that feed the PR of ch 37; each",
              "  untested point is a line in the punch list, not a footnote"]
    emit("s_loops", lines)
    return dict(tot=tot, done=done)


# ------------------------------------------------ 10. tracing a wrong value
STAGES = [   # stage, value seen, unit (the true irradiance is 820 W/m2)
    ("sensor current", 4 + 16 * 820 / 1600, "mA"), ("logger", 820.0, "W/m2"),
    ("gateway register", 8200, "raw"), ("SCADA", 8200.0, "W/m2"),
    ("historian", 8200.0, "W/m2"),
]


def trace(true: float = 820.0) -> dict:
    lines = ["the historian shows 8,200 W/m2 on a sunny day: where does it go wrong?"]
    first = None
    for s, v, u in STAGES:
        ok = u in ("mA", "raw") or abs(v - true) / true < 0.02
        if u == "raw":
            ok = True
        if not ok and first is None:
            first = s
        lines.append(f"  {s:17s} {v:9.2f} {u:5s} {'ok' if ok else 'WRONG'}")
    lines += [f"  first wrong stage: {first} - the gateway sends the raw value",
              "  in tenths (scale 0.1) and the SCADA tag reads it with scale",
              "  1.0: the register map and the tag disagree (lesson C); every",
              "  stage after it is wrong in the same way, and every stage",
              "  before it is right - the view of lab D tells where to look"]
    emit("s_trace", lines)
    return dict(first=first)


if __name__ == "__main__":
    ip()
    emc()
    surge()
    interval()
    money()
    spare_ports()
    cores()
    psu()
    loops()
    trace()
