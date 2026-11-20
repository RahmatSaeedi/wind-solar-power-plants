"""Chapter 44, lesson B: design for manufacture and reliability - the
thermal interface and what its faults do to the junction and to cycle
life, two parallel modules with part spread, DC-link capacitors sharing
ripple by ESR, solder joints on the control board, insulation distances
as a layout check, component stress derating, and a busbar joint that
loses its preload.

Run from the project root:   python -m companion.ch44.examples_b
Writes companion/ch44/expected/b_*.txt and diagrams/data/ch44-*.csv.
Teaching values (A-467, A-468); no process recipes.
"""
from __future__ import annotations

import math

from companion.ch44 import sources as src
from companion.ch44.common import csv, emit
from plantp import convmfg as cm
from plantp import pe

S, I = src.STACKUP, src.INVERTER


# ------------------------------------------------ thermal interface
def tim_states() -> dict[str, dict]:
    cases = {"as designed": (100.0, S["tim_k"], 0.0),
             "printed twice as thick": (200.0, S["tim_k"], 0.0),
             "40 % voids under the chips": (100.0, S["tim_k"], 0.4),
             "pumped out and dried": (150.0, 0.4, 0.2)}
    lines = [f"one IGBT module of the hottest position: {S['p_module_w']:.0f} W, "
             f"coolant {I['coolant_c']:.0f} C,",
             f"  R_jc {S['r_jc']} K/W, cold plate {S['r_hs']} K/W (ch 9: 0.060 in all)",
             f"  interface {S['tim_um']:.0f} um of k {S['tim_k']} W/m K over "
             f"{S['tim_area_cm2']:.0f} cm2 under the chips (teaching)",
             "  interface state                R_tim K/W   Tj C   daily swing K"
             "   cycle life"]
    out = {}
    base = None
    for name, (t_um, k, void) in cases.items():
        r = cm.tim_r(t_um, k, S["tim_area_cm2"], void)
        t_j = cm.tj(S["p_module_w"], S["r_jc"], r, S["r_hs"], I["coolant_c"])
        swing = t_j - I["coolant_c"]
        if base is None:
            base = swing
        life = pe.relative_cycle_life(swing, base)
        out[name] = dict(r=r, tj=t_j, swing=swing, life=life)
        lines.append(f"  {name:30s} {r:9.4f}   {t_j:4.0f}   {swing:13.1f}"
                     f"   {life:10.0%}")
    lines += ["  the interface is a thin layer, but a thick or dry one moves",
              "  the junction by many kelvin; power cycling life falls with",
              "  the fifth power of the swing (ch 9) - the print weight and",
              "  coverage at mounting are process controls, not details"]
    emit("b_tim", lines)
    return out


# ------------------------------------------------ parallel modules
def parallel(spread: float = 0.03, p_pos_w: float = 2 * S["p_module_w"]) -> dict:
    lines = ["two modules in parallel on one switch position: on-state spread",
             f"  share of the current by 1/r; conduction loss ~ share^2 (teaching)",
             "  spread    shares          hotter module loss   Tj rise above even"]
    out = {}
    r_th = S["r_jc"] + cm.tim_r(S["tim_um"], S["tim_k"], S["tim_area_cm2"]) + S["r_hs"]
    for sp in (0.0, spread, 2 * spread, 3 * spread):
        sh = cm.shares([1 - sp / 2, 1 + sp / 2])
        hot = max(sh)
        p_hot = p_pos_w / 2 * (hot / 0.5) ** 2
        rise = (p_hot - p_pos_w / 2) * r_th
        out[sp] = rise
        lines.append(f"  {sp:6.0%}    {sh[0]:.3f}/{sh[1]:.3f}     {p_hot:7.0f} W"
                     f"          {rise:5.1f} K")
    lines += ["  at high current the IGBT's on-state voltage rises with",
              "  temperature, so the hotter module takes a little less - but",
              "  the factory still pairs modules from one voltage class and",
              "  one lot: sharing is designed in, then built in"]
    emit("b_parallel", lines)
    return out


# ------------------------------------------------ capacitor ripple sharing
def caps(n: int = 12, esr_spread: float = 0.15, path_extra: float = 0.10,
         dt_rated: float = 10.0) -> dict[str, float]:
    esr = [1.0 + esr_spread * ((k % 4) - 1.5) / 1.5 for k in range(n)]
    esr = [e * (1 + path_extra * (k / (n - 1))) for k, e in enumerate(esr)]
    sh = cm.shares(esr)
    hot = max(sh) * n
    heat = hot ** 2 * esr[sh.index(max(sh))] / (sum(esr) / n)
    d_t = dt_rated * heat
    life = 2 ** (-(d_t - dt_rated) / 10)
    rows = [(k + 1, round(x * n, 3)) for k, x in enumerate(sh)]
    csv("ch44-caps.csv", "cap,share", rows)
    lines = [f"{n} film capacitors in parallel on one DC link: ESR spread "
             f"+-{esr_spread:.0%},",
             f"  busbar path up to {path_extra:.0%} longer",
             "  current share relative to an even split: "
             + ", ".join(f"{x * n:.2f}" for x in sh[:6]),
             "  " + " " * 41 + ", ".join(f"{x * n:.2f}" for x in sh[6:]),
             f"  hottest capacitor: {hot:.2f} x the even current, {heat:.2f} x the heat",
             f"  hot-spot rise {d_t:.1f} K instead of {dt_rated:.0f} K: life x {life:.2f}"
             " (10 K halves it, ch 9)",
             "  the capacitor nearest the switches works hardest: layout",
             "  equalises the paths, and incoming checks keep the ESR",
             "  spread inside the maker's class"]
    emit("b_caps", lines)
    return dict(hot=hot, heat=heat, life=life)


