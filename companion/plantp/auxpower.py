"""Chapter 23 - auxiliary and control power: load registers by operating
state, demand with duty and diversity, kW/kVA and power factor,
standard transformer sizes, motor-starting voltage dip, short-circuit
current behind a transformer, DC battery sizing from a duty cycle,
charger and UPS sizing, a simple HVAC heat balance, load shedding by
priority and a restoration timeline.

Teaching methods only: equipment is sized from the makers' data and the
applicable standards by qualified engineers.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

STATES = ("normal", "degraded", "emergency", "maintenance")
STD_KVA = (100, 160, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500)


# [start: load]
@dataclass
class Load:
    tag: str
    kw: float                       # input power at full duty
    pf: float = 0.9
    kind: str = "continuous"        # continuous, intermittent, startup
    essential: bool = False
    duty: dict = field(default_factory=dict)   # state -> duty factor 0..1
    priority: int = 9               # 1 = shed last
    motor_start_kva: float = 0.0    # starting kVA of a direct-on-line motor

    def kw_in(self, state: str) -> float:
        return self.kw * self.duty.get(state, 0.0)


def demand(loads, state: str, diversity: float = 1.0):
    """(kW, kvar, kVA) of a register in one operating state; the
    diversity factor (<= 1) applies to the sum of the loads."""
    p = sum(ld.kw_in(state) for ld in loads)
    q = sum(ld.kw_in(state) * math.tan(math.acos(ld.pf)) for ld in loads)
    p, q = p * diversity, q * diversity
    return p, q, math.hypot(p, q)
# [end: load]


# [start: sizing]
def next_size(kva: float, margin: float = 0.2, sizes=STD_KVA) -> int:
    """Smallest standard rating at or above demand x (1 + margin)."""
    need = kva * (1 + margin)
    for s in sizes:
        if s >= need:
            return s
    raise ValueError(f"{need:.0f} kVA above the largest size")


def sc_current_ka(s_kva: float, u_kv: float, z_pu: float,
                  s_source_mva: float = math.inf) -> float:
    """Three-phase fault current on the LV side of a transformer of
    s_kva and impedance z_pu, with the upstream network as a source of
    s_source_mva (both as impedances on the transformer base)."""
    z_src = s_kva / 1000 / s_source_mva if math.isfinite(s_source_mva) else 0.0
    return s_kva / (math.sqrt(3) * u_kv * (z_pu + z_src)) / 1000


def start_dip(s_start_kva: float, s_kva: float, z_pu: float) -> float:
    """Voltage dip (fraction) at a transformer's LV bus when a motor
    takes s_start_kva: the motor as a load on the transformer's
    short-circuit capacity s_kva / z_pu."""
    s_sc = s_kva / z_pu
    return s_start_kva / (s_sc + s_start_kva)
# [end: sizing]


# [start: dc]
def battery_ah(periods, temp_factor: float = 1.11, ageing: float = 1.25,
               margin: float = 1.10) -> tuple[float, float]:
    """Simplified duty-cycle sizing: periods = [(amps, minutes), ...];
    returns (raw Ah, sized Ah) - the raw sum of amp-hours times the
    temperature, ageing and design-margin factors (the makers' curves and
    the applicable standard replace this method in a real design)."""
    raw = sum(a * m / 60 for a, m in periods)
    return raw, raw * temp_factor * ageing * margin


def charger_a(load_a: float, ah: float, hours: float, k: float = 1.1) -> float:
    """Charger current: the standing load plus recharging ah in hours,
    with k for the charge inefficiency."""
    return load_a + k * ah / hours


def ups(kw: float, pf: float, minutes: float, eff: float = 0.92,
        margin: float = 0.25) -> tuple[float, float]:
    """(UPS kVA rating, battery kWh) for kw of load for minutes."""
    kva = kw / pf * (1 + margin)
    kwh = kw * minutes / 60 / eff
    return kva, kwh
# [end: dc]


def hvac_kw(losses_kw: float, ua_kw_per_k: float, t_out: float,
            t_in: float, solar_kw: float = 0.0, cop: float = 3.0):
    """(cooling kW, electric kW) to hold t_in: equipment losses, heat
    through the walls and solar gain, removed with a coefficient of
    performance cop."""
    q = losses_kw + ua_kw_per_k * (t_out - t_in) + solar_kw
    q = max(q, 0.0)
    return q, q / cop


# [start: shed]
def shed(loads, state: str, available_kva: float, diversity: float = 1.0):
    """Keep loads in order of priority (1 first) while the demand fits
    the available supply; returns (kept tags, shed tags, kVA kept)."""
    kept, cut = [], []
    for ld in sorted(loads, key=lambda x: (x.priority, x.tag)):
        if ld.kw_in(state) == 0:
            continue
        trial = kept + [ld]
        if demand(trial, state, diversity)[2] <= available_kva:
            kept = trial
        else:
            cut.append(ld)
    kva = demand(kept, state, diversity)[2]
    return [x.tag for x in kept], [x.tag for x in cut], kva
# [end: shed]


def timeline(events):
    """events = [(t_min, label, kw_on_ups)]: energy the UPS must give
    between events, in kWh; returns (rows, total kWh)."""
    rows, tot = [], 0.0
    for (t0, lab, kw), (t1, *_r) in zip(events[:-1], events[1:]):
        e = kw * (t1 - t0) / 60
        tot += e
        rows.append((t0, t1, lab, kw, e))
    return rows, tot
