"""Chapter 26 - protection, earthing and lightning quantities for
teaching: fault currents by symmetrical components, inverse-time
overcurrent curves and grading margins, current-transformer knee-point
checks, differential bias, distance zones, earth-grid resistance and
ground potential rise, and lightning strike frequency on a structure.

Teaching relations: settings, grids and lightning protection are
designed from the approved network model and site data by qualified
engineers and approved by the responsible operator.
"""
from __future__ import annotations

import math

A = complex(-0.5, math.sqrt(3) / 2)


# [start: faults]
def fault_currents(e_ph: float, z1: complex, z2: complex, z0: complex,
                   zf: complex = 0j) -> dict:
    """Fault currents (A) at a bus with phase voltage e_ph (V) and
    sequence impedances (ohm): three-phase, line-to-line, single
    line-to-earth (through zf)."""
    i3 = e_ph / abs(z1)
    ill = math.sqrt(3) * e_ph / abs(z1 + z2)
    ise = 3 * e_ph / abs(z1 + z2 + z0 + 3 * zf)
    return {"3ph": i3, "LL": ill, "SLG": ise}
# [end: faults]


# [start: idmt]
CURVES = {   # inverse-time curve constants (k, alpha), standard forms
    "standard inverse": (0.14, 0.02),
    "very inverse": (13.5, 1.0),
    "extremely inverse": (80.0, 2.0),
}


def trip_time(i: float, pickup: float, tms: float,
              curve: str = "standard inverse") -> float:
    """Operating time (s) of an inverse-time overcurrent element:
    t = TMS k / ((I/Is)^alpha - 1); inf below pickup."""
    k, a = CURVES[curve]
    m = i / pickup
    return math.inf if m <= 1 else tms * k / (m ** a - 1)


def grading_ok(t_down: float, t_up: float, margin: float = 0.3) -> bool:
    """Upstream relay slower than downstream by at least the margin."""
    return t_up - t_down >= margin
# [end: idmt]


def ct_knee_ok(v_knee: float, i_fault_sec: float, r_ct: float,
               r_burden: float, k: float = 2.0) -> bool:
    """Teaching check: knee-point voltage >= k x If (secondary) x
    (R_ct + R_burden)."""
    return v_knee >= k * i_fault_sec * (r_ct + r_burden)


def diff_trips(i1: float, i2: float, pickup: float = 0.2,
               slope: float = 0.3) -> bool:
    """Biased differential (per unit): trip when |I1 - I2| > pickup +
    slope x (|I1| + |I2|) / 2 (currents with their signs into the zone)."""
    diff = abs(i1 + i2)
    bias = (abs(i1) + abs(i2)) / 2
    return diff > pickup + slope * bias


def distance_zones(z_line: float, z_next: float) -> dict:
    """Typical teaching reaches: zone 1 80 % of the line, zone 2 the line
    plus 50 % of the next, zone 3 the line plus 120 % of the next."""
    return {"Z1": 0.8 * z_line, "Z2": z_line + 0.5 * z_next,
            "Z3": z_line + 1.2 * z_next}


# [start: earthing]
def grid_resistance(rho: float, area_m2: float, length_m: float) -> float:
    """Approximate resistance of a buried mesh: rho/(4 r) + rho/L, with
    r the radius of a circle of the same area (teaching form)."""
    r = math.sqrt(area_m2 / math.pi)
    return rho / (4 * r) + rho / length_m


def gpr(i_grid: float, r_grid: float) -> float:
    """Ground potential rise (V) for the share of fault current that
    returns through the earth grid."""
    return i_grid * r_grid
# [end: earthing]


# [start: lightning]
def collection_area(h: float, l_m: float = 0.0, w_m: float = 0.0) -> float:
    """Collection area (m2) of a structure of height h: a tall slender
    one 9 pi h^2; a building L x W adds the 3h band around it."""
    if l_m == 0 and w_m == 0:
        return 9 * math.pi * h ** 2
    return l_m * w_m + 6 * h * (l_m + w_m) + 9 * math.pi * h ** 2


