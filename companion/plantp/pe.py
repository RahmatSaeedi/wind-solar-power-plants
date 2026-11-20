"""Power electronics (chapter 9): converter relations, PWM, semiconductor
losses and temperatures, efficiency, filters, DC link, fault-ride-through
current and a few component checks.

Every function is a first-order teaching model with its assumptions in the
docstring. Real designs use the semiconductor maker's curves, circuit
simulation and tests (chapter 9, sections C and D).
"""
from __future__ import annotations

import math

import numpy as np

S2 = math.sqrt(2.0)
S3 = math.sqrt(3.0)


# ---------------------------------------------------------- DC-DC converters
def buck_duty(v_in: float, v_out: float) -> float:
    """Ideal buck converter in continuous conduction: D = V_out / V_in."""
    if not 0 < v_out <= v_in:
        raise ValueError("a buck converter needs 0 < V_out <= V_in")
    return v_out / v_in


def boost_duty(v_in: float, v_out: float) -> float:
    """Ideal boost converter in continuous conduction: D = 1 - V_in / V_out."""
    if not 0 < v_in <= v_out:
        raise ValueError("a boost converter needs 0 < V_in <= V_out")
    return 1.0 - v_in / v_out


def buck_ripple(v_in: float, duty: float, l_h: float, f_sw: float) -> float:
    """Peak-to-peak inductor ripple of a buck: V_in D (1 - D) / (L f)."""
    return v_in * duty * (1.0 - duty) / (l_h * f_sw)


def boost_ripple(v_in: float, duty: float, l_h: float, f_sw: float) -> float:
    """Peak-to-peak inductor current ripple of a boost: V_in D / (L f)."""
    return v_in * duty / (l_h * f_sw)


def boost_cap_ripple(i_out: float, duty: float, c_f: float,
                     f_sw: float) -> float:
    """Peak-to-peak output voltage ripple of a boost: I_out D / (C f)."""
    return i_out * duty / (c_f * f_sw)


# ------------------------------------------------------------- rectifiers
def rectifier_6p_vdc(v_ll: float, l_s_h: float = 0.0, i_d: float = 0.0,
                     f_hz: float = 50.0, alpha_deg: float = 0.0) -> float:
    """Mean DC voltage of a six-pulse bridge: (3 sqrt2 / pi) V_LL cos(alpha)
    minus the commutation drop 3 omega L_s I_d / pi."""
    v0 = 3 * S2 / math.pi * v_ll * math.cos(math.radians(alpha_deg))
    return v0 - 3 * 2 * math.pi * f_hz * l_s_h * i_d / math.pi


# --------------------------------------------------------- inverter voltage
def vdc_min(v_ll: float, method: str = "svpwm",
            headroom: float = 0.0) -> float:
    """Smallest DC-link voltage that can synthesise V_LL (RMS) in the linear
    range: sine-triangle PWM needs 2 sqrt2 V_LL / sqrt3, space-vector (or
    third-harmonic) PWM needs sqrt2 V_LL; `headroom` adds a fraction for the
    filter drop, control margin and grid overvoltage."""
    if method == "spwm":
        base = 2 * S2 * v_ll / S3
    elif method == "svpwm":
        base = S2 * v_ll
    else:
        raise ValueError("method is 'spwm' or 'svpwm'")
    return base * (1.0 + headroom)


def vll_max(v_dc: float, method: str = "svpwm") -> float:
    """Largest RMS line voltage a DC-link voltage can make (inverse of
    vdc_min)."""
    return v_dc / vdc_min(1.0, method)


# -------------------------------------------------------------------- PWM
def spwm_leg(m: float, f1: float, f_sw: float, n: int = 20000, levels: int = 2,
             phase_deg: float = 0.0, third: float = 0.0):
    """Naturally sampled carrier PWM of one phase leg over one fundamental
    period. Returns (t, switch state) with the state in {0, 1} (two-level)
    or {-1, 0, 1} (three-level, phase-disposition carriers). `third` adds a
    third-harmonic share to the reference (1/6 lets m reach 2/sqrt3)."""
    t = np.arange(n) / (n * f1)
    th = 2 * np.pi * f1 * t + math.radians(phase_deg)
    ref = m * (np.sin(th) + third * np.sin(3 * th))
    x = (f_sw * t) % 1.0
    tri = np.where(x < 0.5, 4 * x - 1, 3 - 4 * x)            # -1 .. 1
    if levels == 2:
        return t, (ref > tri).astype(float)
    if levels == 3:
        up = (tri + 1) / 2                                    # 0 .. 1
        return t, np.where(ref >= 0, (ref > up).astype(float),
                           -(ref < -up).astype(float))
    raise ValueError("levels is 2 or 3")


