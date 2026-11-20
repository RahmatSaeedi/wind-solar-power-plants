"""Chapter 29, lesson R: three more ground and road lessons - a cautious
(characteristic) value from a handful of tests, the side slope of a
temporary excavation dry and with seepage, and the road wear of the
abnormal loads once chapter 31 has fixed their trailers.

Run from the project root:   python -m companion.ch29.examples_r
Writes companion/ch29/expected/r_*.txt.
Teaching values (A-349, A-353); the design values, slopes and pavement
come from the geotechnical and road engineers with the project's code.
"""
from __future__ import annotations

import math

import numpy as np
from scipy import stats

from companion.ch29 import sources as src  # noqa: F401  (puts plantp on the path)
from companion.ch29.common import emit
from plantp import logistics as lg


def characteristic() -> None:
    phi = np.array([31.0, 34.0, 29.0, 33.0, 36.0, 30.0, 32.0, 35.0])
    n, m, s = len(phi), phi.mean(), phi.std(ddof=1)
    t = stats.t.ppf(0.95, n - 1)
    mean_k = m - t * s / math.sqrt(n)
    local_k = m - t * s * math.sqrt(1 + 1 / n)
    lines = ["a cautious value of the friction angle from eight tests (T07 area)",
             f"  tests: {', '.join(f'{v:.0f}' for v in phi)} degrees",
             f"  mean {m:.1f}, standard deviation {s:.2f}, t(0.95, {n - 1}) = {t:.2f}",
             f"  cautious estimate of the MEAN (large raft, averaging): {mean_k:.1f}",
             f"  cautious estimate of a LOCAL value (pile tip, small area): {local_k:.1f}",
             f"  lowest single test: {phi.min():.0f}",
             "  a raft 24 m wide averages the ground under it, so the mean",
             "  is what matters; a pile tip sits in one spot and may meet",
             "  the weak lens - the same eight tests give two different",
             "  cautious values, and the geotechnical engineer chooses by",
             "  the mechanism, not by habit"]
    emit("r_char", lines)


def slope() -> None:
    phi = math.radians(36.0)
    g_sat, g_w = 20.0, 9.81
    lines = ["side slope of a temporary excavation in dense sand (phi 36 deg, c = 0)",
             "  slope (v:h)   angle   FS dry   FS with seepage parallel to slope"]
    for v, h in [(1, 1.0), (1, 1.5), (1, 2.0)]:
        beta = math.atan(v / h)
        fs_dry = math.tan(phi) / math.tan(beta)
        fs_wet = (g_sat - g_w) / g_sat * fs_dry
        lines.append(f"  {v}:{h:<3.1f}         {math.degrees(beta):5.1f}   {fs_dry:6.2f}"
                     f"   {fs_wet:6.2f}")
    lines += ["  seepage roughly halves the factor of safety: a 1:1.5 side",
              "  that just stands in dry sand slides when groundwater flows",
              "  out of it, and even 1:2 fails - which is why excavations",
              "  near the wadi need the water lowered first or supported",
              "  sides, and why nobody enters a trench whose side has not",
              "  been checked by a competent person (site procedure)"]
    emit("r_slope", lines)


def abnormal() -> None:
    std = 80.0

    def esal(axles):
        return sum((a / std) ** 4 for a in axles)

    def trip(pay, trailer, n):
        tr, ax = lg.axle_loads(pay, 30.0, trailer, n, tractor_axles=4, tractor_share=0.05)
        tr0, ax0 = lg.axle_loads(0.0, 30.0, trailer, n, tractor_axles=4, tractor_share=0.05)
        return esal([tr] * 4 + [ax] * n) + esal([tr0] * 4 + [ax0] * n), ax

    nac, a_nac = trip(160.0, 42.0, 16)
    base, a_base = trip(124.0, 34.0, 14)
    other = 25.04                                   # lesson M: 10 axles of 100 kN
    before = 72 * other
    after = 12 * nac + 12 * base + 48 * other
    total_m = 39_619
    lines = ["road wear of the abnormal loads with chapter 31's trailers",
             f"  nacelle: 16 axles at {a_nac:.0f} kN -> {nac:.1f} ESAL a round trip",
             f"  base section: 14 axles at {a_base:.0f} kN -> {base:.1f} ESAL a round trip",
             f"  other sections and hubs: {other:.2f} ESAL (lesson M's assumption)",
             f"  turbine parts: {before:,.0f} ESAL in lesson M, {after:,.0f} now",
             f"  site total {total_m:,} -> {total_m - before + after:,.0f} standard axles"
             f" (+{(after - before) / total_m * 100:.1f} %)",
             "  the heavier, fewer axles of the real trailers add about a",
             "  thousand standard axles, yet the aggregate and water trucks",
             "  still wear the road most; what the nacelle trailer changes",
             "  is the single pass - a 119 kN axle on a wet subgrade can",
             "  rut it at once, so the soft stretches are proof-rolled",
             "  before the first convoy (ch 31)"]
    emit("r_abnormal", lines)


if __name__ == "__main__":
    characteristic()
    slope()
    abnormal()
