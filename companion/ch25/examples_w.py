"""Chapter 25 - ninth round: a model-based cooling alarm (measured top oil
against the thermal model), the cost of the payment milestones, the
voltage dip of energising a main transformer, the transformer on its
foundation under an earthquake (teaching coefficients), and the 132 kV
tubular busbar.

Run from the project root:   python -m companion.ch25.examples_w
Writes companion/ch25/expected/w_*.txt and diagrams/data/ch25-residual.csv.
Teaching values (A-326..A-330 extended).
"""
from __future__ import annotations

import math
import random

from companion.ch25 import sources as src
from companion.ch25.common import csv, emit

M = src.MAIN


# [start: residual]
def top_oil_day(fail_h: float | None, air: float = 35.0,
                step_min: float = 5.0) -> list:
    """Top-oil temperature through a day (mean air temperature `air`);
    from fail_h the fans stop: ONAN, as if loaded 63/50 times harder."""
    d_or, r, x, tau = 52.0, 6.0, 0.8, 180.0
    d_o, rows = 30.0, []
    for k in range(int(48 * 60 / step_min)):
        t = (k * step_min / 60.0) % 24
        amb = air + 10 * math.sin(math.pi * (t - 9) / 12)
        sun = math.sin(math.pi * (t - 6) / 12)
        pv = max(0.0, sun) if 6 <= t <= 18 else 0.0
        load = min(0.35 + 0.80 * pv, 1.15)
        if fail_h is not None and k >= 24 * 60 / step_min and t >= fail_h:
            load *= M["s_mva"] / M["s_onan_mva"]
        d_ou = d_or * ((1 + r * load ** 2) / (1 + r)) ** x
        d_o += (d_ou - d_o) * step_min / tau
        if k >= 24 * 60 / step_min:
            rows.append((t, amb + d_o))
    return rows
# [end: residual]


def residual_alarm() -> None:
    lines = ["a model-based cooling alarm: the fans fail at 11:00",
             "  model = top oil predicted with fans; measured = fans failed",
             "  (sensor noise 0.8 K); alarm when measured - model > 5 K for",
             "  three readings in a row (15 min); fixed alarm at 95 C top oil",
             "  day (mean air)   model alarm   fixed alarm   lead h   top oil max C"]
    leads = []
    for air in (35.0, 20.0):
        rnd = random.Random(25)
        model = top_oil_day(None, air)
        meas = [(t, v + rnd.gauss(0, 0.8)) for t, v in top_oil_day(11.0, air)]
        if air == 20.0:
            csv("ch25-residual.csv", "h,model,meas",
                [(f"{a[0]:.2f}", f"{a[1]:.1f}", f"{b[1]:.1f}") for a, b in zip(model, meas)])
        run, found, fixed = 0, None, None
        for (t, v_m), (_, v) in zip(model, meas):
            run = run + 1 if v - v_m > 5.0 else 0
            if run == 3 and found is None:
                found = t
            if v > 95.0 and fixed is None:
                fixed = t
        peak = max(v - m for (_, m), (_, v) in zip(model, meas))
        top = max(v for _, v in meas)
        lead = (fixed - found) if fixed else float("nan")
        name = ("hot" if air > 30 else "mild") + f" ({air:.0f} C)"
        lines.append(f"  {name:16s}   {found:9.2f} h   {(f'{fixed:.2f} h' if fixed else 'never'):>11s}"
                     f"   {lead:6.2f}   {top:13.0f}")
        leads.append(lead)
    lines.append(f"  largest residual {peak:.1f} K (both days)")
    lines += [f"  the model alarm comes 45 min after the failure on both days;",
              f"  the fixed alarm follows {leads[0] * 60:.0f} min later on the hot day but",
              f"  {leads[1]:.1f} h later on the mild one, when the oil is already past",
              "  95 C: a fixed threshold waits for the weather, the residual",
              "  does not - the model's constants come from the heat run, and",
              "  the alarm logic belongs to the monitoring specification"]
    emit("w_residual", lines)


