"""Chapter 43, lesson B: materials and preliminary design - the stepped
core, steel grades against the two bids of ch 25, the current density that
the loss evaluation favours, strand thickness and eddy loss, the shipping
mass, a sensitivity of the evaluated cost and the PV unit transformer.

Run from the project root:   python -m companion.ch43.examples_b
Writes companion/ch43/expected/b_*.txt and diagrams/data/ch43-*.csv.
Teaching values (A-458, A-459).
"""
from __future__ import annotations

import math

from companion.ch43 import sources as src
from companion.ch43.common import csv, emit
from companion.ch43.examples_a import I_HV, I_LV, geometry, losses
from plantp import xfmrdesign as xd

M, D, C = src.MAIN_B, src.DESIGN, src.COSTS


# ------------------------------------------------ stepped core
def steps() -> dict[int, float]:
    g = geometry()
    lines = ["stepped core: share of the circle that n steps fill (optimised)",
             "  steps   fill    net area m2 in the 0.638 m circle"]
    out, rows = {}, []
    for n in (1, 2, 3, 4, 5, 7, 9, 11, 13):
        f, _ = xd.stepped_fill(n)
        out[n] = f
        rows.append((n, round(f, 4)))
        area = f * math.pi * g["d"] ** 2 / 4 * D["stacking"]
        lines.append(f"  {n:5d}   {f:.3f}   {area:.4f}")
    csv("ch43-steps.csv", "n,fill", rows)
    f9, y9 = xd.stepped_fill(9)
    widths = [2 * math.sqrt(1 - y * y) * g["d"] / 2 * 1000 for y in y9]
    lines += ["  9 steps, plate widths mm: "
              + ", ".join(f"{w:.0f}" for w in widths[:5]),
              "    " + ", ".join(f"{w:.0f}" for w in widths[5:]),
              "  each step is a stack of one plate width: more steps fill",
              "  the circle better but need more widths to cut and stack -",
              "  the gain from 9 to 13 steps is under 2 points of area"]
    emit("b_steps", lines)
    return out


# ------------------------------------------------ steel grades and the bids
def steels() -> dict[str, float]:
    g = geometry()
    m = g["core_kg"]
    base = src.STEELS["conventional GO"]
    p_base = xd.no_load_loss_kw(m, base["w"], base["bf"])
    lines = [f"the same {m / 1000:.1f} t core in three steels",
             "  (teaching W/kg at 1.7 T and building factors)",
             "  steel                  W/kg   BF     P0 kW   A x dP0   steel extra"
             "   net k u"]
    out = {}
    for name, st in src.STEELS.items():
        p0 = xd.no_load_loss_kw(m, st["w"], st["bf"])
        d_loss = (p0 - p_base) * C["a_kw"]
        d_steel = m * (st["price"] - base["price"]) / 1000
        out[name] = p0
        lines.append(f"  {name:21s} {st['w']:5.2f}  {st['bf']:4.2f}  {p0:7.1f}  "
                     f"{d_loss:8.0f}   {d_steel:10.0f}   {d_loss + d_steel:7.0f}")
    lines += [f"  bid B's {M['p0_kw']:.0f} kW is the conventional core; bid A's 28 kW "
              "is the",
              "  high-permeability one - the bids differ first in the steel",
              f"  at A = {C['a_kw']} k u/kW the better steel repays its price "
              "several times;",
              "  bid A's 250 k u premium bought more than steel (ch 25: B won",
              "  at 70 u/MWh) - the evaluation sees totals, the review sees why"]
    emit("b_steels", lines)
    return out


# ------------------------------------------------ current density
def density() -> dict[str, float]:
    base = losses()
    cu0 = 8.4e3                                   # kg at 3.5 A/mm2 (lesson A)
    j0 = D["j_a_mm2"]
    lines = ["current density: copper bought against load loss evaluated",
             f"  (B = {C['b_kw']} k u/kW, copper {C['copper']:.0f} u/kg)",
             "  J A/mm2   copper t   Pk kW   copper k u   B x Pk k u   sum k u"]
    best = None
    rows = []
    for jj in range(16, 43):
        j = jj / 10
        cu = cu0 * j0 / j
        a, b = cu * C["copper"] / 1000, base["pk"] * j / j0 * C["b_kw"]
        rows.append((j, round(a, 1), round(b, 1), round(a + b, 1)))
    csv("ch43-density.csv", "j,copper,loss,sum", rows)
    for j in (2.0, 2.5, 3.0, 3.5, 4.0):
        cu = cu0 * j0 / j
        pk = base["pk"] * j / j0
        a, b = cu * C["copper"] / 1000, pk * C["b_kw"]
        lines.append(f"  {j:7.1f}   {cu / 1000:8.1f}   {pk:5.0f}   {a:10.0f}   "
                     f"{b:10.0f}   {a + b:7.0f}")
        if best is None or a + b < best[1]:
            best = (j, a + b)
    j_opt = j0 * math.sqrt(cu0 * C["copper"] / 1000 / (base["pk"] * C["b_kw"]))
    j_a = j0 * 215.0 / base["pk"]
    lines += [f"  the two-term optimum is {j_opt:.1f} A/mm2; bid B sits at {j0}, "
              f"bid A near {j_a:.1f}",
              "  bigger windings need a bigger window, core, tank and oil;",
              "  counting those moves the optimum up - the trade is real,",
              "  its exact place is the maker's optimisation"]
    emit("b_density", lines)
    return dict(j_opt=j_opt, j_a=j_a)


