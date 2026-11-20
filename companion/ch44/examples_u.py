"""Chapter 44, round u: integration lessons - DC injection from current-
sensor offsets, the Q(V) check at the factory and the signatures of two
errors, hold-up of the auxiliary supply against a voltage dip, running on
with failed fans, how well the factory can prove an efficiency claim, the
timing of the desaturation protection as a tolerance stack-up, the
parameter set as left on site, and the value of a pre-tested spare stack.

Run from the project root:   python -m companion.ch44.examples_u
Writes companion/ch44/expected/u_*.txt.
Teaching values (A-466 to A-473); nothing here is a test procedure.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch44 import sources as src
from companion.ch44.common import emit
from plantp import convmfg as cm
from plantp import pe

S, I = src.STACKUP, src.INVERTER
I_RATED = I["s_mva"] * 1e6 / (math.sqrt(3) * I["v_ll"])     # A rms
R_PATH = S["r_jc"] + cm.tim_r(S["tim_um"], S["tim_k"], S["tim_area_cm2"]) + S["r_hs"]


# ------------------------------------------------ 1. DC injection from offsets
def dc_offset(seed: int = 4406, n: int = 30000, sensor_range: float = 3000.0,
              limit_pct: float = 0.5) -> dict:
    """The current loop removes the DC it measures: a sensor offset becomes
    a real DC current of the opposite sign. Four stacks add per phase."""
    rng = np.random.default_rng(seed)
    out = {}
    lines = ["DC current into the unit transformer from current-sensor offsets "
             "(teaching):",
             f"  sensor range +-{sensor_range:.0f} A, four stacks a phase, "
             f"rated {I_RATED:,.0f} A rms,",
             f"  limit {limit_pct}% of rated",
             "  offset sd (% of range)   DC sd A   DC sd % rated   phases over"]
    for sd_pct in (0.05, 0.1, 0.3, 0.5):
        dc = rng.normal(0.0, sd_pct / 100 * sensor_range, (n, 4)).sum(axis=1)
        rel = np.abs(dc) / I_RATED * 100
        over = float((rel > limit_pct).mean())
        out[sd_pct] = (float(dc.std()), over)
        lines.append(f"  {sd_pct:22.2f}   {dc.std():7.1f}   {dc.std() / I_RATED:13.2%}"
                     f"   {over:11.2%}")
    lines += ["  an offset of a few amperes in a 3,000 A sensor looks small,",
              "  but the transformer sees it as DC (ch 43: half a percent is",
              "  2.7 x its magnetising ampere-turns) - offsets are trimmed",
              "  and checked at the end of the line, and the limit is",
              "  verified once by type test with its sensors"]
    emit("u_dc", lines)
    return out


# ------------------------------------------------ 2. Q(V) at the factory
def qv(v_pu, droop: float = 0.04, v_gain: float = 1.0) -> float:
    """Reactive power share for a voltage (teaching Q(V), no deadband)."""
    return float(np.clip(-(v_pu * v_gain - 1.0) / droop * 0.5, -1.0, 1.0)) + 0.0


def qv_fat(tol: float = 0.05) -> dict:
    pts = [0.94, 0.97, 1.00, 1.03, 1.06]
    cases = {"as released (droop 4 %)": dict(),
             "droop set to 5 %": dict(droop=0.05),
             "voltage reading +1 % (VT ratio)": dict(v_gain=1.01)}
    lines = [f"Q(V) check at five test voltages; tolerance +-{tol:.0%} of Q max",
             "  (teaching curve: Q/Qmax = -(V-1)/(2 droop))",
             "  case                             "
             + "  ".join(f"{v:5.2f}" for v in pts) + "   fails"]
    out = {}
    for name, kw in cases.items():
        got = [qv(v, **kw) for v in pts]
        want = [qv(v) for v in pts]
        bad = [v for v, g, w in zip(pts, got, want) if abs(g - w) > tol]
        out[name] = bad
        lines.append(f"  {name:32s} " + "  ".join(f"{g:+5.2f}" for g in got)
                     + f"   {len(bad)}")
    lines += ["  a wrong droop changes the slope: every point but 1.00 pu",
              "  fails; a wrong voltage reading shifts the curve: every point",
              "  fails, 1.00 pu included - a check at 1.00 pu alone finds the",
              "  shift and misses the slope: the points must span the curve,",
              "  and the fingerprint (lesson C) and the functional test find",
              "  different faults"]
    emit("u_qv", lines)
    return out


# ------------------------------------------------ 3. hold-up of the auxiliary supply
def holdup(c_f: float = 1.5e-3, v1: float = 380.0, v2: float = 250.0,
           p_w: float = 600.0, need_ms: float = 150.0) -> dict:
    t = c_f * (v1 ** 2 - v2 ** 2) / (2 * p_w)
    c_need = pe.dclink_c_for_holdup(p_w, need_ms / 1000, v1, v2)
    lines = [f"auxiliary supply of the control: bulk {c_f * 1e3:.1f} mF charged to "
             f"{v1:.0f} V,",
             f"  drops out at {v2:.0f} V, load {p_w:.0f} W (control, drivers, "
             "sensors; teaching)",
             f"  hold-up t = C (V1^2 - V2^2) / (2 P) = {t * 1000:.0f} ms",
             f"  needed: {need_ms:.0f} ms of a voltage dip ridden through "
             "(teaching, ch 26 and 28)",
             f"  bulk for {need_ms:.0f} ms: {c_need * 1e3:.2f} mF "
             f"({c_need / c_f:.1f} x), or the control fed from the 24 V UPS",
             f"  verdict: {'meets' if t * 1000 >= need_ms else 'falls short by'}"
             f" {abs(need_ms - t * 1000):.0f} ms - the inverter would ride",
             "  through the dip in its power stage and lose its control:",
             "  the missing end-of-line test was hiding a design question"]
    emit("u_holdup", lines)
    return dict(t_ms=t * 1000, c_need=c_need)


# ------------------------------------------------ 4. failed fans
def fans(q_kw: float = 84.0, ua_kw_k: float = 8.4, n_fans: int = 4,
         expo: float = 0.6, limit_c: float = 90.0) -> dict:
    """Heat exchanger UA ~ airflow^0.6; coolant inlet = air + Q/UA."""
    lines = [f"inverter heat {q_kw:.0f} kW to air through a heat exchanger, "
             f"{n_fans} fans;",
             f"  UA {ua_kw_k} kW/K with all fans",
             "  (UA ~ airflow^0.6, teaching); hottest module Tj = inlet + "
             f"{S['p_module_w']:.0f} W x {R_PATH:.4f} K/W",
             "  fans   air C   UA kW/K   coolant in C   Tj C   margin K"]
    out = {}
    for working in (4, 3, 2):
        ua = ua_kw_k * (working / n_fans) ** expo
        for t_air in (35.0, 45.0):
            t_in = t_air + q_kw / ua
            t_j = t_in + S["p_module_w"] * R_PATH
            out[(working, t_air)] = t_j
            lines.append(f"  {working:4d}   {t_air:5.0f}   {ua:7.2f}   {t_in:12.1f}"
                         f"   {t_j:4.1f}   {limit_c - t_j:8.1f}")
    lines += [f"  with all fans the coolant reaches {35 + q_kw / ua_kw_k:.0f} C at "
              "35 C air - the 45 C",
              "  of the design is a cool-day value; on a 45 C day one failed",
              "  fan leaves a few kelvin, two leave almost none: N+1 fans,",
              "  a fan alarm and derating by temperature (ch 9) belong",
              "  together, and the heat run is judged at the hottest air"]
    emit("u_fans", lines)
    return out


# ------------------------------------------------ 5. proving efficiency
def efficiency_evidence(p_mw: float = 5.0, loss_kw: float = 83.8,
                        u_meter: float = 0.001, u_supply: float = 0.005,
                        split: float = 0.03) -> dict:
    u_direct = math.sqrt(2) * u_meter * p_mw * 1000          # kW
    pair = 2 * loss_kw
    u_b2b = math.sqrt((u_supply * pair / 2) ** 2 + (split * loss_kw) ** 2)
    lines = [f"evidence for the loss of one inverter at {p_mw:.0f} MW (ch 9: "
             f"{loss_kw} kW)",
             f"  direct: input and output meters at {u_meter:.1%} each",
             f"    loss = P_in - P_out: +-{u_direct:.1f} kW "
             f"({u_direct / loss_kw:.0%} of the loss)",
             f"  back-to-back: the grid supplies only the pair's loss "
             f"({pair:.0f} kW) at {u_supply:.1%};",
             f"    split by assumption, unit-to-unit difference +-{split:.0%}: "
             f"+-{u_b2b:.1f} kW ({u_b2b / loss_kw:.1%})",
             "  a direct measurement cannot prove a loss guarantee to better",
             "  than about a tenth; the back-to-back bench can, because it",
             "  measures the small number directly; pairing each unit with",
             "  two partners (three units, three runs, three sums) removes",
             "  the split assumption (ch 42 did the same for gearboxes)"]
    emit("u_eff", lines)
    return dict(direct=u_direct, b2b=u_b2b)


# ------------------------------------------------ 6. desaturation timing
DESAT = [   # stage, nominal us, relative tolerance (+-, uniform)
    ("blanking time (RC)", 3.0, 0.15),
    ("comparator and logic", 0.3, 0.33),
    ("driver propagation", 0.5, 0.20),
    ("soft turn-off", 2.0, 0.20),
]


def desat(withstand_us: float = 10.0, hot_us: float = 8.0, n: int = 200000,
          seed: int = 4407) -> dict:
    rng = np.random.default_rng(seed)
    nom = sum(t for _, t, _ in DESAT)
    worst = sum(t * (1 + r) for _, t, r in DESAT)
    rss = nom + math.sqrt(sum((t * r) ** 2 for _, t, r in DESAT))
    mc = sum(t * (1 + rng.uniform(-r, r, n)) for _, t, r in DESAT)
    p999 = float(np.percentile(mc, 99.9))
    lines = ["short-circuit protection chain of a gate driver (teaching values)",
             "  stage                       nominal us   tolerance"]
    for name, t, r in DESAT:
        lines.append(f"  {name:27s} {t:10.1f}   +-{r:.0%}")
    lines += [f"  total: nominal {nom:.1f} us, worst case {worst:.2f}, nominal + "
              f"RSS {rss:.2f},",
              f"    Monte Carlo 99.9 % {p999:.2f}",
              f"  device withstand {withstand_us:.0f} us cold, {hot_us:.0f} us hot "
              "(teaching): margin hot",
              f"    worst case {hot_us - worst:.2f} us, 99.9 % {hot_us - p999:.2f} us",
              "  the arithmetic worst case still fits the hot withstand; the",
              "  blanking capacitor's tolerance is the largest term, so it",
              "  is a critical characteristic of the driver board - and the",
              "  maker's short-circuit type test is the evidence"]
    emit("u_desat", lines)
    return dict(nom=nom, worst=worst, rss=rss, p999=p999)


# ------------------------------------------------ 7. the set as left on site
def as_left() -> dict:
    released = dict(src.BASE_CONFIG)
    authorised = dict(released, q_v_droop_pct=5.0, ramp_pct_s=8.0)
    as_left = dict(authorised, island_detect="off")
    fps = {k: cm.fingerprint(v) for k, v in (("released", released),
                                              ("authorised", authorised),
                                              ("as left", as_left))}
    diff = [k for k in authorised if authorised[k] != as_left[k]]
    lines = ["one inverter's parameter set from the factory to the end of",
             "  commissioning (teaching)",
             f"  released at the factory      {fps['released']}",
             f"  authorised site changes      {fps['authorised']}",
             "    (droop 4 -> 5 %, ramp 10 -> 8 %/s)",
             f"  read back after commissioning {fps['as left']}",
             f"  as left vs authorised: {', '.join(diff)} = "
             f"{', '.join(str(as_left[k]) for k in diff)}",
             "  two changes were asked for by the grid operator and signed;",
             "  the third was left over from an islanding test - the record",
             "  compares the read-back with the authorised set, not with",
             "  the factory set, which no longer applies (ch 50)"]
    emit("u_asleft", lines)
    return dict(diff=diff, same=fps["as left"] == fps["authorised"])


# ------------------------------------------------ 8. a spare stack
def spare_stack(fails_yr: float = 0.84, mttr_h: float = 72.0, swap_h: float = 8.0,
                p_avg_mw: float = 1.25, price: float = 70.0, rate: float = 0.06,
                years: int = 25) -> dict:
    tree = {r[0]: r for r in src.TREE}
    stack_cost = sum(tree[k][3] * tree[k][5] for k in ("MOD", "GDB", "DCL", "BUS",
                                                       "CLP"))
    mwh = fails_yr * (mttr_h - swap_h) * p_avg_mw
    value = mwh * price / 1000                               # k u a year
    annuity = (1 - (1 + rate) ** -years) / rate
    npv = value * annuity - stack_cost
    lines = [f"a pre-tested spare stack with quick couplings: module repairs "
             f"{mttr_h:.0f} h -> {swap_h:.0f} h",
             f"  module failures in the fleet {fails_yr} a year (lesson A), "
             f"{p_avg_mw} MW lost while down",
             f"  energy kept: {mwh:.0f} MWh a year = {value:.1f} k u at "
             f"{price:.0f} u/MWh",
             f"  stack cost (modules, drivers, capacitors, busbar, plate): "
             f"{stack_cost:.1f} k u",
             f"  simple payback {stack_cost / value:.1f} years; value over "
             f"{years} years at {rate:.0%}: {npv:+.1f} k u",
             "  only module failures counted - a stack swap also shortens",
             "  driver and capacitor repairs; serviceability is designed in",
             "  (stack on rails, couplings that close dry), then proven by a",
             "  timed swap at the factory"]
    emit("u_stack", lines)
    return dict(mwh=mwh, cost=stack_cost, payback=stack_cost / value, npv=npv)


if __name__ == "__main__":
    dc_offset()
    qv_fat()
    holdup()
    fans()
    efficiency_evidence()
    desat()
    as_left()
    spare_stack()
