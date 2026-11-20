"""Chapter 31, lesson C: receipt and preservation - the receiving
inspection of a delivery, damage reports and what they cost, laydown
area for one turbine and the substation, desiccant and storage time,
and the chain-of-custody record with its gaps.

Run from the project root:   python -m companion.ch31.examples_c
Writes companion/ch31/expected/c_*.txt. Teaching values (A-366).
"""
from __future__ import annotations

from companion.ch31 import sources as src
from companion.ch31.common import emit
from plantp import logistics as lg


def receiving() -> None:
    checks = [("shock and tilt indicators read", "nacelle, transformer"),
              ("packing intact, seals and desiccant bags", "all packed items"),
              ("visible damage photographed before unloading", "all loads"),
              ("blade leading edge and tip protection", "blades"),
              ("transformer impact recorder downloaded", "main transformer (ch 25)"),
              ("serial numbers against the packing list", "all loads"),
              ("documents: certificates, preservation log", "all loads")]
    lines = ["receiving inspection: what is checked before the driver leaves"]
    for what, on in checks:
        lines.append(f"  [ ] {what:46s} {on}")
    lines += ["  a damage noted while the driver is there is a transport",
              "  claim; found a week later it is the project's problem - so",
              "  the inspection happens at unloading, with photographs"]
    emit("c_receiving", lines)


def damage() -> None:
    reports = [("blade leading edge chip", 4, 3.0, "repair on site by maker"),
               ("tower flange scratch, coating", 6, 0.5, "touch-up to coating spec"),
               ("nacelle cover crack", 1, 8.0, "maker's assessment"),
               ("transformer impact over limit", 1, 40.0, "maker's inspection, tests"),
               ("cable drum flange broken", 2, 1.5, "re-drum, test the cable")]
    lines = ["damage reports during the delivery campaign (synthetic)",
             "  damage                          n   k u each   action"]
    total = 0.0
    for what, n, cost, act in reports:
        total += n * cost
        lines.append(f"  {what:31s} {n:2d}   {cost:8.1f}   {act}")
    lines += [f"  total about {total:.0f} k u; the transformer's impact alarm costs",
              "  the most because nothing can be energised until the maker",
              "  has inspected and tested it (ch 25, ch 50) - the recorder",
              "  is read before the transformer leaves the trailer"]
    emit("c_damage", lines)


def laydown() -> None:
    fp = []
    for name, (m, l_, w, h, n) in src.COMPONENTS.items():
        if n:
            fp += [l_ * w] * n
    turbine = lg.laydown_area(fp)
    sub = lg.laydown_area([8 * 3.6, 6 * 2.5 * 4, 12 * 2.4 * 6, 20 * 3])
    lines = ["laydown areas (footprints x 1.6 for aisles and handling, teaching)",
             f"  one turbine's components: {turbine:,.0f} m2 (blades dominate)",
             f"  substation equipment and drums: {sub:,.0f} m2",
             f"  four turbines staged at once plus the substation: {4 * turbine + sub:,.0f} m2",
             "  the blades' 74 m length shapes the laydown more than any",
             "  area: they lie on cradles, aligned with the crane's reach",
             "  and the wind, on ground that drains (ch 29)"]
    emit("c_laydown", lines)


def preservation() -> None:
    items = [("converter cabinet", 12.0), ("switchgear panel", 6.0), ("control cabinet", 2.0)]
    lines = ["desiccant for sealed packages (teaching rate 0.25 kg per m3 a month)",
             "  package                 volume m3   3 months kg   9 months kg"]
    for name, vol in items:
        lines.append(f"  {name:22s} {vol:9.0f}   {lg.desiccant_kg(vol, 3):11.1f}"
                     f"   {lg.desiccant_kg(vol, 9):11.1f}")
    lines += ["  storage beyond the packing's design time needs fresh",
              "  desiccant, heaters or a dry store: the maker's storage",
              "  instruction is a warranty condition, and the record of",
              "  checks (dates, humidity cards, heaters on) is the proof"]
    emit("c_preserve", lines)


def custody() -> None:
    log = [("nacelle N-07", ["port", "convoy", "site gate", "laydown", "lifted"]),
           ("transformer TR-1", ["port", "convoy", "site gate", "plinth"]),
           ("blade B-21", ["port", "convoy", "laydown"]),
           ("drum D-33 (33 kV)", ["factory", "site gate", "laydown", "trench"]),
           ("converter C-12", ["port", "site gate", "store"])]
    need = {"nacelle N-07": 5, "transformer TR-1": 5, "blade B-21": 4, "drum D-33 (33 kV)": 5,
            "converter C-12": 4}
    lines = ["chain of custody: signed hand-overs per item (synthetic log)",
             "  item                 hand-overs signed   expected   gap"]
    gaps = 0
    for item, steps in log:
        miss = need[item] - len(steps)
        gaps += miss > 0
        lines.append(f"  {item:20s} {len(steps):17d}   {need[item]:8d}   {'YES' if miss > 0 else ''}")
    lines += [f"  {gaps} items with a missing hand-over: whoever held the item",
              "  then is unknown - a damage found later cannot be placed;",
              "  every hand-over is signed by the giver and the taker"]
    emit("c_custody", lines)


if __name__ == "__main__":
    receiving()
    damage()
    laydown()
    preservation()
    custody()
