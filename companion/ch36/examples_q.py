"""Chapter 36, fourth deeper round: engineering workstations, protocols
without authentication inside the zones, safety functions that do not
depend on the network, the expected yearly loss against the cost of
controls, a query of the software-components list, backup keys, the
follow-up of tabletop findings, and the outside parties with access.

Run from the project root:   python -m companion.ch36.examples_q
Writes companion/ch36/expected/q_*.txt.
Synthetic data and teaching values (A-401 to A-408); defensive only.
"""
from __future__ import annotations

from companion.ch36 import sources as src
from companion.ch36.common import emit


def workstations() -> None:
    rows = [("used only for engineering", "yes"),
            ("no e-mail, no web browsing", "yes"),
            ("connects only through the jump host or on the bench", "yes"),
            ("software and tools from the approved list", "yes"),
            ("kept in the control room when not in use", "yes"),
            ("backed up like a server", "yes")]
    lines = ["the engineering laptops (3, teaching rules)",
             "  rule                                                   kept"]
    for r, k in rows:
        lines.append(f"  {r:54s} {k}")
    lines += ["  the engineering laptop carries the keys to every",
              "  controller: it is treated as part of the control zone,",
              "  not as an office computer that sometimes visits it"]
    emit("q_laptops", lines)


def protocols() -> None:
    auth = {"telecontrol": "older profile: none", "turbine-data": "maker's: none",
            "inverter-data": "maker's: none", "battery-data": "maker's: none",
            "historian-copy": "authenticated", "historian-read": "authenticated",
            "remote-session": "authenticated, 2nd factor", "jump-session": "authenticated"}
    lines = ["authentication on each conduit's service (teaching labels)",
             "  conduit                     service          authentication"]
    weak = 0
    for c in src.CONDUITS:
        a = auth[c["service"]]
        weak += a.endswith("none")
        lines.append(f"  {c['src'] + ' -> ' + c['dst']:27s} {c['service']:16s} {a}")
    lines += [f"  {weak} of {len(src.CONDUITS)} conduits carry field protocols that do not",
              "  prove who is speaking: they stay inside their zone and its",
              "  conduit, behind a gateway; secure profiles (STD-163) are",
              "  asked for in new purchases and enabled where devices",
              "  support them - never assumed"]
    emit("q_protocols", lines)


def safety_independence() -> None:
    rows = [("protection trips", "relays, hard-wired to breakers", "no"),
            ("emergency stop of a turbine", "hard-wired safety chain", "no"),
            ("fire alarm and its actions", "fire panel (ch 32, 35)", "no"),
            ("battery shut-down on fault", "BMS and its own contactors", "no"),
            ("overspeed of a rotor", "turbine safety system", "no"),
            ("plant set points", "PPC over the network", "yes")]
    lines = ["which functions depend on the network (teaching)",
             "  function                         done by                          network?"]
    for f, b, n in rows:
        lines.append(f"  {f:32s} {b:32s} {n}")
    lines += ["  every function that keeps people and equipment safe works",
              "  without the network; only optimisation and sight do not.",
              "  This independence, designed in chapters 26, 32 and 34, is",
              "  the strongest security control of the plant"]
    emit("q_safety", lines)


def expected_loss() -> None:
    rows = [("open vendor path misused", 200_000, 0.10, 15_000, 0.02),
            ("backup fails when needed", 150_000, 0.05, 8_000, 0.01),
            ("test rule left open", 100_000, 0.08, 2_000, 0.02)]
    lines = ["expected yearly loss before and after a control (teaching, u)",
             "  scenario                    before   after   saved   control  worth?"]
    worth = []
    for s, sle, aro, cost, aro2 in rows:
        before, after = sle * aro, sle * aro2
        ok = before - after > cost
        worth.append(ok)
        lines.append(f"  {s:26s} {before:7,.0f}  {after:6,.0f}  {before - after:6,.0f}"
                     f"  {cost:7,d}  {'yes' if ok else 'no'}")
    lines += ["  expected loss = loss of one event x its chance a year; on",
              f"  this sum alone {sum(worth)} of 3 controls pay for themselves - the",
              "  backup test does not, yet it is kept: it also shortens",
              "  every recovery and is the only proof a backup works. The",
              "  chances are teaching guesses: the sum guides, it does not",
              "  decide on its own"]
    emit("q_ale", lines)


