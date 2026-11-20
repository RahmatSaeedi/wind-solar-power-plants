"""Chapter 43, a third round: burr and the stacking factor, lamination
thickness and eddy loss in the steel, the radial build of a disc winding,
how long a resistance reading takes to settle, the ratio bridge against
the tolerance, a rating limit priced on the data-pack year, and the
factory schedule as a network.

Run from the project root:   python -m companion.ch43.examples_t
Writes companion/ch43/expected/t_*.txt.
Teaching values (A-458, A-461, A-465).
"""
from __future__ import annotations

import math

from companion.ch43 import sources as src
from companion.ch43.common import emit
from companion.ch43.examples_a import geometry
from plantp import xfmrdesign as xd

M, D = src.MAIN_B, src.DESIGN


# ------------------------------------------------ burr and stacking factor
def burr(t_sheet_um: float = 270.0, coat_um: float = 2.0) -> dict[float, float]:
    g = geometry()
    st = src.STEELS[D["steel"]]
    a_gross = g["a_gross"]
    lines = [f"burr on the cut edges of {t_sheet_um:.0f} um sheets, coating "
             f"{coat_um:.0f} um a side (teaching)",
             "  a burr props the sheets apart along their edges: the stack",
             "  holds less steel in the same height",
             "  burr um   stacking factor   flux T   P0 kW"]
    out = {}
    for b in (0.0, 10.0, 20.0, 40.0):
        k = t_sheet_um / (t_sheet_um + 2 * coat_um + 0.5 * b)
        b_peak = D["e_t"] / (4.44 * 50 * a_gross * k)
        p0 = xd.no_load_loss_kw(g["core_kg"] * k / D["stacking"],
                                st["w"] * (b_peak / 1.7) ** 2, st["bf"])
        out[b] = p0
        lines.append(f"  {b:7.0f}   {k:15.3f}   {b_peak:6.3f}   {p0:5.1f}")
    lines += ["  the design's stacking factor 0.97 assumed about 10 um;",
              "  less steel in the same section runs at a higher flux, and",
              "  loss grows with its square; a burr also bridges the coating",
              "  between sheets - the burr record per batch is the control",
              "  (T1's batch 8 has none, lab D)"]
    emit("t_burr", lines)
    return out


# ------------------------------------------------ lamination thickness
def lamination(b: float = 1.7, f: float = 50.0, rho_el: float = 0.48e-6) -> dict:
    lines = ["classical eddy loss in the steel sheets: pi^2 f^2 B^2 t^2 /",
             "  (6 rho rho_m) per kg (teaching; the rest is hysteresis and",
             "  excess loss)",
             "  sheet mm   classical eddy W/kg   share of 1.15 W/kg"]
    out = {}
    for t_mm in (0.23, 0.27, 0.30, 0.35):
        t = t_mm / 1000
        pe = math.pi ** 2 * f ** 2 * b ** 2 * t ** 2 / (6 * rho_el * xd.RHO_FE)
        out[t_mm] = pe
        lines.append(f"  {t_mm:8.2f}   {pe:19.3f}   {pe / 1.15:18.0%}")
    lines += ["  thinner sheets cut the eddy part with the square of the",
              "  thickness - and mean more sheets to cut and stack: the",
              "  steel grade on the mill certificate names the thickness"]
    emit("t_lamination", lines)
    return out


# ------------------------------------------------ disc winding build
def disc_build(strands: int = 11, strand_w: float = 6.0, strand_t: float = 1.2,
               paper_mm: float = 0.5, turns_disc: int = 12) -> dict[str, float]:
    i_hv = M["s_mva"] * 1e6 / (math.sqrt(3) * M["hv_kv"] * 1e3)
    area = strands * strand_w * strand_t
    # CTC: two stacks of strands side by side, strands of a stack on top
    cable_radial = (strands + 1) / 2 * (strand_t + 0.1) + 2 * paper_mm
    build = turns_disc * cable_radial / 1000
    discs = math.ceil(D["n_hv"] / turns_disc)
    lines = ["HV disc winding from a continuously transposed cable (teaching)",
             f"  {strands} strands {strand_w} x {strand_t} mm: {area:.0f} mm2 "
             f"-> {i_hv / area:.2f} A/mm2 at rated",
             f"  cable radial size {cable_radial:.1f} mm; {turns_disc} turns a disc: "
             f"radial build {build * 1000:.0f} mm",
             f"  {D['n_hv']} turns in {discs} discs; the design's a2 was "
             f"{D['a2'] * 1000:.0f} mm",
             "  the radial build follows from the cable and the turns per",
             "  disc - a check that the preliminary geometry can be wound",
             "  (the space left is for ducts and the tapping leads)"]
    emit("t_disc", lines)
    return dict(area=area, build=build, discs=discs, j=i_hv / area)


