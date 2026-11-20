"""Chapter 24 - more lessons: the PV string's DC cable and fuse, the
meaning of an enclosure's protection code, the factory's process
controls on a cable (insulation eccentricity, conductor resistance), the
switchgear interlock logic checked by a truth table, and the main-circuit
resistance of a breaker against its type-test value.

Run from the project root:   python -m companion.ch24.examples_g
Writes companion/ch24/expected/g_*.txt. Teaching values A-321 to A-325.
"""
from __future__ import annotations

import itertools

from companion.ch24.common import emit
from plantp import cables as cb


def pv_string() -> None:
    i_mp, i_sc, v_mp = 13.0, 13.9, 1_150.0        # string at STC (teaching)
    lines = ["PV string DC cable and fuse (teaching string of 26 modules):",
             f"  Imp {i_mp} A, Isc {i_sc} A, Vmp {v_mp:.0f} V; cable out and back"]
    for mm2, length in ((4, 60), (6, 60), (6, 120), (10, 120)):
        r = cb.r_at(17.24 / mm2 * 1.0, 70)          # Cu ohm/km
        dv = i_mp * r * 2 * length / 1e3
        lines.append(f"  {mm2:3d} mm2, {length:4d} m: drop {dv:5.1f} V = {dv / v_mp:.2%},"
                     f" loss {i_mp * dv:5.0f} W")
    fuse = 1.5 * i_sc
    lines += [f"  string fuse: at least 1.5 x Isc = {fuse:.1f} A -> 25 A (teaching",
              "  rule; the module's reverse-current rating caps it from",
              "  above, the maker's data and the applicable standard set",
              "  both), DC-rated, in both poles where the earthing asks",
              "  DC isolation: a load-break DC switch at the combiner and",
              "  at the inverter input, so a section can be made dead",
              "  without opening a DC arc on an ordinary AC device"]
    emit("g_pvstring", lines)


def ip_code() -> None:
    rows = [("IP2X", "fingers kept out", "inside a locked room"),
            ("IP54", "dust-protected; splashing water", "outdoor box with a roof"),
            ("IP55", "dust-protected; water jets", "outdoor box, cleaning by hose"),
            ("IP65", "dust-tight; water jets", "combiner box in the field"),
            ("IP67", "dust-tight; temporary immersion", "box in a flood-prone pit")]
    lines = ["enclosure protection codes (first digit solids, second water):",
             "  code  meaning                          where (teaching)"]
    lines += [f"  {c:5s} {m:32s} {w}" for c, m, w in rows]
    lines += ["  the code is proved by the maker's type test; the site keeps",
              "  it by closing every entry correctly - an open gland makes",
              "  an IP65 box an IP2X one"]
    emit("g_ip", lines)


def factory() -> None:
    samples = [(8.1, 7.6), (8.3, 7.5), (8.2, 7.9), (8.6, 6.9), (8.0, 7.7)]
    lines = ["factory process control on a 33 kV cable (teaching samples):",
             "  insulation thickness max/min mm   eccentricity   (limit 15 %)"]
    for tmax, tmin in samples:
        e = (tmax - tmin) / tmax
        lines.append(f"  {tmax:5.1f} / {tmin:5.1f}                      {e:8.1%}   "
                     f"{'ok' if e <= 0.15 else 'reject'}")
    r_meas, r_max = 0.0761, 0.0778
    lines += [f"  conductor resistance at 20 C: {r_meas} ohm/km against max {r_max}"
              f" -> {'ok' if r_meas <= r_max else 'reject'}",
              "  the process controls (extrusion, curing, line speed) keep",
              "  the samples in; routine tests on every drum (voltage,",
              "  partial discharge, resistance) prove each length; type tests",
              "  prove the design once - the site test proves the laying"]
    emit("g_factory", lines)


# [start: interlock]
def allowed(breaker_closed: bool, truck_in: bool, earth_closed: bool,
            door_open: bool) -> bool:
    """Teaching interlock rules of a withdrawable MV panel: the earthing
    switch is closed only with the truck out (and so the breaker away);
    the breaker is closed only with the truck in and the earth open; the
    cable door opens only with the earth closed."""
    if earth_closed and truck_in:
        return False
    if breaker_closed and (not truck_in or earth_closed):
        return False
    if door_open and not earth_closed:
        return False
    return True
# [end: interlock]


def interlocks() -> None:
    states = list(itertools.product([False, True], repeat=4))
    ok = [s for s in states if allowed(*s)]
    unsafe = [("breaker closed, earth closed", (True, True, True, False)),
              ("door open, earth open", (False, False, False, True)),
              ("earth closed, truck in", (False, True, True, False))]
    lines = [f"interlock logic of a 33 kV panel: {len(ok)} of {len(states)} states allowed",
             "  breaker  truck in  earth  door   (allowed states)"]
    for s in ok:
        lines.append("  " + "  ".join(f"{'yes' if x else 'no':6s}" for x in s))
    lines.append("  three unsafe states the logic must refuse:")
    for name, s in unsafe:
        lines.append(f"    {name:30s} {'refused' if not allowed(*s) else 'ALLOWED'}")
    lines += ["  the interlocks are mechanical and electrical parts of the",
              "  panel, proved in the factory; the table is how a reviewer",
              "  checks that the rules leave no unsafe state reachable"]
    emit("g_interlock", lines)


def contact() -> None:
    type_test, factor = 40.0, 1.2                  # micro-ohm, limit factor
    meas = {"+H01": 41.0, "+H02": 44.5, "+H03": 52.0, "+H04": 43.8}
    lines = ["main-circuit resistance of breakers against the type-tested",
             f"value ({type_test:.0f} micro-ohm, limit {factor} x, teaching):"]
    for p, r in meas.items():
        lines.append(f"  {p}: {r:5.1f} micro-ohm -> "
                     f"{'ok' if r <= type_test * factor else 'investigate'}")
    lines += ["  a high value points to a poor contact or a loose joint,",
              "  which heats in service; the routine test sets the",
              "  baseline that site and maintenance tests are compared to"]
    emit("g_contact", lines)


if __name__ == "__main__":
    pv_string()
    ip_code()
    factory()
    interlocks()
    contact()
