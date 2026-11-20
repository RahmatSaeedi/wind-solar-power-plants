"""Chapter 47, lab D: quality dossier lab - a release decision for each
tower section from its records, a foundation inspection and quality plan
from an assumed geotechnical basis with the professional approvals it
needs, and the register of decisions only licensed engineers may take.

Run from the project root:   python -m companion.ch47.lab_d
Writes companion/ch47/expected/d_*.txt.
Teaching values (A-496, A-497); no design approval implied.
"""
from __future__ import annotations

from companion.ch47 import sources as src
from companion.ch47.common import emit
from plantp import civilmfg as cv


# ------------------------------------------------ 1. release by section
# [start: release]
def holds_by_section() -> dict[int, list[str]]:
    """Collect every open finding of the records against its section."""
    holds: dict[int, list[str]] = {k: [] for k in (1, 2, 3, 4)}
    for c in src.CERTS:
        for p in cv.check_cert(c, src.ORDER):
            for can in src.PLATES[c["plate"]]:
                sec = int(can.split("-")[0])
                msg = f"{c['plate']}: {p}"
                if msg not in holds[sec]:
                    holds[sec].append(msg)
    for j, w, p, pos, d in src.WELD_LOG:
        r = cv.qualified(src.WELDERS[w], p, pos, d)
        if r != "ok":
            holds[1].append(f"{j}: {r}")
    for k, (share, low) in cv.coverage(src.NDT_PLAN, src.NDT_DONE).items():
        if low:
            holds[1].append(f"NDT {k} {share:.0%}")
    for n in src.NCRS:
        if not n["closed"]:
            sec = {"NCR-202": 2, "NCR-203": 3, "NCR-205": 1, "NCR-206": 1,
                   "NCR-207": 1}[n["id"]]
            holds[sec].append(f"{n['id']} open")
    return holds
# [end: release]


def release() -> dict:
    holds = holds_by_section()
    lines = ["release decision for each tower section from its records"]
    for sec, hs in holds.items():
        lines.append(f"  section {sec}: {'RELEASE' if not hs else 'HOLD'}"
                     f"{'' if not hs else ' - ' + str(len(hs)) + ' open'}")
        lines += [f"    {h}" for h in hs]
    free = [str(k) for k, v in holds.items() if not v]
    held = ", ".join(f"section {k} {len(v)}" for k, v in holds.items() if v)
    lines += [f"  only section {', '.join(free)} may ship; holds: {held} -",
              "  each one closed by a record",
              "  (a re-test, an NDT report, a qualification, a designer's",
              "  acceptance), not by a signature on the release note"]
    emit("d_release", lines)
    return {k: len(v) for k, v in holds.items()}


# ------------------------------------------------ 2. foundation ITP
BASIS = [   # assumed geotechnical basis (teaching, from ch 29/30)
    "founding layer: dense sand and gravel, G 80 MPa (T07: medium sand, 25 MPa)",
    "groundwater below founding level except T07 (0.5 m in the wet season)",
    "allowable pressure set by the geotechnical engineer, not by this book",
]
ITP = [   # step, point, evidence, who accepts
    ("excavation to level, founding layer inspected", "H",
     "inspection record, photos", "geotechnical engineer"),
    ("blinding level and setting out", "W", "survey record", "surveyor"),
    ("anchor cage position and level", "H", "survey before pour",
     "turbine maker's representative"),
    ("reinforcement against drawings and BBS, cover", "H", "checklist, photos",
     "structural engineer"),
    ("embedded items: earthing, ducts", "W", "checklist", "electrical engineer"),
    ("pour: tickets, temperature, specimens", "R", "tickets, specimen log",
     "contractor's QC"),
    ("curing record", "R", "temperature and moisture log", "contractor's QC"),
    ("anchor cage level after pour", "H", "survey after pour",
     "turbine maker's representative"),
    ("28-day strength conformity", "H", "laboratory reports",
     "structural engineer"),
    ("backfill compaction", "W", "density tests", "geotechnical engineer"),
    ("grouting and anchor tensioning", "H", "grout tests, tension records",
     "turbine maker's representative"),
]
LICENSED = {"geotechnical engineer", "structural engineer"}


def itp() -> dict:
    lic = [s for s, _, _, who in ITP if who in LICENSED]
    holds = [s for s, pt, _, _ in ITP if pt == "H"]
    lines = ["assumed geotechnical basis of the foundation plan (teaching):"]
    lines += [f"  - {b}" for b in BASIS]
    lines += [f"inspection and quality plan of one turbine foundation: {len(ITP)} steps,",
              f"  {len(holds)} hold points; accepted by a licensed engineer: {len(lic)}"]
    for s, pt, ev, who in ITP:
        lines.append(f"  [{pt}] {s}")
        lines.append(f"      {ev}; {who}")
    lines += ["  the plan names who accepts each step; a hold point is a step",
              "  the work may not pass until that person signs - the pour does",
              "  not start before the reinforcement and the cage are accepted"]
    emit("d_itp", lines)
    return dict(lic=len(lic), holds=len(holds))


# ------------------------------------------------ 3. approvals register
APPROVALS = [   # decision, who may take it
    ("accept plate P103 after re-test at -20 C", "structural engineer"),
    ("use or replace plate P106 (S275 for S355)", "structural engineer"),
    ("plate P104 with one low impact: re-test or replace", "structural engineer"),
    ("plate P105 with high CEV: procedure re-qualified for it",
     "welding coordinator"),
    ("repair procedure for weld C1-02 and D1-01", "welding coordinator"),
    ("accept pours F03 and F04 or order cores", "structural engineer"),
    ("grout thickness to correct the cage tilt", "turbine maker"),
    ("founding layer at T07 and its improvement", "geotechnical engineer"),
    ("use of zinc lot Z-02 in mild soil", "structural engineer"),
    ("tracker row R-17 tube: accept, straighten or replace", "tracker maker"),
    ("row 7 of PVF1-1: re-drive or accept", "structural engineer"),
]


def approvals() -> dict:
    by = {}
    for d, who in APPROVALS:
        by.setdefault(who, []).append(d)
    lines = [f"decisions this chapter's records raise, and who may take them "
             f"({len(APPROVALS)})"]
    for who, ds in by.items():
        lines.append(f"  {who}: {len(ds)}")
        lines += [f"    {d}" for d in ds]
    lic = sum(len(v) for k, v in by.items() if k in LICENSED)
    lines += [f"  {lic} of {len(APPROVALS)} belong to licensed structural or "
              "geotechnical",
              "  engineers; the rest to the makers' responsible persons - the",
              "  records show the facts, the named person decides, and the",
              "  decision is filed with the record that raised it"]
    emit("d_approvals", lines)
    return dict(lic=lic, n=len(APPROVALS))


if __name__ == "__main__":
    release()
    itp()
    approvals()
