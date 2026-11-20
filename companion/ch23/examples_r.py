"""Chapter 23 - three more auxiliary-design trade-offs: how the starting
method of the largest essential motor sets the standby generator, how
non-linear loads derate the station-service transformer, and how often
the plant is without AC auxiliary supply with each combination of
sources (own bus, a local distribution feeder, the diesel).

Run from the project root:   python -m companion.ch23.examples_r
Writes companion/ch23/expected/r_*.txt. Teaching values (A-317 extended:
starting ratios, harmonic spectrum, outage rates and durations).
"""
from __future__ import annotations

import math

from companion.ch23.common import emit
from plantp import auxpower as ax

GEN_SIZES = (60, 80, 100, 125, 150, 200, 250)
XD = 0.15                     # generator transient reactance (A-317)
DIP_LIMIT = 0.12              # teaching limit; the makers' limits apply


def starting() -> None:
    dol = 120.0                                   # kVA, HVAC compressor direct-on-line
    run_need = ax.next_size(80.13, 0.25, sizes=GEN_SIZES)   # f_sizing.txt
    methods = [("direct on line", 1.00), ("star-delta", 0.33), ("soft starter", 0.50),
               ("variable-speed drive", 0.30)]
    lines = ["starting method of the control-room HVAC (120 kVA direct on line)",
             f"  against the standby generator (running need: {run_need} kVA):",
             "  method                 start kVA   dip on 125   smallest gen for 12 %"]
    for name, k in methods:
        s = dol * k
        size = next(g for g in GEN_SIZES if g >= run_need and ax.start_dip(s, g, XD) <= DIP_LIMIT)
        lines.append(f"  {name:22s} {s:9.0f}   {ax.start_dip(s, 125, XD):10.1%}   {size:10d} kVA")
    lines += ["  with any reduced-current start the generator falls back to",
              "  the size its running load needs; the drive costs money and",
              "  adds harmonics (next lesson), the larger generator costs",
              "  fuel and space - a trade-off written in the design basis;",
              "  star-delta also opens the circuit for a moment, which some",
              "  compressors do not like (the maker decides)"]
    emit("r_starting", lines)


# [start: kfactor]
def k_factor(spectrum: dict) -> float:
    """K = sum (I_h / I_rms)^2 h^2 for harmonic currents in per unit of
    the fundamental."""
    rms2 = sum(v * v for v in spectrum.values())
    return sum((v * v / rms2) * h * h for h, v in spectrum.items())


def derating(k: float, p_ec: float = 0.10) -> float:
    """Teaching derating of a transformer whose eddy loss (p_ec of the
    load loss at rated current) grows with h^2."""
    return math.sqrt((1 + p_ec) / (1 + k * p_ec))
# [end: kfactor]


def harmonics() -> None:
    linear = {1: 1.0}
    mixed = {1: 1.0, 3: 0.25, 5: 0.18, 7: 0.10, 9: 0.05, 11: 0.04}
    lines = ["non-linear loads on the 250 kVA station-service transformer:",
             "  load mix                          K       usable kVA"]
    for name, sp, share in (("linear only", linear, 0.0), ("UPS, LED, drives (35 %)", mixed, 0.35),
                            ("UPS, LED, drives (70 %)", mixed, 0.70)):
        k = 1 + share * (k_factor(sp) - 1)
        lines.append(f"  {name:32s} {k:5.2f}   {250 * derating(k):8.0f}")
    lines += ["  harmonic currents heat the windings more than their rms",
              "  value suggests (eddy losses grow with h^2): the same",
              "  transformer carries less; the triplen harmonics also add",
              "  in the neutral (lesson E, ch 27)",
              "  the 167 kVA normal demand still fits under 236 kVA - the",
              "  margin of lesson F is partly spent on harmonics"]
    emit("r_harmonics", lines)


def sources() -> None:
    line_out = (0.006 * 7.06 * 12.0 + 4.0)     # h/yr: export line faults + grid outages
    dist_out = 8.0                              # h/yr: local 11 kV feeder (third party)
    p_fail_start = 0.02
    lines = ["hours a year without AC auxiliary supply (teaching expected values):",
             f"  own 33 kV bus via the station-service transformers: {line_out:.1f} h"
             " (the plant",
             "    cannot island, so a line or grid outage takes both SSTs)",
             f"  local distribution feeder alone: {dist_out:.0f} h"]
    both = line_out * dist_out / 8760
    lines += [f"  both, independent: {both:.4f} h  (outages must overlap)",
              f"  own bus + diesel ({p_fail_start:.0%} fail to start): {line_out * p_fail_start:.2f} h"]
    lines += ["  the UPS and the DC battery bridge the minutes before the",
              "  diesel takes the load (lesson F); the second source buys",
              "  hours, not minutes - its value is in long outages: a",
              "  winter grid outage of a day leaves heaters, battery",
              "  HVAC and pumps (ch 19) on the diesel's fuel",
              "  a distribution feeder is a third-party asset with its",
              "  own meter, tariff and agreement - one more boundary"]
    emit("r_sources", lines)


if __name__ == "__main__":
    starting()
    harmonics()
    sources()
