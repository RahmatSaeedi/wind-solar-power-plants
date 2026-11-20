"""Chapter 44, lesson C: factory build and verification - defect escape
through the board line, the interface print checked by weight, the ten
inverters' parameter sets checked by fingerprint, a module lot traced
through the genealogy, the end-of-line tests and what each covers, a
reliability demonstration that cannot be run, and parts bought outside
franchised channels.

Run from the project root:   python -m companion.ch44.examples_c
Writes companion/ch44/expected/c_*.txt.
Teaching values (A-469 to A-471); no process recipes, no live tests.
"""
from __future__ import annotations

import math

from companion.ch44 import sources as src
from companion.ch44.common import emit
from plantp import convmfg as cm


# ------------------------------------------------ board line escapes
def line(boards_a_year: int = 520) -> dict[str, float]:
    esc = cm.escapes(src.LINE["defects_ppm"], src.LINE["detect"])
    total_in = sum(src.LINE["defects_ppm"].values())
    total_out = sum(esc.values())
    lines = ["defects per million boards entering and leaving the board line",
             "  stations: paste inspection, optical, X-ray, in-circuit, functional",
             "  defect                     in ppm   escaping ppm"]
    for k, v in src.LINE["defects_ppm"].items():
        lines.append(f"  {k:26s} {v:6.0f}   {esc[k]:12.1f}")
    worst = max(esc, key=esc.get)
    lines += [f"  all: {total_in:,.0f} in, {total_out:.1f} out ({total_out / total_in:.2%} "
              "escape)",
              f"  on the plant's {boards_a_year} boards: {boards_a_year * total_out / 1e6:.2f}"
              " escaped defects expected",
              f"  {worst}s escape most here; no station is perfect and the",
              "  escape is the product of what each misses - open joints are",
              "  the worst kind to let through: they may pass today and crack",
              "  later, which is why X-ray and in-circuit test are kept"]
    emit("c_line", lines)
    return dict(out=total_out, worst=worst, per_plant=boards_a_year * total_out / 1e6)


# ------------------------------------------------ interface print by weight
def tim_weight(area_cm2: float = 266.0, um: float = 100.0, rho: float = 2.5,
               tol: float = 0.10, readings=(6.6, 6.8, 6.4, 7.9, 6.7, 5.5)):
    target = area_cm2 * um * 1e-4 * rho
    lines = [f"interface paste printed on each module baseplate ({area_cm2:.0f} cm2, "
             f"{um:.0f} um, {rho} g/cm3)",
             f"  target {target:.2f} g; tolerance +-{tol:.0%}: "
             f"{target * (1 - tol):.2f} - {target * (1 + tol):.2f} g",
             "  module   grams   verdict"]
    bad = []
    for k, g in enumerate(readings, 1):
        ok = abs(g / target - 1) <= tol
        if not ok:
            bad.append(k)
        lines.append(f"  M{k:02d}     {g:5.1f}   {'ok' if ok else 'reprint'}")
    lines += [f"  {len(bad)} of {len(readings)} reprinted: too much paste is a thick layer, too",
              "  little leaves voids (lesson B) - a scale is a cheap control",
              "  of a layer nobody can see once the module is bolted down"]
    emit("c_timweight", lines)
    return dict(target=target, bad=bad)


# ------------------------------------------------ parameter fingerprints
def fingerprints() -> dict[str, list[str]]:
    released = cm.fingerprint(src.BASE_CONFIG)
    cfg = src.configs()
    lines = [f"parameter sets read at the end-of-line test; released set "
             f"{released}",
             "  inverter   fingerprint        verdict"]
    odd = []
    for k, c in cfg.items():
        fp = cm.fingerprint(c)
        same = fp == released
        if not same:
            odd.append(k)
        lines.append(f"  {k}     {fp}   {'released' if same else 'DIFFERS'}")
    for k in odd:
        diff = [p for p in src.BASE_CONFIG if cfg[k][p] != src.BASE_CONFIG[p]]
        lines.append(f"  {k}: {', '.join(diff)} = {', '.join(str(cfg[k][p]) for p in diff)}")
    lines += ["  one inverter left the bench with island detection off, one",
              "  with an older firmware image: a fingerprint finds both in",
              "  seconds, a list of 200 parameters read by eye would not -",
              "  the released set and its fingerprint go to the site (ch 50)"]
    emit("c_fingerprint", lines)
    return dict(odd=odd)


