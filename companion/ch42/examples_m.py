"""Chapter 42, a tenth round: tightening passes of a bolted ring with
elastic interaction, planet load sharing against pin-position error,
cooler fouling over the data-pack year, generator air-gap eccentricity
from eight readings, and the break-even of a blade factory near the site.

Run from the project root:   python -m companion.ch42.examples_m
Writes companion/ch42/expected/m_*.txt and diagrams/data/ch42-passes.csv.
Teaching values (A-452, A-455, A-457); no process recipes.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch42.common import csv, emit
from plantp import datapack

# ------------------------------------------------ tightening passes
# [start: passes]
COUPLE = {1: 0.06, 2: 0.03, 3: 0.01}   # preload lost by a neighbour, share


def tighten(order, n=96, passes=3):
    """Preload of each bolt (share of target) after each pass; raising
    bolt j to the target relaxes tight bolts at distance 1-3 by a share
    of the preload it gained."""
    f = np.zeros(n)
    out = []
    for _ in range(passes):
        for j in order:
            gain = 1.0 - f[j]
            f[j] = 1.0
            for d, c in COUPLE.items():
                for i in ((j + d) % n, (j - d) % n):
                    if f[i] > 0:
                        f[i] -= c * gain
        out.append(f.copy())
    return out
# [end: passes]


def passes(n: int = 96) -> dict[str, list[float]]:
    seq = list(range(n))
    star = [k * 24 + q * 12 + r * 6 + s for s in range(6) for r in range(2)
            for q in range(2) for k in range(4)]
    assert sorted(star) == seq
    lines = [f"{n} root bolts tightened one at a time; each tightening relaxes",
             "  tight neighbours by 6, 3 and 1 % of the preload it gains",
             "  (teaching)",
             "  order        pass 1 min / mean   pass 2 min / mean   "
             "pass 3 min / mean"]
    res = {}
    rows = []
    for name, order in (("in sequence", seq), ("crosswise", star)):
        fs = tighten(order, n)
        res[name] = [float(x.min()) for x in fs]
        lines.append(f"  {name:12s} " + "   ".join(
            f"{x.min():6.0%} / {x.mean():4.0%}" for x in fs))
        if name == "crosswise":
            rows = [(k + 1, round(float(fs[0][k]), 3), round(float(fs[1][k]), 3))
                    for k in range(n)]
    csv("ch42-passes.csv", "bolt,pass1,pass2", rows)
    lines += ["  one pass leaves most bolts short of target whatever the",
              "  order; a second pass at the same target recovers most of it",
              "  and a third closes the gap - the work instruction names the",
              "  passes, and the logged tool shows each bolt's last value;",
              "  on a flat flange the order changes little, on a flange with",
              "  a gap it decides where the gap closes (not modelled here)"]
    emit("m_passes", lines)
    return res


# ------------------------------------------------ planet load sharing
def sharing(p_kw: float = 5329.0, rpm: float = 11.5, r_carrier: float = 0.55,
            k_mesh: float = 8e9) -> dict[float, float]:
    torque = p_kw * 1e3 / (rpm * 2 * math.pi / 60)
    f_mesh = torque / (3 * r_carrier) / 2
    lines = [f"first planetary stage, three planets: input torque "
             f"{torque / 1e6:.2f} MN m",
             f"  mesh force per planet {f_mesh / 1e6:.2f} MN; mesh stiffness "
             f"{k_mesh / 1e9:.0f} kN/um (teaching)",
             "  pin error um   load factor   planet bearing life"]
    out = {}
    for d_um in (5.0, 10.0, 20.0, 40.0):
        k = 1 + (2 / 3) * k_mesh * d_um * 1e-6 / f_mesh
        out[d_um] = k
        lines.append(f"  {d_um:12.0f}   {k:11.3f}   {k ** (-10 / 3):17.0%}")
    lines += ["  the planet whose pin sits ahead meets the load first and",
              "  carries more; life falls with the load to the power 10/3",
              "  (ch 11) - pin-hole position on the carrier is a critical",
              "  dimension, measured and recorded per carrier"]
    emit("m_sharing", lines)
    return out


# ------------------------------------------------ cooler fouling
def fouling(t_design: float = 35.0, t_limit: float = 65.0,
            rated_mw: float = 5.0, n_wtg: int = 12) -> dict[float, float]:
    h = datapack.load_hourly()
    t = h["t_air_c"].to_numpy()
    v = h["ws_100m_ms"].to_numpy()
    load = np.clip((v - 3.0) / (11.0 - 3.0), 0, 1) ** 3
    clean = np.clip((t_limit - t) / (t_limit - t_design), 0, None)
    lines = ["cooler fouled by dust: capacity x factor; the turbine derates",
             "  to what the cooler can carry (load share from the data-pack",
             "  wind, heat proportional to load; teaching)",
             "  cooler kept   hours derated   energy lost MWh/yr (12 turbines)"]
    out = {}
    for fac in (1.0, 0.85, 0.70):
        cap = clean * fac
        short = np.clip(load - cap, 0, None)
        hrs = int((short > 0).sum())
        mwh = float(short.sum() * rated_mw * n_wtg)
        out[fac] = mwh
        lines.append(f"  {fac:11.0%}   {hrs:13d}   {mwh:16.0f}")
    lines += ["  a clean cooler sized for 35 C hardly ever limits: the hot",
              "  hours are rarely windy ones; dust takes the margin away, so",
              "  cleaning the fins is on the maintenance plan and the",
              "  cooler's pressure drop is a monitored signal (ch 37)"]
    emit("m_fouling", lines)
    return out


# ------------------------------------------------ air-gap eccentricity
def gap_offset(g) -> tuple[float, float]:
    """Rotor offset (x, y) from gap readings at equal angles: the first
    harmonic of the readings, with the sign of a smaller gap."""
    g = np.asarray(g, float)
    n = len(g)
    th = np.arange(n) * 2 * math.pi / n
    return (float(-2 / n * np.sum(g * np.cos(th))),
            float(-2 / n * np.sum(g * np.sin(th))))


def airgap(readings_mm=(4.21, 4.34, 4.30, 4.06, 3.79, 3.66, 3.71, 3.94),
           tol: float = 0.10) -> dict[str, float]:
    g = np.array(readings_mm)
    n = len(g)
    g0 = g.mean()
    ex, ey = gap_offset(g)
    e = math.hypot(ex, ey)
    ang = math.degrees(math.atan2(ey, ex)) % 360
    lines = [f"generator air gap read at {n} points around the stator (mm):",
             "  " + ", ".join(f"{x:.2f}" for x in g),
             f"  mean gap {g0:.2f} mm; first harmonic: rotor off centre by "
             f"{e:.2f} mm",
             f"    toward {ang:.0f} deg, {e / g0:.1%} of the gap",
             f"    (teaching limit {tol:.0%})",
             "  the first harmonic of the readings is the offset of the",
             "  rotor; what is left is the stator's out-of-roundness - the",
             "  offset sets the unbalanced magnetic pull of ch 8"]
    emit("m_airgap", lines)
    return dict(e=e, share=e / g0)


# ------------------------------------------------ blade factory near site
def local_factory(setup_k: float = 30000.0, transport_k: float = 45.0,
                  premium_k: float = 10.0) -> dict[str, float]:
    save = transport_k - premium_k
    blades = setup_k / save
    lines = ["a blade factory near the site against long-haul blades "
             "(teaching k u)",
             f"  set-up {setup_k:,.0f}; transport saved {transport_k:.0f} a "
             f"blade; local premium {premium_k:.0f} a blade",
             f"  break-even at {blades:,.0f} blades = {blades / 3:,.0f} "
             "turbines",
             f"  Plant P's 36 blades recover {36 * save / setup_k:.0%} of the "
             "set-up",
             "  one plant does not pay for a factory; a pipeline of plants",
             "  in a region may - and where a buyer asks for local content,",
             "  this is the price of it, to be weighed in the bid (ch 39)"]
    emit("m_local", lines)
    return dict(blades=blades)


if __name__ == "__main__":
    passes()
    sharing()
    fouling()
    airgap()
    local_factory()
