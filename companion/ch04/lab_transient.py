"""Chapter 4 laboratory 3 — busbar temperature through its hottest day: hour-by-hour
steady state against a thermal transient solved with RK4.

Run from the project root:   python -m companion.ch04.lab_transient
The 33 kV main busbar (single copper bar 80 x 10 mm, int_busbar) carries the whole plant
export; the room is 15 K above the outdoor air (A-061). Writes
companion/ch04/expected/lab_transient.txt and diagrams/data/ch04-lab3.csv.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plantp import datapack, numerics as nm, physics as ph, screening as sc  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "expected" / "lab_transient.txt"
DATA = HERE.parents[1] / "diagrams" / "data" / "ch04-lab3.csv"

A_BAR, PERIM, H = 8e-4, 0.18, 10.0
R20, ALPHA = 1.72e-8 / A_BAR, 0.00393
C_BAR = 8960 * 385 * A_BAR                       # J/(K m)


# [start: transient]
def make_rhs(current, t_room):
    """dT/dt of the bar; current and room temperature change each hour."""
    def rhs(t, temp):
        h = min(int(t // 3600), 23)
        heat = current[h] ** 2 * R20 * (1 + ALPHA * (temp - 20))
        cool = H * PERIM * (temp - t_room[h])
        return (heat - cool) / C_BAR
    return rhs


def simulate(current, t_room, dt=60.0):
    """Start from the steady state of hour 0, integrate 24 h with RK4."""
    t0, _ = ph.conductor_temperature(current[0], R20, ALPHA, H, PERIM,
                                     t_room[0])
    return nm.rk4(make_rhs(current, t_room), t0, 0.0, 86400.0, dt)
# [end: transient]


def main() -> None:
    year = datapack.load_hourly()
    curve = datapack.load_power_curve()
    vs, pk = curve["wind_speed_ms"].to_numpy(), curve["power_kw"].to_numpy()
    pv = np.asarray(sc.pv_ac_power_mw(year["ghi_wm2"], 60, 50))
    wind = np.asarray(sc.wind_power_mw(year["ws_100m_ms"].to_numpy(), vs, pk, 12))
    i_year = np.minimum(pv + wind, 100.0) * 1e6 / (math.sqrt(3) * 33e3 * 0.95)
    temps = year["t_air_c"].to_numpy() + 15.0
    steady_year = np.array([ph.conductor_temperature(a, R20, ALPHA, H, PERIM, b)[0]
                            for a, b in zip(i_year, temps)])
    d = int(np.argmax(steady_year)) // 24              # day of the hottest hour
    i, t_room = i_year[24 * d:24 * d + 24], temps[24 * d:24 * d + 24]
    steady = np.array([ph.conductor_temperature(a, R20, ALPHA, H, PERIM, b)[0]
                       for a, b in zip(i, t_room)])
    t, y = simulate(i, t_room)
    t, y = np.asarray(t), np.asarray(y, dtype=float)
    tau = C_BAR / (H * PERIM)
    k_ss, k_tr = int(np.argmax(steady)), int(np.argmax(y))
    lines = [f"day {d + 1} of the year (holds the hottest steady-state hour); main busbar",
             f"  Cu 80 x 10 mm, thermal time constant {tau / 60:.1f} min",
             f"  peak current {i.max():.0f} A in hour {int(np.argmax(i))}",
             f"  hour-by-hour steady state: maximum {steady.max():.1f} C in hour {k_ss}",
             f"  transient (RK4, 60 s steps): maximum {y.max():.1f} C at "
             f"{t[k_tr] / 3600:.2f} h",
             f"  the thermal mass shaves {steady.max() - y.max():.1f} K off the peak and "
             "delays it",
             f"  hours with steady state above 90 C: {int((steady > 90).sum())}; "
             f"minutes of transient above 90 C: {int((y > 90).sum())}"]
    text = "\n".join(lines) + "\n"
    OUT.write_text(text, encoding="utf-8", newline="\n")
    with open(DATA, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("h,steady,transient\n")
        for k in range(0, len(t), 15):
            hh = min(int(t[k] // 3600), 23)
            fh.write(f"{t[k] / 3600:.3f},{steady[hh]:.2f},{y[k]:.2f}\n")
    print(text)


if __name__ == "__main__":
    main()
