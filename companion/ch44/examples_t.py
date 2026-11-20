"""Chapter 44, round t: busbar inductance from assembly and the switching
overshoot against the derating rule, thermography of bare copper, how long
the full-power run must last, the length of a fingerprint, a canonical form
for parameters, two-wire and four-wire bonding checks, the cabinet's
anti-condensation heater, and thermal-cycling qualification of boards.

Run from the project root:   python -m companion.ch44.examples_t
Writes companion/ch44/expected/t_*.txt.
Teaching values (A-466 to A-472); no process recipes, no test voltages.
"""
from __future__ import annotations

import json
import math

import numpy as np

from companion.ch44.common import emit
from plantp import convmfg as cm
from plantp import pe

SIGMA = 5.670e-8


# ------------------------------------------------ 1. busbar loop and overshoot
def overshoot(seed: int = 4404, n: int = 960, di_dt: float = 5e9,
              v_block: float = 650.0, rating: float = 1200.0, rule: float = 0.80):
    """Loop = fixed part + busbar part proportional to layer spacing."""
    rng = np.random.default_rng(seed)
    l_fixed, l_bus0, d0 = 35e-9, 25e-9, 1.0              # H, H, mm (teaching)
    d = np.clip(rng.normal(d0, 0.12, n), 0.6, None)
    l_loop = l_fixed + l_bus0 * d / d0
    l_loop[[17, 503]] += 15e-9                           # spacer left out twice
    v = v_block + pe.overshoot_v(l_loop, di_dt)
    ratio = v / rating
    over = int((ratio > rule).sum())
    l_cross = (rule * rating - v_block) / di_dt
    d_cross = (l_cross - l_fixed) / l_bus0 * d0
    spacer_over = int((ratio[[17, 503]] > rule).sum())
    lines = [f"turn-off overshoot of {n} outer switches, di/dt {di_dt / 1e9:.0f} "
             f"kA/us, {v_block:.0f} V blocked",
             f"  loop = {l_fixed * 1e9:.0f} nH fixed + {l_bus0 * 1e9:.0f} nH x "
             "layer spacing / 1 mm",
             "  (spacing sd 0.12 mm, teaching)",
             f"  designed loop {(l_fixed + l_bus0) * 1e9:.0f} nH: overshoot "
             f"{pe.overshoot_v(l_fixed + l_bus0, di_dt):.0f} V, device sees "
             f"{v_block + pe.overshoot_v(l_fixed + l_bus0, di_dt):.0f} V "
             f"(ratio {(v_block + pe.overshoot_v(l_fixed + l_bus0, di_dt)) / rating:.2f})",
             f"  spread: ratio mean {ratio.mean():.3f}, highest {ratio.max():.3f}",
             f"  switches over the {rule:.2f} rule: {over} of {n} "
             f"({over / n:.1%})",
             f"  the rule is crossed at a loop of {l_cross * 1e9:.0f} nH, a spacing "
             f"of {d_cross:.2f} mm:",
             "  the design sits so close to the rule that a quarter of the",
             f"  switches cross it; the {spacer_over} switches with a spacer left"
             " out",
             "  (+15 nH) are the highest. The IGBT sat on its rule (lesson",
             "  B): either the design gains margin (a tighter loop, slower",
             "  switching) or the spacing becomes a critical characteristic",
             "  with its own control"]
    emit("t_overshoot", lines)
    return dict(over=over, mean=float(ratio.mean()), max=float(ratio.max()))


# ------------------------------------------------ 2. thermography of copper
def apparent(t_c: float, eps: float, eps_set: float = 0.95,
             t_refl_c: float = 30.0) -> float:
    """Temperature a camera set to eps_set shows for a surface of eps."""
    t, tr = t_c + 273.15, t_refl_c + 273.15
    w = eps * t ** 4 + (1 - eps) * tr ** 4
    return ((w - (1 - eps_set) * tr ** 4) / eps_set) ** 0.25 - 273.15


def thermography() -> dict:
    rows = [("good joint, painted dot", 55.0, 0.90),
            ("good joint, bare copper", 55.0, 0.10),
            ("hot joint, bare copper", 90.0, 0.10),
            ("hot joint, oxidised copper", 90.0, 0.60),
            ("hot joint, painted dot", 90.0, 0.90)]
    lines = ["camera set to emissivity 0.95, surroundings 30 C (broadband "
             "teaching model)",
             "  surface                        true C   emissivity   camera C"]
    out = {}
    for name, t, eps in rows:
        a = apparent(t, eps)
        out[name] = a
        lines.append(f"  {name:30s} {t:6.0f}   {eps:10.2f}   {a:8.1f}")
    lines += ["  a hot joint on bare copper reads colder than a good joint",
              "  with a painted dot: shiny metal reflects its surroundings",
              "  and emits little - joints get an emissivity dot or tape at",
              "  assembly, so that the heat run's camera reads true"]
    emit("t_thermo", lines)
    return out


