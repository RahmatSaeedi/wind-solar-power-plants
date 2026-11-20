"""Chapter 41, a seventh round: wafer routes compared through their
lifetime spread, cell formats and what a larger cell does to the plant,
what the insulated edge of a module costs, and a gauge study of two flash
testers.

Run from the project root:   python -m companion.ch41.examples_x
Writes companion/ch41/expected/x_*.txt.
Teaching values (A-443, A-448); no process settings.
"""
from __future__ import annotations

import math
import random
from statistics import mean, pstdev

from companion.ch41.common import emit
from companion.ch41.examples_a import implied_voc
from plantp import quality as qa


# ------------------------------------------- wafer routes
ROUTES = {  # route: (median bulk lifetime s, lognormal sd) - teaching
    "pulled mono (Cz)": (1.5e-3, 0.4),
    "cast mono": (6e-4, 0.6),
    "multi (cast)": (1.5e-4, 0.8),
}


def routes(n: int = 400, seed: int = 4122) -> dict[str, tuple[float, float]]:
    rng = random.Random(seed)
    out = {}
    lines = ["wafer routes through their lifetime spread (surfaces S = 10 cm/s)",
             "  route              median tau   mean iVoc   sd iVoc   5th pct"]
    for name, (med, sd) in ROUTES.items():
        v = sorted(implied_voc(med * math.exp(rng.gauss(0, sd)), 10)[1]
                   for _ in range(n))
        out[name] = (mean(v), pstdev(v))
        lines.append(f"  {name:18s} {med * 1e6:8.0f} us   {mean(v):9.3f}   "
                     f"{pstdev(v) * 1000:5.1f} mV  {v[int(0.05 * n)]:7.3f}")
    gap = out["pulled mono (Cz)"][0] - out["multi (cast)"][0]
    lines += [f"  pulled mono leads by {gap * 1000:.0f} mV on average and its "
              "spread is narrower:",
              "  grain boundaries and impurities shorten and scatter the",
              "  lifetime of cast wafers; the cheaper route costs voltage",
              "  and a wider bin ladder - the route is chosen upstream and",
              "  shows only in the cells' data (lesson B, binning)"]
    emit("x_routes", lines)
    return out


# ------------------------------------------- cell formats
def formats() -> dict[str, dict[str, float]]:
    base_isc, base_area, base_mass = 13.98, 2.583, 28.1
    out = {}
    lines = ["cell format and what it does to the plant (half-cut, 144 cells,",
             "  current scales with cell area; teaching)",
             "  format     module Isc A   fuse 1.5 x Isc   area m2   mass kg"]
    for name, side in (("182 mm", 182.0), ("210 mm", 210.0)):
        k = (side / 182.0) ** 2
        isc = base_isc * k
        area = base_area * (0.08 + 0.92 * k)
        mass = base_mass * area / base_area
        out[name] = dict(isc=isc, area=area, mass=mass)
        lines.append(f"  {name:8s} {isc:12.2f}   {1.5 * isc:14.1f}   {area:7.2f}"
                     f"   {mass:7.1f}")
    lines += ["  a larger cell carries a third more current: string fuses,",
              "  cables and the inverter's input current change (ch 24, ch 26),",
              "  and a 37 kg module of 3.4 m2 is a two-person lift that",
              "  catches more wind on the way to the table (ch 32, lifting);",
              "  the format is a plant decision as much as a module one"]
    emit("x_formats", lines)
    return out


# ------------------------------------------- the insulated edge
def edge(l_m: float = 2.278, w_m: float = 1.134,
         cells_m2: float = 72 * 0.0330) -> dict[str, float]:
    area = l_m * w_m
    per_mm = 2 * (l_m + w_m) * 0.001
    lines = [f"module {l_m} x {w_m} m = {area:.3f} m2; cells {cells_m2:.3f} m2 "
             f"({cells_m2 / area:.1%} active)",
             f"  one more millimetre of edge all round: +{per_mm:.4f} m2 of "
             f"glass ({per_mm / area:.2%})",
             f"  module efficiency falls by the same {per_mm / area:.2%} "
             "(same cells, larger module)",
             "  the edge keeps a creepage and clearance distance between",
             "  live cells and the earthed frame: its width comes from the",
             "  safety qualification for the system voltage (IEC 61730), so",
             "  a 1500 V module needs more edge than a 1000 V one - one of",
             "  the costs of a higher string voltage"]
    emit("x_edge", lines)
    return dict(per_mm=per_mm / area, active=cells_m2 / area)


# ------------------------------------------- gauge study of two flashers
def flashers(seed: int = 4123, bias: float = 1.2, rep: float = 0.6):
    rng = random.Random(seed)
    parts = [552.4 + rng.gauss(0, 1.6) for _ in range(10)]

    def study(b):
        return [[[p + (b if f else 0.0) + rng.gauss(0, rep) for _ in range(3)]
                 for f in range(2)] for p in parts]
    before = qa.grr_anova(study(bias))
    after = qa.grr_anova(study(0.1))
    tol = 5.0
    lines = ["gauge study: 10 modules x 2 flash testers x 3 repeats (teaching)",
             "  case                       repeat W   between W   %GRR   "
             "6 sd / 5 W class",
             ]
    out = {}
    for name, g in (("as found (B reads +1.2 W)", before),
                    ("after golden-module match", after)):
        sd = math.sqrt(g["repeatability"] + g["reproducibility"])
        out[name] = dict(grr=g["grr_pct"], tol=6 * sd / tol)
        lines.append(f"  {name:26s} {math.sqrt(g['repeatability']):8.2f}   "
                     f"{math.sqrt(g['reproducibility']):9.2f}   "
                     f"{g['grr_pct']:4.0f}   {6 * sd / tol:16.0%}")
    lines += ["  the bias between testers is most of the error; matching",
              "  both to one golden module removes it, but repeatability",
              f"  alone still spans {out['after golden-module match']['tol']:.0%}"
              " of a 5 W class - flashers",
              "  sort modules into classes with some misbinning, which the",
              "  0/+5 W tolerance and the buyer's decision rule absorb"]
    emit("x_flashers", lines)
    return out


if __name__ == "__main__":
    routes()
    formats()
    edge()
    flashers()
