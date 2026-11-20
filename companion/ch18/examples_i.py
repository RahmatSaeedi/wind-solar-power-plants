"""Chapter 18, last architecture lessons: the plant's data network sized
from the product breakdown (points, update rates, data a day), water
treatment by reverse osmosis for cleaning water (feed, brine, permit),
the option value of preparing a first stage for an extension, and what
the architecture loses without the battery (S0 against S1).

Run from the project root:   python -m companion.ch18.examples_i
Writes companion/ch18/expected/i2_*.txt.
Teaching values A-286 (technical) and A-287 (costs).
"""
from __future__ import annotations

from companion.ch18 import lab_d, sources as src
from companion.ch18.common import emit

# [start: points]
POINTS = {   # device: (count, points each, seconds between samples)
    "wind turbine": (12, 400, 1), "PV inverter": (10, 200, 1),
    "combiner box": (210, 25, 10), "battery container": (8, 400, 1),
    "BESS inverter": (4, 150, 1), "33 kV feeder bay": (14, 60, 1),
    "132 kV bay and meters": (2, 150, 1), "weather station": (3, 30, 1),
    "water and auxiliaries": (1, 80, 10),
}
# [end: points]


def network() -> None:
    lines = ["plant data points and the data they make (teaching, A-286):",
             "  device                   count  points   every s   samples/day"]
    tot_p = tot_s = 0
    for name, (n, pts, dt) in POINTS.items():
        s = n * pts * 86400 // dt
        tot_p, tot_s = tot_p + n * pts, tot_s + s
        lines.append(f"  {name:23s} {n:6d} {n * pts:7,d}   {dt:6d}   {s:13,d}")
    gb = tot_s * 16 / 1e9                        # 8 B value + 8 B time stamp
    lines += [f"  total                          {tot_p:7,d}             {tot_s:13,d}",
              f"  stored raw (16 bytes a sample): {gb:.0f} GB a day, {gb * 365 / 1e3:.1f} TB a year",
              "  historians store changes only and compress, often ten",
              "  times or more; the network carries the 1 s stream: ring",
              "  topology along the collector trenches, separate zones for",
              "  control, monitoring and remote access (chapters 34-36)"]
    emit("i2_network", lines)


def treatment() -> None:
    """Reverse osmosis for cleaning water at 70 % recovery (teaching)."""
    d = lab_d.demands()
    clean = float(d["cleaning"].sum())
    rec = 0.70
    feed = clean / rec
    brine = feed - clean
    other = float(d["sanitation"].sum() + d["bess_makeup"].sum())
    lines = ["treating cleaning water by reverse osmosis (teaching, 70 %):",
             f"  cleaning water needed       {clean:7,.0f} m3/yr",
             f"  feed from the well          {feed:7,.0f} m3/yr",
             f"  brine to dispose of         {brine:7,.0f} m3/yr",
             f"  well abstraction with the other uses {feed + other:7,.0f} m3/yr",
             f"    (against {other + clean:,.0f} m3/yr untreated)",
             "  treatment adds an interface on each side: the permit covers",
             "  the feed, not the product, and the brine needs a disposal",
             "  route the environmental permit accepts (chapter 33)"]
    emit("i2_treatment", lines)


def option_value() -> None:
    """Prepare now (spare bay, transformer space, ducts) or retrofit."""
    now = 400.0                          # k u, first-stage preparation (A-287)
    later = 1500.0                       # k u, retrofit without preparation
    from companion.ch15 import sources as s15
    mean = float(s15.plant_year()["poc"].clip(0, 100).mean())
    outage_mwh = 3 * 24 * mean           # three days of mean output
    later_tot = later + outage_mwh * src.COST["price"] / 1e3
    p_even = now / later_tot
    lines = ["preparing the first stage for an extension (teaching, A-287):",
             f"  prepare now: {now:,.0f} k u; retrofit later: {later:,.0f} k u plus three",
             f"    days of outage ({outage_mwh:,.0f} MWh, {outage_mwh * 50 / 1e3:,.0f} k u):"
             f" {later_tot:,.0f} k u",
             f"  break-even chance of the extension: {100 * p_even:.0f} %",
             "  (no discounting; a later retrofit costs less in today's",
             "  money, which raises the break-even chance)",
             "  if the owner rates the extension more likely than that,",
             "  preparing pays; the preparation is also an option on a",
             "  higher export limit or a larger battery"]
    emit("i2_option", lines)


def s0_s1() -> None:
    import math
    from companion.ch18 import examples_g as eg, examples_h as eh
    from plantp import demand as dm
    need = 100.0 * math.tan(math.acos(0.95)) + 18.6        # h_reactive
    give_s1, give_s0 = 0.33 * 60 + 0.30 * 50 + 20.0, 0.33 * 60 + 0.30 * 50
    pairs_s0 = sum(1 for (i, j) in eg.LINKS if 2 not in (i, j))
    hours = dm.critical_hours(0.2, 40, 20, 0.5)
    back = eh.recapture(20.0, 100.0)
    lines = ["what the architecture loses without the battery (S0):",
             "  item                         S1 (battery)       S0",
             "  33 kV bays for storage       2                  0",
             f"  reactive margin at full P    {give_s1 - need:+5.1f} Mvar"
             f"         {give_s0 - need:+5.1f} Mvar",
             f"  recapture of curtailment     {back:,.0f} MWh/yr         0",
             f"  critical-load back-up        battery, ~{hours:.0f} h     UPS only",
             f"  interfaces (system pairs)    {len(eg.LINKS)}                 {pairs_s0}",
             "  water for chiller make-up    180 m3/yr          0",
             "  without the battery a compensator becomes likely and the",
             "  island for critical loads needs its own source"]
    emit("i2_s0s1", lines)


if __name__ == "__main__":
    network()
    treatment()
    option_value()
    s0_s1()
