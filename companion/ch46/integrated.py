"""Chapter 46 - three integrated Plant P examples: one cable segment's loss
and drop by hand, the acceptance of the 33 kV cables, switchgear and
panels summarised, and the manufacturing and acceptance basis D-050.

Run from the project root:   python -m companion.ch46.integrated
Writes companion/ch46/expected/int_*.txt.
"""
from __future__ import annotations

import math

from companion.ch24 import sources as s24
from companion.ch46.common import emit
from plantp import cables as cb


# [start: hand]
def by_hand(p_mw: float = 20.0, kv: float = 33.0, pf: float = 0.95,
            mm2: int = 630, length_m: float = 850.0,
            theta: float = 70.0) -> dict:
    i = p_mw * 1e6 / (math.sqrt(3) * kv * 1e3 * pf)
    c = s24.MV_CABLES[mm2]
    r = cb.r_at(c["r20"], theta, 0.00403)                  # aluminium
    loss = 3 * i ** 2 * r * length_m / 1000 / 1000          # kW
    du = math.sqrt(3) * i * length_m / 1000 * (r * pf + c["x"] *
                                                math.sin(math.acos(pf)))
    # [end: hand]
    lines = [f"segment W001 of string WS1 by hand ({mm2} mm2 Al, {length_m:.0f} m)",
             f"  current at {p_mw:.0f} MW, {kv:.0f} kV, pf {pf}: I = P / (sqrt3 U "
             f"pf) = {i:.0f} A",
             f"  r at {theta:.0f} C = {c['r20']} x (1 + 0.00403 x 50) = {r:.4f} "
             "ohm/km",
             f"  loss = 3 I^2 r L = {loss:.1f} kW; drop = {du:.1f} V = "
             f"{du / (kv * 1e3) * 100:.3f} %",
             "  check: the same as segment W001 in lesson A, computed there",
             "  through the ch 24 helpers"]
    emit("int_hand", lines)
    return dict(i=i, r=r, loss=loss, drop=du / (kv * 1e3) * 100)


def acceptance() -> dict:
    from companion.ch46 import examples_a as ea
    from companion.ch46 import examples_b as eb
    from companion.ch46 import examples_c as ec
    from companion.ch46 import lab_d
    sc = lab_d.schedule()
    dr = ea.drums()
    cr = ea.crimps()
    ct = eb.contacts()
    tm = eb.timing()
    il = eb.interlocks()
    pp = ec.p2p()
    rl = ec.relays()
    mp = lab_d.mapping()
    rej = [d for d, (_, ok) in dr["out"].items() if not ok]
    lines = ["acceptance of the 33 kV cables, switchgear and panels, summarised",
             f"  cable schedule: {len(sc['problems'])} problems - back to the "
             "author before ordering",
             f"  drums: {', '.join(rej)} rejected after the 20 C correction",
             f"  crimps: {len(cr['bad'])} low pulls, all from tool B - re-made, "
             "tool calibrated",
             f"  switchgear: {', '.join(ct['bad'])} pole L2 resistance, "
             f"{', '.join(tm['bad'])} pole timing -",
             "    corrected at the factory",
             f"  interlocks: logic correct (0 forbidden states reached)",
             f"  panel WS1: {len(pp['missing'])} missing and {len(pp['extra'])} "
             "extra connections - rewired, rechecked",
             f"  relays: {', '.join(rl['odd'])} differ from the register - reloaded",
             f"  one-line mapping: {len(mp['gaps'])} gaps - VT drawing and the "
             "cable's site test added"]
    from companion.ch46 import examples_e as ee
    from companion.ch46 import examples_f as ef
    from companion.ch46 import examples_g as eg
    rp = ee.reports()
    th = ee.thickness()
    tt = ef.typetest()
    itf = ef.interfaces()
    ctr = ef.ct_records()
    tr = eg.trip_matrix()
    ce = [c for c, n, _ in eg.ct_earths() if n != 1]
    lines += [f"  drum reports: {len(rp)} findings; thickness: "
              f"{len(th['bad'])} drum ends fail",
              f"  type tests: {len(tt)} gaps (the 1,600 A incomer not covered)",
              f"  interfaces: {len(itf)} (connector family, cable positions)",
              f"  CTs: {', '.join(ctr['odd'])}; earths: {len(ce)} circuits wrong",
              f"  trip matrix: {len(tr)} functions with wrong trip outputs",
              "  a functional test alone would have found only the missing",
              "  CT wire; everything else passes it - the gear works, and only",
              "  the records and the checks show what is wrong"]
    emit("int_accept", lines)
    return dict(n=len(sc["problems"]), drums=rej, interlock=il["bad"])


def basis() -> None:
    lines = ["D-050 cable, switchgear and panel manufacturing and acceptance basis",
             "  1 cable schedule validated on every revision before use",
             "  2 conductor resistance by drum corrected to 20 C; sheath print",
             "    read at both ends; crimp pull tests traced to the tool",
             "  3 main-circuit resistance compared pole to pole and against",
             "    the limit; pole timing spread recorded as a baseline",
             "  4 interlock logic explored state by state at design review;",
             "    interlocks proven at FAT and site",
             "  5 every panel wired against its list point to point; terminal",
             "    plans checked against the wire list before wiring",
             "  6 relay settings fingerprinted against the register at panel",
             "    FAT and at site",
             "  7 one-line items mapped to compartment, terminal drawing and",
             "    tests; type, routine and site tests each kept",
             "  8 later findings: drum reports read line by line; both drum",
             "    ends' thickness kept; compound and kit lots recorded with",
             "    changeover points; type-test coverage checked before the",
             "    order (1,600 A incomer); maker-to-maker interfaces checked",
             "    from the cable schedule; trip matrix, CT earths and wire",
             "    markers checked from the lists; FAT design changes carried",
             "    into drawing revisions; no panel ships with an open A item",
             "  open: makers' type-test reports for the exact designs and the",
             "    panel builder's records (U-127)"]
    emit("int_basis", lines)


if __name__ == "__main__":
    by_hand()
    acceptance()
    basis()
