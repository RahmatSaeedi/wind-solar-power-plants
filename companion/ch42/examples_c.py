"""Chapter 42, lesson C - drivetrain, nacelle and tower production at
textbook level: the back-to-back gearbox test, oil cleanliness and
filters, cooling against the hot day, generator insulation life over a
data-pack year, rotor balance against a grade, coupling alignment, gear
accuracy and mesh noise, a bedplate weld in fatigue, yaw brakes, the
insulation dryness index and serial traceability.

Run from the project root:   python -m companion.ch42.examples_c
Writes companion/ch42/expected/c_*.txt and diagrams/data/ch42-*.csv.
Teaching values (A-453, A-454); no test or work procedures.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch42 import sources as src
from companion.ch42.common import csv, emit
from companion.ch42.examples_a import drivetrain
from plantp import datapack
from plantp import structures as st
from plantp import turbinemfg as tm


# ------------------------------------------------ back-to-back test
def back_to_back(p_kw: float = 5000.0) -> dict[str, float]:
    out = {}
    lines = [f"two gearboxes back to back at {p_kw:.0f} kW: the grid supplies "
             "only the losses",
             "  gearbox efficiency   grid power kW   share of the test power"]
    for eta in (0.985, 0.980, 0.970):
        g = tm.back_to_back_power(p_kw, eta)
        out[eta] = g
        lines.append(f"  {eta:18.3f}   {g:13.0f}   {g / p_kw:24.1%}")
    lines += ["  the bench tests a pair at full torque for a fraction of the",
              "  power - and the measured grid power gives the pair's",
              "  efficiency, a check on the loss budget (lesson A); a run-in",
              "  at rising load with vibration and oil records follows",
              "  (lab D)"]
    emit("c_b2b", lines)
    return out


# ------------------------------------------------ oil cleanliness
def filters(ingress: float = 1.0) -> dict[float, float]:
    out = {}
    lines = ["gearbox oil: particles left when a filter of ratio beta runs in",
             "  the loop (relative to the beta 10 filter, same ingress)",
             "  beta    removed a pass   particles at balance (relative)"]
    base = None
    for beta in (10, 75, 200, 1000):
        r = tm.filter_removal(beta)
        level = ingress / r
        out[beta] = level
        base = base or level
        lines.append(f"  {beta:5d}   {r:14.1%}   {level / base:31.2f}")
    lines += ["  at balance, what enters equals what the filter takes out:",
              "  a finer filter changes the level only a little once it",
              "  removes most particles - keeping dirt out (seals,",
              "  breathers, clean filling at the factory) matters more;",
              "  the oil sample at the end of the run-in is a release record"]
    emit("c_filters", lines)
    return out


# ------------------------------------------------ cooling and hot days
def cooling(t_design: float = 35.0, t_limit: float = 65.0) -> dict[str, float]:
    d = drivetrain()
    q_gbx, q_gen = d["gearbox (3 stages)"], d["generator"]
    oil = q_gbx * 1000 / (1900 * 10.0)                 # kg/s, dT 10 K
    air = q_gen * 1000 / (1005 * 15.0)                 # kg/s, dT 15 K
    h = datapack.load_hourly()
    t = h["t_air_c"].to_numpy()
    hot = t > t_design
    cap = np.clip((t_limit - t) / (t_limit - t_design), 0, 1)
    lines = ["nacelle cooling at rated (heat from lesson A)",
             f"  gearbox {q_gbx:.0f} kW: oil {oil:.1f} kg/s for a 10 K rise "
             "(cp 1.9 kJ/kg K)",
             f"  generator {q_gen:.0f} kW: air {air:.1f} kg/s for a 15 K rise",
             f"  coolers sized for {t_design:.0f} C air; capacity falls with",
             f"  (T_limit - T_air), limit {t_limit:.0f} C",
             f"  hours above {t_design:.0f} C in the data-pack year: "
             f"{int(hot.sum())}; lowest capacity {cap.min():.0%}",
             "  on those hours the turbine derates unless the coolers are",
             "  sized for the site's 40.7 C - a purchase choice (hot-climate",
             "  package, lesson A) with its own price and energy value"]
    emit("c_cooling", lines)
    return dict(oil=oil, air=air, hot_h=int(hot.sum()), cap_min=float(cap.min()))


# ------------------------------------------------ insulation life
def insulation_life(t_ref: float = 120.0, life_ref_y: float = 20.0,
                    rise: float = 95.0, nacelle: float = 20.0) -> dict:
    h = datapack.load_hourly()
    v = h["ws_100m_ms"].to_numpy()
    t = h["t_air_c"].to_numpy()
    load = np.clip((v - 3.0) / (11.0 - 3.0), 0, 1) ** 3
    load[(v < 3) | (v > 25)] = 0.0
    hot_spot = t + nacelle + rise * load ** 2           # nacelle + winding
    use = np.sum(2.0 ** ((hot_spot - t_ref) / 10.0))     # hours at t_ref
    life = life_ref_y * 8760 / use
    edges = list(range(0, 141, 10))
    counts = [int(((hot_spot >= a) & (hot_spot < a + 10)).sum())
              for a in edges[:-1]]
    csv("ch42-hotspot.csv", "lo,hours", list(zip(edges[:-1], counts)))
    hot = hot_spot + 10.0
    life_hot = life_ref_y * 8760 / np.sum(2.0 ** ((hot - t_ref) / 10.0))
    lines = ["generator winding: hot spot over the data-pack year (teaching:",
             f"  air + {nacelle:.0f} K nacelle + {rise:.0f} K x load^2; designed for "
             f"{life_ref_y:.0f} years at {t_ref:.0f} C)",
             f"  hottest hour {hot_spot.max():.0f} C; hours above 120 C: "
             f"{int((hot_spot > 120).sum())}",
             f"  life used a year {use:,.0f} h-equivalent: insulation life "
             f"{life:.0f} years",
             f"  10 K hotter everywhere (a blocked filter): {life_hot:.0f} years",
             "  most hours run at part load, so the winding outlives its",
             "  design point; a cooling fault halves that life - margin",
             "  gone, not yet a failure: winding temperature sensors are a",
             "  factory-tested, monitored item"]
    emit("c_insulation", lines)
    return dict(life=life, life_hot=life_hot, max=float(hot_spot.max()))


# ------------------------------------------------ rotor balance
def balance(mass_kg: float = 4000.0, rpm: float = 1155.0,
            grade_mm_s: float = 2.5, measured_gmm: float = 145_000.0):
    w = rpm * 2 * math.pi / 60
    e_um = grade_mm_s / w * 1000
    u_perm = mass_kg * e_um / 1000 * 1000                # g mm
    lines = [f"generator rotor {mass_kg / 1000:.0f} t at {rpm:.0f} rpm "
             f"(teaching grade {grade_mm_s} mm/s)",
             f"  permissible eccentricity e = G / w = {e_um:.1f} um",
             f"  permissible residual unbalance {u_perm:,.0f} g mm "
             f"(two planes: {u_perm / 2:,.0f} each)",
             f"  measured after assembly {measured_gmm:,.0f} g mm: "
             f"{'accept' if measured_gmm <= u_perm else 'correct and re-run'}",
             "  the grade sets a target speed times eccentricity; a faster",
             "  rotor must be more exact - balance is corrected in the",
             "  factory, recorded, and checked again by the vibration of",
             "  the run-in (lab D)"]
    emit("c_balance", lines)
    return dict(e_um=e_um, u_perm=u_perm)


# ------------------------------------------------ coupling alignment
def alignment(offset: float = 0.30, angle: float = 0.12,
              front: float = 0.6, back: float = 1.8, tol: float = 0.05):
    f, b = tm.alignment_moves(offset, angle, front, back)
    lines = ["gearbox - generator coupling, laser readings (vertical, teaching)",
             f"  offset at the coupling {offset:+.2f} mm; angle {angle:+.2f} mm/m",
             f"  generator feet {front} m and {back} m from the coupling",
             f"  shims: front {f:+.2f} mm, back {b:+.2f} mm",
             f"  after the move both readings within +-{tol} (teaching)",
             "  misalignment shows as a strong 2x line in the run-in",
             "  spectrum (lab D, G09); the frame flexes on the tower, so",
             "  the coupling allows for it and the alignment is checked",
             "  again at the site after the nacelle is lifted"]
    emit("c_align", lines)
    return dict(front=f, back=b)


# ------------------------------------------------ gear accuracy, noise
def gear_noise(te_um: float = 3.0, step: float = 1.4):
    lines = ["gear accuracy grade and mesh noise (teaching: each finer grade",
             f"  divides the transmission error by {step})",
             "  grades finer   transmission error um   mesh level dB"]
    out = {}
    for k in range(0, 4):
        te = te_um / step ** k
        db = 20 * math.log10(te / te_um)
        out[k] = db
        lines.append(f"  {k:13d}   {te:22.2f}   {db:+13.1f}")
    lines += ["  about 3 dB less mesh tone for each finer grade: a tonal",
              "  noise limit at the village (ch 33) can become a gear",
              "  grinding requirement; the tone is checked on the bench"]
    emit("c_gears", lines)
    return out


# ------------------------------------------------ bedplate weld fatigue
def weld_fatigue(ds_del: float = 32.0, n_eq: float = 1e8):
    out = {}
    lines = [f"bedplate weld: damage-equivalent range {ds_del:.0f} MPa at "
             f"{n_eq:.0e} cycles (teaching)",
             "  detail category MPa   life cycles     damage in 20 years"]
    for cat in (71.0, 90.0, 112.0):
        n = st.sn_life(ds_del, cat)
        out[cat] = n_eq / n
        lines.append(f"  {cat:19.0f}   {n:11.2e}   {n_eq / n:18.2f}")
    lines += ["  the same load is unsafe on a rough weld and safe on a",
              "  ground one: the detail category is a manufacturing",
              "  outcome - weld profile, grinding and NDT records make it",
              "  true (ch 30, weld fatigue)"]
    emit("c_weld", lines)
    return out


# ------------------------------------------------ yaw brakes
def yaw_brakes(m_yaw_mnm: float = 6.0, clamp_kn: float = 300.0,
               mu: float = 0.40, r_m: float = 2.0, k: float = 1.5):
    per = 2 * mu * clamp_kn * 1e3 * r_m
    need = math.ceil(k * m_yaw_mnm * 1e6 / per)
    lines = [f"yaw brakes holding {m_yaw_mnm} MN m with margin {k} (teaching)",
             f"  one caliper: 2 faces x {mu} x {clamp_kn:.0f} kN at {r_m} m = "
             f"{per / 1e6:.2f} MN m",
             f"  calipers needed: {need}",
             "  friction falls with oil or glazing on the disc, so the",
             "  factory records the clamping test and the pads' burnishing;",
             "  in service the yaw drives also hold, and a slipping nacelle",
             "  is a safety event (ch 32)"]
    emit("c_yaw", lines)
    return dict(per=per, need=need)


# ------------------------------------------------ insulation dryness index
def pi_index(r1: float = 2.0, r10: float = 5.0, r1_wet: float = 0.8,
             r10_wet: float = 0.9):
    pi, pi_wet = r10 / r1, r10_wet / r1_wet
    lines = ["insulation resistance after 1 and 10 minutes (G ohm, teaching)",
             f"  dry winding: {r1} -> {r10}: index {pi:.1f}",
             f"  damp winding: {r1_wet} -> {r10_wet}: index {pi_wet:.2f}",
             "  a dry winding keeps polarising, so its resistance rises;",
             "  a damp one leaks, so it stays flat - the index catches",
             "  moisture picked up in transport or storage before the",
             "  machine is energised; the test is done by qualified",
             "  people under the maker's procedure, not from this book"]
    emit("c_pi", lines)
    return dict(pi=pi, pi_wet=pi_wet)


# ------------------------------------------------ serial traceability
def traceability(records_per_turbine: int = 4500, n_wtg: int = 12):
    lines = ["serial traceability of the turbine (teaching)",
             f"  about {records_per_turbine:,} records a turbine: serials, heat",
             "  numbers, inspection and test reports, torque records",
             f"  {records_per_turbine * n_wtg:,} records for the twelve turbines",
             "  a heat of bearing steel found weak: which turbines? only a",
             "  record that links heat > bearing > gearbox > turbine",
             "  answers in a day; the turbine's 'birth certificate' is",
             "  handed over with it (ch 49, ch 50)"]
    emit("c_trace", lines)


if __name__ == "__main__":
    back_to_back()
    filters()
    cooling()
    insulation_life()
    balance()
    alignment()
    gear_noise()
    weld_fatigue()
    yaw_brakes()
    pi_index()
    traceability()
