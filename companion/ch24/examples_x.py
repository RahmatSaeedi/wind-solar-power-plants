"""Chapter 24 - corona on the 132 kV conductor: the surface field of a
round conductor against the onset field of air (Peek's form), and how
altitude and the conductor's radius move the margin; plus the daily
current and the cable temperature behind the cyclic rating (figure data).

Run from the project root:   python -m companion.ch24.examples_x
Writes companion/ch24/expected/x_corona.txt and diagrams/data/ch24-cyclic.csv.
Teaching physics (A-324 extended): the line designer checks corona and
radio noise with the conductor maker's data.
"""
from __future__ import annotations

import math

from companion.ch24.common import csv, emit


def corona() -> None:
    u_ph = 145 / math.sqrt(3)              # kV rms, highest voltage
    d_ph = 400.0                           # cm, equivalent phase spacing
    lines = ["corona on the 132 kV conductor (single conductor per phase):",
             "  E = U / (r ln(D / r)); onset E0 = 30 m d (1 + 0.3 / sqrt(d r))",
             "  (kV/cm peak; m 0.85 for a stranded surface, d relative air density)",
             "  radius cm   site            d     E kV/cm   E0 kV/cm   margin"]
    for r in (1.225, 1.60):
        e = u_ph * math.sqrt(2) / (r * math.log(d_ph / r))
        for site, delta in (("sea level", 1.00), ("1,500 m", 0.85), ("2,500 m", 0.75)):
            e0 = 30 * 0.85 * delta * (1 + 0.3 / math.sqrt(delta * r))
            lines.append(f"  {r:9.3f}   {site:12s} {delta:5.2f}   {e:7.1f}   {e0:8.1f}"
                         f"   {e0 / e:6.2f}")
    e_small = u_ph * math.sqrt(2) / (1.225 * math.log(d_ph / 1.225))
    lines.append("  in rain (surface factor m about 0.5, teaching), radius 1.225 cm:")
    for site, delta in (("sea level", 1.00), ("2,500 m", 0.75)):
        e0w = 30 * 0.5 * delta * (1 + 0.3 / math.sqrt(delta * 1.225))
        lines.append(f"    {site:10s} E0 {e0w:5.1f} kV/cm against E {e_small:.1f}:"
                     f" {'corona' if e0w < e_small else 'margin ' + format(e0w / e_small, '.2f')}")
    lines += ["  thin air lowers the onset field and rain lowers it more: a",
              "  conductor quiet in dry weather at sea level can hum and lose",
              "  power in rain on a high plateau; a larger diameter (or two",
              "  conductors per phase) lowers the surface field - corona,",
              "  audible and radio noise are checked by the line designer",
              "  with the maker's data"]
    emit("x_corona", lines)


def cyclic_data() -> None:
    rows = []
    for h in range(24):
        sun = max(0.0, math.sin(math.pi * (h - 6) / 12)) if 6 <= h <= 18 else 0.0
        i = 765.0 * sun                     # A, the cyclic rating of lesson A at noon
        rows.append((h, f"{i:.0f}", f"{660:.0f}"))
    csv("ch24-cyclic.csv", "h,pv,cont", rows)


if __name__ == "__main__":
    corona()
    cyclic_data()
