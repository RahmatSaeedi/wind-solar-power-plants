"""Chapter 20, section C - design of the control system as records that
can be checked: a service register (each service mapped to its enabling
conditions, controller mode, resource and measured acceptance
criterion), conflicts between services found from shared resources, the
mode state machine with coverage tests (a planted defect is found), and
settings under configuration control (a fingerprint of the as-designed
settings compared with the as-left ones).

Run from the project root:   python -m companion.ch20.lab_c
Writes companion/ch20/expected/c_*.txt.
Teaching records; no grid-code value is quoted (A-299, A-300).
"""
from __future__ import annotations

import hashlib
import itertools
import json

from companion.ch20 import sources as src
from companion.ch20.common import emit

# [start: register]
# service: (status, mode, resources, acceptance criterion, evidence)
SERVICES = {
    "export limit": ("baseline", "P-LIMIT", {"re_down"},
                     "export <= cap + band", "sim + SAT + monitor"),
    "ramp limit": ("conditional", "P-RAMP", {"re_down", "bess_p"},
                   "1-min change <= limit", "sim + SAT + monitor"),
    "frequency response": ("conditional", "P-F DROOP",
                           {"re_down", "bess_p", "bess_e"},
                           "dP/df on droop line +- tol",
                           "sim + test + monitor"),
    "voltage / Q control": ("baseline", "Q-V", {"q_cap"},
                            "Q on the set curve +- tol",
                            "sim + SAT + monitor"),
    "upward reserve REQ-S01": ("conditional", "RESERVE", {"bess_p", "bess_e"},
                               "held >= 95 % window h", "sim + monitor"),
    "energy shifting": ("baseline", "SCHEDULE", {"bess_p", "bess_e"},
                        "plan followed or alarm", "sim + monitor"),
    "fault ride-through": ("unit capability", "FRT (units)", {"units"},
                           "units ride through", "type test + model"),
    "grid-forming": ("not offered", "GFM", {"bess_p", "bess_e"},
                     "if permitted, studied", "study first"),
    "black start": ("not offered", "BLACK START", {"bess_p", "bess_e"},
                    "only if contracted", "study first"),
}
# [end: register]


def register() -> None:
    lines = ["service register of Plant P (teaching; A-300):",
             "  service                 status           mode"]
    for k, (st, mode, _, crit, ev) in SERVICES.items():
        lines.append(f"  {k:23s} {st:16s} {mode}")
    lines += ["  each service also carries its acceptance criterion and",
              "  evidence route:",
              "  service                 criterion                   evidence"]
    for k, (_, _, _, crit, ev) in SERVICES.items():
        lines.append(f"  {k:23s} {crit:27s} {ev}")
    lines += ["  'conditional' = only where the equipment, the contract, the",
              "  grid rules and the operator permit it; evidence routes follow",
              "  the three of IEC TS 63102: test, simulation, monitoring"]
    emit("c_register", lines)


def conflicts() -> None:
    active = {k: v for k, v in SERVICES.items() if v[0] in ("baseline", "conditional")}
    lines = ["services that share a resource (must be ranked or split):",
             "  pair                                          shared"]
    n = 0
    for (a, va), (b, vb) in itertools.combinations(active.items(), 2):
        sh = va[2] & vb[2]
        if sh:
            n += 1
            lines.append(f"  {a[:20]:20s} + {b[:22]:22s} {', '.join(sorted(sh))}")
    lines += [f"  {n} conflicts; each needs a priority, a split of the",
              "  resource (e.g. 5 MW reserve, 15 MW schedule) or a rule that",
              "  one service is not offered while the other runs"]
    emit("c_conflicts", lines)