# ------------------------------------------------ resistance reading settles
def settle(l_h: float = 60.0, r_ohm: float = 0.53, r_source: float = 2.0) -> dict:
    tau = l_h / (r_ohm + r_source)
    lines = [f"winding resistance by DC: current rises with tau = L / R "
             f"(teaching L {l_h:.0f} H)",
             f"  winding {r_ohm} ohm with a {r_source} ohm source: tau = {tau:.0f} s",
             "  error left   time"]
    out = {}
    for err in (0.01, 0.001, 0.0001):
        t = tau * math.log(1 / err)
        out[err] = t
        lines.append(f"  {err:10.2%}   {t / 60:5.1f} min")
    lines += ["  a reading taken while the current still rises is wrong by",
              "  the part not yet settled; the test set's stability record",
              "  shows the reading was taken flat - and the cold resistance",
              "  is the base of the heat-run calculation (lesson C)"]
    emit("t_settle", lines)
    return dict(tau=tau, t_01=out[0.001])


# ------------------------------------------------ ratio bridge
def bridge(acc_pct: float = 0.1, tol_pct: float = 0.5) -> dict[str, float]:
    tur = tol_pct / acc_pct
    guard = tol_pct - acc_pct
    lines = [f"ratio bridge accuracy {acc_pct} % against a +-{tol_pct} % tolerance",
             f"  test uncertainty ratio {tur:.0f}:1 (ch 40)",
             f"  a reading of {guard:.2f} % or less is a pass with the bridge's",
             f"  error included; between {guard:.2f} and {tol_pct:.2f} % the",
             "  result needs the decision rule of the contract",
             "  T1's -0.39 % at the -10 % tap is inside the guard band;",
             "  +0.62 % at +8.75 % is outside whatever the bridge's error"]
    emit("t_bridge", lines)
    return dict(tur=tur, guard=guard)


# ------------------------------------------------ rating limit priced
def rating_limit(x: float = 0.8) -> dict[str, float]:
    from companion.ch25.examples_b import unit_load
    rise, limit = 66.5, M["winding_rise"]
    p_total = 42.2 + 298.0
    ratio = (limit / rise) ** (1 / x)
    k2 = (ratio * p_total - 42.2) / 298.0
    k_lim = math.sqrt(k2)
    k = unit_load()
    over = int((k > k_lim).sum())
    lines = [f"winding rise {rise} K against {limit:.0f} K: what rating keeps it",
             f"  inside? (teaching: rise ~ total loss^{x})",
             f"  losses must fall to {ratio:.1%}: load {k_lim:.3f} pu = "
             f"{k_lim * M['s_mva']:.1f} MVA",
             f"  the data-pack year reaches {k.max():.2f} pu: hours above the "
             f"limit {over}",
             "  for this plant a written rating limit costs no energy -",
             "  the owner may accept it instead of a cooling repair, but",
             "  only in writing, with the limit in the plant controller",
             "  and the reason in the asset record (lab D, open decisions)"]
    emit("t_limit", lines)
    return dict(k_lim=k_lim, mva=k_lim * M["s_mva"], over=over, kmax=float(k.max()))


# ------------------------------------------------ factory schedule
ACTS = {   # activity: (weeks, predecessors) - teaching durations
    "design release": (6, []),
    "core steel delivered": (14, ["design release"]),
    "core cut and stacked": (4, ["core steel delivered"]),
    "copper (CTC) delivered": (10, ["design release"]),
    "windings": (6, ["copper (CTC) delivered"]),
    "tank and radiators": (8, ["design release"]),
    "active part assembly": (3, ["core cut and stacked", "windings"]),
    "drying, tanking, oil": (2, ["active part assembly", "tank and radiators"]),
    "tests": (2, ["drying, tanking, oil"]),
    "preparation for shipment": (1, ["tests"]),
}


def schedule() -> dict[str, float]:
    early: dict[str, float] = {}
    for a, (d, pre) in ACTS.items():
        early[a] = max((early[p] for p in pre), default=0.0) + d
    end = max(early.values())
    late: dict[str, float] = {}
    for a in reversed(list(ACTS)):
        succ = [s for s, (_, pre) in ACTS.items() if a in pre]
        late[a] = min((late[s] - ACTS[s][0] for s in succ), default=end)
    lines = [f"factory route as a network (teaching weeks): {end:.0f} weeks to ship",
             "  activity                      finishes   float"]
    crit = []
    for a in ACTS:
        fl = late[a] - early[a]
        if fl == 0:
            crit.append(a)
        lines.append(f"  {a:29s} {early[a]:8.0f}   {fl:5.0f}")
    lines += ["  critical: design release, core steel, cutting, assembly,",
              "  drying, tests - the windings wait with "
              f"{late['windings'] - early['windings']:.0f} weeks of float;",
              "  core steel from the mill is the long lead: reserving it at",
              "  award (ch 39) moves the whole date"]
    emit("t_schedule", lines)
    return dict(end=end, crit=len(crit), float_w=late["windings"] - early["windings"])


if __name__ == "__main__":
    burr()
    lamination()
    disc_build()
    settle()
    bridge()
    rating_limit()
    schedule()