SBOM = [  # device kind, count, components (synthetic)
    ("ring switch", 14, ["os-kernel 5.4", "web-ui 2.1", "ssh 8.2"]),
    ("substation switch", 6, ["os-kernel 5.4", "web-ui 2.1"]),
    ("gateway", 1, ["os-kernel 4.19", "telecontrol-lib 3.0"]),
    ("HMI", 6, ["desktop-os 10", "hmi-app 7.2"]),
    ("historian", 1, ["server-os 2019", "db-engine 14"])]


def sbom_query() -> None:
    notice = "web-ui 2.1"
    hit = [(k, n) for k, n, comps in SBOM if notice in comps]
    lines = [f"a maker's notice about '{notice}': which devices are affected?",
             "  device kind          count"]
    for k, n in hit:
        lines.append(f"  {k:20s} {n:5d}")
    lines += [f"  {sum(n for _, n in hit)} devices of {sum(n for _, n, _ in SBOM)}, answered from the list in",
              "  minutes; without a software-components list from each",
              "  maker the same question takes days of asking. The",
              "  compensating control for these: the web interface off on",
              "  every switch until the fix is installed (lesson C)"]
    emit("q_sbom", lines)


def backup_keys() -> None:
    lines = ["encrypted backups and their keys (teaching)",
             "  backups are encrypted, so a lost copy reveals nothing;",
             "  the key is kept apart from the backups, in the vault, with",
             "  a second sealed copy in the owner's safe",
             "  a restore test therefore includes fetching the key: in",
             "  the synthetic year 1 of 4 tests found the key holder",
             "  absent - the second copy and a named deputy closed it",
             "  a backup without its key is no backup"]
    emit("q_keys", lines)


def exercise_follow_up() -> None:
    rows = [("call list with an old number", "OT lead", 7, True),
            ("HMI image older than the last patch", "control engineer", 30, True),
            ("grid operator contact not in the plan", "asset owner", 14, True),
            ("no spare HMI on site", "control engineer", 90, False)]
    closed = sum(r[3] for r in rows)
    lines = ["findings of the yearly tabletop and their follow-up (synthetic)",
             "  finding                                  owner             days  closed"]
    for f, o, d, c in rows:
        lines.append(f"  {f:40s} {o:17s} {d:4d}  {'yes' if c else 'NO'}")
    lines += [f"  {closed} of {len(rows)} closed by their date; the open one is in the",
              "  findings record of lesson D with a new date",
              "  an exercise is worth its findings only if they are closed"]
    emit("q_followup", lines)


def third_parties() -> None:
    rows = [("turbine maker", "remote sessions", "contract clauses, quarterly review"),
            ("inverter maker", "data transfers", "transfer register, expiry"),
            ("integrator", "design, commissioning", "sanitised model, NDA"),
            ("grid operator", "telecontrol", "agreed profile (U-115)"),
            ("insurer", "summaries", "transfer register")]
    lines = ["outside parties with any access to the control system (teaching)",
             "  party            access                  controlled by"]
    for p, a, c in rows:
        lines.append(f"  {p:16s} {a:23s} {c}")
    lines += [f"  {len(rows)} parties, each with a contract, an owner on the plant",
              "  side and an end date for every right it holds"]
    emit("q_parties", lines)


if __name__ == "__main__":
    workstations()
    protocols()
    safety_independence()
    expected_loss()
    sbom_query()
    backup_keys()
    exercise_follow_up()
    third_parties()
