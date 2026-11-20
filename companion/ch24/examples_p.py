"""Chapter 24 - cable manufacture in numbers: concentric stranding (wires
per layer, diameter and compaction), insulation thickness and
eccentricity from a cut sample with a process-capability index, the drum
weight that limits the joints, and the cable test families named by their
purpose. No process recipes: the makers' processes stay theirs.

Run from the project root:   python -m companion.ch24.examples_p
Writes companion/ch24/expected/p_*.txt. Teaching values (A-321
extended).
"""
from __future__ import annotations

import math
import statistics

from companion.ch24.common import emit


def stranding() -> None:
    lines = ["concentric stranding: 1 + 6 + 12 + 18 + ... wires",
             "  layers  wires  wire mm   area mm2   round dia mm   compacted mm"]
    for layers, d_w in ((3, 3.25), (4, 3.45), (5, 3.60)):
        n = 1 + sum(6 * k for k in range(1, layers))
        area = n * math.pi * d_w ** 2 / 4
        d_round = (2 * layers - 1) * d_w
        d_comp = math.sqrt(4 * area / math.pi / 0.92)
        lines.append(f"  {layers:6d}  {n:5d}  {d_w:7.2f}   {area:8.0f}   {d_round:12.1f}"
                     f"   {d_comp:12.1f}")
    lines += ["  each layer adds six wires; a round strand fills about 75 %",
              "  of its circle, a compacted one about 92 %: a smaller",
              "  conductor diameter means less insulation volume, a smoother",
              "  screen and less stress - the conductor's resistance, not",
              "  its nominal area, is what the routine test checks"]
    emit("p_strand", lines)


# [start: eccentricity]
def insulation_check(t_meas: list, t_nom: float,
                     t_min_pct: float = 0.90) -> dict:
    """Thickness checks of one insulation cut: average, minimum against a
    fraction of nominal, and eccentricity (max - min) / max."""
    t_max, t_min = max(t_meas), min(t_meas)
    return {"avg": statistics.mean(t_meas),
            "min_ok": t_min >= t_min_pct * t_nom,
            "ecc": (t_max - t_min) / t_max}


def cpk(values: list, lsl: float, usl: float) -> float:
    """Process capability: distance of the mean to the nearer limit in
    units of three standard deviations."""
    m, s = statistics.mean(values), statistics.stdev(values)
    return min(usl - m, m - lsl) / (3 * s)
# [end: eccentricity]


def eccentricity() -> None:
    cuts = {"drum 1": [8.4, 8.2, 8.1, 8.0, 8.1, 8.3],
            "drum 2": [8.9, 8.6, 8.0, 7.6, 7.9, 8.5],
            "drum 3": [8.1, 8.2, 8.2, 8.1, 8.0, 8.1]}
    lines = ["insulation thickness of 33 kV cores (nominal 8.0 mm, teaching limits:",
             "  minimum >= 90 % of nominal, eccentricity <= 10 %)",
             "  sample   average mm   minimum ok   eccentricity   result"]
    for name, t in cuts.items():
        r = insulation_check(t, 8.0)
        ok = r["min_ok"] and r["ecc"] <= 0.10
        lines.append(f"  {name:7s}  {r['avg']:10.2f}   {'yes' if r['min_ok'] else 'NO':10s}"
                     f"   {r['ecc']:12.1%}   {'pass' if ok else 'FAIL'}")
    means = [8.10, 8.32, 7.95, 8.25, 8.05, 8.40, 7.90, 8.20, 8.15, 8.30]
    c = cpk(means, 7.6, 8.8)
    lines += ["  drum 2 has enough average but the core sits off-centre: the",
              "  thin side sets the electrical stress, the thick side wastes",
              "  material - the extrusion line's centring is the cause",
              f"  ten drums' average thickness: Cpk {c:.2f} against 7.6-8.8 mm",
              f"  (a capable process keeps Cpk above about 1.33: this line is"
              f" {'capable' if c >= 1.33 else 'NOT capable'} -",
              "  less spread or better centring before the next lot; the",
              "  limits here are teaching values, the real ones are the",
              "  cable standard's and the contract's)"]
    emit("p_eccentricity", lines)


def drums() -> None:
    kg_m, drum_t, limit_t = 9.2, 2.0, 15.0
    lines = ["drum weight against the joints of a 4.4 km string (630 mm2, 9.2 kg/m):",
             "  drum m   cable t   gross t   transport   joints per string"]
    for m in (500, 750, 1100, 1500):
        gross = kg_m * m / 1e3 + drum_t
        joints = 4 * (math.ceil(1100 / m) - 1)       # per 1.1 km section
        lines.append(f"  {m:6d}   {kg_m * m / 1e3:7.1f}   {gross:7.1f}   "
                     f"{'ok' if gross <= limit_t else 'special':9s}   {max(joints, 0):17d}")
    lines += [f"  (teaching road limit {limit_t:.0f} t on the trailer; joints at the",
              "  turbines' switchgear are terminations, not joints)",
              "  1,100 m drums put every joint inside a turbine and stay",
              "  under the road limit; 1,500 m drums need special transport",
              "  for no fewer joints and leave 400 m off-cuts - the section",
              "  length decides (lesson B, ch 46)"]
    emit("p_drums", lines)


def tests() -> None:
    fam = [("routine (every length)", "conductor resistance, voltage test, partial discharge",
            "each drum's test report"),
           ("sample (some lengths)", "dimensions, eccentricity, hot set, conductor",
            "sample test report per lot"),
           ("type (once per design)", "electrical and thermal cycling, ageing, bending",
            "type-test certificate"),
           ("after laying (site)", "sheath integrity, insulation test, VLF or AC test",
            "site test record per section")]
    lines = ["cable test families and what each proves (names and records only):"]
    for a, b, c in fam:
        lines += [f"  {a}:", f"    {b}", f"    record: {c}"]
    lines += ["  the factory proves the cable was made right; the site test",
              "  proves it survived transport, pulling and jointing - neither",
              "  replaces the other; methods, voltages and durations are",
              "  the standard's and the maker's, done by trained staff"]
    emit("p_tests", lines)


if __name__ == "__main__":
    stranding()
    eccentricity()
    drums()
    tests()
