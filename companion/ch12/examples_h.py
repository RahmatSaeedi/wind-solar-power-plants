"""Chapter 12, last lessons - the monthly quality report of the faulty
station year, clear-sky day detection, and east-west against south-facing
orientation.

Run from the project root:   python -m companion.ch12.examples_h
Writes companion/ch12/expected/h_*.txt and diagrams/data/ch12-*.csv.
Data pack 1.1.0 (S0); faulty year A-246.
"""
from __future__ import annotations

import numpy as np

from companion.ch12 import lab_d, sources
from companion.ch12.common import csv, emit
from plantp import irradiance as ir, pvcell as pc, solar

MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def monthly_report(month: int = 2) -> None:
    """The QC report of one month (March: the clock error begins)."""
    p = sources.pack()
    pr = sources.provider()
    g, faults, soil = lab_d.faulty_year()
    sel = p["month"] == month
    cs = ir.clear_sky_haurwitz(p["cz"])
    x = g[sel]
    day_h = sel & (p["cz"] > 0.087)
    miss = np.isnan(x).sum()
    spike = (np.nan_to_num(x) > 1.25 * cs.max()).sum()
    lag = ir.best_lag(np.nan_to_num(x), cs[sel], 2)
    ratio = np.nansum(g[day_h]) / pr["ghi"][day_h].sum()
    lines = [f"monthly quality report, station GHI, {MONTHS[month]} 2023 (A-246):",
             f"  records {sel.sum()}, missing {miss}, recovery"
             f" {100 * (1 - miss / sel.sum()):.1f} %",
             f"  spikes above 1.25 x clear-sky maximum: {spike}",
             f"  clock test against clear sky: shift {lag} h -> action: logger",
             "    time zone checked, data shifted back, flag 'time corrected'",
             f"  ratio to the provider series: {ratio:.3f} (annual mean 0.995)",
             "  dome cleaning log: weekly; sawtooth soiling up to 2 % (flag",
             "    'soiling corrected', factor from the cleaning dates)",
             "  closure: not tested (GHI only in this record)",
             "  verdict: accepted after correction; time error opened as",
             "    an incident with its cause and the date it was fixed"]
    emit("h_report", lines)


# [start: clearsky]
def clear_days(ghi, cz, days: int = 365, kc_min: float = 0.95,
               var_max: float = 0.03, cz_min: float = 0.4):
    """Clear days: mean clear-sky index above kc_min and little
    hour-to-hour change of the index while the sun is above about 24 deg."""
    cs = ir.clear_sky_haurwitz(cz)
    out = []
    for d in range(days):
        s = slice(d * 24, d * 24 + 24)
        up = cz[s] > cz_min
        if up.sum() < 4:
            continue
        kc = ghi[s][up] / cs[s][up]
        if np.mean(kc) > kc_min and np.std(np.diff(kc)) < var_max:
            out.append(d)
    return out
# [end: clearsky]


def clear_sky_days() -> None:
    p = sources.pack()
    days = clear_days(p["ghi"], p["cz"])
    month_of = np.array([int(p["month"][d * 24]) for d in days])
    counts = [int(np.sum(month_of == m)) for m in range(12)]
    lines = ["clear days in the station year (index > 0.95, steady, A-249):",
             "  " + "  ".join(f"{MONTHS[m]} {counts[m]:2d}" for m in range(6)),
             "  " + "  ".join(f"{MONTHS[m]} {counts[m]:2d}" for m in range(6, 12)),
             f"  {len(days)} clear days in the year",
             "  clear days check the clock (symmetry), the level and the",
             "  cosine response (morning against afternoon at the same sun",
             "  height), and the station's ratio to a clear-sky model"]
    emit("h_clear", lines)
    csv("ch12-cleardays.csv", "month,days", [(m + 1, counts[m]) for m in range(12)])


def east_west() -> None:
    """East-west tables at 10 deg against south-facing 25 deg tables
    (Hay-Davies; no inter-row shading; per m2 of module)."""
    p = sources.pack()
    idx = np.arange(8760)
    n, hour = idx // 24 + 1, idx % 24
    res = {}
    for name, tilt, az in (("south 25", 25.0, 180.0), ("east 10", 10.0, 90.0),
                           ("west 10", 10.0, 270.0)):
        ci = np.zeros(8760)
        czs = np.zeros(8760)
        for s in (np.arange(6) + 0.5) / 6:
            el, a = solar.sun_position(sources.LAT, n, solar.solar_time(hour + s, n))
            up = el > 0
            ci += np.where(up, np.clip(solar.incidence_cos(el, a, tilt, az), 0, None), 0)
            czs += np.where(up, np.sin(np.radians(el)), 0)
        b, sk, g = pc.poa_hay_davies(p["ghi"], p["dni"], p["dhi"], ci / 6, czs / 6,
                                     p["g0n"], tilt)
        res[name] = b + sk + g
    ew = 0.5 * (res["east 10"] + res["west 10"])
    s = res["south 25"]
    prof = [(h, f"{s[p['hour'] == h].mean():.1f}", f"{ew[p['hour'] == h].mean():.1f}")
            for h in range(24)]
    csv("ch12-eastwest.csv", "hour,south,ew", prof)
    lines = ["east-west tables at 10 deg against south-facing 25 deg (per m2):",
             f"  annual POA: south {s.sum() / 1e3:,.0f}, east-west"
             f" {ew.sum() / 1e3:,.0f} kWh/m2 ({100 * (ew.sum() / s.sum() - 1):+.1f} %)",
             f"  highest hourly mean: south {max(float(r[1]) for r in prof):.0f},"
             f" east-west {max(float(r[2]) for r in prof):.0f} W/m2",
             "  east-west gives less per module but a flatter day (less",
             "  clipping, a better fit to a morning or evening peak) and more",
             "  modules per hectare: a resource question and a land question",
             "  (chapters 14 and 18)"]
    emit("h_eastwest", lines)


if __name__ == "__main__":
    monthly_report()
    clear_sky_days()
    east_west()
