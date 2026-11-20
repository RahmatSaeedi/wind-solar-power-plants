"""Chapter 46, lab D: plant traceability - the cable schedule validated
before it is used, one feeder of the one-line mapped to switchgear
compartments, terminal drawings and tests, and an inspection and test
matrix with who may do each check.

Run from the project root:   python -m companion.ch46.lab_d
Writes companion/ch46/expected/d_*.txt.
Teaching values (A-482, A-488, A-489); no test procedure, no live work.
"""
from __future__ import annotations

from companion.ch46 import sources as src
from companion.ch46.common import emit
from plantp import cablemfg as km


# ------------------------------------------------ 1. cable schedule
def schedule() -> dict:
    rows = src.schedule()
    probs = km.check_schedule(rows, src.ENDS, src.SIZES)
    lines = [f"33 kV cable schedule as issued: {len(rows)} cables (planted faults)",
             "  cable   problem"]
    for cid, p in probs:
        lines.append(f"  {cid:6s}  {p}")
    lines += [f"  {len(probs)} problems in {len({c for c, _ in probs})} cables; every",
              "  one would reach a drum order, a pull plan or a loss sum if",
              "  the schedule were used as issued - the checker runs on",
              "  every revision, and a schedule that fails goes back to its",
              "  author before anyone orders cable (ch 38)"]
    emit("d_schedule", lines)
    return dict(n=len(rows), problems=probs)


# ------------------------------------------------ 2. one-line to terminal and test
def mapping() -> dict:
    gaps = []
    lines = ["feeder WS1: one-line item -> compartment -> terminal drawing -> tests",
             "  item                      compartment          drawing     tests"]
    for item, comp, dwg, tests in src.ONELINE:
        lines.append(f"  {item:25s} {comp:20s} {dwg or '-':11s} {tests or '-'}")
        if not dwg:
            gaps.append(f"{item}: no terminal drawing")
        if not tests:
            gaps.append(f"{item}: no test")
        elif "SAT" not in tests:
            gaps.append(f"{item}: no site test")
    lines += ["  gaps:"] + [f"    {g}" for g in gaps]
    lines += [
              "  every item of the one-line must land in a compartment, on a",
              "  terminal drawing and in a site test (a factory test where",
              "  the item is made in the panel); a gap here is a gap in the",
              "  commissioning record later (ch 23, ch 50)"]
    emit("d_mapping", lines)
    return dict(gaps=gaps)


# ------------------------------------------------ 3. inspection and test matrix
MATRIX = [   # check, where, evidence, who
    ("conductor resistance, drum", "cable factory", "routine report",
     "maker's test bay"),
    ("sheath and insulation integrity", "after laying", "site record",
     "test contractor, qualified"),
    ("termination workmanship", "site", "photos, checklist, crimp record",
     "certified jointer"),
    ("main-circuit resistance", "switchgear factory", "routine report",
     "maker's test bay"),
    ("interlocks, mechanical and electrical", "factory and site", "checklist",
     "maker; commissioning engineer"),
    ("wiring point to point", "panel shop", "marked wire list", "panel builder"),
    ("relay settings fingerprint", "panel FAT and site", "register entry",
     "protection engineer"),
    ("secondary injection, trip paths", "site", "test sheets",
     "protection engineer, qualified"),
    ("energisation", "site", "switching programme, permit",
     "authorised person only"),
]


def matrix() -> int:
    lines = ["inspection and test matrix of the 33 kV system (teaching)",
             "  check                                 where",
             "    who"]
    for check, where, ev, who in MATRIX:
        lines.append(f"  {check:37s} {where}")
        lines.append(f"    {who}")
    q = [c for c, _, _, w in MATRIX if "qualified" in w or "authorised" in w
         or "certified" in w]
    lines += [f"  {len(q)} of {len(MATRIX)} checks name a qualified, certified or "
              "authorised",
              "  person: the matrix states who may do each check; anything",
              "  touching gear that can be live is done under the site's",
              "  permit system by those people, never from this book (ch 32)"]
    emit("d_matrix", lines)
    return len(q)


