"""Battery cell, module and container manufacture arithmetic (chapter 45):
electrode balance and capacity from loading, self-discharge from a rest
test (K-value), cell matching into series strings, pack limits from the
cell, a BMS settings check against the cell data, an educational state-of-
charge simulator with invariants, moisture in the dry room, and material
accounting at the end of life.

Teaching relations only. Nothing here is a cell-making recipe or a
battery-management program; real values come from the cell maker and the
integrator with test evidence.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field


# ------------------------------------------------------------ electrode balance
def areal_capacity(loading_mg_cm2: float, active: float,
                   spec_mah_g: float) -> float:
    """Areal capacity (mAh/cm2) of an electrode coating: loading x active
    share x specific capacity of the active material."""
    return loading_mg_cm2 * active * spec_mah_g / 1000.0


def np_ratio(neg_mah_cm2: float, pos_mah_cm2: float) -> float:
    """Negative-to-positive capacity ratio of facing electrodes."""
    return neg_mah_cm2 / pos_mah_cm2


def cell_capacity_ah(pos_mah_cm2: float, area_cm2: float, first_eff: float) -> float:
    """Cell capacity (Ah) from the positive electrode's areal capacity, the
    total facing area and the share kept after the first cycle."""
    return pos_mah_cm2 * area_cm2 * first_eff / 1000.0


# ------------------------------------------------------------ rest test
def k_value(v_start: float, v_end: float, days: float) -> float:
    """Self-discharge indicator: open-circuit voltage drop (mV) a day."""
    return (v_start - v_end) * 1000.0 / days


# ------------------------------------------------------------ matching
def string_capacity(caps) -> float:
    """A series string can deliver only the capacity of its weakest cell."""
    return min(caps)


def match(caps, n_series: int, method: str = "sorted") -> list[list[float]]:
    """Split cells into strings of n_series: in arrival order ('random')
    or sorted so that neighbours in capacity share a string ('sorted')."""
    cells = sorted(caps) if method == "sorted" else list(caps)
    k = len(cells) // n_series
    return [cells[i * n_series:(i + 1) * n_series] for i in range(k)]


# ------------------------------------------------------------ pack limits
def pack_limits(n_s: int, n_p: int, q_ah: float, v_min: float, v_nom: float,
                v_max: float, c_max: float) -> dict:
    """Voltage window, nominal energy and current limit of a pack."""
    return dict(v_min=n_s * v_min, v_nom=n_s * v_nom, v_max=n_s * v_max,
                e_kwh=n_s * n_p * q_ah * v_nom / 1000.0,
                i_max=n_p * q_ah * c_max)


def bms_check(settings: dict, cell: dict, margin: dict) -> list:
    """Compare each BMS limit with the cell's data and the required margin:
    (name, setting, cell limit, ok). 'hi' limits must sit below the cell
    limit by the margin, 'lo' limits above it."""
    out = []
    for name, (kind, value) in settings.items():
        lim = cell[name]
        m = margin.get(name, 0.0)
        ok = value <= lim - m if kind == "hi" else value >= lim + m
        out.append((name, value, lim, ok))
    return out


# ------------------------------------------------------------ SOC simulator
# [start: socsim]
@dataclass
class SocSim:
    """Educational state-of-charge simulator of one battery (not a BMS).
    Current > 0 charges. The window [lo, hi] is never left: a request
    that would leave it is cut and the cut is recorded."""
    q_ah: float
    soc: float = 0.5
    lo: float = 0.10
    hi: float = 0.90
    eta_c: float = 0.995               # charge kept of charge put in
    ah_in: float = 0.0
    ah_out: float = 0.0
    refused_ah: float = 0.0
    log: list = field(default_factory=list)

    def step(self, i_a: float, dt_s: float) -> float:
        """Apply a current for dt_s; return the current actually taken."""
        if dt_s <= 0:
            raise ValueError("time step must be positive")
        ah = i_a * dt_s / 3600.0
        if ah >= 0:
            room = (self.hi - self.soc) * self.q_ah / self.eta_c
            take = min(ah, max(room, 0.0))
            self.soc += take * self.eta_c / self.q_ah
            self.ah_in += take
        else:
            room = (self.soc - self.lo) * self.q_ah
            take = -min(-ah, max(room, 0.0))
            self.soc += take / self.q_ah
            self.ah_out -= take
        self.refused_ah += abs(ah - take)
        if take != ah:
            self.log.append(("cut", round(ah, 6), round(take, 6)))
        return take * 3600.0 / dt_s

    def balance_error(self, soc0: float) -> float:
        """Invariant: charge kept minus charge taken equals the SOC change."""
        kept = self.ah_in * self.eta_c - self.ah_out
        return kept - (self.soc - soc0) * self.q_ah
# [end: socsim]


# ------------------------------------------------------------ dry room
def abs_humidity_g_m3(dew_c: float) -> float:
    """Water in air (g/m3) at a dew point, from the Magnus vapour pressure
    and the ideal gas (teaching accuracy)."""
    p_hpa = 6.112 * math.exp(17.62 * dew_c / (243.12 + dew_c))
    return 216.7 * p_hpa / (dew_c + 273.15)


# ------------------------------------------------------------ end of life
def recovered(masses_kg: dict, rates: dict) -> dict:
    """Mass recovered of each material at its recovery rate."""
    return {k: m * rates.get(k, 0.0) for k, m in masses_kg.items()}
