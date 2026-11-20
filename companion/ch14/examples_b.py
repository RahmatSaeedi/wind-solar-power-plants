"""Chapter 14, section B - wind and PV layout principles on the synthetic
site: farm energy of the two candidate layouts with the teaching terrain
speed-up and chapter 11's Jensen wakes, wake loss against spacing, the
turbulence a turbine adds behind it, the land a 60 MWp block needs, the
shadow of a turbine on PV, and collector cables (tree and strings).

Run from the project root:   python -m companion.ch14.examples_b
Writes companion/ch14/expected/b_*.txt and diagrams/data/ch14-*.csv.
Site A-259; the hourly year of the data pack; D-015 wake model; D-017
long-term factor and hub density (chapter 13).
"""
from __future__ import annotations

import math
from functools import lru_cache

import numpy as np

from companion.ch11 import lab_d as l11
from companion.ch13 import sources as s13
from companion.ch14 import sources as src
from companion.ch14.common import csv, emit
from plantp import datapack, siting as st, wind as w

G = src.GRID
D = 2 * src.RADIUS
LT = 191.87 / 186.69                      # chapter 13 long-term factor (D-017)


@lru_cache(maxsize=1)
def wind_table():
    """Hours of the data year binned by direction (2 deg: the top-hat wake
    model jumps with coarser bins) and density-equivalent hub speed
    (0.5 m/s), with hub density (D-017)."""
    h = datapack.load_hourly()
    v = h["ws_100m_ms"].to_numpy(float)
    wd = h["wd_100m_deg"].to_numpy(float)
    rho = s13.hub_density(h["p_hpa"].to_numpy(float), h["t_air_c"].to_numpy(float))
    veq = w.density_equivalent_speed(v, rho)
    db = (np.floor(wd / 2.0) % 180).astype(int)
    vb = np.round(veq / 0.5).astype(int)
    table = {}
    for a, b in zip(db, vb):
        table[(a, b)] = table.get((a, b), 0) + 1
    return table


def farm_energy(xy, speedup=None):
    """Free-stream and waked energy (GWh a year, data year) of a layout;
    speedup: fractional terrain speed-up at each turbine."""
    xy = np.asarray(xy, float)
    s = np.zeros(len(xy)) if speedup is None else np.asarray(speedup, float)
    vg, _, _, ctg = l11.rotor.curve_arrays()
    e_free = e_wake = 0.0
    for (a, b), n in wind_table().items():
        v = 0.5 * b
        if v < 2.5:
            continue
        ct = float(np.interp(v, vg, ctg))
        vs = w.farm_speeds(xy, v, 2.0 * a + 1.0, ct, D)
        e_free += n * float(l11.pack_power(v * (1 + s)).sum())
        e_wake += n * float(l11.pack_power(vs * (1 + s)).sum())
    return e_free / 1e6, e_wake / 1e6


def speedups(xy):
    sp = st.hill_speedup(src.terrain(), G.cell, 800.0)
    return G.sample(sp, xy[:, 0], xy[:, 1])


def layouts_energy() -> None:
    lines = ["farm energy of the two candidate layouts (data year x long-term",
             f"  factor {LT:.4f}, hub density, teaching speed-up, Jensen wakes):",
             "  layout              speed-up   free GWh   waked GWh   wake loss"]
    rows = []
    for name, xy in src.layouts().items():
        s = speedups(xy)
        f, e = farm_energy(xy, s)
        lines.append(f"  {name:18s}  {100 * s.mean():+5.1f} %   {LT * f:8.2f}    {LT * e:8.2f}"
                     f"     {100 * (1 - e / f):5.2f} %")
        rows.append((name.split()[0], f"{LT * f:.2f}", f"{LT * e:.2f}"))
        if name.startswith("W1"):
            e_ridge = e
    flat, flat_w = farm_energy(src.layouts()["W1 ridge (1 row)"])
    lines += [f"  the ridge row without its speed-up: {LT * flat_w:.2f} GWh",
              f"  the hill adds {100 * (e_ridge / flat_w - 1):.0f} % to the ridge's energy"
              " and the single row",
              "  across the wind loses little to wakes; the plain loses more",
              "  behind its front row; the teaching speed-up is the largest",
              "  uncertainty of the ridge (a flow model and a second mast)"]
    emit("b_layouts", lines)
    csv("ch14-layouts.csv", "layout,free,waked", rows)


def spacing() -> None:
    """Two rows of six across the prevailing wind (285 deg): along-wind
    spacing 3D .. 10D at 4D across."""
    lines = ["wake loss of two rows of six against the row spacing (4D along",
             "  the row, rows across the prevailing wind, flat ground):",
             "  rows apart    wake loss   farm GWh"]
    rows = []
    th = math.radians(285.0 - 90.0)                     # row axis: 15/195 deg
    ax = np.array([math.sin(math.radians(15.0)), math.cos(math.radians(15.0))])
    nx = np.array([math.sin(math.radians(285.0)), math.cos(math.radians(285.0))])
    del th
    for k in (3, 4, 5, 6, 8, 10):
        xy = np.array([j * 4 * D * ax + r * k * D * nx for r in (0, 1) for j in range(6)])
        f, e = farm_energy(xy)
        rows.append((k, f"{100 * (1 - e / f):.2f}"))
        lines.append(f"  {k:3d} D         {100 * (1 - e / f):5.2f} %    {LT * e:7.2f}")
    lines += ["  the loss falls with spacing, quickly at first and then slowly;",
              "  land, cable and road grow with it: the choice is an optimum,",
              "  not a rule (with 10 deg direction bins this top-hat model",
              "  jumps up and down: the result must not depend on the bins)"]
    emit("b_spacing", lines)
    csv("ch14-spacing.csv", "k,loss", rows)