# ------------------------------------------------ solder joints
def solder(height_mm: float = 0.10, years: float = 25.0) -> dict[str, dict]:
    need = years * 365
    lines = ["solder joints on the control board, one thermal cycle a day",
             f"  ({need:,.0f} in {years:.0f} years)",
             "  part                       cycles at dT 20 K   at dT 40 K   verdict at 40"]
    out = {}
    for name, dnp, dcte in src.PARTS:
        n20 = cm.cycles_to_failure(cm.solder_strain(dnp, dcte, 20, height_mm))
        n40 = cm.cycles_to_failure(cm.solder_strain(dnp, dcte, 40, height_mm))
        out[name] = (n20, n40)
        lines.append(f"  {name:26s} {n20:17,.0f}   {n40:10,.0f}   "
                     f"{'ok' if n40 >= need else 'short'}")
    lines += ["  large, stiff parts far from their centre and boards that",
              "  swing many kelvin a day fail first: the layout keeps big",
              "  ceramics away from heat, and the cabinet's cooling keeps",
              "  the daily swing small (teaching constants; the maker's",
              "  qualification by thermal cycling is the evidence)"]
    emit("b_solder", lines)
    return out


# ------------------------------------------------ insulation distances
PAIRS = [   # net pair, working V, spacing mm, coated
    ("DC+ to DC- on the gate board", 1000.0, 9.0, False),
    ("gate drive to control (isolation)", 1000.0, 14.0, False),
    ("24 V to chassis", 24.0, 1.0, False),
    ("DC+ to heat sink", 1000.0, 6.0, True),
]


def creepage(mm_per_kv_pd2: float = 5.0, mm_per_kv_pd3: float = 12.5,
             pd: int = 3) -> dict[str, bool]:
    lines = [f"creepage along the board for the cabinet's pollution class {pd}",
             f"  (teaching mm per kV: {mm_per_kv_pd2} for class 2, {mm_per_kv_pd3} for "
             "class 3;",
             "  under a coating, treated as class 2)",
             "  net pair                               V     has mm   needs mm   ok"]
    out = {}
    for name, v, mm, coated in PAIRS:
        rate = mm_per_kv_pd2 if (coated or pd == 2) else mm_per_kv_pd3
        need = max(0.5, v / 1000 * rate)
        ok = mm >= need
        out[name] = ok
        lines.append(f"  {name:36s} {v:6.0f}  {mm:6.1f}   {need:7.1f}   "
                     f"{'yes' if ok else 'NO'}")
    lines += ["  dust and condensation in an outdoor cabinet make the board",
              "  surface a weaker insulator: the spacing is set for the",
              "  pollution the cabinet lets in, and a coating changes it;",
              "  real spacings come from the tables of the safety standards",
              "  (STD-050, STD-044), not from a rate per kV"]
    emit("b_creep", lines)
    return out


# ------------------------------------------------ derating check
def derate() -> list:
    res = cm.derating(src.DERATE, src.DERATE_RULES)
    lines = ["component stresses against the derating rules (teaching rules)",
             "  part                                          ratio   rule   ok"]
    for part, ratio, allowed, ok in res:
        lines.append(f"  {part:45s} {ratio:5.2f}   {allowed:4.2f}   {'yes' if ok else 'NO'}")
    bad = [r[0] for r in res if not r[3]]
    near = [r[0].split(",")[0] for r in res if r[3] and r[2] - r[1] < 0.015]
    lines += [f"  {len(bad)} parts over their rule: " + " and ".join(bad) + ";",
              f"  {len(near)} at their rule ({', '.join(near)}): design review",
              "  questions (a larger connector, capacitors rated for the",
              "  window's top, margin for the IGBT), answered before the",
              "  factory builds"]
    emit("b_derate", lines)
    return bad


# ------------------------------------------------ busbar joint
def joint(i_a: float = 1375.0, r0_uohm: float = 5.0) -> dict[float, float]:
    lines = [f"bolted busbar joint on the DC side of a stack, {i_a:.0f} A (teaching:",
             "  contact resistance ~ clamping force^-0.5)",
             "  preload left   contact uOhm   heat W"]
    out = {}
    for f in (1.0, 0.75, 0.5, 0.25):
        r = r0_uohm * f ** -0.5
        p = i_a ** 2 * r * 1e-6
        out[f] = p
        lines.append(f"  {f:12.0%}   {r:12.1f}   {p:6.1f}")
    lines += ["  a joint that loses its preload heats, oxidises and loses",
              "  more: torque marks and a torque record per joint at the",
              "  factory, thermography in the heat run (lesson C)"]
    emit("b_joint", lines)
    return out


if __name__ == "__main__":
    tim_states()
    parallel()
    caps()
    solder()
    creepage()
    derate()
    joint()
    _ = math
