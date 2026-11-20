"""Chapter 46, round s: sampling a lot of drums, cable capacitance from the
geometry, PD results against their background, busbar heating scaled from
a type test, pole timing across the line-up with robust scores, contact
resistance from FAT to site, wire sizes by circuit class, a FAT plan,
settings history, schedule revisions, drums re-planned after rejects and
an ITP checked against the failure modes it must cover.

Run from the project root:   python -m companion.ch46.examples_s
Writes companion/ch46/expected/s_*.txt.
Teaching values (A-483 to A-489); no test voltages, no test procedure.
"""
from __future__ import annotations

import math
from math import comb

from companion.ch24 import sources as s24
from companion.ch46 import sources as src
from companion.ch46.common import csv, emit
from plantp import convmfg as cm
from plantp import pvfab as pf

EPS0 = 8.854e-12


# ------------------------------------------------ 1. sampling a lot of drums
def sampling(n_lot: int = 40, bad: int = 3) -> dict:
    lines = [f"a lot of {n_lot} drums with {bad} thin-insulation drums: chance a "
             "sample finds one",
             "  drums sampled   chance to find at least one"]
    out = {}
    for n in (1, 2, 4, 8, 16):
        p = 1 - comb(n_lot - bad, n) / comb(n_lot, n)
        out[n] = p
        lines.append(f"  {n:13d}   {p:27.1%}")
    csv("ch46-sampling.csv", "n,p",
        [(k, round(100 * (1 - comb(n_lot - bad, k) / comb(n_lot, k)), 2))
         for k in range(n_lot + 1)])
    lines += ["  a sample test checks that production matches the design; it",
              "  cannot find a few bad drums - that is why the thickness of",
              "  both ends of every drum is in its routine record (lesson A)"]
    emit("s_sampling", lines)
    return out


# ------------------------------------------------ 2. capacitance from geometry
def capacitance(eps_r: float = 2.3, u0_kv: float = 33 / math.sqrt(3)) -> dict:
    from companion.ch46.examples_e import radii
    lines = ["capacitance of a core from its geometry,",
             f"  C = 2 pi eps0 eps_r / ln(ri/rc), eps_r {eps_r}",
             "  size mm2   C uF/km (geometry)   C uF/km (ch 24 data)   charging A/km"]
    out = {}
    for a in (240, 400, 630):
        rc, ri = radii(a)
        c = 2 * math.pi * EPS0 * eps_r / math.log(ri / rc) * 1e9      # uF/km
        ic = 2 * math.pi * 50 * c * 1e-6 * u0_kv * 1e3
        out[a] = c
        lines.append(f"  {a:8d}   {c:18.3f}   {s24.MV_CABLES[a]['c']:20.2f}   "
                     f"{ic:13.2f}")
    rc, ri = radii(240)
    c_thin = 2 * math.pi * EPS0 * eps_r / math.log((rc + 7.1) / rc) * 1e9
    lines += ["  the geometry gives the data-sheet values within 5 %; a core",
              f"  thinned to 7.1 mm all round would show {c_thin:.3f} uF/km "
              f"(+{c_thin / out[240] - 1:.0%}) -",
              "  capacitance is a second, independent look at the same",
              "  geometry that the thickness slices measure"]
    emit("s_capacitance", lines)
    return dict(c=out, thin=c_thin)


# ------------------------------------------------ 3. PD results and background
PD = [   # drum, reported PD pC, background noise pC (from the report)
    ("D401", 2, 1), ("D402", 9, 3), ("D403", 2, 2), ("D404", 4, 2),
    ("D405", 3, 1), ("D406", None, None), ("D407", 2, 1), ("D408", 5, 14),
]


def pd_results(limit: float = 10.0) -> dict:
    lines = [f"PD results read against the background of the same test "
             f"(teaching limit {limit:.0f} pC)",
             "  drum   PD pC   background pC   verdict"]
    odd = {}
    for d, pd, bg in PD:
        if pd is None:
            odd[d] = "no PD result"
            lines.append(f"  {d}       -               -   NO RESULT (lesson A)")
            continue
        if bg >= limit:
            v = "NOT CREDIBLE - background above the limit"
        elif pd > 0.8 * limit:
            v = "pass, close to the limit"
        else:
            v = "pass"
        if v != "pass":
            odd[d] = v
        lines.append(f"  {d}   {pd:5d}   {bg:13d}   {v}")
    lines += ["  a reading of 5 pC means nothing when the test bay's own noise",
              "  is 14 pC: the bay could not have seen a 10 pC discharge, so",
              "  D408's report is asked again; D406 has no PD line at all",
              "  (lesson A) - a result is read with its background"]
    emit("s_pd", lines)
    return odd


