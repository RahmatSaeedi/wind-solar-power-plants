"""Chapter 53, lesson C: decommissioning and circularity - the material
balance, blades, the financial provision, waste chain of custody,
foundation removal depth, restoration monitoring, and second-life
modules.

Run from the project root:   python -m companion.ch53.examples_c
Writes companion/ch53/expected/c_*.txt and diagrams/data/ch53-waste.csv.
Teaching values (A-540).
"""
from __future__ import annotations

import numpy as np

from companion.ch53 import sources as src
from companion.ch53.common import csv, emit
from plantp import lifecycle as lc


# ------------------------------------------------ 1. material balance
def materials() -> dict:
    w = lc.waste_balance(src.MATERIALS)
    rows = []
    for k, (t, r, u, h) in src.MATERIALS.items():
        rows.append((k, t, t * r, t * u, t * (1 - r - u), h))
    csv("ch53-waste.csv", "k,recycled,reused,landfill",
        [(i + 1, round(r), round(u), round(l)) for i, (_, _, r, u, l, _) in enumerate(rows)])
    lines = ["materials at closure (t, teaching shares)",
             "  material                          tonnes  recycled  reused  landfill"]
    lines += [f"  {k:32s} {t:7,.0f} {r:9,.0f} {u:7,.0f} {l:9,.0f}" + ("  HAZ" if h else "")
              for k, t, r, u, l, h in rows]
    lines += [f"  total {w['total']:,.0f} t: recycled {w['recycled'] / w['total']:.0%}, reused "
              f"{w['reused'] / w['total']:.0%}, landfill {w['landfill'] / w['total']:.0%}",
              f"  hazardous {w['hazardous']:,.0f} t - small by mass, large by obligation:",
              "  each load goes to a licensed receiver with its transfer note"]
    emit("c_materials", lines)
    return w


# ------------------------------------------------ 2. blades
def blades() -> dict:
    t = src.MATERIALS["blades (composite)"][0]
    routes = {"cement co-processing": 0.55, "mechanical grinding (filler)": 0.15,
              "reuse (structures)": 0.10, "landfill (where allowed)": 0.20}
    lines = [f"36 blades, {t:,.0f} t of composite: routes (teaching shares)"]
    lines += [f"  {k:30s} {v:4.0%}  {t * v:5.0f} t" for k, v in routes.items()]
    lines += ["  most blade 'recycling' is energy and mineral recovery in a",
              "  kiln, not new blades; whether landfill is allowed at all is a",
              "  local rule (ch 54-58) - the closure plan names the route and",
              "  its receiver before the cranes come"]
    emit("c_blades", lines)
    return dict(t=t)


# ------------------------------------------------ 3. financial provision
def provision() -> dict:
    net_now = (src.DECOM_COST - src.SALVAGE)
    years_to_end = src.LIFE - src.YEAR_NOW
    net_end = net_now * (1 + src.INFLATION) ** src.LIFE
    from_start = lc.sinking_fund(net_end, src.LIFE, 0.04)
    from_now = lc.sinking_fund(net_end, years_to_end, 0.04)
    lines = [f"decommissioning cost {src.DECOM_COST:,.0f} k u less salvage {src.SALVAGE:,.0f} "
             "(year-1 money, ch 21)",
             f"  at year 25 with {src.INFLATION:.1%} inflation: {net_end:,.0f} k u",
             f"  sinking fund at 4 %: {from_start:,.0f} k u a year from year 1, or "
             f"{from_now:,.0f} from year {src.YEAR_NOW}",
             f"  starting late costs {from_now / from_start:.1f} times a year - the provision",
             "  is a bond or a fund held for the landholder and authority",
             "  (ch 33 closure), its size reviewed as salvage prices move"]
    emit("c_provision", lines)
    return dict(net_end=net_end, start=from_start, late=from_now)


