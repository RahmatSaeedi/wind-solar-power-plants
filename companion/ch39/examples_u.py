"""Chapter 39, a third round of lessons: prequalification thresholds, a
supplier's factory load and the wait it adds, the logistics chain to
site simulated, whether an offered type-test report applies to the unit
bought, the standards editions cited in the offers, the clarification
log, grievance figures at a sub-supplier, securities that expire before
taking over, and the asset rows a supplier delivers checked by rule.

Run from the project root:   python -m companion.ch39.examples_u
Writes companion/ch39/expected/u_*.txt and diagrams/data/ch39-*.csv.
Teaching values (A-429 to A-432); fictional parties; concepts only.
"""
from __future__ import annotations

import math
import re

import numpy as np

from companion.ch39 import sources as src  # noqa: F401  (plantp on path)
from companion.ch39.common import csv, emit

# ------------------------------------------------- prequalification
PREQ = {  # supplier: answers to the prequalification questionnaire
    "U-A": dict(current_ratio=1.6, refs=6, cap_mva_y=900, iso9001=True,
                hse_rate=0.8),
    "U-B": dict(current_ratio=1.25, refs=3, cap_mva_y=400, iso9001=True,
                hse_rate=1.9),
    "U-C": dict(current_ratio=1.3, refs=4, cap_mva_y=250, iso9001=True,
                hse_rate=1.1),
    "U-D": dict(current_ratio=0.8, refs=5, cap_mva_y=1200, iso9001=False,
                hse_rate=0.9),
}
# [start: prequal]
FLOORS = dict(current_ratio=1.2, refs=3, cap_mva_y=3 * 56, iso9001=True)
CEILING = dict(hse_rate=2.0)          # recordable rate per 200,000 h
# [end: prequal]


def prequal() -> dict[str, list[str]]:
    lines = ["prequalification: floors that every bidder must meet",
             "  (current ratio, references, capacity of 3 x our order in",
             "  MVA a year, quality system, recordable injury rate)"]
    out = {}
    for s, a in PREQ.items():
        fails = [k for k, v in FLOORS.items()
                 if (a[k] < v if not isinstance(v, bool) else a[k] != v)]
        fails += [k for k, v in CEILING.items() if a[k] > v]
        out[s] = fails
        lines.append(f"  {s}  {'qualified' if not fails else 'out: ' + ', '.join(fails)}")
    lines += ["  U-D is not invited to bid; U-B passes every floor by a",
              "  hair - the audit of lesson D later finds its process",
              "  control below the floor. Floors are pass/fail before any",
              "  price is opened: a low price cannot buy back a weak",
              "  balance sheet; U-C's small capacity is checked next"]
    emit("u_prequal", lines)
    return out


# ------------------------------------------------- factory load
def wait_weeks(load: float, service_w: float = 2.0) -> float:
    """Mean wait in a single-server queue (M/M/1): service x rho/(1-rho)."""
    if load >= 1:
        return math.inf
    return service_w * load / (1 - load)


def factory_load() -> dict[str, float]:
    order = 56.0                                  # MVA
    book = {"U-A": 600.0, "U-C": 170.0}           # MVA already booked a year
    lines = ["factory load with our order and the wait it adds",
             "  supplier  capacity  booked + ours  load   mean wait, weeks"]
    out = {}
    for s, booked in book.items():
        cap = PREQ[s]["cap_mva_y"]
        rho = (booked + order) / cap
        w = wait_weeks(rho)
        out[s] = w
        lines.append(f"  {s:8s}  {cap:8.0f}  {booked + order:13.0f}  "
                     f"{rho:4.0%}   {w:6.1f}")
    rows = [(round(r, 2), round(wait_weeks(r), 2))
            for r in np.arange(0.30, 0.955, 0.01)]
    csv("ch39-load.csv", "rho,wait", rows)
    lines += ["  a queue's wait grows as load/(1 - load): at 73 % it is",
              "  about 5 weeks, at 90 % three times that; a busy factory",
              "  is not a better one - the audit asks for its order book"]
    emit("u_load", lines)
    return out


# ------------------------------------------------- logistics chain
LEGS = [  # leg, median days, spread (lognormal sigma)
    ("factory to port", 4.0, 0.3), ("sea passage", 24.0, 0.15),
    ("port and customs", 9.0, 0.6), ("port to site (heavy haul)", 5.0, 0.4)]


