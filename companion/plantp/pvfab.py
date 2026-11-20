"""PV cell and module manufacturing arithmetic (chapter 41), at textbook
level and without any process recipe: absorption depth and diffusion
length, open-circuit voltage from the saturation current, the empirical
fill factor and its series-resistance loss, a cell loss budget, binning
of cells by current, the mismatch loss of cells in series, the
cell-to-module ratio and the resistive gain of half-cut cells, robust
outlier flags for flash-test data, translation of a flash reading to
STC, and the longest string a cold morning allows.

Every function is checked by hand in companion/tests/test_ch41_pvfab.py.
"""
from __future__ import annotations

import math
from statistics import median

K_B = 1.380649e-23
Q_E = 1.602176634e-19


def thermal_voltage(t_c: float = 25.0) -> float:
    """kT/q in volts."""
    return K_B * (t_c + 273.15) / Q_E


# [start: device]
def absorption_depth_um(alpha_per_cm: float) -> float:
    """Depth at which light falls to 1/e of its value, micrometres."""
    return 1e4 / alpha_per_cm


def diffusion_length_um(d_cm2_s: float, tau_s: float) -> float:
    """How far a minority carrier wanders before it recombines."""
    return 1e4 * math.sqrt(d_cm2_s * tau_s)


def voc(jsc: float, j0: float, n: float = 1.0, t_c: float = 25.0) -> float:
    """Open-circuit voltage of a cell from its short-circuit and
    saturation current densities (same units)."""
    return n * thermal_voltage(t_c) * math.log(jsc / j0 + 1)


def fill_factor(voc_v: float, rs_ohm_cm2: float = 0.0, jsc: float = 0.0,
                n: float = 1.0, t_c: float = 25.0,
                rsh_ohm_cm2: float = math.inf) -> float:
    """Empirical fill factor (Green): ideal value from the normalised
    Voc, reduced by the series resistance r_s = R_s J_sc / V_oc and by
    the shunt r_sh = R_sh J_sc / V_oc (r_sh infinite: no shunt)."""
    v = voc_v / (n * thermal_voltage(t_c))
    ff0 = (v - math.log(v + 0.72)) / (v + 1)
    rs = rs_ohm_cm2 * jsc / voc_v if voc_v else 0.0
    ffs = ff0 * (1 - rs)
    if math.isinf(rsh_ohm_cm2):
        return ffs
    rsh = rsh_ohm_cm2 * jsc / voc_v
    return ffs * (1 - (v + 0.7) / v * ffs / rsh)
# [end: device]


def loss_budget(steps) -> list[tuple[str, float, float]]:
    """Waterfall of a cell's efficiency: each step keeps a share of what
    reaches it. Returns (step, share kept, efficiency after)."""
    eff, out = 1.0, []
    for name, keep in steps:
        eff *= keep
        out.append((name, keep, eff))
    return out


# [start: binning]
def bin_of(current_a: float, edges) -> int:
    """Index of the current bin a cell falls in (edges ascending)."""
    for k in range(len(edges) - 1):
        if edges[k] <= current_a < edges[k + 1]:
            return k
    raise ValueError("current outside the bins")


def series_mismatch(currents, v_cell: float = 0.6) -> float:
    """Share of power lost when cells of different current are put in
    series and the string runs at the weakest current (no bypass acting):
    a first, conservative estimate."""
    p_sum = sum(currents) * v_cell
    p_string = min(currents) * v_cell * len(currents)
    return 1 - p_string / p_sum
# [end: binning]


# [start: mismatch]
def string_pmax(curves) -> float:
    """Maximum power of curves in series (each with its bypass diode),
    swept in current with the ch 15 model."""
    from plantp.mppt import pv_curve_partial
    _, _, p = pv_curve_partial(curves, n=6000)
    return float(p.max())


def mismatch_loss(curves) -> float:
    """Share of the summed individual maximum powers lost in series."""
    alone = sum(c.mpp()[1] for c in curves)
    return 1 - string_pmax(curves) / alone


def cells_pmax(curves, n: int = 4000) -> float:
    """Maximum power of cells in series with no diode of their own: the
    string current cannot exceed the weakest cell's I_sc (reverse
    breakdown ignored - a conservative first estimate)."""
    import numpy as np
    i = np.linspace(0.0, min(c.isc for c in curves), n)
    v = sum(c.v(i) for c in curves)
    return float((v * i).max())


def cell_mismatch_loss(curves) -> float:
    alone = sum(c.mpp()[1] for c in curves)
    return 1 - cells_pmax(curves) / alone
# [end: mismatch]


def ctm(p_module: float, p_cells) -> float:
    """Cell-to-module power ratio."""
    return p_module / sum(p_cells)


def half_cut_gain(i_full: float, r_ribbon: float, n_cells: int) -> float:
    """Ribbon power saved by half-cut cells: the current in each half is
    halved, so I^2 R falls to a quarter in twice the number of paths of
    half the length - a net quarter of the full-cell loss is kept."""
    full = i_full ** 2 * r_ribbon * n_cells
    half = 2 * (i_full / 2) ** 2 * (r_ribbon / 2) * n_cells
    return full - half


# [start: outliers]
def robust_z(values):
    """Robust z-scores from the median and the median absolute deviation
    (0.6745 makes them comparable with ordinary z for normal data)."""
    med = median(values)
    mad = median(abs(x - med) for x in values)
    if mad == 0:
        raise ValueError("no spread in the data")
    return [0.6745 * (x - med) / mad for x in values]


def flag_outliers(values, limit: float = 3.5) -> list[int]:
    return [k for k, z in enumerate(robust_z(values)) if abs(z) > limit]
# [end: outliers]


def to_stc(p_meas: float, g_meas: float, t_meas_c: float,
           gamma_pct_per_c: float = -0.35) -> float:
    """Simple translation of a flash reading to STC by irradiance ratio
    and power temperature coefficient (a teaching approximation; the
    laboratory uses the standard's procedure)."""
    return p_meas * (1000.0 / g_meas) / (1 + gamma_pct_per_c / 100 *
                                          (t_meas_c - 25.0))


def max_string_length(voc_stc: float, beta_pct_per_c: float,
                      t_min_c: float, v_max: float) -> int:
    """Longest string whose open-circuit voltage on the coldest morning
    stays below the system voltage."""
    voc_cold = voc_stc * (1 + beta_pct_per_c / 100 * (t_min_c - 25.0))
    return math.floor(v_max / voc_cold)
