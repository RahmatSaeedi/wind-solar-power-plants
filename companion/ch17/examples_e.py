"""Chapter 17, section E - the connection boundary: the responsibility
matrix of the assets between the plant and the grid, where the meter
sits and who carries the line losses, and three patterns of connection
cost (teaching money values A-285; the rules are national, chapters 55-57).

Run from the project root:   python -m companion.ch17.examples_e
Writes companion/ch17/expected/e_*.txt.
"""
from __future__ import annotations

from collections import Counter

import numpy as np

from companion.ch15 import sources as s15
from companion.ch17 import sources as src
from companion.ch17.common import emit

ACTS = ("design", "permit", "pay", "own", "operate", "accept")

# [start: matrix]
# P project, U utility / grid operator, S shared, ? open (A-285)
MATRIX = {
    "PV array, inverters":        "P P P P P P",
    "wind turbines":              "P P P P P P",
    "33 kV collector cables":     "P P P P P P",
    "site substation 33/132 kV":  "P P P P P S",
    "132 kV export line 7.06 km": "P P ? ? ? S",
    "line corridor and easement": "P P P ? ? U",
    "bay at the grid substation": "S U ? U U U",
    "revenue metering":           "S U P ? U U",
    "protection interface":       "S S P S S U",
    "telemetry and dispatch":     "S U P S S U",
    "grid substation, network":   "U U U U U U",
}
# [end: matrix]


def matrix() -> None:
    cells = {a: row.split() for a, row in MATRIX.items()}
    c = Counter(x for row in cells.values() for x in row)
    open_ = [(a, ACTS[i]) for a, row in cells.items() for i, x in enumerate(row) if x == "?"]
    lines = [f"responsibility matrix: {len(cells)} assets x {len(ACTS)} activities"
             f" = {len(cells) * len(ACTS)} cells",
             f"  project {c['P']}, utility {c['U']}, shared {c['S']}, open {c['?']}",
             "  open cells:"]
    for a, act in open_:
        lines.append(f"    {a:28s} {act}")
    lines += ["  the export line and its corridor hold five of the seven open",
              "  cells: who owns, pays and runs them decides where the POC",
              "  really is; shared cells need an interface document with",
              "  named owners"]
    emit("e_matrix", lines)


def meter_losses() -> None:
    """Line losses of the 7.06 km line, unity power factor, by hour of the
    plant's export (model 15.1)."""
    n = src.NETWORK
    r_ohm = n["r_ohm_km"] * n["line_km"]
    p = np.clip(s15.plant_year()["net"], 0, None)
    loss = r_ohm * (p / n["v_kv"]) ** 2                 # MW
    lines = ["where the meter sits decides who carries the line losses:",
             f"  line R {r_ohm:.3f} ohm; loss at 100 MW {r_ohm * (100 / n['v_kv']) ** 2:.3f} MW",
             f"  yearly loss {loss.sum():,.0f} MWh = {100 * loss.sum() / p.sum():.2f} % of"
             f" {p.sum() / 1e3:.1f} GWh",
             "  meter at the site substation: the buyer receives less than is",
             "  metered (or the contract corrects for it); meter at the grid",
             "  bay: the project carries the loss; either way, the contract",
             "  and the model (chapter 15 boundary) must use the same point"]
    emit("e_meter", lines)


def costs() -> None:
    """Teaching connection costs (A-285), million u: line 0.45 per km,
    bay 1.8, site substation 9.5, upstream transformer replacement 14.0
    of which Plant P would take a share by capacity (100 of 160 MW)."""
    line = 0.45 * src.NETWORK["line_km"]
    bay, sub, up = 1.8, 9.5, 14.0
    share = 100 / 160
    pats = {"assets to the plant side of the bay": sub + line,
            "plus the bay (shallow)": sub + line + bay,
            "plus a share of the reinforcement (deep)": sub + line + bay + share * up}
    lines = ["three patterns of connection cost (teaching values, million u):",
             f"  line {line:.2f}, bay {bay:.2f}, site substation {sub:.2f},"
             f" upstream {up:.2f} (share {share:.3f})"]
    for k, v in pats.items():
        lines.append(f"  {k:44s} {v:6.2f}  ({1000 * v / 110:5.0f} k u per MW)")
    lines += ["  the pattern is set by national rules and the connection offer,",
              "  not by the engineer; the requirement register records which",
              "  pattern applies and the boundary follows from it"]
    emit("e_costs", lines)


if __name__ == "__main__":
    matrix()
    meter_losses()
    costs()
