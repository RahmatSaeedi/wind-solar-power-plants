"""Preliminary power-transformer design and factory-test arithmetic
(chapter 43). Teaching relations for review and estimation - a maker's
design uses its own validated methods, materials data and test history.

Builds on plantp.transformer (ch 25): volts per turn, equivalent circuit,
loss capitalisation, hot spot and ageing.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

MU0 = 4e-7 * math.pi
RHO_CU_75 = 0.0211e-6        # ohm m, copper at 75 C (teaching)
RHO_FE = 7650.0              # kg/m3, electrical steel


# ------------------------------------------------------------ core
# [start: steps]
def stepped_fill(n_steps: int) -> tuple[float, list[float]]:
    """Largest share of a circle that n symmetric rectangular steps can
    fill (stacked core cross-section). Returns the fill factor and the
    step half-heights y_k (radius 1); widths are sqrt(1 - y_k^2)."""
    from scipy.optimize import minimize

    def neg_area(y):
        y = np.sort(np.clip(y, 0.0, 1.0))
        x = np.sqrt(1 - y ** 2)
        return -4 * np.sum(x * np.diff(np.concatenate([[0.0], y])))

    y0 = np.linspace(1, n_steps, n_steps) / (n_steps + 1)
    best = minimize(neg_area, y0, method="Nelder-Mead",
                    options=dict(xatol=1e-10, fatol=1e-12, maxiter=40000))
    return -best.fun / math.pi, sorted(float(v) for v in best.x)
# [end: steps]


def core_section(e_t: float, b_peak: float, f: float = 50.0,
                 stacking: float = 0.97, fill: float = 0.93) -> dict[str, float]:
    """Net and gross core area for a volts-per-turn and flux density, and
    the circumscribed core diameter for a stepped section."""
    a_net = e_t / (4.44 * f * b_peak)
    a_gross = a_net / stacking
    d = math.sqrt(4 * a_gross / (math.pi * fill))
    return dict(a_net=a_net, a_gross=a_gross, d=d)


def core_mass_kg(a_net: float, h_window: float, centres: float,
                 d_core: float, limbs: int = 3) -> float:
    """Three-limb core: limbs of window height plus two yokes spanning the
    outer limbs (teaching geometry; corners counted once)."""
    yoke = (limbs - 1) * centres + d_core
    return RHO_FE * a_net * (limbs * h_window + 2 * yoke)


def no_load_loss_kw(mass_kg: float, w_per_kg: float, building: float) -> float:
    return mass_kg * w_per_kg * building / 1000


# ------------------------------------------------------------ windings
def tap_table(n_principal: int, step_pct: float, n_each_side: int,
              turns_per_step: int) -> list[tuple[float, int, float]]:
    """Tap position (% of principal), turns, and ratio error against the
    nominal tap voltage when each step is a whole number of turns."""
    out = []
    for k in range(-n_each_side, n_each_side + 1):
        pct = k * step_pct
        n = n_principal + k * turns_per_step
        want = n_principal * (1 + pct / 100)
        out.append((pct, n, 100 * (n / want - 1)))
    return out


def resistance_ohm(turns: int, d_mean: float, area_mm2: float,
                   rho: float = RHO_CU_75) -> float:
    return rho * turns * math.pi * d_mean / (area_mm2 * 1e-6)


# [start: ux]
def ux_pct(f: float, ni: float, e_t: float, d_m: float, a12: float,
           a1: float, a2: float, h: float) -> float:
    """Reactance of two concentric windings from their geometry, with the
    Rogowski factor for the leakage flux spreading at the winding ends."""
    k_r = 1 - (a1 + a2 + a12) / (math.pi * h)
    h_eff = h / k_r
    return (100 * 2 * math.pi * f * MU0 * ni * math.pi * d_m
            * (a12 + (a1 + a2) / 3) / (e_t * h_eff))
# [end: ux]


def eddy_ratio(f: float, b_peak_gap: float, t_m: float, j_a_m2: float,
               rho: float = RHO_CU_75) -> float:
    """Eddy loss over DC loss of strips of thickness t in the axial leakage
    field of a winding (the field falls from b_peak_gap to zero across the
    winding, so the mean of its peak square is a third). The strip
    formula w^2 B^2 t^2 / 24 rho uses the peak field."""
    b2 = b_peak_gap ** 2 / 3
    w = 2 * math.pi * f
    return w ** 2 * b2 * t_m ** 2 / (24 * rho ** 2 * j_a_m2 ** 2)


# ------------------------------------------------------------ forces
def hoop_stress_mpa(ni_peak: float, h: float, d_m: float, turns: int,
                    a_turn_mm2: float) -> float:
    """Mean hoop stress of a winding at the peak short-circuit current:
    radial force N i x B/2 x pi D, shared by the turns' cross-section."""
    b = MU0 * ni_peak / h
    f_r = ni_peak * b / 2 * math.pi * d_m
    return f_r / (2 * math.pi * turns * a_turn_mm2 * 1e-6) / 1e6


