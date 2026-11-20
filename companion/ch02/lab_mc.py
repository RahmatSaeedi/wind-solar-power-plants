"""Chapter 2 laboratory 2 — when the first-order (GUM) formula and Monte Carlo disagree.

Run from the project root:   python -m companion.ch02.lab_mc
Propagates an uncertain wind speed through the WT-5.0-150 power curve at three
operating points, by the linear formula and by Monte Carlo, and shows how the Monte
Carlo estimate settles as the number of draws grows.
Writes companion/ch02/expected/lab_mc.txt and diagrams/data/ch02-lab-mc.csv.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plantp import datapack, uncertainty as un  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "expected" / "lab_mc.txt"
DATA = HERE.parents[1] / "diagrams" / "data" / "ch02-lab-mc.csv"


def main() -> None:
    curve = datapack.load_power_curve()
    speeds = curve["wind_speed_ms"].to_numpy()
    power = curve["power_kw"].to_numpy()

    def turbine_kw(v):
        return np.interp(v, speeds, power)

    lines = ["WT-5.0-150 power from a wind speed with u(v) = 0.5 m/s (assumed, normal)",
             f"{'v (m/s)':>8s} {'P lin':>8s} {'u lin':>7s} {'P mc':>8s} {'u mc':>7s} "
             f"{'95 % interval (kW)':>20s}"]
    # [start: compare]
    for v0 in (6.0, 9.0, 12.5):
        # first order (GUM): slope of the curve times u(v)
        lin = un.combine(lambda v: float(turbine_kw(v)), {"v": v0},
                         {"v": 0.5})
        # Monte Carlo: 200,000 speeds from N(v0, 0.5), each through the curve
        mc = un.monte_carlo(lambda v: turbine_kw(v),
                            {"v": ("normal", v0, 0.5)})
        lines.append(f"{v0:8.1f} {lin.y:8.0f} {lin.u_c:7.0f} "
                     f"{mc.mean:8.0f} {mc.std:7.0f} "
                     f"{mc.low:9.0f} .. {mc.high:6.0f}")
    # [end: compare]
    lines.append("at 12.5 m/s the curve bends towards rated power:")
    lines.append("    the linear formula misses the asymmetry")

    lines.append("")
    lines.append("convergence of Monte Carlo at v = 9.0 m/s (20 seeds per size)")
    rows = []
    sigma_p = 488.0                       # std of P from the large run above, kW
    for n in (100, 1_000, 10_000, 100_000):
        means = [un.monte_carlo(lambda v: turbine_kw(v), {"v": ("normal", 9.0, 0.5)},
                                n=n, seed=s).mean for s in range(20)]
        spread = float(np.std(means, ddof=1))
        rows.append((n, np.mean(means), spread))
        lines.append(f"  n = {n:>7,d}: mean {np.mean(means):7.1f} kW, spread between "
                     f"seeds {spread:5.1f} kW (theory {sigma_p / np.sqrt(n):5.1f})")
    lines.append("the spread shrinks about 3.2 times for every 10 times more draws "
                 "(1 / sqrt(n))")
    with open(DATA, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("n,mean,spread\n")
        for n, m, s in rows:
            fh.write(f"{n},{m:.2f},{s:.3f}\n")
    text = "\n".join(lines) + "\n"
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(text)


if __name__ == "__main__":
    main()
