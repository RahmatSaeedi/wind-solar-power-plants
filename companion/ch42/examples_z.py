"""Chapter 42, a ninth round on measurement at the factory: why the
back-to-back rig measures gearbox loss better than two power readings,
the nacelle's centre of gravity from four load cells, the root insert
circle fitted by least squares, saddle loads of the static blade test
found by linear programming, and coating thickness by mean and minimum.

Run from the project root:   python -m companion.ch42.examples_z
Writes companion/ch42/expected/z_*.txt.
Teaching values (A-453, A-456); measurement relations, no procedures.
"""
from __future__ import annotations

import math
import random
from statistics import mean

import numpy as np
from scipy.optimize import linprog

from companion.ch42.common import emit


# ------------------------------------------------ loss: direct or back to back
def loss_uncertainty(p_in: float = 5329.0, p_out: float = 5313.0 - 106.0,
                     u_power: float = 0.003, gb_loss: float = 106.0,
                     machine_loss: float = 130.0, u_machine: float = 0.05,
                     u_meter: float = 0.002) -> dict[str, float]:
    u_direct = math.hypot(u_power * 5313.0, u_power * p_out)
    supply = 2 * gb_loss + 2 * machine_loss
    u_b2b = math.sqrt((u_meter * supply) ** 2
                      + 2 * (u_machine * machine_loss) ** 2) / 2
    lines = [f"gearbox loss {gb_loss:.0f} kW at rated: two ways to measure it "
             "(teaching)",
             f"  direct: input and output power, each to {u_power:.1%}",
             f"  loss as a difference of two large numbers: +-{u_direct:.0f} kW",
             f"    ({u_direct / gb_loss:.0%} of the loss)",
             f"  back to back: the supply makes up {supply:.0f} kW of losses "
             f"(meter {u_meter:.1%})",
             f"  machine losses known to {u_machine:.0%}; one gearbox: "
             f"+-{u_b2b:.1f} kW ({u_b2b / gb_loss:.1%})",
             "  the rig measures the small number directly instead of",
             "  subtracting two big ones - its loss result is "
             f"{u_direct / u_b2b:.0f} times",
             "  sharper, which is why efficiency claims cite it"]
    emit("z_loss", lines)
    return dict(direct=u_direct, b2b=u_b2b)


# ------------------------------------------------ centre of gravity
def cog(readings_t=(47.1, 44.3, 35.2, 33.4), dx: float = 2.0, dy: float = 1.5,
        drawing=(0.20, 0.00), limit_mm: float = 100.0, u_cell: float = 0.005):
    pts = [(dx, dy), (dx, -dy), (-dx, dy), (-dx, -dy)]
    tot = sum(readings_t)
    x = sum(f * p[0] for f, p in zip(readings_t, pts)) / tot
    y = sum(f * p[1] for f, p in zip(readings_t, pts)) / tot
    off = 1000 * math.hypot(x - drawing[0], y - drawing[1])
    u_x = 1000 * dx * math.sqrt(4 * (u_cell * tot / 4) ** 2) / tot
    lines = ["nacelle on four load cells at the lifting points (+-2.0 m, "
             "+-1.5 m)",
             "  readings t: " + ", ".join(f"{r:.1f}" for r in readings_t)
             + f"; total {tot:.1f} t",
             f"  centre of gravity x {x:.3f} m, y {y:.3f} m; drawing "
             f"{drawing[0]:.2f} / {drawing[1]:.2f} m",
             f"  difference {off:.0f} mm (teaching limit {limit_mm:.0f})",
             f"  load-cell error moves x by about {u_x:.0f} mm",
             "  the weighed mass and centre go on the record the crane plan",
             "  of ch 31 uses; a drawing value is a prediction, and here it",
             "  is out by nearly the whole limit"]
    emit("z_cog", lines)
    return dict(x=x, y=y, off=off)


# ------------------------------------------------ insert circle
# [start: circle]
def fit_circle(x, y):
    """Least-squares circle through points (Kasa): centre and radius."""
    a = np.column_stack([x, y, np.ones_like(x)])
    rhs = -(x ** 2 + y ** 2)
    d, e, f = np.linalg.lstsq(a, rhs, rcond=None)[0]
    xc, yc = -d / 2, -e / 2
    return xc, yc, math.sqrt(xc ** 2 + yc ** 2 - f)
# [end: circle]