# ------------------------------------------------ 4. rejected drums to circuits
def drum_trace() -> dict:
    from companion.ch46 import examples_a as ea
    from companion.ch46 import examples_e as ee
    rej = [d for d, (_, ok) in ea.drums()["out"].items() if not ok]
    rows = {r["id"]: r for r in src.schedule()}
    hit = [(d, ee.ALLOCATED[d]) for d in rej if d in ee.ALLOCATED]
    spare = [d for d, (_, ok) in ea.drums()["out"].items()
             if ok and d not in ee.ALLOCATED.values()]
    lines = ["rejected 400 mm2 drums traced to the circuits planned from them"]
    for d, c in hit:
        r = rows[c]
        to = r["to"] if r["to"] in src.ENDS else r["to"] + " (?)"
        lines.append(f"  {d} -> {c}  {r['from']} to {to}, {r['length_m']} m")
    lines.append("  (?) the far end 'T13' is one of the schedule's faults "
                 "(d_schedule)")
    need = sum(rows[c]["length_m"] for _, c in hit)
    lines += [f"  {len(hit)} circuits lose their drum: {need:,} m of 400 mm2 to "
              "re-order",
              "  (one per string: WS3, PVF1 and PVF3 each wait on a drum) - the",
              "  allocation table is what turns a drum's number into a",
              "  string's date; without it the reject is only a drum number"]
    emit("d_drums", lines)
    return dict(hit=hit, need=need)


# ------------------------------------------------ 5. dossier of each cable
def dossier() -> dict:
    rows = [r for r in src.schedule()]
    have = {}
    for k, r in enumerate(rows):
        have[(r["id"], k)] = dict(drum=True, report=True, term_a=True, term_b=True,
                                  site=True)
    keys = list(have)
    have[keys[1]]["term_b"] = False                     # W002 far end
    have[keys[9]]["report"] = False                     # W010: drum rejected
    have[keys[12]]["site"] = False                      # W013 not tested
    have[keys[22]]["term_a"] = False                    # W023
    have[keys[22]]["term_b"] = False
    have[keys[25]]["drum"] = False                      # W026: drum not recorded
    items = ["drum", "report", "term_a", "term_b", "site"]
    tot = len(have) * len(items)
    got = sum(v[i] for v in have.values() for i in items)
    full = sum(all(v.values()) for v in have.values())
    lines = [f"records of each of the {len(rows)} cables: drum, routine report,",
             "  termination at each end, site test",
             f"  {got} of {tot} records present ({got / tot:.1%}); complete "
             f"cables: {full} of {len(rows)}",
             "  missing:"]
    for (cid, _), v in have.items():
        miss = [i for i in items if not v[i]]
        if miss:
            lines.append(f"    {cid}: {', '.join(miss)}")
    lines += [f"  {got / tot:.0%} of the records sounds nearly complete; "
              f"{len(rows) - full} of {len(rows)} cables",
              "  cannot be handed over - completeness is counted by item,",
              "  accepted by cable (ch 38 handover score, ch 50)"]
    emit("d_dossier", lines)
    return dict(got=got, tot=tot, full=full)


# ------------------------------------------------ 6. termination kit recall
TERMS = [   # cable, end, kit lot
    ("W001", "SWG/WS1", "K-22"), ("W001", "T01", "K-22"),
    ("W002", "T01", "K-23"), ("W002", "T02", "K-23"),
    ("W005", "SWG/WS2", "K-22"), ("W005", "T05", "K-23"),
    ("W009", "SWG/WS3", "K-24"), ("W013", "SWG/PVF1", "K-23"),
    ("W013", "PVF1-1", "K-24"), ("W023", "SWG/BESS-A", "K-24"),
]


def recall(lot: str = "K-23") -> dict:
    hit = [(c, e) for c, e, k in TERMS if k == lot]
    panels = sorted({e[4:] for _, e in hit if e.startswith("SWG/")})
    lines = [f"kit maker's notice on termination kit lot {lot}: where are they?"]
    lines += [f"  {c} at {e}" for c, e in hit]
    lines += [f"  {len(hit)} terminations on {len({c for c, _ in hit})} cables; "
              f"in the switchgear: {', '.join(panels)}",
              "  the jointing record of each termination carries its kit lot;",
              "  without it every termination of the plant would be suspect -",
              f"  with it the inspection list has {len(hit)} lines (ch 24 jointing",
              "  records, ch 52 maintenance)"]
    emit("d_recall", lines)
    return dict(hit=hit, panels=panels)


if __name__ == "__main__":
    schedule()
    mapping()
    matrix()
    drum_trace()
    dossier()
    recall()
