"""Chapter 33, lesson A: baseline and assessment in numbers - a screening
of aspects against receptors, turbine noise at the dwellings, shadow
flicker of layout W2b in the seasons people are there, raptor collisions
near the nest, the energy a bat curtailment costs, the habitat the
project takes, how many turbines each receptor sees, and cumulative
noise with the existing road.

Run from the project root:   python -m companion.ch33.examples_a
Writes companion/ch33/expected/a_*.txt and diagrams/data/ch33-noise.csv.
Teaching values (A-376 to A-379); studies, permits and the people
affected decide the real ones (U-112, U-113).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch33 import sources as src
from companion.ch33.common import csv, emit
from companion.ch14 import examples_c as c14
from plantp import datapack
from plantp import envsocial as es

RECEPTORS = dict(src.DWELLINGS, **{"village centre": src.VILLAGE_CENTRE})


def screening() -> None:
    rows = [("noise at night", "dwellings, camp", 3, 3), ("shadow flicker", "camp B (seasonal)", 3, 2),
            ("raptor collision", "nest NW", 2, 4), ("bat collision", "migrants, autumn", 2, 3),
            ("habitat loss", "rangeland, wadi", 2, 2), ("landscape", "village, road", 3, 2),
            ("water use", "village wells, spring", 3, 4), ("traffic", "village, school", 3, 3),
            ("dust", "village, farms", 2, 2), ("cultural heritage", "cemetery, ruin", 1, 5),
            ("grazing access", "herders' families", 4, 4)]
    lines = ["screening: magnitude x sensitivity (1-5, teaching; scoping decides)",
             "  aspect               receptor                 mag  sens  score  study?"]
    for a, r, m, s in sorted(rows, key=lambda x: -x[2] * x[3]):
        sc = m * s
        lines.append(f"  {a:20s} {r:24s} {m:3d}  {s:4d}  {sc:5d}  {'yes' if sc >= 6 else 'note'}")
    lines += ["  screening chooses where baseline studies go; a low score",
              "  with a sensitive receptor (the cemetery) still gets a",
              "  protection rule - scoping with the authority and the",
              "  community confirms the list (lesson B)"]
    emit("a_screen", lines)


def noise() -> None:
    n = src.NOISE
    rows = []
    lines = ["turbine noise at night at the receptors (12 turbines, W2b, teaching)",
             f"  sound power {n['lw_turbine']:.0f} dB(A) each; limit {n['night_limit']:.0f} (PLACEHOLDER);"
             f" background {n['background']:.0f}",
             "  receptor                       nearest m   turbines dB(A)   with background"]
    for name, (x, y) in RECEPTORS.items():
        d = np.hypot(src.TURBINES[:, 0] - x, src.TURBINES[:, 1] - y)
        lvl = es.db_sum([es.noise_at(n["lw_turbine"], max(r, 50.0), n["alpha_db_km"]) for r in d])
        tot = es.db_sum([lvl, n["background"]])
        flag = "  over" if lvl > n["night_limit"] else ""
        rows.append((len(rows) + 1, round(lvl, 1)))
        lines.append(f"  {name:30s} {d.min():9.0f}   {lvl:14.1f}   {tot:15.1f}{flag}")
    csv("ch33-noise.csv", "receptor,level", rows)
    lines += ["  every receptor is under the placeholder limit, but the",
              "  camp and farmhouse A hear the turbines about 10 dB above",
              "  the quiet background - clearly audible at night; if the",
              "  permit uses a background-based criterion, a noise-reduced",
              "  mode for the nearest turbines in the camp's months is",
              "  weighed against the energy it costs (ch 14)"]
    emit("a_noise", lines)


def flicker() -> None:
    lines = ["shadow flicker of layout W2b (geometric worst case, ch 14 method)",
             "  receptor                         worst case h/yr   worst day min"]
    for name in ("herders' camp B (seasonal)", "farmhouse A", "farmhouse C"):
        x, y = src.DWELLINGS[name]
        zh = float(c14.z_at([(x, y)])[0])
        hrs, day = c14.flicker_hours(src.TURBINES, (x, y), zh)
        lines.append(f"  {name:32s} {hrs:15.1f}   {day:13.0f}")
    lines += ["  W2b's adjustment moved the turbines out of reach of the",
              "  dwellings: layout W2 gave the camp 112 h a year (ch 14),",
              "  W2b gives none - avoidance by siting, the first step of",
              "  the mitigation hierarchy; a flicker timer remains the",
              "  remedy if a later layout change brings it back"]
    emit("a_flicker", lines)


def birds() -> None:
    b = src.BIRDS
    lines = ["raptor collisions near the nest (teaching collision estimate)",
             f"  {b['passages_at_nest']:.0f} passages a year near the nest, falling as"
             f" exp(-d / {b['decay_m']:.0f} m); p {b['p_collision']}, avoidance {b['avoidance']}",
             "  turbine   distance to nest m   passages/yr   collisions/yr"]
    total = 0.0
    d = np.hypot(src.TURBINES[:, 0] - src.NEST[0], src.TURBINES[:, 1] - src.NEST[1])
    for k in np.argsort(d)[:4]:
        pas = b["passages_at_nest"] * math.exp(-d[k] / b["decay_m"])
        col = es.collision_estimate(pas, b["p_collision"], b["avoidance"])
        lines.append(f"  T{k + 1:02d}      {d[k]:18.0f}   {pas:11.0f}   {col:13.3f}")
    for k in range(len(d)):
        total += es.collision_estimate(b["passages_at_nest"] * math.exp(-d[k] / b["decay_m"]),
                                       b["p_collision"], b["avoidance"])
    near = sum(es.collision_estimate(b["passages_at_nest"] * math.exp(-d[k] / b["decay_m"]),
                                     b["p_collision"], b["avoidance"]) for k in np.argsort(d)[:4])
    lines += [f"  all twelve: about {total:.1f} collisions a year, {total * 25:.0f} over 25 years",
              "  far more than a long-lived raptor with a few pairs in",
              f"  the region can absorb; the four nearest turbines carry"
              f" {near / total * 100:.0f} % - siting, a",
              "  seasonal shutdown in the breeding months or an observer",
              "  system are the options (study first: U-113)"]
    emit("a_birds", lines)


def bats() -> None:
    d = datapack.load_hourly()
    pc = datapack.load_power_curve()
    v = d["ws_100m_ms"].to_numpy()
    h = d.index.hour.to_numpy()
    m = d.index.month.to_numpy()
    p = np.interp(v, pc.iloc[:, 0].to_numpy(), pc.iloc[:, 1].to_numpy())  # kW one turbine
    b = src.BATS
    night = (h >= b["night"][0]) | (h < b["night"][1])
    season = np.isin(m, b["months"])
    cut = night & season & (v < b["cut_in"])
    e_year = p.sum() * 12 / 1e6
    e_lost = p[cut].sum() * 12 / 1e6
    lines = ["bat curtailment: rotors stopped below 6 m/s on autumn nights",
             f"  hours curtailed: {int(cut.sum())} of {int((night & season).sum())} autumn night hours",
             f"  energy lost: {e_lost:.2f} GWh of {e_year:.1f} GWh ({e_lost / e_year * 100:.2f} %)",
             f"  expected reduction of bat collisions: about {b['reduction'] * 100:.0f} % (teaching)",
             "  bats fly mostly in low wind, when turbines make little",
             "  energy: a cut-in raised on autumn nights halves the",
             "  risk for a fraction of a per cent of energy - the",
             "  months, hours and speed come from the bat survey"]
    emit("a_bats", lines)


def habitat() -> None:
    lines = ["habitat the project takes and a teaching offset (ha)",
             "  use                          area   habitat              offset ratio"]
    tot, off = 0.0, 0.0
    for (name, a), (hab, ratio) in zip(src.LAND_USE.items(),
                                       [("rangeland", 1.0), ("rangeland, wadi edge", 2.0),
                                        ("rangeland", 1.0), ("rangeland (restored)", 0.0),
                                        ("farmland strips", 1.0)]):
        tot += a
        off += a * ratio
        lines.append(f"  {name:28s} {a:6.1f}   {hab:20s} {ratio:5.1f}")
    lines += [f"  total {tot:.1f} ha; offset area at these ratios {off:.1f} ha",
              "  avoidance comes first (the wadi edge, the nest), then",
              "  restoration of temporary areas, and an offset only for",
              "  what remains - the ratios and whether an offset applies",
              "  come from the framework and the biodiversity study"]
    emit("a_habitat", lines)


def visibility() -> None:
    z = c14.z_at
    lines = ["how many turbines each receptor sees (blade tip over the terrain)",
             "  receptor                       turbines visible   nearest km"]
    for name, (x, y) in RECEPTORS.items():
        z0 = float(z([(x, y)])[0]) + 1.7
        seen = 0
        for tx, ty in src.TURBINES:
            zt = float(z([(tx, ty)])[0]) + src.TIP
            s = np.linspace(0.02, 0.98, 60)
            px, py = x + (tx - x) * s, y + (ty - y) * s
            ground = z(np.column_stack([px, py]))
            ray = z0 + (zt - z0) * s
            seen += int(np.all(ground < ray))
        dmin = np.hypot(src.TURBINES[:, 0] - x, src.TURBINES[:, 1] - y).min() / 1000
        lines.append(f"  {name:30s} {seen:16d}   {dmin:10.1f}")
    lines += ["  on an open plain almost every turbine is seen from",
              "  everywhere: visibility is not avoidable here, so the",
              "  assessment turns to how the view changes (photomontages",
              "  agreed with the village) and to lights at night"]
    emit("a_visibility", lines)


def cumulative() -> None:
    n = src.NOISE
    road = 33.0                                    # dB(A) at the camp from the road at night (teaching)
    x, y = src.DWELLINGS["herders' camp B (seasonal)"]
    d = np.hypot(src.TURBINES[:, 0] - x, src.TURBINES[:, 1] - y)
    turb = es.db_sum([es.noise_at(n["lw_turbine"], r, n["alpha_db_km"]) for r in d])
    lines = ["cumulative night noise at the seasonal camp (teaching)",
             f"  background {n['background']:.0f}, road {road:.0f}, turbines {turb:.1f} dB(A)",
             f"  all together: {es.db_sum([n['background'], road, turb]):.1f} dB(A)",
             f"  without the turbines: {es.db_sum([n['background'], road]):.1f} dB(A)",
             "  decibels add as energy: the turbines dominate and the",
             "  road adds little - but a second project on the next",
             "  ridge would add its own share, which is why cumulative",
             "  effects are assessed with the other projects, not alone"]
    emit("a_cumulative", lines)


if __name__ == "__main__":
    screening()
    noise()
    flicker()
    birds()
    bats()
    habitat()
    visibility()
    cumulative()