def spectrum(x, f1: float):
    """Single-sided amplitude spectrum of one period (sample count = len(x)):
    returns (harmonic orders, amplitudes)."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    c = np.fft.rfft(x) / n
    amp = np.abs(c) * 2
    amp[0] /= 2
    return np.arange(len(amp)), amp


def thd(amp, h_max: int | None = None) -> float:
    """Total harmonic distortion from a spectrum indexed by harmonic order."""
    a = np.asarray(amp, dtype=float)
    top = len(a) if h_max is None else min(len(a), h_max + 1)
    return float(np.sqrt(np.sum(a[2:top] ** 2)) / a[1])


# ---------------------------------------------------------------- losses
def conduction_losses(i_pk: float, m: float, cos_phi: float, v_t0: float,
                      r_t: float, v_d0: float,
                      r_d: float) -> tuple[float, float]:
    """Mean conduction loss of one IGBT and one diode of a two-level leg with
    sinusoidal PWM (current peak I, modulation m, displacement cos phi), from
    the threshold-plus-resistance device model."""
    p_t = (1 / (2 * math.pi) + m * cos_phi / 8) * v_t0 * i_pk \
        + (1 / 8 + m * cos_phi / (3 * math.pi)) * r_t * i_pk ** 2
    p_d = (1 / (2 * math.pi) - m * cos_phi / 8) * v_d0 * i_pk \
        + (1 / 8 - m * cos_phi / (3 * math.pi)) * r_d * i_pk ** 2
    return p_t, p_d


def switching_losses(i_pk: float, v_dc: float, f_sw: float, e_on_off: float,
                     e_rr: float, i_ref: float,
                     v_ref: float) -> tuple[float, float]:
    """Mean switching loss of one IGBT and one diode: the data-sheet energies
    at (I_ref, V_ref) scaled linearly in current and voltage and averaged over
    a sine half-wave (factor 1/pi)."""
    k = (i_pk / i_ref) * (v_dc / v_ref) / math.pi
    return f_sw * e_on_off * k, f_sw * e_rr * k


def leg_losses_numeric(i_pk: float, m: float, phi_deg: float, v_dc: float,
                       f_sw: float, dev: dict, n: int = 200000) -> dict:
    """Time-domain check of the averaged formulas: one fundamental period of
    a naturally sampled leg; conduction from the instantaneous duty, one
    turn-on and one turn-off energy per carrier period (data-sheet energy
    scaled linearly). Returns IGBT and diode losses of the upper switch
    pair."""
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    i = i_pk * np.sin(th - math.radians(phi_deg))
    duty = 0.5 * (1 + m * np.sin(th))
    pos = i > 0
    ip = np.where(pos, i, 0.0)
    p_ct = duty * (dev["v_t0"] * ip + dev["r_t"] * ip ** 2)
    p_cd = (1 - duty) * (dev["v_d0"] * ip + dev["r_d"] * ip ** 2)
    k = (ip / dev["i_ref"]) * (v_dc / dev["v_ref"])
    p_st = f_sw * dev["e_on_off"] * k
    p_sd = f_sw * dev["e_rr"] * k
    return {"cond_t": float(p_ct.mean()), "cond_d": float(p_cd.mean()),
            "sw_t": float(p_st.mean()), "sw_d": float(p_sd.mean())}


def leg_losses_switched(i_pk: float, m: float, phi_deg: float, v_dc: float,
                        f_sw: float, l_h: float, dev: dict, f1: float = 50.0,
                        steps_per_carrier: int = 200) -> dict:
    """Independent check: simulate one fundamental period of a two-level leg
    switch by switch. The leg current is the fundamental plus the ripple that
    the switched voltage drives through L; conduction uses the instantaneous
    current, each switching event uses the current at that instant. Returns
    the upper IGBT and upper diode losses and the peak-to-peak ripple."""
    n_car = int(round(f_sw / f1))
    n = n_car * steps_per_carrier
    dt = 1 / (f1 * n)
    t = np.arange(n) * dt
    th = 2 * np.pi * f1 * t
    x = (f_sw * t) % 1.0
    tri = np.where(x < 0.5, 4 * x - 1, 3 - 4 * x)
    state = (m * np.sin(th) > tri).astype(float)
    v_err = v_dc * (state - 0.5 * (1 + m * np.sin(th)))
    rip = np.cumsum(v_err) * dt / l_h
    rip = rip.reshape(n_car, steps_per_carrier)
    rip = (rip - rip.mean(axis=1, keepdims=True)).ravel()
    i = i_pk * np.sin(th - math.radians(phi_deg)) + rip
    up = state > 0.5
    p_t = np.where(up & (i > 0), dev["v_t0"] * i + dev["r_t"] * i ** 2, 0.0)
    p_d = np.where(up & (i < 0), dev["v_d0"] * -i + dev["r_d"] * i ** 2, 0.0)
    trans = np.flatnonzero(np.diff(state) != 0) + 1
    e_t = e_d = 0.0
    for k in trans:
        scale = abs(i[k]) / dev["i_ref"] * v_dc / dev["v_ref"]
        if i[k] > 0:                                   # T1 turns on or off
            e_t += 0.5 * dev["e_on_off"] * scale
        elif state[k] < 0.5:                           # 1 -> 0 with i < 0
            e_d += dev["e_rr"] * scale                 # D1 recovers
    period = 1 / f1
    return {"cond_t": float(p_t.mean()), "cond_d": float(p_d.mean()),
            "sw_t": e_t / period, "sw_d": e_d / period,
            "ripple_pp": float(np.ptp(rip))}


def npc_leg_losses(i_pk: float, m: float, phi_deg: float, v_dc: float,
                   f_sw: float, dev: dict, n: int = 20000) -> dict:
    """Losses of the devices of one three-level neutral-point-clamped leg
    (T1..T4 switches, D1..D4 their diodes, D5/D6 clamp diodes) with
    phase-disposition PWM and duty-averaged conduction. Each switching event
    blocks V_dc / 2; `dev` holds the data of one switch position at
    (I_ref, V_ref). Returns a dict of losses in watts per device."""
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    ref = m * np.sin(th)
    i = i_pk * np.sin(th - math.radians(phi_deg))
    a = np.abs(i)
    pc_t = dev["v_t0"] * a + dev["r_t"] * a ** 2
    pc_d = dev["v_d0"] * a + dev["r_d"] * a ** 2
    k = a / dev["i_ref"] * (v_dc / 2) / dev["v_ref"]
    e_sw = f_sw * dev["e_on_off"] * k
    e_rr = f_sw * dev["e_rr"] * k
    d_out = np.abs(ref)                       # time in P (ref > 0) or N
    d_mid = 1 - d_out                         # time in O
    pos, neg = ref >= 0, ref < 0
    ip, im = i > 0, i < 0
    out = {}
    out["T1"] = np.where(pos & ip, d_out * pc_t + e_sw, 0.0)
    out["T2"] = (np.where(pos & ip, pc_t, 0.0)
                 + np.where(neg & ip, d_mid * pc_t + e_sw, 0.0))
    out["T3"] = (np.where(neg & im, pc_t, 0.0)
                 + np.where(pos & im, d_mid * pc_t + e_sw, 0.0))
    out["T4"] = np.where(neg & im, d_out * pc_t + e_sw, 0.0)
    out["D1"] = np.where(pos & im, d_out * pc_d + e_rr, 0.0)
    out["D2"] = np.where(pos & im, d_out * pc_d, 0.0)
    out["D3"] = np.where(neg & ip, d_out * pc_d, 0.0)
    out["D4"] = np.where(neg & ip, d_out * pc_d + e_rr, 0.0)
    out["D5"] = np.where(pos & ip, d_mid * pc_d + e_rr, 0.0)
    out["D6"] = np.where(neg & im, d_mid * pc_d + e_rr, 0.0)
    return {key: float(val.mean()) for key, val in out.items()}


# ----------------------------------------------------------------- thermal
def tj_steady(p_w: float, r_jc: float, r_ch: float, r_ha: float,
              t_amb_c: float) -> float:
    """Steady junction temperature through a series thermal path."""
    return t_amb_c + p_w * (r_jc + r_ch + r_ha)


def foster_step(p_w: float, r_list, tau_list, t_s):
    """Temperature rise of a Foster network for a power step at t = 0:
    sum R_i (1 - exp(-t / tau_i))."""
    t = np.asarray(t_s, dtype=float)
    return p_w * sum(r * (1 - np.exp(-t / tau))
                     for r, tau in zip(r_list, tau_list))


def foster_sim(p_series, dt_s: float, r_list, tau_list):
    """Temperature rise under an arbitrary power series (exact discrete update
    of each first-order Foster element)."""
    p = np.asarray(p_series, dtype=float)
    states = np.zeros(len(r_list))
    a = np.array([math.exp(-dt_s / tau) for tau in tau_list])
    r = np.array(r_list, dtype=float)
    out = np.empty(len(p))
    for k, pk in enumerate(p):
        states = a * states + (1 - a) * r * pk
        out[k] = states.sum()
    return out


def relative_cycle_life(delta_t_k: float, ref_delta_t_k: float,
                        exponent: float = 5.0) -> float:
    """Cycles to failure relative to a reference swing, N ~ dT^-n (a
    teaching power law; real constants come from the module maker)."""
    return (ref_delta_t_k / delta_t_k) ** exponent


# -------------------------------------------------------------- efficiency
def fit_loss_coeffs(points) -> tuple[float, float, float]:
    """Fit P_loss = c0 + c1 P + c2 P^2 (per unit of rated power) through
    (load_pu, efficiency) points by least squares."""
    pts = [(float(p), float(e)) for p, e in points]
    a = np.array([[1.0, p, p * p] for p, _ in pts])
    y = np.array([p * (1 / e - 1) for p, e in pts])          # loss per unit
    c, *_ = np.linalg.lstsq(a, y, rcond=None)
    return float(c[0]), float(c[1]), float(c[2])


def efficiency_from_coeffs(p_pu, c: tuple[float, float, float]):
    """Efficiency P / (P + loss) at per-unit output power(s)."""
    p = np.asarray(p_pu, dtype=float)
    loss = c[0] + c[1] * p + c[2] * p * p
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(p > 0, p / (p + loss), 0.0)


EURO_WEIGHTS = {0.05: 0.03, 0.10: 0.06, 0.20: 0.13, 0.30: 0.10,
                0.50: 0.48, 1.00: 0.20}
CEC_WEIGHTS = {0.10: 0.04, 0.20: 0.05, 0.30: 0.12, 0.50: 0.21,
               0.75: 0.53, 1.00: 0.05}


def weighted_efficiency(c: tuple[float, float, float], weights: dict) -> float:
    """Weighted efficiency for a set of (load point: weight) pairs."""
    return float(sum(w * efficiency_from_coeffs(p, c)
                     for p, w in weights.items()))


def derating(t_amb_c, altitude_m: float = 0.0, t_knee_c: float = 40.0,
             slope_per_k: float = 0.02, alt_knee_m: float = 1000.0,
             alt_slope_per_100m: float = 0.01, floor: float = 0.0):
    """Available output (per unit) under a teaching derating curve: full
    output up to the temperature knee, then a linear fall; a further linear
    fall above the altitude knee. Real curves come from the data sheet."""
    t = np.asarray(t_amb_c, dtype=float)
    k_t = np.clip(1 - slope_per_k * np.maximum(t - t_knee_c, 0.0), floor, 1.0)
    k_a = 1 - alt_slope_per_100m * max(altitude_m - alt_knee_m, 0.0) / 100
    return k_t * max(k_a, floor)


# ----------------------------------------------------------------- filters
def lcl_resonance(l1_h: float, l2_h: float, c_f: float) -> float:
    """Resonant frequency of an LCL filter (Hz):
    sqrt((L1 + L2) / (L1 L2 C)) / 2 pi."""
    return math.sqrt((l1_h + l2_h) / (l1_h * l2_h * c_f)) / (2 * math.pi)


def lcl_gain(f_hz, l1_h: float, l2_h: float, c_f: float, r_d: float = 0.0):
    """|I_grid / V_inverter| (siemens) of an LCL filter with a damping
    resistor in series with the capacitor, grid side short-circuited."""
    s = 2j * np.pi * np.asarray(f_hz, dtype=float)
    zc = r_d + 1 / (s * c_f)
    z2 = s * l2_h
    z_in = s * l1_h + zc * z2 / (zc + z2)
    return np.abs(zc / (zc + z2) / z_in)


def l_for_ripple(v_dc: float, f_sw: float, ripple_a: float) -> float:
    """Converter-side inductance that limits the peak-to-peak switching ripple
    of a three-wire two-level bridge to `ripple_a`, from the first-order
    rule V_dc / (8 L f_sw); a switched simulation gives 0.13 to 0.14
    V_dc / (L f_sw) near m = 0.9 to 1, so keep a margin."""
    return v_dc / (8 * f_sw * ripple_a)


# ----------------------------------------------------------------- DC link
def dclink_c_for_holdup(p_w: float, t_s: float, v1: float, v2: float) -> float:
    """Capacitance that supplies P for t while the voltage falls v1 -> v2."""
    return 2 * p_w * t_s / (v1 ** 2 - v2 ** 2)


def dclink_ripple_current_rms(i_ac_rms: float, m: float,
                              cos_phi: float) -> float:
    """RMS ripple current in the DC-link capacitor of a two-level three-phase
    inverter with sinusoidal PWM, phase current I (RMS), modulation index m:
    I_C = I sqrt(2 m [sqrt3/(4 pi) + cos^2 phi (sqrt3/pi - 9 m / 16)])."""
    x = 2 * m * (S3 / (4 * math.pi)
                 + cos_phi ** 2 * (S3 / math.pi - 9 * m / 16))
    return i_ac_rms * math.sqrt(x)


def dclink_ripple_current_numeric(m: float, phi_deg: float,
                                  f_sw_ratio: int = 99,
                                  n: int = 200000) -> float:
    """Time-domain check of the closed form: DC-link current of a naturally
    sampled two-level inverter (unit RMS phase current) minus its mean, RMS."""
    t = np.arange(n) / n
    th = 2 * np.pi * t
    x = (f_sw_ratio * t) % 1.0
    tri = np.where(x < 0.5, 4 * x - 1, 3 - 4 * x)
    i_dc = np.zeros(n)
    for k in range(3):
        ang = th - 2 * np.pi * k / 3
        s = (m * np.sin(ang) > tri).astype(float)
        i_dc += s * S2 * np.sin(ang - math.radians(phi_deg))
    return float(np.sqrt(np.mean((i_dc - i_dc.mean()) ** 2)))


# ------------------------------------------------------- fault ride-through
def frt_currents(v_pu: float, k: float = 2.0, i_max: float = 1.1,
                 i_p_pre: float = 1.0,
                 deadband: float = 0.1) -> tuple[float, float]:
    """Reactive current injection during a voltage dip: I_q = k (1 - V) above
    a dead band, capped by the current limit; active current gets what is
    left. Values per unit of rated current; the real k, dead band and
    priority are set by the grid code (chapters 17 and 28)."""
    i_q = min(i_max, k * (1.0 - v_pu)) if v_pu < 1.0 - deadband else 0.0
    i_p = min(i_p_pre, math.sqrt(max(0.0, i_max ** 2 - i_q ** 2)))
    return i_q, i_p


# --------------------------------------------------------- component checks
def overshoot_v(l_stray_h: float, di_dt_a_per_s: float) -> float:
    """Turn-off voltage overshoot L di/dt across the stray inductance."""
    return l_stray_h * di_dt_a_per_s


def gate_drive_power(q_g_c: float, dv_gate: float, f_sw: float) -> float:
    """Gate-driver power Q_g dV f per switch."""
    return q_g_c * dv_gate * f_sw


def deadtime_error(v_dc: float, t_dead_s: float, f_sw: float) -> float:
    """Mean output-voltage error caused by dead time: V_dc t_d f_sw."""
    return v_dc * t_dead_s * f_sw


def capacitor_energy_j(c_f: float, v: float) -> float:
    return 0.5 * c_f * v * v
