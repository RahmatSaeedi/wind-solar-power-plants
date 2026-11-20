"""PV curves for converter studies and maximum-power-point tracking
(chapter 9).

The I-V curve is the explicit four-point model that passes exactly through
(0, I_sc), (V_mp, I_mp) and (V_oc, 0) of the data sheet:

    I(V) = I_sc (1 - C1 (exp(V / (C2 V_oc)) - 1))
    C2 = (V_mp / V_oc - 1) / ln(1 - I_mp / I_sc)
    C1 = (1 - I_mp / I_sc) exp(-V_mp / (C2 V_oc))

It is a teaching model for converter control, not a physical cell model;
chapter 10 builds the physical one.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

K_B = 1.380649e-23
Q_E = 1.602176634e-19


@dataclass(frozen=True)
class Curve:
    """Four data-sheet points of a module or string at given conditions."""
    isc: float
    voc: float
    imp: float
    vmp: float

    @property
    def c2(self) -> float:
        return (self.vmp / self.voc - 1) / math.log(1 - self.imp / self.isc)

    @property
    def c1(self) -> float:
        return ((1 - self.imp / self.isc)
                * math.exp(-self.vmp / (self.c2 * self.voc)))

    def i(self, v):
        """Current at voltage(s) v, clipped at zero above V_oc."""
        v = np.asarray(v, dtype=float)
        out = self.isc * (1 - self.c1 * np.expm1(v / (self.c2 * self.voc)))
        return np.clip(out, 0.0, None)

    def v(self, i):
        """Voltage at current(s) i (inverse of the model), 0 <= i <= I_sc."""
        i = np.clip(np.asarray(i, dtype=float), 0.0, self.isc)
        return self.c2 * self.voc * np.log1p((1 - i / self.isc) / self.c1)

    def p(self, v):
        return np.asarray(v, dtype=float) * self.i(v)

    def mpp(self, n: int = 4001) -> tuple[float, float]:
        """(V, P) of the maximum-power point by a fine scan."""
        v = np.linspace(0, self.voc, n)
        p = self.p(v)
        k = int(np.argmax(p))
        return float(v[k]), float(p[k])


@dataclass(frozen=True)
class Module:
    """STC data sheet values and coefficients (per cent per kelvin)."""
    isc: float
    voc: float
    imp: float
    vmp: float
    cells_series: int
    alpha_isc: float          # %/K
    beta_voc: float           # %/K (negative)
    gamma_pmax: float         # %/K (negative)
    ideality: float = 1.2

    def at(self, g_wm2: float, tc_c: float, n_series: int = 1) -> Curve:
        """Four-point curve of n modules in series at irradiance and cell
        temperature: currents scale with G (and slightly with T); voltages
        fall with T and rise with ln(G) (the diode law). V_mp falls with the
        coefficient gamma - alpha, so that P_mp follows gamma at 1000 W/m2."""
        if g_wm2 <= 0:
            raise ValueError("irradiance must be positive")
        dt = tc_c - 25.0
        v_t = K_B * (tc_c + 273.15) / Q_E
        k_i = g_wm2 / 1000 * (1 + self.alpha_isc / 100 * dt)
        dv_g = self.cells_series * self.ideality * v_t * math.log(g_wm2 / 1000)
        voc = self.voc * (1 + self.beta_voc / 100 * dt) + dv_g
        beta_vmp = self.gamma_pmax - self.alpha_isc
        vmp = self.vmp * (1 + beta_vmp / 100 * dt) + dv_g * self.vmp / self.voc
        return Curve(self.isc * k_i, n_series * voc, self.imp * k_i,
                     n_series * vmp)


# the chapter 6 module (PVM-550, half-cut cells: 72 cells in series)
PVM_550 = Module(isc=13.98, voc=49.90, imp=13.11, vmp=41.96, cells_series=72,
                 alpha_isc=0.048, beta_voc=-0.27, gamma_pmax=-0.35)


def cell_temperature(t_air_c, g_wm2, noct_c: float = 45.0):
    """Cell temperature by the NOCT rule (chapter 6)."""
    return np.asarray(t_air_c) + (noct_c - 20.0) / 800.0 * np.asarray(g_wm2)


def string_with_bypass(curves, i, v_bypass: float = 0.5):
    """Voltage of a series string of sub-strings, each with a bypass diode,
    at string current(s) i: a sub-string whose I_sc is below i is bypassed
    (it contributes -v_bypass)."""
    i = np.asarray(i, dtype=float)
    total = np.zeros_like(i)
    for c in curves:
        total += np.where(i <= c.isc, c.v(i), -v_bypass)
    return total


def pv_curve_partial(curves, n: int = 3000):
    """(V, I, P) arrays of a partially shaded string, swept in current."""
    i_top = max(c.isc for c in curves)
    i = np.linspace(0, i_top, n)
    v = string_with_bypass(curves, i)
    keep = v >= 0
    return v[keep], i[keep], v[keep] * i[keep]


# ------------------------------------------------------------ trackers
@dataclass
class PerturbObserve:
    """Perturb and observe: step the voltage reference; keep the direction
    while power rises, reverse it when power falls."""
    v_ref: float
    step: float
    p_last: float = 0.0
    direction: float = 1.0

    def update(self, v_meas: float, i_meas: float) -> float:
        p = v_meas * i_meas
        if p < self.p_last:
            self.direction = -self.direction
        self.p_last = p
        self.v_ref += self.direction * self.step
        return self.v_ref


@dataclass
class IncrementalConductance:
    """Incremental conductance: at the MPP dI/dV = -I/V; move the voltage
    reference towards that condition."""
    v_ref: float
    step: float
    v_last: float = 0.0
    i_last: float = 0.0
    tol: float = 1e-3

    def update(self, v_meas: float, i_meas: float) -> float:
        dv, di = v_meas - self.v_last, i_meas - self.i_last
        if abs(dv) < 1e-9:
            if abs(di) > self.tol:
                self.v_ref += self.step if di > 0 else -self.step
        else:
            g = di / dv + i_meas / v_meas          # zero at the MPP
            if g > self.tol / max(v_meas, 1.0):
                self.v_ref += self.step
            elif g < -self.tol / max(v_meas, 1.0):
                self.v_ref -= self.step
        self.v_last, self.i_last = v_meas, i_meas
        return self.v_ref


def global_scan(curve_fn, v_lo: float, v_hi: float, n: int = 60) -> float:
    """Voltage of the highest power found by a coarse sweep (used every few
    minutes against partial shading); curve_fn(v) returns current."""
    v = np.linspace(v_lo, v_hi, n)
    p = v * np.asarray([curve_fn(x) for x in v])
    return float(v[int(np.argmax(p))])
