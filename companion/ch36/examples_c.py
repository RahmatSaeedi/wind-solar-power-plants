"""Chapter 36, lesson C (resilience and response): the asset inventory and
its gaps, recovery time of each system against its target, how often to
test a restore, the patch exposure window, changes with their backups,
the incident timeline of a tabletop, continuity without SCADA, and end
of support over the plant's life.

Run from the project root:   python -m companion.ch36.examples_c
Writes companion/ch36/expected/c_*.txt.
Synthetic data and teaching values (A-404, A-405, A-408); defensive only.
"""
from __future__ import annotations

from companion.ch36 import sources as src
from companion.ch36.common import emit
from plantp import ot_security as ot


def inventory() -> None:
    req = ("owner", "firmware", "support_end")
    gaps = ot.inventory_gaps(src.INVENTORY, req)
    lines = ["the asset inventory checked for gaps (synthetic extract of 10)",
             "  field          rows missing it"]
    for f, n in gaps.items():
        lines.append(f"  {f:14s} {n:5d}")
    rows = [it["tag"] for it in src.INVENTORY if any(not it.get(f) for f in req)]
    soon = [it["tag"] for it in src.INVENTORY if it.get("support_end") and it["support_end"] <= 2028]
    lines += [f"  rows with a gap: {', '.join(rows)}",
              f"  support ends by 2028: {', '.join(soon)}",
              "  an inventory without an owner has nobody to patch it, one",
              "  without a firmware version cannot be checked against a",
              "  maker's notice, and one without an end of support date",
              "  hides the next replacement; the inventory is the first",
              "  control, because every other one needs it"]
    emit("c_inventory", lines)


def recovery() -> None:
    lines = ["recovery time of each system against its target (teaching steps, h)",
             "  system                      steps h   target h   meets?"]
    miss = []
    for name, steps in src.RECOVERY.items():
        target = steps["target"]
        t = ot.recovery_time_h({k: v for k, v in steps.items() if k != "target"})
        if t > target:
            miss.append(name)
        lines.append(f"  {name:27s} {t:7.1f}   {target:8.1f}   {'yes' if t <= target else 'NO'}")
    his = ot.recovery_time_h({k: v for k, v in src.RECOVERY["historian"].items()
                              if k != "target"})
    lines += [f"  misses: {', '.join(miss)} - by minutes; a configured spare on the",
              "    shelf removes the gap",
              f"  the historian meets its target only just ({his:.0f} of"
              f" {src.RECOVERY['historian']['target']:.0f} h):",
              "    12 h of it is restoring data; a standby copy in the DMZ",
              "    (ch 35) would shorten it",
              "  recovery times are measured in a restore test, not only",
              "  added up on paper"]
    emit("c_recovery", lines)


def restore_tests() -> None:
    p_bad = 0.02                          # chance a month that a backup silently breaks
    lines = ["how often to test a restore (teaching: 2 % a month a backup breaks silently)",
             "  test every   chance the latest backup is broken when needed"]
    for months in (1, 3, 12, 36):
        # broken at some point since the last good test; mean over the interval
        mean_age = (months + 1) / 2
        p = 1 - (1 - p_bad) ** mean_age
        lines.append(f"  {months:4d} months   {p * 100:10.1f} %")
    lines += ["  a backup that was never restored is a hope, not a",
              "  control; a quarterly restore on a test bench keeps the",
              "  chance of finding a broken one in an emergency small,",
              "  and each test is recorded with its time (lesson C)"]
    emit("c_restore", lines)


def patches() -> None:
    lines = ["days from a maker's fix to its installation (teaching)",
             "  test days   window every   mean days   worst days"]
    for test, window in ((14, 30), (14, 90), (14, 365)):
        mean, worst = ot.patch_exposure_days(test, window)
        lines.append(f"  {test:9d}   {window:8d} d     {mean:9.0f}   {worst:10.0f}")
    lines += ["  plant devices are patched in outage windows after a test",
              "  on the test bench; a long gap is covered by compensating",
              "  controls (the conduit closed, the service switched off)",
              "  and recorded with the risk it leaves - never by patching",
              "  a running controller on the day the fix appears"]
    emit("c_patch", lines)


def changes() -> None:
    per_year, backup_min, test_h = 60, 15, 1.5
    lines = ["changes to the control system in a year (teaching)",
             f"  {per_year} changes, each with a backup before and after"
             f" ({2 * backup_min} min)",
             f"  and a test ({test_h} h): {per_year * (2 * backup_min / 60 + test_h):.0f} h of work",
             "  each change: request, risk check, approval, backup,",
             "  change, test, fingerprint compared, backup, record. An",
             "  emergency change follows the same record afterwards; a",
             "  change outside this path is itself an incident"]
    emit("c_change", lines)


TIMELINE = [  # minute, event (synthetic tabletop scenario, defensive)
    (0, "operator sees an unknown login on an HMI"),
    (5, "OT lead called; physical security checks the control room"),
    (15, "the HMI is isolated from the network; the plant runs on the PPC"),
    (30, "logs collected and kept; the account disabled"),
    (60, "grid operator informed of the reduced view, as agreed"),
    (120, "HMI rebuilt from the tested image; fingerprint compared"),
    (180, "HMI back in service; review of the cause starts")]


def tabletop() -> None:
    lines = ["tabletop exercise: an unknown login on an HMI (synthetic)",
             "  minute   step"]
    for m, e in TIMELINE:
        lines.append(f"  {m:6d}   {e}")
    lines += ["  safety first, then keep the plant running, then the",
              "  evidence: the HMI is isolated, the plant is not stopped,",
              "  because protection and the PPC do not need the HMI. The",
              "  exercise tests the call list, the decisions and the",
              "  records - nothing is done to a real system"]
    emit("c_tabletop", lines)


def continuity() -> None:
    lines = ["the plant without SCADA for a day (teaching)",
             "  protection: unaffected, local in every relay",
             "  plant controller: runs; holds the last limits, then the",
             "    fallback of ch 20 after the comms hold",
             "  operators: two on site in shifts, local panels, a",
             "    logbook every 30 min; the grid operator informed",
             "  data: buffered in the devices (ch 35), back-filled after",
             "  a continuity plan says who goes where, with which keys",
             "  and procedures, and is rehearsed - not invented on the day"]
    emit("c_continuity", lines)


def end_of_support() -> None:
    life = 25
    rows = [("firewalls", 2, 8), ("switches", 34, 10), ("servers", 3, 6),
            ("plant controllers", 2, 12), ("protection relays", 30, 15)]
    lines = ["replacements forced by end of support over 25 years (teaching)",
             "  device              count   support years   replacements each"]
    total = 0
    for name, n, yrs in rows:
        k = -(-life // yrs) - 1
        total += n * k
        lines.append(f"  {name:19s} {n:5d}   {yrs:13d}   {k:16d}")
    lines += [f"  {total} device replacements in the plant's life",
              "  the end of a maker's support is a date in the inventory,",
              "  planned like a gearbox exchange: budget, spare, test",
              "  bench, outage window - not a surprise in year 9"]
    emit("c_eos", lines)


if __name__ == "__main__":
    inventory()
    recovery()
    restore_tests()
    patches()
    changes()
    tabletop()
    continuity()
    end_of_support()