# ------------------------------------------------ strand thickness
def strands() -> dict[float, float]:
    b_gap = xd.MU0 * D["n_hv"] * I_HV * math.sqrt(2) / D["h"]
    j = D["j_a_mm2"] * 1e6
    lines = ["eddy loss of strips in the axial leakage field",
             f"  (peak {b_gap:.3f} T in the gap at rated)",
             "  strand mm   eddy / DC loss (axial field only)"]
    out = {}
    for t in (1.0, 1.5, 2.0, 2.5, 3.0):
        r = xd.eddy_ratio(50.0, b_gap, t / 1000, j)
        out[t] = r
        lines.append(f"  {t:9.1f}   {r:.2%}")
    lines += ["  the axial field alone gives a few per cent; at the winding",
              "  ends the leakage flux bends radially and strikes the wide",
              "  face of the strip, adding several times more - hence thin",
              "  strands transposed along the winding (CTC) and the larger",
              "  teaching share of ch 25; the maker's field calculation",
              "  places the hot spots"]
    emit("b_strands", lines)
    return out


# ------------------------------------------------ shipping mass
def mass() -> dict[str, float]:
    g = geometry()
    parts = [("core", g["core_kg"] / 1000), ("windings (copper)", 8.4),
             ("leads, tap winding, insulation, clamps", 6.0),
             ("tank and cover", 16.0), ("oil (22 m3)", 22 * 0.88),
             ("radiators, fans", 6.0), ("conservator, bushings, OLTC drive", 4.0)]
    total = sum(v for _, v in parts)
    ship = parts[0][1] + parts[1][1] + parts[2][1] + parts[3][1] + 2.0
    lines = ["mass of the 63 MVA unit (teaching estimate)"]
    for name, v in parts:
        lines.append(f"  {name:40s} {v:5.1f} t")
    lines += [f"  in service {total:.0f} t (ch 25: {M['mass_t']:.0f} t)",
              "  shipped without oil, radiators and bushings, gas-filled,",
              f"  with 2 t bracing: {ship:.0f} t",
              f"  limit {M['transport_t']:.0f} t: margin {M['transport_t'] - ship:.0f} t"
              " - the reason the tank ships dry and",
              "  the accessories travel apart (ch 25, transport; ch 31)"]
    emit("b_mass", lines)
    return dict(total=total, ship=ship)


# ------------------------------------------------ sensitivity
def tornado() -> list[tuple[str, float, float]]:
    g = geometry()
    st = src.STEELS["conventional GO"]
    base = losses()

    def cost(w=1.0, bf=1.0, j=1.0, a=1.0, b=1.0, cu=1.0):
        p0 = xd.no_load_loss_kw(g["core_kg"], st["w"] * w, st["bf"] * bf)
        pk = base["pk"] * j
        steel = g["core_kg"] * st["price"] / 1000
        copper = 8.4e3 / j * C["copper"] * cu / 1000
        return steel + copper + p0 * C["a_kw"] * a + pk * C["b_kw"] * b
    c0 = cost()
    rows = []
    for name, key in (("steel W/kg", "w"), ("building factor", "bf"),
                      ("current density", "j"), ("A factor", "a"),
                      ("B factor", "b"), ("copper price", "cu")):
        lo, hi = cost(**{key: 0.9}), cost(**{key: 1.1})
        rows.append((name, lo - c0, hi - c0))
    rows.sort(key=lambda r: -abs(r[2] - r[1]))
    lines = [f"evaluated cost of the active part and its losses: {c0:,.0f} k u",
             "  input +-10 %          -10 % k u   +10 % k u"]
    for name, lo, hi in rows:
        lines.append(f"  {name:20s} {lo:10.0f}   {hi:9.0f}")
    lines += ["  the no-load loss terms lead: steel quality and the building",
              "  factor (cutting and stacking, lesson C) move the evaluated",
              "  cost more than copper - a factory's core shop is where the",
              "  A factor is earned or lost"]
    emit("b_tornado", lines)
    return rows


# ------------------------------------------------ PV unit transformer
def pv_unit() -> dict[str, float]:
    u = src.PVU
    v_lv = u["lv_kv"] * 1e3 / math.sqrt(3)
    out = {}
    lines = [f"PV unit transformer {u['s_mva']} MVA {u['hv_kv']:.0f}/"
             f"{u['lv_kv']} kV {u['vector']} (ch 39, offer U-A)",
             f"  LV star phase {v_lv:.0f} V; phase current "
             f"{u['s_mva'] * 1e6 / (3 * v_lv):,.0f} A",
             "  LV turns   volts a turn   HV turns (delta, 33 kV)   ratio error"]
    for n_lv in (14, 16, 18):
        e_t = v_lv / n_lv
        n_hv = round(u["hv_kv"] * 1e3 / e_t)
        err = 100 * (n_hv * e_t / (u["hv_kv"] * 1e3) - 1)
        out[n_lv] = e_t
        lines.append(f"  {n_lv:8d}   {e_t:12.2f}   {n_hv:23d}   {err:+.2f} %")
    a = 16
    e_t = v_lv / a
    c = xd.core_section(e_t, 1.7, fill=0.91)
    lines += [f"  with 16 LV turns: core {c['a_net'] * 1e4:.0f} cm2 net, "
              f"{c['d'] * 1000:.0f} mm across",
              "  one LV turn is 6 % of the voltage: the LV side fixes the",
              "  volts a turn, and a few thousand amperes a phase call for",
              "  a foil winding; taps go on the 33 kV side, where a turn is",
              "  a small step"]
    emit("b_pvunit", lines)
    return out


if __name__ == "__main__":
    steps()
    steels()
    density()
    strands()
    mass()
    tornado()
    pv_unit()
