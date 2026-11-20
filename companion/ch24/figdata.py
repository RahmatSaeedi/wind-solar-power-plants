"""Chapter 24 - plot data for the figures (CSV in diagrams/data).

Run from the project root:   python -m companion.ch24.figdata
"""
from __future__ import annotations

import math

from companion.ch24 import examples_a as ea
from companion.ch24 import sources as src
from companion.ch24.common import csv
from plantp import cables as cb

ALPHA_AL = 0.00403


def main() -> None:
    rows = []
    for k, (mm2, d) in enumerate(src.MV_CABLES.items(), 1):
        i, _ = cb.rating(d["i0"], src.FACTORS)
        rows.append((k, mm2, f"{d['i0']:.0f}", f"{i:.0f}"))
    csv("ch24-derating.csv", "k,mm2,ref,place", rows)

    i = ea.string_currents()
    rows = []
    for k, (mm2, d) in enumerate(src.MV_CABLES.items(), 1):
        r = cb.r_at(d["r20"], 65, ALPHA_AL)
        e = sum(cb.annual_loss_mwh(i * (5 - s) / 4, r, 1.1) for s in range(1, 5))
        rows.append((k, mm2, f"{e:.1f}"))
    csv("ch24-losses.csv", "k,mm2,mwh", rows)

    w, mu = 9.8 * 7.5, 0.35
    pts, t, x = [(0, 0.0)], 0.0, 0.0
    for seg in range(1, 21):                       # 200 m straight
        x, t = 10 * seg, mu * w * 10 * seg
        pts.append((x, t / 1e3))
    t = t * math.exp(mu * math.pi / 2)
    pts.append((200, t / 1e3))
    t0 = t
    for seg in range(1, 16):                       # 150 m straight
        x, t = 200 + 10 * seg, t0 + mu * w * 10 * seg
        pts.append((x, t / 1e3))
    t = t * math.exp(mu * math.pi / 4)
    pts.append((350, t / 1e3))
    csv("ch24-pulling.csv", "m,kn", [(a, f"{b:.2f}") for a, b in pts])

    rows = []
    for L in range(0, 1001, 100):
        rows.append((L, f"{cb.sheath_v(437, 140, 105, L):.1f}",
                     f"{cb.sheath_v(20_000, 140, 105, L) / 100:.1f}"))
    csv("ch24-bonding.csv", "m,full,fault100", rows)

    af = (1 - 1.075 ** -25) / 0.075
    rows = []
    plans = [(240, 240, 240, 240), (630, 240, 240, 240), (630, 400, 240, 240),
             (630, 630, 630, 630)]
    for k, sizes in enumerate(plans, 1):
        cost = loss = 0.0
        for s, mm2 in enumerate(sizes, 1):
            d = src.MV_CABLES[mm2]
            cost += d["cost"] * 1.1
            loss += cb.annual_loss_mwh(i * (5 - s) / 4,
                                       cb.r_at(d["r20"], 65, ALPHA_AL), 1.1)
        rows.append((k, f"{cost:.0f}", f"{loss * 70 / 1e3 * af:.0f}"))
    csv("ch24-graded.csv", "k,cost,losspv", rows)

    h = src.LINE["breaking_kn"] * 1e3 * src.LINE["tension_pct"] / 100
    rows = []
    for x in range(0, 351, 10):
        def y(span):
            if x > span:
                return "nan"
            s = cb.sag_m(src.LINE["weight_n_m"], span, h)
            return f"{-4 * s * (x / span) * (1 - x / span):.2f}"
        rows.append((x, y(250), y(300), y(350)))
    csv("ch24-sag.csv", "x,s250,s300,s350", rows)


if __name__ == "__main__":
    main()
    print("figure data written")
