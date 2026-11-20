"""Chapter 4, fifth part — thermography and emissivity, air insulation at altitude, sunlight
on cables, ultraviolet dose from the data pack, and friction in slip-critical joints.

Run from the project root:   python -m companion.ch04.examples_last
Writes companion/ch04/expected/u_*.txt and diagrams/data/ch04-u-*.csv.
Values marked "assumed" (A-080 .. A-083) are teaching values, not a design.
"""
from __future__ import annotations

import numpy as np

from companion.ch04.common import csv, emit
from plantp import datapack, physics as ph


def thermography() -> None:
    lines = [f"peak emission wavelength (Wien): sun {ph.wien_peak_um(5778):.2f} um, "
             f"a 80 C joint {ph.wien_peak_um(353.15):.1f} um (long-wave infrared)",
             "joint truly at 80 C in a 30 C room; camera emissivity set to 0.95 (A-080):"]
    for name, eps in (("black tape or paint", 0.95), ("oxidised copper", 0.60),
                      ("dull aluminium", 0.20), ("bright copper", 0.05)):
        lines.append(f"  {name:20s} eps {eps:.2f}: camera reads "
                     f"{ph.apparent_temperature(80, eps, 0.95, 30):5.1f} C")
    lines.append("  shiny metal reflects the room and hides its own heat: survey on painted or")
    lines.append("    taped spots, or set the emissivity, and record the load at the time")
    emit("u_thermography", lines)
    eps = np.linspace(0.05, 1.0, 39)
    csv("ch04-u-thermo.csv", "eps,t", [(f"{e:.3f}", f"{ph.apparent_temperature(80, e, 0.95, 30):.2f}")
                                       for e in eps])


def air_insulation() -> None:
    hourly = datapack.load_hourly()
    p, t = hourly["p_hpa"].to_numpy(), hourly["t_air_c"].to_numpy()
    delta = np.array([ph.relative_air_density(a, b) for a, b in zip(p, t)])
    emit("u_altitude", [
        "relative air density delta = (p / 1013.25) (293.15 / T) at the Plant P station:",
        f"  mean {delta.mean():.3f}, lowest {delta.min():.3f} (hot summer afternoon)",
        f"  first order, the flashover voltage of an air gap scales with delta: about "
        f"{100 * (1 - delta.min()):.0f} % lower",
        "  equipment rated for sea level is checked, and clearances corrected, for the",
        "    site altitude by the methods of the governing standards (chapters 24 and 25)",
    ])


def cable_in_sun() -> None:
    d, alpha_s, g = 0.050, 0.6, 1000.0                       # A-081
    q_sun = alpha_s * g * d
    w_joule = 572.0 ** 2 * 0.125e-3
    emit("u_cablesun", [
        "cable in free air, diameter 50 mm, sheath absorptance 0.6, sun 1000 W/m2 (A-081)",
        f"  absorbed sunlight alpha G D = {q_sun:.0f} W/m (projected width = diameter)",
        f"  Joule loss of the feeder cable at peak current {w_joule:.0f} W/m",
        f"  the sun adds {100 * q_sun / w_joule:.0f} % of the conductor's own heat: cables in",
        "    the sun are derated or shaded; a light-coloured sheath or a sun shield helps",
    ])


def uv_dose() -> None:
    hourly = datapack.load_hourly()
    ghi = hourly["ghi_wm2"].to_numpy()
    kwh = ghi.sum() / 1000.0
    uv_frac, chamber = 0.05, 60.0                            # A-082
    uv_mj = kwh * uv_frac * 3.6
    hours = kwh * uv_frac * 1000.0 / chamber
    emit("u_uv", [
        f"data pack: global horizontal irradiation {kwh:,.0f} kWh/m2 per year",
        f"  ultraviolet share about 5 % (assumed, A-082): {kwh * uv_frac:.0f} kWh/m2 = "
        f"{uv_mj:.0f} MJ/m2 per year",
        f"  a UV chamber at 60 W/m2 delivers one site-year in {hours:,.0f} h "
        f"({hours / 24:.0f} days)",
        f"  25 years outdoors = {25 * hours / 24 / 365:.1f} years of chamber time: tests",
        "    accelerate dose but not every ageing path (heat, moisture, cycling) at once",
    ])


def friction_joint() -> None:
    mu, n_b, fp = 0.35, 8, 475e3                            # A-083
    for_slip = mu * n_b * fp
    emit("u_slip", [
        "slip-critical joint: 8 preloaded M36 bolts, faying-surface friction 0.35 (A-083)",
        f"  slip resistance mu n F_p = {for_slip / 1e3:.0f} kN (one friction plane)",
        f"  if the surfaces are painted (friction 0.2): {0.2 * n_b * fp / 1e3:.0f} kN",
        f"  if a quarter of the preload relaxes: {mu * n_b * 0.75 * fp / 1e3:.0f} kN",
        "  the joint relies on surface preparation and preload, both recorded at",
        "    erection; once it slips, the bolts carry the load in bearing and wear the holes",
    ])


def main() -> None:
    thermography()
    air_insulation()
    cable_in_sun()
    uv_dose()
    friction_joint()


if __name__ == "__main__":
    main()
