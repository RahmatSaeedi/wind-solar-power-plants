"""Chapter 50, lesson A (commissioning governance): energisation requests
against the authority register, the prerequisites of one energisation,
and the test instruments' calibration on the test day.

Run from the project root:   python -m companion.ch50.examples_a
Writes companion/ch50/expected/a_*.txt.
"""
from __future__ import annotations

from companion.ch50 import sources as src
from companion.ch50.common import emit


# [start: authority]
def authority() -> list:
    bad = []
    for boundary, _, by, permit in src.REQUESTS:
        why = []
        if by not in src.AUTHORITY.get(boundary, set()):
            why.append(f"{by} is not authorised for it")
        if permit is None:
            why.append("no sanction-for-test permit")
        if why:
            bad.append((boundary, why))
    return bad
# [end: authority]


def show_authority() -> list:
    bad = authority()
    lines = ["energisation requests against the owner's authority register"]
    for b, by_, who, permit in src.REQUESTS:
        lines.append(f"  {b:22s} authorised by {who:24s} permit {permit or 'none'}")
    lines += [f"  {b}: {'; '.join(w)}" for b, w in bad]
    lines += ["  energising is a decision with a named owner: a signature by",
              "  someone not on the register, or a test without a permit,",
              "  is stopped however ready the equipment is; the 132 kV side",
              "  is the network operator's decision alone (ch 23 boundary)"]
    emit("a_authority", lines)
    return bad


def prerequisites(boundary: str = "=PVF1-3.MV") -> list:
    missing = [k for k, v in src.PREREQ.items() if not v]
    lines = [f"prerequisites before {boundary} is energised for the first time"]
    lines += [f"  [{'x' if v else ' '}] {k}" for k, v in src.PREREQ.items()]
    lines += [f"  {len(missing)} of {len(src.PREREQ)} open: settings not read back, crews not",
              "  told, alarms not proven - each is a way for the first",
              "  energisation to surprise someone; none is waived by the",
              "  test team, only closed"]
    emit("a_prereq", lines)
    return missing


def instruments() -> dict:
    expired = [k for k, d in src.INSTRUMENTS.items() if d is not None and d < src.TODAY]
    none = [k for k, d in src.INSTRUMENTS.items() if d is None]
    lines = [f"test instruments on {src.TODAY}: calibration due date"]
    lines += [f"  {k:30s} {d or 'no record'}" for k, d in src.INSTRUMENTS.items()]
    lines += [f"  out of calibration: {', '.join(expired)}; no record: {', '.join(none)}",
              "  a result from an instrument out of calibration is a result",
              "  to repeat; the test record names the instrument for that",
              "  reason (ch 48 as-found, ch 49 torque tools)"]
    emit("a_instruments", lines)
    return dict(expired=expired, none=none)


if __name__ == "__main__":
    show_authority()
    prerequisites()
    instruments()
