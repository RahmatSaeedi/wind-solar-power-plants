"""The Plant P turbine rotor used by all chapter 11 scripts: the fictional
blade of plantp.wind designed for tip-speed ratio 8, the control limits of
WT-5.0-150 (A-211) and cached steady power curves.

Teaching values A-211: rotor 150 m, hub 100 m, rated 5 MW, drivetrain
efficiency 0.94, rotor speed 5 .. 11.5 rpm, cut-in 3 m/s, cut-out 25 m/s.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

from companion.ch11 import common  # noqa: F401  (puts plantp on the path)
from plantp import wind as w

HUB = 100.0
RADIUS = 75.0
AREA = np.pi * RADIUS ** 2
RHO0 = 1.225
RHO_SITE = 1.056                 # D-008 mean site density (chapter 5)


@lru_cache(maxsize=1)
def blade() -> w.Blade:
    return w.design_blade(radius=RADIUS)


@lru_cache(maxsize=1)
def tsr_opt() -> float:
    lam = np.arange(7.0, 10.01, 0.25)
    cps = [w.bem(blade(), float(x)).cp for x in lam]
    return float(lam[int(np.argmax(cps))])


@lru_cache(maxsize=1)
def turbine() -> w.Turbine:
    return w.Turbine(blade(), tsr_opt=tsr_opt())


@lru_cache(maxsize=4)
def curve(rho: float = RHO0):
    """Steady operating points every 0.5 m/s from 3 to 25 m/s."""
    vs = np.arange(3.0, 25.01, 0.5)
    return [w.operate(turbine(), float(v), rho) for v in vs]


def curve_arrays(rho: float = RHO0, ti: float = 0.10):
    """(v, steady power kW, smoothed power kW, ct) on 0..30 m/s."""
    ops = curve(rho)
    v = np.arange(0.0, 30.01, 0.5)
    p = np.zeros_like(v)
    ct = np.zeros_like(v)
    for o in ops:
        k = int(round(o.v / 0.5))
        p[k], ct[k] = o.power_w / 1e3, o.ct
    sm = w.smooth_power_curve(v, p, ti)
    sm[v > 25.0] = 0.0
    sm[v < 2.5] = 0.0
    return v, p, sm, ct
