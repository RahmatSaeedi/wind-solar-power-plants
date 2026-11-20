"""Chapter 45, round m: the safe operating envelope as layers of limits
with their margins, and cell-to-cell propagation as an energy balance
(concept only - no fire prescription, no abuse values).

Run from the project root:   python -m companion.ch45.examples_m
Writes companion/ch45/expected/m_*.txt.
Teaching values (A-477, A-479).
"""
from __future__ import annotations

from companion.ch45 import sources as src
from companion.ch45.common import emit

C = src.CELL


# ------------------------------------------------ 1. the safe operating envelope
LAYERS = [   # quantity, unit, cell data-sheet limit, BMS trip, BMS alarm, normal
    ("cell voltage, high", "V", 3.65, 3.60, 3.55, 3.45),
    ("cell voltage, low", "V", 2.50, 2.60, 2.70, 3.00),
    ("cell temperature, charging high", "C", 55.0, 52.0, 47.0, 35.0),
    ("cell temperature, charging low", "C", 0.0, 2.0, 5.0, 15.0),
    ("charge current", "C-rate", 0.50, 0.50, 0.48, 0.45),
]


def envelope() -> dict:
    lines = ["safe operating envelope of the S1 cell as layers (teaching values;",
             "  the maker's limits rule)",
             "  quantity                        unit    cell   trip  alarm  normal"
             "  margin"]
    out = {}
    for q, u, lim, trip, alarm, norm in LAYERS:
        margin = abs(lim - norm)
        zero = abs(lim - trip) < 1e-9
        out[q] = (abs(lim - trip), abs(trip - alarm), abs(alarm - norm))
        lines.append(f"  {q:31s} {u:6s} {lim:6.2f} {trip:6.2f} {alarm:6.2f} "
                     f"{norm:7.2f}  {margin:5.2f}{' !' if zero else ''}")
    lines += ["  ! the trip equals the cell's limit",
              "  each layer keeps the next one from being reached: normal",
              "  operation stays inside the alarms, alarms come before trips,",
              "  trips come before the cell's own limits - the charge-current",
              "  trip sits on the cell's limit with no margin, a design-review",
              "  question like the charging temperature of lesson B"]
    emit("m_envelope", lines)
    return out


# ------------------------------------------------ 2. propagation as energy
def propagation(cp_j_gk: float = 1.0, rise_k: float = 100.0,
                share_to_neighbours: float = 0.5) -> dict:
    """How many neighbours one cell's stored energy could heat by rise_k if
    a share of it reached them (concept; no onset values)."""
    e_cell_kj = C["q_ah"] * C["v_nom"] * 3.6                 # kJ stored
    heat_cell_kj = C["mass_kg"] * 1000 * cp_j_gk * rise_k / 1000
    n = share_to_neighbours * e_cell_kj / heat_cell_kj
    lines = [f"one S1 cell stores {e_cell_kj:,.0f} kJ (its electrical energy alone);",
             f"  heating a {C['mass_kg']} kg neighbour by {rise_k:.0f} K takes about "
             f"{heat_cell_kj:.0f} kJ",
             "  (teaching heat capacity)",
             "  if half of one cell's energy reached its neighbours, it could",
             f"  heat {n:.1f} of them that much",
             "  a cell holds several times the energy needed to heat its",
             "  neighbours a long way: propagation is stopped by design -",
             "  spacing, barriers, heat paths and venting chosen from tests",
             "  and the hazard assessment (ch 19, STD-099), not by hoping"]
    emit("m_propagation", lines)
    return dict(e=e_cell_kj, heat=heat_cell_kj, n=n)


if __name__ == "__main__":
    envelope()
    propagation()
