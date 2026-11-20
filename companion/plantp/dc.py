"""Direct-current circuit calculations (chapter 6).

Educational code: every function states its model and its limits. Resistivity
and temperature-coefficient values are textbook reference values for pure
metals at 20 C; cable standards quote slightly different, conductor-specific
figures, which chapter 24 uses.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

# ---- material reference values (pure metal, 20 C) ---------------------------
RESISTIVITY_20C = {"copper": 1.72e-8, "aluminium": 2.82e-8}     # ohm * m
TEMP_COEFF = {"copper": 0.00393, "aluminium": 0.00403}            # 1/K
BOLTZMANN = 1.380649e-23      # J/K
ELEMENTARY_CHARGE = 1.602176634e-19   # C


# ---- Ohm's law and power -------------------------------------------------------
def ohm_voltage(current_a: float, resistance_ohm: float) -> float:
    """V = R I"""
    return resistance_ohm * current_a


def ohm_current(voltage_v: float, resistance_ohm: float) -> float:
    """I = V / R"""
    if resistance_ohm <= 0:
        raise ValueError("resistance must be positive")
    return voltage_v / resistance_ohm


def ohm_resistance(voltage_v: float, current_a: float) -> float:
    """R = V / I"""
    if current_a == 0:
        raise ValueError("current must be non-zero")
    return voltage_v / current_a


def power_vi(voltage_v: float, current_a: float) -> float:
    """P = V I"""
    return voltage_v * current_a


def power_i2r(current_a: float, resistance_ohm: float) -> float:
    """P = R I^2 (heat in a resistor)"""
    return resistance_ohm * current_a ** 2


def power_v2r(voltage_v: float, resistance_ohm: float) -> float:
    """P = V^2 / R"""
    if resistance_ohm <= 0:
        raise ValueError("resistance must be positive")
    return voltage_v ** 2 / resistance_ohm


def energy_wh(power_w: float, hours: float) -> float:
    """E = P t, with t in hours, result in watt-hours"""
    if hours < 0:
        raise ValueError("time cannot be negative")
    return power_w * hours


# ---- combining resistors -------------------------------------------------------
def series(*resistances: float) -> float:
    """Resistors in series add."""
    if not resistances:
        raise ValueError("give at least one resistance")
    return float(sum(resistances))


def parallel(*resistances: float) -> float:
    """Conductances of resistors in parallel add: 1/R = sum(1/R_k)."""
    if not resistances:
        raise ValueError("give at least one resistance")
    if any(r <= 0 for r in resistances):
        raise ValueError("resistances must be positive")
    return 1.0 / sum(1.0 / r for r in resistances)


def divider_voltage(v_in: float, r_top: float, r_bottom: float) -> float:
    """Voltage across r_bottom in a two-resistor divider fed by v_in."""
    return v_in * r_bottom / (r_top + r_bottom)


def voltmeter_reading(v_in: float, r_top: float, r_bottom: float, r_meter: float) -> float:
    """What a voltmeter of input resistance r_meter shows across r_bottom.

    The meter sits in parallel with r_bottom and changes the circuit it
    measures (measurement loading).
    """
    return divider_voltage(v_in, r_top, parallel(r_bottom, r_meter))


# ---- conductors -----------------------------------------------------------------
def resistivity_at(material: str, temp_c: float) -> float:
    """rho(T) = rho_20 * (1 + alpha (T - 20)), linear model, valid roughly -50..+200 C."""
    if material not in RESISTIVITY_20C:
        raise ValueError(f"unknown material {material!r}; choose {sorted(RESISTIVITY_20C)}")
    return RESISTIVITY_20C[material] * (1.0 + TEMP_COEFF[material] * (temp_c - 20.0))


def conductor_resistance(length_m: float, area_mm2: float, material: str = "copper",
                         temp_c: float = 20.0) -> float:
    """R = rho L / A for ONE conductor of length L and cross-section A."""
    if length_m < 0 or area_mm2 <= 0:
        raise ValueError("length must be >= 0 and area > 0")
    return resistivity_at(material, temp_c) * length_m / (area_mm2 * 1e-6)


@dataclass
class FeederResult:
    loop_resistance_ohm: float   # both conductors (out and back)
    drop_v: float                # voltage lost along the feeder
    loss_w: float                # heat produced in the feeder
    drop_fraction: float | None  # drop / source voltage, when a source voltage is given


def feeder(current_a: float, length_m: float, area_mm2: float,
           material: str = "copper", temp_c: float = 20.0, conductors: int = 2,
           source_voltage_v: float | None = None) -> FeederResult:
    """Voltage drop and loss of a DC feeder carrying a steady current.

    length_m is the ONE-WAY route length; `conductors` = 2 counts the return
    conductor (both carry the same current). Model: constant current, uniform
    conductor temperature, no inductance (steady DC).
    """
    if current_a < 0 or conductors < 1:
        raise ValueError("current must be >= 0 and conductors >= 1")
    r_loop = conductors * conductor_resistance(length_m, area_mm2, material, temp_c)
    drop = ohm_voltage(current_a, r_loop)
    loss = power_i2r(current_a, r_loop)
    frac = drop / source_voltage_v if source_voltage_v else None
    return FeederResult(r_loop, drop, loss, frac)


def area_for_drop(current_a: float, length_m: float, max_drop_v: float,
                  material: str = "copper", temp_c: float = 20.0, conductors: int = 2) -> float:
    """Smallest cross-section (mm2, not rounded to a standard size) that keeps
    the feeder drop at or below max_drop_v."""
    if max_drop_v <= 0:
        raise ValueError("allowed drop must be positive")
    rho = resistivity_at(material, temp_c)
    return conductors * rho * length_m * current_a / max_drop_v * 1e6


STANDARD_AREAS_MM2 = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300, 400, 500, 630]


def next_standard_area(area_mm2: float) -> float:
    """The smallest standard conductor size that is at least area_mm2."""
    for a in STANDARD_AREAS_MM2:
        if a >= area_mm2:
            return a
    raise ValueError(f"{area_mm2:.0f} mm2 exceeds the largest size in the list; use parallel conductors")


def conductor_temperature(current_a: float, length_m: float, area_mm2: float, material: str,
                          ambient_c: float, thermal_resistance_k_per_w: float,
                          iterations: int = 100) -> float:
    """Steady conductor temperature when I^2 R(T) heat leaves through a fixed
    thermal resistance to the ambient: T = T_a + I^2 R(T) R_th.

    Solved by fixed-point iteration. The linear resistance model and a
    constant thermal resistance are teaching simplifications; real cable
    ratings come from standards and installation conditions (chapter 24).
    """
    t = ambient_c
    for _ in range(iterations):
        r = conductor_resistance(length_m, area_mm2, material, t)
        t_new = ambient_c + power_i2r(current_a, r) * thermal_resistance_k_per_w
        if abs(t_new - t) < 1e-6:
            return t_new
        if t_new > 1000:
            raise ValueError("no steady state: the conductor would run away thermally")
        t = t_new
    return t


def conductor_temperature_closed_form(current_a: float, r20_ohm: float, alpha_per_k: float,
                                      ambient_c: float, thermal_resistance_k_per_w: float) -> float:
    """Exact solution of T = T_a + I^2 R20 (1 + alpha (T - 20)) R_th.

    Rearranged: (T - T_a)(1 - I^2 R20 alpha R_th) = I^2 R20 (1 + alpha (T_a - 20)) R_th.
    A steady temperature exists only while I^2 R20 alpha R_th < 1.
    """
    k = current_a ** 2 * r20_ohm * alpha_per_k * thermal_resistance_k_per_w
    if k >= 1.0:
        raise ValueError("no steady state: I^2 R20 alpha R_th >= 1 (thermal runaway)")
    rise = current_a ** 2 * r20_ohm * (1.0 + alpha_per_k * (ambient_c - 20.0)) * thermal_resistance_k_per_w
    return ambient_c + rise / (1.0 - k)


def runaway_current(r20_ohm: float, alpha_per_k: float, thermal_resistance_k_per_w: float) -> float:
    """Current at which the linear model has no steady temperature: 1 / sqrt(R20 alpha R_th)."""
    return 1.0 / math.sqrt(r20_ohm * alpha_per_k * thermal_resistance_k_per_w)


# ---- short-circuit (adiabatic) heating ------------------------------------------
# volumetric heat capacity of the conductor metal, J/(m3 K): c_p x density
VOLUMETRIC_HEAT_CAPACITY = {"copper": 385.0 * 8960.0, "aluminium": 897.0 * 2700.0}


def adiabatic_k(material: str, t_initial_c: float, t_final_c: float) -> float:
    """Constant k of I^2 t = k^2 A^2, in A s^0.5 / mm2, from first principles.

    During a short fault all heat stays in the metal (no time to escape):
    c_v A dT = I^2 rho(T) / A dt, with rho(T) = rho20 alpha (T + beta),
    beta = 1/alpha - 20. Integrating from T_i to T_f:
    I^2 t = A^2 (c_v / (rho20 alpha)) ln((T_f + beta) / (T_i + beta)).
    """
    rho20, alpha = RESISTIVITY_20C[material], TEMP_COEFF[material]
    beta = 1.0 / alpha - 20.0
    k_si = math.sqrt(VOLUMETRIC_HEAT_CAPACITY[material] / (rho20 * alpha)
                     * math.log((t_final_c + beta) / (t_initial_c + beta)))
    return k_si * 1e-6            # A s^0.5 / m2  ->  A s^0.5 / mm2


def adiabatic_withstand_time(current_a: float, area_mm2: float, k: float) -> float:
    """Seconds a conductor can carry a fault current before reaching the final temperature."""
    if current_a <= 0:
        raise ValueError("fault current must be positive")
    return (k * area_mm2 / current_a) ** 2


# ---- insulation -------------------------------------------------------------------
def cylinder_insulation_resistance(resistivity_ohm_m: float, r_inner_m: float,
                                   r_outer_m: float, length_m: float) -> float:
    """Leakage resistance of a cylindrical insulation layer (current flows radially):
    dR = rho dr / (2 pi r L)  ->  R = rho ln(r_out / r_in) / (2 pi L)."""
    if not 0 < r_inner_m < r_outer_m or length_m <= 0:
        raise ValueError("need 0 < r_inner < r_outer and length > 0")
    return resistivity_ohm_m * math.log(r_outer_m / r_inner_m) / (2 * math.pi * length_m)


# ---- non-ohmic elements and sensors -------------------------------------------------
def diode_current(voltage_v, saturation_a: float = 1e-12, ideality: float = 1.0,
                  temp_c: float = 25.0):
    """Shockley diode law I = I_s (exp(V / (n V_t)) - 1)."""
    v_t = BOLTZMANN * (temp_c + 273.15) / ELEMENTARY_CHARGE
    return saturation_a * np.expm1(np.asarray(voltage_v, dtype=float) / (ideality * v_t))


def pt100_resistance(temp_c: float, r0: float = 100.0, alpha: float = 0.00385) -> float:
    """Linear model of a platinum resistance thermometer (0..150 C)."""
    return r0 * (1.0 + alpha * temp_c)


def bridge_output(v_excitation: float, r1: float, r2: float, r3: float, r_x: float) -> float:
    """Wheatstone bridge: left divider r1 (top) / r2 (bottom), right divider
    r3 (top) / r_x (bottom); output = V(right middle) - V(left middle).
    Balanced (zero output) when r_x / r3 = r2 / r1."""
    return v_excitation * (r_x / (r3 + r_x) - r2 / (r1 + r2))


# ---- capacitors and inductors -------------------------------------------------------
def capacitor_energy(capacitance_f: float, voltage_v: float) -> float:
    """E = C V^2 / 2"""
    return 0.5 * capacitance_f * voltage_v ** 2


def inductor_energy(inductance_h: float, current_a: float) -> float:
    """E = L I^2 / 2"""
    return 0.5 * inductance_h * current_a ** 2


def rc_discharge(v0: float, r_ohm: float, c_f: float, t_s):
    """Capacitor voltage while it discharges through R: v = V0 exp(-t / (R C))."""
    return v0 * np.exp(-np.asarray(t_s, dtype=float) / (r_ohm * c_f))


def rc_charge(v_source: float, r_ohm: float, c_f: float, t_s):
    """Capacitor voltage while it charges from 0 V through R: v = V (1 - exp(-t / (R C)))."""
    return v_source * -np.expm1(-np.asarray(t_s, dtype=float) / (r_ohm * c_f))


def rc_time_to_discharge(v0: float, v_target: float, r_ohm: float, c_f: float) -> float:
    """t = R C ln(V0 / V_target)"""
    if not 0 < v_target < v0:
        raise ValueError("need 0 < target voltage < initial voltage")
    return r_ohm * c_f * math.log(v0 / v_target)


def rc_discharge_euler(v0: float, r_ohm: float, c_f: float, t_end_s: float, dt_s: float):
    """Explicit Euler solution of C dv/dt = -v / R; returns (times, voltages).
    Used to show how a numerical method approaches the exact answer as dt shrinks."""
    n = int(round(t_end_s / dt_s))
    t = np.linspace(0.0, n * dt_s, n + 1)
    v = np.empty(n + 1)
    v[0] = v0
    for k in range(n):
        v[k + 1] = v[k] - dt_s * v[k] / (r_ohm * c_f)
    return t, v


# ---- PV cell temperature (screening model, chapter 10 refines it) ---------------------
def cell_temperature_noct(t_air_c, irradiance_wm2, noct_c: float = 45.0):
    """T_cell = T_air + (NOCT - 20) / 800 * G   (NOCT test: 800 W/m2, 20 C air, 1 m/s wind)."""
    return np.asarray(t_air_c, dtype=float) + (noct_c - 20.0) / 800.0 * np.asarray(irradiance_wm2, dtype=float)


# ---- economic conductor size (Kelvin's law) ------------------------------------------
def kelvin_optimum_area(loss_constant_kwh_mm2: float, energy_value: float,
                        cost_per_mm2: float, annuity: float) -> float:
    """Area that minimises annual cost = annuity * cost_per_mm2 * A + energy_value * K / A.

    loss_constant_kwh_mm2: K such that annual loss energy = K / A (kWh per year).
    cost_per_mm2: installed conductor cost per mm2 of cross-section (whole circuit).
    annuity: fraction of the capital cost charged per year (chapter 21).
    d(cost)/dA = annuity * cost_per_mm2 - energy_value * K / A^2 = 0.
    """
    return math.sqrt(energy_value * loss_constant_kwh_mm2 / (annuity * cost_per_mm2))


# ---- general DC network solver (modified nodal analysis) ------------------------
@dataclass
class DCSolution:
    node_voltages: np.ndarray        # index = node number; node 0 is the reference (0 V)
    source_currents: np.ndarray      # current through each voltage source, + from its '-' to its '+' terminal inside the source


def solve_dc(n_nodes: int, resistors: list[tuple[int, int, float]],
             voltage_sources: list[tuple[int, int, float]] = (),
             current_sources: list[tuple[int, int, float]] = ()) -> DCSolution:
    """Solve a linear DC network.

    resistors:        (node_a, node_b, R_ohm)
    voltage_sources:  (node_plus, node_minus, V)  ideal source, + terminal at node_plus
    current_sources:  (node_from, node_to, I)     ideal source pushing I from node_from into node_to
    Node 0 is the reference. Returns node voltages and the current in each
    voltage source (positive when the source delivers current out of its + terminal).
    """
    if n_nodes < 2:
        raise ValueError("a circuit needs at least two nodes (one is the reference)")
    m = len(voltage_sources)
    size = (n_nodes - 1) + m
    a = np.zeros((size, size))
    z = np.zeros(size)

    def idx(node):
        return node - 1

    for na, nb, r in resistors:
        if r <= 0:
            raise ValueError("resistances must be positive")
        g = 1.0 / r
        for p, q, sign in ((na, na, +1), (nb, nb, +1), (na, nb, -1), (nb, na, -1)):
            if p != 0 and q != 0:
                a[idx(p), idx(q)] += sign * g
    for nf, nt, i in current_sources:
        if nf != 0:
            z[idx(nf)] -= i
        if nt != 0:
            z[idx(nt)] += i
    for k, (np_, nm, v) in enumerate(voltage_sources):
        row = (n_nodes - 1) + k
        if np_ != 0:
            a[idx(np_), row] += 1.0
            a[row, idx(np_)] += 1.0
        if nm != 0:
            a[idx(nm), row] -= 1.0
            a[row, idx(nm)] -= 1.0
        z[row] = v
    try:
        x = np.linalg.solve(a, z)
    except np.linalg.LinAlgError as exc:
        raise ValueError("singular network: a node is floating or sources conflict") from exc
    voltages = np.concatenate([[0.0], x[: n_nodes - 1]])
    # MNA gives the current flowing INTO the + terminal through the source; flip it
    return DCSolution(voltages, -x[n_nodes - 1:])


def thevenin(n_nodes: int, resistors, voltage_sources=(), current_sources=(),
             terminal_a: int = 1, terminal_b: int = 0) -> tuple[float, float]:
    """Thevenin voltage and resistance seen between two nodes.

    V_th: open-circuit voltage from the full network.
    R_th: with every source turned off (voltage sources shorted, current
    sources opened), inject 1 A at terminal_a and measure the voltage.
    """
    sol = solve_dc(n_nodes, resistors, voltage_sources, current_sources)
    v_th = sol.node_voltages[terminal_a] - sol.node_voltages[terminal_b]
    shorted = [(p, q, 1e-9) for p, q, _ in voltage_sources]      # a dead voltage source is a short
    probe = solve_dc(n_nodes, list(resistors) + shorted, (), [(terminal_b, terminal_a, 1.0)])
    r_th = probe.node_voltages[terminal_a] - probe.node_voltages[terminal_b]
    return float(v_th), float(r_th)


# ---- the PV string as a DC source (preview of chapter 10) ------------------------
@dataclass(frozen=True)
class PVModule:
    """Datasheet values at standard test conditions (1000 W/m2, 25 C, AM1.5)."""
    v_oc: float
    i_sc: float
    v_mp: float
    i_mp: float
    n_cells: int
    beta_voc_pct_per_c: float     # temperature coefficient of V_oc, percent per C (negative)
    alpha_isc_pct_per_c: float    # of I_sc, percent per C (small, positive)
    gamma_pmax_pct_per_c: float   # of P_max, percent per C (negative)


PVM_550 = PVModule(v_oc=49.90, i_sc=13.98, v_mp=41.96, i_mp=13.11, n_cells=144,
                   beta_voc_pct_per_c=-0.27, alpha_isc_pct_per_c=0.048, gamma_pmax_pct_per_c=-0.35)


def string_voc(module: PVModule, n_series: int, cell_temp_c: float) -> float:
    """Open-circuit voltage of n modules in series at a cell temperature
    (irradiance effect on V_oc neglected: a few percent, chapter 10)."""
    if n_series < 1:
        raise ValueError("a string has at least one module")
    return n_series * module.v_oc * (1.0 + module.beta_voc_pct_per_c / 100.0 * (cell_temp_c - 25.0))


def string_isc(module: PVModule, irradiance_wm2: float, cell_temp_c: float) -> float:
    """Short-circuit current of a string: proportional to irradiance, weakly rising with temperature."""
    if irradiance_wm2 < 0:
        raise ValueError("irradiance cannot be negative")
    return module.i_sc * irradiance_wm2 / 1000.0 * (1.0 + module.alpha_isc_pct_per_c / 100.0 * (cell_temp_c - 25.0))


def string_pmax(module: PVModule, n_series: int, irradiance_wm2: float, cell_temp_c: float) -> float:
    """Maximum power of a string with the datasheet temperature coefficient."""
    p_stc = n_series * module.v_mp * module.i_mp
    return p_stc * irradiance_wm2 / 1000.0 * (1.0 + module.gamma_pmax_pct_per_c / 100.0 * (cell_temp_c - 25.0))


def pv_iv_curve(module: PVModule, n_series: int, voltage_v, irradiance_wm2: float = 1000.0,
                cell_temp_c: float = 25.0, ideality: float = 1.0):
    """Current of a string at the given terminal voltage(s): a simplified
    one-diode model without series/shunt resistance, fitted to I_sc and V_oc.

    I = I_sc - I_0 (exp(V / (n_cells_total * a * V_t)) - 1)
    Good enough to SHOW the shape of the curve; chapter 10 fits a real model.
    """
    v = np.asarray(voltage_v, dtype=float)
    t_k = cell_temp_c + 273.15
    v_t = BOLTZMANN * t_k / ELEMENTARY_CHARGE
    n_tot = n_series * module.n_cells
    i_sc = string_isc(module, irradiance_wm2, cell_temp_c)
    v_oc = string_voc(module, n_series, cell_temp_c)
    if irradiance_wm2 <= 0:
        return np.zeros_like(v)
    i_0 = i_sc / math.expm1(v_oc / (n_tot * ideality * v_t))
    i = i_sc - i_0 * np.expm1(v / (n_tot * ideality * v_t))
    return np.clip(i, 0.0, None)


def pv_resistive_operating_point(module: PVModule, n_series: int, load_ohm: float,
                                 irradiance_wm2: float = 1000.0, cell_temp_c: float = 25.0):
    """Where a string's I-V curve meets a resistor's line I = V / R (bisection).

    Returns (voltage_v, current_a). The string current falls with voltage and
    the resistor current rises, so their difference changes sign exactly once.
    """
    if load_ohm <= 0:
        raise ValueError("load resistance must be positive")
    lo, hi = 0.0, string_voc(module, n_series, cell_temp_c)

    def gap(v):
        return float(pv_iv_curve(module, n_series, v, irradiance_wm2, cell_temp_c)) - v / load_ohm

    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if gap(mid) > 0:
            lo = mid
        else:
            hi = mid
    v = 0.5 * (lo + hi)
    return v, v / load_ohm


def max_modules_in_series(module: PVModule, system_voltage_v: float, min_cell_temp_c: float) -> int:
    """Largest string length whose cold open-circuit voltage stays at or below the system limit."""
    v_cold = string_voc(module, 1, min_cell_temp_c)
    return int(system_voltage_v // v_cold)
