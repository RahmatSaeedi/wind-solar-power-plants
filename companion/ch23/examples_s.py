"""Chapter 23 - three deliverables printed in full from the one-line model:
the switchgear, cable and line schedule with every open item flagged,
the battery's path to the grid with its interfaces, and the electrical
drawing register of the design stage.

Run from the project root:   python -m companion.ch23.examples_s
Writes companion/ch23/expected/s_*.txt. Teaching data (A-316, A-319).
"""
from __future__ import annotations

from companion.ch23 import sources as src
from companion.ch23.common import emit


def rating_text(r: dict) -> str:
    keys = [("km", "km"), ("mm2", "mm2"), ("a", "A"), ("ka", "kA"), ("kv", "kV"), ("mva", "MVA")]
    return " ".join(f"{r[k]:g} {u}" for k, u in keys if k in r)


def full_schedule() -> None:
    g = src.plant()
    kinds = ("breaker", "disconnector", "line", "cable")
    rows = [b for b in g.branches if b.kind in kinds]
    lines = ["switchgear, line and cable schedule (open items flagged *):",
             "  tag          kind         from -> to            rating"
             "          open"]
    n_open = 0
    for b in rows:
        op = b.open_items()
        n_open += bool(op) or b.owner.startswith("open")
        flag = ", ".join(op) if op else ""
        if b.owner.startswith("open") and "owner" not in op:
            flag = (flag + ", owner").lstrip(", ")
        ends = b.a + " -> " + b.b
        mark = ("*" + flag) if flag else ""
        lines.append(f"  {b.tag:12s} {b.kind:12s} {ends:21s}"
                     f" {rating_text(b.rating):15s} {mark}")
    lines += [f"  {len(rows)} rows; {n_open} with open items -"
              " each open item names",
              "  the chapter or the party that will close it (ch 24: cable",
              "  lengths and sections; ch 25-26: ratings and fault duties;",
              "  U-065: the line's owner)"]
    emit("s_schedule", lines)


def bess_trace() -> None:
    g = src.plant()
    lines = ["battery block BESS-B-2 traced to the grid (interfaces on the way):"]
    lines += [f"  {n}" for n in g.crossings("BESS-B-2-LV", "GRID")]
    lines += ["  the battery crosses the same boundaries as a turbine, plus",
              "  one the turbine does not have: it also imports from the",
              "  grid - every meter on the path counts in both directions",
              "  and the protection must see faults fed from either side"]
    emit("s_bess", lines)


REGISTER = [
    ("PLP-ELE-DWG-0001", "inverter skid block diagram (ch 9)", "concept"),
    ("PLP-ELE-DWG-0002", "PV block layout (ch 10)", "concept"),
    ("PLP-ELE-DWG-0003", "export route options and corridor (ch 14)", "concept"),
    ("PLP-ELE-DWG-0004", "architecture diagrams (ch 18)", "concept"),
    ("PLP-ELE-DWG-0005", "one-line diagram, plant", "IFR"),
    ("PLP-ELE-DWG-0006", "one-line diagram, 33 kV sections", "IFR"),
    ("PLP-ELE-DWG-0007", "station-service and DC one-line", "IFR"),
    ("PLP-ELE-DWG-0008", "export bay arrangement (ch 25)", "IFR"),
    ("PLP-ELE-LST-0004", "equipment schedule", "IFR"),
    ("PLP-ELE-LST-0005", "auxiliary load register", "IFR"),
    ("PLP-ELE-LST-0006", "interface register", "IFR"),
    ("PLP-ELE-CAL-0008", "auxiliary sizing and DC autonomy", "IFR"),
    ("PLP-ELE-REP-0007", "plant-to-grid boundary report", "IFR"),
    ("PLP-ELE-REG-0001", "open items of the one-line", "live"),
]


def register_list() -> None:
    lines = ["electrical documents of the design stage (register extract):",
             "  number             title                                       status"]
    lines += [f"  {n:18s} {t:43s} {s}" for n, t, s in REGISTER]
    lines += [f"  {len(REGISTER)} entries; at this design stage nothing is IFC yet - the",
              "  32-entry register of lesson C is a later stage; an entry is",
              "  the only way a drawing exists for the project: it gives the",
              "  number, the revision, the status and who holds the latest",
              "  copy; the open-items register stays 'live' until the last",
              "  item is closed"]
    emit("s_register", lines)


if __name__ == "__main__":
    full_schedule()
    bess_trace()
    register_list()
