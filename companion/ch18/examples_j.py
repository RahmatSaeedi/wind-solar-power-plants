"""Chapter 18, closing lessons: the source for the planned island of the
plant's critical loads (continuous load plus the largest motor start),
and spare parts sized from the product breakdown with Poisson demand
over the supplier's lead time.

Run from the project root:   python -m companion.ch18.examples_j
Writes companion/ch18/expected/j_*.txt.
Teaching values A-286 (loads, motors) and A-288 (failure rates).
"""
from __future__ import annotations

from scipy.stats import poisson

from companion.ch18.common import emit


def island() -> None:
    """Island source for 200 kW of critical loads with a 30 kW pump."""
    p_crit, pf = 200.0, 0.90                     # kW, ch 17 critical class
    motor_kw, start_x, start_pf = 30.0, 6.0, 0.35
    s_run = p_crit / pf
    s_start = motor_kw / 0.85 * start_x          # kVA drawn while starting
    peak = s_run + s_start
    lines = ["source for the critical-load island (teaching, A-286):",
             f"  running load {p_crit:.0f} kW at pf {pf}: {s_run:.0f} kVA",
             f"  largest motor {motor_kw:.0f} kW starting at x{start_x:.0f}"
             f" (pf {start_pf}): {s_start:.0f} kVA",
             f"  peak the source must carry: {peak:.0f} kVA (kVA added, an upper bound)",
             "  options:",
             "    dedicated grid-forming UPS of 500 kVA with 400 kWh: 2 h,",
             "      longer only with the main battery behind it",
             "    one 5 MVA battery block switched to the island: days,",
             "      but that block leaves the market while it serves",
             "    a 500 kVA generator: fuel-limited, a new interface",
             "  a soft starter on the pump cuts the start to about half",
             "  and lets a smaller source carry the island"]
    emit("j_island", lines)


# [start: spares]
SPARES = {  # item: (installed, failures per unit-year, lead time weeks)
    "PV module": (109_200, 0.0005, 12),
    "string fuse": (8_400, 0.002, 4),
    "inverter power stage": (40, 0.125, 8),
    "turbine blade": (36, 0.003, 26),
    "gearbox": (12, 0.02, 26),
    "main transformer": (2, 0.01, 52),
}


def spares_needed(n, lam, weeks, level=0.95):
    """Smallest stock that covers Poisson demand over the lead time
    with the given probability."""
    mean = n * lam * weeks / 52.0
    return mean, int(poisson.ppf(level, mean))
# [end: spares]


def spares() -> None:
    lines = ["spares from the breakdown, 95 % cover over the lead time",
             "  (failure rates A-288):",
             "  item                   installed  failures/yr  lead wk  mean  stock"]
    for k, (n, lam, wk) in SPARES.items():
        mean, stock = spares_needed(n, lam, wk)
        lines.append(f"  {k:21s} {n:10,d}   {n * lam:9.2f}   {wk:6d}  {mean:5.2f}  {stock:4d}")
    lines += ["  cheap many-unit items get a stock from demand; rare costly",
              "  items get zero or one, or a shared spare among plants; the",
              "  main transformer's answer (0) is why section B weighed",
              "  the second unit for the tail, not the mean"]
    emit("j_spares", lines)


# [start: lifecycle]
STAGES = ["identified", "defined", "agreed", "verified", "closed"]
GATES = {   # interface: stage reached at each gate (teaching)
    "concept":     [1, 1, 0, 1, 0, 0, 0, 1, 0, 0],
    "procurement": [2, 2, 2, 2, 1, 1, 1, 2, 2, 1],
    "commission":  [4, 4, 4, 4, 4, 3, 3, 4, 4, 4],
}
# [end: lifecycle]


def lifecycle() -> None:
    lines = ["interface register by stage at three gates (IF-001..IF-010):",
             "  gate          " + "".join(f"{s:>11s}" for s in STAGES)]
    for gate, st in GATES.items():
        counts = [st.count(k) for k in range(len(STAGES))]
        lines.append(f"  {gate:12s}  " + "".join(f"{c:11d}" for c in counts))
    late = [f"IF-{k + 1:03d}" for k, v in enumerate(GATES["commission"]) if v < 4]
    lines += ["  rule: every interface 'agreed' before its purchase order and",
              "  'closed' before hand-over; at commissioning still open: "
              + ", ".join(late),
              "  (battery heat and protocol: the two planted mismatches that",
              "  were fixed late, so they are verified last)"]
    emit("j_lifecycle", lines)


if __name__ == "__main__":
    island()
    spares()
    lifecycle()
