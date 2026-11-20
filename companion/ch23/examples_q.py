"""Chapter 23 - drawing development checks done by program (title blocks,
cross-references, legends, tag names), the balance of single-phase loads
on the station-service board, and a connection asset shared with a
third party: losses allocated three ways and the boundaries it adds.

Run from the project root:   python -m companion.ch23.examples_q
Writes companion/ch23/expected/q_*.txt. Teaching data (A-316 extended:
drawing set, single-phase loads, third-party generator).
"""
from __future__ import annotations

import cmath
import math
import re

from companion.ch23 import sources as src
from companion.ch23.common import emit

# [start: titleblock]
FIELDS = ("project", "number", "title", "revision", "status", "date",
          "drawn", "checked", "approved")
def sheet(number, title, rev, status, date, drawn, checked, approved):
    return dict(project="Plant P", number=number, title=title, revision=rev,
                status=status, date=date, drawn=drawn, checked=checked,
                approved=approved)


SHEETS = [
    sheet("PLP-ELE-DWG-0005", "one-line, plant", "C", "IFC", "2026-11-10",
          "AB", "CD", "EF"),
    sheet("PLP-ELE-DWG-0006", "one-line, 33 kV section A", "B", "IFC",
          "2026-11-10", "AB", "CD", ""),
    sheet("PLP-ELE-DWG-006", "one-line, 33 kV section B", "B", "IFA",
          "2026-11-10", "AB", "CD", "EF"),
    sheet("PLP-ELE-DWG-0007", "station service", "", "IFC", "2026-11-12",
          "GH", "CD", "EF"),
    sheet("PLP-ELE-DWG-0008", "export bay", "A", "IFR", "2026-11-14",
          "GH", "GH", ""),
]
NUMBER = re.compile(r"^PLP-[A-Z]{3}-(CAL|DWG|SPC|REP|REG|PRO|LST)-\d{4}$")


def title_problems(sheet: dict) -> list:
    out = [f"missing {f}" for f in FIELDS if not sheet.get(f)
           and not (f == "approved" and sheet.get("status") in ("IFR", "IFA"))]
    if not NUMBER.match(sheet.get("number", "")):
        out.append("number not in the register format")
    if sheet.get("drawn") and sheet.get("drawn") == sheet.get("checked"):
        out.append("checked by the drafter")
    return out
# [end: titleblock]


def title_blocks() -> None:
    lines = ["title-block check of five sheets (teaching):"]
    for s in SHEETS:
        p = title_problems(s)
        lines.append(f"  {s['number']:17s} {s['status']:4s} {'; '.join(p) if p else 'ok'}")
    lines += ["  an approval is required only from IFC on; a sheet checked",
              "  by its own drafter has not been checked; a number outside",
              "  the register cannot be found again - faults a",
              "  program finds in seconds, before a reviewer reads a line"]
    emit("q_titles", lines)


XREF = {   # sheet -> references "continued on" other sheets
    "0005/1": ["0006/1", "0007/1"],
    "0006/1": ["0005/1", "0006/2"],
    "0006/2": ["0006/1", "0006/3"],
    "0007/1": ["0005/1", "0006/2"],
}


def cross_refs() -> None:
    sheets = set(XREF)
    broken = [(s, r) for s, refs in XREF.items() for r in refs if r not in sheets]
    back = [(s, r) for s, refs in XREF.items() for r in refs
            if r in sheets and s not in XREF[r]]
    lines = ["cross-references between sheets (continued-on arrows):"]
    lines += [f"  {s} -> {r}: the target sheet does not exist" for s, r in broken]
    lines += [f"  {s} -> {r}: no reference back" for s, r in back]
    lines += ["  a broken arrow leaves a wire going nowhere on paper; a",
              "  missing return arrow leaves the reader of the other sheet",
              "  unaware where the wire comes from - both are listed for",
              "  the drafter, not judged by the program"]
    emit("q_xref", lines)


LEGEND = {"breaker", "disconnector", "transformer", "cable", "line"}


def legend() -> None:
    g = src.plant()
    g2 = src.plant()
    src.pv_block_detail(g2)
    used = {b.kind for b in g2.branches}
    missing = sorted(used - LEGEND)
    unused = sorted(LEGEND - used)
    lines = ["legend against the symbols used (plant model with one PV block):",
             f"  kinds used: {', '.join(sorted(used))}",
             f"  missing from the legend: {', '.join(missing) if missing else 'none'}",
             f"  in the legend but unused: {', '.join(unused) if unused else 'none'}",
             "  the PV block detail brought new symbols the legend of the",
             "  plant sheet lacks: each sheet's legend is built from what",
             "  the sheet shows, not copied from the last project",
             f"  (plant without the detail: {len(g.branches)} branches,"
             f" with it: {len(g2.branches)})"]
    emit("q_legend", lines)


