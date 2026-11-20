"""Chapter 46, lesson B: switchgear product - main-circuit resistance of
every pole, close and open times and the spread between poles, and the
interlocks of a feeder bay explored as a state machine (with a planted
error that lets the earth switch close onto a closed disconnector).

Run from the project root:   python -m companion.ch46.examples_b
Writes companion/ch46/expected/b_*.txt.
Teaching values (A-485); no test procedure, no operation of live gear.
"""
from __future__ import annotations

import statistics

from companion.ch46 import sources as src
from companion.ch46.common import emit
from plantp import cablemfg as km


# ------------------------------------------------ main-circuit resistance
def contacts() -> dict:
    lines = ["main-circuit resistance of each pole (micro-ohm, teaching limits",
             "  32 for incomers and coupler, 42 for feeders)",
             "  panel    L1   L2   L3   limit   spread   verdict"]
    bad = []
    for p, poles in src.CONTACTS.items():
        lim = src.CONTACT_MAX.get(p, 42)
        sp = max(poles) - min(poles)
        ok = max(poles) <= lim and sp <= 0.2 * statistics.median(poles)
        if not ok:
            bad.append(p)
        lines.append(f"  {p:7s} {poles[0]:4d} {poles[1]:4d} {poles[2]:4d}   "
                     f"{lim:5d}   {sp:6d}   {'ok' if ok else 'CHECK'}")
    lines += [f"  to check: {', '.join(bad)} - pole L2 of PVF1 is 52 against 35",
              "  and 36: over the limit and far from its own neighbours; the",
              "  pole-to-pole comparison finds a bad joint even when the",
              "  absolute limit is generous (as for busbar joints in ch 44)"]
    emit("b_contacts", lines)
    return dict(bad=bad)


# ------------------------------------------------ pole timing
def timing() -> dict:
    lines = [f"close and open times of the breakers (ms), pole spread limit "
             f"{src.POLE_SPREAD_MAX} ms (teaching)",
             "  panel   close L1/L2/L3        spread   open L1/L2/L3        spread"]
    bad = []
    for p, (c, o) in src.TIMES.items():
        sc, so = km.pole_spread(c), km.pole_spread(o)
        if max(sc, so) > src.POLE_SPREAD_MAX:
            bad.append(p)
        lines.append(f"  {p:6s}  {c[0]:5.1f}/{c[1]:5.1f}/{c[2]:5.1f}   {sc:6.1f}"
                     f"   {o[0]:5.1f}/{o[1]:5.1f}/{o[2]:5.1f}   {so:6.1f}")
    lines += [f"  over the spread limit: {', '.join(bad)} (pole L2 closes "
              "4.6 ms late)",
              "  a late pole closes the circuit on two phases for a few",
              "  milliseconds: a mechanism adjustment the factory makes and",
              "  records before shipment, and a baseline for site and",
              "  maintenance timing later (ch 52)"]
    emit("b_timing", lines)
    return dict(bad=bad)


# ------------------------------------------------ interlocks
def interlocks() -> dict:
    names = {0: "open", 1: "closed"}
    good = km.reachable()
    bad = km.reachable(faulty=True)
    lines = ["interlocks of a feeder bay: breaker CB, disconnector DS, earth switch",
             "  ES; every state reachable from all-open by allowed operations",
             "  state (CB, DS, ES)          correct logic   faulty logic"]
    for s in km.all_states():
        tag = " <- forbidden" if s in km.FORBIDDEN else ""
        lines.append(f"  ({names[s[0]]:6s}, {names[s[1]]:6s}, {names[s[2]]:6s})"
                     f"   {'yes' if s in good else 'no ':3s}            "
                     f"{'yes' if s in bad else 'no '}{tag}")
    hit = sorted(km.FORBIDDEN & bad)
    lines += [f"  forbidden states reachable: correct {len(km.FORBIDDEN & good)}, "
              f"faulty {len(hit)}",
              "  the faulty logic lets the disconnector close while the earth",
              "  switch is closed - earthing the busbar; exploring every state",
              "  finds it without a single operation on real gear, and the",
              "  check is part of the interlock design review and the FAT"]
    emit("b_interlock", lines)
    return dict(good=len(good), bad=hit)


if __name__ == "__main__":
    contacts()
    timing()
    interlocks()
