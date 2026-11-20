"""Chapter 46, lesson C: protection and control panels - a point-to-point
check of one panel's wiring against its wiring list, terminal-plan
consistency, relay setting fingerprints against the released register,
and which test - type, routine or site - proves what.

Run from the project root:   python -m companion.ch46.examples_c
Writes companion/ch46/expected/c_*.txt.
Teaching values (A-486, A-487); no test values, no live work.
"""
from __future__ import annotations

from companion.ch46 import sources as src
from companion.ch46.common import emit
from plantp import cablemfg as km
from plantp import convmfg as cm


# ------------------------------------------------ point to point
def p2p() -> dict:
    design = {frozenset(c) for c in src.WIRING_DESIGN}
    meas = {frozenset(c) for c in src.WIRING_MEASURED}
    r = km.point_to_point(design, meas)
    lines = [f"panel WS1, point-to-point check: {len(design)} designed "
             f"connections, {len(meas)} found",
             "  missing: " + "; ".join(f"{a}-{b}" for a, b in r["missing"]),
             "  extra:   " + "; ".join(f"{a}-{b}" for a, b in r["extra"]),
             "  the two trip-coil wires are crossed (each missing where it",
             "  belongs and found where it does not), one CT wire is absent",
             "  and a link joins two auxiliary contacts - a crossed trip coil",
             "  still trips the breaker, so only the wiring check finds it,",
             "  not a functional test of the trip"]
    emit("c_p2p", lines)
    return r


# ------------------------------------------------ terminal plan
WIRES = [("101", "X1:1", "K1:A1"), ("102", "X1:2", "K1:A2"), ("103", "X1:3", "F11:CT-L1"),
         ("104", "X1:3", "F11:CT-L2"), ("105", "X1:5", "F11:CT-L3"),
         ("106", "X1:6", ""), ("107", "X2:1", "F11:VT-L1")]


def terminals() -> list:
    out = km.terminal_check(WIRES)
    lines = ["terminal plan of strip X1/X2 checked from the wire list (teaching)"]
    lines += [f"  {x}" for x in out]
    lines += [f"  {len(out)} problems: two wires on one terminal where the plan has",
              "  one (X1:4 left empty), and a wire with no far end; the check",
              "  runs on the list before anyone wires - a terminal plan and a",
              "  wire list that disagree are two drawings of two panels"]
    emit("c_terminals", lines)
    return out


# ------------------------------------------------ relay fingerprints
def relays() -> dict:
    released = cm.fingerprint({"50": 1.6, "51": 0.9, "51N": 0.2, "tms": 0.15,
                               "fw": "7.3"})
    fps = src.relay_fingerprints()
    odd = {p: f for p, f in fps.items() if f != released}
    lines = ["relay settings read back at the panel FAT;",
             f"  released set {released} (ch 26 register)",
             f"  relays: {len(fps)}; differing: {', '.join(odd)}"]
    for p in odd:
        diff = {k: v for k, v in src.RELAY_SETS[p].items()
                if v != {"50": 1.6, "51": 0.9, "51N": 0.2, "tms": 0.15,
                         "fw": "7.3"}[k]}
        lines.append(f"    {p}: {', '.join(f'{k} = {v}' for k, v in diff.items())}")
    lines += ["  one relay carries a time multiplier from an earlier study, one",
              "  an older firmware: the panel builder loaded what the",
              "  register said a month earlier - the register's revision is",
              "  part of the panel's record (ch 26, ch 38)"]
    emit("c_relays", lines)
    return dict(odd=list(odd))


# ------------------------------------------------ type, routine, site
TESTS = [   # item, type test proves, routine test proves, site test proves
    ("33 kV cable", "design: insulation, ageing, fault", "each drum made right",
     "installed whole, joints, sheath"),
    ("termination", "design in its kit", "(kit parts)", "this termination made right"),
    ("switchgear", "design: rating, arc, mechanics", "each panel made right",
     "installed, connected, interlocks"),
    ("protection panel", "relay design (maker)", "wiring, functions",
     "CTs, VTs, trip paths to the gear"),
]


def which_test() -> int:
    lines = ["which test proves what, and why none replaces another",
             "  item              type test                          routine",
             "                    site"]
    for item, ty, ro, si in TESTS:
        lines.append(f"  {item:17s} {ty:34s} {ro}")
        lines.append(f"  {'':17s} {si}")
    lines += ["  a type test says the design can; a routine test says this",
              "  unit was made like the design; a site test says it was",
              "  installed and connected right - three different questions,",
              "  each answered once and kept (ch 9, ch 43)"]
    emit("c_tests", lines)
    return len(TESTS)


if __name__ == "__main__":
    p2p()
    terminals()
    relays()
    which_test()