# ------------------------------------------------ 4. busbar rise scaled
def busbar_rise(i_test: float = 1250.0, dt_test: float = 55.0,
                i_ord: float = 1600.0, limit: float = 65.0) -> dict:
    lines = [f"temperature rise of the incomer from a type test at {i_test:.0f} A "
             f"({dt_test:.0f} K)",
             f"  rise grows as I^n; teaching joint limit {limit:.0f} K",
             "  exponent n   rise at 1600 A K   current at the limit A"]
    out = {}
    for n in (1.6, 1.8, 2.0):
        dt = dt_test * (i_ord / i_test) ** n
        i_lim = i_test * (limit / dt_test) ** (1 / n)
        out[n] = (dt, i_lim)
        lines.append(f"  {n:10.1f}   {dt:16.0f}   {i_lim:21.0f}")
    lines += ["  whatever the exponent, the tested design runs too hot at",
              "  1,600 A: the higher rating needs a larger busbar or contact",
              "  system and its own test - an extrapolation is a reason to",
              "  ask, never a substitute for the report (lesson B)"]
    emit("s_busbar", lines)
    return out


# ------------------------------------------------ 5. timing across the line-up
SPREADS = {"INC-A": 0.5, "WS1": 0.4, "WS2": 0.4, "PVF3": 0.6, "BESS-A": 0.3,
           "BC": 0.5, "INC-B": 0.4, "WS3": 4.6, "PVF1": 0.5, "PVF2": 0.7,
           "BESS-B": 0.4, "SST": 0.6}


def timing_stats(limit: float = 3.5) -> dict:
    vals = list(SPREADS.values())
    m = sum(vals) / len(vals)
    sd = (sum((v - m) ** 2 for v in vals) / (len(vals) - 1)) ** 0.5
    z = [(v - m) / sd for v in vals]
    rz = pf.robust_z(vals)
    names = list(SPREADS)
    lines = ["pole close-time spread of the 12 breakers, ms; scores against the",
             f"  line-up (flag above {limit})",
             "  panel    spread   ordinary z   robust z"]
    for p, v, a, b in zip(names, vals, z, rz):
        lines.append(f"  {p:7s}  {v:6.1f}   {a:10.1f}   {b:8.1f}")
    flag_z = [p for p, a in zip(names, z) if abs(a) > limit]
    flag_r = [p for p, b in zip(names, rz) if abs(b) > limit]
    zmax = (len(vals) - 1) / len(vals) ** 0.5
    lines += [f"  ordinary z flags: {', '.join(flag_z) or 'none'}; robust z flags: "
              f"{', '.join(flag_r)}",
              f"  with 12 values the ordinary z can never pass {zmax:.2f}: the",
              "  outlier inflates the very sd it is measured by; the median",
              "  and MAD are not moved by it (ch 41)"]
    emit("s_timing", lines)
    return dict(flag_z=flag_z, flag_r=flag_r, zmax=zmax)


# ------------------------------------------------ 6. contact resistance, FAT to site
SAT = {p: tuple(round(r * 1.02) for r in v) for p, v in src.CONTACTS.items()}
SAT["BESS-A"] = (49, 35, 36)
SAT["PVF1"] = (37, 36, 36)                      # repaired after the FAT


def fat_to_site(limit: float = 1.2) -> dict:
    lines = [f"main-circuit resistance at the FAT and at site, ratio limit "
             f"{limit} (teaching)", "  panel    pole   FAT   site   ratio"]
    odd = []
    for p, v in src.CONTACTS.items():
        for k, (a, b) in enumerate(zip(v, SAT[p])):
            r = b / a
            if r > limit:
                odd.append((p, f"L{k + 1}", a, b, r))
                lines.append(f"  {p:7s}  L{k + 1}    {a:3d}   {b:4d}   {r:5.2f}")
    lines += [f"  rises: {', '.join(f'{p} {pl}' for p, pl, *_ in odd)}",
              "  BESS-A pole L1 rose 40 % between the factory and the site",
              "  while its neighbours stayed: a joint moved in transport -",
              "  the FAT record is what makes the site reading mean something;",
              "  PVF1 L2 fell to its neighbours after the factory repair"]
    emit("s_fatsite", lines)
    return dict(odd=odd)