def logistics(n: int = 20000, seed: int = 392) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    total = np.zeros(n)
    spread = {}
    for leg, med, sig in LEGS:
        x = rng.lognormal(math.log(med), sig, n)
        spread[leg] = float(np.quantile(x, 0.9) - np.median(x))
        total += x
    med_t, p90 = float(np.median(total)), float(np.quantile(total, 0.9))
    lines = ["the transport chain from factory to site (days, simulated)",
             "  leg                          median  90 % minus median"]
    for leg, med, _ in LEGS:
        lines.append(f"  {leg:28s} {med:6.0f}  {spread[leg]:17.1f}")
    worst = max(spread, key=spread.get)
    lines += [f"  whole chain: median {med_t:.0f} days, 90 % {p90:.0f} days",
              f"  the widest leg is {worst}: the buffer and the",
              "  document preparation go there, not to the sea passage;",
              "  the delivery term of the contract says where the risk",
              "  of loss passes from seller to buyer (concept only)"]
    emit("u_logistics", lines)
    return dict(median=med_t, p90=p90, worst=worst)


# ------------------------------------------ type-test report applies?
OUR = dict(mva=5.6, hv_kv=33.0, um_kv=36.0, cooling="ONAN", windings="Cu",
           design="T-56")
# [start: typetest]
REPORTS = {  # offer: the type-test report it submits
    "U-A": dict(mva=5.6, hv_kv=33.0, um_kv=36.0, cooling="ONAN",
                windings="Cu", design="T-56"),
    "U-B": dict(mva=4.0, hv_kv=33.0, um_kv=36.0, cooling="ONAN",
                windings="Al", design="T-40"),
    "U-C": dict(mva=6.3, hv_kv=33.0, um_kv=36.0, cooling="ONAN",
                windings="Cu", design="T-56"),
}


def applies(rep: dict, our: dict, band: float = 0.15) -> list[str]:
    """Reasons a type-test report does not cover our unit."""
    out = []
    if abs(rep["mva"] - our["mva"]) / our["mva"] > band:
        out.append("rating outside +/- 15 %")
    for k in ("um_kv", "cooling", "windings", "design"):
        if rep[k] != our[k]:
            out.append(f"different {k}")
    return out
# [end: typetest]


def type_tests() -> dict[str, list[str]]:
    lines = ["does the offered type-test report cover the unit we buy?",
             "  (a teaching rule: same design family, insulation level,",
             "  cooling and winding material, rating within +/- 15 %)"]
    out = {}
    for o, rep in REPORTS.items():
        why = applies(rep, OUR)
        out[o] = why
        lines.append(f"  {o}  {rep['mva']:.1f} MVA  "
                     f"{'covers' if not why else 'does not:'}")
        if why:
            lines.append("      " + ", ".join(why))
    lines += ["  U-C's 6.3 MVA report of the same design covers ours by",
              "  the rule; U-B's report is another design and material -",
              "  either a new type test (time, cost) or a deviation priced;",
              "  the real rule is the standard's and the owner's (STD-120)"]
    emit("u_typetest", lines)
    return out


# ------------------------------------------------ standards editions
CITED = {"U-A": "IEC 60076-1 edition 3.0 (2011)",
         "U-B": "IEC 60076-1, an earlier edition",
         "U-C": "IEC 60076-1 (no edition given)"}


def editions() -> dict[str, str]:
    lines = ["standards editions cited in the offers (register: STD-120,",
             "IEC 60076-1:2011, edition 3.0)"]
    out = {}
    for o, c in CITED.items():
        if "3.0" in c:
            v = "matches the register"
        elif "earlier" in c:
            v = "superseded edition: a deviation until shown equal"
        else:
            v = "undated: ask which edition, record the answer"
        out[o] = v
        lines += [f"  {o}  {c}", f"      {v}"]
    lines += ["  the specification names the edition it relies on; an",
              "  offer to another edition is checked clause by clause by",
              "  the engineer, not assumed to be the same"]
    emit("u_editions", lines)
    return out


# ------------------------------------------------- clarifications
CLAR = [  # (question, offer, days to answer or None, changes price?)
    ("loss tolerance basis", "U-A", 3, False),
    ("heat-run witness", "U-B", None, True),
    ("data schedule items", "U-B", 12, True),
    ("coating class proof", "U-C", 5, False),
    ("sound level method", "U-C", 4, False),
    ("monitoring relay link", "U-A", 6, True),
]


def clarifications() -> dict[str, int]:
    deadline = 7
    late = [c for c in CLAR if c[2] is None or c[2] > deadline]
    lines = [f"clarification log of the tender (answers due in {deadline} days)"]
    for q, o, d, price in CLAR:
        lines.append(f"  {o}  {q:24s} {'no answer' if d is None else str(d) + ' days'}"
                     f"{'  price changes' if price else ''}")
    lines += [f"  late or missing: {len(late)}; each is treated as stated in",
              "  the instructions to bidders - here, the least favourable",
              "  reading priced as a deviation; a clarification that",
              "  changes the price is recorded and applied to all bidders"]
    emit("u_clar", lines)
    return dict(late=len(late))


