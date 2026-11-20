"""Electrical machines (chapter 8): speeds, the induction-machine equivalent
circuit, the synchronous machine, DFIG slip power, losses and efficiency,
thermal and insulation-life rules, balancing and bearing frequencies.

Conventions: SI units; per-phase (star) quantities with RMS values; motor
convention for the induction machine (positive slip = motor, negative slip
= generator); angles in radians unless a name says _deg.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

R_GAS = 8.314462618        # J/(mol K)


# ------------------------------------------------------------------ speeds
def sync_speed_rpm(f_hz: float, poles: int) -> float:
    """Synchronous speed n_s = 120 f / p (p = number of poles)."""
    if poles <= 0 or poles % 2:
        raise ValueError("poles must be a positive even number")
    return 120.0 * f_hz / poles


def electrical_freq_hz(n_rpm: float, poles: int) -> float:
    """Frequency of a synchronous machine turning at n_rpm."""
    return n_rpm * poles / 120.0


def slip(n_sync_rpm: float, n_rpm: float) -> float:
    """s = (n_s - n) / n_s; s < 0 means generating (above synchronous)."""
    return (n_sync_rpm - n_rpm) / n_sync_rpm


def torque_nm(p_w: float, n_rpm: float) -> float:
    """Shaft torque T = P / omega."""
    return p_w / (2 * math.pi * n_rpm / 60.0)


def rotor_volume_m3(torque: float, shear_pa: float) -> float:
    """Air-gap rotor volume pi D^2 L / 4 from T = 2 sigma V_r."""
    return torque / (2.0 * shear_pa)


def emf_rms(f_hz: float, turns: float, flux_wb: float, k_w: float = 1.0) -> float:
    """E = 4.44 f N Phi k_w (RMS, per phase)."""
    return 4.44 * f_hz * turns * flux_wb * k_w


# --------------------------------------------------------- induction machine
@dataclass
class InductionMachine:
    """Per-phase equivalent circuit (T form), star values, RMS phase voltage."""
    v_ph: float
    f_hz: float
    poles: int
    r1: float
    x1: float
    xm: float
    r2: float
    x2: float
    p_mech_loss_w: float = 0.0      # friction and windage, taken as constant

    @property
    def n_sync(self) -> float:
        return sync_speed_rpm(self.f_hz, self.poles)

    def operate(self, s: float) -> dict:
        """Currents, powers, torque and pf at slip s (s != 0)."""
        if s == 0:
            raise ValueError("slip must not be zero")
        z2 = complex(self.r2 / s, self.x2)
        zm = complex(0.0, self.xm)
        z_par = zm * z2 / (zm + z2)
        z_in = complex(self.r1, self.x1) + z_par
        i1 = self.v_ph / z_in
        e = i1 * z_par
        i2 = e / z2
        p_ag = 3 * abs(i2) ** 2 * self.r2 / s            # air-gap power
        p_conv = p_ag * (1 - s)                          # converted to mechanical
        w_sync = 2 * math.pi * self.n_sync / 60
        s_in = 3 * self.v_ph * i1.conjugate()
        p_shaft = p_conv - self.p_mech_loss_w
        return {"i1": i1, "i2": i2, "p_in": s_in.real, "q_in": s_in.imag,
                "pf": s_in.real / abs(s_in), "p_ag": p_ag, "p_conv": p_conv,
                "p_shaft": p_shaft, "torque": p_ag / w_sync,
                "n_rpm": self.n_sync * (1 - s),
                "p_cu1": 3 * abs(i1) ** 2 * self.r1,
                "p_cu2": 3 * abs(i2) ** 2 * self.r2}

    def slip_for_shaft_power(self, p_shaft: float, lo=1e-5, hi=0.2) -> float:
        """Motor slip that gives the requested shaft power (bisection)."""
        for _ in range(100):
            mid = 0.5 * (lo + hi)
            if self.operate(mid)["p_shaft"] < p_shaft:
                lo = mid
            else:
                hi = mid
        return 0.5 * (lo + hi)


# -------------------------------------------------------- synchronous machine
def sm_emf(v_ph: complex, i: complex, xs: float, ra: float = 0.0) -> complex:
    """Internal EMF of a generator: E = V + (Ra + jXs) I (generator convention)."""
    return v_ph + complex(ra, xs) * i


def sm_power(e: float, v: float, xs: float, delta_rad: float) -> float:
    """Per-phase active power E V sin(delta) / Xs (round rotor, Ra = 0)."""
    return e * v * math.sin(delta_rad) / xs


def sm_reactive(e: float, v: float, xs: float, delta_rad: float) -> float:
    """Per-phase reactive power delivered: (E V cos(delta) - V^2) / Xs."""
    return (e * v * math.cos(delta_rad) - v * v) / xs


# --------------------------------------------------------------------- DFIG
def dfig_rotor_power(p_mech: float, s: float) -> float:
    """Slip power through the rotor converter (lossless): P_stator =
    P_mech / (1 - s), P_rotor = -s P_stator (s < 0: rotor feeds the grid)."""
    return -s * p_mech / (1 - s)


# ------------------------------------------------------------ losses, heat
def loss_model(load_pu: float, p_rated: float, eta_rated: float,
               fixed_share: float = 0.35) -> float:
    """Losses at a load (per unit of rating): fixed part (core, friction,
    windage) plus a part growing with load squared (copper, stray). The two
    parts add up to the rated losses; fixed_share is their split at rating."""
    p_loss_r = p_rated * (1 / eta_rated - 1)
    return p_loss_r * (fixed_share + (1 - fixed_share) * load_pu ** 2)


def efficiency(load_pu: float, p_rated: float, eta_rated: float,
               fixed_share: float = 0.35) -> float:
    """Output / input at a load, from loss_model (output = load x rating)."""
    out = load_pu * p_rated
    if out <= 0:
        return 0.0
    return out / (out + loss_model(load_pu, p_rated, eta_rated, fixed_share))


def r_at_temperature(r_ref: float, t_ref: float, t: float,
                     k: float = 234.5) -> float:
    """Copper resistance at t (deg C) from r_ref at t_ref: (k + t)/(k + t_ref)."""
    return r_ref * (k + t) / (k + t_ref)


def temperature_from_resistance(r_cold: float, t_cold: float, r_hot: float,
                                k: float = 234.5) -> float:
    """Winding temperature by the resistance method."""
    return r_hot / r_cold * (k + t_cold) - k


def life_factor(t_c: float, t_ref_c: float, ea_j_mol: float) -> float:
    """Arrhenius ageing: life at t relative to life at t_ref."""
    t, t0 = t_c + 273.15, t_ref_c + 273.15
    return math.exp(ea_j_mol / R_GAS * (1 / t - 1 / t0))


# ------------------------------------------------------ mechanics, bearings
def residual_unbalance(mass_kg: float, grade_mm_s: float, n_rpm: float) -> dict:
    """Permissible specific unbalance e = G / omega and U = m e for a
    balance-quality grade G (mm/s); the grade itself comes from the standard."""
    w = 2 * math.pi * n_rpm / 60
    e_m = grade_mm_s / 1000 / w
    u = mass_kg * e_m
    return {"e_um": e_m * 1e6, "u_gmm": u * 1e6, "force_n": u * w * w}


def bearing_freqs(n_rpm: float, n_balls: int, d_ball: float, d_pitch: float,
                  contact_deg: float = 0.0) -> dict:
    """Kinematic defect frequencies of a rolling bearing (outer race fixed)."""
    fr = n_rpm / 60
    r = d_ball / d_pitch * math.cos(math.radians(contact_deg))
    return {"fr": fr,
            "bpfo": n_balls / 2 * fr * (1 - r),
            "bpfi": n_balls / 2 * fr * (1 + r),
            "bsf": d_pitch / (2 * d_ball) * fr * (1 - r * r),
            "ftf": fr / 2 * (1 - r)}


# ------------------------------------------------------- windings, cogging
def winding_factor(slots: int, poles: int, span: int, harmonic: int = 1) -> float:
    """Winding factor of a balanced double-layer three-phase winding by the
    star of slots: one coil starts in every slot (top side in slot k, return
    side in slot k + span); a coil belongs to the phase whose 60-degree belt
    holds the angle of its top side. Returns |sum of phase-A coil EMFs| over
    the arithmetic sum (2 per coil)."""
    pp = poles // 2
    if poles % 2 or (slots // math.gcd(slots, pp)) % 3:
        raise ValueError("not a balanced three-phase winding")
    total, count = 0j, 0
    for k in range(slots):
        ang = (k * pp * 360.0 / slots) % 360.0
        belt = int(((ang + 30.0) % 360.0) // 60.0)   # 0 A+, 3 A-, others B, C
        if belt not in (0, 3):
            continue
        sign = 1 if belt == 0 else -1
        a1 = math.radians(harmonic * k * pp * 360.0 / slots)
        a2 = math.radians(harmonic * (k + span) * pp * 360.0 / slots)
        total += sign * (complex(math.cos(a1), math.sin(a1))
                         - complex(math.cos(a2), math.sin(a2)))
        count += 1
    return abs(total) / (2 * count)


def cogging_periods(slots: int, poles: int) -> tuple[int, int]:
    """Cogging periods per revolution, lcm(Q, poles), and gcd(Q, poles): the
    larger the lcm (the smaller the gcd), the weaker the cogging, as a rule."""
    return math.lcm(slots, poles), math.gcd(slots, poles)


def skew_factor(skew_elec_deg: float, harmonic: int = 1) -> float:
    """EMF reduction by a skew of the given electrical angle."""
    x = math.radians(harmonic * skew_elec_deg) / 2
    return 1.0 if x == 0 else math.sin(x) / x
