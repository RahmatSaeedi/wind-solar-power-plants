"""Chapter 24 - two installation-QA lessons: where a cable fault lies from
the time of its reflection, and the as-built cover depth of a trench
read as statistics against the specified minimum.

Run from the project root:   python -m companion.ch24.examples_y
Writes companion/ch24/expected/y_*.txt. Teaching values (A-321..A-325
extended); fault location is done by trained crews with their own
instruments and procedures.
"""
from __future__ import annotations

import statistics

from companion.ch24.common import emit

C = 299.79                       # m per microsecond


def reflection() -> None:
    vf = 0.55                    # velocity factor of the XLPE cable (teaching)
    v = vf * C
    lines = ["locating a cable fault from the time of its reflection:",
             f"  pulse speed in the cable {vf} x c = {v:.0f} m/us; distance = v t / 2",
             "  echo after us   distance m   which section of =WS1"]
    for t in (4.0, 13.3, 26.7, 40.0):
        dist = v * t / 2
        sec = min(int(dist // 1100) + 1, 4)
        lines.append(f"  {t:13.1f}   {dist:10.0f}   W{sec}")
    lines += ["  the echo time gives the distance only as well as the speed",
              "  is known: a 5 % error in the velocity factor is 110 m at",
              "  the far end - the crew then pinpoints on the surface before",
              "  anyone digs; the as-built route survey turns the distance",
              "  into a place on the ground"]
    emit("y_reflection", lines)


DEPTHS = [0.98, 1.02, 0.95, 1.05, 0.88, 1.01, 0.97, 0.79, 1.03, 0.99, 1.04, 0.92,
          0.96, 1.00, 0.76, 1.02, 0.98, 0.94, 1.06, 0.97]           # m, as-built


def depth() -> None:
    spec_min = 0.80
    low = [(i * 50, d) for i, d in enumerate(DEPTHS) if d < spec_min]
    lines = ["as-built cover over the cable, every 50 m along one trench (m):",
             f"  mean {statistics.mean(DEPTHS):.2f}, lowest {min(DEPTHS):.2f},"
             f" readings below the {spec_min:.2f} m minimum: {len(low)}"]
    lines += [f"    at {x:4d} m: {d:.2f} m" for x, d in low]
    lines += ["  the mean says the trench is fine; two places are not -",
              "  each becomes a nonconformity: dig and lower, or protect",
              "  with a slab and record it; a shallow cable is a future",
              "  dig-in, closer to the summer-hot surface and to ploughs -",
              "  its rating even rises a little, so the defect is",
              "  mechanical, and the record is what protects it"]
    emit("y_depth", lines)


if __name__ == "__main__":
    reflection()
    depth()
