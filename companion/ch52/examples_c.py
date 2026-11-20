"""Chapter 52, lesson C: fault diagnosis and restoration - an event
chronology across clocks, isolation authority as a record, a root-cause
chain checked link by link for evidence, down time by stage, repair
verified against the commissioning baseline, repeat failures, and the
permit records of fault work.

Run from the project root:   python -m companion.ch52.examples_c
Writes companion/ch52/expected/c_*.txt. Teaching values (A-532).
"""
from __future__ import annotations

import numpy as np

from companion.ch52 import sources as src
from companion.ch52.common import emit


# ------------------------------------------------ 1. chronology
def chronology() -> dict:
    ev = sorted(src.EVENTS_T03)
    first = ev[0]
    lines = ["T03 trip: events from four sources on one time base (s from 14:02:00)"]
    lines += [f"  {t:+7.3f}  {s:16s} {e}" for t, s, e in ev]
    rode = [s for t, s, e in ev if "FRT ended" in e]
    lines += [f"  first event: {first[2]} at {first[1]} ({first[0]:+.3f} s) - the cause",
              f"  came from the grid; {rode[0].split()[0]} rode through it and T03 did not:",
              "  the question is T03's own ride-through (DC-link chopper,",
              "  setting or firmware), not the dip - SCADA alone shows a",
              "  'grid loss' alarm at a polling time and would have blamed",
              "  the grid"]
    emit("c_chronology", lines)
    return dict(first=first[1], rode=rode[0].split()[0])


# ------------------------------------------------ 2. isolation authority
AUTHORITY = [   # task, authorised person needed, permit, switching program, grid operator
    ("inspect inverter cabinet (AC breaker open)", True, True, False, False),
    ("replace string fuse in a combiner", True, True, False, False),
    ("open WS1 breaker and earth the feeder", True, True, True, False),
    ("work on the plant HV bay E1", True, True, True, True),
    ("reset a turbine fault from SCADA", False, False, False, False),
    ("change a protection setting", True, True, False, True)]


def authority() -> dict:
    grid = [t for t, *_, g in AUTHORITY if g]
    lines = ["fault work: the authority each task needs (records, not a procedure)",
             "  task                                        AP  permit  program  grid op"]
    lines += [f"  {t:43s} {'yes' if a else ' - ':3s} {'yes' if p else ' - ':6s} "
              f"{'yes' if s else ' - ':7s}  {'yes' if g else ' -'}"
              for t, a, p, s, g in AUTHORITY]
    lines += [f"  {len(grid)} tasks need the grid operator's agreement: those at the",
              "  boundary (ch 23) and a setting it approved (ch 26); the remote",
              "  reset needs none, which is why its use is logged (lesson I)"]
    emit("c_authority", lines)
    return dict(grid=len(grid))


# ------------------------------------------------ 3. root-cause chain
CHAIN = [   # why, answer, evidence
    ("why did T03 stop?", "converter tripped on DC-link overvoltage", "event log"),
    ("why the overvoltage?", "chopper did not fire during the dip", "converter fault record"),
    ("why did the chopper not fire?", "chopper enable set off after a service", "settings file diff"),
    ("why was it off?", "service laptop loaded a test profile", "service report WO-0412"),
    ("why was that not caught?", "no settings check at hand-back", "")]


def rca() -> dict:
    gaps = [w for w, _, e in CHAIN if not e]
    lines = ["T03: the root-cause chain, each answer with its evidence"]
    for w, a, e in CHAIN:
        lines += [f"  {w}", f"     -> {a} [{e or 'NO EVIDENCE'}]"]
    lines += [f"  {len(gaps)} link(s) without evidence: the last answer is a claim until",
              "  the hand-back records are checked - and it is the link the",
              "  corrective action rests on (settings check at every",
              "  hand-back, ch 48 fingerprints)"]
    emit("c_rca", lines)
    return dict(gaps=len(gaps))


# ------------------------------------------------ 4. down time by stage
STAGES = ["detect", "respond", "diagnose", "wait parts", "repair", "test", "return"]
JOBS = {   # minutes by stage
    "T03 converter": [5, 90, 180, 2_880, 240, 60, 30],
    "PVF2-3 fan": [60, 240, 30, 0, 45, 15, 10],
    "BESS-A C2 HVAC": [10, 120, 90, 24_600, 300, 60, 30],
    "WS2 trip": [1, 45, 60, 0, 0, 30, 20],
    "PVF2-3 CB14 fuses": [62_000, 480, 120, 0, 60, 20, 10]}