def buckling_free_mpa(e_pa: float, t: float, d: float) -> float:
    """Free-buckling stress of a thin ring under external pressure:
    sigma = E (t / D)^2."""
    return e_pa * (t / d) ** 2 / 1e6


def buckling_supported_mpa(e_pa: float, t: float, span: float) -> float:
    """A conductor held by sticks every `span` buckles between them like
    a fixed-fixed strut: sigma = pi^2 E t^2 / (3 span^2)."""
    return math.pi ** 2 * e_pa * t ** 2 / (3 * span ** 2) / 1e6


# ------------------------------------------------------------ insulation
def field_in_gap(u_kv: float, d_oil_mm: float, d_pb_mm: float,
                 eps_oil: float = 2.2, eps_pb: float = 4.4) -> tuple[float, float]:
    """Field (kV/mm) in the oil and in the pressboard of a series gap."""
    e_oil = u_kv / (d_oil_mm + d_pb_mm * eps_oil / eps_pb)
    return e_oil, e_oil * eps_oil / eps_pb


def water_solubility_ppm(t_c: float) -> float:
    """Saturation water content of a mineral oil (teaching empirical form
    log10 S = 7.42 - 1670 / T)."""
    return 10 ** (7.42 - 1670 / (t_c + 273.15))


# ------------------------------------------------------------ tests
def r_to_ref(r: float, t_meas: float, t_ref: float = 75.0, k: float = 235.0) -> float:
    """Copper resistance referred to another temperature."""
    return r * (k + t_ref) / (k + t_meas)


def waveform_corrected(p_meas: float, u_rms: float, u_mean: float) -> float:
    """No-load loss measured with a distorted voltage, corrected with the
    reading of a mean-value voltmeter scaled to rms (teaching form)."""
    d = (u_mean - u_rms) / u_mean
    return p_meas * (1 + d)


def cooling_curve(t_min, r_ohm) -> dict[str, float]:
    """Fit R(t) = a + b exp(-t / tau) to winding resistances read after
    the heat run stops, and extrapolate to the moment of shut-down."""
    from scipy.optimize import curve_fit
    t = np.asarray(t_min, float)
    r = np.asarray(r_ohm, float)

    def model(x, a, b, tau):
        return a + b * np.exp(-x / tau)

    p, _ = curve_fit(model, t, r, p0=(r[-1], r[0] - r[-1], 10.0), maxfev=20000)
    return dict(a=p[0], b=p[1], tau=p[2], r0=p[0] + p[1])


def sound_power_db(l_pa: float, s_m2: float) -> float:
    return l_pa + 10 * math.log10(s_m2)


# ------------------------------------------------------------ calculator
# [start: calc]
@dataclass
class LossTempCalc:
    """Hourly losses, hot spot and ageing of a transformer over a year;
    `sensitivity` changes one input at a time."""
    p0_kw: float
    pk_kw: float
    load_pu: np.ndarray
    ambient_c: np.ndarray
    d_top_r: float = 52.0
    d_hs_r: float = 26.0
    r_ratio: float = 6.0
    changes: dict = field(default_factory=dict)

    def run(self) -> dict[str, float]:
        from plantp import transformer as tr
        k = self.load_pu * self.changes.get("load", 1.0)
        amb = self.ambient_c + self.changes.get("ambient", 0.0)
        pk = self.pk_kw * self.changes.get("pk", 1.0)
        loss = self.p0_kw + pk * k ** 2
        hs = np.array([tr.hot_spot(x, a, self.d_top_r, self.d_hs_r,
                                   self.r_ratio) for x, a in zip(k, amb)])
        age = np.array([tr.ageing_rate(h) for h in hs])
        return dict(loss_mwh=float(loss.sum() / 1000), hs_max=float(hs.max()),
                    life_days=float(age.sum() / 24))

    def sensitivity(self, cases: dict) -> dict[str, dict[str, float]]:
        out = {"base": self.run()}
        for name, ch in cases.items():
            out[name] = LossTempCalc(self.p0_kw, self.pk_kw, self.load_pu,
                                     self.ambient_c, self.d_top_r, self.d_hs_r,
                                     self.r_ratio, ch).run()
        return out
# [end: calc]