# ------------------------------------------------ genealogy
def genealogy(lot: str = "L2212") -> dict[str, int]:
    hit = [k for k, lots in src.GENEALOGY.items() if lot in lots]
    lines = [f"module lot {lot} reported weak by the module maker: which inverters?",
             "  genealogy: inverter -> module lots (A-471)",
             f"  inverters with {lot}: {', '.join(hit)}",
             f"  {len(hit)} of {len(src.GENEALOGY)} inverters, found in one query; without",
             "  the record every inverter would be opened",
             "  the serial of each module, its lot and its position in the",
             "  stack are written at mounting - the cheapest record of all"]
    emit("c_genealogy", lines)
    return dict(n=len(hit))


# ------------------------------------------------ end-of-line tests
EOL = [   # test, what it finds, items covered (tree ids)
    ("protective earth continuity", "loose or missing bonds", ["ENC"]),
    ("insulation test", "creepage faults, damaged insulation", ["BUS", "GDB", "SWG"]),
    ("low-voltage functional test", "wiring, sensors, gate signals", ["GDB", "CTL", "SNS"]),
    ("cooling loop pressure and flow", "leaks, blocked plates", ["COO", "CLP"]),
    ("full-power run on a back-to-back bench", "losses, heat, sharing", ["MOD", "DCL", "FLT"]),
    ("firmware and parameter fingerprint", "wrong image or settings", ["CTL"]),
]


def eol() -> dict[str, int]:
    covered = {i for _, _, ids in EOL for i in ids}
    items = [r[0] for r in src.TREE if r[1] is not None and r[4] > 0]
    missing = [i for i in items if i not in covered]
    lines = ["end-of-line tests of each inverter and the product tree they"
             " cover",
             "  test                                    finds"]
    for t, finds, _ in EOL:
        lines.append(f"  {t:39s} {finds}")
    lines += ["  items of the tree not reached by any test: "
              + (", ".join(missing) or "none"),
              "  the auxiliary supplies have no test of their own: a",
              "  hold-up test would reach them (ch 34) - every item of the",
              "  tree should meet at least one test before shipment"]
    emit("c_eol", lines)
    return dict(missing=len(missing))


# ------------------------------------------------ a demonstration nobody runs
def demonstration(r_target: float = 0.90, conf: float = 0.90) -> dict[str, float]:
    n = math.ceil(math.log(1 - conf) / math.log(r_target))
    lines = [f"show R = {r_target:.0%} over a mission at {conf:.0%} confidence, zero "
             "failures:",
             f"  n = ln(1 - C) / ln(R) = {n} inverters run for the whole mission",
             "  no one tests 22 five-megawatt inverters for their life:",
             "  reliability is shown by parts (power cycling of modules,",
             "  capacitor endurance), by accelerated tests of assemblies,",
             "  and by the field record of earlier units (ch 37, ch 40)"]
    emit("c_demo", lines)
    return dict(n=n)


# ------------------------------------------------ parts outside franchised channels
def brokers(share: float = 0.05, p_bad: float = 0.02, parts: int = 3000,
            screen: float = 0.80) -> dict[str, float]:
    bad = parts * share * p_bad
    left = bad * (1 - screen)
    lines = [f"a shortage: {share:.0%} of {parts:,} purchased part lines bought from "
             "brokers (teaching)",
             f"  {p_bad:.0%} of broker lines doubtful: {bad:.1f} doubtful lines",
             f"  incoming screening finds {screen:.0%}: {left:.1f} lines left in "
             "production",
             "  a counterfeit part passes a functional test and fails in the",
             "  field: franchised sourcing is the control, screening the",
             "  backstop, and the BOM record names the channel (ch 39)"]
    emit("c_brokers", lines)
    return dict(bad=bad, left=left)


if __name__ == "__main__":
    line()
    tim_weight()
    fingerprints()
    genealogy()
    eol()
    demonstration()
    brokers()