TAG = re.compile(r"^=[A-Z0-9]+(-[A-Z0-9]+)*$")
TAGS = ["=WS1-Q1", "=WS1-W2", "=T1-Q2", "WS2-Q1", "=PVF1-1-T1", "=MV-Q0", "=ws3-q1",
        "=E1-Q9", "=BESS-A-Q1", "=A1 T1"]


def naming() -> None:
    bad = [t for t in TAGS if not TAG.match(t)]
    lines = ["tag names against the designation pattern (teaching pattern):",
             f"  {len(TAGS)} tags checked, {len(bad)} malformed: {', '.join(bad)}",
             "  a missing '=' prefix, lower case and a space each break",
             "  searching, sorting and the link to the schedule; the",
             "  pattern itself comes from the project's designation rules",
             "  (IEC 81346, ch 18 and lesson A); the program only applies it"]
    emit("q_naming", lines)


# [start: balance]
def phase_currents(loads: dict) -> tuple:
    """Phase currents (A) and neutral current of single-phase loads (kW at
    unity power factor, 230 V) assigned to L1, L2, L3."""
    i = {p: sum(kw for kw, ph in loads.values() if ph == p) * 1e3 / 230
         for p in ("L1", "L2", "L3")}
    a = cmath.rect(1, 2 * math.pi / 3)
    n = abs(i["L1"] + i["L2"] * a * a + i["L3"] * a)
    return i, n
# [end: balance]


SINGLE = {"yard lighting A": (6.0, "L1"), "yard lighting B": (6.0, "L1"),
          "building lighting": (3.0, "L2"), "sockets control room": (4.0, "L1"),
          "sockets workshop": (6.0, "L2"), "panel heaters": (5.0, "L1"),
          "kitchen and facilities": (4.0, "L3"), "security cameras": (1.0, "L3")}


def balance() -> None:
    i, n = phase_currents(SINGLE)
    avg = sum(i.values()) / 3
    lines = ["single-phase loads on the 400/230 V station board (teaching):",
             "  as first drawn:  " + "  ".join(f"{p} {v:5.1f} A" for p, v in i.items())
             + f"   N {n:5.1f} A",
             f"    unbalance (max - mean)/mean: {(max(i.values()) - avg) / avg:.0%}"]
    moved = dict(SINGLE, **{"yard lighting B": (6.0, "L3"), "panel heaters": (5.0, "L2")})
    j, m = phase_currents(moved)
    avg2 = sum(j.values()) / 3
    lines += ["  lighting B to L3, heaters to L2:",
              "                   " + "  ".join(f"{p} {v:5.1f} A" for p, v in j.items())
              + f"   N {m:5.1f} A",
              f"    unbalance: {(max(j.values()) - avg2) / avg2:.0%}",
              "  the busiest phase sets the cable and breaker; the neutral",
              "  carries the difference (and the third harmonics of UPS and",
              "  LED drivers, which add instead of cancel - ch 27); the",
              "  phase of each circuit is a column of the schedule"]
    emit("q_balance", lines)


def shared() -> None:
    r = 0.12 * 7.06                           # ohm, the 132 kV line (ch 18)
    p_mw, q_mw = 100.0, 40.0
    def loss(mw: float) -> float:
        i = mw * 1e6 / (math.sqrt(3) * 132e3)
        return 3 * i ** 2 * r / 1e6           # MW
    total = loss(p_mw + q_mw)
    own = loss(p_mw)
    lines = ["a third-party generator (40 MW) shares Plant P's 132 kV line:",
             f"  losses at full output: alone {own:.3f} MW, shared {total:.3f} MW",
             "  allocation of the shared losses        Plant P   third party"]
    pro = total * p_mw / (p_mw + q_mw)
    inc_tp = total - own
    tp_alone = loss(q_mw)
    avg_marg = {"pro rata to output": (pro, total - pro),
                "third party connected last": (own, inc_tp),
                "Plant P connected last": (total - tp_alone, tp_alone)}
    for k, (a, b) in avg_marg.items():
        lines.append(f"  {k:36s} {a:9.3f}   {b:11.3f}")
    lines += ["  the losses grow with the square of the current: whoever is",
              "  counted 'last' carries the cross term 2 I1 I2 R; the rule",
              "  moves about 0.4 MW at full output from one owner to the",
              "  other - a commercial term, decided in the agreement",
              "  the line becomes a third-party connection asset: a meter",
              "  for each generator before the shared part, the rule for",
              "  losses in the agreement, one more owner on the isolation",
              "  and test boundaries, and protection that serves both"]
    emit("q_shared", lines)


if __name__ == "__main__":
    title_blocks()
    cross_refs()
    legend()
    naming()
    balance()
    shared()