def strikes_per_year(ng_per_km2: float, area_m2: float,
                     cd: float = 1.0) -> float:
    """Expected direct strikes a year: Ng x Ae x location factor."""
    return ng_per_km2 * area_m2 / 1e6 * cd
# [end: lightning]


# [start: sequence]
def sequence(ia: complex, ib: complex, ic: complex) -> tuple:
    """Zero, positive and negative sequence components of three phasors."""
    i0 = (ia + ib + ic) / 3
    i1 = (ia + A * ib + A * A * ic) / 3
    i2 = (ia + A * A * ib + A * ic) / 3
    return i0, i1, i2
# [end: sequence]


def phasor(mag: float, deg: float) -> complex:
    """Phasor from magnitude and angle in degrees."""
    return mag * complex(math.cos(math.radians(deg)), math.sin(math.radians(deg)))


def pickup_window(i_load_max: float, i_fault_min: float,
                  k_load: float = 1.2, k_fault: float = 1.5) -> tuple:
    """Allowed pickup range: above k_load x the largest load current and
    below the smallest fault current / k_fault; (low, high, feasible)."""
    lo, hi = k_load * i_load_max, i_fault_min / k_fault
    return lo, hi, lo < hi


def tms_for(t_target: float, i: float, pickup: float,
            curve: str = "standard inverse") -> float:
    """Time multiplier that gives time t_target at current i."""
    return t_target / trip_time(i, pickup, 1.0, curve)


# [start: earth-physics]
def hemisphere_v(rho: float, i: float, r: float) -> float:
    """Surface potential (V) at distance r (m) from the centre of a
    hemispherical electrode carrying i (A) into soil of rho (ohm m)."""
    return rho * i / (2 * math.pi * r)


def foot_resistance(rho_surface: float, b: float = 0.08) -> float:
    """Resistance (ohm) of one foot as a disc of radius b on the surface:
    rho / (4 b)."""
    return rho_surface / (4 * b)


def body_current(v_touch: float, r_body: float, r_foot: float,
                 feet: str = "touch") -> float:
    """Body current (A) for a touch (feet in parallel) or step (feet in
    series) voltage."""
    r_feet = r_foot / 2 if feet == "touch" else 2 * r_foot
    return v_touch / (r_body + r_feet)
# [end: earth-physics]


def rolling_sphere_r(h: float, radius: float) -> float:
    """Protected radius at ground level around a mast of height h under
    a rolling sphere of the given radius (h <= radius)."""
    h = min(h, radius)
    return math.sqrt(h * (2 * radius - h))


def loop_voltage(area_m2: float, d_m: float, di_dt: float) -> float:
    """Voltage induced in a small loop of area A at distance d from a
    straight lightning channel with current slope di/dt (A/s)."""
    mu0 = 4e-7 * math.pi
    return mu0 * area_m2 / (2 * math.pi * d_m) * di_dt


def at_equipment(u_res_kv: float, s_m: float, du_dt_kv_us: float,
                 v_m_us: float = 300.0) -> float:
    """Teaching travelling-wave estimate of the voltage at equipment a
    distance s beyond the arrester: U_res + 2 S (dU/dt) / v."""
    return u_res_kv + 2 * s_m * du_dt_kv_us / v_m_us


def fuse_needed(n_strings: int, i_sc: float, i_reverse: float) -> bool:
    """String fuses are needed when the other strings in parallel can
    push more than the module's reverse current rating back through a
    faulted string: (n - 1) x Isc > I_reverse."""
    return (n_strings - 1) * i_sc > i_reverse


def p_fail_to_clear(p_main: float, p_backup: float) -> float:
    """Probability a fault is not cleared when main and independent
    backup each fail to operate with the given probabilities."""
    return p_main * p_backup