def added_turbulence() -> None:
    """Wake-added turbulence of one upstream turbine (a published empirical
    form, Frandsen): I_add = 1 / (1.5 + 0.8 (x/D) / sqrt(Ct)); effective
    I = sqrt(I_amb^2 + I_add^2). Teaching; the design standard has its own
    method with direction weighting."""
    i_amb, ct = 0.132, 0.36                    # 15 m/s: rep. TI (ch 13), Ct at 15
    lines = ["turbulence behind a turbine at 15 m/s (ambient representative",
             f"  {i_amb:.3f}, Ct {ct:.2f}; design curve 0.184, ch 13 A-258):",
             "  distance   added    effective   below the design curve?"]
    for x in (3, 4, 6, 8, 10):
        add = 1 / (1.5 + 0.8 * x / math.sqrt(ct))
        eff = math.hypot(i_amb, add)
        lines.append(f"  {x:3d} D      {add:.3f}    {eff:.3f}       "
                     f"{'yes' if eff < 0.184 else 'no'}")
    csv("ch14-turbulence.csv", "x,eff",
        [(f"{x:.1f}", f"{math.hypot(i_amb, 1 / (1.5 + 0.8 * x / math.sqrt(ct))):.4f}")
         for x in np.arange(2.0, 12.01, 0.5)])
    lines += ["  directly behind a close neighbour the effective turbulence can",
              "  pass the design curve; it occurs only for the sectors where the",
              "  neighbour stands upwind, so the real check weights by direction",
              "  (chapter 16 and the manufacturer's site suitability)"]
    emit("b_turbulence", lines)


def pv_land() -> None:
    modules = 4200 * 26                        # D-013
    area_mod = modules * 2.278 * 1.134
    rows_ha = area_mod / 0.40 / 1e4             # GCR 0.40 (A-183)
    total = rows_ha * 1.25
    blk = st.polygon_area(src.PV_BLOCK) / 1e4
    lines = ["land of the 60 MWp block (fixed tilt, GCR 0.40, D-013):",
             f"  modules {modules:,} x 2.58 m2 = {area_mod / 1e4:.1f} ha of glass",
             f"  rows at GCR 0.40: {rows_ha:.1f} ha; with roads, inverter stations,",
             f"    fence and buffers (x 1.25, teaching): {total:.0f} ha"
             f" ({total / 60.06:.2f} ha/MWp)",
             f"  the screening block: {blk:.0f} ha ({100 * total / blk:.0f} % used)",
             "  trackers need more land per MWp (larger pitch), bifacial rows",
             "  gain from a higher pitch: the block size follows chapter 10"]
    emit("b_pvland", lines)


def turbine_shadow() -> None:
    lat = 34.0
    dec = -23.44
    noon = 90 - lat + dec
    lines = ["shadow of a turbine on PV (tip 175 m, latitude 34 N):",
             f"  winter noon sun {noon:.1f} deg: tip shadow"
             f" {src.TIP / math.tan(math.radians(noon)):.0f} m to the north",
             "  sun elevation   tip shadow"]
    for el in (10, 15, 20, 30):
        lines.append(f"    {el:3d} deg       {src.TIP / math.tan(math.radians(el)):6.0f} m")
    near = min(math.hypot(x - 6900.0, y - 2725.0) for x, y in src.layouts()["W2 plain (2 rows)"])
    lines += [f"  nearest W2 turbine to the PV block edge: about {near:,.0f} m",
              "  a moving rotor shadow on PV costs little energy but causes",
              "  flicker on the inverters' MPP trackers; keep PV north and",
              "  north-east of turbines out of the long winter shadows or",
              "  accept and model them (chapter 15)"]
    emit("b_shadow", lines)


def cables() -> None:
    lines = ["33 kV collector network to the site substation (straight lines):",
             "  layout              tree (MST) km   radial strings km   strings"]
    for name, xy in src.layouts().items():
        pts = np.vstack([np.array(src.SITE_SUB), xy])
        _, mst = st.minimum_spanning_tree(pts)
        strings, rad = st.radial_strings(xy, src.SITE_SUB, 4)
        lines.append(f"  {name:18s}  {mst / 1e3:8.2f}        {rad / 1e3:8.2f}           "
                     f"{len(strings)}")
    lines += ["  four turbines per string (20 MW at 33 kV, teaching; cable",
              "  sizing in chapter 24); the tree is a lower bound, the strings",
              "  are buildable; both follow roads in practice (longer)"]
    emit("b_cables", lines)


if __name__ == "__main__":
    layouts_energy()
    spacing()
    added_turbulence()
    pv_land()
    turbine_shadow()
    cables()