def stages() -> dict:
    tot = np.array([sum(v[k] for v in JOBS.values()) for k in range(len(STAGES))], float)
    share = tot / tot.sum()
    lines = ["corrective jobs: minutes in each stage of the down time"]
    lines += [f"  {j:16s} " + " ".join(f"{x:6d}" for x in v) for j, v in JOBS.items()]
    lines += ["  stages: " + ", ".join(STAGES)]
    lines += [f"  share of all down time: " + ", ".join(
        f"{s} {p:.0%}" for s, p in zip(STAGES, share) if p >= 0.01)]
    lines += ["  the repair itself is a sliver: the combiner fault sat",
              "  undetected for 43 days (lesson D) and the HVAC part took 17",
              "  days to come - detection and parts are where hours are won"]
    emit("c_stages", lines)
    return dict(share=dict(zip(STAGES, share)))


# ------------------------------------------------ 5. repair verified against the baseline
def verify(seed: int = 521, tol: float = 0.03, n_min: int = 30) -> dict:
    rng = np.random.default_rng(seed)
    bins = np.arange(4, 13)
    base = np.array([0.24, 0.47, 0.82, 1.30, 1.94, 2.70, 3.50, 4.25, 4.75])   # MW, ch 50 test
    after = base * (1 + rng.normal(0, 0.012, bins.size))
    after[2] *= 0.95                                                           # 6 m/s bin low
    n = rng.integers(20, 120, bins.size)
    dev = after / base - 1
    fail = [int(b) for b, d, k in zip(bins, dev, n) if abs(d) > tol and k >= n_min]
    thin = [int(b) for b, k in zip(bins, n) if k < n_min]
    lines = [f"T03 after the repair: power by wind bin against its commissioning baseline",
             f"  (pass: within {tol:.0%} in every bin with at least {n_min} ten-minute points)",
             "  bin m/s  baseline MW  after MW   dev    points"]
    lines += [f"  {b:7d} {x:11.2f} {y:9.2f} {d:+6.1%} {k:7d}" for b, x, y, d, k in
              zip(bins, base, after, dev, n)]
    lines += [f"  failing bins: {fail or 'none'}; bins with too few points: {thin or 'none'}",
              f"  the repair is not accepted yet: the {fail[0]} m/s bin is low with",
              f"  enough data, and the {thin[0]} m/s bin waits for more wind - the",
              "  work order stays open until the test record closes it"]
    emit("c_verify", lines)
    return dict(fail=fail, thin=thin)


# ------------------------------------------------ 6. repeat failures
FAILS = [("=WT03-PIT", 31), ("=WT03-PIT", 74), ("=WT03-CNV", 120), ("=PVF2-3-CB01", 140),
         ("=WT07-GBX", 201), ("=WT03-PIT", 160), ("=PVF2-3-INV", 180), ("=PVF2-3-CB01", 215)]


def repeats(window: int = 90) -> dict:
    by = {}
    for a, d in sorted(FAILS, key=lambda x: x[1]):
        by.setdefault(a, []).append(d)
    rep = {a: ds for a, ds in by.items()
           if any(b - a_ <= window for a_, b in zip(ds, ds[1:]))}
    lines = [f"repeat failures: the same asset failing again within {window} days"]
    lines += [f"  {a:14s} days " + ", ".join(map(str, ds)) for a, ds in by.items()]
    lines += [f"  repeats: {', '.join(rep)}",
              "  the pitch battery failed three times - replacing it each time",
              "  treats the symptom; the charger or the cabinet heat is the",
              "  next question (RCA); the combiner failed again after 75 days"]
    emit("c_repeats", lines)
    return dict(rep=list(rep))


# ------------------------------------------------ 7. permit records of fault work
def permits() -> dict:
    jobs = [(True, True, True), (True, True, True), (True, False, True), (True, True, False),
            (True, True, True), (False, False, False), (True, True, True), (True, True, True)]
    names = ["permit", "isolation verified", "hand-back signed"]
    miss = [sum(1 for j in jobs if not j[k]) for k in range(3)]
    lines = [f"fault jobs of a month: {len(jobs)}; missing records by kind"]
    lines += [f"  {n:20s} {m}" for n, m in zip(names, miss)]
    lines += ["  one job has none at all: a reset in the field that became",
              "  a repair - the moment it did, it needed a permit; the",
              "  hand-back is the record lesson C's root cause rests on"]
    emit("c_permits", lines)
    return dict(miss=miss)


if __name__ == "__main__":
    chronology()
    authority()
    rca()
    stages()
    verify()
    repeats()
    permits()
