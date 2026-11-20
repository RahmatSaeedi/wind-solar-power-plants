"""Chapter 7 - integrated Plant P examples: currents from the units to the
point of connection (introductory), the reactive-power balance of the
plant (intermediate) and a first screening at the point of connection:
grid strength, voltage change, harmonic summation, resonance (integrated).

Run from the project root:   python -m companion.ch07.integrated
Writes companion/ch07/expected/i_*.txt and diagrams/data/ch07-qbal.csv.
Seed ratings SR-01..SR-06, A-032/A-052 (cable), A-040 (inverter
harmonics), A-091/A-092, A-100..A-102, A-107..A-109 (all teaching values).
"""
from __future__ import annotations

import math

from companion.ch07.common import csv, emit
from plantp import ac

S3 = math.sqrt(3)
P_EXPORT = 100.0                 # MW at the point of connection, SR-06
P_PV, P_WIND = 50.0, 60.0        # MW AC, SR-02, SR-03
N_INV, N_WT = 10, 12             # 5 MW units
S_INV = 5.5                      # MVA per PV inverter, A-101
S_WT = 5.0 / 0.95                # MVA per turbine converter, A-107
S_TX, X_TX, IM_TX = 120.0, 0.12, 0.003      # export transformer, A-102
S_UT, X_UT = 5.5, 0.06           # unit transformers, A-102
Q_CABLE = 1.79                   # Mvar, collector cables at 33 kV (sec. A)
X_FEED = 0.110 * 6.0             # ohm per feeder, A-032, A-091
Q_FILTER = 0.2                   # Mvar of filter capacitors per unit, A-107
PF_TARGET = 0.95                 # teaching target at the POC, A-108
S_SC_POC, XR_POC = 1000.0, 10.0  # grid at the 132 kV POC, A-109


def currents() -> None:
    lines = ["currents from the units to the point of connection (POC):"]
    for pf in (1.0, 0.95):
        lines.append(f"  POC 132 kV, {P_EXPORT:.0f} MW at pf {pf:.2f}: "
                     f"{ac.line_current_a(P_EXPORT * 1e6, 132e3, pf):6.1f} A")
    p_loss = 0.060 + 0.400 * (P_EXPORT / PF_TARGET / S_TX) ** 2   # A-092
    p_bus = P_EXPORT + p_loss
    i_bus = ac.line_current_a(p_bus * 1e6, 33e3, PF_TARGET)
    lines.append(f"  33 kV bus: {p_bus:.2f} MW at pf 0.95: {i_bus:6.0f} A "
                 f"(transformer losses {1000 * p_loss:.0f} kW, A-092)")
    for name, p in (("one feeder at the export limit", P_EXPORT / 4),
                    ("one feeder at full output", (P_PV + P_WIND) / 4)):
        lines.append(f"  {name:31s} {p:5.1f} MW: "
                     f"{ac.line_current_a(p * 1e6, 33e3, PF_TARGET):6.1f} A")
    lines.append(f"  one 5 MW unit at 33 kV: "
                 f"{ac.line_current_a(5e6, 33e3, PF_TARGET):5.1f} A; at its "
                 f"own 0.69 kV terminals: "
                 f"{ac.line_current_a(5e6, 690, PF_TARGET):6.0f} A")
    lines += ["  25 MW at 33 kV and 100 MW at 132 kV carry the same current:",
              "  100/132 = 25/33, the voltage ratio equals the power ratio",
              "  busbar and switchgear currents are a design decision of "
              "chapters 23-25"]
    emit("i_currents", lines)


def unit_q(s_unit: float, p_unit: float) -> float:
    return ac.q_capability(s_unit, p_unit)


