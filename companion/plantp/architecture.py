"""Plant architecture (chapter 18): conversion chains of AC- and DC-coupled
storage, collector and export options (current, losses, voltage drop,
cable charging, unserved energy), the product breakdown tree, interface
records with mismatch checks, and a monthly water source/use balance.

Powers in MW, energies in MWh, lengths in km unless stated.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np


# ------------------------------------------------------------ coupling
# [start: chains]
def chain(*effs: float) -> float:
    """Efficiency of conversions in series."""
    out = 1.0
    for e in effs:
        out *= e
    return out


def ac_coupled(eta_pv_inv: float, eta_bess_inv: float,
               eta_cell: float) -> dict:
    """PV energy stored and returned through two AC inverters."""
    store = chain(eta_pv_inv, eta_bess_inv, math.sqrt(eta_cell))
    back = chain(math.sqrt(eta_cell), eta_bess_inv)
    return {"pv_to_grid_via_battery": store * back, "battery_round_trip":
            chain(eta_bess_inv, eta_cell, eta_bess_inv)}


def dc_coupled(eta_pv_inv: float, eta_dcdc: float, eta_cell: float) -> dict:
    """PV DC energy stored through a DC/DC converter and sent out through
    the PV inverter."""
    store = chain(eta_dcdc, math.sqrt(eta_cell))
    back = chain(math.sqrt(eta_cell), eta_dcdc, eta_pv_inv)
    return {"pv_to_grid_via_battery": store * back, "battery_round_trip":
            chain(eta_dcdc, eta_cell, eta_dcdc)}
# [end: chains]


# ------------------------------------------------------------ circuits
# [start: circuits]
def current_ka(p_mw, v_kv: float, pf: float = 1.0):
    """Line current of a three-phase circuit, kA."""
    return np.asarray(p_mw, float) / (math.sqrt(3) * v_kv * pf)


def loss_mw(p_mw, v_kv: float, r_ohm: float, pf: float = 1.0):
    """Three-phase I^2 R loss, MW."""
    i = current_ka(p_mw, v_kv, pf)
    return 3.0 * i * i * r_ohm


def drop_pct(p_mw, v_kv: float, r_ohm: float, x_ohm: float, pf: float = 1.0):
    """Approximate voltage drop in per cent, (R P + X Q) / V^2."""
    p = np.asarray(p_mw, float)
    q = p * math.tan(math.acos(pf))
    return 100.0 * (r_ohm * p + x_ohm * q) / v_kv ** 2


def charging_mvar(v_kv: float, c_uf_per_km: float, km: float,
                  f_hz: float = 50.0) -> float:
    """Reactive power a cable produces at voltage, Mvar (V^2 w C l)."""
    return v_kv ** 2 * 2 * math.pi * f_hz * c_uf_per_km * 1e-6 * km


def unserved_mwh(p_mw, failures_per_yr: float, repair_h: float,
                 circuits: int = 1, rating_mw: float = 1e9) -> float:
    """Expected export lost to circuit outages: with one circuit every
    outage hour loses the plant's output; with two, an outage of one
    loses only what exceeds the other's rating (independent failures,
    no overlap). p_mw is the hourly export of one year."""
    p = np.asarray(p_mw, float)
    mean_loss = p.mean() if circuits == 1 else np.clip(p - rating_mw, 0, None).mean()
    return float(failures_per_yr * circuits * repair_h * mean_loss)
# [end: circuits]


# ------------------------------------------------------------ breakdown
@dataclass
class Node:
    name: str
    level: str                       # plant, system, subsystem, equipment, unit
    count: int = 1
    make_buy: str = ""               # buy, make, buy+integrate
    children: list = field(default_factory=list)

    def add(self, *kids):
        self.children.extend(kids)
        return self

    def walk(self, mult: int = 1, depth: int = 0):
        n = mult * self.count
        yield self, n, depth
        for c in self.children:
            yield from c.walk(n, depth + 1)


# ------------------------------------------------------------ interfaces
# [start: interfaces]
@dataclass
class Interface:
    iid: str
    kind: str          # electrical, mechanical, thermal, comms, ...
    side_a: str
    side_b: str
    item: str          # the parameter both sides must agree on
    value_a: object
    value_b: object
    tol: float = 0.0   # allowed relative difference for numbers
    owner: str = ""

    def mismatch(self) -> str:
        """Empty when both sides agree, else a short reason."""
        a, b = self.value_a, self.value_b
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            if b == 0 or abs(a - b) / abs(b) > self.tol:
                return f"{a} against {b} (tol {100 * self.tol:.0f} %)"
            return ""
        if isinstance(b, (set, frozenset, tuple, list)):
            return "" if a in b else f"{a} not in {sorted(b)}"
        return "" if a == b else f"{a} against {b}"
# [end: interfaces]


# ------------------------------------------------------------ water
def water_balance(supply_m3, demand: dict, store_m3: float,
                  reserve_m3: float, start_m3: float | None = None):
    """Monthly balance with a tank: the reserve (fire, emergency) is held
    and never used for operations. Returns the end-of-month stock of
    usable water and the unmet demand per month (m3)."""
    supply = np.asarray(supply_m3, float)
    use = np.sum([np.asarray(v, float) for v in demand.values()], axis=0)
    usable_cap = store_m3 - reserve_m3
    s = usable_cap if start_m3 is None else start_m3
    stock, unmet = [], []
    for k in range(len(supply)):
        s = s + supply[k] - use[k]
        short = max(-s, 0.0)
        s = min(max(s, 0.0), usable_cap)
        stock.append(s)
        unmet.append(short)
    return np.array(stock), np.array(unmet)