# [start: states]
STATES = ["OFF", "STANDBY", "GRID", "LIMITED", "FALLBACK", "ISLAND", "TRIPPED"]
TRANSITIONS = {
    ("OFF", "STANDBY"): "auxiliaries healthy, operator start",
    ("STANDBY", "GRID"): "grid healthy, permissions given",
    ("GRID", "LIMITED"): "operator cap or service instruction",
    ("LIMITED", "GRID"): "cap released",
    ("GRID", "FALLBACK"): "comms lost past timeout",
    ("LIMITED", "FALLBACK"): "comms lost past timeout",
    ("GRID", "ISLAND"): "grid lost, island permitted (critical loads)",
    ("ISLAND", "STANDBY"): "grid back, synchro-check passed",
    ("GRID", "TRIPPED"): "protection trip",
    ("LIMITED", "TRIPPED"): "protection trip",
    ("ISLAND", "TRIPPED"): "protection trip",
    ("TRIPPED", "OFF"): "fault cleared, operator reset",
    ("STANDBY", "OFF"): "operator stop",
}
# [end: states]


def check_machine(trans: dict) -> list[str]:
    """Every state reachable from OFF, every state has an exit, and the
    machine can get back to OFF from every state."""
    issues = []
    nxt = {s: {b for (a, b) in trans if a == s} for s in STATES}
    seen, todo = {"OFF"}, ["OFF"]
    while todo:
        for b in nxt[todo.pop()]:
            if b not in seen:
                seen.add(b)
                todo.append(b)
    issues += [f"{s} not reachable" for s in STATES if s not in seen]
    issues += [f"{s} has no exit" for s in STATES if not nxt[s]]
    for s in STATES:
        reach, todo = {s}, [s]
        while todo:
            for b in nxt[todo.pop()]:
                if b not in reach:
                    reach.add(b)
                    todo.append(b)
        if "OFF" not in reach:
            issues.append(f"no way back to OFF from {s}")
    return issues


def machine() -> None:
    lines = ["mode state machine of the plant controller:",
             f"  {len(STATES)} states, {len(TRANSITIONS)} transitions"]
    issues = check_machine(TRANSITIONS)
    lines.append("  checks on the drawn machine:")
    lines += [f"    {i}" for i in issues]
    fixed = dict(TRANSITIONS)
    fixed[("FALLBACK", "GRID")] = "comms back, plan re-read"
    fixed[("FALLBACK", "TRIPPED")] = "protection trip"
    lines.append("  after adding FALLBACK -> GRID and FALLBACK -> TRIPPED: "
                 + (", ".join(check_machine(fixed)) or "no issue"))
    lines += ["  test cases: one per transition (guard true and guard false),",
              f"  that is {2 * len(fixed)} cases; the drawing had a mode with no",
              "  way out - found by a script before any test was run"]
    emit("c_machine", lines)


# [start: settings]
def fingerprint(settings: dict) -> str:
    """SHA-256 of the settings written in one canonical form."""
    text = json.dumps(settings, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode()).hexdigest()[:12]
# [end: settings]


def settings() -> None:
    L = src.LIMITS
    designed = {"export_mw": L["export_mw"], "droop": 0.04, "deadband_hz": 0.02,
                "q_slope": 0.04, "ramp_mw_min": 10.0, "comms_timeout_s": 3600,
                "e_min_mwh": L["e_min"], "e_max_mwh": L["e_max"],
                "reserve_mw": 5.0, "fw": "2.3.1"}
    as_left = dict(designed, deadband_hz=0.2)
    diff = [k for k in designed if designed[k] != as_left[k]]
    lines = ["settings under configuration control (PLP-CTL-SPC-0001):",
             f"  as designed fingerprint {fingerprint(designed)}",
             f"  as left     fingerprint {fingerprint(as_left)}",
             f"  differing setting(s): {', '.join(diff)} "
             f"({designed[diff[0]]} -> {as_left[diff[0]]})",
             "  a deadband ten times wider makes the plant ignore most",
             "  frequency deviations; the fingerprint shows that something",
             "  changed, the comparison shows what; the as-left record is",
             "  signed at commissioning (chapters 44, 48 and 50)"]
    emit("c_settings", lines)


if __name__ == "__main__":
    register()
    conflicts()
    machine()
    settings()
