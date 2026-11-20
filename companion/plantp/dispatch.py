"""Battery dispatch by dynamic programming, chapter 3 (chapters 19 and 22 build on it).

    dp_arbitrage    best charge/discharge plan for one price series on a grid
                    of stored energies, by backward induction (Bellman)

Model: hourly steps of 1 h; charging c MW for one hour adds eta c MWh,
discharging d MW removes d / eta MWh (one-way efficiency eta);
|power| <= p_max; stored energy stays in [e_min, e_max]; the plan starts
and ends at e_start. Revenue = sum price (d - c).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class DPResult:
    revenue: float
    energy: np.ndarray        # stored energy at hour boundaries, T + 1 values
    power: np.ndarray         # grid power per hour: + discharge, - charge (MW)
    states: int


def dp_arbitrage(price, p_max: float, e_min: float, e_max: float,
                 e_start: float, eta: float, step: float,
                 wear: float = 0.0) -> DPResult:
    """wear: cost per MWh discharged; revenue is then net of wear."""
    price = np.asarray(price, dtype=float)
    grid = np.arange(e_min, e_max + step / 2, step)
    if not np.any(np.isclose(grid, e_start)):
        raise ValueError("e_start must lie on the energy grid")
    n_s, n_t = grid.size, price.size
    i_start = int(np.argmin(np.abs(grid - e_start)))
    # [start: bellman]
    delta = grid[None, :] - grid[:, None]      # change [from, to] in MWh
    power = np.where(delta > 0, -delta / eta, -delta * eta)  # + discharge
    allowed = np.abs(power) <= p_max + 1e-9
    worn = wear * np.maximum(power, 0.0)       # wear cost of each move
    value = np.full(n_s, -np.inf)              # value after the last hour:
    value[i_start] = 0.0                       # only "back at start" counts
    choice = np.zeros((n_t, n_s), dtype=int)
    for t in range(n_t - 1, -1, -1):           # backward in time
        gain = price[t] * power - worn + value[None, :]
        gain[~allowed] = -np.inf
        choice[t] = np.argmax(gain, axis=1)    # best next state from each
        value = gain[np.arange(n_s), choice[t]]
    path = [i_start]                           # forward: follow choices
    for t in range(n_t):
        path.append(int(choice[t, path[-1]]))
    # [end: bellman]
    energy = grid[path]
    p = power[path[:-1], path[1:]]
    return DPResult(float(value[i_start]), energy, p, n_s)


# ---- chapter 5: a rule-based daily dispatch, written to be tested ---------
@dataclass
class RuleResult:
    export_mw: np.ndarray       # at the point of connection, after the BESS
    charge_mw: np.ndarray       # AC power into the battery (>= 0)
    discharge_mw: np.ndarray    # AC power out of the battery (>= 0)
    soc_mwh: np.ndarray         # stored energy at the END of each hour


def rule_based_shift(gen_mw, charge_hours, discharge_hours, p_max: float,
                     usable_mwh: float, roundtrip: float, limit_mw: float,
                     soc0: float = 0.0) -> RuleResult:
    """Charge from on-site generation in charge_hours and discharge in
    discharge_hours (clock hours 0..23; the series starts at 00:00).

    Rules: never charge from the grid (charge <= generation); never export
    more than limit_mw; |power| <= p_max; 0 <= soc <= usable_mwh.
    One-way efficiency sqrt(roundtrip) on charge and on discharge.
    """
    gen = np.asarray(gen_mw, dtype=float)
    eta = float(np.sqrt(roundtrip))
    n = gen.size
    ch, dis, soc = np.zeros(n), np.zeros(n), np.zeros(n)
    e = soc0                                    # stored energy, MWh
    for k in range(n):
        h = k % 24
        if h in charge_hours:
            ch[k] = min(p_max, gen[k], (usable_mwh - e) / eta)
            e += ch[k] * eta
        elif h in discharge_hours:
            room = max(limit_mw - gen[k], 0.0)  # free export capacity
            dis[k] = min(p_max, e * eta, room)
            e -= dis[k] / eta
        e = min(max(e, 0.0), usable_mwh)
        soc[k] = e
    export = np.minimum(gen - ch + dis, limit_mw)
    return RuleResult(export, ch, dis, soc)
