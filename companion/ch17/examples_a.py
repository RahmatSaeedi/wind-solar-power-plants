"""Chapter 17, section A - demand and use cases: metrics from interval
data, the duration curve, peaks by resolution, monthly and daily shapes,
diversity of the components, growth, the plant's own loads by class, and
how long a battery carries the critical load.

Run from the project root:   python -m companion.ch17.examples_a
Writes companion/ch17/expected/a_*.txt and diagrams/data/ch17-*.csv.
Synthetic loads A-284.
"""
from __future__ import annotations

import numpy as np

from companion.ch17 import sources as src
from companion.ch17.common import csv, emit
from plantp import demand as dm


def metrics() -> None:
    r = src.regional()
    m = dm.metrics(r["total"])
    hour, dow, month, _ = src.calendar()
    k = m["peak_at"]
    lines = ["regional load, hourly, one year (synthetic, A-284):",
             f"  energy {m['energy'] / 1e3:.1f} GWh; mean {m['mean']:.2f} MW",
             f"  peak {m['peak']:.2f} MW on day {k // 24 + 1} (month {month[k] + 1}) at"
             f" {hour[k]:02d}:00; minimum {m['min']:.2f} MW",
             f"  load factor {m['load_factor']:.3f}",
             f"  peak of 15-minute values {src.regional_15min().max():.2f} MW;"
             f" of their hourly means {dm.peak_by_resolution(src.regional_15min(), 4):.2f} MW",
             "  the peak depends on the averaging interval: the request names",
             "  it, and equipment is rated on the shorter one"]
    emit("a_metrics", lines)
    ldc = dm.duration_curve(r["total"])
    csv("ch17-ldc.csv", "h,p", [(i, f"{ldc[i]:.2f}") for i in range(0, 8760, 20)])


def shapes() -> None:
    r = src.regional()
    hour, dow, month, _ = src.calendar()
    p = r["total"]
    lines = ["monthly energy and peak of the regional load:",
             "  month   GWh     peak MW"]
    rows = []
    for k in range(12):
        sel = month == k
        lines.append(f"  {k + 1:5d}   {p[sel].sum() / 1e3:5.2f}   {p[sel].max():6.2f}")
        rows.append((k + 1, f"{p[sel].sum() / 1e3:.2f}", f"{p[sel].max():.2f}"))
    csv("ch17-monthly.csv", "m,e,peak", rows)
    summer = (month >= 5) & (month <= 7)
    winter = (month <= 1) | (month == 11)
    day = []
    for hh in range(24):
        day.append((hh, f"{p[summer & (hour == hh)].mean():.2f}",
                    f"{p[winter & (hour == hh)].mean():.2f}",
                    f"{p[(dow >= 5) & (hour == hh)].mean():.2f}"))
    csv("ch17-daily.csv", "h,summer,winter,weekend", day)
    lines += ["  summer afternoons carry the peak (cooling); winter mornings add",
              "  heating; weekends lose the industry; the shape says when the",
              "  plant's export meets local demand and when it flows up"]
    emit("a_shapes", lines)


def components() -> None:
    r = src.regional()
    cf, df = dm.diversity([r["town"], r["pump"], r["industry"]])
    lines = ["components of the regional load (peaks do not add):"]
    for k in ("town", "pump", "industry"):
        lines.append(f"  {k:9s} peak {r[k].max():6.2f} MW, energy {r[k].sum() / 1e3:6.1f} GWh")
    lines += [f"  sum of the peaks {sum(r[k].max() for k in ('town', 'pump', 'industry')):.2f} MW;"
              f" peak of the sum {r['total'].max():.2f} MW",
              f"  coincidence factor {cf:.3f}; diversity factor {df:.3f}",
              "  the components peak at different hours: rating each feeder",
              "  for its own peak is right, adding them for the substation is not"]
    emit("a_components", lines)


def growth() -> None:
    r = src.regional()
    lines = ["the regional load in ten years at three growth rates (same shape):",
             "  rate    peak MW   energy GWh   minimum MW"]
    for g in (0.02, 0.035, 0.05):
        p = dm.grow(r["total"], g, 10)
        lines.append(f"  {100 * g:3.1f} %   {p.max():6.2f}     {p.sum() / 1e3:6.1f}       {p.min():6.2f}")
    lines += ["  with one of the two 63 MVA transformers out, the peak (at unity",
              "  power factor) passes 63 MW from about 2 % a year: growth helps",
              "  the plant (more local use, less upward flow) but brings the",
              "  substation's reinforcement closer;"
              ,"  'same shape' is an assumption: cooling and electric cars",
              "  change the shape (A-284)"]
    emit("a_growth", lines)


def plant_classes() -> None:
    pl = src.plant_loads_hourly()
    tot = sum(v for v in pl.values())
    lines = ["Plant P's own loads by class (A-284):",
             "  class            peak kW   energy MWh   share"]
    for k, v in pl.items():
        lines.append(f"  {k:14s}   {1000 * v.max():7.0f}     {v.sum():7.0f}     {100 * v.sum() / tot.sum():4.1f} %")
    lines += [f"  all             {1000 * tot.max():7.0f}     {tot.sum():7.0f}",
              "  critical: must run when the grid is lost (protection, control,",
              "  battery cooling); controllable: may be shifted to hours of",
              "  surplus; interruptible: may be dropped; the list sets the size",
              "  of the auxiliary supply and back-up (chapters 18 and 25)"]
    emit("a_classes", lines)


def resilience() -> None:
    pl = src.plant_loads_hourly()
    crit = float(pl["critical"].max())
    lines = ["how long the S1 battery (20 MW, 40 MWh) can carry the plant's",
             f"  critical load of {1000 * crit:.0f} kW after a loss of the grid:"]
    for soc in (0.9, 0.5, 0.2):
        h = dm.critical_hours(crit, 40.0, 20.0, soc=soc)
        lines.append(f"  starting at {100 * soc:3.0f} % charge: {h:6.0f} h ({h / 24:4.1f} days)")
    lines += ["  the battery is sized for the market, so its reserve for the",
              "  plant is large; but islanding needs a grid-forming inverter,",
              "  protection that works without the grid, and the grid",
              "  operator's rules (chapters 19, 25 and 28): a resilience",
              "  requirement names all of them"]
    emit("a_resilience", lines)


if __name__ == "__main__":
    metrics()
    shapes()
    components()
    growth()
    plant_classes()
    resilience()