# ------------------------------------------------ 7. wire sizes by circuit class
MIN_MM2 = {"CT": 2.5, "VT": 1.5, "trip": 1.5, "DC supply": 2.5, "signal": 0.75}
WIRES = [   # wire, class, mm2
    ("101", "trip", 1.5), ("102", "trip", 1.5), ("103", "CT", 2.5), ("104", "CT", 2.5),
    ("105", "CT", 1.5), ("106", "CT", 2.5), ("107", "VT", 1.5), ("108", "VT", 1.5),
    ("109", "VT", 1.0), ("110", "trip", 1.5), ("111", "trip", 1.5), ("112", "trip", 0.75),
    ("113", "signal", 0.75), ("114", "signal", 0.75), ("115", "DC supply", 2.5),
    ("116", "DC supply", 1.5), ("117", "signal", 0.75), ("118", "signal", 0.75),
]


def wire_sizes() -> list:
    bad = [(w, c, s, MIN_MM2[c]) for w, c, s in WIRES if s < MIN_MM2[c]]
    lines = ["wire sizes of panel WS1 against the teaching rule by circuit class",
             "  class: minimum mm2  " + "; ".join(f"{c} {m}" for c, m in MIN_MM2.items())]
    lines += [f"  wire {w}: {c} in {s} mm2, rule {m}" for w, c, s, m in bad]
    lines += [f"  {len(bad)} wires under the rule: a CT wire too thin adds burden and",
              "  can saturate the core in a fault; a thin trip or supply wire",
              "  drops voltage at the coil - the wire list carries the class",
              "  of each wire so the check runs before any wire is cut"]
    emit("s_wires", lines)
    return bad


# ------------------------------------------------ 8. FAT plan
FUNCS = {"incomer": 14, "feeder": 9, "coupler": 6, "station": 7}
KIND = {p: ("incomer" if p.startswith("INC") else "coupler" if p == "BC" else
            "station" if p == "SST" else "feeder") for p in src.PANELS}


def fat_plan(minutes: float = 12.0, day_h: float = 7.0,
             witness_share: float = 0.4) -> dict:
    funcs = sum(FUNCS[KIND[p]] for p in src.PANELS)
    hours = funcs * minutes / 60
    days = hours / day_h
    w_days = days * witness_share
    lines = [f"FAT of the line-up: {funcs} functions at {minutes:.0f} minutes each "
             "(teaching)",
             f"  {hours:.0f} hours, {days:.1f} test days of {day_h:.0f} h",
             f"  buyer witnesses the trip matrix, interlocks and one panel of",
             f"  each kind in full: about {witness_share:.0%} of the time, "
             f"{w_days:.1f} days",
             "  the rest is reviewed from the maker's records - which is why",
             "  the records must be read line by line (lessons A-C)"]
    emit("s_fatplan", lines)
    return dict(funcs=funcs, days=days, w_days=w_days)


# ------------------------------------------------ 9. settings history
REL = {"50": 1.6, "51": 0.9, "51N": 0.2, "tms": 0.15, "fw": "7.3"}
HISTORY = [   # stage, settings of PVF2, change record?
    ("FAT", dict(REL, tms=0.25), None),
    ("FAT reload", dict(REL), "C-PVF2-01"),
    ("SAT", dict(REL), None),
    ("month 3", dict(REL, **{"51N": 0.3}), None),
    ("month 9", dict(REL, **{"51N": 0.3}), None),
]


def history() -> dict:
    lines = ["settings fingerprints of relay PVF2 through its first year",
             "  stage        fingerprint        same as before   change record"]
    prev, odd = None, []
    for stage, s, rec in HISTORY:
        fp = cm.fingerprint(s)
        same = "-" if prev is None else ("yes" if fp == prev else "NO")
        lines.append(f"  {stage:11s}  {fp}   {same:14s}   {rec or '-'}")
        if same == "NO" and not rec:
            odd.append(stage)
        prev = fp
    lines += [f"  changed without a record: {', '.join(odd)}",
              "  the reload at the FAT has its record; the change at month 3",
              "  has none - someone raised the earth-fault stage; the",
              "  fingerprint finds the change, the register asks who and why",
              "  (ch 26 settings register, ch 38 change control)"]
    emit("s_history", lines)
    return dict(odd=odd)


