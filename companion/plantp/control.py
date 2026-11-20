"""Plant control and energy management (chapter 20): a first-order plant
under a PI loop with a rate limiter, frequency-power and voltage-reactive
droop, the P-Q capability of an inverter, headroom and footroom, the
SOC headroom a battery can keep for a service, a dynamic-programming
schedule with time-varying charge and export caps, an hourly plant
controller with priorities, fallback and alarms, and imbalance
settlement.

Powers in MW, energies in MWh, time steps in hours unless stated. All
limits are teaching values (A-299 onwards), never grid-code values.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np


# ------------------------------------------------------------ loops
# [start: pi]
def pi_response(kp: float, ki: float, tau: float, dt: float, n: int,
                setpoint: float = 1.0, rate: float | None = None,
                u_max: float = 1e9, anti_windup: bool = False):
    """First-order plant dy/dt = (u - y)/tau under a PI controller on
    the error; the command u is clipped to +-u_max and, if rate is
    given, may change at most rate per second. With anti_windup the
    integral stops growing while the command is held by a limit."""
    y = u = integ = 0.0
    ys, us = [], []
    for _ in range(n):
        e = setpoint - y
        integ += e * dt
        want = kp * e + ki * integ
        u_new = max(-u_max, min(u_max, want))
        if rate is not None:
            u_new = u + max(-rate * dt, min(rate * dt, u_new - u))
        if anti_windup and abs(u_new - want) > 1e-12:
            integ -= e * dt          # held by a limit: do not wind up
        u = u_new
        y += dt * (u - y) / tau
        ys.append(y)
        us.append(u)
    return np.array(ys), np.array(us)
# [end: pi]


def rate_limit(x, max_step: float):
    """Series with each step limited to +-max_step."""
    x = np.asarray(x, float)
    out = np.empty_like(x)
    out[0] = x[0]
    for k in range(1, len(x)):
        out[k] = out[k - 1] + np.clip(x[k] - out[k - 1], -max_step, max_step)
    return out


# ------------------------------------------------------------ droop
# [start: droop]
def droop_power(df_hz, p_rated: float, droop: float = 0.05,
                deadband_hz: float = 0.0, f_nom: float = 50.0):
    """Change of active power for a frequency deviation (MW): -df/f_nom
    / droop * p_rated outside a deadband (teaching settings)."""
    df = np.asarray(df_hz, float)
    eff = np.sign(df) * np.clip(np.abs(df) - deadband_hz, 0, None)
    return -eff / f_nom / droop * p_rated


def droop_reactive(dv_pu, q_max: float, slope: float = 0.04):
    """Reactive power for a voltage deviation (per unit): -dv/slope *
    q_max, clipped to +-q_max (generator convention, + = export)."""
    q = -np.asarray(dv_pu, float) / slope * q_max
    return np.clip(q, -q_max, q_max)
# [end: droop]


# ------------------------------------------------------------ capability
# [start: pq]
def q_limit(p_mw, s_rated: float, q_frac: float):
    """Largest reactive power at active power p: the smaller of a fixed
    share of the rating and what the apparent-power circle leaves."""
    p = np.asarray(p_mw, float)
    circle = np.sqrt(np.clip(s_rated ** 2 - p ** 2, 0, None))
    return np.minimum(q_frac * s_rated, circle)


def headroom(p_avail, p_set):
    """Upward room: available minus set point (never negative)."""
    room = np.asarray(p_avail, float) - np.asarray(p_set, float)
    return np.clip(room, 0, None)


def soc_room(e_mwh: float, e_min: float, e_max: float, eta: float,
             hours: float) -> tuple[float, float]:
    """Power (MW) the battery can hold up and down for a given number of
    hours from its stored energy: up uses e - e_min, down fills to e_max."""
    up = (e_mwh - e_min) * eta / hours
    down = (e_max - e_mwh) / eta / hours
    return max(up, 0.0), max(down, 0.0)
# [end: pq]


# ------------------------------------------------------------ schedule
# [start: dp]
def dp_schedule(price, charge_cap, export_room, p_max: float, e_min: float,
                e_max: float, e0: float, eta: float, step: float = 1.0,
                wear: float = 0.0, floor=None, e_end: float | None = None):
    """Best hourly battery plan: charge c_t <= min(p_max, charge_cap_t)
    (energy the plant can give), discharge d_t <= min(p_max,
    export_room_t); start and end at e0; revenue = sum price (d - c)
    - wear d; optional floor_t: least energy at the start and end of
    hour t (a held reserve); e_end: energy at the end (default e0).
    Returns (revenue, energy path, power: + discharge)."""
    price = np.asarray(price, float)
    grid = np.arange(e_min, e_max + step / 2, step)
    n_s, n_t = grid.size, price.size
    i0 = int(np.argmin(np.abs(grid - e0)))
    delta = grid[None, :] - grid[:, None]                 # [from, to]
    power = np.where(delta > 0, -delta / eta, -delta * eta)
    i_end = i0 if e_end is None else int(np.argmin(np.abs(grid - e_end)))
    value = np.full(n_s, -np.inf)
    value[i_end] = 0.0
    choice = np.zeros((n_t, n_s), dtype=int)
    for t in range(n_t - 1, -1, -1):
        ok = ((power <= min(p_max, export_room[t]) + 1e-9)
              & (-power <= min(p_max, charge_cap[t]) + 1e-9))
        if floor is not None:
            low = floor[t] - 1e-9
            ok &= (grid[:, None] >= low) & (grid[None, :] >= low)
        gain = price[t] * power - wear * np.maximum(power, 0) + value[None, :]
        gain[~ok] = -np.inf
        choice[t] = np.argmax(gain, axis=1)
        value = gain[np.arange(n_s), choice[t]]
    path = [i0]
    for t in range(n_t):
        path.append(int(choice[t, path[-1]]))
    p = power[path[:-1], path[1:]]
    return float(value[i0]), grid[path], p
# [end: dp]


# ------------------------------------------------------------ controller
# [start: controller]
@dataclass
class Controller:
    """Hourly plant controller with a fixed priority order:
    1 safety and SOC limits, 2 operator instruction (export cap),
    3 contracted service headroom, 4 schedule, 5 recapture of
    curtailment. On comms loss it holds the last valid export cap and
    sets the battery to its fallback after a timeout (hours)."""
    export_cap: float = 100.0
    p_max: float = 20.0
    e_min: float = 4.0
    e_max: float = 36.0
    eta: float = math.sqrt(0.86)
    reserve_up: float = 0.0          # MW held for a service (upward)
    reserve_h: float = 1.0           # for this many hours
    timeout_h: int = 1
    e: float = 4.0
    lost_h: int = 0
    alarms: list = field(default_factory=list)

    def step(self, hour: int, plant_mw: float, request_mw: float,
             cap_mw: float | None, comm_ok: bool) -> dict:
        """plant_mw: renewable output at the POC; request_mw: battery
        request from the schedule (+ discharge); cap_mw: operator's
        export cap (None = unchanged)."""
        if comm_ok:
            self.lost_h = 0
            if cap_mw is not None:
                self.export_cap = cap_mw
        else:
            self.lost_h += 1
            if self.lost_h > self.timeout_h:
                request_mw = 0.0                   # fallback: battery idle
                self.alarms.append((hour, "comms lost: battery to fallback"))
        req = request_mw
        if abs(req) > self.p_max:
            self.alarms.append((hour, f"request {req:+.1f} MW beyond rating"))
            req = math.copysign(self.p_max, req)
        # upward reserve: keep energy for reserve_up over reserve_h
        e_floor = self.e_min + self.reserve_up * self.reserve_h / self.eta
        if req > 0:
            d = min(req, self.p_max - self.reserve_up,
                    max((self.e - e_floor) * self.eta, 0.0),
                    max(self.export_cap - plant_mw, 0.0))
            if d < req - 1e-9:
                self.alarms.append((hour, "discharge limited"))
            c = 0.0
        else:
            d = 0.0
            c = min(-req, (self.e_max - self.e) / self.eta, max(plant_mw, 0.0))
            if c < -req - 1e-9:
                self.alarms.append((hour, "charge limited"))
        # recapture curtailment with any room left
        spill = max(plant_mw + d - c - self.export_cap, 0.0)
        room = (self.e_max - self.e) / self.eta - c
        extra = min(spill, self.p_max - c - d, room)
        extra = max(extra, 0.0) if d == 0.0 else 0.0
        c += extra
        self.e += c * self.eta - d / self.eta
        export = min(plant_mw - c + d, self.export_cap)
        curtailed = max(plant_mw - c + d - self.export_cap, 0.0)
        return {"export": export, "charge": c, "discharge": d,
                "curtailed": curtailed, "soc": self.e, "cap": self.export_cap}
# [end: controller]


def imbalance(scheduled, actual, short_price: float,
              long_price: float) -> float:
    """Penalty (money) for deviations from the schedule: each MWh short
    costs short_price, each MWh long costs long_price (teaching
    two-price settlement, on top of the energy price)."""
    dev = np.asarray(actual, float) - np.asarray(scheduled, float)
    short = np.clip(-dev, 0, None) * short_price
    long = np.clip(dev, 0, None) * long_price
    return float((short + long).sum())
