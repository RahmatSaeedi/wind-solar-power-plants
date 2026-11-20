"""Chapter 27 - expansion round 14: the filter's tuning as a statistical
budget - capacitor and reactor tolerances, temperature and ageing - with
and without setting the reactor tap on site after the capacitors are
measured.

Run from the project root:   python -m companion.ch27.examples_ad
Writes companion/ch27/expected/ad_tuning.txt. Teaching tolerances (A-340).
"""
from __future__ import annotations

import numpy as np

from companion.ch27 import sources as src
from companion.ch27.common import emit


# [start: tuning]
def tuned_orders(n: int, tap_on_site: bool, seed: int = 290) -> np.ndarray:
    """Tuned order h = h0 / sqrt(C L / C0 L0) for n sampled filters."""
    rng = np.random.default_rng(seed)
    h0 = src.FILTER["h_tune"]
    tol = rng.uniform(-0.05, 0.05, n)              # capacitor tolerance
    temp = rng.uniform(-10, 50, n)                 # capacitor temperature C
    age = rng.uniform(-0.01, 0.0, n)               # ageing over the life
    d_c = tol - 0.0003 * (temp - 20) + age         # -0.03 % per K (teaching)
    if tap_on_site:                                # tap set new, at 20 C:
        d_l = -tol + rng.uniform(-0.01, 0.01, n)   # cancels the tolerance
    else:                                          # but not temperature
        d_l = rng.uniform(-0.03, 0.03, n)          # or ageing
    return h0 / np.sqrt((1 + d_c) * (1 + d_l))
# [end: tuning]


def tuning() -> None:
    lines = ["the filter's tuned order as a statistical budget (10,000 sampled",
             "  filters; C +/- 5 %, L +/- 3 %, -0.03 %/K over -10..50 C, ageing -1 %)",
             "  case                        mean h   99th pct   share above 4.85"]
    for name, tap in (("factory tolerances only", False), ("reactor tap set on site", True)):
        h = tuned_orders(10000, tap)
        lines.append(f"  {name:26s}  {h.mean():6.2f}   {np.percentile(h, 99):8.2f}"
                     f"   {np.mean(h > 4.85):16.1%}")
    lines += ["  with factory tolerances alone about one filter in twenty",
              "  sits closer to the 5th than 4.85 at some time; setting",
              "  the reactor tap after measuring the installed capacitors",
              "  leaves only temperature, ageing and the tap step - the",
              "  margin from 4.7 to 5 is a budget, spent by each of these"]
    emit("ad_tuning", lines)


if __name__ == "__main__":
    tuning()
