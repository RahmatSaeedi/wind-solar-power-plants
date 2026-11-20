"""Chapter 25 - transformers: the simplified design relations that show
the dependencies (volts per turn from Faraday's law, core section,
current density), the equivalent circuit from the no-load and
short-circuit tests, regulation, efficiency, the capitalised cost of
losses, a steady-state thermal model with the paper's ageing rate,
load sharing in parallel, short-circuit current and force scaling,
sound levels, and containment volume.

Teaching relations only: a transformer is designed by its maker's
software and checked by review and tests against the contract and the
applicable standards.
"""
from __future__ import annotations

import math

F_HZ = 50.0


# [start: faraday]
def volts_per_turn(b_peak: float, a_core_m2: float, f: float = F_HZ) -> float:
    """E/N = 4.44 f B A (sinusoidal flux)."""
    return 4.44 * f * b_peak * a_core_m2


def turns(v_phase: float, b_peak: float, a_core_m2: float,
          f: float = F_HZ) -> float:
    return v_phase / volts_per_turn(b_peak, a_core_m2, f)


def conductor_mm2(i: float, j_a_mm2: float) -> float:
    """Section for a current density j (A/mm2)."""
    return i / j_a_mm2
# [end: faraday]


# [start: tests]
def from_tests(s_kva: float, u_kv: float, p0_kw: float, i0_pct: float,
               pk_kw: float, uk_pct: float) -> dict:
    """Per-unit equivalent circuit from the no-load test (P0, I0) and the
    short-circuit test (Pk at rated current, uk): series r, x and the
    shunt magnetising branch, referred to the rated base."""
    r = pk_kw / s_kva
    z = uk_pct / 100
    x = math.sqrt(max(z ** 2 - r ** 2, 0.0))
    g = p0_kw / s_kva
    y = i0_pct / 100
    b = math.sqrt(max(y ** 2 - g ** 2, 0.0))
    return {"r": r, "x": x, "z": z, "g": g, "b": b}


def regulation_pct(r: float, x: float, load: float, pf: float) -> float:
    """Voltage regulation (%) at a per-unit load and power factor
    (lagging): u_r cos + u_x sin + (u_x cos - u_r sin)^2 / 200, with
    u_r and u_x in % at that load."""
    s = math.sin(math.acos(pf))
    ur, ux = 100 * r * load, 100 * x * load
    return ur * pf + ux * s + (ux * pf - ur * s) ** 2 / 200


def efficiency(load: float, s_kva: float, pf: float, p0_kw: float,
               pk_kw: float) -> float:
    out = load * s_kva * pf
    return out / (out + p0_kw + load ** 2 * pk_kw)
# [end: tests]


# [start: capitalise]
def loss_cost(p0_kw: float, pk_kw: float, a_per_kw: float,
              b_per_kw: float) -> float:
    """Capitalised cost of losses: A P0 + B Pk (k u when A, B are k u/kW)."""
    return a_per_kw * p0_kw + b_per_kw * pk_kw


def ab_factors(price: float, years: int, rate: float, load_loss_factor: float,
               hours: float = 8760.0) -> tuple[float, float]:
    """A (no-load) and B (load-loss) factors in k u per kW: energy price
    (u/MWh) over the years at the rate; B scaled by the loss load factor
    (mean of the square of the per-unit load)."""
    af = (1 - (1 + rate) ** -years) / rate
    a = price * hours / 1e6 * af
    return a, a * load_loss_factor
# [end: capitalise]


# [start: thermal]
def hot_spot(k: float, theta_a: float, d_top_r: float = 52.0,
             d_hs_r: float = 26.0,
             r_ratio: float = 6.0, x: float = 0.8, y: float = 1.6) -> float:
    """Steady hot-spot temperature at load factor k (teaching exponential
    model): top-oil rise d_top_r((1 + R k^2)/(1 + R))^x plus hot-spot
    gradient d_hs_r k^y above the ambient theta_a."""
    top = d_top_r * ((1 + r_ratio * k ** 2) / (1 + r_ratio)) ** x
    return theta_a + top + d_hs_r * k ** y


def ageing_rate(theta_hs: float, ref: float = 98.0,
                step: float = 6.0) -> float:
    """Relative ageing rate of the paper: doubles every `step` K above
    `ref` (teaching relation for non-upgraded paper)."""
    return 2 ** ((theta_hs - ref) / step)
# [end: thermal]


def share(loads_kva: float, ratings_kva, z_pu) -> list[float]:
    """Load each of several parallel transformers carries: in proportion
    to rating / impedance (same ratio and vector group)."""
    w = [s / z for s, z in zip(ratings_kva, z_pu)]
    tot = sum(w)
    return [loads_kva * x / tot for x in w]


def sc_current_ka(s_mva: float, u_kv: float, z_pu: float) -> float:
    """Short-circuit current through a transformer from an infinite bus."""
    return s_mva / (math.sqrt(3) * u_kv * z_pu)


def force_ratio(z_pu: float) -> float:
    """Short-circuit force relative to the force at rated current: F ~ I^2,
    so (1/z)^2 (peak factor aside)."""
    return (1 / z_pu) ** 2


def sound_sum(levels_db) -> float:
    return 10 * math.log10(sum(10 ** (l / 10) for l in levels_db))


def sound_at(l_ref: float, r_ref: float, r: float) -> float:
    """Free-field point source: -20 log10(r / r_ref)."""
    return l_ref - 20 * math.log10(r / r_ref)


def bund_m3(oil_m3: float, rain_mm: float, area_m2: float, margin: float = 1.1) -> float:
    """Containment volume: margin x oil plus a design rainfall on the
    open area (teaching; the authority and the fire design set the rule)."""
    return margin * oil_m3 + rain_mm / 1000 * area_m2
