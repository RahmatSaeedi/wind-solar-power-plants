"""Chapter 17 - three integrated Plant P examples: sizing the auxiliary
supply from the plant's own loads (introductory), choosing the point of
connection (intermediate), and the requirements baseline (integrated).

Run from the project root:   python -m companion.ch17.integrated
Writes companion/ch17/expected/i_*.txt.
"""
from __future__ import annotations

from collections import Counter

from companion.ch17 import examples_e as ee, lab_d, sources as src
from companion.ch17.common import emit

SIZES_KVA = (400, 630, 800, 1000, 1250)                 # teaching size list


def aux_supply() -> None:
    pl = src.plant_loads_hourly()
    peak_kw = 1000 * float(sum(pl.values()).max())
    need = peak_kw * 1.25 / 0.9                          # margin, power factor (A-284)
    size = next(s for s in SIZES_KVA if s >= need)
    crit = 1000 * float(pl["critical"].max())
    lines = ["auxiliary supply from the plant's own loads (A-284):",
             f"  peak of all own loads {peak_kw:.0f} kW; x 1.25 margin / pf 0.9 ="
             f" {need:.0f} kVA",
             f"  next size in the teaching list: {size} kVA (two for redundancy)",
             f"  critical part {crit:.0f} kW: UPS and a back-up source sized on it,",
             "    not on the whole list",
             "  the margin and the redundancy are requirements with owners;",
             "  ratings come from the supplier's data with evidence (ch 25)"]
    emit("i_aux", lines)


def poc_choice() -> None:
    lines = ["choosing the point of connection (summary of sections B and E):",
             "  at the site substation 132 kV: project owns less, meter close to",
             "    the plant, line losses (754 MWh a year) carried by the buyer",
             "    or corrected in the contract; open: who owns the line",
             "  at the grid substation bay: project owns the line and pays the",
             "    bay (shallow pattern 14.48 million u), carries the losses,",
             "    operates the line or contracts it",
             "  in both: voltage rise about 0.5 %, short-circuit ratio 15:",
             "    screening passes; the operator's studies decide"]
    emit("i_poc", lines)


def baseline() -> None:
    reg = lab_d.register()
    st = Counter(r.status for r in reg)
    cells = [x for row in ee.MATRIX.values() for x in row.split()]
    lines = ["requirements baseline for D-021 (draft):",
             f"  register: {len(reg)} requirements; verified {st['verified']}, assumed"
             f" {st['assumed']}, open {st['open']}",
             f"  grid request: 12 items to the operator; boundary matrix: {cells.count('?')}"
             " open cells",
             "  the baseline is frozen only for what is verified or assumed",
             "  with a source; open items carry an owner and a date; any",
             "  change after the freeze goes through change control"]
    emit("i_baseline", lines)


if __name__ == "__main__":
    aux_supply()
    poc_choice()
    baseline()