# ------------------------------------------------ 4. chain of custody
def custody() -> dict:
    loads = [  # load, shipped t, received t (weighbridge at the licensed receiver)
        ("transformer oil T1", 18.0, 17.9), ("transformer oil T2", 18.0, 18.0),
        ("unit transformer oil", 25.0, 24.8), ("gearbox oil", 14.4, 11.2),
        ("battery modules lot 1", 120.0, 120.0), ("battery modules lot 2", 120.0, 119.6)]
    bad = [(k, s, r) for k, s, r in loads if abs(s - r) / s > 0.02]
    lines = ["hazardous loads: shipped against received (t), tolerance 2 %"]
    lines += [f"  {k:24s} {s:6.1f} {r:6.1f}" + ("  CHECK" if abs(s - r) / s > 0.02 else "")
              for k, s, r in loads]
    lines += [f"  {len(bad)} load(s) to check: {', '.join(k for k, *_ in bad)} - "
              f"{bad[0][1] - bad[0][2]:.1f} t missing",
              "  between the site and the receiver; until the transfer notes",
              "  reconcile, the closure evidence is not complete"]
    emit("c_custody", lines)
    return dict(bad=len(bad))


# ------------------------------------------------ 5. foundation removal depth
def foundations(price_t: float = 0.012, truck_t: float = 25.0) -> dict:
    full = 893.0 * 2.4
    top = 180.0 * 2.4
    out = {}
    for k, tonnes in (("top 1 m (teaching permit case)", top), ("full removal", full)):
        out[k] = (tonnes * 12, tonnes * 12 * price_t, tonnes * 12 / truck_t)
    lines = ["12 turbine foundations: concrete removed (t), cost (k u) and truck loads"]
    lines += [f"  {k:32s} {t:8,.0f} {c:7,.0f} {n:7,.0f}" for k, (t, c, n) in out.items()]
    f, t = out["full removal"], out["top 1 m (teaching permit case)"]
    lines += [f"  full removal is {f[0] / t[0]:.1f} times the trucks past the village",
              "  for land that the top-1-m case also returns to grazing; the",
              "  depth is the permit's and the landholder's agreement (ch 30,",
              "  ch 54-58), and the choice has a traffic and footprint cost"]
    emit("c_found", lines)
    return out


# ------------------------------------------------ 6. restoration monitoring
def restoration() -> dict:
    cover = {"PV area plot 1": [12, 28, 41], "PV area plot 2": [9, 18, 22],
             "road verges": [20, 35, 48], "laydown": [5, 14, 30]}   # % vegetation cover
    target = 40.0
    met = [k for k, v in cover.items() if v[-1] >= target]
    lines = ["vegetation cover after restoration, years 1-3 (%),",
             f"  target {target:.0f} % (teaching, from the baseline of ch 33)"]
    lines += [f"  {k:16s} " + " ".join(f"{x:3d}" for x in v) for k, v in cover.items()]
    lines += [f"  target met in year 3: {', '.join(met)}",
              f"  the laydown is on its way (+{cover['laydown'][2] - cover['laydown'][1]} points in year 3); plot 2 has",
              f"  stalled (+{cover['PV area plot 2'][2] - cover['PV area plot 2'][1]}) - reseeding and a grazing pause, agreed",
              "  with the herders (ch 33); the bond is released only on the",
              "  monitoring record"]
    emit("c_restore", lines)
    return dict(met=met)


# ------------------------------------------------ 7. second-life modules
def second_life(n: int = 109_200, seed: int = 540) -> dict:
    rng = np.random.default_rng(seed)
    yrs = np.arange(1, len(src.PV_PR) + 1)
    b, _ = lc.trend(yrs, src.PV_PR)
    mean25 = 1 + b / src.PV_PR[0] * 25                  # lesson A rate carried to year 25
    power = rng.normal(mean25, 0.03, n)                 # share of nameplate at year 25
    cracked = rng.random(n) < 0.04
    ok = (power >= 0.85) & ~cracked
    lines = ["modules at year 25: power as a share of nameplate (lesson A's rate",
             "  carried to year 25, spread teaching)",
             f"  mean {power.mean():.3f}; below 85 % {np.mean(power < 0.85):.1%}; cracked "
             f"(EL) {cracked.mean():.0%}",
             f"  fit for a second life after testing: {ok.mean():.0%} ({ok.sum():,} modules)",
             "  a second life needs a test record per module (ch 41 flash",
             "  and EL) and a buyer; without both they are waste with a",
             "  recycling cost"]
    emit("c_second", lines)
    return dict(share=float(ok.mean()), n=int(ok.sum()))


if __name__ == "__main__":
    materials()
    blades()
    provision()
    custody()
    foundations()
    restoration()
    second_life()