# ------------------------------------------------- grievance figures
DAYS = [3, 5, 6, 8, 9, 12, 14, 15, 21, 25, 28, 34, 41, 47, 60, 75]   # A-430


def grievances() -> dict[str, float]:
    closed30 = sum(d <= 30 for d in DAYS) / len(DAYS)
    med = float(np.median(DAYS))
    over60 = sum(d > 60 for d in DAYS)
    lines = [f"worker grievances at a sub-supplier: {len(DAYS)} closed this year",
             f"  median days to close: {med:.0f}; closed within 30 days: "
             f"{closed30:.0%} (target 80 %)",
             f"  over 60 days: {over60}; escalated to the buyer: 2",
             "  the figures are evidence that the channel works - people",
             "  use it and get answers; a channel with no cases is not",
             "  a clean site, it is a question to ask (lesson G)"]
    emit("u_grievance", lines)
    return dict(closed30=closed30, median=med)


# ------------------------------------------------- securities and dates
def securities() -> dict[int, list[str]]:
    taking_over = 70                          # planned week of taking over
    defects_end = taking_over + 104           # two-year defects period
    bonds = {"performance security": 78, "warranty security": 170}
    lines = ["securities against the dates they must cover (weeks from order)",
             f"  taking over planned at week {taking_over}; defects period "
             f"to week {defects_end}",
             "  performance security to week 78, warranty security to 170",
             "  delay   security that ends before its date (weeks short)"]
    out = {}
    for delay in (0, 10, 20):
        to, de = taking_over + delay, defects_end + delay
        gaps = []
        if bonds["performance security"] < to:
            gaps.append(f"performance -{to - bonds['performance security']} wk")
        if bonds["warranty security"] < de:
            gaps.append(f"warranty -{de - bonds['warranty security']} wk")
        out[delay] = gaps
        lines.append(f"  {delay:2d} wk   {'; '.join(gaps) if gaps else 'covered'}")
    lines += ["  a security with a fixed expiry date shrinks with every",
              "  week of delay; the contract ties extension to the dates",
              "  it covers - wording for the lawyers, dates for the engineer"]
    emit("u_securities", lines)
    return out


# ------------------------------------------ delivered asset rows checked
TAGS = {f"=PVF{f}-{b}-T1" for f in (1, 2, 3) for b in (1, 2, 3, 4)}


def delivered_rows():
    rows = []
    for k, (f, b) in enumerate([(1, 1), (1, 2), (1, 3), (1, 4), (2, 1),
                                (2, 2), (2, 3), (3, 1), (3, 2), (3, 3)]):
        rows.append(dict(tag=f"=PVF{f}-{b}-T1", serial=f"TX-51{k + 1:02d}",
                         mva=5.6, uk=7.0, losses_kw=(4.1, 41.0)))
    rows[3]["serial"] = ""                        # planted problems
    rows[6]["mva"] = 5.5                          # pre-C-017 value
    rows[8]["tag"] = "PVF3-2-T1"                  # tag without '='
    rows[9]["uk"] = 0.07                          # share, not per cent
    return rows


def check_rows() -> dict[str, list[int]]:
    rows = delivered_rows()
    rules = {
        "tag known": lambda r: r["tag"] in TAGS,
        "serial present": lambda r: bool(r["serial"]),
        "rating 5.6 MVA (C-017)": lambda r: r["mva"] == 5.6,
        "impedance in per cent": lambda r: 1.0 < r["uk"] < 20.0,
    }
    lines = [f"asset rows delivered by U-A: {len(rows)} rows, "
             f"{len(rules)} rules"]
    out = {}
    for name, f in rules.items():
        bad = [k + 1 for k, r in enumerate(rows) if not f(r)]
        out[name] = bad
        lines.append(f"  {name:24s} {'ok' if not bad else 'fails row ' + ', '.join(map(str, bad))}")
    clean = sum(all(f(r) for f in rules.values()) for r in rows)
    lines += [f"  rows accepted: {clean} of {len(rows)}; the four go back with",
              "  the rule each failed - payment for the data item waits",
              "  for accepted rows (lesson I), not for a file count"]
    emit("u_rows", lines)
    return out


if __name__ == "__main__":
    prequal()
    factory_load()
    logistics()
    type_tests()
    editions()
    clarifications()
    grievances()
    securities()
    check_rows()
