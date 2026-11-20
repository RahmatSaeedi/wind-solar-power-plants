"""Chapter 29, lesson K (more on the survey and the ground model): a
levelling loop and its misclosure, a drone survey planned from the
camera, the chance that boreholes miss a soft lens, soil classes from
laboratory results, groundwater under a foundation, and collapsible
soil that settles when wetted.

Run from the project root:   python -m companion.ch29.examples_k
Writes companion/ch29/expected/k_*.txt and diagrams/data/ch29-lens.csv.
Teaching values (A-349); no foundation is designed here (ch 30).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch29 import sources as src
from companion.ch29.common import csv, emit
from plantp import civil as cv
from plantp import siting as st


def levelling() -> None:
    legs = [("BM1-P1", 1.10, +2.315), ("P1-P2", 0.95, -0.842), ("P2-P3", 1.30, +1.976),
            ("P3-P4", 0.85, -3.104), ("P4-P5", 1.20, +0.521), ("P5-BM1", 0.80, -0.852)]
    k = sum(d for _, d, _ in legs)
    mis = sum(h for _, _, h in legs)
    allow = 12 * math.sqrt(k) / 1000
    lines = ["a closed levelling loop from benchmark BM1 (teaching)",
             f"  length {k:.2f} km; misclosure {1000 * mis:+.0f} mm; allowed 12 sqrt(K) ="
             f" {1000 * allow:.0f} mm",
             "  leg       km    observed m   correction mm   adjusted m   height m"]
    h = 1200.000
    for name, d, dh in legs:
        corr = -mis * d / k
        h += dh + corr
        lines.append(f"  {name:8s} {d:4.2f}   {dh:+10.3f}   {1000 * corr:+13.1f}   {dh + corr:+10.3f}"
                     f"   {h:8.3f}")
    lines += ["  the loop closes within its allowance, so the misclosure",
              "  is shared in proportion to length and BM1 returns to",
              "  1200.000 m; a loop outside it is re-observed, never",
              "  'adjusted' - the error is found, not spread"]
    emit("k_levelling", lines)


def drone() -> None:
    pixel, focal, height = 2.41e-6, 8.8e-3, 100.0          # 1-inch 20 MP camera (teaching)
    gsd = pixel * height / focal
    w_img, h_img = 5472 * gsd, 3648 * gsd
    step_side, step_front = w_img * (1 - 0.65), h_img * (1 - 0.75)
    x, y = np.meshgrid(np.arange(5000, 13000, 25.0), np.arange(0, 7000, 25.0))
    pv = float(st.in_polygon(x, y, src.PV_BLOCK).sum() * 625) / 1e6
    areas = [("PV block", pv), ("roads, 60 m corridor x 28 km", 28 * 0.06),
             ("turbine areas 200 x 200 m", 12 * 0.04), ("substation and compound", 0.10)]
    total = sum(a for _, a in areas)
    path = total * 1e6 / step_side / 1000
    flights = math.ceil(path / (10 * 20 * 60 / 1000))
    rng = np.random.default_rng(29)
    err = 0.015 + 0.03 * rng.standard_normal(15)
    rmse = float(np.sqrt(np.mean(err ** 2)))
    lines = ["a drone survey planned from the camera (teaching values)",
             f"  ground sample distance at {height:.0f} m: {100 * gsd:.2f} cm;"
             f" image {w_img:.0f} x {h_img:.0f} m",
             f"  65 % side and 75 % front overlap: lines {step_side:.1f} m apart,"
             f" photos every {step_front:.1f} m"]
    for name, a in areas:
        lines.append(f"  {name:31s} {a:5.2f} km2")
    lines += [f"  total {total:.2f} km2 -> {path:.0f} km of flight lines -> {flights} flights"
              " of 20 min at 10 m/s",
              f"  15 check points: mean error {100 * err.mean():+.1f} cm, RMSE {100 * rmse:.1f} cm"
              " (teaching requirement 5 cm)",
              "  the check points are surveyed separately and never used",
              "  to fit the model; the RMSE is within the requirement and",
              "  the mean shows no bias - a mean far from zero (a datum or",
              "  antenna-height error) would fail the model even with a",
              "  small spread"]
    emit("k_drone", lines)


def lens() -> None:
    rf = 10.0                                           # footprint radius m (ch 30 decides)
    patterns = {"1 borehole at the centre": [(0.0, 0.0)],
                "centre + 3 CPTs at 7 m": [(0.0, 0.0)] + [(7 * math.cos(a), 7 * math.sin(a))
                                                         for a in (0.5, 2.6, 4.7)],
                "centre + 6 CPTs at 8 m": [(0.0, 0.0)] + [(8 * math.cos(a), 8 * math.sin(a))
                                                         for a in np.arange(6) * math.pi / 3]}
    rng = np.random.default_rng(7)
    lines = ["the chance that probes find a soft lens which lies under part of a",
             "  20 m footprint (lens centre random; Monte Carlo, 40,000 draws)",
             "  lens diameter m   1 borehole   + 3 CPTs at 7 m   + 6 CPTs at 8 m"]
    rows = []
    for d in (5, 10, 20, 40):
        r = d / 2
        rad = (rf + r) * np.sqrt(rng.random(40_000))
        ang = 2 * math.pi * rng.random(40_000)
        cx, cy = rad * np.cos(ang), rad * np.sin(ang)
        p = []
        for pts in patterns.values():
            hit = np.zeros(cx.size, bool)
            for px, py in pts:
                hit |= np.hypot(cx - px, cy - py) <= r
            p.append(hit.mean())
        rows.append((d, *(f"{q:.3f}" for q in p)))
        lines.append(f"  {d:15d}   {100 * p[0]:9.0f} %   {100 * p[1]:13.0f} %   {100 * p[2]:13.0f} %")
    csv("ch29-lens.csv", "d,one,four,seven", rows)
    lines += [f"  (one central borehole, exact: r^2/(R+r)^2 = {100 * 2.5 ** 2 / 12.5 ** 2:.0f} %"
              " for a 5 m lens)",
              "  one borehole finds a small lens only by luck; more probes",
              "  raise the chance quickly, and geophysics or a CPT pattern",
              "  is what a foundation on mixed ground needs - between the",
              "  turbines, 600 m apart, a lens is never found by boreholes"]
    emit("k_lens", lines)


def classify() -> None:
    samples = [("BH-01 0.5 m", 5, 70, 25, 22, 19, None, None),
               ("BH-01 3.0 m", 55, 41, 4, None, None, 25.0, 1.8),
               ("BH-04 1.0 m", 0, 20, 80, 42, 20, None, None),
               ("BH-04 5.0 m", 5, 87, 8, None, None, 3.2, 0.9),
               ("BH-07 1.0 m", 10, 60, 30, 28, 21, None, None),
               ("BH-09 0.5 m", 2, 68, 30, 24, 21, None, None)]

    def plastic(ll, pl):
        if ll is None:
            return "M"
        pi = ll - pl
        return "C" if pi > 4 and pi > 0.73 * (ll - 20) else "M"

    def graded(main, cu, cc):
        ok = cu is not None and 1 <= cc <= 3 and cu >= (4 if main == "G" else 6)
        return "W" if ok else "P"

    lines = ["soil classes from the laboratory results (unified classification,",
             "  simplified teaching rules; A-line PI = 0.73 (LL - 20))",
             "  sample        gravel  sand  fines   LL   PI   class   log description"]
    logs = {"BH-01 0.5 m": "silty sand", "BH-01 3.0 m": "sand and gravel",
            "BH-04 1.0 m": "silty clay, soft", "BH-04 5.0 m": "sand, medium dense",
            "BH-07 1.0 m": "silty sand, gypsum", "BH-09 0.5 m": "silty sand"}
    for name, g, s, f, ll, pl, cu, cc in samples:
        if f > 50:
            cls = plastic(ll, pl) + ("H" if ll >= 50 else "L")
        else:
            main = "G" if g > s else "S"
            if f < 5:
                cls = main + graded(main, cu, cc)
            elif f > 12:
                cls = main + plastic(ll, pl)
            else:
                cls = f"{main}{graded(main, cu, cc)}-{main}{plastic(ll, pl)}"
        ll_s = f"{ll:4d}" if ll else "  NP"
        pi_s = f"{ll - pl:4d}" if ll else "   -"
        lines.append(f"  {name:12s}  {g:6d}  {s:4d}  {f:5d}  {ll_s} {pi_s}   {cls:6s}  {logs[name]}")
    lines += ["  BH-07's 'silty sand' is a clayey sand (SC) in the",
              "  laboratory: the log is a field description, the class a",
              "  test - where they disagree the test wins and the log is",
              "  annotated; the class alone never gives design values"]
    emit("k_classify", lines)


def uplift() -> None:
    rf, base = 10.0, src.FOUNDATION_DEPTH
    area = math.pi * rf ** 2
    n60 = 18 * 45 / 60                                  # T07 sand, cautious energy (a_spt)
    phi = 27.1 + 0.3 * n60 - 0.00054 * n60 ** 2
    nc, nq, ng = cv.bearing_factors(phi)
    lines = ["groundwater at T07 (BH-04: 3.0 m below ground) and a foundation",
             f"  whose base would sit {base:.1f} m down (20 m footprint, teaching)",
             "  water depth m   submerged m   uplift kN   bearing q_ult kPa (sand phi 31)"]
    for w in (25.0, 3.0, 2.0, 0.5):
        sub = max(base - w, 0.0)
        u = 9.81 * area * sub
        g_over = 19.0 if w >= base else (19.0 * w + 9.2 * (base - w)) / base
        g_below = 9.2 if w <= base + 2 * rf else 19.0
        q = g_over * base * nq + 0.4 * g_below * 2 * rf * ng
        label = "  deep (dry)" if w > 20 else f"  {w:10.1f}"
        lines.append(f"{label}     {sub:11.1f}   {u:9,.0f}   {q:12,.0f}")
    lines += ["  (water within one footprint width below the base halves",
              "  the soil weight in the width term: the dry row is a_spt's)",
              "  a rise of the water table from 3.0 to 0.5 m multiplies the",
              "  uplift by six and lowers the ultimate bearing by a sixth:",
              "  the seasonal and flood range of groundwater (question Q6",
              "  of lab D) is a design input, not a borehole footnote"]
    emit("k_uplift", lines)


def collapse() -> None:
    tests = [("BH-01 0.5 m", 0.4), ("BH-09 0.5 m", 1.2), ("BH-07 0.5 m (gypsum)", 6.5)]
    lines = ["collapse on wetting (oedometer at 200 kPa, strain % when flooded;",
             "  classes are teaching - published ones differ)",
             "  sample                  strain %   class      settlement of 1.5 m layer mm"]
    for name, e in tests:
        cls = "slight" if e < 1 else "moderate" if e < 5 else "severe"
        lines.append(f"  {name:22s} {e:8.1f}   {cls:10s} {10 * e * 1.5:12.0f}")
    lines += ["  dry, the gypsum layer at T12 is strong; wetted (a leaking",
              "  pipe, ponding beside a pad) it can settle about 100 mm",
              "  under a building or a tank: keep water away by design -",
              "  falls away from structures, no soakaways near them - and",
              "  ask the engineer whether to replace or pre-wet the layer"]
    emit("k_collapse", lines)


if __name__ == "__main__":
    levelling()
    drone()
    lens()
    classify()
    uplift()
    collapse()
