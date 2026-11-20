"""Chapter 30, lesson A: loads and structural response - the load path
and the masses, wind with height and the tower's own drag in the 50-year
storm, vortex shedding of a tower standing without its nacelle, seismic
base shear of the turbine and the transformer, snow and heat on a PV
table, and a teaching load combination for overturning.

Run from the project root:   python -m companion.ch30.examples_a
Writes companion/ch30/expected/a_*.txt and diagrams/data/ch30-*.csv.
Teaching values (A-356 .. A-361); never a design.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch30 import sources as src
from companion.ch30.common import csv, emit
from plantp import datapack
from plantp import structures as st
from plantp import wind as w

G = 9.81


def masses() -> None:
    f = src.FOUNDATION
    conc = f["concrete_m3"] * f["gamma_c"] / 1e3
    back = f["backfill_m3"] * f["gamma_b"] / 1e3
    above = (src.TOP_T + src.TOWER_T) * G / 1e3
    lines = ["the load path of one turbine, top to ground (weights in MN)",
             f"  {'rotor and nacelle ' + format(src.TOP_T, '.0f') + ' t':28s} {src.TOP_T * G / 1e3:6.2f}",
             f"  {'steel tower ' + format(src.TOWER_T, '.0f') + ' t':28s} {src.TOWER_T * G / 1e3:6.2f}",
             f"  {'concrete ' + format(f['concrete_m3'], '.0f') + ' m3':28s} {conc:6.2f}",
             f"  {'backfill ' + format(f['backfill_m3'], '.0f') + ' m3':28s} {back:6.2f}",
             f"  {'total on the ground':28s} {above + conc + back:6.2f}",
             "  tower-base loads (characteristic, teaching A-356):"]
    for name, ld in src.LOADS.items():
        lines.append(f"    {name:30s} M {ld['m_mnm']:6.1f} MN m   H {ld['h_mn']:4.2f} MN")
    lines += ["  each load passes rotor -> nacelle -> yaw bearing -> tower",
              "  flanges -> anchor cage -> concrete -> soil; every joint on",
              "  that path is checked for strength, fatigue and stiffness",
              "  - a chain fails at its weakest link, not on average"]
    emit("a_masses", lines)


def tower_drag() -> None:
    v10 = src.SITE["gust50_10m"]
    rho = src.SITE["rho"]
    z = np.linspace(1, src.HUB, 100)
    d = np.interp(z, [0, src.HUB], [4.5, 3.0])
    v = st.wind_profile(v10, 10.0, z, 0.11)
    q = st.dynamic_pressure(v, rho)
    dz = z[1] - z[0]
    force = np.sum(st.drag_force(q, 0.6, d * dz))
    moment = np.sum(st.drag_force(q, 0.6, d * dz) * z)
    csv("ch30-wind.csv", "z,v,q", [(f"{a:.0f}", f"{b:.1f}", f"{c:.0f}") for a, b, c in
                                    zip(z[::5], v[::5], q[::5])])
    lines = ["the 50-year gust with height and the tower's own drag (teaching)",
             f"  gust at 10 m {v10:.1f} m/s, power law 0.11, air {rho} kg/m3",
             f"  gust at hub {st.wind_profile(v10, 10, src.HUB, 0.11):.1f} m/s,"
             f" pressure {st.dynamic_pressure(st.wind_profile(v10, 10, src.HUB, 0.11), rho):,.0f} Pa",
             f"  tower drag {force / 1e3:,.0f} kN, base moment {moment / 1e6:.1f} MN m (Cd 0.6)",
             f"  against the parked extreme of A-356: {src.LOADS['extreme (parked, 50-yr gust)']['m_mnm']:.0f}"
             " MN m",
             f"  in the storm the tower's own drag adds about"
             f" {100 * moment / 1e6 / src.LOADS['extreme (parked, 50-yr gust)']['m_mnm']:.0f} % to the base",
             "  moment: the turbine maker's load set includes it, and a",
             "  site gust above the turbine's class is a question for",
             "  the maker (site suitability, ch 11)"]
    emit("a_drag", lines)


def vortex() -> None:
    i_eq = w.tube_inertia(4.4, 0.031)
    mpm = math.pi * 4.4 * 0.031 * src.STEEL["rho"]
    f_bare = w.tower_frequency(src.STEEL["e"], i_eq, mpm, src.HUB, 0.0)
    f_top = w.tower_frequency(src.STEEL["e"], i_eq, mpm, src.HUB, src.TOP_T * 1e3)
    v_cr = st.vortex_speed(f_bare, 3.0)
    hub = datapack.load_hourly()["ws_100m_ms"].to_numpy()
    band = int(((hub > 0.85 * v_cr) & (hub < 1.15 * v_cr)).sum())
    counts, edges = np.histogram(hub, bins=np.arange(0, 26, 1.0))
    csv("ch30-hubwind.csv", "v,h", [(f"{e + 0.5:.1f}", int(c)) for e, c in zip(edges[:-1], counts)])
    lines = ["vortex shedding: the tower standing without its nacelle",
             f"  bare tower (equivalent tube, ch 11): f1 = {f_bare:.2f} Hz",
             f"  with the rotor and nacelle on top: {f_top:.3f} Hz",
             f"  lock-in speed at the 3.0 m top (Strouhal 0.2): {v_cr:.1f} m/s",
             f"  hours of the data-pack year within 15 % of it: {band} of 8,760",
             f"  with the nacelle on: lock-in at {st.vortex_speed(f_top, 3.0):.1f} m/s - harmless",
             f"  a bare tower meets its lock-in wind in {100 * band / 8760:.0f} % of the",
             "  hours: towers are not left standing without the nacelle",
             "  overnight unless the maker's procedure allows it (with a",
             "  temporary damper or a wind limit) - a construction load",
             "  the finished turbine never sees (ch 31)"]
    emit("a_vortex", lines)


def seismic() -> None:
    ag, tc = src.SITE["ag"], src.SITE["tc"]

    def sa(t):
        return 2.5 * ag if t <= tc else 2.5 * ag * tc / t

    top = (src.TOP_T + 0.24 * src.TOWER_T) * 1e3
    t_turb = 1 / src.F1_FIXED
    v_t = st.base_shear(top, sa(t_turb))
    v_tr = st.base_shear(95e3, sa(0.15))
    lines = ["equivalent seismic base shear (teaching spectrum: plateau 2.5 ag",
             f"  to {tc} s, falling as 1/T beyond; ag = {ag} g; no code assumed)",
             "  structure                period s   Sa/g    mass t   shear kN"]
    for name, t, m, v in (("turbine (top + 0.24 tower)", t_turb, top / 1e3, v_t),
                          ("main transformer on plinth", 0.15, 95.0, v_tr)):
        lines.append(f"  {name:26s} {t:8.2f}   {sa(t):5.3f}   {m:6.0f}   {v / 1e3:8.0f}")
    m_turb = v_t * src.HUB / 1e6
    lines += [f"  turbine: {m_turb:.0f} MN m at the base against"
              f" {src.LOADS['extreme (parked, 50-yr gust)']['m_mnm']:.0f} from wind -",
              "  wind governs the tall, soft tower",
              "  transformer: a stiff, heavy item sits on the plateau; with",
              "  tall bushings, anchors and the plinth, earthquake can",
              "  govern the substation - the local seismic code and the",
              "  equipment's qualification decide (ch 25)"]
    emit("a_seismic", lines)


def pv_loads() -> None:
    p = src.PV_TABLE
    area = p["rows"] * p["module_l"] * p["modules_per_row"] * p["module_w"]
    length = p["modules_per_row"] * p["module_w"]
    q = st.dynamic_pressure(src.SITE["gust50_10m"] * (2.0 / 10) ** 0.11, src.SITE["rho"])
    uplift = q * 1.2 * area / 1e3
    dead = p["rows"] * p["modules_per_row"] * p["module_kn"] + p["steel_kn"]
    snow = src.SITE["snow_kpa"] * area * math.cos(math.radians(p["tilt_deg"]))
    t = datapack.load_hourly()["t_air_c"].to_numpy()
    dt = (t.max() + 25.0) - t.min()
    lines = ["one PV table (2P x 26, 25 deg; teaching coefficients A-360, A-361)",
             f"  area {area:.0f} m2, length {length:.1f} m",
             f"  50-yr gust at 2 m: pressure {q:,.0f} Pa; uplift (net coefficient 1.2): {uplift:.0f} kN",
             f"  dead weight {dead:.0f} kN; net uplift {uplift - dead:.0f} kN on"
             f" {p['frames'] * p['posts_per_frame']} posts",
             f"  snow {src.SITE['snow_kpa']} kPa on plan: {snow:.0f} kN downward (rare here)",
             f"  temperature range of the steel: {t.min():.1f} to {t.max() + 25:.1f} C (sun +25 K)",
             f"  free expansion of a {length:.1f} m rail: {1000 * st.thermal_expansion(12e-6, length, dt):.0f} mm",
             "  wind uplift, not weight, sizes the posts and their",
             "  embedment; the rail needs slotted holes or a joint so",
             "  the heat is not turned into a force on the posts"]
    emit("a_pv", lines)


def combination() -> None:
    f = src.FOUNDATION
    weight = ((src.TOP_T + src.TOWER_T) * G / 1e3 + f["concrete_m3"] * f["gamma_c"] / 1e3
              + f["backfill_m3"] * f["gamma_b"] / 1e3)
    ex = src.LOADS["extreme (parked, 50-yr gust)"]
    m_tot = ex["m_mnm"] + ex["h_mn"] * f["depth"]
    lines = ["overturning about the toe of the 20 m base, extreme case (teaching",
             "  factors: action x 1.35, stabilising weight x 0.9; the code sets real ones)",
             "  case                     overturning MN m   resisting MN m   ratio"]
    for name, fa, fs in (("characteristic", 1.0, 1.0), ("factored (teaching)", 1.35, 0.9)):
        over = fa * m_tot
        res = fs * weight * f["r"]
        lines.append(f"  {name:24s} {over:16.0f}   {res:14.0f}   {res / over:5.2f}")
    lines += ["  the factors make the check carry its own uncertainty; the",
              "  ratio stays above 1, but the soil under the compressed",
              "  part of the base is checked too (lesson D, effective area)"]
    emit("a_combination", lines)


if __name__ == "__main__":
    masses()
    tower_drag()
    vortex()
    seismic()
    pv_loads()
    combination()
