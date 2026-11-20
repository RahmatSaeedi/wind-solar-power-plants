"""Chapter 50, round v: test instruments against the tolerance they judge,
authorised persons across the shift roster, and the muster count of the
evacuation drill against the gate log.

Run from the project root:   python -m companion.ch50.examples_v
Writes companion/ch50/expected/v_*.txt.
Teaching values (A-514 to A-521).
"""
from __future__ import annotations

from companion.ch50.common import emit

# ------------------------------------------------ 1. instrument to tolerance
TUR_ROWS = [   # test, tolerance judged (+/-), instrument uncertainty (+/-), unit
    ("relay operating time at 0.86 s", 0.083, 0.010, "s"),
    ("string Voc at 1,217 V", 36.5, 6.1, "V"),
    ("reactive power at the POC", 1.0, 0.33, "Mvar"),
    ("PR from the reference pyranometer", 2.0, 1.05, "%"),
]


def tur(rule: float = 4.0) -> list:
    rows = [(t, tol, u, unit, tol / u) for t, tol, u, unit in TUR_ROWS]
    low = [r for r in rows if r[4] < rule]
    lines = ["test instruments against the tolerance each result is judged by",
             f"  (ch 40 asks for a ratio of {rule:.0f})",
             "  test                                  tolerance  uncertainty  ratio"]
    lines += [f"  {t:36s} {tol:7.3g} {unit:4s} {u:7.3g} {unit:4s}  {r:5.1f}"
              for t, tol, u, unit, r in rows]
    lines += [f"  below {rule:.0f}: {', '.join(r[0] for r in low)}",
              "  the PR test's own instrument is the weak one: the",
              "  calibration chain of ch 48 (ratio 1.4) carries into the",
              "  guarantee - which is why the lower bound of lesson B",
              "  fell just below the guarantee"]
    emit("v_tur", lines)
    return low


# ------------------------------------------------ 2. authorised persons on shifts
SHIFTS = ["A", "B", "C", "D"]
AP = {"N. Tehrani": "A", "A. Hosseini": "B", "K. Saberi": "B"}


def shifts() -> dict:
    cover = {s: [n for n, sh in AP.items() if sh == s] for s in SHIFTS}
    gaps = [s for s, n in cover.items() if not n]
    lines = [f"authorised persons (HV) assessed: {len(AP)}; shifts on the roster: "
             f"{len(SHIFTS)}"]
    lines += [f"  shift {s}: {', '.join(n) if n else 'none'}" for s, n in cover.items()]
    lines += [f"  shifts without an authorised person: {', '.join(gaps)}",
              "  a fault on those shifts waits for a call-out before any",
              "  switching: the fourth person of lesson C is needed for",
              "  the roster, and shift B's second could move to C or D"]
    emit("v_shifts", lines)
    return dict(gaps=gaps)


# ------------------------------------------------ 3. muster count
def muster(gate_in: int = 62, mustered: int = 60, visitors_unlogged: int = 2,
           left_unlogged: int = 4) -> dict:
    expected = gate_in
    missing = expected - mustered
    true_inside = gate_in - left_unlogged + visitors_unlogged
    explained = true_inside - mustered
    lines = ["evacuation drill: muster count against the gate log",
             f"  inside by the gate log {expected}; mustered {mustered}; "
             f"unaccounted {missing}",
             f"  found afterwards: {left_unlogged} had left without badging out and",
             f"  {visitors_unlogged} visitors had come in with a group, never logged",
             f"  really inside {true_inside}; still missing {explained} - nobody, but",
             "  the count took 25 minutes to prove it; in a real event",
             "  rescuers would have searched for people who were not there",
             "  (ch 49 gate and induction)"]
    emit("v_muster", lines)
    return dict(missing=missing, true=true_inside, still=explained)


if __name__ == "__main__":
    tur()
    shifts()
    muster()
