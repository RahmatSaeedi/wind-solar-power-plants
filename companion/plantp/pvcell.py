"""PV cell and module physics (chapter 10): the single-diode model fitted to
a data sheet, its translation to other irradiance and temperature, reverse
bias with avalanche breakdown (hot spots), module temperature with wind,
and plane-of-array irradiance.

The single-diode model:

    I = I_L - I_0 (exp((V + I R_s) / a) - 1) - (V + I R_s) / R_sh,
    a = n N_s k T / q

solved explicitly with the Lambert W function. The fit follows the usual
five-parameter route: four equations at STC (short circuit, open circuit,
maximum-power point and dP/dV = 0 there) give I_L, I_0, R_s and R_sh for a
trial ideality n, and n is then chosen so that the model reproduces the
data-sheet temperature coefficient of V_oc. Teaching implementation; real
studies use validated tools and measured module data.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy.optimize import brentq, fsolve
from scipy.special import lambertw

K_B = 1.380649e-23
Q_E = 1.602176634e-19
EG_REF = 1.121          # eV, silicon at 25 C
T_REF = 298.15          # K


def w_exp(log_x):
    """Lambert W of exp(log_x), stable for very large arguments: scipy for
    moderate values, Newton iteration on w + ln w = log_x above that."""
    lx = np.asarray(log_x, dtype=float)
    small = lx < 500.0
    out = np.empty_like(lx)
    out[small] = np.real(lambertw(np.exp(lx[small])))
    big = lx[~small]
    if big.size:
        w = big - np.log(big)
        for _ in range(8):
            w = w - (w + np.log(w) - big) / (1 + 1 / w)
        out[~small] = w
    return out if out.ndim else float(out)


@dataclass(frozen=True)
class SDM:
    """Single-diode parameters of one module at one condition."""
    i_l: float
    i_0: float
    a: float            # modified ideality factor n N_s k T / q, volts
    r_s: float
    r_sh: float

    # [start: sdm]
    def i(self, v):
        """Current at voltage(s) v (Lambert W, explicit)."""
        v = np.asarray(v, dtype=float)
        rs, rsh, a = self.r_s, self.r_sh, self.a
        il0 = self.i_l + self.i_0
        log_theta = (math.log(rs * self.i_0 * rsh / (a * (rs + rsh)))
                     + rsh * (rs * il0 + v) / (a * (rs + rsh)))
        w = w_exp(log_theta)
        return (rsh * il0 - v) / (rs + rsh) - a * w / rs

    def v(self, i):
        """Voltage at current(s) i (Lambert W, explicit)."""
        i = np.asarray(i, dtype=float)
        rsh, a = self.r_sh, self.a
        log_psi = (math.log(self.i_0 * rsh / a)
                   + rsh * (self.i_l + self.i_0 - i) / a)
        w = w_exp(log_psi)
        return (self.i_l + self.i_0 - i) * rsh - i * self.r_s - a * w
    # [end: sdm]

    @property
    def isc(self) -> float:
        return float(self.i(0.0))

    @property
    def voc(self) -> float:
        return float(self.v(0.0))

    def mpp(self) -> tuple[float, float, float]:
        """(V_mp, I_mp, P_mp) by golden-section search on P(V)."""
        lo, hi = 0.0, self.voc
        g = (math.sqrt(5) - 1) / 2
        x1, x2 = hi - g * (hi - lo), lo + g * (hi - lo)
        f1, f2 = x1 * float(self.i(x1)), x2 * float(self.i(x2))
        for _ in range(80):
            if f1 > f2:
                hi, x2, f2 = x2, x1, f1
                x1 = hi - g * (hi - lo)
                f1 = x1 * float(self.i(x1))
            else:
                lo, x1, f1 = x1, x2, f2
                x2 = lo + g * (hi - lo)
                f2 = x2 * float(self.i(x2))
        v = 0.5 * (lo + hi)
        i = float(self.i(v))
        return v, i, v * i


@dataclass(frozen=True)
class Datasheet:
    voc: float
    isc: float
    vmp: float
    imp: float
    n_s: int                  # cells in series
    alpha_isc: float          # A/K
    beta_voc: float           # V/K


PVM_550_DS = Datasheet(voc=49.90, isc=13.98, vmp=41.96, imp=13.11, n_s=72,
                       alpha_isc=13.98 * 0.00048, beta_voc=49.90 * -0.0027)


def _fit_at_n(ds: Datasheet, n: float) -> SDM:
    a = n * ds.n_s * K_B * T_REF / Q_E

    def eqs(x):
        rs, log_rsh = x
        rsh = math.exp(log_rsh)
        i_l = ds.isc * (1 + rs / rsh)
        i_0 = (i_l - ds.voc / rsh) / math.expm1(ds.voc / a)
        e = math.exp((ds.vmp + ds.imp * rs) / a)
        f_mp = i_l - i_0 * (e - 1) - (ds.vmp + ds.imp * rs) / rsh - ds.imp
        # dI/dV at the MPP from implicit differentiation; dP/dV = I + V dI/dV
        g = i_0 / a * e + 1 / rsh
        didv = -g / (1 + rs * g)
        f_dp = ds.imp + ds.vmp * didv
        return [f_mp, f_dp]

    rs, log_rsh = fsolve(eqs, [0.2, math.log(300.0)], xtol=1e-12)
    rsh = math.exp(log_rsh)
    i_l = ds.isc * (1 + rs / rsh)
    i_0 = (i_l - ds.voc / rsh) / math.expm1(ds.voc / a)
    return SDM(i_l, i_0, a, rs, rsh)


def at_conditions(ref: SDM, g_wm2: float, t_cell_c: float,
                  alpha_isc: float) -> SDM:
    """De Soto-style translation of the STC parameters to irradiance G and
    cell temperature T: I_L with G and alpha, I_0 with T^3 exp(-Eg/kT),
    a with T, R_sh with 1/G, R_s constant."""
    t = t_cell_c + 273.15
    eg = EG_REF * (1 - 0.0002677 * (t - T_REF))
    i_l = g_wm2 / 1000 * (ref.i_l + alpha_isc * (t - T_REF))
    i_0 = (ref.i_0 * (t / T_REF) ** 3
           * math.exp(EG_REF * Q_E / (K_B * T_REF) - eg * Q_E / (K_B * t)))
    return SDM(i_l, i_0, ref.a * t / T_REF, ref.r_s,
               ref.r_sh * 1000 / max(g_wm2, 1.0))


def fit(ds: Datasheet) -> SDM:
    """Five-parameter fit: n chosen so that dV_oc/dT matches the data sheet."""
    def beta_err(n):
        ref = _fit_at_n(ds, n)
        v1 = at_conditions(ref, 1000, 20, ds.alpha_isc).voc
        v2 = at_conditions(ref, 1000, 30, ds.alpha_isc).voc
        return (v2 - v1) / 10 - ds.beta_voc

    n = brentq(beta_err, 0.85, 1.25, xtol=1e-6)
    return _fit_at_n(ds, n)


# --------------------------------------------------------------- reverse bias
def cell_reverse_current(v_cell, i_l: float, r_sh: float, v_br: float = -15.0,
                         a_br: float = 0.1, m_br: float = 3.7):
    """Current of one cell in reverse bias (Bishop's avalanche term): the
    photocurrent plus a shunt current that grows sharply near breakdown."""
    v = np.asarray(v_cell, dtype=float)
    shunt = v / r_sh * (1 + a_br * (1 - v / v_br) ** (-m_br))
    return i_l - shunt


# --------------------------------------------------------- module temperature
def faiman(t_air_c, g_poa, wind_ms, u0: float = 25.0, u1: float = 6.84):
    """Module temperature, Faiman model: T = T_air + G / (U0 + U1 v)."""
    wind = np.asarray(wind_ms)
    return np.asarray(t_air_c) + np.asarray(g_poa) / (u0 + u1 * wind)


def wind_at_height(ws_ref, h_ref: float, h: float, alpha: float = 0.2):
    """Power-law shear (chapter 4)."""
    return np.asarray(ws_ref) * (h / h_ref) ** alpha


# --------------------------------------------------------- plane of array
def iam_ashrae(cos_inc, b0: float = 0.05):
    """Incidence-angle modifier 1 - b0 (1/cos theta - 1), zero beyond 90
    deg."""
    c = np.asarray(cos_inc, dtype=float)
    with np.errstate(divide="ignore"):
        out = 1 - b0 * (1 / np.where(c > 0, c, np.inf) - 1)
    return np.clip(np.where(c > 0, out, 0.0), 0.0, 1.0)


def poa_hay_davies(ghi, dni, dhi, cos_inc, cos_zen, g0n, tilt_deg: float,
                   albedo: float = 0.2):
    """Plane-of-array irradiance (beam, sky diffuse, ground) with the
    Hay-Davies sky model: a circumsolar share A = DNI / G0n follows the
    beam geometry, the rest is isotropic."""
    b = math.radians(tilt_deg)
    ghi, dni, dhi = (np.asarray(x, dtype=float) for x in (ghi, dni, dhi))
    ci = np.clip(np.asarray(cos_inc, dtype=float), 0, None)
    cz = np.asarray(cos_zen, dtype=float)
    a_i = np.divide(dni, g0n, out=np.zeros_like(dni),
                    where=np.asarray(g0n) > 0)
    rb = np.divide(ci, cz, out=np.zeros_like(ci), where=cz > 0.087)
    beam = dni * ci
    sky = dhi * (a_i * rb + (1 - a_i) * (1 + math.cos(b)) / 2)
    ground = ghi * albedo * (1 - math.cos(b)) / 2
    return beam, sky, ground
