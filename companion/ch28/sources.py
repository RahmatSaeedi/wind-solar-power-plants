"""Chapter 28 - the study model of Plant P from the POC to the units
(teaching values A-341 to A-345, from chapters 17, 23, 24 and 25).

Per unit on 100 MVA. Buses: 0 grid source, 1 POC (132 kV), 2 plant HV
bus, 3 MV-A, 4 MV-B (33 kV), then one end bus and one aggregated unit bus
for each of the eight feeders. A feeder is modelled at half its length
(generation spread along it); its unit transformers are aggregated.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from companion.ch28 import common  # noqa: F401  (puts plantp on the path)
from plantp import gridstudy as gs

S_BASE = 100.0
W = 2 * math.pi * 50

# [start: grid]
GRID = {   # Thevenin source at the POC (A-341)
    "max": dict(s_sc=1500.0, xr=8.0),      # ch 17, all network in service
    "min": dict(s_sc=900.0, xr=6.0),       # one grid transformer out (teaching)
}
LINE = dict(km=7.06, r=0.12, x=0.40, c_nf=9.0, kv=132.0, rating_a=650.0)
MAIN = dict(s_mva=63.0, uk=0.12, pk_kw=250.0, p0_kw=35.0, tap_step=0.0125, taps=8)
# [end: grid]

# [start: feeders]
@dataclass(frozen=True)
class Feeder:
    name: str
    side: int            # 3 = MV-A, 4 = MV-B
    units: int
    unit_mva: float      # rating of one unit (converter) at 1.0 pu voltage
    unit_mw: float
    section: int         # mm2 of the equivalent cable
    km: float            # route length
    kind: str            # wind / pv / bess


FEEDERS = (
    Feeder("WS1", 3, 4, 5.6, 5.0, 630, 4.4, "wind"),
    Feeder("WS2", 3, 4, 5.6, 5.0, 630, 4.8, "wind"),
    Feeder("PVF3", 3, 3, 5.5, 5.0, 400, 2.2, "pv"),
    Feeder("BESS-A", 3, 2, 5.0, 5.0, 240, 0.3, "bess"),
    Feeder("WS3", 4, 4, 5.6, 5.0, 630, 5.2, "wind"),
    Feeder("PVF1", 4, 4, 5.5, 5.0, 400, 2.4, "pv"),
    Feeder("PVF2", 4, 3, 5.5, 5.0, 400, 2.0, "pv"),
    Feeder("BESS-B", 4, 2, 5.0, 5.0, 240, 0.3, "bess"),
)
CABLE = {240: (0.125, 0.116, 0.21), 400: (0.0778, 0.108, 0.25), 630: (0.0469, 0.101, 0.30)}
UNIT_TX = dict(uk=0.06, pk_per_mva_kw=9.0)     # aggregated unit transformers (A-342)
# [end: feeders]

NAMES = ["GRID", "POC", "HV", "MV-A", "MV-B"] + [f.name for f in FEEDERS] + \
        [f.name + "-U" for f in FEEDERS]
N = len(NAMES)


def r_hot(r20: float, temp: float = 70.0) -> float:
    return r20 * (1 + 0.00403 * (temp - 20))


def branches(grid: str = "max", tap=(1.0, 1.0), coupler: bool = False,
             out=(), line_scale: float = 1.0) -> list:
    """Branch list of the study model. out names elements out of service:
    'T1', 'T2', 'LINE' or a feeder name."""
    zg = gs.thevenin(GRID[grid]["s_sc"], GRID[grid]["xr"], S_BASE)
    zb132 = LINE["kv"] ** 2 / S_BASE
    zb33 = 33.0 ** 2 / S_BASE
    br = [gs.Branch(0, 1, zg.real, zg.imag)]
    km = LINE["km"] * line_scale
    br.append(gs.Branch(1, 2, LINE["r"] * km / zb132, LINE["x"] * km / zb132,
                        W * LINE["c_nf"] * 1e-9 * km * zb132, status="LINE" not in out))
    xt = MAIN["uk"] * S_BASE / MAIN["s_mva"]
    rt = MAIN["pk_kw"] / 1e3 / MAIN["s_mva"] * S_BASE / MAIN["s_mva"]
    br.append(gs.Branch(2, 3, rt, xt, tap=tap[0], status="T1" not in out))
    br.append(gs.Branch(2, 4, rt, xt, tap=tap[1], status="T2" not in out))
    br.append(gs.Branch(3, 4, 1e-5, 1e-4, status=coupler))
    for k, f in enumerate(FEEDERS):
        r20, x, c = CABLE[f.section]
        half = f.km / 2
        br.append(gs.Branch(f.side, 5 + k, r_hot(r20) * half / zb33, x * half / zb33,
                            W * c * 1e-6 * f.km * zb33, status=f.name not in out))
        s_agg = f.units * f.unit_mva
        xu = UNIT_TX["uk"] * S_BASE / s_agg
        ru = UNIT_TX["pk_per_mva_kw"] / 1e3 * S_BASE / s_agg
        br.append(gs.Branch(5 + k, 13 + k, ru, xu, status=f.name not in out))
    return br


# [start: solve]
def solve(p_share: dict, q_pu: float, grid: str = "max", e: float = 1.0,
          tap=(1.0, 1.0), **kw) -> dict:
    """Load flow with each feeder's units at p_share[kind] of their MW and
    reactive power q_pu of their MVA (generator convention). A kind not
    named in p_share is not built (S0: no 'bess' key, no battery)."""
    out = tuple(kw.pop("out", ())) + tuple(f.name for f in FEEDERS
                                           if f.kind not in p_share)
    br = branches(grid, tap, out=out, **kw)
    kind = ["slack"] + ["pq"] * (N - 1)
    p, q = np.zeros(N), np.zeros(N)
    for k, f in enumerate(FEEDERS):
        if f.name in out:
            continue
        p[13 + k] = f.units * f.unit_mw * p_share.get(f.kind, 0.0) / S_BASE
        qk = q_pu.get(f.kind, 0.0) if isinstance(q_pu, dict) else q_pu
        q[13 + k] = f.units * f.unit_mva * qk / S_BASE
    res = gs.load_flow(gs.ybus(N, br), kind, p, q, [e] + [1.0] * (N - 1))
    fl = gs.flows(res["v"], br)
    s_poc = -fl[1]["s_ij"] * S_BASE if br[1].status else 0j
    loss = sum(f_["loss"].real for f_ in fl[1:]) * S_BASE
    return {"v": np.abs(res["v"]), "s_poc": s_poc, "loss_mw": loss, "flows": fl,
            "branches": br, "p_units": p.sum() * S_BASE, "q_units": q.sum() * S_BASE,
            "iterations": res["iterations"]}
# [end: solve]


def q_for_target(p_share: dict, target: float, quantity: str = "q_poc",
                 lo: float = -0.3, hi: float = 0.5, **kw) -> tuple:
    """Uniform unit reactive power (pu of unit MVA) that gives the target
    reactive power (MVAr) or voltage (pu) at the POC; bisection."""
    def g(qu):
        r = solve(p_share, qu, **kw)
        return (r["s_poc"].imag if quantity == "q_poc" else r["v"][1]) - target
    a, b = lo, hi
    ga = g(a)
    for _ in range(60):
        m = 0.5 * (a + b)
        gm = g(m)
        if (gm > 0) == (ga > 0):
            a, ga = m, gm
        else:
            b = m
    qu = 0.5 * (a + b)
    return qu, solve(p_share, qu, **kw)


NOLOAD_MW = (2 * MAIN["p0_kw"] + 12 * 7.0 + 10 * 4.5) / 1e3    # S0 transformers energised


def unit_limit_q(v_unit: float, p_mw: float, s_mva: float) -> float:
    """Reactive capability (pu of the unit's MVA) of a current-limited
    unit at voltage v_unit delivering p_mw: S = v_unit x rating."""
    s = v_unit * s_mva
    return math.sqrt(max(s * s - p_mw * p_mw, 0.0)) / s_mva


def oltc(p_share: dict, q_pu, **kw) -> tuple:
    """Main-transformer taps (both alike, HV side) that hold the 33 kV
    bus nearest 1.00 pu, in 1.25 % steps within +/-10 %."""
    t = 1.0
    r = solve(p_share, q_pu, tap=(t, t), **kw)
    for _ in range(8):
        t_new = 1 + round((t * r["v"][3] - 1) / MAIN["tap_step"]) * MAIN["tap_step"]
        t_new = min(max(t_new, 0.9), 1.1)
        if abs(t_new - t) < 1e-9:
            break
        t = t_new
        r = solve(p_share, q_pu, tap=(t, t), **kw)
    r["tap"] = t
    return t, r


def q_limits(p_share: dict, sign: float = 1.0, band=(0.90, 1.10),
             derate: float = 1.0, **kw) -> dict:
    """Largest reactive power the units give (sign +1) or absorb (-1):
    each kind at a share lam of its current limit at 1.0 pu (times a
    temperature derating), the taps holding the 33 kV bus, and lam cut
    until every unit terminal stays inside the voltage band (or the load
    flow solves at all)."""
    qmax = {f.kind: unit_limit_q(derate, f.unit_mw * p_share[f.kind], f.unit_mva)
            for f in FEEDERS if f.kind in p_share}

    def run(lam):
        try:
            _, r = oltc(p_share, {k: sign * lam * v for k, v in qmax.items()}, **kw)
        except RuntimeError:
            return None
        vu = [r["v"][13 + k] for k, f in enumerate(FEEDERS) if f.kind in p_share]
        return r if band[0] <= min(vu) and max(vu) <= band[1] else None

    r = run(1.0)
    if r is not None:
        r["lam"] = 1.0
        return r
    lo, hi = 0.0, 1.0
    best = run(0.0)
    for _ in range(25):
        m = 0.5 * (lo + hi)
        rm = run(m)
        if rm is None:
            hi = m
        else:
            lo, best = m, rm
    best["lam"] = lo
    return best
