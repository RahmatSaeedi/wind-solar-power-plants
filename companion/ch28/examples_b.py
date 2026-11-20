"""Chapter 28, lesson B: steady-state and fault studies of Plant P -
load-flow cases with the controller and the tap changers, the reactive
balance and capability at the POC, losses against the energy model,
fault currents with converters as limited sources, what a distance
relay at each end of the line sees, and a load flow checked against
SCADA snapshots.

Run from the project root:   python -m companion.ch28.examples_b
Writes companion/ch28/expected/b_*.txt and diagrams/data/ch28-*.csv.
Teaching values (A-341 to A-345).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch28 import sources as src
from companion.ch28.common import csv, emit
from plantp import gridstudy as gs

FULL = {"wind": 1.0, "pv": 0.84}          # about 100 MW at the POC (S0)


def operate(ps: dict, q_target: float = 0.0, **kw) -> tuple:
    """Plant controller (Q at the POC) and tap changers together."""
    t = 1.0
    for _ in range(5):
        qu, r = src.q_for_target(ps, q_target, tap=(t, t), **kw)
        t_new, r = src.oltc(ps, qu, **kw)
        if abs(t_new - t) < 1e-9:
            break
        t = t_new
    return qu, t, r


def cases() -> None:
    lines = ["load-flow cases at full output, Q = 0 at the POC (S0, teaching)",
             "  grid  source   tap %   V POC   V MV-A   V unit max   unit q pu   loss MW"]
    rows, qs = [], []
    for g in ("max", "min"):
        for e in (0.95, 1.00, 1.05):
            qu, t, r = operate(FULL, grid=g, e=e)
            qs.append(qu)
            vu = max(r["v"][13:])
            lines.append(f"  {g:4s}  {e:6.2f}   {100 * (t - 1):+5.1f}   {r['v'][1]:5.3f}   "
                         f"{r['v'][3]:6.3f}   {vu:10.3f}   {qu:9.3f}   {r['loss_mw']:7.2f}")
            if g == "max":
                rows.append((e, r))
    night = src.solve({"wind": 0.0, "pv": 0.0}, 0.0)
    lines += [f"  night, units idle: POC gets {night['s_poc'].imag:+.1f} Mvar from cables and line,"
              f" V POC {night['v'][1]:.3f}",
              "  the taps keep the 33 kV bus near 1.00 and the units inside",
              f"  their band in every case; the units supply about {100 * np.mean(qs):.0f} % of",
              "  their rating as reactive power just to cancel what the",
              "  transformers and line absorb at full output"]
    emit("b_cases", lines)
    names = ["POC", "HV", "MV-A", "WS1", "PVF3", "WS1-U", "PVF3-U"]
    idx = [1, 2, 3, 5, 7, 13, 15]
    csv("ch28-voltages.csv", "k,name,e095,e100,e105",
        [(k, n, *(f"{r['v'][i]:.4f}" for _, r in rows)) for k, (n, i) in enumerate(zip(names, idx))])


def reactive() -> None:
    qu, t, r = operate(FULL)
    fl = r["flows"]
    q = lambda ks: sum(fl[k]["loss"].imag for k in ks) * src.S_BASE   # noqa: E731
    unit_tx = [6 + 2 * k for k in range(len(src.FEEDERS))]
    cables = [5 + 2 * k for k in range(len(src.FEEDERS))]
    parts = [("unit transformers", q(unit_tx)), ("33 kV cables", q(cables)),
             ("main transformers", q([2, 3])), ("132 kV line", q([1]))]
    lines = ["reactive balance at full output with Q = 0 at the POC (grid max, 1.00)",
             f"  units supply                      {r['q_units']:6.1f} Mvar"]
    for name, v in parts:
        lines.append(f"  absorbed by {name:21s} {v:6.1f} Mvar")
    lines.append(f"  delivered at the POC              {r['s_poc'].imag:6.1f} Mvar")
    lines += ["", "reactive capability at the POC at full output (units inside 0.90-1.10 pu)",
              "  grid  source   giving Mvar  (share)   absorbing Mvar  (share)"]
    for g in ("max", "min"):
        for e in (0.95, 1.00, 1.05):
            hi = src.q_limits(FULL, 1, grid=g, e=e)
            lo = src.q_limits(FULL, -1, grid=g, e=e)
            lines.append(f"  {g:4s}  {e:6.2f}   {hi['s_poc'].imag:11.1f}  ({hi['lam']:4.2f})"
                         f"   {lo['s_poc'].imag:14.1f}  ({lo['lam']:4.2f})")
    lines += ["  share = part of the units' current limit usable before a",
              "  terminal leaves its band; a teaching requirement of +/-33",
              "  Mvar at 100 MW is met in every case; the least margin is",
              "  in giving: 40 Mvar on the weak grid at 1.05, where unit",
              "  terminals reach 1.10, and about 46 elsewhere - below the",
              "  simpler estimate of ch 27 (56 Mvar), which left out the",
              "  unit transformers"]
    emit("b_reactive", lines)


def losses() -> None:
    from companion.ch15 import sources as s15
    p_list = np.arange(10, 101, 10.0)
    rows, loss = [], []
    for p in p_list:
        ps = {"wind": p / 110, "pv": p / 110}
        qu, r = src.q_for_target(ps, 0.0)
        loss.append(r["loss_mw"])
        rows.append((f"{p:.0f}", f"{r['loss_mw'] + src.NOLOAD_MW:.3f}",
                     f"{0.10 + 0.015 * 100 * (p / 100) ** 2:.3f}"))
    loss = np.array(loss)
    b = float(np.sum(loss * p_list ** 2) / np.sum(p_list ** 4))
    csv("ch28-losses.csv", "p,flow,model15", rows)
    y = s15.plant_year()
    mv = np.clip(y["mv"], 0, 110)
    annual = (b * np.sum(mv ** 2) + src.NOLOAD_MW * 8760) / 1e3
    lines = ["electrical losses from the unit terminals to the POC (Q = 0 at the POC)",
             "  units MW   load flow + no-load MW   model 15.1 MW"]
    for (p, f, m) in rows[1::2]:
        lines.append(f"  {p:>8s}   {float(f):22.2f}   {float(m):13.2f}")
    lines += [f"  fit: load losses = {b * 1e4:.2f} x (P/100)^2 MW;"
              f" no-load {1e3 * src.NOLOAD_MW:.0f} kW all year",
              f"  a year of model 15.1's hourly output: {annual:.2f} GWh lost;",
              f"  model 15.1 says {y['el_loss'].sum() / 1e3:.2f} GWh",
              "  the energy model's 1.5 % at 100 MW and 0.10 MW no-load",
              "  are below the study's values: the unit transformers and",
              "  the reactive current were not in them - the next model",
              "  version takes the study's curve (a finding for ch 15/16)"]
    emit("b_losses", lines)


def short_circuit() -> None:
    lines = ["three-phase fault currents (kA), converters as 1.1 pu current sources",
             "  bus      kV    max: grid  converters  total    min: grid only   rating"]
    rating = {132: 31.5, 33: 25.0}
    bars = []
    for name, k, kv in (("POC", 1, 132), ("HV", 2, 132), ("MV-A", 3, 33), ("WS1 end", 5, 33)):
        res = {}
        for case, c in (("max", 1.1), ("min", 1.0)):
            br = src.branches(case)
            y = gs.ybus(src.N, br)[1:, 1:]
            zb = np.linalg.inv(y)
            sources = [(13 + j - 1, f.units * f.unit_mva * 1.1 / src.S_BASE)
                       for j, f in enumerate(src.FEEDERS) if f.kind != "bess"]
            res[case] = gs.fault_current(zb, k - 1, c, sources if case == "max" else ())
        ib = src.S_BASE / (math.sqrt(3) * kv)
        mx, mn = res["max"], res["min"]
        lines.append(f"  {name:8s} {kv:4d}   {mx['grid'] * ib:9.2f}  {mx['converters'] * ib:10.2f}"
                     f"  {mx['total'] * ib:5.2f}   {mn['grid'] * ib:14.2f}   {rating[kv]:6.1f}")
        bars.append((name, f"{mx['grid'] * ib:.2f}", f"{mx['converters'] * ib:.2f}",
                     f"{mn['grid'] * ib:.2f}"))
    csv("ch28-faults.csv", "bus,grid,conv,min", bars)
    lines += ["  the converters add little at 132 kV and more at 33 kV,",
              "  where they sit close; switchgear is checked with the",
              "  maximum (c 1.1 and every source), protection reach and",
              "  sensitivity with the minimum (c 1.0, converters left out",
              "  because their fault current is controlled, not physical)"]
    emit("b_sc", lines)


def infeed() -> None:
    zb132 = 132.0 ** 2 / src.S_BASE
    z_line = complex(src.LINE["r"], src.LINE["x"]) * src.LINE["km"]
    zg = gs.thevenin(src.GRID["max"]["s_sc"], src.GRID["max"]["xr"]) * zb132
    i_grid = 1.0 / zg * 132e3 / math.sqrt(3)                    # A, near the POC
    i_plant = -1j * 1.1 * 122.2e6 / (math.sqrt(3) * 132e3)      # A, reactive, 1.1 pu
    x_reach, r_reach = 0.8 * z_line.imag, 10.0
    pts = []
    lines = ["a fault half-way along the 132 kV line through a resistance R_f:",
             "  impedance seen by the distance relay at each end (ohm, primary)",
             f"  current into the fault: grid {abs(i_grid):.0f} A, plant {abs(i_plant):.0f} A"
             f" (full-load current 437 A)",
             "  R_f ohm   grid end R + jX       seen?   plant end R + jX      seen?"]
    for rf in (0.0, 1.0, 2.0, 5.0):
        z_half = z_line / 2
        zg_end = gs.apparent_impedance(z_half, rf, i_grid, i_plant)
        zp_end = gs.apparent_impedance(z_half, rf, i_plant, i_grid)
        seen = lambda z: z.imag <= x_reach and 0 <= z.real <= r_reach  # noqa: E731
        lines.append(f"  {rf:7.1f}   {zg_end.real:6.2f} {zg_end.imag:+6.2f}j     "
                     f"{'yes' if seen(zg_end) else 'NO':5s}   {zp_end.real:7.2f} {zp_end.imag:+6.2f}j"
                     f"    {'yes' if seen(zp_end) else 'NO'}")
        pts.append((f"{rf:.0f}", f"{zg_end.real:.3f}", f"{zg_end.imag:.3f}",
                    f"{min(zp_end.real, 40):.3f}", f"{zp_end.imag:.3f}"))
    csv("ch28-rx.csv", "rf,rg,xg,rp,xp", pts)
    lines += [f"  zone 1: X up to {x_reach:.2f} ohm, R up to {r_reach:.0f} ohm (teaching)",
              "  the grid end sees each fault; the plant end sees only the",
              "  bolted one - the grid's infeed multiplies the fault",
              "  resistance about twelve times, and the plant's fault",
              "  current is barely above full load: the line needs a",
              "  differential scheme or an intertrip to clear its plant end"]
    emit("b_infeed", lines)


def validation() -> None:
    rng = np.random.default_rng(281)
    snaps = [(0.2, 0.1, 1.00, 0), (0.5, 0.4, 1.01, 0), (0.8, 0.7, 1.02, 1),
             (1.0, 0.84, 1.03, 2), (0.6, 0.0, 0.99, 0), (0.9, 0.5, 1.00, 1)]
    recorded_taps = [0, 0, 1, 0, 0, 1]          # SCADA tap reading (snapshot 4 wrong)
    lines = ["load flow against six SCADA snapshots (synthetic 'measured' values)",
             "  snap   P POC MW   V MV meas   V MV model   dV %    Q POC meas  model   check"]
    for k, ((w, pv, e, tap), rec) in enumerate(zip(snaps, recorded_taps), 1):
        ps = {"wind": w, "pv": pv}
        t_true = 1 + tap * src.MAIN["tap_step"]
        meas = src.solve(ps, 0.05, e=e, tap=(t_true, t_true))
        v_meas = meas["v"][3] * (1 + 0.001 * rng.standard_normal())
        q_meas = meas["s_poc"].imag + 0.3 * rng.standard_normal()
        t_rec = 1 + rec * src.MAIN["tap_step"]
        mod = src.solve(ps, 0.05, e=e, tap=(t_rec, t_rec))
        dv = 100 * (mod["v"][3] - v_meas)
        ok = abs(dv) <= 1.0 and abs(mod["s_poc"].imag - q_meas) <= 2.0
        lines.append(f"  {k:4d}   {meas['s_poc'].real:8.1f}   {v_meas:9.3f}   {mod['v'][3]:10.3f}"
                     f"   {dv:+5.2f}   {q_meas:10.1f}  {mod['s_poc'].imag:5.1f}   {'ok' if ok else 'CHECK'}")
    lines += ["  teaching acceptance: 33 kV voltage within 1 %, Q within 2 Mvar;",
              "  snapshot 4 fails on voltage only: the model is right, the",
              "  SCADA tap reading is two steps behind the real tap - a",
              "  validation finds data errors as often as model errors"]
    emit("b_validation", lines)


if __name__ == "__main__":
    cases()
    reactive()
    losses()
    short_circuit()
    infeed()
    validation()
