"""Chapter 33, lab D (worked example 1): the impact - mitigation -
monitoring register of Plant P, a checker that finds the gaps a draft
register usually has, and the split between illustrative controls and
conditions the permits will set.

Run from the project root:   python -m companion.ch33.lab_d
Writes companion/ch33/expected/d_*.txt.
Teaching values (A-382); significance ratings, controls and conditions
come from the impact assessment, the permits and the lenders' plan.
"""
from __future__ import annotations

from companion.ch33 import sources as src  # noqa: F401  (puts plantp on the path)
from companion.ch33.common import emit

# [start: register]
REGISTER = [  # (id, impact, phase, before, after, mitigation, indicator,
              #  frequency, owner, source)  source: P permit, I illustrative
    ("E01", "night noise at camp B", "O", "M", "L",
     "reduced mode in camp months",
     "LAeq at camp", "quarterly", "O&M manager", "P"),
    ("E02", "dust at village", "C", "M", "L",
     "water, speed, wind rule",
     "dust days over trigger", "daily", "site manager", "P"),
    ("E03", "village wells drawdown", "C,O", "H", "M",
     "pumping limit, monitoring",
     "well levels", "monthly", "E&S manager", "P"),
    ("E04", "raptor collisions", "O", "H", "M",
     "siting, seasonal shutdown",
     "carcass search", "weekly in season", "", "P"),
    ("E05", "bat collisions", "O", "M", "L", "autumn night cut-in 6 m/s",
     "carcass search", "weekly in autumn", "O&M manager", "P"),
    ("S01", "herders' access to spring", "C,O", "H", "L",
     "fence gap, crossing",
     "route open, survey", "quarterly", "E&S manager", "I"),
    ("S02", "traffic at the school", "C", "H", "M", "truck hold, marshal",
     "", "daily", "logistics lead", "I"),
    ("S03", "heritage near the ruin", "C", "M", "H", "re-route, archaeologist",
     "watching brief log", "during works", "E&S manager", "P"),
    ("E06", "fire-water runoff", "O", "M", "L", "closed pond, testing",
     "pond outlet log", "after events", "O&M manager", "I"),
]
# [end: register]

RANK = {"L": 1, "M": 2, "H": 3}


def check(reg) -> list[str]:
    """Rules: every row has an indicator, a frequency and an owner; the
    residual significance is not higher than before mitigation."""
    out = []
    for r in reg:
        rid, imp, _ph, b, a, _m, ind, freq, own, _s = r
        if not ind:
            out.append(f"{rid} {imp}: no indicator")
        if not freq:
            out.append(f"{rid} {imp}: no frequency")
        if not own:
            out.append(f"{rid} {imp}: no owner")
        if RANK[a] > RANK[b]:
            out.append(f"{rid} {imp}: residual {a} above {b} - mitigation wrong")
    return out


def table() -> None:
    lines = ["impact - mitigation - monitoring register of Plant P (draft)",
             "  id   impact                       phase  before after  source"]
    for r in REGISTER:
        lines.append(f"  {r[0]}  {r[1]:28s} {r[2]:5s}  {r[3]:6s} {r[4]:5s}  {r[9]}")
    errs = check(REGISTER)
    lines.append(f"  checker findings: {len(errs)}")
    lines += [f"    {e}" for e in errs]
    emit("d_register", lines)


def fixed() -> None:
    reg = [list(r) for r in REGISTER]
    reg[3][8] = "O&M manager"
    reg[6][6] = "trucks in school hours (count)"
    reg[7][4] = "L"
    reg[7][5] = "re-route outside the buffer"
    left = check([tuple(r) for r in reg])
    p = sum(1 for r in reg if r[9] == "P")
    lines = ["the register after review",
             f"  checker findings: {len(left)}",
             f"  rows that a permit will set (P): {p}; illustrative (I): {len(reg) - p}",
             "  P rows are drafts of conditions: the indicator, limit and",
             "  frequency are copied from the permit when it is issued,",
             "  and the register says so; I rows are the project's own",
             "  controls and can be changed through management of change",
             "  - the reader never mistakes one for the other"]
    emit("d_fixed", lines)


if __name__ == "__main__":
    table()
    fixed()
