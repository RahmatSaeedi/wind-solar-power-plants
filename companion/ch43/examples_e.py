"""Chapter 43, lesson E: plant integration of the main transformer - fan
control over the data-pack year, the differential protection's spill
current across the tap range, the data the maker must hand to each plant
discipline, and the factory baselines the site checks compare with.

Run from the project root:   python -m companion.ch43.examples_e
Writes companion/ch43/expected/e_*.txt.
Teaching values (A-464); no energised or live-work procedures.
"""
from __future__ import annotations

import numpy as np

from companion.ch43 import sources as src
from companion.ch43.common import emit

M = src.MAIN_B


# ------------------------------------------------ fan control
def fans(on_c: float = 65.0, off_c: float = 55.0, n_fans: int = 8,
         fan_kw: float = 1.1, d_top_r: float = 52.0, r: float = 6.0,
         x: float = 0.8) -> dict[str, float]:
    from companion.ch25.examples_b import unit_load
    from plantp import datapack
    k = unit_load() * M["s_mva"] / M["s_onan_mva"]      # against the ONAN rating
    amb = datapack.load_hourly()["t_air_c"].to_numpy()
    top = amb + d_top_r * ((1 + r * k ** 2) / (1 + r)) ** x
    run = np.zeros_like(top, dtype=bool)
    state = False
    for i, t in enumerate(top):
        if not state and t >= on_c:
            state = True
        elif state and t <= off_c:
            state = False
        run[i] = state
    hours = int(run.sum())
    starts = int(np.sum(run[1:] & ~run[:-1]))
    over = int((k > 1.0).sum())
    lines = [f"fan control of a main transformer on the data-pack year (top oil "
             f"on {on_c:.0f} C,",
             f"  off {off_c:.0f} C; ONAN steady model; teaching)",
             f"  top oil above {on_c:.0f} C or load above the ONAN rating: fans "
             f"run {hours} h, {starts} starts",
             f"  hours above the ONAN rating: {over}; fan energy "
             f"{hours * n_fans * fan_kw / 1000:.1f} MWh a year",
             f"  highest top oil {top.max():.0f} C (hour {int(top.argmax())})",
             "  the band between on and off keeps the fans from hunting; a",
             "  failed fan group is an alarm and, above the ONAN rating, a",
             "  load limit sent to the plant controller (ch 20, ch 23)"]
    emit("e_fans", lines)
    return dict(hours=hours, starts=starts, over=over)


# ------------------------------------------------ differential spill with taps
def spill(pickup: float = 0.2, slope: float = 0.3) -> dict[float, float]:
    lines = ["differential protection matched at the principal tap: spill "
             "current",
             f"  when the tap moves (pickup {pickup} pu, slope {slope:.0%}; ch 26)",
             "  tap %    through 1 pu   through 4 pu   threshold at 4 pu"]
    out = {}
    for tap in (-10.0, -5.0, 0.0, 5.0, 10.0):
        s1 = abs(1 - 1 / (1 + tap / 100))
        s4 = 4 * s1
        thr = pickup + slope * 4
        out[tap] = s1
        lines.append(f"  {tap:+6.1f}   {s1:12.3f}   {s4:12.3f}   {thr:17.2f}")
    lines += ["  at the end taps the relay sees about a tenth of the through",
              "  current as 'differential': the bias slope is set above it,",
              "  and the CT data (ratio, class, knee point) from the maker's",
              "  CT schedule feed the setting calculation"]
    emit("e_spill", lines)
    return out


# ------------------------------------------------ data the plant needs
DATA = [   # discipline, maker data, status at FAT
    ("civil (ch 29, 30)", "mass, centre of gravity, anchors", "given"),
    ("fire, bund (ch 25, 32)", "oil volume, fire load", "given"),
    ("HV and MV connections (ch 24)", "bushing terminals, allowed loads", "given"),
    ("protection (ch 26)", "CT ratio, class, knee point", "partial"),
    ("earthing (ch 26)", "earthing points, neutral rating", "given"),
    ("control, SCADA (ch 34, 35)", "signals, cooling logic, OLTC", "given"),
    ("logistics (ch 31)", "shipping dims, mass, lift points", "partial"),
    ("O&M (ch 51, 52)", "manuals, spares, FRA/DGA baselines", "partial"),
]


def data() -> dict[str, int]:
    lines = ["maker data each plant discipline needs from the transformer",
             "  discipline                     status    data"]
    count = {}
    for disc, what, st in DATA:
        count[st] = count.get(st, 0) + 1
        lines.append(f"  {disc:30s} {st:8s}  {what}")
    lines += [f"  {count.get('partial', 0)} of {len(DATA)} partial: the CT knee "
              "points, the shipping",
              "  dimensions and the LV frequency-response file - each one",
              "  blocks a design or a site check downstream"]
    emit("e_data", lines)
    return count


# ------------------------------------------------ factory baselines for the site
BASE = [   # site check, factory baseline, compare, available
    ("ratio at every tap", "factory ratio test", "same within tolerance", True),
    ("winding resistance", "factory values", "same after correction", True),
    ("insulation resistance, PI", "factory values", "trend, not absolute", True),
    ("frequency response HV", "factory FRA file", "trace comparison", True),
    ("frequency response LV", "factory FRA file", "trace comparison", False),
    ("dissolved gases", "after-heat-run DGA", "baseline for the trend", True),
    ("oil water and breakdown", "filling record", "after site filling", True),
    ("impact during transport", "recorder log", "limits in the contract", False),
]


def baselines() -> dict[str, int]:
    have = sum(1 for b in BASE if b[3])
    lines = ["site checks before energising and the factory record each compares",
             "  with (purpose only; the procedures are the maker's and the",
             "  commissioning engineer's)",
             "  site check                   baseline                   available"]
    for chk, base, _, ok in BASE:
        lines.append(f"  {chk:28s} {base:26s} {'yes' if ok else 'NO'}")
    lines += [f"  {have} of {len(BASE)} baselines exist: without the LV file and the",
              "  recorder log, a winding moved in transport could go unseen -",
              "  the two open items of lab D are site risks, not paperwork"]
    emit("e_baselines", lines)
    return dict(have=have, total=len(BASE))


if __name__ == "__main__":
    fans()
    spill()
    data()
    baselines()