def circle(seed: int = 4218, n: int = 96, r_mm: float = 1600.0,
           limit_mm: float = 1.5) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    ang = np.arange(n) * 2 * math.pi / n
    r = r_mm + rng.normal(0.0, 0.3, n)
    r[57] += 2.6                                   # one insert displaced
    x = 0.4 + r * np.cos(ang)
    y = -0.2 + r * np.sin(ang)
    xc, yc, rf = fit_circle(x, y)
    dev = np.hypot(x - xc, y - yc) - rf
    worst = int(np.argmax(np.abs(dev)))
    over = int(np.sum(np.abs(dev) > limit_mm))
    lines = [f"{n} root inserts measured on a {2 * r_mm / 1000:.1f} m circle "
             "(coordinate machine)",
             f"  fitted centre ({xc:+.2f}, {yc:+.2f}) mm; radius "
             f"{rf - r_mm:+.2f} mm from nominal",
             f"  worst insert {worst + 1}: {dev[worst]:+.2f} mm radially; "
             f"over +-{limit_mm} mm: {over}",
             "  the fit takes out where the circle sits; what is left is each",
             "  insert's own error, which the bolt must pass through the",
             "  bearing's hole - one bad insert is an NCR, not a re-machined",
             "  bearing"]
    emit("z_circle", lines)
    return dict(worst=worst + 1, dev=float(dev[worst]), over=over)


# ------------------------------------------------ static test saddles
STATIONS = np.array([5.0, 15.0, 25.0, 35.0, 45.0, 55.0, 65.0])


def target(r):
    return 30.8 * (1 - r / 75.0) ** 2              # MN m, extreme (teaching)


def saddle_forces(pos):
    """Smallest overshoot: test moment at least the target at each station."""
    arm = np.array([[max(a - r, 0.0) for a in pos] for r in STATIONS])
    res = linprog(arm.sum(axis=0), A_ub=-arm, b_ub=-target(STATIONS),
                  bounds=[(0, None)] * len(pos), method="highs")
    return res.x, arm @ res.x


def saddles() -> dict[str, float]:
    lines = ["static flap test: saddle forces so that the test moment is at",
             "  least the extreme moment at every station, with the least",
             "  overshoot (linear programming; target 30.8 (1 - r/75)^2 MN m)"]
    lines.append("  stations m: " + " ".join(f"{r:4.0f}" for r in STATIONS))
    out = {}
    for name, pos in (("two", [35.0, 68.0]), ("three A", [25.0, 45.0, 68.0]),
                      ("three B", [30.0, 50.0, 68.0]),
                      ("six", [15.0, 28.0, 40.0, 52.0, 62.0, 70.0])):
        f, m = saddle_forces(pos)
        ratio = m / target(STATIONS)
        out[name] = float(ratio.max())
        lines.append(f"  {name} at " + ", ".join(f"{p:.0f}" for p in pos)
                     + " m: kN " + ", ".join(f"{v * 1000:.0f}" for v in f))
        lines.append("    test/target " + " ".join(f"{v:4.2f}" for v in ratio)
                     + f"   worst +{ratio.max() - 1:.0%}")
    lines += ["  point loads give a moment that is straight between saddles",
              "  while the target curves: placement matters as much as the",
              f"  number (three A +{out['three A'] - 1:.0%}, three B "
              f"+{out['three B'] - 1:.0%}), and a station tested far",
              "  above its load is one the test may break for the wrong",
              "  reason"]
    emit("z_saddles", lines)
    return out


# ------------------------------------------------ coating thickness
def coating(seed: int = 4219, nominal: float = 500.0) -> dict[str, list[str]]:
    rng = random.Random(seed)
    lines = [f"leading-edge coating, 20 readings a blade (nominal {nominal:.0f} "
             "um; teaching rule:",
             "  mean at least nominal and no reading below 80 %)",
             "  blade    mean um   lowest um   verdict"]
    bad = []
    for b in ("B-131", "B-132", "B-133"):
        vals = [rng.gauss(560.0, 30.0) for _ in range(20)]
        if b == "B-133":
            vals[7:10] = [372.0, 365.0, 381.0]
        ok = mean(vals) >= nominal and min(vals) >= 0.8 * nominal
        if not ok:
            bad.append(b)
        lines.append(f"  {b}   {mean(vals):7.0f}   {min(vals):9.0f}   "
                     f"{'accept' if ok else 'recoat'}")
    lines += ["  B-133's mean passes; three thin readings in one patch do not",
              "  - erosion starts at the thinnest place, not at the mean"
              " (ch 11)"]
    emit("z_coating", lines)
    return dict(bad=bad)


if __name__ == "__main__":
    loss_uncertainty()
    cog()
    circle()
    saddles()
    coating()