# ------------------------------------------------ 3. how long a heat run
def heatrun(tau_min: float = 12.0, d_bad: float = 11.9, sd_peer: float = 2.6,
            noise: float = 0.5) -> dict:
    """First-order rise; the bad module's excess and the peers' spread
    grow together, the sensor noise does not."""
    lines = [f"full-power run: junction rise with time constant {tau_min:.0f} "
             "min (teaching);",
             f"  bad module {d_bad} K above the peers' mean at steady state,",
             f"  peers' sd {sd_peer} K, sensor noise {noise} K",
             "  minutes   share of steady rise   bad module z   steady within"]
    out = {}
    for t in (2, 5, 10, 20, 30, 60):
        f = 1 - math.exp(-t / tau_min)
        z = d_bad * f / math.sqrt((sd_peer * f) ** 2 + noise ** 2)
        out[t] = (f, z)
        lines.append(f"  {t:7d}   {f:20.0%}   {z:12.1f}   "
                     f"{(1 - f) * 30.7:9.1f} K")
    t3 = -tau_min * math.log(1 - 1 / math.sqrt((d_bad / 3) ** 2 - sd_peer ** 2)
                             * noise) if d_bad / 3 > sd_peer else float("inf")
    t5 = 5 * tau_min
    lines += [f"  the bad module stands 3 sd out after {t3:.1f} min; the",
              f"  temperatures are steady (within 1 %) after about {t5:.0f} min",
              "  a peer comparison finds a bad print in minutes; limits on",
              "  the rise need the steady state; the rest of a long run",
              "  tests what changes slowly - seals, joints, the cooling",
              "  loop - not the print"]
    emit("t_heatrun", lines)
    return dict(t3=t3, t5=t5)


# ------------------------------------------------ 4. how long a fingerprint
def hashlength() -> dict:
    lines = ["chance that two different parameter sets share a fingerprint",
             "  (birthday bound n^2 / 2^(b+1))",
             "  hex digits   bits        n = 10       n = 10^4      n = 10^6"]
    out = {}
    for hexd in (4, 8, 16, 64):
        b = 4 * hexd
        row = [min(1.0, n ** 2 / 2 ** (b + 1)) for n in (10, 1e4, 1e6)]
        out[hexd] = row
        lines.append(f"  {hexd:10d}   {b:4d}   " +
                     "   ".join(f"{x:11.2e}" for x in row))
    lines += ["  16 hex digits (64 bits) are far more than any plant needs;",
              "  with 8 a shared fingerprint becomes likely beyond ~10^5 sets;",
              "  the fingerprint detects a change - it is not a signature:",
              "  it cannot tell who made the change (ch 36)"]
    emit("t_hash", lines)
    return out


# ------------------------------------------------ 5. canonical form
def canonical(config: dict, digits: int = 9) -> dict:
    """Numbers as text with a fixed number of significant digits."""
    def norm(x):
        if isinstance(x, bool) or not isinstance(x, (int, float)):
            return x
        return format(float(x), f".{digits}g")
    out = {}
    for k, x in config.items():
        seq = isinstance(x, (list, tuple))
        out[k] = [norm(v) for v in x] if seq else norm(x)
    return out


def canonical_lesson() -> dict:
    a = {"q_v_droop_pct": 4.0, "ramp_pct_s": 10.0, "f_trip_hz": [47.5, 51.5]}
    b = {"q_v_droop_pct": 4, "ramp_pct_s": 10, "f_trip_hz": (47.5, 51.5)}
    c = dict(a, q_v_droop_pct=4.0000000001)
    d = dict(a, q_v_droop_pct=4.01)
    raw = {k: cm.fingerprint(v) for k, v in (("a", a), ("b", b), ("c", c),
                                              ("d", d))}
    can = {k: cm.fingerprint(canonical(v)) for k, v in (("a", a), ("b", b),
                                                         ("c", c), ("d", d))}
    lines = ["the same settings written two ways, and two small changes",
             "  set                               raw fingerprint    canonical",
             f"  a  droop 4.0, ramp 10.0           {raw['a']}   {can['a']}",
             f"  b  droop 4, ramp 10 (integers)    {raw['b']}   {can['b']}",
             f"  c  droop 4.0000000001             {raw['c']}   {can['c']}",
             f"  d  droop 4.01                     {raw['d']}   {can['d']}",
             f"  raw: a and b differ ({raw['a'] != raw['b']}) though the "
             "settings are equal - a false alarm",
             f"  canonical (9 digits): a = b ({can['a'] == can['b']}), a = c "
             f"({can['a'] == can['c']}), a = d ({can['a'] == can['d']})",
             "  the canonical form fixes how numbers are written; its digits",
             "  must be finer than any setting the device can hold, or a",
             "  real change disappears - the form is part of the release",
             f"  (text of a: {json.dumps(canonical(a), sort_keys=True)[:44]}...)"]
    emit("t_canon", lines)
    return dict(raw_ab=raw["a"] == raw["b"], can_ab=can["a"] == can["b"],
                can_ac=can["a"] == can["c"], can_ad=can["a"] == can["d"])


