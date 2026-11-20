"""Chapter 18, more architecture lessons: the energy at each power-flow
boundary of Plant P (meters M1-M4), radial against open-ring collector
strings, three substation arrangements, environmental ratings against
the site (temperature and altitude), and the system-level interface
(N-squared) matrix.

Run from the project root:   python -m companion.ch18.examples_g
Writes companion/ch18/expected/g_*.txt.
Teaching values A-286 (technical), A-288 (reliability), A-289 (ratings).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch14 import lab_d as l14, sources as s14
from companion.ch15 import sources as s15
from companion.ch18 import sources as src
from companion.ch18.common import csv, emit
from plantp import datapack, siting as st

R = src.REL


def flows() -> None:
    """Yearly energy at each boundary of model 15.1 (GWh)."""
    r = s15.plant_year()
    g = {k: float(np.sum(r[k])) / 1e3 for k in
         ("w_av", "pv_av", "mv", "el_loss", "aux", "poc", "curtailed", "net")}
    out = g["poc"] - g["curtailed"] - g["net"]
    lines = ["energy at the power-flow boundaries of Plant P (model 15.1, S0):",
             "  boundary                                      GWh/yr",
             f"  M1 wind farm at the 33 kV bus                {g['w_av']:8.2f}",
             f"  M2 PV plant at the 33 kV bus                 {g['pv_av']:8.2f}",
             f"     sum at the 33 kV bus                      {g['mv']:8.2f}",
             f"     less transformer and line losses          {g['el_loss']:8.2f}",
             f"     less own use (auxiliaries)                {g['aux']:8.2f}",
             f"  M3 at the POC before the limit               {g['poc']:8.2f}",
             f"     less export-limit curtailment             {g['curtailed']:8.2f}",
             f"     less grid outages                         {out:8.2f}",
             f"  M4 revenue meter, net export                 {g['net']:8.2f}",
             "  each line is a boundary someone owns: the turbine and PV",
             "  suppliers guarantee M1 and M2, the EPC contractor the losses,",
             "  the grid operator the limit, the buyer pays on M4"]
    emit("g_flows", lines)


def _segments(xy, root, chain):
    pos, segs = np.asarray(root, float), []
    for k in chain:
        segs.append(float(np.hypot(*(xy[k] - pos))) / 1000)
        pos = xy[k]
    return segs


# [start: ring]
def ring() -> None:
    """A fault on a radial string section loses every turbine beyond it
    until repair; an open ring (far ends tied through a normally open
    switch) restores them after switching."""
    xy = l14.layouts()["W2b plain, adjusted"]
    strings, _ = st.radial_strings(xy, s14.SITE_SUB, 4)
    p_t = s15.plant_year()["w_av"].mean() / 12.0          # mean MW a turbine
    lam, rep, switch_h = R["cable_fail_per_km"], R["cable_repair_h"], 4.0
    radial = opened = 0.0
    for chain in strings:
        for k, km in enumerate(_segments(xy, s14.SITE_SUB, chain)):
            beyond = len(chain) - k                         # turbines cut off
            radial += lam * km * rep * beyond * p_t
            opened += lam * km * switch_h * beyond * p_t
    ends = [xy[c[-1]] for c in strings]
    tie = sum(float(np.hypot(*(ends[i] - ends[i + 1]))) / 1000
              for i in range(len(ends) - 1))
    kv, ohm, mh, amp, cost = src.CABLES["33 kV 240 mm2"]
    two = 8 * 5.0 / (math.sqrt(3) * kv * 0.95)      # kA, two strings on one
    lines = ["radial strings against an open ring (A-288, expected values):",
             f"  radial: {radial:6.0f} MWh/yr lost to cable faults",
             f"  open ring: {opened:6.0f} MWh/yr (switching {switch_h:.0f} h,"
             " then fed from the other end)",
             f"  tie cables {tie:.2f} km, about {cost * tie:,.0f} k u,"
             " plus two ring switches",
             f"  when switched, one cable carries two strings: {two:.3f} kA,",
             f"  above the {amp} kA of 240 mm2 and the"
             f" {src.CABLES['33 kV 630 mm2'][3]} kA of 630 mm2",
             "  so the ring restores only part of a string at full wind, or",
             "  needs larger cables; at these failure rates it saves little",
             "  energy and is bought where repairs are slow (remote sites,",
             "  winter access)"]
    emit("g_ring", lines)
# [end: ring]


def collector_map() -> None:
    """Plot data: string sections and ring ties (km, local grid)."""
    xy = l14.layouts()["W2b plain, adjusted"]
    strings, _ = st.radial_strings(xy, s14.SITE_SUB, 4)
    rows = []
    for k, chain in enumerate(strings):
        pos = np.asarray(s14.SITE_SUB, float)
        for j in chain:
            rows.append((k, f"{pos[0] / 1e3:.3f}", f"{pos[1] / 1e3:.3f}",
                         f"{xy[j][0] / 1e3:.3f}", f"{xy[j][1] / 1e3:.3f}"))
            pos = xy[j]
    ends = [xy[c[-1]] for c in strings]
    for i in range(len(ends) - 1):
        rows.append((9, f"{ends[i][0] / 1e3:.3f}", f"{ends[i][1] / 1e3:.3f}",
                     f"{ends[i + 1][0] / 1e3:.3f}", f"{ends[i + 1][1] / 1e3:.3f}"))
    csv("ch18-strings.csv", "s,x1,y1,x2,y2", rows)
    csv("ch18-wtg.csv", "x,y", [(f"{a / 1e3:.3f}", f"{b / 1e3:.3f}") for a, b in xy])


def substation() -> None:
    """Energy lost in one event for three arrangements (teaching)."""
    p = np.minimum(s15.plant_year()["poc"], 100.0).clip(0, None)
    mean, above60 = p.mean(), np.clip(p - 60.0, 0, None).mean()
    bus_h = 48.0                                # 33 kV busbar repair (A-288)
    rows = [("single bus, one transformer", mean * R["trafo_repair_h"], mean * bus_h, 1),
            ("single bus, two transformers", above60 * R["trafo_repair_h"], mean * bus_h, 2),
            ("split bus, two transformers", above60 * R["trafo_repair_h"],
             0.5 * mean * bus_h, 2)]          # half the plant on each section
    lines = ["substation arrangements: energy lost in one event (MWh)",
             "  arrangement                    transformer   busbar   units"]
    for name, t, b, n in rows:
        lines.append(f"  {name:29s} {t:11,.0f} {b:8,.0f}   {n:5d}")
    lines += ["  the split (sectionalised) 33 kV bus with a bus-section",
              "  breaker keeps half the plant on a busbar fault; the second",
              "  transformer covers the long transformer outage; both add",
              "  bays, protection and space (chapters 26-27)"]
    emit("g_substation", lines)


def environment() -> None:
    """Site conditions against teaching rating bases (A-289)."""
    h = datapack.load_hourly()
    t = h["t_air_c"].to_numpy(float)
    elev = 1200.0                                  # data-pack manifest
    pv = s15.plant_year()["pv_av"]
    hot = t > 40.0

    def lost_mwh(temp):
        derate = np.clip((temp - 40.0) * 0.02, 0, None)  # 2 %/K above 40 C
        cap = 49.0 * (1 - derate)                         # ten inverters
        return float(np.clip(pv - cap, 0, None).sum())
    lines = ["environmental ratings against the site (teaching, A-289):",
             f"  air temperature {t.min():.1f} to {t.max():.1f} C; hours above 40 C:"
             f" {int(hot.sum())}",
             "  inverter full power to 40 C, -2 %/K above (teaching basis)",
             f"  energy lost to derating: {lost_mwh(t):.1f} MWh/yr outdoors;"
             f" {lost_mwh(t + 10.0):.1f} MWh/yr",
             f"    if the inverter room runs 10 K warmer ({int((t > 30).sum())} hours"
             " above 40 C)",
             f"  site elevation {elev:.0f} m against a 1000 m rating basis:",
             "    insulation and cooling ratings need the maker's altitude",
             "    correction; the enclosure needs ventilation that still",
             "    cools in thinner air",
             "  also to state: dust and water ingress (IP code), corrosion",
             "  category, snow and wind loads, UV, and the temperature",
             "  inside the room or container, not only outside"]
    emit("g_environment", lines)


# [start: n2]
SYSTEMS = ["wind", "PV", "BESS", "collector", "substation", "grid",
           "control", "water", "civil"]
LINKS = {   # (i, j): interface kinds; E electrical, M mechanical, T thermal,
            # P protection, C control/comms, V civil, W water, G grid code
    (0, 3): "EPC", (1, 3): "EPC", (2, 3): "EPC", (3, 4): "EP",
    (4, 5): "EPCG", (0, 6): "C", (1, 6): "C", (2, 6): "CT", (4, 6): "CP",
    (5, 6): "CG", (2, 7): "W", (1, 7): "W", (0, 8): "MV", (1, 8): "MV",
    (2, 8): "MV", (4, 8): "MV", (7, 8): "V", (3, 8): "V",
}
# [end: n2]


def n2() -> None:
    n = len(SYSTEMS)
    lines = ["system-level interface (N-squared) matrix:",
             "  " + " " * 11 + "".join(f"{s[:5]:>6s}" for s in SYSTEMS)]
    rows = []
    for i in range(n):
        cells = []
        for j in range(n):
            k = LINKS.get((min(i, j), max(i, j)), "")
            cells.append(f"{'##':>6s}" if i == j else f"{k or '.':>6s}")
            if i < j and k:
                rows.append((i, j, k))
        lines.append(f"  {SYSTEMS[i]:11s}" + "".join(cells))
    kinds = {}
    for _, _, k in rows:
        for ch in k:
            kinds[ch] = kinds.get(ch, 0) + 1
    lines += [f"  {len(rows)} system pairs interface out of {n * (n - 1) // 2}; by kind:",
              "    " + ", ".join(f"{k} {v}" for k, v in sorted(kinds.items())),
              "  control touches every power system; civil touches every",
              "  thing that stands; each mark is an owner and a document"]
    emit("g_n2", lines)
    csv("ch18-n2.csv", "i,j,k", rows)


if __name__ == "__main__":
    flows()
    ring()
    substation()
    environment()
    n2()
