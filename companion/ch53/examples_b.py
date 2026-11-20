"""Chapter 53, lesson B: repair, upgrade or repower - the inverter fleet's
failure trend and support end, a gearbox's remaining life, repowering the
turbines inside the export limit, grid-requirement changes, permits and
downtime of a repowering.

Run from the project root:   python -m companion.ch53.examples_b
Writes companion/ch53/expected/b_*.txt. Teaching values (A-539).
"""
from __future__ import annotations

import numpy as np

from companion.ch15 import sources as s15
from companion.ch53 import sources as src
from companion.ch53.common import emit
from plantp import lifecycle as lc
from plantp import performance as pf


# ------------------------------------------------ 1. inverter fleet: trend and support
def inverters() -> dict:
    inv = src.INVERTER
    yrs = np.arange(13, 13 + len(inv["failures_yr"]))
    n_fail = np.array(inv["failures_yr"]) * inv["units"]
    times = []
    for y, n in zip(yrs, n_fail):                       # spread failures in each year
        times += list(np.linspace(y - 1 + 0.5 / n, y - 0.5 / n, int(round(n))))
    beta = pf.crow_amsaa_beta(np.array(times) - 12, float(yrs[-1] - 12))
    lines = ["PV inverter fleet (10 units): failures a unit-year, years 13-18",
             "  " + " ".join(f"{x:.1f}" for x in inv["failures_yr"]),
             f"  growth slope over years 13-18: {beta:.2f} (above 1: failures thickening)",
             f"  maker's support ends after year {inv['supported_until']}: spares and firmware",
             "  stop while the plant has 7 years to run (ch 52 obsolescence)",
             "  - a fleet that is wearing out AND losing support is a",
             "  replacement candidate, whatever its repair cost today"]
    emit("b_inverters", lines)
    return dict(beta=beta)


# ------------------------------------------------ 2. a gearbox's remaining life
def gearbox() -> dict:
    g = src.GEARBOX
    med = lc.median_remaining(g["hours"], g["k"], g["c"])
    r7 = float(lc.conditional_reliability(g["hours"], 7 * 8760 * 0.93, g["k"], g["c"]))
    lines = [f"main gearboxes: Weibull k {g['k']}, c {g['c']:,.0f} h; each has run "
             f"{g['hours']:,.0f} h",
             f"  median remaining life {med:,.0f} h ({med / 8760 / 0.93:.1f} years of running)",
             f"  chance one survives the 7 years to year 25: {r7:.0%}",
             f"  expected failures in the fleet of 12 by year 25: {12 * (1 - r7):.1f}",
             "  remaining life is a conditional question: an 18-year-old",
             "  gearbox has less left than a new one's mean life suggests"]
    emit("b_gearbox", lines)
    return dict(med=med, r7=r7, fails=12 * (1 - r7))


# ------------------------------------------------ 3. repowering inside the export limit
def repower() -> dict:
    r = src.REPOWER
    y = s15.plant_year()
    wind = np.asarray(y["w_av"], float)
    pv = np.asarray(y["pv_av"], float)
    area = (r["new_rotor"] / r["old_rotor"]) ** 2
    new_wind = np.minimum(wind * area * (1 + r["cp_gain"]), 12 * r["new_mw"])
    lim = r["export_limit"]
    old = np.minimum(wind + pv, lim)
    new = np.minimum(new_wind + pv, lim)
    gain = float(new.sum() - old.sum())
    spilled = float(np.clip(new_wind + pv - lim, 0, None).sum() - np.clip(wind + pv - lim, 0, None).sum())
    lines = [f"repowering the 12 turbines: {r['old_mw']} -> {r['new_mw']} MW, rotor {r['old_rotor']:.0f} -> "
             f"{r['new_rotor']:.0f} m",
             f"  wind energy up by (170/150)^2 x {1 + r['cp_gain']:.2f} = {area * (1 + r['cp_gain']):.2f} "
             "(capped at the new rating)",
             f"  plant energy below the {lim:.0f} MW export limit: +{gain / 1000:.1f} GWh a year;",
             f"  extra energy spilled at the limit: {spilled / 1000:.1f} GWh a year",
             f"  the limit takes {spilled / (gain + spilled):.0%} of the extra wind energy - small",
             "  now, larger if the PV is repowered too; and a repowering is",
             "  a new grid application (the next lesson, ch 17, ch 28)"]
    emit("b_repower", lines)
    return dict(gain=gain, spilled=spilled, factor=area * (1 + r["cp_gain"]))


# ------------------------------------------------ 4. grid requirements that changed
CHANGES = [   # requirement, at COD, now (teaching), plant meets now?
    ("reactive power at full output", "0.95 pf", "0.95 pf plus voltage control", True),
    ("fault ride-through depth", "0.15 pu, 150 ms", "0 pu, 150 ms", False),
    ("frequency response", "none required", "droop 4 %, 10 % headroom", False),
    ("telemetry latency", "4 s", "1 s", True),
    ("cyber requirements", "none stated", "IEC 62443 based, audited", False)]


def grid_changes() -> dict:
    miss = [r for r, a, b, ok in CHANGES if not ok]
    lines = ["grid requirements: at COD and now (teaching; real ones from the operator)"]
    for r, a, b, ok in CHANGES:
        lines += [f"  {r:32s} {'meets' if ok else 'GAP'}", f"     {a} -> {b}"]
    lines += [f"  {len(miss)} gaps: an existing plant usually keeps its connection",
              "  terms, but a repowering is a new application and must meet",
              "  the requirements of its date - the gaps become part of the",
              "  repowering's cost (converters, controls, OT security)"]
    emit("b_grid", lines)
    return dict(gaps=len(miss))


# ------------------------------------------------ 5. downtime and permits of a repowering
def repower_time() -> dict:
    steps = [("permit amendment (teaching)", 14.0, False), ("grid study and agreement", 10.0, False),
             ("procurement of turbines", 12.0, False), ("dismantling, 2 turbines a week", 1.5, True),
             ("foundation adaptation", 2.0, True), ("erection and commissioning", 3.0, True)]
    before = sum(m for _, m, down in steps if not down)
    down = sum(m for _, m, d in steps if d)
    wind_month = float(np.mean(np.asarray(s15.plant_year()["w_av"], float))) * 730
    lines = ["repowering timeline (months, teaching; steps partly overlap in practice)"]
    lines += [f"  {k:34s} {m:5.1f}" + ("  wind farm down" if d else "") for k, m, d in steps]
    lines += [f"  {before:.0f} months before any turbine stops; {down:.1f} months with the farm",
              f"  down in sequence - about {down * wind_month / 1000:.0f} GWh of wind energy lost if",
              "  all stopped together; turbine by turbine it is a fraction,",
              "  and the PV keeps exporting (lesson F)"]
    emit("b_time", lines)
    return dict(before=before, down=down, lost=down * wind_month)


if __name__ == "__main__":
    inverters()
    gearbox()
    repower()
    grid_changes()
    repower_time()