# ------------------------------------------------ 10. schedule revisions
def revisions() -> dict:
    rev_b = {r["id"]: r for r in src.schedule()[:12]}
    rev_c = {k: dict(v) for k, v in rev_b.items()}
    rev_c["W003"]["size_mm2"] = 400
    rev_c["W008"]["length_m"] = 1290
    del rev_c["W012"]
    rev_c["W027"] = dict(id="W027", **{"from": "T12"}, to="T11",
                         type="33 kV Al XLPE 3c", size_mm2=240, length_m=640, cores=3)
    added = sorted(set(rev_c) - set(rev_b))
    removed = sorted(set(rev_b) - set(rev_c))
    changed = [(k, f, rev_b[k][f], rev_c[k][f]) for k in sorted(set(rev_b) & set(rev_c))
               for f in rev_b[k] if rev_b[k][f] != rev_c[k][f]]
    lines = ["cable schedule rev B against rev C (wind strings only)",
             f"  added: {', '.join(added)}; removed: {', '.join(removed)}"]
    lines += [f"  changed: {k} {f} {a} -> {b}" for k, f, a, b in changed]
    lines += ["  each change reaches something already done: W003's larger",
              "  size needs a 400 mm2 drum and larger lugs and connectors;",
              "  W008's longer route may need a joint; W012 replaced by W027",
              "  reverses the string's far end - drums allocated, kits bought",
              "  and terminations planned for rev B are checked against rev C"]
    emit("s_revisions", lines)
    return dict(added=added, removed=removed, changed=changed)


# ------------------------------------------------ 11. drums re-planned
def replan(need=(970, 690, 690)) -> dict:
    def ffd(lengths, drum):
        bins = []
        for x in sorted(lengths, reverse=True):
            for b in bins:
                if sum(b) + x <= drum:
                    b.append(x)
                    break
            else:
                bins.append([x])
        return bins
    lines = [f"re-ordering 400 mm2 for {len(need)} circuits ({sum(need):,} m) after "
             "the rejects",
             "  drum m   drums   cut waste m   fill"]
    out = {}
    for drum in (1000, 1500, 2500):
        bins = ffd(need, drum)
        waste = len(bins) * drum - sum(need)
        out[drum] = (len(bins), waste)
        lines.append(f"  {drum:6d}   {len(bins):5d}   {waste:11d}   "
                     f"{sum(need) / (len(bins) * drum):4.0%}")
    best = min(out, key=lambda d: out[d][1])
    lines += [f"  1,000 and 1,500 m drums leave the same {out[1000][1]} m; two 1,500 m",
              "  drums mean one drum fewer to ship and handle; one",
              f"  {best:,} m drum leaves only {out[best][1]} m but carries all three circuits",
              "  on one drum (one delay holds three strings) and needs the",
              "  transport check of ch 24 - the choice is written into the",
              "  allocation table before the order"]
    emit("s_replan", lines)
    return out


# ------------------------------------------------ 12. ITP against failure modes
MODES = {
    "conductor resistance high": ["drum resistance at 20 C"],
    "insulation thin or off centre": ["drum-end thickness"],
    "contaminated compound": ["PD result with background", "compound lot record"],
    "sheath damaged in laying": ["sheath integrity after laying"],
    "termination workmanship": ["jointing record and photos"],
    "crimp tool out of adjustment": ["pull test by tool"],
    "joint loosening in service": [],
    "bad contact in a breaker pole": ["main-circuit resistance, pole to pole"],
    "slow mechanism": ["travel curve against baseline"],
    "gas leak": ["density series"],
    "wrong CT ratio or polarity": ["CT record against schedule"],
    "wiring error in a panel": ["point-to-point", "marker check"],
    "wrong trip routing": ["trip matrix"],
    "wrong settings loaded": ["fingerprint against register"],
    "CT circuit earthed twice": ["circuit search of the wire list"],
    "design change not in drawings": [],
}


def itp_cover() -> dict:
    gaps = [m for m, c in MODES.items() if not c]
    single = [m for m, c in MODES.items() if len(c) == 1]
    lines = [f"inspection and test plan against {len(MODES)} failure modes of this "
             "chapter",
             f"  modes with no check: {len(gaps)}"]
    lines += [f"    {m}" for m in gaps]
    lines += [f"  modes with one check only: {len(single)} of {len(MODES)}",
              "  joint loosening shows only in service: thermography and",
              "  torque marks go into the maintenance plan (ch 52); drawing",
              "  revisions after FAT changes get their own check (lesson C) -",
              "  an ITP is complete when every failure mode has a check"]
    emit("s_itp", lines)
    return dict(gaps=gaps, single=len(single))


if __name__ == "__main__":
    sampling()
    capacitance()
    pd_results()
    busbar_rise()
    timing_stats()
    fat_to_site()
    wire_sizes()
    fat_plan()
    history()
    revisions()
    replan()
    itp_cover()
