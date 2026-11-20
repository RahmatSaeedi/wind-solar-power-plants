"""Chapter 47, round y: concrete specimens traced to their truck, a tower
section's internals against its list, a hold closed by a re-test, and
NCRs whose closure lacks its evidence.

Run from the project root:   python -m companion.ch47.examples_y
Writes companion/ch47/expected/y_*.txt.
Teaching values (A-494 to A-496).
"""
from __future__ import annotations

from companion.ch47 import sources as src
from companion.ch47.common import emit

# ------------------------------------------------ 1. specimens to trucks
SPECIMENS = {   # pour F04: specimen -> truck (None = not written)
    "F04-1": 21, "F04-2": None, "F04-3": 24,
}


def custody() -> dict:
    lost = [s for s, t in SPECIMENS.items() if t is None]
    low = "F04-2"
    lines = ["pour F04: each specimen against the truck it was taken from",
             "  " + ", ".join(f"{s} <- {'truck ' + str(t) if t else '?'}"
                              for s, t in SPECIMENS.items()),
             f"  the low result (30.2 MPa) is specimen {low}, whose truck was not",
             "  written: whether a truck was weak or the specimen was badly",
             "  made can no longer be told - the engineer must core the",
             "  foundation; one line on the specimen label would have pointed",
             "  to one truck's ticket (lesson B) and perhaps saved the cores"]
    emit("y_custody", lines)
    return dict(lost=lost)


# ------------------------------------------------ 2. internals of a section
INTERNALS = {   # item: (on the list, fitted in section 3)
    "platform": (1, 0), "ladder segments": (5, 5), "fall-arrest rail": (5, 5),
    "cable clamps": (24, 24), "lighting": (6, 6), "platform hatch": (1, 0),
}


def internals() -> dict:
    miss = {k: a - b for k, (a, b) in INTERNALS.items() if b < a}
    lines = ["internals of tower section 3 against its list"]
    lines += [f"  missing: {k} ({n})" for k, n in miss.items()]
    lines += ["  the 6 % mass gap of round t is the platform and its hatch;",
              "  the dossier said 'complete' because the list was signed at",
              "  the coating step - the internals list is signed after the",
              "  last item is fitted, and the weighing confirms it"]
    emit("y_internals", lines)
    return dict(miss=miss)


# ------------------------------------------------ 3. closing a hold
RETEST = dict(plate="P103", heat="H5523", temp_c=-20, values=(44, 39, 47))


def closing(order_j: float = 27.0) -> dict:
    ok = min(RETEST["values"]) >= order_j
    lines = [f"hold on {RETEST['plate']} (impact tested at 0 C): specimens of heat "
             f"{RETEST['heat']} re-tested",
             f"  at {RETEST['temp_c']} C: "
             + ", ".join(f"{v} J" for v in RETEST["values"])
             + f"; each >= {order_j:.0f} J: {'yes' if ok else 'no'}",
             f"  the hold closes on this record, filed with the plate's certificate",
             "  and NCR-205; the structural engineer's acceptance is the last",
             "  line - but the same heat's lamination of round s is a",
             "  separate finding and keeps its own NCR open"]
    emit("y_closing", lines)
    return dict(ok=ok)


# ------------------------------------------------ 4. NCR closure evidence
CLOSURES = {   # NCR: (decision, approver, verification record)
    "NCR-201": ("re-rolled", "QC", ""),
    "NCR-204": ("repaired to repair WPS", "welding coordinator", "UT report R-77"),
}


def closure() -> dict:
    bad = [n for n, (d, a, v) in CLOSURES.items() if not (d and a and v)]
    lines = ["closed NCRs: is the closure itself complete?",
             "  NCR       decision                 approver              verification"]
    for n, (d, a, v) in CLOSURES.items():
        lines.append(f"  {n}   {d:23s}  {a:20s}  {v or '-'}")
    lines += [f"  closed without verification: {', '.join(bad)}",
              "  a re-rolled can is closed only when its ovality is measured",
              "  again; an NCR is closed by the record that proves the fix,",
              "  not by the decision to fix it (ch 40)"]
    emit("y_closure", lines)
    return dict(bad=bad)


if __name__ == "__main__":
    custody()
    internals()
    closing()
    closure()