# ------------------------------------------------ 6. bonding checks
BONDS = [0.020, 0.025, 0.030, 0.035, 0.040, 0.030, 0.045, 0.090, 0.120, 0.028]


def bonding(limit: float = 0.10, leads: float = 0.080, contact_sd: float = 0.015,
            seed: int = 4405) -> dict:
    rng = np.random.default_rng(seed)
    contact = rng.normal(0.0, contact_sd, len(BONDS))
    meth = {"two-wire, leads not nulled": [b + leads + abs(c) for b, c in
                                           zip(BONDS, contact)],
            "two-wire, leads nulled": [b + abs(c) for b, c in zip(BONDS, contact)],
            "four-wire": list(BONDS)}
    truth = [b <= limit for b in BONDS]
    lines = [f"protective bonding of ten points against a {limit} ohm teaching "
             "limit",
             f"  test leads {leads} ohm, probe contact sd {contact_sd} ohm",
             "  method                       false fails   false passes"]
    out = {}
    for name, reading in meth.items():
        ff = sum(1 for r, t in zip(reading, truth) if t and r > limit)
        fp = sum(1 for r, t in zip(reading, truth) if not t and r <= limit)
        out[name] = (ff, fp)
        lines.append(f"  {name:28s} {ff:11d}   {fp:12d}")
    lines += ["  unnulled leads fail good bonds and waste repairs; the probe",
              "  contact still adds to a two-wire reading; four wires measure",
              "  the bond alone - and the bad bond (0.120) fails in every",
              "  method: method error shows as false fails here, not as a",
              "  missed fault, because the error only adds"]
    emit("t_bond", lines)
    return out


# ------------------------------------------------ 7. anti-condensation heater
def p_sat(t_c: float) -> float:
    """Magnus approximation of saturation vapour pressure (hPa)."""
    return 6.112 * math.exp(17.62 * t_c / (243.12 + t_c))


def heater(area_m2: float = 30.0, u_w: float = 4.0, rh_out: float = 0.95,
           rh_max: float = 0.85) -> dict:
    ua = area_m2 * u_w
    lines = [f"cabinet {area_m2:.0f} m2 at {u_w} W/m2 K (UA {ua:.0f} W/K); "
             f"night air at {rh_out:.0%} RH;",
             f"  keep the inside below {rh_max:.0%} RH by warming it (teaching)",
             "  outside C   warming needed K   heater W"]
    out = {}
    for t in (-5.0, 5.0, 15.0, 25.0):
        lo, hi = 0.0, 20.0
        for _ in range(60):
            mid = (lo + hi) / 2
            if rh_out * p_sat(t) / p_sat(t + mid) > rh_max:
                lo = mid
            else:
                hi = mid
        out[t] = (hi, ua * hi)
        lines.append(f"  {t:10.0f}   {hi:17.2f}   {ua * hi:8.0f}")
    lines += ["  a few kelvin are enough at any temperature: the heater is",
              "  small, but it must run when the inverter is off at night -",
              "  on the auxiliary supply, with its own alarm, and tested at",
              "  the end of the line like any other item of the tree"]
    emit("t_heater", lines)
    return out


# ------------------------------------------------ 8. thermal-cycling qualification
def cycling(dt_field: float = 20.0, dt_test: float = 100.0, field_cycles: float = 9125,
            r: float = 0.90, conf: float = 0.90, beta: float = 2.0) -> dict:
    expo = -1 / -0.442                                   # Coffin-Manson (lesson B)
    af = (dt_test / dt_field) ** expo
    eq = field_cycles / af
    lines = [f"board qualification by thermal cycling: field {dt_field:.0f} K a "
             f"day for {field_cycles:,.0f} cycles,",
             f"  test {dt_test:.0f} K; acceleration (dT ratio)^{expo:.2f} = "
             f"{af:.1f};",
             f"  one field life = {eq:.0f} test cycles",
             f"  zero-failure demonstration of R {r:.0%} at {conf:.0%} "
             f"confidence, Weibull shape {beta}:",
             "  test length (field lives)   boards   test cycles   board-cycles"]
    out = {}
    for k in (1.0, 1.5, 2.0, 3.0):
        n = math.ceil(math.log(1 - conf) / (k ** beta * math.log(r)))
        out[k] = n
        lines.append(f"  {k:26.1f}   {n:6d}   {k * eq:11.0f}   {n * k * eq:12.0f}")
    lines += ["  testing longer needs fewer boards (the shape makes late",
              "  failures likelier); the acceleration rests on the fatigue",
              "  law holding at the test swing - the maker's test plan and",
              "  failure analysis are the evidence, not this arithmetic"]
    emit("t_cycling", lines)
    return dict(af=af, eq=eq, boards=out)


if __name__ == "__main__":
    overshoot()
    thermography()
    heatrun()
    hashlength()
    canonical_lesson()
    bonding()
    heater()
    cycling()
