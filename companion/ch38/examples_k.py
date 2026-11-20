"""Chapter 38, lesson K (release to manufacture): configuration baselines,
the release-for-manufacture gate of the inverter skid, and the hazard
review of its design with the share of actions closed.

Run from the project root:   python -m companion.ch38.examples_k
Writes companion/ch38/expected/k_*.txt.
Teaching values (A-424); the makers' factory processes are in ch 40-48.
"""
from __future__ import annotations

from companion.ch38.common import emit


def baselines() -> None:
    rows = [("functional", "what the plant must do", "requirements",
             "owner"),
            ("allocated", "which part does what", "specs, ICDs",
             "design authority"),
            ("product", "how each part is built", "IFC drawings",
             "change board"),
            ("as-built", "what was built", "ASB set, assets",
             "operations")]
    lines = ["four configuration baselines of Plant P (teaching)",
             "  baseline     fixes                    held in          changed by"]
    for a, b, c, d in rows:
        lines.append(f"  {a:11s}  {b:23s}  {c:15s}  {d}")
    lines += ["  a change names the baseline it touches; a change to the",
              "  functional baseline goes back to the owner, one to the",
              "  product baseline stays with the change board"]
    emit("k_baselines", lines)


def release() -> None:
    gate = [("specification approved (APP)", True), ("ICD items all closed", False),
            ("design review comments closed", True), ("DfM/DfT review held", True),
            ("hazard review actions closed or accepted", True),
            ("inspection and test plan agreed", True), ("FAT procedure approved", False),
            ("document set at IFC and in the register", True)]
    done = sum(ok for _, ok in gate)
    lines = ["release-for-manufacture gate of the inverter skid (teaching)"]
    for item, ok in gate:
        lines.append(f"  [{'x' if ok else ' '}] {item}")
    lines += [f"  {done} of {len(gate)} met: the skid is not released; the open",
              "  ICD items (short-circuit level, heat, grid behaviour) and",
              "  the FAT procedure hold it. Releasing early buys weeks and",
              "  pays them back as factory rework (ch 40, ch 44)"]
    emit("k_release", lines)


def hazid() -> None:
    rows = [("electrical", 6, 6), ("fire", 4, 3), ("mechanical / lifting", 3, 3),
            ("thermal", 2, 1), ("access / falls", 3, 3), ("environment", 2, 2)]
    total = sum(r[1] for r in rows)
    closed = sum(r[2] for r in rows)
    lines = ["hazard review of the inverter skid design (synthetic record)",
             "  guideword              findings   actions closed"]
    for g, n, c in rows:
        lines.append(f"  {g:22s} {n:8d}   {c:14d}")
    lines += [f"  {closed} of {total} actions closed ({closed / total * 100:.0f} %);"
              " the two open ones",
              "  (fire separation, heat at the inlet) wait for the ICD",
              "  values - a hazard review is part of the design, and its",
              "  open actions are holds like any other (ch 32)"]
    emit("k_hazid", lines)


if __name__ == "__main__":
    baselines()
    release()
    hazid()
