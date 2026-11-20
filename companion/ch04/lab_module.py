"""Chapter 4 laboratory 2 — PV module temperature from an energy balance, calibrated against
the data-sheet NOCT and compared with the simple NOCT model on the summer subset day.

Run from the project root:   python -m companion.ch04.lab_module
Wind at 2 m is taken from the 60 m speed with the log law (z0 = 0.225 m from a_shear).
Writes companion/ch04/expected/lab_module.txt and diagrams/data/ch04-r-module.csv.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plantp import datapack, numerics as nm, physics as ph  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "expected" / "lab_module.txt"
DATA = HERE.parents[1] / "diagrams" / "data" / "ch04-r-module.csv"


# [start: calibrate]
def calibrate(noct_c=45.0):
    """Find the convection scale that reproduces the data-sheet NOCT."""
    def miss(scale):
        t = ph.module_temperature_balance(800.0, 20.0, 1.0, h_scale=scale)
        return t - noct_c
    return nm.bisection(miss, 0.2, 2.0, tol=1e-6).root


def wind_at_2m(v60, z0=0.225):
    """Log law from 60 m down to 2 m (neutral air)."""
    return v60 * math.log(2.0 / z0) / math.log(60.0 / z0)
# [end: calibrate]


def main() -> None:
    day = datapack.load_hourly("day_summer")
    g = day["ghi_wm2"].to_numpy()
    ta = day["t_air_c"].to_numpy()
    v2 = wind_at_2m(day["ws_60m_ms"].to_numpy())
    raw = ph.module_temperature_balance(800.0, 20.0, 1.0)
    scale = calibrate()
    t_noct = np.asarray(ph.pv_cell_temp_noct(ta, g, 45.0))
    t_bal = np.array([ph.module_temperature_balance(gi, ti, vi, h_scale=scale)
                      for gi, ti, vi in zip(g, ta, v2)])
    k = int(np.argmax(g))

    def weighted(tc):
        return float(np.sum(g * -0.35 * (tc - 25.0)) / np.sum(g))
    lines = ["energy balance, both faces, textbook convection h = 5.7 + 3.8 v (W/m2K):",
             f"  at NOCT conditions (800 W/m2, 20 C, 1 m/s) it gives {raw:.1f} C, not 45 C",
             f"  calibrated convection scale {scale:.3f} (bisection) reproduces 45.0 C",
             f"summer subset day, wind at 2 m from the 60 m speed: noon {v2[k]:.1f} m/s",
             f"  noon cell temperature: NOCT model {t_noct[k]:.1f} C, energy balance "
             f"{t_bal[k]:.1f} C",
             f"  irradiance-weighted power change: NOCT {weighted(t_noct):+.1f} %, "
             f"balance {weighted(t_bal):+.1f} %",
             f"  night: the balance puts the module {ta[2] - t_bal[2]:.1f} K below the air "
             "(radiation to the sky)"]
    for v in (1.0, 4.0):
        lines.append(f"  noon with a steady {v:.0f} m/s wind: "
                     f"{ph.module_temperature_balance(g[k], ta[k], v, h_scale=scale):.1f} C")
    text = "\n".join(lines) + "\n"
    OUT.write_text(text, encoding="utf-8", newline="\n")
    with open(DATA, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("hour,tair,tnoct,tbal\n")
        for h in range(24):
            fh.write(f"{h},{ta[h]:.2f},{t_noct[h]:.2f},{t_bal[h]:.2f}\n")
    print(text)


if __name__ == "__main__":
    main()