def milestones() -> None:
    price, rate = 1_700.0, 0.06
    schemes = {
        "progress": [(20, 0.10), (17, 0.10), (12, 0.30), (6, 0.30), (4, 0.10), (1, 0.10)],
        "on delivery": [(20, 0.10), (4, 0.80), (1, 0.10)],
    }
    lines = ["payment milestones for one main transformer (bid B, 1,700 k u;",
             "  money at 6 % a year until COD; months before COD)",
             "  scheme        payments (months: share)                    cost k u"]
    for name, pays in schemes.items():
        cost = sum(price * s * ((1 + rate) ** (m / 12) - 1) for m, s in pays)
        txt = ", ".join(f"{m}:{s:.0%}" for m, s in pays)
        lines.append(f"  {name:12s}  {txt:45s} {cost:6.1f}")
    lines += ["  paying for progress costs the owner more interest but lets",
              "  the maker buy copper and steel without borrowing (its price",
              "  is lower or its risk smaller); each advance is protected by",
              "  a guarantee and each milestone by evidence (design approved,",
              "  FAT passed, delivered) - the terms are the contract's",
              "  (ch 39); this is a commercial sketch, not legal advice"]
    emit("w_milestones", lines)


def energising_dip() -> None:
    ik = 5.2e3                      # 132 kV bus fault current (ch 26 network)
    lines = ["voltage dip when a main transformer is energised from 132 kV",
             "  rough upper estimate: dU/U ~ (i_peak / sqrt2) / Ik, Ik 5.2 kA",
             "  case                                      i_peak A   dip"]
    for name, ip in (("residual flux 0.8 Bn, worst instant", 2086), ("no residual, worst instant", 1047),
                     ("controlled switching (teaching 1.5 x In)", 1.5 * 276 * math.sqrt(2))):
        lines.append(f"  {name:41s} {ip:8.0f}   {ip / math.sqrt(2) / ik:4.0%}")
    lines += ["  a worst-case energising can dip the 132 kV bus by a quarter",
              "  for the first cycles; the grid operator limits such rapid",
              "  voltage changes (its own figure, open until the grid offer),",
              "  so controlled switching or a pre-insertion resistor may be",
              "  asked for - the electromagnetic transient study (ch 28)",
              "  gives the real value"]
    emit("w_dip", lines)


def seismic() -> None:
    m_t, g = M["mass_t"], 9.81
    w = m_t * g
    base_w, h_cg, mu = 4.5, 2.0, 0.30
    lines = ["the transformer on its foundation (teaching coefficients only)",
             f"  mass {m_t:.0f} t, weight {w:.0f} kN, base 4.5 m wide, centre of mass",
             "  2.0 m up; friction steel on concrete 0.30",
             "  horizontal coeff   force kN   overturning kNm   resisting kNm   slides?"]
    for a in (0.10, 0.20, 0.30, 0.40):
        f = a * w
        lines.append(f"  {a:16.2f}   {f:8.0f}   {f * h_cg:15.0f}   {w * base_w / 2:13.0f}"
                     f"   {'yes' if f > mu * w else 'no'}")
    lines += ["  the unit does not tip, but from about 0.3 it would slide on its",
              "  rails: it is anchored to the foundation; the tall bushings",
              "  on the tank top shake harder than the ground (amplified),",
              "  so their seismic qualification is part of the bid evidence;",
              "  the site's design acceleration comes from the seismic",
              "  hazard study and the structural engineer (ch 29), not here"]
    emit("w_seismic", lines)


def tube_bus() -> None:
    d_o, d_i, rho_al, e_al = 0.100, 0.088, 2700.0, 70e9
    area = math.pi / 4 * (d_o ** 2 - d_i ** 2)
    inertia = math.pi / 64 * (d_o ** 4 - d_i ** 4)
    wgt = area * rho_al * 9.81
    lines = ["132 kV tubular busbar, aluminium 100/88 mm (teaching):",
             f"  self-weight {wgt:.1f} N/m; I = {inertia * 1e6:.2f} x 10^-6 m^4",
             "  span m   deflection mm (5wL^4/384EI)   limit L/200 mm"]
    for span in (8.0, 10.0, 12.0):
        dfl = 5 * wgt * span ** 4 / (384 * e_al * inertia)
        lines.append(f"  {span:6.0f}   {dfl * 1e3:29.0f}   {span / 0.2:14.0f}")
    ip = 2.5 * 31.5e3
    f_l = 0.866 * 2e-7 * ip ** 2 / 2.0
    lines += [f"  fault force at the gear's 31.5 kA rating (ip {ip / 1e3:.0f} kA), 2.0 m",
              f"  phase spacing: {f_l:.0f} N/m - {f_l / wgt:.0f} times the self-weight",
              "  spans up to about 10 m meet L/200 under self-weight alone;",
              "  at 132 kV the wide spacing keeps fault forces moderate;",
              "  the span is set by sag, wind, ice and the supports'",
              "  strength under the fault - the maker's or designer's",
              "  calculation to the standard, checked in the design review"]
    emit("w_tube", lines)


if __name__ == "__main__":
    residual_alarm()
    milestones()
    energising_dip()
    seismic()
    tube_bus()
