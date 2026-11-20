"""Chapter 28 - expansion round 5: is the aggregated feeder good enough
(one wind string modelled turbine by turbine), what reactive power at
zero output costs in energy, and how the line's temperature moves its
losses.

Run from the project root:   python -m companion.ch28.examples_p
Writes companion/ch28/expected/p_*.txt. Teaching values (A-342, A-348).
"""
from __future__ import annotations

import numpy as np

from companion.ch28 import sources as src
from companion.ch28.common import emit
from plantp import gridstudy as gs

ZB33 = 33.0 ** 2 / src.S_BASE


# [start: string]
def string_flow(n_units: int, km_each: float, aggregated: str = "") -> dict:
    """One wind string at full output from a stiff 33 kV bus: turbine by
    turbine, or aggregated at a fraction of its length ('half', 'third')."""
    r20, x, c = src.CABLE[630]
    r = src.r_hot(r20)
    ux, ur = 0.06 * 100 / 5.6, 0.009 * 100 / 5.6     # one unit transformer
    if aggregated:
        frac = {"half": 0.5, "third": 1 / 3}[aggregated]
        km = n_units * km_each * frac
        br = [gs.Branch(0, 1, r * km / ZB33, x * km / ZB33),
              gs.Branch(1, 2, ur / n_units, ux / n_units)]
        p, q = [0, 0, n_units * 0.05], [0, 0, n_units * 5.6 * 0.12 / 100]
        kinds = ["slack", "pq", "pq"]
    else:
        br, p, q, kinds = [], [0.0], [0.0], ["slack"]
        zc = (r * km_each / ZB33, x * km_each / ZB33)
        for k in range(n_units):              # cable node k+1, unit 1+n+k
            br.append(gs.Branch(k, k + 1, *zc))
        for k in range(n_units):
            br.append(gs.Branch(k + 1, n_units + 1 + k, ur, ux))
        p += [0.0] * n_units + [0.05] * n_units
        q += [0.0] * n_units + [5.6 * 0.12 / 100] * n_units
        kinds += ["pq"] * (2 * n_units)
    n = len(kinds)
    res = gs.load_flow(gs.ybus(n, br), kinds, p, q, [1.0] * n)
    fl = gs.flows(res["v"], br)
    loss = sum(f["loss"].real for f in fl)
    return {"v_last": abs(res["v"][-1]), "loss_kw": 1e5 * loss}
# [end: string]


def aggregation() -> None:
    d = string_flow(4, 1.1)
    h = string_flow(4, 1.1, "half")
    t = string_flow(4, 1.1, "third")
    lines = ["one wind string (4 turbines, 1.1 km apart, 630 mm2) at full output",
             "  model                         V at the far unit   losses kW",
             f"  turbine by turbine            {d['v_last']:17.4f}   {d['loss_kw']:9.1f}",
             f"  aggregated at half length     {h['v_last']:17.4f}   {h['loss_kw']:9.1f}",
             f"  aggregated at a third         {t['v_last']:17.4f}   {t['loss_kw']:9.1f}",
             "  at half length the losses agree within about 1 %; at a",
             "  third they come out 6 % low - with turbines one span apart",
             "  from the bus the loss-equivalent length is near half (a",
             "  third holds for load spread evenly from the bus); the far",
             "  turbine's terminal is within 0.1 % here, but on a long",
             "  string it is checked with the detailed string, not the",
             "  aggregate"]
    emit("p_aggregate", lines)


def night_q() -> None:
    from companion.ch15 import sources as s15
    p = s15.plant_year()["delivered"]
    idle = int(np.sum(p < 1.0))
    standby_kw = 0.003 * (12 * 5600 + 10 * 5500)          # 0.3 % of rating, teaching
    r = src.solve({"wind": 0.0, "pv": 0.0}, 0.0)
    lines = ["reactive power at zero output (night, calm) - what it costs",
             f"  Q at the POC with the units idle (cables and line): {r['s_poc'].imag:+.1f} Mvar",
             f"  hours of the data year with less than 1 MW of export: {idle}",
             f"  units kept energised in Q mode: {standby_kw:.0f} kW of standby losses",
             f"  energy for a year of Q-at-night readiness: {standby_kw * idle / 1e3:.0f} MWh"
             f" ({standby_kw * idle / 1e3 * 0.07:.0f} k u at 70 u/MWh)",
             "  a requirement for a Q range at zero output is met by the",
             "  units (if their makers allow Q mode at night), at this",
             "  energy cost - or by a small reactor or compensator; the",
             "  study prices both, the operator says if it is required"]
    emit("p_night", lines)


def line_temperature() -> None:
    i = 437.0
    lines = ["the line's losses at full export against conductor temperature",
             "  conductor C   R ohm (7.06 km)   loss MW"]
    for tc in (20, 50, 75):
        r = 0.10 * (1 + 0.00403 * (tc - 20)) * src.LINE["km"]
        lines.append(f"  {tc:11d}   {r:15.3f}   {3 * i * i * r / 1e6:7.3f}")
    lines += ["  the study's 0.12 ohm/km is the conductor at about 70 C:",
              "  right for full export, a little high for a cool night -",
              "  a few per cent of the line's losses, inside the budget of",
              "  lesson G; stated in the assumptions, not hidden"]
    emit("p_linetemp", lines)


if __name__ == "__main__":
    aggregation()
    night_q()
    line_temperature()
