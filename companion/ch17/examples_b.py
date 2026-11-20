"""Chapter 17, section B - Plant P at the grid node: net flow at the grid
substation (local use, upward flow, import), the upstream transfer limit
as a bounded check, the voltage rise along the export line, the line's
thermal margin and the short-circuit ratio. Screening only: the grid
operator's studies decide (chapter 28).

Run from the project root:   python -m companion.ch17.examples_b
Writes companion/ch17/expected/b_*.txt and diagrams/data/ch17-*.csv.
Network teaching values A-285; plant model 15.1.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch15 import sources as s15
from companion.ch17 import sources as src
from companion.ch17.common import csv, emit
from plantp import demand as dm

N = src.NETWORK


def netflow() -> None:
    r = s15.plant_year()
    gen = np.clip(r["net"], 0, None)
    load = src.regional()["total"]
    f = dm.net_flow(load, gen)
    up = f > 0
    over = np.clip(f - N["upstream_mw"], 0, None)
    lines = ["flow at the grid substation's 132 kV bus (Plant P export minus",
             "  the regional load; positive = flowing up into the network):",
             f"  hours flowing up {int(up.sum())}; energy up {f[up].sum() / 1e3:.1f} GWh",
             f"  local use of the plant's energy {np.minimum(gen, load).sum() / 1e3:.1f} GWh"
             f" of {gen.sum() / 1e3:.1f} GWh",
             f"  largest upward flow {f.max():.1f} MW; upstream limit {N['upstream_mw']:.0f} MW"
             " (teaching)",
             f"  hours above the limit {int((over > 0).sum())}; energy above it"
             f" {over.sum() / 1e3:.2f} GWh",
             "  if the network beyond could take less (teaching limits):"]
    for lim in (50, 60, 70, 80):
        ov = np.clip(f - lim, 0, None)
        lines.append(f"    {lim} MW: {int((ov > 0).sum()):4d} h above, {ov.sum() / 1e3:5.2f} GWh to curtail")
    lines += ["  a bounded check, not a study: if the network beyond cannot take",
              "  the flow, the operator limits the plant (chapter 15 curtailment)"]
    emit("b_netflow", lines)
    fd = np.sort(f)[::-1]
    csv("ch17-netflow.csv", "h,f", [(i, f"{fd[i]:.2f}") for i in range(0, 8760, 20)])


def voltage() -> None:
    R = N["r_ohm_km"] * N["line_km"]
    X = N["x_ohm_km"] * N["line_km"]
    lines = [f"export line {N['line_km']} km at {N['v_kv']:.0f} kV: R {R:.3f}, X {X:.3f} ohm"
             " (teaching)",
             "  voltage rise at the plant end, dV/V = (R P + X Q) / V^2:",
             "  P MW    Q Mvar   rise %"]
    for p, q in ((100, 0), (100, 32.9), (100, -32.9), (50, 0)):
        lines.append(f"  {p:4d}   {q:6.1f}   {float(dm.voltage_rise(p, q, R, X, N['v_kv'])):6.2f}")
    lines += ["  this short 132 kV line moves the voltage by about half a per",
              "  cent at unity power factor and one per cent with reactive",
              "  export; reactive power moves it more than active (X > R);",
              "  the grid code's voltage window and the operator's studies",
              "  decide the reactive mode (chapters 25 and 28)"]
    emit("b_voltage", lines)


def thermal_scr() -> None:
    s_max = 100 / 0.95
    scr = dm.short_circuit_ratio(N["s_sc_mva"], 100.0)
    lines = ["thermal and system-strength screening (teaching values):",
             f"  export at the limit, pf 0.95: {s_max:.1f} MVA; line rating"
             f" {N['line_rating_mva']:.0f} MVA:"
             f" {'ok' if dm.thermal_ok(s_max, N['line_rating_mva']) else 'over'}",
             f"  short-circuit power at the POC {N['s_sc_mva']:.0f} MVA; ratio to 100 MW: {scr:.1f}",
             f"  with the 110 MW installed: {N['s_sc_mva'] / 110:.1f}",
             "  a high ratio means a 'strong' node where inverters behave",
             "  well; a low one needs studies of control stability; the",
             "  operator gives the short-circuit power for normal and",
             "  outage cases (data request)"]
    emit("b_thermal", lines)


if __name__ == "__main__":
    netflow()
    voltage()
    thermal_scr()