def reactive_balance() -> None:
    share = P_EXPORT / (P_PV + P_WIND)               # all units curtailed
    p_unit = 5.0 * share
    q_req = P_EXPORT * math.tan(math.acos(PF_TARGET))
    s_poc = P_EXPORT / PF_TARGET
    q_tx = X_TX * (s_poc / S_TX) ** 2 * S_TX + IM_TX * S_TX
    q_ut = (N_INV + N_WT) * X_UT * (p_unit / S_UT) ** 2 * S_UT
    i_feed = ac.line_current_a(P_EXPORT / 4 * 1e6, 33e3, 1.0)
    q_feed = 4 * 3 * i_feed ** 2 * X_FEED / 1e6
    q_inv = N_INV * unit_q(S_INV, p_unit)
    q_wt = N_WT * unit_q(S_WT, p_unit)
    lines = [f"export {P_EXPORT:.0f} MW at the POC; every unit at "
             f"{p_unit:.2f} MW ({100 * share:.0f} % of rating)",
             f"teaching target pf {PF_TARGET} at the POC (A-108): "
             f"|Q| = {q_req:.1f} Mvar",
             "reactive power, Mvar (+ = supplied towards the grid, "
             "generator convention):"]
    rows = [("cable charging (sec. A)", Q_CABLE),
            ("feeder series reactance", -q_feed),
            ("unit transformers", -q_ut),
            ("export transformer", -q_tx)]
    for name, q in rows:
        lines.append(f"  {name:28s} {q:+7.2f}")
    net_plant = sum(q for _, q in rows)
    lines.append(f"  {'sum of the passive parts':28s} {net_plant:+7.2f}")
    need_lag = q_req - net_plant
    need_lead = -q_req - net_plant
    lines += [f"to supply {q_req:.1f} Mvar at the POC the units must "
              f"supply {need_lag:.1f} Mvar",
              f"to absorb {q_req:.1f} Mvar at the POC the units must absorb "
              f"{-need_lead:.1f} Mvar",
              f"units available at {p_unit:.2f} MW: PV inverters "
              f"{N_INV} x {unit_q(S_INV, p_unit):.2f} = {q_inv:.1f},",
              f"  turbines {N_WT} x {unit_q(S_WT, p_unit):.2f} = "
              f"{q_wt:.1f}",
              f"  total {q_inv + q_wt:.1f} Mvar; margin for the supplying "
              f"case {q_inv + q_wt - need_lag:.1f} Mvar",
              "limits: one operating point, voltages held at 1.0 pu, "
              "feeder current as if",
              "  lumped at the far end (conservative); a load flow decides "
              "(chapter 28)"]
    emit("i_reactive", lines)
    rows_csv = []
    for p_poc in range(0, 101, 5):
        sh = p_poc / (P_PV + P_WIND)
        pu = 5.0 * sh
        cap = N_INV * unit_q(S_INV, pu) + N_WT * unit_q(S_WT, pu)
        s = max(p_poc / PF_TARGET, 1e-9)
        loss = X_TX * (s / S_TX) ** 2 * S_TX + IM_TX * S_TX \
            + (N_INV + N_WT) * X_UT * (pu / S_UT) ** 2 * S_UT \
            + 4 * 3 * ac.line_current_a(max(p_poc, 1e-9) / 4 * 1e6, 33e3,
                                        1.0) ** 2 * X_FEED / 1e6 - Q_CABLE
        rows_csv.append((f"{p_poc}", f"{cap:.2f}", f"{cap - loss:.2f}",
                         f"{p_poc * math.tan(math.acos(PF_TARGET)):.2f}"))
    csv("ch07-qbal.csv", "p,qunits,qpoc,qreq", rows_csv)
    q_night = Q_CABLE - IM_TX * S_TX
    emit("i_night", [
        "night, no wind, all units stopped: P = 0",
        f"  cables still supply {Q_CABLE:.2f} Mvar; the export transformer's",
        f"  magnetising current absorbs {IM_TX * S_TX:.2f} Mvar",
        f"  net {q_night:+.2f} Mvar flows to the grid with no active power",
        "  small here (24 km at 33 kV); long HV export cables can need a "
        "shunt reactor:",
        "  whether Q at no output is allowed is the grid operator's rule "
        "(ch 17, 55)",
    ])


def poc_screening() -> None:
    s_sc33 = 1 / (1 / S_SC_POC + X_TX / S_TX)        # MVA at the 33 kV bus
    scr = S_SC_POC / P_EXPORT
    z_pu = P_EXPORT / S_SC_POC                       # on a 100 MVA base
    r_pu = z_pu / math.sqrt(1 + XR_POC ** 2)
    x_pu = r_pu * XR_POC
    lines = [f"grid at the 132 kV POC (A-109): S_sc {S_SC_POC:.0f} MVA, "
             f"X/R {XR_POC:.0f}",
             f"  behind the 120 MVA, 12 % transformer the 33 kV bus sees "
             f"{s_sc33:.0f} MVA (A-100: 500)",
             f"  short-circuit ratio S_sc / P = {scr:.0f}; network impedance "
             f"{z_pu:.3f} pu on 100 MVA",
             "voltage change at the POC, dV ~ R P + X Q (pu, generator "
             "convention):"]
    q_lim = P_EXPORT * math.tan(math.acos(PF_TARGET)) / 100
    for name, q in (("pf 1", 0.0), ("supplying Q", q_lim),
                    ("absorbing Q", -q_lim)):
        dv = r_pu * 1.0 + x_pu * q
        lines.append(f"  P 1.00 pu, Q {q:+.3f} pu ({name:11s}): dV "
                     f"{100 * dv:+.2f} %")
    lines.append("  active power alone moves the voltage little (R small); "
                 "Q moves it")
    emit("i_poc", lines)
    s_sc_bus = s_sc33 * 1e6
    x_sc = 33e3 ** 2 / s_sc_bus
    vph = 33e3 / S3
    i_unit = 5e6 / (S3 * 33e3)
    n = N_INV + N_WT
    lines = [f"harmonic voltage at the 33 kV bus, {n} units of 5 MW, "
             "spectrum A-040:"]
    for h, a in ((5, 0.04), (7, 0.03)):
        v1 = a * i_unit * h * x_sc / vph
        sums = {alpha: v1 * n ** (1 / alpha) for alpha in (1.0, 1.4, 2.0)}
        lines.append(f"  order {h}: one unit {100 * v1:.3f} %; {n} units "
                     f"alpha 1: {100 * sums[1.0]:.2f} %, 1.4: "
                     f"{100 * sums[1.4]:.2f} %, 2: {100 * sums[2.0]:.2f} %")
    lines += ["  sum = (sum of V_i^alpha)^(1/alpha): alpha 1 = all in phase "
              "(worst case),",
              "  alpha 2 = random phases; the study uses the exponents and "
              "limits",
              "  the grid operator applies (chapter 27)"]
    q_c = Q_CABLE + n * Q_FILTER
    for name, qc in (("cables only", Q_CABLE),
                     (f"cables + {n} unit filters", q_c)):
        h = ac.resonance_order(s_sc33, qc)
        lines.append(f"  resonance, {name:24s} Q_c {qc:5.2f} Mvar: h = "
                     f"{h:5.2f}")
    lines.append("  the filters move the resonance down towards the orders "
                 "the units emit")
    emit("i_harmonic", lines)


if __name__ == "__main__":
    currents()
    reactive_balance()
    poc_screening()
