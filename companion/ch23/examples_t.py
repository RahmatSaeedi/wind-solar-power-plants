"""Chapter 23 - a temporary load in the maintenance state (an oil-treatment
plant for a main transformer) checked against one station-service
transformer, and the receiving network seen from the point of
connection: how the plant's export moves the voltage there.

Run from the project root:   python -m companion.ch23.examples_t
Writes companion/ch23/expected/t_*.txt. Teaching values (A-317, A-320
extended: oil-treatment plant, grid X/R).
"""
from __future__ import annotations

import math

from companion.ch23 import sources as src
from companion.ch23.common import emit
from plantp import auxpower as ax


def temporary() -> None:
    p, q, s = ax.demand(src.AUX, "maintenance", src.DIVERSITY)
    kw, pf = 60.0, 0.85
    q_t = kw * math.tan(math.acos(pf))
    s2 = math.hypot(p + kw, q + q_t)
    usable = 236.0                       # 250 kVA after harmonics (lesson F)
    lines = ["maintenance state with a temporary oil-treatment plant (60 kW):",
             f"  register, maintenance state: {s:.0f} kVA",
             f"  plus the treatment plant: {s2:.0f} kVA on one 250 kVA transformer",
             f"    ({s2 / 250:.0%} of rating, {s2 / usable:.0%} of the {usable:.0f} kVA left"
             " after harmonics)",
             "  the second transformer may be out for its own maintenance",
             "  at the same time: then the plan must keep the workshop and",
             "  the socket outlets off while the plant runs, or bring a",
             "  temporary generator - a line in the maintenance plan (ch 52)",
             "  temporary loads enter the register as a state of their own,",
             "  with their own supply point and protection"]
    emit("t_temporary", lines)


def receiving() -> None:
    s_k, xr = 1500.0, 10.0
    z = 100.0 / s_k                      # pu on 100 MVA at the POC
    r, x = z / math.sqrt(1 + xr ** 2), z * xr / math.sqrt(1 + xr ** 2)
    lines = ["the receiving network seen from the POC (1,500 MVA, X/R 10, teaching):",
             f"  grid impedance on 100 MVA: r {r:.4f}, x {x:.4f} pu",
             "  export P MW   Q Mvar   voltage change at the POC %"]
    for p_mw, q_mvar in ((100, 0), (100, -20), (100, -33), (50, 0)):
        dv = (r * p_mw + x * q_mvar) / 100.0
        lines.append(f"  {p_mw:11d}   {q_mvar:6d}   {dv * 100:+8.2f}")
    lines += ["  dV ~ R P + X Q: export raises the voltage a little through",
              "  R; absorbing reactive power pulls it back through X; with",
              "  a strong grid the effect is small - the receiving network's",
              "  strength and X/R are utility data (U-089) and the full study",
              "  is ch 28; the one-line carries the grid as an impedance at",
              "  the POC for exactly this purpose"]
    emit("t_receiving", lines)


if __name__ == "__main__":
    temporary()
    receiving()
