"""Chapter 13, section B - campaign design and data quality: lidar against
the mast, how fast a redundant sensor reveals a fault, icing hours, and
the length of a campaign against the uncertainty of its mean.

Run from the project root:   python -m companion.ch13.examples_b
Writes companion/ch13/expected/b_*.txt.
Synthetic data A-250 .. A-252.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch13 import sources
from companion.ch13.common import emit
from plantp import irradiance as ir, windres as wr


def lidar_vs_mast() -> None:
    m = sources.mast_year()
    li = sources.lidar()
    lg = m["logged"]
    ok = ~np.isnan(lg["v100"]) & ~m["iced"] & ~np.isnan(li[100]) & (lg["v100"] > 4)
    x, y = lg["v100"][ok], li[100][ok]
    slope0 = float(np.sum(x * y) / np.sum(x * x))
    r = float(np.corrcoef(x, y)[0, 1])
    a = wr.fit_shear([60, 80, 100], [m["true"]["v60"].mean(), m["true"]["v80"].mean(),
                                     m["true"]["v100"].mean()])
    ok150 = ~np.isnan(li[150]) & ~np.isnan(lg["v100"]) & ~m["iced"]
    ext = lg["v100"][ok150] * 1.5 ** a
    lines = ["lidar against the mast at 100 m (A-252):",
             f"  records compared {ok.sum():,} (both valid, above 4 m/s)",
             f"  slope through the origin {slope0:.4f}; r^2 {r ** 2:.4f};"
             f" MBE {ir.mbe(y, x):+.3f} m/s",
             f"  lidar recovery {100 * (1 - li['lost'].mean()):.1f} %",
             f"  at 150 m: lidar {np.mean(li[150][ok150]):.3f} m/s; mast extrapolated"
             f" with one shear {np.mean(ext):.3f} m/s",
             f"    ({100 * (np.mean(ext) / np.mean(li[150][ok150]) - 1):+.1f} %)",
             "  a lidar checked against a mast at one height can then carry the",
             "  measurement to heights the mast does not reach; its own",
             "  calibration (a verification against a reference mast) is part",
             "  of the evidence"]
    emit("b_lidar", lines)


def redundancy() -> None:
    m = sources.mast_year()
    lg = m["logged"]
    ok = (~np.isnan(lg["v100"]) & ~m["iced"] & ~m["shadow"] & (lg["v100"] > 4))
    ratio = np.where(ok, lg["v80"] / lg["v100"], np.nan)
    week = np.arange(len(ratio)) // (6 * 24 * 7)
    wk = np.array([np.nanmean(ratio[week == k]) for k in range(52)])
    base = wk[:20]
    mu, sd = np.nanmean(base), np.nanstd(base, ddof=1)
    alarm = [k for k in range(26, 52) if wk[k] < mu - 2 * sd and wk[k - 1] < mu - 2 * sd]
    lines = ["a redundant height finds the 80 m bearing wear (weekly ratio 80/100):",
             f"  reference weeks 1-20: mean {mu:.4f}, sd {sd:.4f}",
             "  wear starts in week 26 (July); two weeks in a row below",
             f"    mean - 2 sd first in week {alarm[0] + 1 if alarm else 'none'}",
             "  without a second sensor nearby, the same loss would look like",
             "  a calm summer; with it, the fault is a few weeks old when found"]
    emit("b_redundancy", lines)


def icing() -> None:
    m = sources.mast_year()
    t = m["true"]
    cold = t["t"] < 1.0
    lines = ["icing exposure of the mast year:",
             f"  ten-minute records below +1 C: {cold.sum():,}"
             f" ({100 * cold.mean():.1f} % of the year)",
             f"  injected icing events: {m['iced'].sum()} records (6 x 8 h)",
             "  detection by 'almost no variability while cold' finds the",
             "  start of each event; the end is missed when the air warms",
             "  before the ice melts (lab D); heated cups and vanes and a",
             "  second, differently heated sensor make the gaps smaller"]
    emit("b_icing", lines)


def campaign_length() -> None:
    """How the uncertainty of the mean falls with campaign length (monthly
    means of the synthetic year, assumed independent: a teaching bound)."""
    t = sources.mast_year()["true"]
    month = t["day"] * 12 // 365
    mm = np.array([t["v100"][month == k].mean() for k in range(12)])
    sd = mm.std(ddof=1) / mm.mean()
    lines = ["campaign length and the uncertainty of the mean wind speed:",
             f"  monthly means vary by {100 * sd:.1f} % (sd, synthetic year)",
             "  months   relative standard error (if months were independent)"]
    for n in (3, 6, 12, 24):
        lines.append(f"  {n:4d}     {100 * sd / math.sqrt(n):5.1f} %")
    lines += ["  a short campaign also misses the seasons: twelve months is the",
              "  usual minimum, and the long-term correction (section C) carries",
              "  the year to the decades the project needs"]
    emit("b_length", lines)


if __name__ == "__main__":
    lidar_vs_mast()
    redundancy()
    icing()
    campaign_length()
