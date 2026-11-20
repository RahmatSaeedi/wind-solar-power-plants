"""Grid-study tools (chapter 28).

Small, readable forms of the calculations behind an interconnection
study: the bus admittance matrix, a Newton-Raphson load flow, branch
flows and losses, a Thevenin source from a short-circuit level, fault
currents by the equivalent-source idea with converters as limited
current sources, the apparent impedance a distance relay sees, a
quasi-steady ride-through simulation, a frequency event on an
aggregated system, the non-detection zone of passive islanding relays,
grid-strength ratios, model-validation error measures, and the current
of a grid-forming source after a phase jump.

These are teaching forms. Real studies use the operator's network
model, validated vendor models and approved software and methods.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


# [start: branch]
@dataclass(frozen=True)
class Branch:
    """A line, cable or transformer in per unit: series r + jx, total
    shunt susceptance b, off-nominal tap on the i side, in service?"""
    i: int
    j: int
    r: float
    x: float
    b: float = 0.0
    tap: float = 1.0
    status: bool = True


def ybus(n: int, branches) -> np.ndarray:
    """Bus admittance matrix of n buses (pi model, tap on the i side)."""
    y = np.zeros((n, n), complex)
    for br in branches:
        if not br.status:
            continue
        ys = 1 / complex(br.r, br.x)
        t = br.tap
        y[br.i, br.i] += ys / t ** 2 + 0.5j * br.b
        y[br.j, br.j] += ys + 0.5j * br.b
        y[br.i, br.j] -= ys / t
        y[br.j, br.i] -= ys / t
    return y
# [end: branch]


# [start: loadflow]
def load_flow(y: np.ndarray, kind, p, q, v_set, tol: float = 1e-9,
              max_iter: int = 30) -> dict:
    """Newton-Raphson load flow in polar form. kind[k] is 'slack', 'pv'
    or 'pq'; p, q are specified injections (generation positive, pu);
    v_set holds the voltage magnitude of slack and pv buses."""
    n = len(kind)
    live = _energised(y, [k for k in range(n) if kind[k] == "slack"])
    pv = [k for k in range(n) if kind[k] == "pv" and k in live]
    pq = [k for k in range(n) if kind[k] == "pq" and k in live]
    pvpq = pv + pq
    vm = np.array([(v_set[k] if kind[k] != "pq" else 1.0) if k in live else 0.0
                   for k in range(n)])
    va = np.zeros(n)
    p, q = np.asarray(p, float), np.asarray(q, float)
    for it in range(max_iter + 1):
        v = vm * np.exp(1j * va)
        i = y @ v
        s = v * np.conj(i)
        mis = np.r_[p[pvpq] - s.real[pvpq], q[pq] - s.imag[pq]]
        if np.max(np.abs(mis)) < tol:
            return {"v": v, "s": s, "iterations": it}
        vn = np.divide(v, vm, out=np.zeros_like(v), where=vm > 0)
        ds_dva = 1j * np.diag(v) @ np.conj(np.diag(i) - y @ np.diag(v))
        ds_dvm = (np.diag(v) @ np.conj(y @ np.diag(vn))
                  + np.conj(np.diag(i)) @ np.diag(vn))
        jac = np.block([
            [ds_dva.real[np.ix_(pvpq, pvpq)], ds_dvm.real[np.ix_(pvpq, pq)]],
            [ds_dva.imag[np.ix_(pq, pvpq)], ds_dvm.imag[np.ix_(pq, pq)]]])
        try:
            dx = np.linalg.solve(jac, mis)
        except np.linalg.LinAlgError as err:
            raise RuntimeError("load flow did not converge") from err
        va[pvpq] += dx[:len(pvpq)]
        vm[pq] += dx[len(pvpq):]
    raise RuntimeError("load flow did not converge")
# [end: loadflow]


def _energised(y: np.ndarray, slack: list) -> set:
    """Buses connected to a slack bus through the network (others are
    de-energised: voltage 0, left out of the load flow)."""
    seen, todo = set(slack), list(slack)
    while todo:
        k = todo.pop()
        for j in np.nonzero(np.abs(y[k]) > 0)[0]:
            if j not in seen:
                seen.add(int(j))
                todo.append(int(j))
    return seen


def flows(v: np.ndarray, branches) -> list[dict]:
    """Complex power into each branch end (pu) and its losses."""
    out = []
    for br in branches:
        if not br.status:
            out.append({"s_ij": 0j, "s_ji": 0j, "loss": 0j, "i": 0.0})
            continue
        ys = 1 / complex(br.r, br.x)
        t = br.tap
        vi, vj = v[br.i], v[br.j]
        i_ij = (ys / t ** 2 + 0.5j * br.b) * vi - ys / t * vj
        i_ji = -ys / t * vi + (ys + 0.5j * br.b) * vj
        s_ij, s_ji = vi * np.conj(i_ij), vj * np.conj(i_ji)
        out.append({"s_ij": s_ij, "s_ji": s_ji, "loss": s_ij + s_ji,
                    "i": max(abs(i_ij), abs(i_ji))})
    return out


def thevenin(s_sc_mva: float, xr: float, s_base: float = 100.0) -> complex:
    """Source impedance (pu on s_base) for a short-circuit level and X/R."""
    zm = s_base / s_sc_mva
    r = zm / math.sqrt(1 + xr ** 2)
    return complex(r, r * xr)


# [start: fault]
def fault_current(zb: np.ndarray, k: int, c: float = 1.1,
                  sources=()) -> dict:
    """Three-phase bolted fault at bus k (pu): the voltage source c of
    the network behind the bus impedance matrix zb, plus converters as
    current sources (bus, current pu) that inject reactive current
    (lagging the pre-fault voltage) during the fault."""
    z_kk = zb[k, k]
    v_open = c + sum(zb[k, j] * (-1j * i_j) for j, i_j in sources)
    i_grid = c / z_kk
    i_total = v_open / z_kk
    return {"grid": abs(i_grid), "converters": abs(i_total) - abs(i_grid),
            "total": abs(i_total)}
# [end: fault]


def apparent_impedance(z_to_fault: complex, r_fault: float,
                       i_local: complex, i_remote: complex) -> complex:
    """Impedance a distance relay sees for a fault through r_fault when
    the far end feeds the same fault resistance."""
    return z_to_fault + r_fault * (1 + i_remote / i_local)


# [start: frt]
def frt_sim(t: np.ndarray, e_grid: np.ndarray, z: complex, p0: float,
            k: float = 2.0, imax: float = 1.1, tau: float = 0.02,
            ramp: float = 2.0) -> dict:
    """Quasi-steady ride-through: grid source e_grid(t) behind z (pu on
    the plant's rating). Below 0.9 pu the plant injects reactive current
    k (1 - U) and gives it priority within imax; active current that this
    cuts comes back after the dip at ramp pu/s. Currents follow through a
    lag tau. The POC voltage is the reference phasor."""
    dt = t[1] - t[0]
    iq = id_ = 0.0
    u_out, p_out, q_out = [], [], []
    p_lim, cut, u = p0, False, 1.0
    for e in e_grid:
        if u < 0.9:
            iq_ref = min(k * (1 - u), imax)
            room = math.sqrt(max(imax ** 2 - iq_ref ** 2, 0.0))
            id_ref = min(p0 / max(u, 0.05), room)
            cut = cut or (iq_ref > 0 and id_ref < p0 / max(u, 0.05))
            p_lim = u * id_ref
        else:
            iq_ref = 0.0
            p_lim = min(p0, p_lim + ramp * dt) if cut else p0
            cut = cut and p_lim < p0
            id_ref = min(p_lim / u, imax)
        iq += (iq_ref - iq) * dt / tau
        id_ += (id_ref - id_) * dt / tau
        w = z * complex(id_, -iq)            # E = U - z I (I into the grid)
        u = max(w.real + math.sqrt(max(e * e - w.imag ** 2, 0.0)), 0.0)
        u_out.append(u)
        p_out.append(u * id_)
        q_out.append(u * iq)
    return {"u": np.array(u_out), "p": np.array(p_out),
            "q": np.array(q_out)}
# [end: frt]


# [start: freq]
def freq_event(t: np.ndarray, s_sys: float, h: float, dp_loss: float,
               d_load: float = 1.0, gov=(0.05, 6.0, 0.10),
               plant=None, f0: float = 50.0) -> dict:
    """Frequency after losing dp_loss MW on an aggregated system of
    s_sys MW with inertia constant h (s) and load damping d_load (% of
    load per % of frequency). gov = (droop, time constant s, share of
    the system that responds); plant = (MW rated, droop, deadband Hz,
    headroom up MW, time constant s[, MW it may reduce]) or None."""
    dt = t[1] - t[0]
    df = 0.0
    p_gov = p_plant = 0.0
    f_out, pp_out = [], []
    r_g, t_g, share = gov
    for _ in t:
        target_g = -df / (r_g * f0) * s_sys * share
        p_gov += (target_g - p_gov) * dt / t_g
        if plant is not None:
            rated, r_p, db, head, t_p, *rest = plant
            down = rest[0] if rest else 0.0
            dev = df + db if df < -db else (df - db if df > db else 0.0)
            target_p = min(max(-dev / (r_p * f0) * rated, -down), head)
            p_plant += (target_p - p_plant) * dt / t_p
        damping = d_load * df / f0 * s_sys
        dfdt = (p_gov + p_plant - dp_loss - damping) / s_sys * f0 / (2 * h)
        df += dfdt * dt
        f_out.append(f0 + df)
        pp_out.append(p_plant)
    f = np.array(f_out)
    return {"f": f, "nadir": float(f.min()), "plant_mw": np.array(pp_out),
            "rocof": float((f[min(int(0.5 / dt), len(f) - 1)] - f0) / 0.5)}
# [end: freq]


def ndz(v_min: float, v_max: float, f_min: float, f_max: float,
        qf: float, f0: float = 50.0) -> dict:
    """Non-detection zone of passive under/over voltage and frequency
    relays for a parallel RLC load of quality factor qf: ranges of the
    power mismatch dP/P and dQ/P (grid supplies the mismatch) inside
    which an island keeps voltage and frequency within the windows."""
    return {"dp": ((1 / v_max) ** 2 - 1, (1 / v_min) ** 2 - 1),
            "dq": (qf * (1 - (f0 / f_min) ** 2), qf * (1 - (f0 / f_max) ** 2))}


def escr(s_sc_mva: float, q_shunt_mvar: float, p_mw: float) -> float:
    """Effective short-circuit ratio: shunt capacitors at the bus reduce
    the strength the plant sees."""
    return (s_sc_mva - q_shunt_mvar) / p_mw


def wscr(s_sc_mva, p_mw) -> float:
    """Weighted short-circuit ratio of several plants close together
    (one common weighting): sum(S_sc,i P_i) / (sum P_i)^2."""
    s, p = np.asarray(s_sc_mva, float), np.asarray(p_mw, float)
    return float(np.sum(s * p) / np.sum(p) ** 2)


def validation_errors(t: np.ndarray, sim: np.ndarray, meas: np.ndarray,
                      windows: dict) -> dict:
    """Mean, mean absolute and maximum error of sim - meas in named time
    windows {name: (t_start, t_end)}."""
    out = {}
    for name, (a, b) in windows.items():
        m = (t >= a) & (t < b)
        e = sim[m] - meas[m]
        out[name] = {"me": float(e.mean()), "mae": float(np.abs(e).mean()),
                     "mxe": float(np.abs(e).max())}
    return out


def phase_jump_current(dtheta_deg: float, x_pu: float) -> float:
    """Extra current (pu) a voltage source behind x_pu must carry when the
    grid voltage angle jumps by dtheta_deg."""
    return 2 * math.sin(math.radians(dtheta_deg) / 2) / x_pu


def sync_power(v1: float, v2: float, x_pu: float, dtheta_deg: float) -> float:
    """Active power (pu) that flows the moment two systems are joined
    through x_pu with an angle difference dtheta_deg."""
    return v1 * v2 * math.sin(math.radians(dtheta_deg)) / x_pu
